from aio_pika import Channel
from typing import Optional
import asyncio
import json
from typing import Callable, Coroutine, Dict, Any, Union
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import (
    AbstractExchange,
    AbstractQueue,
    AbstractIncomingMessage,
    ConsumerTag,
    AbstractRobustConnection
)
from sycommon.rabbitmq.rabbitmq_pool import RabbitMQConnectionPool
from sycommon.logging.kafka_log import SYLogger
from sycommon.models.mqmsg_model import MQMsgModel


# 最大重试次数限制
MAX_RETRY_COUNT = 3

logger = SYLogger


class RabbitMQClient:
    """
    RabbitMQ 客户端（支持消息发布、消费、自动重连、异常重试）
    核心特性：
    1. 基于连接池复用资源，性能优化
    2. 连接/通道失效时自动重建，高可用
    3. 消息发布支持重试，消费支持手动ACK/NACK
    4. 兼容JSON/字符串/字典消息格式
    5. 严格的协程调用规范，避免"未等待"警告
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
        prefetch_count: int = 2,
        # 兼容旧代码参数（无需使用）
        **kwargs,
    ):
        # 依赖注入：连接池（必须已初始化）
        self.connection_pool = connection_pool
        if not self.connection_pool._initialized:
            raise RuntimeError("连接池未初始化，请先调用 connection_pool.init_pools()")

        # 交换机配置
        self.exchange_name = exchange_name.strip()
        try:
            self.exchange_type = ExchangeType(exchange_type.lower())
        except ValueError:
            SYLogger.warning(f"无效的exchange_type: {exchange_type}，默认使用'topic'")
            self.exchange_type = ExchangeType.topic

        # 队列配置
        self.queue_name = queue_name.strip() if queue_name else None
        self.routing_key = routing_key.strip() if routing_key else "#"
        self.durable = durable  # 消息/队列持久化
        self.auto_delete = auto_delete  # 无消费者时自动删除队列/交换机
        self.auto_parse_json = auto_parse_json  # 自动解析JSON消息体
        self.create_if_not_exists = create_if_not_exists  # 不存在则创建交换机/队列

        # 消费配置
        self.prefetch_count = max(1, prefetch_count)  # 每次预取消息数（避免消息堆积）

        # 内部状态（资源+连接）
        self._channel: Optional[Channel] = None
        self._channel_conn: Optional[AbstractRobustConnection] = None  # 通道所属连接
        self._exchange: Optional[AbstractExchange] = None
        self._queue: Optional[AbstractQueue] = None
        self._consumer_tag: Optional[ConsumerTag] = None
        self._message_handler: Optional[Callable[[
            MQMsgModel, AbstractIncomingMessage], Coroutine[Any, Any, None]]] = None
        self._closed = False

        # 线程安全锁
        self._consume_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()

    @property
    async def is_connected(self) -> bool:
        """异步检查客户端连接状态（属性，不可调用）"""
        if self._closed:
            return False
        try:
            # 校验通道+连接+核心资源都有效
            return (
                self._channel and not self._channel.is_closed
                and self._channel_conn and not self._channel_conn.is_closed
                and self._exchange is not None
                and (not self.queue_name or self._queue is not None)
            )
        except Exception as e:
            SYLogger.warning(f"检查连接状态失败: {str(e)}")
            return False

    async def connect(self) -> None:
        """建立连接并初始化交换机/队列（支持重连）"""
        if self._closed:
            raise RuntimeError("客户端已关闭，无法重新连接")

        async with self._connect_lock:
            # 释放旧的无效资源
            if self._channel and self._channel_conn:
                try:
                    await self.connection_pool.release_channel(self._channel, self._channel_conn)
                except Exception as e:
                    SYLogger.warning(f"释放旧通道失败: {str(e)}")
            self._channel = None
            self._channel_conn = None
            self._exchange = None
            self._queue = None

            try:
                # 1. 从连接池获取通道+连接
                self._channel, self._channel_conn = await self.connection_pool.acquire_channel()

                # 2. 设置预取计数（限流）
                await self._channel.set_qos(prefetch_count=self.prefetch_count)
                SYLogger.debug(f"设置预取计数: {self.prefetch_count}")

                # 3. 声明交换机
                self._exchange = await self._channel.declare_exchange(
                    name=self.exchange_name,
                    type=self.exchange_type,
                    durable=self.durable,
                    auto_delete=self.auto_delete,
                    passive=not self.create_if_not_exists,  # passive=True时，不存在则报错
                )
                SYLogger.info(
                    f"交换机初始化成功: {self.exchange_name}（类型: {self.exchange_type.value}）")

                # 4. 声明队列（如果配置了队列名）
                if self.queue_name:
                    self._queue = await self._channel.declare_queue(
                        name=self.queue_name,
                        durable=self.durable,
                        auto_delete=self.auto_delete,
                        passive=not self.create_if_not_exists,
                    )
                    # 绑定队列到交换机
                    await self._queue.bind(
                        exchange=self._exchange,
                        routing_key=self.routing_key,
                    )
                    SYLogger.info(
                        f"队列初始化成功: {self.queue_name} "
                        f"（绑定交换机: {self.exchange_name}, routing_key: {self.routing_key}）"
                    )

                SYLogger.info("客户端连接初始化完成")
            except Exception as e:
                SYLogger.error(f"客户端连接失败: {str(e)}", exc_info=True)
                # 清理异常状态
                if self._channel and self._channel_conn:
                    try:
                        await self.connection_pool.release_channel(self._channel, self._channel_conn)
                    except:
                        pass
                self._channel = None
                self._channel_conn = None
                raise

    async def set_message_handler(
        self,
        handler: Callable[[MQMsgModel, AbstractIncomingMessage], Coroutine[Any, Any, None]],
    ) -> None:
        """设置消息处理器（必须是协程函数）"""
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError("消息处理器必须是协程函数（使用 async def 定义）")

        async with self._consume_lock:
            self._message_handler = handler
            SYLogger.info("消息处理器设置成功")

    async def start_consuming(self) -> Optional[ConsumerTag]:
        """启动消息消费（支持自动重连）"""
        if self._closed:
            raise RuntimeError("客户端已关闭，无法启动消费")

        async with self._consume_lock:
            # 1. 校验前置条件
            if not self._message_handler:
                raise RuntimeError("未设置消息处理器，请先调用 set_message_handler()")
            if not await self.is_connected:
                await self.connect()
            if not self._queue:
                raise RuntimeError("未配置队列名，无法启动消费")

            # 2. 定义消费回调（包含异常处理和重连逻辑）
            async def consume_callback(message: AbstractIncomingMessage):
                try:
                    # 解析消息体
                    if self.auto_parse_json:
                        try:
                            body_dict = json.loads(
                                message.body.decode("utf-8"))
                            msg_obj = MQMsgModel(**body_dict)
                        except json.JSONDecodeError as e:
                            SYLogger.error(
                                f"JSON消息解析失败: {str(e)}，消息体: {message.body[:100]}...")
                            await message.nack(requeue=False)  # 解析失败，不重入队
                            return
                    else:
                        msg_obj = MQMsgModel(
                            body=message.body.decode("utf-8"),
                            routing_key=message.routing_key,
                            delivery_tag=message.delivery_tag,
                        )

                    # 调用消息处理器（必须await，避免协程未等待警告）
                    await self._message_handler(msg_obj, message)

                    # 手动ACK（消息处理成功）
                    await message.ack()
                    SYLogger.debug(
                        f"消息处理成功，delivery_tag: {message.delivery_tag}")

                except Exception as e:
                    SYLogger.error(
                        f"消息处理失败，delivery_tag: {message.delivery_tag}",
                        exc_info=True
                    )
                    # 处理失败逻辑：首次失败重入队，再次失败丢弃
                    if message.redelivered:
                        SYLogger.warning(
                            f"消息已重入队过，本次拒绝入队: {message.delivery_tag}")
                        await message.reject(requeue=False)
                    else:
                        SYLogger.warning(f"消息重入队: {message.delivery_tag}")
                        await message.nack(requeue=True)

                    # 检查连接状态，失效则触发重连
                    if not await self.is_connected:
                        SYLogger.warning("连接已失效，触发客户端重连")
                        asyncio.create_task(self.connect())

            # 3. 启动消费
            self._consumer_tag = await self._queue.consume(consume_callback)
            SYLogger.info(
                f"开始消费队列: {self._queue.name}，consumer_tag: {self._consumer_tag}"
            )
            return self._consumer_tag

    async def stop_consuming(self) -> None:
        """停止消息消费"""
        async with self._consume_lock:
            if self._consumer_tag and self._queue and not self._queue.is_closed:
                try:
                    await self._queue.cancel(self._consumer_tag)
                    SYLogger.info(f"停止消费成功，consumer_tag: {self._consumer_tag}")
                except Exception as e:
                    SYLogger.error(f"停止消费失败: {str(e)}", exc_info=True)
                finally:
                    self._consumer_tag = None

    async def publish(
        self,
        message_body: Union[str, Dict[str, Any], MQMsgModel],
        headers: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT,
        retry_count: int = 3,
    ) -> None:
        """
        发布消息（支持自动重试、JSON序列化）
        :param message_body: 消息体（字符串/字典/MQMsgModel）
        :param headers: 消息头（可选）
        :param content_type: 内容类型（默认application/json）
        :param delivery_mode: 投递模式（PERSISTENT=持久化，TRANSIENT=非持久化）
        :param retry_count: 重试次数（默认3次）
        """
        if self._closed:
            raise RuntimeError("客户端已关闭，无法发布消息")

        # 处理消息体序列化
        try:
            if isinstance(message_body, MQMsgModel):
                body = json.dumps(message_body.to_dict(),
                                  ensure_ascii=False).encode("utf-8")
            elif isinstance(message_body, dict):
                body = json.dumps(
                    message_body, ensure_ascii=False).encode("utf-8")
            elif isinstance(message_body, str):
                body = message_body.encode("utf-8")
            else:
                raise TypeError(f"不支持的消息体类型: {type(message_body)}")
        except Exception as e:
            SYLogger.error(f"消息体序列化失败: {str(e)}", exc_info=True)
            raise

        # 构建消息对象
        message = Message(
            body=body,
            headers=headers or {},
            content_type=content_type,
            delivery_mode=delivery_mode,
        )

        # 发布重试逻辑
        for retry in range(retry_count):
            try:
                # 确保连接有效
                if not await self.is_connected:
                    SYLogger.warning(f"发布消息前连接失效，触发重连（retry: {retry}）")
                    await self.connect()

                # 发布消息
                await self._exchange.publish(
                    message=message,
                    routing_key=self.routing_key or self.queue_name or "#",
                )
                SYLogger.info(
                    f"消息发布成功（retry: {retry}），routing_key: {self.routing_key}，"
                    f"delivery_mode: {delivery_mode.value}"
                )
                return
            except Exception as e:
                SYLogger.error(
                    f"消息发布失败（retry: {retry}/{retry_count-1}）: {str(e)}",
                    exc_info=True
                )
                # 清理失效状态，下次重试时重连
                self._exchange = None
                # 重试间隔（指数退避）
                await asyncio.sleep(0.5 * (2 ** retry))

        # 所有重试失败，抛出异常
        raise RuntimeError(
            f"消息发布失败（已重试{retry_count}次），routing_key: {self.routing_key}"
        )

    async def close(self) -> None:
        """关闭客户端（释放资源）"""
        if self._closed:
            SYLogger.warning("客户端已关闭，无需重复操作")
            return

        self._closed = True
        SYLogger.info("开始关闭RabbitMQ客户端...")

        # 1. 停止消费
        await self.stop_consuming()

        # 2. 释放通道到连接池
        async with self._connect_lock:
            if self._channel and self._channel_conn:
                try:
                    await self.connection_pool.release_channel(self._channel, self._channel_conn)
                    SYLogger.info("通道释放成功")
                except Exception as e:
                    SYLogger.error(f"通道释放失败: {str(e)}", exc_info=True)
            self._channel = None
            self._channel_conn = None
            self._exchange = None
            self._queue = None
            self._message_handler = None

        SYLogger.info("RabbitMQ客户端已完全关闭")
