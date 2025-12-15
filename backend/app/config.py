"""应用配置管理"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置
    
    使用 pydantic-settings 管理应用配置，支持从环境变量和 .env 文件加载
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用配置
    app_name: str = Field(default="教育知识图谱系统", description="应用名称")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # CORS 配置
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="允许的跨域来源",
    )

    # Neo4j 配置
    neo4j_uri: str = Field(default="bolt://localhost:7687", description="Neo4j 连接 URI")
    neo4j_user: str = Field(default="neo4j", description="Neo4j 用户名")
    neo4j_password: str = Field(default="password", description="Neo4j 密码")
    neo4j_database: str = Field(default="neo4j", description="Neo4j 数据库名")
    neo4j_max_connection_pool_size: int = Field(default=50, description="Neo4j 连接池大小")
    neo4j_connection_timeout: int = Field(default=30, description="Neo4j 连接超时时间（秒）")
    neo4j_max_transaction_retry_time: int = Field(default=30, description="Neo4j 最大事务重试时间（秒）")

    # Redis 配置
    redis_host: str = Field(default="localhost", description="Redis 主机")
    redis_port: int = Field(default=6379, description="Redis 端口")
    redis_db: int = Field(default=0, description="Redis 数据库编号")
    redis_password: str | None = Field(default=None, description="Redis 密码")
    redis_max_connections: int = Field(default=50, description="Redis 最大连接数")

    # PostgreSQL 配置（可选）
    postgres_host: str = Field(default="localhost", description="PostgreSQL 主机")
    postgres_port: int = Field(default=5432, description="PostgreSQL 端口")
    postgres_user: str = Field(default="postgres", description="PostgreSQL 用户名")
    postgres_password: str = Field(default="password", description="PostgreSQL 密码")
    postgres_db: str = Field(default="education_kg", description="PostgreSQL 数据库名")

    # 阿里云通义千问配置
    dashscope_api_key: str = Field(default="", description="阿里云 DashScope API 密钥")
    qwen_model_simple: str = Field(
        default="qwen-turbo",
        description="简单任务使用的模型（情感分析、分类）- 免费额度充足",
    )
    qwen_model_medium: str = Field(
        default="qwen-plus",
        description="中等复杂度任务使用的模型（知识点提取、错误分析）",
    )
    qwen_model_complex: str = Field(
        default="qwen-max",
        description="复杂任务使用的模型（复杂推理）- 仅在必要时使用",
    )
    qwen_max_tokens: int = Field(default=2000, description="通义千问最大 token 数")
    qwen_temperature: float = Field(default=0.7, description="通义千问温度参数")

    # Celery 配置
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery 消息代理 URL",
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery 结果后端 URL",
    )

    # 数据处理配置
    batch_size: int = Field(default=1000, ge=1, le=10000, description="批处理大小")
    llm_rate_limit: int = Field(default=100, ge=1, description="LLM 每分钟请求数限制")
    llm_retry_max: int = Field(default=3, ge=1, le=10, description="LLM 最大重试次数")
    llm_retry_delay: float = Field(default=1.0, ge=0.1, description="LLM 重试延迟（秒）")
    
    # 缓存配置
    cache_ttl: int = Field(default=3600, ge=0, description="缓存过期时间（秒）")
    cache_enabled: bool = Field(default=True, description="是否启用缓存")
    cache_strategy: str = Field(default="ttl", description="缓存策略：ttl, lru, lfu")
    cache_max_keys: int = Field(default=10000, ge=100, description="缓存最大键数量")
    cache_protection_enabled: bool = Field(default=True, description="是否启用缓存防护机制")
    cache_bloom_filter_fpp: float = Field(default=0.01, description="布隆过滤器误判率")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式（json 或 console）")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS 来源列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v):
        """验证日志格式"""
        valid_formats = ["json", "console"]
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"log_format must be one of {valid_formats}")
        return v_lower

    @property
    def redis_url(self) -> str:
        """构建 Redis URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def postgres_url(self) -> str:
        """构建 PostgreSQL URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


# 全局配置实例
settings = Settings()
