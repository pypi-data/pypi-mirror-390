"""Celery 配置 - 从 settings 读取配置"""
from server.settings import settings

def get_celery_config():
    """获取 Celery 配置字典"""
    config = {
        "broker_url": settings.REDIS_URL,
        "result_backend": settings.REDIS_URL,
        
        # 基本配置
        "task_serializer": settings.CELERY_TASK_SERIALIZER,
        "result_serializer": settings.CELERY_RESULT_SERIALIZER,
        "accept_content": settings.CELERY_ACCEPT_CONTENT,
        "timezone": settings.CELERY_TIMEZONE,
        "enable_utc": settings.CELERY_ENABLE_UTC,
        
        # 任务跟踪
        "task_track_started": settings.CELERY_TASK_TRACK_STARTED,
        "task_send_sent_event": settings.CELERY_TASK_SEND_SENT_EVENT,
        "worker_send_task_events": settings.CELERY_WORKER_SEND_TASK_EVENTS,
        "task_always_eager": settings.CELERY_TASK_ALWAYS_EAGER,
        
        # 任务时间限制
        "task_time_limit": settings.CELERY_TASK_TIME_LIMIT,
        "task_soft_time_limit": settings.CELERY_TASK_SOFT_TIME_LIMIT,
        
        # 任务确认机制（可靠性）
        "task_acks_late": settings.CELERY_TASK_ACKS_LATE,
        "task_reject_on_worker_lost": settings.CELERY_TASK_REJECT_ON_WORKER_LOST,
        "task_acks_on_failure_or_timeout": settings.CELERY_TASK_ACKS_ON_FAILURE_OR_TIMEOUT,
        
        # 工作进程配置（稳定性）
        "worker_prefetch_multiplier": settings.CELERY_WORKER_PREFETCH_MULTIPLIER,
        "worker_max_tasks_per_child": settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
        "worker_max_memory_per_child": settings.CELERY_WORKER_MAX_MEMORY_PER_CHILD,
        "worker_disable_rate_limits": settings.CELERY_WORKER_DISABLE_RATE_LIMITS,
        "worker_pool": settings.CELERY_WORKER_POOL,
        "worker_hijack_root_logger": settings.CELERY_WORKER_HIJACK_ROOT_LOGGER,
        "worker_log_color": settings.CELERY_WORKER_LOG_COLOR,
        "worker_log_format": settings.CELERY_WORKER_LOG_FORMAT,
        "worker_task_log_format": settings.CELERY_WORKER_TASK_LOG_FORMAT,
        
        # 任务路由和优先级
        "task_default_queue": settings.CELERY_TASK_DEFAULT_QUEUE,
        "task_default_exchange_type": settings.CELERY_TASK_DEFAULT_EXCHANGE_TYPE,
        "task_default_routing_key": settings.CELERY_TASK_DEFAULT_ROUTING_KEY,
        "task_default_priority": settings.CELERY_TASK_DEFAULT_PRIORITY,
        
        # 任务序列化优化
        "task_ignore_result": settings.CELERY_TASK_IGNORE_RESULT,
        "task_eager_propagates": settings.CELERY_TASK_EAGER_PROPAGATES,
        
        # 高可用配置（容灾能力）
        "broker_connection_retry_on_startup": settings.CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP,
        "broker_connection_retry": settings.CELERY_BROKER_CONNECTION_RETRY,
        "broker_connection_max_retries": settings.CELERY_BROKER_CONNECTION_MAX_RETRIES,
        "broker_connection_retry_delay": settings.CELERY_BROKER_CONNECTION_RETRY_DELAY,
    }
    
    # 可选配置（仅在设置时添加）
    if settings.CELERY_RESULT_EXPIRES is not None:
        config["result_expires"] = settings.CELERY_RESULT_EXPIRES
    
    if settings.CELERY_WORKER_CONCURRENCY is not None:
        config["worker_concurrency"] = settings.CELERY_WORKER_CONCURRENCY
    
    if settings.CELERY_TASK_DEFAULT_EXCHANGE is not None:
        config["task_default_exchange"] = settings.CELERY_TASK_DEFAULT_EXCHANGE
    
    if settings.CELERY_TASK_COMPRESSION is not None:
        config["task_compression"] = settings.CELERY_TASK_COMPRESSION
    
    if settings.CELERY_RESULT_COMPRESSION is not None:
        config["result_compression"] = settings.CELERY_RESULT_COMPRESSION
    
    # 任务注解（限流等）
    if settings.CELERY_TASK_ANNOTATIONS:
        config["task_annotations"] = settings.CELERY_TASK_ANNOTATIONS
    
    # 结果后端传输选项
    if settings.CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS:
        config["result_backend_transport_options"] = settings.CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS
    
    # 消息确认机制
    if settings.CELERY_BROKER_TRANSPORT_OPTIONS:
        config["broker_transport_options"] = settings.CELERY_BROKER_TRANSPORT_OPTIONS
    
    return config

# 为了向后兼容，保留 celery_config 变量
celery_config = get_celery_config()

