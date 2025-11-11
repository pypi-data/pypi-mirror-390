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
)
from src.sycommon.rabbitmq.rabbitmq_pool import RabbitMQConnectionPool
from sycommon.logging.kafka_log import SYLogger
from sycommon.models.mqmsg_model import MQMsgModel


# 最大重试次数限制
MAX_RETRY_COUNT = 3

logger = SYLogger


class RabbitMQClient:
    """
    RabbitMQ客户端（基于连接池），支持集群、自动重连、消息发布/消费
    依赖 aio_pika 的内置重连机制，移除手动重连逻辑
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
        rpc_timeout: int = 10,
        prefetch_count: int = 2,
        consumption_stall_threshold: int = 60,
    ):
        self.connection_pool = connection_pool
        if not self.connection_pool._initialized:
            raise RuntimeError("连接池未初始化，请先调用 connection_pool.init_pools()")

        # 交换机配置
        self.exchange_name = exchange_name
        self.exchange_type = ExchangeType(exchange_type.lower())
        # 队列配置
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.durable = durable
        self.auto_delete = auto_delete
        self.auto_parse_json = auto_parse_json
        self.create_if_not_exists = create_if_not_exists

        # 运行时配置
        self.rpc_timeout = rpc_timeout
        self.prefetch_count = prefetch_count
        self.consumption_stall_threshold = consumption_stall_threshold

        # 内部状态
        self._channel: Optional[Channel] = None
        self._exchange: Optional[AbstractExchange] = None
        self._queue: Optional[AbstractQueue] = None
        self._consumer_tag: Optional[ConsumerTag] = None
        self._message_handler: Optional[Callable] = None
        self._closed = False

        # 细粒度锁
        self._consume_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()

    @property
    async def is_connected(self) -> bool:
        """异步检查客户端连接状态（属性，不是函数）"""
        if self._closed:
            return False
        try:
            # 检查通道是否有效
            if self._channel and not self._channel.is_closed:
                # 检查交换机和队列（如果需要）
                if self.create_if_not_exists and self.queue_name:
                    return bool(self._exchange and self._queue)
                return True
            return False
        except Exception as e:
            logger.warning(f"检查连接状态失败: {str(e)}")
            return False

    async def _get_connection_resources(self) -> tuple[Optional[Channel], Optional[AbstractExchange], Optional[AbstractQueue]]:
        """原子获取连接资源（通道、交换机、队列）"""
        async with self._connect_lock:
            return self._channel, self._exchange, self._queue

    async def connect(self) -> None:
        """建立连接并初始化交换机/队列（使用新的通道获取方式）"""
        if self._closed:
            raise RuntimeError("客户端已关闭，无法重新连接")

        async with self._connect_lock:
            try:
                # 关键修复：使用连接池的 acquire_channel 方法获取通道
                self._channel = await self.connection_pool.acquire_channel()
                # 设置预取计数
                await self._channel.set_qos(prefetch_count=self.prefetch_count)

                # 声明交换机
                self._exchange = await self._channel.declare_exchange(
                    name=self.exchange_name,
                    type=self.exchange_type,
                    durable=self.durable,
                    auto_delete=self.auto_delete,
                    passive=not self.create_if_not_exists  # 不创建时使用passive模式检查
                )

                # 声明队列（如果配置了队列名）
                if self.queue_name:
                    self._queue = await self._channel.declare_queue(
                        name=self.queue_name,
                        durable=self.durable,
                        auto_delete=self.auto_delete,
                        passive=not self.create_if_not_exists
                    )
                    # 绑定队列到交换机
                    await self._queue.bind(
                        exchange=self._exchange,
                        routing_key=self.routing_key or self.queue_name
                    )
                    logger.info(
                        f"队列 '{self.queue_name}' 已声明并绑定到交换机 '{self.exchange_name}' "
                        f"(exchange_type: {self.exchange_type}, routing_key: {self.routing_key})"
                    )
                else:
                    logger.info(
                        f"未配置队列名，仅初始化交换机 '{self.exchange_name}' (exchange_type: {self.exchange_type})")

                logger.info(f"RabbitMQ客户端连接成功（exchange: {self.exchange_name}）")
            except Exception as e:
                logger.error(f"客户端连接失败: {str(e)}", exc_info=True)
                # 清理异常状态
                if self._channel:
                    await self.connection_pool.release_channel(self._channel)
                self._channel = None
                self._exchange = None
                self._queue = None
                raise

    async def set_message_handler(self, handler: Callable[[MQMsgModel, AbstractIncomingMessage], Coroutine[Any, Any, None]]):
        """设置消息处理器（消费消息时使用）"""
        async with self._consume_lock:
            self._message_handler = handler
            logger.info("消息处理器已设置")

    async def start_consuming(self) -> Optional[ConsumerTag]:
        """启动消费（返回消费者标签）"""
        if self._closed:
            logger.warning("客户端已关闭，无法启动消费")
            return None

        async with self._consume_lock:
            # 检查前置条件
            if not self._message_handler:
                raise RuntimeError("未设置消息处理器，请先调用 set_message_handler")

            # 确保连接已建立
            if not await self.is_connected:
                await self.connect()

            # 确保队列已初始化
            _, _, queue = await self._get_connection_resources()
            if not queue:
                raise RuntimeError("队列未初始化，无法启动消费")

            # 定义消费回调
            async def consume_callback(message: AbstractIncomingMessage):
                try:
                    # 解析消息
                    if self.auto_parse_json:
                        body = json.loads(message.body.decode('utf-8'))
                        parsed_data = MQMsgModel(**body)
                    else:
                        parsed_data = MQMsgModel(
                            msg=message.body.decode('utf-8'))

                    # 调用处理器
                    await self._message_handler(parsed_data, message)
                    # 手动确认消息
                    await message.ack()
                except Exception as e:
                    logger.error(
                        f"处理消息失败 (delivery_tag: {message.delivery_tag}): {str(e)}", exc_info=True)
                    # 消费失败时重新入队（最多重试3次）
                    if message.redelivered:
                        logger.warning(
                            f"消息已重试过，拒绝入队 (delivery_tag: {message.delivery_tag})")
                        await message.reject(requeue=False)
                    else:
                        await message.nack(requeue=True)

            # 启动消费
            self._consumer_tag = await queue.consume(consume_callback)
            logger.info(
                f"开始消费队列 '{queue.name}'，consumer_tag: {self._consumer_tag}")
            return self._consumer_tag

    async def stop_consuming(self) -> None:
        """停止消费"""
        async with self._consume_lock:
            if self._consumer_tag and not self._closed:
                _, _, queue = await self._get_connection_resources()
                if queue and not queue.is_closed:
                    try:
                        await queue.cancel(self._consumer_tag)
                        logger.info(f"停止消费，consumer_tag: {self._consumer_tag}")
                    except Exception as e:
                        logger.error(f"停止消费失败: {str(e)}")
                self._consumer_tag = None

    async def publish(
        self,
        message_body: Union[str, Dict[str, Any], MQMsgModel],
        headers: Optional[Dict[str, Any]] = None,
        content_type: str = "application/json",
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    ) -> None:
        """发布消息（修复 is_closed 问题）"""
        if self._closed:
            raise RuntimeError("客户端已关闭，无法发布消息")

        # 确保连接已建立
        if not await self.is_connected:
            await self.connect()

        # 处理消息体
        if isinstance(message_body, MQMsgModel):
            body = json.dumps(message_body.__dict__,
                              ensure_ascii=False).encode('utf-8')
        elif isinstance(message_body, dict):
            body = json.dumps(message_body, ensure_ascii=False).encode('utf-8')
        else:
            body = str(message_body).encode('utf-8')

        # 创建消息
        message = Message(
            body=body,
            headers=headers or {},
            content_type=content_type,
            delivery_mode=delivery_mode
        )

        # 发布消息
        try:
            async with self._connect_lock:
                if not self._exchange:
                    # 交换机未初始化，重新声明
                    logger.warning("交换机未初始化，重新声明")
                    self._exchange = await self._channel.declare_exchange(
                        name=self.exchange_name,
                        type=self.exchange_type,
                        durable=self.durable,
                        auto_delete=self.auto_delete
                    )
                await self._exchange.publish(
                    message=message,
                    routing_key=self.routing_key or self.queue_name or "#"
                )
            logger.debug(f"消息发布成功（routing_key: {self.routing_key}）")
        except Exception as e:
            logger.error(f"发布消息失败: {str(e)}", exc_info=True)
            # 发布失败时清理状态，下次自动重连
            self._exchange = None
            raise

    async def close(self) -> None:
        """关闭客户端（释放通道）"""
        if self._closed:
            return

        self._closed = True
        logger.info("开始关闭RabbitMQ客户端...")

        # 先停止消费
        await self.stop_consuming()

        # 释放通道到连接池
        async with self._connect_lock:
            if self._channel and not self._channel.is_closed:
                try:
                    await self.connection_pool.release_channel(self._channel)
                except Exception as e:
                    logger.warning(f"释放通道失败: {str(e)}")
            self._channel = None
            self._exchange = None
            self._queue = None

        logger.info("RabbitMQ客户端已关闭")
