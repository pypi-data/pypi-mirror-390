from aio_pika.pool import Pool
from aio_pika.abc import AbstractRobustConnection
from aio_pika import connect_robust, Channel
from typing import Optional, List
import asyncio
import json
from typing import Callable, Coroutine, Optional, Dict, Any, Union, Set
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import (
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractIncomingMessage,
    ConsumerTag,
)
from aiormq.exceptions import ChannelInvalidStateError, ConnectionClosed

from sycommon.logging.kafka_log import SYLogger
from sycommon.models.mqmsg_model import MQMsgModel
from sycommon.rabbitmq.rabbitmq_pool import RabbitMQConnectionPool

# 最大重试次数限制
MAX_RETRY_COUNT = 3

logger = SYLogger


class RabbitMQClient:
    """
    RabbitMQ客户端（基于连接池），支持集群多节点配置
    提供自动故障转移、连接恢复和消息可靠性保障
    采用细粒度锁设计，彻底避免死锁隐患
    """

    def __init__(
        self,
        connection_pool: RabbitMQConnectionPool,
        exchange_name: str = "system.topic.exchange",
        exchange_type: str = "topic",
        queue_name: Optional[str] = None,
        routing_key: str = "#",
        durable: bool = True,
        auto_delete: bool = False,
        auto_parse_json: bool = True,
        create_if_not_exists: bool = True,
        connection_timeout: int = 10,
        rpc_timeout: int = 10,
        reconnection_delay: int = 1,
        max_reconnection_attempts: int = 5,
        prefetch_count: int = 2,
        consumption_stall_threshold: int = 10
    ):
        # 连接池依赖
        self.connection_pool = connection_pool

        # 交换器和队列参数
        self.exchange_name = exchange_name
        self.exchange_type = ExchangeType(exchange_type)
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.durable = durable
        self.auto_delete = auto_delete

        # 行为控制参数
        self.auto_parse_json = auto_parse_json
        self.create_if_not_exists = create_if_not_exists
        self.connection_timeout = connection_timeout
        self.rpc_timeout = rpc_timeout
        self.prefetch_count = prefetch_count

        # 重连参数
        self.reconnection_delay = reconnection_delay
        self.max_reconnection_attempts = max_reconnection_attempts

        # 消息处理参数
        self.consumption_stall_threshold = consumption_stall_threshold

        # 通道和资源对象（由 _connection_lock 保护）
        self.channel: Optional[AbstractChannel] = None
        self.exchange: Optional[AbstractExchange] = None
        self.queue: Optional[AbstractQueue] = None

        # 状态跟踪（按类型拆分锁保护）
        self.actual_queue_name: Optional[str] = None
        self._exchange_exists = False  # 由 _connection_lock 保护
        self._queue_exists = False     # 由 _connection_lock 保护
        self._queue_bound = False      # 由 _connection_lock 保护
        self._closed = False           # 由 _connection_lock 保护
        # 由 _consume_state_lock 保护：通过 consumer_tag 存在性判断是否在消费
        self._consumer_tag: Optional[ConsumerTag] = None
        self._last_activity_timestamp = asyncio.get_event_loop().time()
        self._last_message_processed = asyncio.get_event_loop().time()

        # 任务和处理器
        self.message_handler: Optional[Callable[
            [Union[Dict[str, Any], str], AbstractIncomingMessage],
            Coroutine[Any, Any, None]
        ]] = None  # 由 _consume_state_lock 保护
        self._consuming_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        self._keepalive_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None

        # 消息处理跟踪（由 _tracking_lock 保护）
        self._tracking_messages: Dict[str, Dict[str, Any]] = {}

        # 细粒度锁（核心设计：按资源类型拆分，避免嵌套）
        # 保护消费状态（message_handler、_consumer_tag）
        self._consume_state_lock = asyncio.Lock()
        self._tracking_lock = asyncio.Lock()       # 保护消息跟踪记录（_tracking_messages）
        # 保护连接/资源状态（channel、exchange、queue、_closed等）
        self._connection_lock = asyncio.Lock()

    @property
    async def is_connected(self) -> bool:
        """异步属性：检查当前通道是否有效（线程安全）"""
        async with self._connection_lock:
            return (not self._closed and
                    self.channel is not None and
                    not self.channel.is_closed and
                    self.exchange is not None)

    def _update_activity_timestamp(self) -> None:
        """更新最后活动时间戳（非共享状态，无需锁）"""
        self._last_activity_timestamp = asyncio.get_event_loop().time()

    def _update_message_processed_timestamp(self) -> None:
        """更新最后消息处理时间戳（非共享状态，无需锁）"""
        self._last_message_processed = asyncio.get_event_loop().time()

    # ------------------------------
    # 消费状态操作（_consume_state_lock 专属保护）
    # ------------------------------
    async def _get_consume_state(self) -> tuple[bool, Optional[Callable], Optional[ConsumerTag]]:
        """安全获取消费相关状态（一次性获取，避免多次加锁）"""
        async with self._consume_state_lock:
            # 通过 _consumer_tag 是否存在判断是否在消费
            is_consuming = self._consumer_tag is not None
            return is_consuming, self.message_handler, self._consumer_tag

    async def _set_consumer_tag(self, consumer_tag: Optional[ConsumerTag] = None):
        """安全更新消费者标签（替代原 _set_consume_state）"""
        async with self._consume_state_lock:
            old_tag = self._consumer_tag
            self._consumer_tag = consumer_tag
            old_is_consuming = old_tag is not None
            new_is_consuming = consumer_tag is not None
            if old_is_consuming != new_is_consuming:
                logger.info(f"消费状态变更: {old_is_consuming} → {new_is_consuming}")

    async def set_message_handler(self, handler):
        """设置消息处理器（加锁保护，避免并发修改）"""
        async with self._consume_state_lock:
            self.message_handler = handler
            logger.info("消息处理器已设置")

    # ------------------------------
    # 连接状态操作（_connection_lock 专属保护）
    # ------------------------------
    async def _is_closed(self) -> bool:
        """检查客户端是否已关闭（线程安全）"""
        async with self._connection_lock:
            return self._closed

    async def _mark_closed(self):
        """标记客户端已关闭（原子操作）"""
        async with self._connection_lock:
            self._closed = True

    async def _get_connection_resources(self) -> tuple[Optional[AbstractChannel], Optional[AbstractExchange], Optional[AbstractQueue]]:
        """安全获取连接资源（channel/exchange/queue）"""
        async with self._connection_lock:
            return self.channel, self.exchange, self.queue

    async def _reset_connection_state(self):
        """重置连接状态（用于重连时，原子操作）"""
        async with self._connection_lock:
            self._exchange_exists = False
            self._queue_exists = False
            self._queue_bound = False
            self.channel = None
            self.exchange = None
            self.queue = None
            self.actual_queue_name = None

    async def _update_connection_resources(self, channel: AbstractChannel, exchange: AbstractExchange, queue: Optional[AbstractQueue] = None):
        """更新连接资源（原子操作）"""
        async with self._connection_lock:
            self.channel = channel
            self.exchange = exchange
            self.queue = queue
            if queue:
                self.actual_queue_name = queue.name

    # ------------------------------
    # 消息跟踪操作（_tracking_lock 专属保护）
    # ------------------------------
    async def _add_tracking_message(self, msg_id: str, delivery_tag: int, channel_number: Optional[int]):
        """添加消息跟踪记录（原子操作）"""
        async with self._tracking_lock:
            self._tracking_messages[msg_id] = {
                'delivery_tag': delivery_tag,
                'acked': False,
                'channel_number': channel_number,
                'start_time': asyncio.get_event_loop().time()
            }

    async def _mark_tracking_acked(self, msg_id: str):
        """标记消息已确认（原子操作）"""
        async with self._tracking_lock:
            if msg_id in self._tracking_messages:
                self._tracking_messages[msg_id]['acked'] = True

    async def _remove_tracking_message(self, msg_id: str):
        """删除消息跟踪记录（原子操作，避免KeyError）"""
        async with self._tracking_lock:
            if msg_id in self._tracking_messages:
                del self._tracking_messages[msg_id]
                logger.info(f"已删除消息跟踪信息: {msg_id}")

    async def _check_duplicate_message(self, msg_id: str) -> bool:
        """检查消息是否重复处理（原子操作）"""
        async with self._tracking_lock:
            return msg_id in self._tracking_messages

    async def _get_tracking_count(self) -> int:
        """获取当前跟踪的消息数（原子操作）"""
        async with self._tracking_lock:
            return len(self._tracking_messages)

    async def _cleanup_acked_tracking_messages(self) -> int:
        """清理已确认的跟踪记录（原子操作，返回清理数量）"""
        async with self._tracking_lock:
            acked_ids = [
                msg_id for msg_id, info in self._tracking_messages.items() if info.get('acked')]
            for msg_id in acked_ids:
                del self._tracking_messages[msg_id]
            return len(acked_ids)

    async def _clear_tracking_messages(self):
        """清空所有跟踪记录（原子操作）"""
        async with self._tracking_lock:
            self._tracking_messages.clear()

    # ------------------------------
    # 基础工具方法
    # ------------------------------
    async def _get_channel(self) -> AbstractChannel:
        """从通道池获取通道（使用上下文管理器，自动归还）"""
        if not self.connection_pool.channel_pool:
            raise Exception("连接池未初始化，请先调用init_pools")

        async with self.connection_pool.channel_pool.acquire() as channel:
            return channel

    async def _check_exchange_exists(self, channel: AbstractChannel) -> bool:
        """检查交换机是否存在"""
        try:
            await asyncio.wait_for(
                channel.declare_exchange(
                    name=self.exchange_name,
                    type=self.exchange_type,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            return True
        except Exception:
            return False

    async def _check_queue_exists(self, channel: AbstractChannel) -> bool:
        """检查队列是否存在"""
        if not self.queue_name:
            return False
        try:
            await asyncio.wait_for(
                channel.declare_queue(
                    name=self.queue_name,
                    passive=True
                ),
                timeout=self.rpc_timeout
            )
            return True
        except Exception:
            return False

    async def _bind_queue(self, channel: AbstractChannel, queue: AbstractQueue, exchange: AbstractExchange) -> bool:
        """将队列绑定到交换机（带重试）"""
        bind_routing_key = self.routing_key if self.routing_key else '#'

        for attempt in range(MAX_RETRY_COUNT + 1):
            try:
                await asyncio.wait_for(
                    queue.bind(
                        exchange,
                        routing_key=bind_routing_key
                    ),
                    timeout=self.rpc_timeout
                )
                logger.info(
                    f"队列 '{queue.name}' 已绑定到交换机 '{exchange.name}'，路由键: {bind_routing_key}")
                return True
            except Exception as e:
                logger.warning(
                    f"队列绑定失败（第{attempt+1}次尝试）: {str(e)}")
            if attempt < MAX_RETRY_COUNT:
                await asyncio.sleep(1)
        return False

    # ------------------------------
    # 核心业务方法
    # ------------------------------
    async def connect(self, force_reconnect: bool = False, declare_queue: bool = True) -> None:
        """从连接池获取资源并初始化（交换机、队列）"""
        logger.info(
            f"连接参数 - force_reconnect={force_reconnect}, "
            f"declare_queue={declare_queue}, create_if_not_exists={self.create_if_not_exists}"
        )

        # 检查是否已关闭
        if await self._is_closed():
            raise Exception("客户端已关闭，无法连接")

        # 检查是否已连接（非强制重连则直接返回）
        if await self.is_connected and not force_reconnect:
            logger.info("已处于连接状态，无需重复连接")
            return

        # 取消现有重连任务
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                logger.info("旧重连任务已取消")

        # 重置连接状态和跟踪记录
        await self._reset_connection_state()
        await self._clear_tracking_messages()
        await self._set_consumer_tag(None)  # 重置消费者标签（停止消费）

        retries = 0
        last_exception = None

        while retries < self.max_reconnection_attempts:
            try:
                # 获取新通道
                channel = await self._get_channel()
                await channel.set_qos(prefetch_count=self.prefetch_count)

                # 处理交换机
                exchange_exists = await self._check_exchange_exists(channel)
                if not exchange_exists:
                    if self.create_if_not_exists:
                        exchange = await asyncio.wait_for(
                            channel.declare_exchange(
                                name=self.exchange_name,
                                type=self.exchange_type,
                                durable=self.durable,
                                auto_delete=self.auto_delete
                            ),
                            timeout=self.rpc_timeout
                        )
                        logger.info(f"已创建交换机 '{self.exchange_name}'")
                    else:
                        raise Exception(
                            f"交换机 '{self.exchange_name}' 不存在且不允许自动创建")
                else:
                    exchange = await channel.get_exchange(self.exchange_name)
                    logger.info(f"使用已存在的交换机 '{self.exchange_name}'")

                # 处理队列
                queue = None
                if declare_queue and self.queue_name:
                    queue_exists = await self._check_queue_exists(channel)

                    if not queue_exists:
                        if not self.create_if_not_exists:
                            raise Exception(
                                f"队列 '{self.queue_name}' 不存在且不允许自动创建")

                        queue = await asyncio.wait_for(
                            channel.declare_queue(
                                name=self.queue_name,
                                durable=self.durable,
                                auto_delete=self.auto_delete,
                                exclusive=False
                            ),
                            timeout=self.rpc_timeout
                        )
                        logger.info(f"已创建队列 '{self.queue_name}'")
                    else:
                        queue = await channel.get_queue(self.queue_name)
                        logger.info(f"使用已存在的队列 '{self.queue_name}'")

                    # 绑定队列到交换机
                    if queue and exchange:
                        bound = await self._bind_queue(channel, queue, exchange)
                        if not bound:
                            raise Exception(f"队列 '{queue.name}' 绑定到交换机失败")

                # 更新连接资源
                await self._update_connection_resources(channel, exchange, queue)

                # 验证连接状态
                if not await self.is_connected:
                    raise Exception("连接验证失败，状态异常")

                # 重新开始消费（如果已设置处理器且之前在消费）
                _, handler, consumer_tag = await self._get_consume_state()
                if handler and consumer_tag:  # 有处理器且之前有消费标签，说明需要恢复消费
                    await self.start_consuming()

                # 启动监控和保活任务
                self._start_monitoring()
                self._start_keepalive()

                self._update_activity_timestamp()

                # 首次启动时延迟1秒（避免初始化未完成就接收消息）
                if not force_reconnect:
                    logger.info("客户端初始化成功，延迟1秒接收消息（解决启动时序问题）")
                    await asyncio.sleep(1)

                logger.info(f"RabbitMQ客户端初始化成功 (队列: {self.actual_queue_name})")
                return

            except Exception as e:
                last_exception = e
                logger.warning(f"资源初始化失败: {str(e)}，重试中...")
                retries += 1
                if retries < self.max_reconnection_attempts:
                    await asyncio.sleep(self.reconnection_delay)

        logger.error(f"最终初始化失败: {str(last_exception)}")
        raise Exception(
            f"经过{self.max_reconnection_attempts}次重试后仍无法初始化客户端。最后错误: {str(last_exception)}")

    def _start_monitoring(self) -> None:
        """启动连接和消费监控任务（无锁，仅通过原子方法访问状态）"""
        if self._monitor_task and not self._monitor_task.done():
            return

        async def monitor():
            while not await self._is_closed():
                try:
                    # 检查通道状态
                    channel, _, _ = await self._get_connection_resources()
                    if channel and channel.is_closed:
                        logger.warning("检测到通道已关闭，尝试重建")
                        await self._recreate_channel()
                        continue

                    current_time = asyncio.get_event_loop().time()

                    # 清理已确认的跟踪记录
                    cleaned_count = await self._cleanup_acked_tracking_messages()
                    if cleaned_count > 0:
                        logger.info(f"清理了 {cleaned_count} 条已确认消息记录")

                    # 检查消费停滞（仅当有消费者标签时）
                    _, handler, consumer_tag = await self._get_consume_state()
                    if consumer_tag:  # 有消费标签说明正在消费
                        tracking_count = await self._get_tracking_count()
                        if current_time - self._last_message_processed > self.consumption_stall_threshold:
                            if tracking_count > 0:
                                logger.warning(
                                    f"消费停滞，但有 {tracking_count} 个消息正在处理，暂不重启")
                            else:
                                logger.info("消费停滞且无消息处理，重启消费")
                                try:
                                    await self.stop_consuming()
                                    await asyncio.sleep(1)
                                    # 检查处理器是否存在
                                    _, handler, _ = await self._get_consume_state()
                                    if handler:
                                        await self.start_consuming()
                                    else:
                                        logger.error("消费处理器已丢失，无法重启消费")
                                except Exception as e:
                                    logger.error(
                                        f"重启消费失败: {str(e)}", exc_info=True)
                                    await self._set_consumer_tag(None)

                except Exception as e:
                    logger.error(f"监控任务出错: {str(e)}", exc_info=True)

                await asyncio.sleep(60)  # 监控间隔60秒

        self._monitor_task = asyncio.create_task(monitor())
        logger.info("监控任务已启动")

    async def _recreate_channel(self) -> None:
        """重建通道并恢复资源（无锁嵌套）"""
        # 先停止消费
        await self._set_consumer_tag(None)
        logger.info("开始重建通道...")

        try:
            # 获取新通道
            channel = await self._get_channel()
            await channel.set_qos(prefetch_count=self.prefetch_count)

            # 重新获取交换机
            exchange = await channel.get_exchange(self.exchange_name)

            # 重新获取队列并绑定
            queue = None
            if self.queue_name:
                queue = await channel.get_queue(self.queue_name)
                if queue and exchange:
                    bound = await self._bind_queue(channel, queue, exchange)
                    if not bound:
                        raise Exception("队列绑定失败，通道重建不完整")

            # 更新连接资源
            await self._update_connection_resources(channel, exchange, queue)

            # 重新开始消费（如果有处理器）
            _, handler, _ = await self._get_consume_state()
            if handler:
                await self.start_consuming()

            # 清空跟踪记录
            await self._clear_tracking_messages()
            logger.info("通道已重建并恢复服务")
            self._update_activity_timestamp()
        except Exception as e:
            logger.error(f"通道重建失败: {str(e)}，触发重连", exc_info=True)
            await self._set_consumer_tag(None)
            await self.connect(force_reconnect=True)

    def _start_keepalive(self) -> None:
        """启动连接保活任务（无锁，仅通过原子方法访问状态）"""
        if self._keepalive_task and not self._keepalive_task.done():
            return

        async def keepalive():
            while not await self._is_closed():
                try:
                    # 检查连接状态
                    if not await self.is_connected:
                        logger.warning("保活任务检测到连接断开，触发重连")
                        await self.connect(force_reconnect=True)
                        await asyncio.sleep(5)
                        continue

                    current_time = asyncio.get_event_loop().time()
                    # 检查活动时间
                    if current_time - self._last_activity_timestamp > self.connection_pool.heartbeat * 2:
                        logger.info(
                            f"连接 {self.connection_pool.heartbeat*2}s 无活动，执行保活检查")
                        channel, exchange, _ = await self._get_connection_resources()
                        if channel and not channel.is_closed and exchange:
                            # 轻量级操作：检查交换机是否存在
                            await asyncio.wait_for(
                                channel.declare_exchange(
                                    name=self.exchange_name,
                                    type=self.exchange_type,
                                    passive=True
                                ),
                                timeout=5
                            )
                            self._update_activity_timestamp()
                            logger.info("保活检查成功")
                        else:
                            raise Exception("连接资源无效")

                except Exception as e:
                    logger.warning(f"保活检查失败: {str(e)}，触发重连")
                    await self.connect(force_reconnect=True)

                await asyncio.sleep(self.connection_pool.heartbeat)

        self._keepalive_task = asyncio.create_task(keepalive())
        logger.info("保活任务已启动")

    async def _schedule_reconnect(self) -> None:
        """安排重新连接（无锁）"""
        if self._reconnect_task and not self._reconnect_task.done():
            return

        logger.info(f"将在 {self.reconnection_delay} 秒后尝试重新连接...")

        async def reconnect():
            try:
                await asyncio.sleep(self.reconnection_delay)
                if not await self._is_closed():
                    await self.connect(force_reconnect=True)
            except Exception as e:
                logger.error(f"重连任务失败: {str(e)}")
                if not await self._is_closed():
                    await self._schedule_reconnect()

        self._reconnect_task = asyncio.create_task(reconnect())

    async def close(self) -> None:
        """关闭客户端并释放资源（原子操作，无锁嵌套）"""
        if await self._is_closed():
            logger.info("客户端已关闭，无需重复操作")
            return

        logger.info("开始关闭RabbitMQ客户端...")

        # 标记为已关闭
        await self._mark_closed()

        # 停止消费
        await self.stop_consuming()

        # 取消所有后台任务
        tasks = [self._keepalive_task,
                 self._reconnect_task, self._monitor_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"任务 {task.get_name()} 已取消")

        # 重置所有状态和资源
        await self._reset_connection_state()
        await self._clear_tracking_messages()
        async with self._consume_state_lock:
            self.message_handler = None
            self._consumer_tag = None

        logger.info("RabbitMQ客户端已完全关闭")

    async def publish(
        self,
        message_body: Union[str, Dict[str, Any]],
        routing_key: Optional[str] = None,
        content_type: str = "application/json",
        headers: Optional[Dict[str, Any]] = None,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    ) -> None:
        """发布消息（从池获取通道，自动重试，无锁冲突）"""
        if await self._is_closed():
            raise Exception("客户端已关闭，无法发布消息")

        # 检查连接状态
        if not await self.is_connected:
            logger.warning("连接已断开，尝试重连后发布消息")
            await self.connect(force_reconnect=True)

        # 处理消息体
        if isinstance(message_body, dict):
            message_body_str = json.dumps(message_body, ensure_ascii=False)
            if content_type == "text/plain":
                content_type = "application/json"
        else:
            message_body_str = str(message_body)

        # 创建消息对象
        message = Message(
            body=message_body_str.encode(),
            content_type=content_type,
            headers=headers or {},
            delivery_mode=delivery_mode
        )

        # 发布消息（带重试机制）
        retry_count = 0
        max_retries = 2
        while retry_count < max_retries:
            try:
                async with self.connection_pool.channel_pool.acquire() as publish_channel:
                    exchange = await publish_channel.get_exchange(self.exchange_name)
                    confirmed = await exchange.publish(
                        message,
                        routing_key=routing_key or self.routing_key or '#',
                        mandatory=True,
                        timeout=5
                    )
                    if not confirmed:
                        raise Exception("消息未被服务器确认接收")

                self._update_activity_timestamp()
                logger.info(
                    f"消息已发布到交换机 '{self.exchange_name}'（路由键: {routing_key or self.routing_key or '#'}）")
                return
            except (ConnectionClosed, ChannelInvalidStateError, asyncio.TimeoutError):
                retry_count += 1
                logger.warning(f"连接异常，尝试重连后重新发布 (重试次数: {retry_count})")
                await self.connect(force_reconnect=True)
            except Exception as e:
                retry_count += 1
                logger.error(f"消息发布失败 (重试次数: {retry_count}): {str(e)}")
                if retry_count < max_retries:
                    await asyncio.sleep(1)

        raise Exception(f"消息发布失败，经过{retry_count}次重试仍未成功")

    async def _safe_cancel_consumer(self, consumer_tag: ConsumerTag, queue: AbstractQueue) -> bool:
        """安全取消消费者（无锁，仅操作传入的局部变量）"""
        try:
            await asyncio.wait_for(
                queue.cancel(consumer_tag),
                timeout=self.rpc_timeout
            )
            logger.info(f"消费者 {consumer_tag} 已取消")
            return True
        except Exception as e:
            logger.error(f"取消消费者 {consumer_tag} 异常: {str(e)}")
            return False

    async def start_consuming(self) -> ConsumerTag:
        """启动消费（无锁嵌套，通过原子方法获取/更新状态）"""
        # 检查客户端状态
        if await self._is_closed():
            raise Exception("客户端已关闭，无法启动消费")

        # 检查连接状态（确保通道完全就绪）
        if not await self.is_connected:
            await self.connect()

        # 确保通道未关闭（解决启动时通道初始化滞后问题）
        channel, _, _ = await self._get_connection_resources()
        max_wait_attempts = 5
        wait_interval = 0.5
        for attempt in range(max_wait_attempts):
            if channel and not channel.is_closed:
                break
            logger.debug(f"等待通道就绪（第{attempt+1}/{max_wait_attempts}次）")
            await asyncio.sleep(wait_interval)
            channel, _, _ = await self._get_connection_resources()
        if not channel or channel.is_closed:
            raise Exception("通道初始化失败，无法启动消费")

        # 获取消费状态和资源
        _, handler, consumer_tag = await self._get_consume_state()
        _, exchange, queue = await self._get_connection_resources()

        # 检查是否已在消费（通过 consumer_tag 是否存在判断）
        if consumer_tag:
            logger.info(f"已经在消费中，返回现有consumer_tag: {consumer_tag}")
            return consumer_tag

        # 检查必要条件
        if not handler:
            raise Exception("未设置消息处理函数，请先调用set_message_handler")
        if not queue:
            raise Exception("队列未初始化，无法开始消费")
        if not channel or channel.is_closed:
            raise Exception("通道无效，无法开始消费")

        try:
            # 启动消费
            new_consumer_tag = await queue.consume(
                self._message_wrapper,
                no_ack=False  # 手动确认消息
            )

            if not new_consumer_tag:
                raise Exception("未能获取到有效的consumer_tag")

            # 更新消费状态（设置消费者标签）
            await self._set_consumer_tag(new_consumer_tag)
            logger.info(
                f"消费者已启动，队列: {queue.name}, tag: {new_consumer_tag}")
            return new_consumer_tag
        except Exception as e:
            # 异常时回滚状态
            await self._set_consumer_tag(None)
            logger.error(f"启动消费失败: {str(e)}", exc_info=True)
            raise

    async def stop_consuming(self) -> None:
        """停止消费（无锁嵌套，通过原子方法获取/更新状态）"""
        # 获取消费状态和资源
        _, _, consumer_tag = await self._get_consume_state()
        _, _, queue = await self._get_connection_resources()

        if not consumer_tag:  # 无消费标签说明未在消费
            logger.info("未处于消费状态，无需停止")
            return

        logger.info(f"开始停止消费（consumer_tag: {consumer_tag}）")

        # 先清除消费标签
        await self._set_consumer_tag(None)

        # 取消消费者
        if consumer_tag and queue and not await self._is_closed():
            await self._safe_cancel_consumer(consumer_tag, queue)

        # 等待所有正在处理的消息完成
        tracking_count = await self._get_tracking_count()
        if tracking_count > 0:
            logger.info(f"等待 {tracking_count} 个正在处理的消息完成...")
            wait_start = asyncio.get_event_loop().time()
            while True:
                # 检查是否超时或已关闭
                if await self._is_closed() or asyncio.get_event_loop().time() - wait_start > 30:
                    timeout = asyncio.get_event_loop().time() - wait_start > 30
                    if timeout:
                        logger.warning("等待消息处理超时，强制清理跟踪记录")
                        await self._clear_tracking_messages()
                    break
                # 检查跟踪记录是否为空
                current_count = await self._get_tracking_count()
                if current_count == 0:
                    break
                await asyncio.sleep(1)

        logger.info(f"已停止消费队列: {queue.name if queue else '未知'}")

    async def _parse_message(self, message: AbstractIncomingMessage) -> Union[Dict[str, Any], str]:
        """解析消息体（无锁，仅处理局部变量）"""
        try:
            body_str = message.body.decode('utf-8')
            self._update_activity_timestamp()

            if self.auto_parse_json:
                return json.loads(body_str)
            return body_str
        except json.JSONDecodeError:
            logger.warning(
                f"消息 {message.message_id or id(message)} 解析JSON失败，返回原始字符串")
            return body_str
        except Exception as e:
            logger.error(
                f"消息 {message.message_id or id(message)} 解析出错: {str(e)}")
            return message.body.decode('utf-8')

    async def _handle_business_retry(
        self,
        message: AbstractIncomingMessage,
        error: Exception,
        drop: bool = True
    ) -> None:
        """
        封装业务失败重试逻辑：更新重试计数Header，延迟3秒重新发布
        达到最大次数则标记失败（无锁，仅通过原子方法操作跟踪记录）
        """
        # 获取当前重试次数
        current_headers = message.headers or {}
        retry_count = current_headers.get('x-retry-count', 0)
        retry_count += 1
        message_id = message.message_id or str(id(message))

        error_msg = f"[{type(error).__name__}] {str(error)}"[:200]

        # 打印错误日志
        logger.error(
            f"消息 {message_id} 处理出错（第{retry_count}次重试）: {error_msg}",
            exc_info=True
        )

        # 达到最大重试次数：ack标记失败
        if drop and retry_count >= MAX_RETRY_COUNT:
            logger.error(
                f"消息 {message_id} 已达到最大重试次数{MAX_RETRY_COUNT}，标记为失败")
            # 标记跟踪记录为已确认
            await self._mark_tracking_acked(message_id)
            await message.ack()
            self._update_activity_timestamp()
            return

        # 构造新消息Header
        new_headers = current_headers.copy()
        new_headers['x-retry-count'] = retry_count
        new_headers['x-retry-error'] = error_msg

        # 提交异步任务，延迟3秒后重新发布
        asyncio.create_task(
            self._delayed_republish(
                message, new_headers, retry_count, message_id)
        )

    async def _delayed_republish(
        self,
        message: AbstractIncomingMessage,
        new_headers: Dict[str, Any],
        retry_count: int,
        message_id: str
    ) -> None:
        """延迟发布重试消息（无锁，仅通过原子方法操作资源）"""
        try:
            # 延迟3秒重试
            await asyncio.sleep(3)

            # 检查客户端状态
            if await self._is_closed():
                logger.warning(f"客户端已关闭，放弃消息 {message_id} 的重试发布")
                return

            # 获取交换机
            _, exchange, _ = await self._get_connection_resources()
            if not exchange:
                raise Exception("交换机未初始化，无法发布重试消息")

            # 构造新消息
            new_message = Message(
                body=message.body,
                content_type=message.content_type,
                headers=new_headers,
                delivery_mode=message.delivery_mode
            )

            # 重新发布消息
            await exchange.publish(
                new_message,
                routing_key=self.routing_key or '#',
                mandatory=True,
                timeout=5.0
            )
            self._update_activity_timestamp()
            logger.info(f"消息 {message_id} 已重新发布，当前重试次数: {retry_count}")

            # 拒绝原始消息（不重新入队）
            await message.reject(requeue=False)
            # 标记跟踪记录为已确认
            await self._mark_tracking_acked(message_id)

        except Exception as e:
            logger.error(
                f"消息 {message_id} 延迟发布失败（错误：{str(e)}），触发requeue兜底",
                exc_info=True
            )
            # 发布失败兜底：requeue原始消息
            await message.reject(requeue=True)

    async def _message_wrapper(self, message: AbstractIncomingMessage) -> None:
        """消息处理包装器（无锁嵌套，仅通过原子方法操作状态）"""
        message_id = message.message_id or str(id(message))
        max_check_attempts = 3
        check_interval = 1

        # 重试检查消费状态（处理极端并发场景）
        for attempt in range(max_check_attempts):
            _, handler, consumer_tag = await self._get_consume_state()
            if consumer_tag and handler:  # 有消费标签且有处理器才继续
                break
            if attempt < max_check_attempts - 1:
                logger.debug(
                    f"消息 {message_id} 处理状态检查重试（第{attempt+1}次）: "
                    f"handler={'存在' if handler else '不存在'}, "
                    f"consumer_tag={'存在' if consumer_tag else '不存在'}"
                )
                await asyncio.sleep(check_interval)

        # 最终状态判断：状态异常则拒绝消息
        _, handler, consumer_tag = await self._get_consume_state()
        if not consumer_tag or not handler:
            err_msg = f"消息 {message_id} 拒绝处理：handler={'存在' if handler else '不存在'}, consumer_tag={'存在' if consumer_tag else '不存在'}"
            logger.warning(err_msg)
            try:
                await self._handle_business_retry(message, Exception(err_msg), drop=False)
            except Exception as e:
                logger.error(f"消息 {message_id} 拒绝处理失败: {e}")
            return

        # 检查重复处理
        if await self._check_duplicate_message(message_id):
            logger.warning(f"检测到重复处理的消息ID: {message_id}，直接确认")
            await message.ack()
            return

        # 添加跟踪记录
        channel, _, _ = await self._get_connection_resources()
        channel_number = channel.number if channel else None
        await self._add_tracking_message(message_id, message.delivery_tag, channel_number)

        try:
            logger.info(f"收到队列 {self.actual_queue_name} 的消息: {message_id}")

            # 解析消息
            parsed_data = await self._parse_message(message)
            # 转换为MQMsgModel
            if isinstance(parsed_data, dict):
                msg_model = MQMsgModel(**parsed_data)
            else:
                msg_model = MQMsgModel(data=parsed_data)

            # 调用业务处理器
            await handler(msg_model, message)

            # 处理成功：标记跟踪记录并确认消息
            await self._mark_tracking_acked(message_id)
            await message.ack()
            self._update_activity_timestamp()
            self._update_message_processed_timestamp()
            logger.info(f"消息 {message_id} 处理完成并确认")

        except Exception as e:
            # 业务处理失败：触发重试逻辑
            await self._handle_business_retry(message, e)
        finally:
            # 清理跟踪记录
            await self._remove_tracking_message(message_id)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
