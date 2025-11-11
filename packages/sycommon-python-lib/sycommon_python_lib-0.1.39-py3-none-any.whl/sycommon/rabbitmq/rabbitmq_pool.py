import asyncio
from typing import List, Set
from aio_pika import connect_robust, Channel
from aio_pika.abc import AbstractRobustConnection

from sycommon.logging.kafka_log import SYLogger

logger = SYLogger


class RabbitMQConnectionPool:
    """RabbitMQ连接池管理（简化实现，避免上下文管理器冲突）"""

    def __init__(
        self,
        hosts: List[str],
        port: int,
        username: str,
        password: str,
        virtualhost: str = "/",
        connection_pool_size: int = 2,
        channel_pool_size: int = 10,
        heartbeat: int = 10,
        app_name: str = ""
    ):
        self.hosts = [host.strip() for host in hosts if host.strip()]
        if not self.hosts:
            raise ValueError("至少需要提供一个RabbitMQ主机地址")
        self.port = port
        self.username = username
        self.password = password
        self.virtualhost = virtualhost
        self.app_name = app_name or "rabbitmq-client"
        self.heartbeat = heartbeat

        # 连接池配置
        self.connection_pool_size = connection_pool_size
        self.channel_pool_size = channel_pool_size

        # 实际存储的连接和通道
        self._connections: List[AbstractRobustConnection] = []
        self._free_channels: List[Channel] = []
        self._used_channels: Set[Channel] = set()

        # 锁用于线程安全
        self._conn_lock = asyncio.Lock()
        self._chan_lock = asyncio.Lock()

        # 连接状态
        self._initialized = False

    async def init_pools(self):
        """初始化连接池（创建指定数量的连接）"""
        if self._initialized:
            logger.warning("连接池已初始化，无需重复调用")
            return

        try:
            # 创建核心连接（数量=connection_pool_size）
            for i in range(self.connection_pool_size):
                conn = await self._create_connection()
                self._connections.append(conn)
                # 为每个连接创建初始通道（数量=channel_pool_size//connection_pool_size）
                chan_count_per_conn = self.channel_pool_size // self.connection_pool_size
                for _ in range(chan_count_per_conn):
                    chan = await conn.channel()
                    self._free_channels.append(chan)

            self._initialized = True
            logger.info(
                f"RabbitMQ连接池初始化成功 - 连接数: {len(self._connections)}, "
                f"空闲通道数: {len(self._free_channels)}, 集群节点: {self.hosts}"
            )
        except Exception as e:
            logger.error(f"连接池初始化失败: {str(e)}", exc_info=True)
            # 清理异常状态
            await self.close()
            raise

    async def _create_connection(self) -> AbstractRobustConnection:
        """创建单个RabbitMQ连接（支持集群节点轮询）"""
        hosts = self.hosts.copy()
        while hosts:
            host = hosts.pop(0)
            try:
                connection = await connect_robust(
                    host=host,
                    port=self.port,
                    login=self.username,
                    password=self.password,
                    virtualhost=self.virtualhost,
                    heartbeat=self.heartbeat,
                    client_properties={
                        "connection_name": f"{self.app_name}@{host}"
                    },
                    reconnect_interval=2  # aio_pika 内置重连间隔
                )
                logger.info(f"成功连接到 RabbitMQ 节点: {host}:{self.port}")
                return connection
            except Exception as e:
                logger.warning(
                    f"连接主机 {host}:{self.port} 失败，尝试下一个节点: {str(e)}")
                if not hosts:
                    raise  # 所有节点失败时抛出异常

    async def acquire_channel(self) -> Channel:
        """获取通道（从空闲通道池获取，无则创建新通道）"""
        if not self._initialized:
            raise RuntimeError("连接池未初始化，请先调用 init_pools()")

        async with self._chan_lock:
            # 优先从空闲通道池获取
            if self._free_channels:
                channel = self._free_channels.pop()
                # 检查通道是否有效
                if not channel.is_closed:
                    self._used_channels.add(channel)
                    return channel
                else:
                    logger.warning("发现无效通道，已自动清理")

            # 空闲通道不足，创建新通道（不超过最大限制）
            if len(self._used_channels) < self.channel_pool_size:
                # 选择一个空闲连接创建通道
                async with self._conn_lock:
                    for conn in self._connections:
                        if not conn.is_closed:
                            try:
                                channel = await conn.channel()
                                self._used_channels.add(channel)
                                logger.info(
                                    f"创建新通道，当前通道数: {len(self._used_channels)}/{self.channel_pool_size}")
                                return channel
                            except Exception as e:
                                logger.warning(f"使用连接创建通道失败: {str(e)}")
                    # 所有连接都无效，尝试重新创建连接
                    conn = await self._create_connection()
                    self._connections.append(conn)
                    channel = await conn.channel()
                    self._used_channels.add(channel)
                    return channel
            else:
                raise RuntimeError(f"通道池已达最大限制: {self.channel_pool_size}")

    async def release_channel(self, channel: Channel):
        """释放通道（归还到空闲通道池）"""
        async with self._chan_lock:
            if channel in self._used_channels:
                self._used_channels.remove(channel)
                # 通道有效则归还，无效则丢弃
                if not channel.is_closed:
                    self._free_channels.append(channel)
                else:
                    logger.warning("释放无效通道，已自动丢弃")

    async def close(self):
        """关闭连接池（释放所有连接和通道）"""
        # 释放所有通道
        async with self._chan_lock:
            for channel in self._free_channels + list(self._used_channels):
                try:
                    if not channel.is_closed:
                        await channel.close()
                except Exception as e:
                    logger.warning(f"关闭通道失败: {str(e)}")
            self._free_channels.clear()
            self._used_channels.clear()

        # 关闭所有连接
        async with self._conn_lock:
            for conn in self._connections:
                try:
                    if not conn.is_closed:
                        await conn.close()
                except Exception as e:
                    logger.warning(f"关闭连接失败: {str(e)}")
            self._connections.clear()

        self._initialized = False
        logger.info("RabbitMQ连接池已完全关闭")
