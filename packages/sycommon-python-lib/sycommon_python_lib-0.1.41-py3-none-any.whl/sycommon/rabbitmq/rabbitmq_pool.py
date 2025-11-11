import asyncio
from typing import List, Optional, Set, Tuple, cast
from aio_pika import connect_robust, Channel
from aio_pika.abc import AbstractRobustConnection, AbstractConnection

from sycommon.logging.kafka_log import SYLogger

logger = SYLogger


class RabbitMQConnectionPool:
    """增强版连接池，支持连接自动重建、通道有效性校验"""

    def __init__(
        self,
        hosts: List[str],
        port: int,
        username: str,
        password: str,
        virtualhost: str = "/",
        connection_pool_size: int = 2,
        channel_pool_size: int = 10,
        heartbeat: int = 30,
        app_name: str = "",
        reconnect_interval: int = 3,
        connection_timeout: int = 30
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
        self.reconnect_interval = reconnect_interval
        self.connection_timeout = connection_timeout

        # 连接池配置
        self.connection_pool_size = connection_pool_size
        self.channel_pool_size = channel_pool_size

        # 实际存储的连接和通道（用元组存储连接+最后活动时间，便于清理超时连接）
        self._connections: List[Tuple[AbstractRobustConnection, float]] = []
        self._free_channels: List[Tuple[Channel,
                                        AbstractRobustConnection]] = []  # 通道绑定所属连接
        self._used_channels: Set[Tuple[Channel,
                                       AbstractRobustConnection]] = set()

        # 锁用于线程安全
        self._conn_lock = asyncio.Lock()
        self._chan_lock = asyncio.Lock()

        # 连接状态
        self._initialized = False
        self._reconnect_task: Optional[asyncio.Task] = None

    async def init_pools(self):
        """初始化连接池+启动连接监控任务"""
        if self._initialized:
            logger.warning("连接池已初始化，无需重复调用")
            return

        try:
            # 创建初始连接
            await self._create_initial_connections()
            # 启动连接监控任务（后台检查并重建失效连接）
            self._reconnect_task = asyncio.create_task(
                self._monitor_connections())
            self._initialized = True
            logger.info(
                f"RabbitMQ连接池初始化成功 - 连接数: {len(self._connections)}, "
                f"空闲通道数: {len(self._free_channels)}, 集群节点: {self.hosts}"
            )
        except Exception as e:
            logger.error(f"连接池初始化失败: {str(e)}", exc_info=True)
            await self.close()
            raise

    async def _create_initial_connections(self):
        """创建初始连接和通道"""
        for i in range(self.connection_pool_size):
            try:
                conn = await self._create_single_connection()
                self._connections.append(
                    (conn, asyncio.get_event_loop().time()))
                # 为每个连接创建初始通道
                chan_count_per_conn = self.channel_pool_size // self.connection_pool_size
                for _ in range(chan_count_per_conn):
                    chan = await conn.channel()
                    self._free_channels.append((chan, conn))
            except Exception as e:
                logger.error(f"创建初始连接/通道失败（第{i+1}个）: {str(e)}", exc_info=True)
                # 允许部分连接失败，后续监控任务会重试
                continue

    async def _create_single_connection(self) -> AbstractRobustConnection:
        """创建单个RabbitMQ连接（支持集群轮询+失败重试）"""
        hosts = self.hosts.copy()
        retry_count = 0
        max_retries = 3  # 最大重试3次

        while retry_count < max_retries:
            if not hosts:
                hosts = self.hosts.copy()  # 所有节点尝试完毕，重新轮询
                retry_count += 1
                # 指数退避重试（1s, 2s, 4s）
                await asyncio.sleep(self.reconnect_interval * (2 ** (retry_count - 1)))

            host = hosts.pop(0)
            conn_url = (
                f"amqp://{self.username}:{self.password}@{host}:{self.port}/{self.virtualhost}"
                f"?heartbeat={self.heartbeat}&timeout={self.connection_timeout}"
            )

            try:
                conn = await connect_robust(
                    conn_url,
                    client_properties={
                        "connection_name": f"{self.app_name}@{host}"
                    },
                    reconnect_interval=self.reconnect_interval,
                )

                # 定义连接关闭回调函数（接收连接实例和异常信息）
                def on_connection_closed(conn_instance: AbstractConnection, exc: Optional[BaseException]):
                    logger.error(
                        f"RabbitMQ连接关闭: {conn_instance!r}，原因: {exc}", exc_info=exc)
                    # 异步触发连接重建（需用 asyncio.create_task 包装）
                    asyncio.create_task(
                        self._remove_invalid_connection(cast(AbstractRobustConnection, conn_instance)))

                # 直接向 close_callbacks 添加回调（AbstractConnection 原生支持）
                conn.close_callbacks.add(on_connection_closed)

                logger.info(f"成功连接到RabbitMQ节点: {host}:{self.port}")
                return conn
            except Exception as e:
                logger.warning(
                    f"连接节点 {host}:{self.port} 失败（重试{retry_count}/{max_retries}）: {str(e)}"
                )

        raise RuntimeError(
            f"所有RabbitMQ节点连接失败（已重试{max_retries}次），节点列表: {self.hosts}"
        )

    async def _remove_invalid_connection(self, invalid_conn: AbstractRobustConnection) -> None:
        """移除失效连接及关联通道"""
        # 1. 移除失效连接
        async with self._conn_lock:
            self._connections = [
                (conn, ts) for conn, ts in self._connections if conn != invalid_conn
            ]
        # 2. 移除该连接关联的所有通道
        async with self._chan_lock:
            self._free_channels = [
                (chan, conn) for chan, conn in self._free_channels if conn != invalid_conn
            ]
            self._used_channels = {
                (chan, conn) for chan, conn in self._used_channels if conn != invalid_conn
            }
        # 3. 触发连接重建
        asyncio.create_task(self._recreate_connection())

    async def _recreate_connection(self):
        """重建一个连接并补充通道"""
        try:
            conn = await self._create_single_connection()
            async with self._conn_lock:
                self._connections.append(
                    (conn, asyncio.get_event_loop().time()))
            # 补充通道
            chan_count_per_conn = self.channel_pool_size // self.connection_pool_size
            for _ in range(chan_count_per_conn):
                try:
                    chan = await conn.channel()
                    async with self._chan_lock:
                        self._free_channels.append((chan, conn))
                except Exception as e:
                    logger.warning(f"为新连接创建通道失败: {str(e)}")
        except Exception as e:
            logger.error(f"重建连接失败: {str(e)}", exc_info=True)

    async def _monitor_connections(self):
        """后台监控连接状态（每30秒检查一次）"""
        while self._initialized:
            try:
                await asyncio.sleep(30)
                current_time = asyncio.get_event_loop().time()
                async with self._conn_lock:
                    # 检查连接有效性+清理超时连接（10分钟无活动）
                    valid_connections = []
                    for conn, last_active in self._connections:
                        if conn.is_closed or (current_time - last_active) > 600:
                            logger.warning(f"清理失效/超时连接: {conn}")
                            try:
                                await conn.close()
                            except:
                                pass
                        else:
                            valid_connections.append((conn, last_active))
                    self._connections = valid_connections

                # 补充缺失的连接
                missing_conn_count = self.connection_pool_size - \
                    len(self._connections)
                for _ in range(missing_conn_count):
                    asyncio.create_task(self._recreate_connection())
            except Exception as e:
                logger.error(f"连接监控任务异常: {str(e)}", exc_info=True)

    async def acquire_channel(self) -> Tuple[Channel, AbstractRobustConnection]:
        """获取通道（返回通道+所属连接，便于释放时校验）"""
        if not self._initialized:
            raise RuntimeError("连接池未初始化，请先调用 init_pools()")

        async with self._chan_lock:
            # 优先从空闲通道池获取有效通道
            for i in range(len(self._free_channels)-1, -1, -1):
                chan, conn = self._free_channels[i]
                # 校验通道和连接是否有效
                if not conn.is_closed and not chan.is_closed:
                    # 更新连接最后活动时间
                    async with self._conn_lock:
                        for j, (c, ts) in enumerate(self._connections):
                            if c == conn:
                                self._connections[j] = (
                                    c, asyncio.get_event_loop().time())
                                break
                    # 移到已使用通道集合
                    self._free_channels.pop(i)
                    self._used_channels.add((chan, conn))
                    return chan, conn
                else:
                    # 移除无效通道
                    self._free_channels.pop(i)
                    logger.warning("清理无效空闲通道")

            # 空闲通道不足，创建新通道
            if len(self._used_channels) < self.channel_pool_size:
                # 选择一个有效连接创建通道
                async with self._conn_lock:
                    for conn, _ in self._connections:
                        if not conn.is_closed:
                            try:
                                chan = await conn.channel()
                                self._used_channels.add((chan, conn))
                                logger.info(
                                    f"创建新通道，当前通道数: {len(self._used_channels)}/{self.channel_pool_size}")
                                return chan, conn
                            except Exception as e:
                                logger.warning(f"使用连接创建通道失败: {str(e)}")
                    # 无有效连接，尝试创建新连接
                    try:
                        conn = await self._create_single_connection()
                        self._connections.append(
                            (conn, asyncio.get_event_loop().time()))
                        chan = await conn.channel()
                        self._used_channels.add((chan, conn))
                        return chan, conn
                    except Exception as e:
                        logger.error(f"创建新连接+通道失败: {str(e)}", exc_info=True)
                        raise RuntimeError("无可用连接创建通道")
            else:
                raise RuntimeError(f"通道池已达最大限制: {self.channel_pool_size}")

    async def release_channel(self, channel: Channel, conn: AbstractRobustConnection):
        """释放通道（校验有效性后归还）"""
        async with self._chan_lock:
            key = (channel, conn)
            if key in self._used_channels:
                self._used_channels.remove(key)
                # 通道和连接都有效才归还
                if not conn.is_closed and not channel.is_closed:
                    self._free_channels.append(key)
                else:
                    logger.warning("释放无效通道，已自动丢弃")

    async def close(self):
        """关闭连接池+监控任务"""
        self._initialized = False
        # 停止监控任务
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        # 释放所有通道
        async with self._chan_lock:
            for channel, conn in self._free_channels + list(self._used_channels):
                try:
                    if not channel.is_closed:
                        await channel.close()
                except Exception as e:
                    logger.warning(f"关闭通道失败: {str(e)}")
            self._free_channels.clear()
            self._used_channels.clear()

        # 关闭所有连接
        async with self._conn_lock:
            for conn, _ in self._connections:
                try:
                    if not conn.is_closed:
                        await conn.close()
                except Exception as e:
                    logger.warning(f"关闭连接失败: {str(e)}")
            self._connections.clear()

        logger.info("RabbitMQ连接池已完全关闭")
