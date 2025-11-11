"""服务端配置 - 从 YAML 文件加载配置"""
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml


class Settings:
    """应用配置"""
    
    def __init__(self):
        """初始化配置，从 YAML 文件加载"""
        # 获取配置文件路径（现在 settings.py 在 server/ 目录，config.yaml 在 server/config/ 目录）
        config_dir = Path(__file__).parent / "config"
        config_path = config_dir / "config.yaml"
        
        # 加载合并后的配置文件
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
        
        # 加载 Redis 配置
        self._load_redis_config(config.get("redis", {}))
        
        # 加载 Celery 配置
        self._load_celery_config(config.get("celery", {}))
        
        # 加载 gRPC 配置
        self._load_grpc_config(config.get("grpc", {}))
        
        # 任务队列配置
        self.TASK_PREFIX: str = "agent_queue"  # 队列前缀
        # 任务结果过期时间（秒），None 表示不过期
        self.TASK_RESULT_EXPIRES: Optional[int] = None  # 不过期
        
        # 日志配置
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def _load_redis_config(self, redis_config: Dict[str, Any]):
        """加载 Redis 配置"""
        if redis_config:
            # 基本连接配置（优先使用环境变量）
            self.REDIS_HOST: str = os.getenv("REDIS_HOST", redis_config.get("host", "localhost"))
            self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", redis_config.get("port", 6379)))
            self.REDIS_DB: int = int(os.getenv("REDIS_DB", redis_config.get("db", 0)))
            self.REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", redis_config.get("password"))
            self.REDIS_URL_ENV: Optional[str] = os.getenv("REDIS_URL", redis_config.get("url"))
            
            # 连接超时配置
            self.REDIS_SOCKET_CONNECT_TIMEOUT: float = float(redis_config.get("socket_connect_timeout", 5))
            self.REDIS_SOCKET_TIMEOUT: float = float(redis_config.get("socket_timeout", 5))
            self.REDIS_SOCKET_KEEPALIVE: bool = redis_config.get("socket_keepalive", True)
            socket_keepalive_opts = redis_config.get("socket_keepalive_options", {})
            self.REDIS_SOCKET_KEEPALIVE_OPTIONS: Dict[str, int] = {
                "TCP_KEEPIDLE": socket_keepalive_opts.get("TCP_KEEPIDLE", 1),
                "TCP_KEEPINTVL": socket_keepalive_opts.get("TCP_KEEPINTVL", 3),
                "TCP_KEEPCNT": socket_keepalive_opts.get("TCP_KEEPCNT", 5),
            }
            
            # 连接池配置
            self.REDIS_MAX_CONNECTIONS: int = int(redis_config.get("max_connections", 50))
            self.REDIS_RETRY_ON_TIMEOUT: bool = redis_config.get("retry_on_timeout", True)
            self.REDIS_HEALTH_CHECK_INTERVAL: int = int(redis_config.get("health_check_interval", 30))
            
            # SSL/TLS 配置
            self.REDIS_SSL: bool = redis_config.get("ssl", False)
            self.REDIS_SSL_CERT_REQS: Optional[str] = redis_config.get("ssl_cert_reqs")
            self.REDIS_SSL_CA_CERTS: Optional[str] = redis_config.get("ssl_ca_certs")
            self.REDIS_SSL_CERTFILE: Optional[str] = redis_config.get("ssl_certfile")
            self.REDIS_SSL_KEYFILE: Optional[str] = redis_config.get("ssl_keyfile")
            self.REDIS_SSL_CHECK_HOSTNAME: bool = redis_config.get("ssl_check_hostname", False)
            
            # 重试配置
            self.REDIS_RETRY_ON_ERROR: List[str] = redis_config.get("retry_on_error", ["ConnectionError", "TimeoutError", "ResponseError"])
            self.REDIS_MAX_RETRIES: int = int(redis_config.get("max_retries", 3))
            self.REDIS_RETRY_DELAY: float = float(redis_config.get("retry_delay", 1))
            
            # 主从/哨兵模式配置
            self.REDIS_SENTINEL: bool = redis_config.get("sentinel", False)
            self.REDIS_SENTINEL_HOSTS: List[Dict[str, Any]] = redis_config.get("sentinel_hosts", [])
            self.REDIS_SENTINEL_SERVICE_NAME: Optional[str] = redis_config.get("sentinel_service_name")
            self.REDIS_SENTINEL_PASSWORD: Optional[str] = redis_config.get("sentinel_password")
            self.REDIS_SENTINEL_SOCKET_TIMEOUT: float = float(redis_config.get("sentinel_socket_timeout", 0.1))
            
            # 集群模式配置
            self.REDIS_CLUSTER: bool = redis_config.get("cluster", False)
            self.REDIS_CLUSTER_NODES: List[Dict[str, Any]] = redis_config.get("cluster_nodes", [])
            
            # 连接验证
            self.REDIS_DECODE_RESPONSES: bool = redis_config.get("decode_responses", False)
            
            # 性能优化
            self.REDIS_ENCODING: str = redis_config.get("encoding", "utf-8")
            self.REDIS_ENCODING_ERRORS: str = redis_config.get("encoding_errors", "strict")
        else:
            # 如果配置不存在，使用环境变量或默认值
            self.REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
            self.REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
            self.REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
            self.REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
            self.REDIS_URL_ENV: Optional[str] = os.getenv("REDIS_URL", None)
            
            # 默认值
            self.REDIS_SOCKET_CONNECT_TIMEOUT: float = 5.0
            self.REDIS_SOCKET_TIMEOUT: float = 5.0
            self.REDIS_SOCKET_KEEPALIVE: bool = True
            self.REDIS_SOCKET_KEEPALIVE_OPTIONS: Dict[str, int] = {
                "TCP_KEEPIDLE": 1,
                "TCP_KEEPINTVL": 3,
                "TCP_KEEPCNT": 5,
            }
            self.REDIS_MAX_CONNECTIONS: int = 50
            self.REDIS_RETRY_ON_TIMEOUT: bool = True
            self.REDIS_HEALTH_CHECK_INTERVAL: int = 30
            self.REDIS_SSL: bool = False
            self.REDIS_SSL_CERT_REQS: Optional[str] = None
            self.REDIS_SSL_CA_CERTS: Optional[str] = None
            self.REDIS_SSL_CERTFILE: Optional[str] = None
            self.REDIS_SSL_KEYFILE: Optional[str] = None
            self.REDIS_SSL_CHECK_HOSTNAME: bool = False
            self.REDIS_RETRY_ON_ERROR: List[str] = ["ConnectionError", "TimeoutError", "ResponseError"]
            self.REDIS_MAX_RETRIES: int = 3
            self.REDIS_RETRY_DELAY: float = 1.0
            self.REDIS_SENTINEL: bool = False
            self.REDIS_SENTINEL_HOSTS: List[Dict[str, Any]] = []
            self.REDIS_SENTINEL_SERVICE_NAME: Optional[str] = None
            self.REDIS_SENTINEL_PASSWORD: Optional[str] = None
            self.REDIS_SENTINEL_SOCKET_TIMEOUT: float = 0.1
            self.REDIS_CLUSTER: bool = False
            self.REDIS_CLUSTER_NODES: List[Dict[str, Any]] = []
            self.REDIS_DECODE_RESPONSES: bool = False
            self.REDIS_ENCODING: str = "utf-8"
            self.REDIS_ENCODING_ERRORS: str = "strict"
    
    def _load_celery_config(self, celery_config: Dict[str, Any]):
        """加载 Celery 配置"""
        if celery_config:
            # 基本配置
            self.CELERY_TASK_SERIALIZER: str = celery_config.get("task_serializer", "json")
            self.CELERY_RESULT_SERIALIZER: str = celery_config.get("result_serializer", "json")
            self.CELERY_ACCEPT_CONTENT: list = celery_config.get("accept_content", ["json"])
            self.CELERY_TIMEZONE: str = celery_config.get("timezone", "UTC")
            self.CELERY_ENABLE_UTC: bool = celery_config.get("enable_utc", True)
            
            # 任务跟踪
            self.CELERY_TASK_TRACK_STARTED: bool = celery_config.get("task_track_started", True)
            self.CELERY_TASK_SEND_SENT_EVENT: bool = celery_config.get("task_send_sent_event", True)
            self.CELERY_WORKER_SEND_TASK_EVENTS: bool = celery_config.get("worker_send_task_events", True)
            self.CELERY_TASK_ALWAYS_EAGER: bool = celery_config.get("task_always_eager", False)
            
            # 任务时间限制
            self.CELERY_TASK_TIME_LIMIT: int = celery_config.get("task_time_limit", 30 * 60)
            self.CELERY_TASK_SOFT_TIME_LIMIT: int = celery_config.get("task_soft_time_limit", 25 * 60)
            
            # 结果过期时间
            result_expires = celery_config.get("result_expires")
            self.CELERY_RESULT_EXPIRES: Optional[int] = None if result_expires is None else int(result_expires)
            
            # 结果后端传输选项
            result_backend_opts = celery_config.get("result_backend_transport_options", {})
            self.CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS: Dict[str, Any] = result_backend_opts
            
            # 任务确认机制
            self.CELERY_TASK_ACKS_LATE: bool = celery_config.get("task_acks_late", True)
            self.CELERY_TASK_REJECT_ON_WORKER_LOST: bool = celery_config.get("task_reject_on_worker_lost", True)
            self.CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT: bool = celery_config.get("task_acks_on_failure_or_timeout", True)
            
            # 任务自动重试
            self.CELERY_TASK_AUTORETRY_FOR: List[str] = celery_config.get("task_autoretry_for", ["Exception"])
            self.CELERY_TASK_RETRY_BACKOFF: bool = celery_config.get("task_retry_backoff", True)
            self.CELERY_TASK_RETRY_BACKOFF_MAX: int = celery_config.get("task_retry_backoff_max", 600)
            self.CELERY_TASK_RETRY_JITTER: bool = celery_config.get("task_retry_jitter", True)
            self.CELERY_TASK_MAX_RETRIES: int = celery_config.get("task_max_retries", 3)
            
            # 工作进程配置
            self.CELERY_WORKER_PREFETCH_MULTIPLIER: int = celery_config.get("worker_prefetch_multiplier", 4)
            self.CELERY_WORKER_MAX_TASKS_PER_CHILD: int = celery_config.get("worker_max_tasks_per_child", 1000)
            self.CELERY_WORKER_MAX_MEMORY_PER_CHILD: int = celery_config.get("worker_max_memory_per_child", 200000)
            self.CELERY_WORKER_DISABLE_RATE_LIMITS: bool = celery_config.get("worker_disable_rate_limits", False)
            self.CELERY_WORKER_POOL: str = celery_config.get("worker_pool", "prefork")
            self.CELERY_WORKER_CONCURRENCY: Optional[int] = celery_config.get("worker_concurrency")
            
            # 任务路由和优先级
            self.CELERY_TASK_DEFAULT_QUEUE: str = celery_config.get("task_default_queue", "default")
            self.CELERY_TASK_DEFAULT_EXCHANGE: Optional[str] = celery_config.get("task_default_exchange")
            self.CELERY_TASK_DEFAULT_EXCHANGE_TYPE: str = celery_config.get("task_default_exchange_type", "direct")
            self.CELERY_TASK_DEFAULT_ROUTING_KEY: str = celery_config.get("task_default_routing_key", "default")
            self.CELERY_TASK_DEFAULT_PRIORITY: int = celery_config.get("task_default_priority", 5)
            
            # 任务注解（限流等）
            self.CELERY_TASK_ANNOTATIONS: Dict[str, Any] = celery_config.get("task_annotations", {})
            
            # 任务压缩
            self.CELERY_TASK_COMPRESSION: Optional[str] = celery_config.get("task_compression")
            self.CELERY_RESULT_COMPRESSION: Optional[str] = celery_config.get("result_compression")
            
            # 任务序列化优化
            self.CELERY_TASK_IGNORE_RESULT: bool = celery_config.get("task_ignore_result", False)
            
            # 消息确认机制
            self.CELERY_BROKER_TRANSPORT_OPTIONS: Dict[str, Any] = celery_config.get("broker_transport_options", {})
            
            # 任务拒绝策略
            self.CELERY_TASK_REJECT_ON_WORKER_LOST: bool = celery_config.get("task_reject_on_worker_lost", True)
            
            # 监控和日志
            self.CELERY_WORKER_HIJACK_ROOT_LOGGER: bool = celery_config.get("worker_hijack_root_logger", False)
            self.CELERY_WORKER_LOG_COLOR: bool = celery_config.get("worker_log_color", True)
            self.CELERY_WORKER_LOG_FORMAT: str = celery_config.get("worker_log_format", '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s')
            self.CELERY_WORKER_TASK_LOG_FORMAT: str = celery_config.get("worker_task_log_format", '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s')
            
            # 性能优化
            self.CELERY_TASK_EAGER_PROPAGATES: bool = celery_config.get("task_eager_propagates", False)
            
            # 高可用配置
            self.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = celery_config.get("broker_connection_retry_on_startup", True)
            self.CELERY_BROKER_CONNECTION_RETRY: bool = celery_config.get("broker_connection_retry", True)
            self.CELERY_BROKER_CONNECTION_MAX_RETRIES: int = celery_config.get("broker_connection_max_retries", 10)
            self.CELERY_BROKER_CONNECTION_RETRY_DELAY: float = float(celery_config.get("broker_connection_retry_delay", 2.0))
        else:
            # 如果配置不存在，使用默认值
            self.CELERY_TASK_SERIALIZER: str = "json"
            self.CELERY_RESULT_SERIALIZER: str = "json"
            self.CELERY_ACCEPT_CONTENT: list = ["json"]
            self.CELERY_TIMEZONE: str = "UTC"
            self.CELERY_ENABLE_UTC: bool = True
            self.CELERY_TASK_TRACK_STARTED: bool = True
            self.CELERY_TASK_SEND_SENT_EVENT: bool = True
            self.CELERY_WORKER_SEND_TASK_EVENTS: bool = True
            self.CELERY_TASK_ALWAYS_EAGER: bool = False
            self.CELERY_TASK_TIME_LIMIT: int = 30 * 60
            self.CELERY_TASK_SOFT_TIME_LIMIT: int = 25 * 60
            self.CELERY_RESULT_EXPIRES: Optional[int] = None
            self.CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS: Dict[str, Any] = {}
            self.CELERY_TASK_ACKS_LATE: bool = True
            self.CELERY_TASK_REJECT_ON_WORKER_LOST: bool = True
            self.CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT: bool = True
            self.CELERY_TASK_AUTORETRY_FOR: List[str] = ["Exception"]
            self.CELERY_TASK_RETRY_BACKOFF: bool = True
            self.CELERY_TASK_RETRY_BACKOFF_MAX: int = 600
            self.CELERY_TASK_RETRY_JITTER: bool = True
            self.CELERY_TASK_MAX_RETRIES: int = 3
            self.CELERY_WORKER_PREFETCH_MULTIPLIER: int = 4
            self.CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000
            self.CELERY_WORKER_MAX_MEMORY_PER_CHILD: int = 200000
            self.CELERY_WORKER_DISABLE_RATE_LIMITS: bool = False
            self.CELERY_WORKER_POOL: str = "prefork"
            self.CELERY_WORKER_CONCURRENCY: Optional[int] = None
            self.CELERY_TASK_DEFAULT_QUEUE: str = "default"
            self.CELERY_TASK_DEFAULT_EXCHANGE: Optional[str] = None
            self.CELERY_TASK_DEFAULT_EXCHANGE_TYPE: str = "direct"
            self.CELERY_TASK_DEFAULT_ROUTING_KEY: str = "default"
            self.CELERY_TASK_DEFAULT_PRIORITY: int = 5
            self.CELERY_TASK_ANNOTATIONS: Dict[str, Any] = {}
            self.CELERY_TASK_COMPRESSION: Optional[str] = None
            self.CELERY_RESULT_COMPRESSION: Optional[str] = None
            self.CELERY_TASK_IGNORE_RESULT: bool = False
            self.CELERY_BROKER_TRANSPORT_OPTIONS: Dict[str, Any] = {}
            self.CELERY_WORKER_HIJACK_ROOT_LOGGER: bool = False
            self.CELERY_WORKER_LOG_COLOR: bool = True
            self.CELERY_WORKER_LOG_FORMAT: str = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
            self.CELERY_WORKER_TASK_LOG_FORMAT: str = '[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s'
            self.CELERY_TASK_EAGER_PROPAGATES: bool = False
            self.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP: bool = True
            self.CELERY_BROKER_CONNECTION_RETRY: bool = True
            self.CELERY_BROKER_CONNECTION_MAX_RETRIES: int = 10
            self.CELERY_BROKER_CONNECTION_RETRY_DELAY: float = 2.0
    
    def _load_grpc_config(self, grpc_config: Dict[str, Any]):
        """加载 gRPC 配置"""
        if grpc_config:
            # 服务器连接配置（优先使用环境变量）
            self.GRPC_HOST: str = os.getenv("GRPC_HOST", grpc_config.get("host", "0.0.0.0"))
            self.GRPC_PORT: int = int(os.getenv("GRPC_PORT", str(grpc_config.get("port", 50051))))
            
            # 服务器选项配置
            self.GRPC_MAX_RECEIVE_MESSAGE_LENGTH: int = int(grpc_config.get("max_receive_message_length", 4194304))
            self.GRPC_MAX_SEND_MESSAGE_LENGTH: int = int(grpc_config.get("max_send_message_length", 4194304))
            max_concurrent_streams = grpc_config.get("max_concurrent_streams")
            self.GRPC_MAX_CONCURRENT_STREAMS: Optional[int] = None if max_concurrent_streams is None else int(max_concurrent_streams)
            self.GRPC_CONNECTION_TIMEOUT: float = float(grpc_config.get("connection_timeout", 30))
            
            # Keepalive 配置
            self.GRPC_KEEPALIVE_TIME: int = int(grpc_config.get("keepalive_time", 30))
            self.GRPC_KEEPALIVE_TIMEOUT: int = int(grpc_config.get("keepalive_timeout", 5))
            self.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: bool = grpc_config.get("keepalive_permit_without_calls", True)
            self.GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA: int = int(grpc_config.get("http2_max_pings_without_data", 0))
            self.GRPC_HTTP2_MIN_TIME_BETWEEN_PINGS_MS: int = int(grpc_config.get("http2_min_time_between_pings_ms", 10000))
            self.GRPC_HTTP2_MIN_PING_INTERVAL_WITHOUT_DATA_MS: int = int(grpc_config.get("http2_min_ping_interval_without_data_ms", 300000))
            
            # 线程池配置
            self.GRPC_MAX_WORKERS: int = int(grpc_config.get("max_workers", 10))
            self.GRPC_THREAD_POOL_PREFIX: str = grpc_config.get("thread_pool_prefix", "grpc-pool")
            
            # SSL/TLS 配置
            self.GRPC_USE_TLS: bool = grpc_config.get("use_tls", False)
            self.GRPC_TLS_CERT_FILE: Optional[str] = grpc_config.get("tls_cert_file")
            self.GRPC_TLS_KEY_FILE: Optional[str] = grpc_config.get("tls_key_file")
            self.GRPC_TLS_CA_CERTS: Optional[str] = grpc_config.get("tls_ca_certs")
            self.GRPC_TLS_CLIENT_AUTH: bool = grpc_config.get("tls_client_auth", False)
            
            # 压缩配置
            self.GRPC_COMPRESSION: Optional[str] = grpc_config.get("compression")
            
            # 日志配置
            self.GRPC_ENABLE_LOGGING: bool = grpc_config.get("enable_logging", False)
            self.GRPC_LOG_LEVEL: str = grpc_config.get("log_level", "INFO")
            
            # 性能优化配置
            self.GRPC_SO_REUSEPORT: bool = grpc_config.get("so_reuseport", False)
            so_rcvbuf = grpc_config.get("so_rcvbuf")
            self.GRPC_SO_RCVBUF: Optional[int] = None if so_rcvbuf is None else int(so_rcvbuf)
            so_sndbuf = grpc_config.get("so_sndbuf")
            self.GRPC_SO_SNDBUF: Optional[int] = None if so_sndbuf is None else int(so_sndbuf)
            
            # 健康检查配置
            self.GRPC_ENABLE_HEALTH_CHECK: bool = grpc_config.get("enable_health_check", True)
            self.GRPC_HEALTH_CHECK_INTERVAL: int = int(grpc_config.get("health_check_interval", 30))
            
            # 反射服务配置
            self.GRPC_ENABLE_REFLECTION: bool = grpc_config.get("enable_reflection", False)
            
            # 限流配置
            max_concurrent_rpcs = grpc_config.get("max_concurrent_rpcs_per_connection")
            self.GRPC_MAX_CONCURRENT_RPCS_PER_CONNECTION: Optional[int] = None if max_concurrent_rpcs is None else int(max_concurrent_rpcs)
            
            # 超时配置
            self.GRPC_DEFAULT_TIMEOUT: float = float(grpc_config.get("default_timeout", 30))
            self.GRPC_MAX_TIMEOUT: float = float(grpc_config.get("max_timeout", 300))
        else:
            # 如果配置不存在，使用环境变量或默认值
            self.GRPC_HOST: str = os.getenv("GRPC_HOST", "0.0.0.0")
            self.GRPC_PORT: int = int(os.getenv("GRPC_PORT", "50051"))
            self.GRPC_MAX_RECEIVE_MESSAGE_LENGTH: int = 4194304
            self.GRPC_MAX_SEND_MESSAGE_LENGTH: int = 4194304
            self.GRPC_MAX_CONCURRENT_STREAMS: Optional[int] = None
            self.GRPC_CONNECTION_TIMEOUT: float = 30.0
            self.GRPC_KEEPALIVE_TIME: int = 30
            self.GRPC_KEEPALIVE_TIMEOUT: int = 5
            self.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: bool = True
            self.GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA: int = 0
            self.GRPC_HTTP2_MIN_TIME_BETWEEN_PINGS_MS: int = 10000
            self.GRPC_HTTP2_MIN_PING_INTERVAL_WITHOUT_DATA_MS: int = 300000
            self.GRPC_MAX_WORKERS: int = 10
            self.GRPC_THREAD_POOL_PREFIX: str = "grpc-pool"
            self.GRPC_USE_TLS: bool = False
            self.GRPC_TLS_CERT_FILE: Optional[str] = None
            self.GRPC_TLS_KEY_FILE: Optional[str] = None
            self.GRPC_TLS_CA_CERTS: Optional[str] = None
            self.GRPC_TLS_CLIENT_AUTH: bool = False
            self.GRPC_COMPRESSION: Optional[str] = None
            self.GRPC_ENABLE_LOGGING: bool = False
            self.GRPC_LOG_LEVEL: str = "INFO"
            self.GRPC_SO_REUSEPORT: bool = False
            self.GRPC_SO_RCVBUF: Optional[int] = None
            self.GRPC_SO_SNDBUF: Optional[int] = None
            self.GRPC_ENABLE_HEALTH_CHECK: bool = True
            self.GRPC_HEALTH_CHECK_INTERVAL: int = 30
            self.GRPC_ENABLE_REFLECTION: bool = False
            self.GRPC_MAX_CONCURRENT_RPCS_PER_CONNECTION: Optional[int] = None
            self.GRPC_DEFAULT_TIMEOUT: float = 30.0
            self.GRPC_MAX_TIMEOUT: float = 300.0
    
    @property
    def REDIS_URL(self) -> str:
        """Redis URL"""
        # 优先使用环境变量或 YAML 中的 URL
        if hasattr(self, 'REDIS_URL_ENV') and self.REDIS_URL_ENV:
            return self.REDIS_URL_ENV
        
        # 否则根据配置构建 URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def get_redis_connection_kwargs(self) -> Dict[str, Any]:
        """获取 Redis 连接参数字典（用于创建 Redis 客户端）"""
        kwargs = {
            "host": self.REDIS_HOST,
            "port": self.REDIS_PORT,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD,
            "socket_connect_timeout": self.REDIS_SOCKET_CONNECT_TIMEOUT,
            "socket_timeout": self.REDIS_SOCKET_TIMEOUT,
            "socket_keepalive": self.REDIS_SOCKET_KEEPALIVE,
            "socket_keepalive_options": self.REDIS_SOCKET_KEEPALIVE_OPTIONS,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "retry_on_timeout": self.REDIS_RETRY_ON_TIMEOUT,
            "health_check_interval": self.REDIS_HEALTH_CHECK_INTERVAL,
            "decode_responses": self.REDIS_DECODE_RESPONSES,
            "encoding": self.REDIS_ENCODING,
            "encoding_errors": self.REDIS_ENCODING_ERRORS,
        }
        
        # SSL/TLS 配置
        if self.REDIS_SSL:
            kwargs["ssl"] = True
            if self.REDIS_SSL_CERT_REQS:
                import ssl
                cert_reqs_map = {
                    "none": ssl.CERT_NONE,
                    "optional": ssl.CERT_OPTIONAL,
                    "required": ssl.CERT_REQUIRED,
                }
                kwargs["ssl_cert_reqs"] = cert_reqs_map.get(self.REDIS_SSL_CERT_REQS.lower(), ssl.CERT_REQUIRED)
            if self.REDIS_SSL_CA_CERTS:
                kwargs["ssl_ca_certs"] = self.REDIS_SSL_CA_CERTS
            if self.REDIS_SSL_CERTFILE:
                kwargs["ssl_certfile"] = self.REDIS_SSL_CERTFILE
            if self.REDIS_SSL_KEYFILE:
                kwargs["ssl_keyfile"] = self.REDIS_SSL_KEYFILE
            kwargs["ssl_check_hostname"] = self.REDIS_SSL_CHECK_HOSTNAME
        
        return kwargs


settings = Settings()

