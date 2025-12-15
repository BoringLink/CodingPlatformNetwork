"""Neo4j 数据库连接管理"""

import asyncio
import time
from typing import Optional
from contextlib import asynccontextmanager
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
import structlog

from app.config import settings

logger = structlog.get_logger()


class Neo4jConnection:
    """Neo4j 连接管理器
    
    管理 Neo4j 数据库连接池和会话，支持健康检查和自动重连
    """
    
    def __init__(self):
        self._driver: Optional[AsyncDriver] = None
        self._connected: bool = False
        self._last_connection_attempt: Optional[float] = None
        self._connection_attempts: int = 0
        
    async def connect(self) -> None:
        """建立数据库连接
        
        实现自动重连机制，最多尝试3次
        """
        if self._driver is not None and self._connected:
            logger.warning("Neo4j driver already connected")
            return
            
        max_attempts = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_attempts):
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                    max_connection_pool_size=settings.neo4j_max_connection_pool_size,
                    connection_timeout=settings.neo4j_connection_timeout,
                    max_transaction_retry_time=settings.neo4j_max_transaction_retry_time,
                )
                
                # 验证连接
                await self._driver.verify_connectivity()
                self._connected = True
                self._connection_attempts = 0
                self._last_connection_attempt = None
                
                logger.info(
                    "neo4j_connected",
                    uri=settings.neo4j_uri,
                    database=settings.neo4j_database,
                )
                return
            except Exception as e:
                self._connection_attempts += 1
                self._last_connection_attempt = time.time()
                
                if attempt < max_attempts - 1:
                    logger.warning(
                        "neo4j_connection_failed_retrying",
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        error=str(e),
                        delay=retry_delay,
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    logger.error("neo4j_connection_failed_max_attempts", error=str(e))
                    self._connected = False
                    raise
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            self._connected = False
            logger.info("neo4j_disconnected")
    
    async def health_check(self) -> bool:
        """健康检查
        
        Returns:
            bool: 连接是否健康
        """
        if self._driver is None:
            logger.warning("neo4j_driver_not_initialized")
            return False
        
        try:
            await self._driver.verify_connectivity()
            self._connected = True
            return True
        except Exception as e:
            logger.warning("neo4j_health_check_failed", error=str(e))
            self._connected = False
            return False
    
    async def ensure_connection(self) -> None:
        """确保连接有效，无效则尝试重连
        
        Raises:
            RuntimeError: 如果无法建立连接
        """
        # 检查连接是否健康
        if not await self.health_check():
            # 尝试重新连接
            logger.info("neo4j_attempting_reconnect")
            await self.connect()
    
    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """获取数据库会话
        
        使用上下文管理器确保会话正确关闭，并在获取会话前检查连接健康状态
        """
        # 确保连接有效
        await self.ensure_connection()
        
        if self._driver is None:
            raise RuntimeError("Neo4j driver not connected. Call connect() first.")
        
        async with self._driver.session(database=settings.neo4j_database) as session:
            try:
                yield session
            except Exception as e:
                logger.error("neo4j_session_error", error=str(e))
                # 如果是连接相关错误，尝试重新连接
                if "Connection" in str(type(e)) or "connection" in str(e).lower():
                    logger.warning("neo4j_connection_error_detected")
                    self._connected = False
                raise
    
    @property
    def driver(self) -> AsyncDriver:
        """获取驱动实例
        
        Raises:
            RuntimeError: 如果驱动未连接
        """
        if self._driver is None:
            raise RuntimeError("Neo4j driver not connected. Call connect() first.")
        return self._driver
    
    @property
    def is_connected(self) -> bool:
        """获取连接状态
        
        Returns:
            bool: 连接是否有效
        """
        return self._connected
    
    @property
    def connection_stats(self) -> dict:
        """获取连接统计信息
        
        Returns:
            dict: 包含连接状态、尝试次数等统计信息
        """
        return {
            "connected": self._connected,
            "connection_attempts": self._connection_attempts,
            "last_connection_attempt": self._last_connection_attempt,
            "driver_initialized": self._driver is not None,
        }


# 全局连接实例
neo4j_connection = Neo4jConnection()


async def init_database() -> None:
    """初始化数据库连接和约束"""
    await neo4j_connection.connect()
    await create_constraints_and_indexes()


async def close_database() -> None:
    """关闭数据库连接"""
    await neo4j_connection.close()


async def create_constraints_and_indexes() -> None:
    """创建数据库约束和索引
    
    根据设计文档创建唯一性约束和索引
    """
    constraints_and_indexes = [
        # 唯一性约束
        "CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.student_id IS UNIQUE",
        "CREATE CONSTRAINT teacher_id_unique IF NOT EXISTS FOR (t:Teacher) REQUIRE t.teacher_id IS UNIQUE",
        "CREATE CONSTRAINT course_id_unique IF NOT EXISTS FOR (c:Course) REQUIRE c.course_id IS UNIQUE",
        "CREATE CONSTRAINT knowledge_point_id_unique IF NOT EXISTS FOR (k:KnowledgePoint) REQUIRE k.knowledge_point_id IS UNIQUE",
        "CREATE CONSTRAINT error_type_id_unique IF NOT EXISTS FOR (e:ErrorType) REQUIRE e.error_type_id IS UNIQUE",
        
        # 节点属性索引 - 用于优化频繁的属性查询
        "CREATE INDEX student_name_index IF NOT EXISTS FOR (s:Student) ON (s.name)",
        "CREATE INDEX student_student_id_index IF NOT EXISTS FOR (s:Student) ON (s.student_id)",
        "CREATE INDEX course_name_index IF NOT EXISTS FOR (c:Course) ON (c.name)",
        "CREATE INDEX course_course_id_index IF NOT EXISTS FOR (c:Course) ON (c.course_id)",
        "CREATE INDEX knowledge_point_name_index IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.name)",
        "CREATE INDEX knowledge_point_knowledge_point_id_index IF NOT EXISTS FOR (k:KnowledgePoint) ON (k.knowledge_point_id)",
        "CREATE INDEX error_type_name_index IF NOT EXISTS FOR (et:ErrorType) ON (et.name)",
        "CREATE INDEX error_type_error_type_id_index IF NOT EXISTS FOR (et:ErrorType) ON (et.error_type_id)",
    ]
    
    async with neo4j_connection.get_session() as session:
        for query in constraints_and_indexes:
            try:
                await session.run(query)
                logger.info("constraint_or_index_created", query=query)
            except Exception as e:
                logger.warning(
                    "constraint_or_index_creation_failed",
                    query=query,
                    error=str(e),
                )
