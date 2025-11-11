"""Agent 客户端接口 - 优化的 gRPC 接口封装"""
# 导出 gRPC 生成的代码和客户端

# 导出 gRPC 生成的代码
try:
    from . import queue_service_pb2, queue_service_pb2_grpc
    
    # ========== 服务类 ==========
    QueueServiceStub = queue_service_pb2_grpc.QueueServiceStub
    
    # ========== 消息类型 ==========
    # 请求消息
    CreateQueueRequest = queue_service_pb2.CreateQueueRequest
    QueueExistsRequest = queue_service_pb2.QueueExistsRequest
    GetQueueInfoRequest = queue_service_pb2.GetQueueInfoRequest
    ClearQueueRequest = queue_service_pb2.ClearQueueRequest
    DeleteQueueRequest = queue_service_pb2.DeleteQueueRequest
    SubmitTaskRequest = queue_service_pb2.SubmitTaskRequest
    BatchSubmitTasksRequest = queue_service_pb2.BatchSubmitTasksRequest
    SubmitTaskItem = queue_service_pb2.SubmitTaskItem
    GetTaskRequest = queue_service_pb2.GetTaskRequest
    QueryTaskRequest = queue_service_pb2.QueryTaskRequest
    UpdateTaskStatusRequest = queue_service_pb2.UpdateTaskStatusRequest
    DeleteTaskRequest = queue_service_pb2.DeleteTaskRequest
    BatchDeleteTasksRequest = queue_service_pb2.BatchDeleteTasksRequest
    CancelTaskRequest = queue_service_pb2.CancelTaskRequest
    RetryTaskRequest = queue_service_pb2.RetryTaskRequest
    ListTasksRequest = queue_service_pb2.ListTasksRequest
    GetTasksByStatusRequest = queue_service_pb2.GetTasksByStatusRequest
    GetTaskStatsRequest = queue_service_pb2.GetTaskStatsRequest
    HealthCheckRequest = queue_service_pb2.HealthCheckRequest
    StreamQueueReportsRequest = queue_service_pb2.StreamQueueReportsRequest
    
    # 响应消息
    CreateQueueResponse = queue_service_pb2.CreateQueueResponse
    QueueExistsResponse = queue_service_pb2.QueueExistsResponse
    GetQueueInfoResponse = queue_service_pb2.GetQueueInfoResponse
    ClearQueueResponse = queue_service_pb2.ClearQueueResponse
    DeleteQueueResponse = queue_service_pb2.DeleteQueueResponse
    SubmitTaskResponse = queue_service_pb2.SubmitTaskResponse
    BatchSubmitTasksResponse = queue_service_pb2.BatchSubmitTasksResponse
    GetTaskResponse = queue_service_pb2.GetTaskResponse
    QueryTaskResponse = queue_service_pb2.QueryTaskResponse
    UpdateTaskStatusResponse = queue_service_pb2.UpdateTaskStatusResponse
    DeleteTaskResponse = queue_service_pb2.DeleteTaskResponse
    BatchDeleteTasksResponse = queue_service_pb2.BatchDeleteTasksResponse
    CancelTaskResponse = queue_service_pb2.CancelTaskResponse
    RetryTaskResponse = queue_service_pb2.RetryTaskResponse
    ListTasksResponse = queue_service_pb2.ListTasksResponse
    GetTasksByStatusResponse = queue_service_pb2.GetTasksByStatusResponse
    GetTaskStatsResponse = queue_service_pb2.GetTaskStatsResponse
    HealthCheckResponse = queue_service_pb2.HealthCheckResponse
    
    # 数据模型
    Task = queue_service_pb2.Task
    
    # ========== 枚举类型 ==========
    TaskStatus = queue_service_pb2.TaskStatus
    TaskType = queue_service_pb2.TaskType
    
    # ========== 枚举值（方便使用） ==========
    # TaskStatus 枚举值
    PENDING = TaskStatus.PENDING
    PROCESSING = TaskStatus.PROCESSING
    COMPLETED = TaskStatus.COMPLETED
    FAILED = TaskStatus.FAILED
    
    # TaskType 枚举值
    UNKNOWN = TaskType.UNKNOWN
    DATA_PROCESSING = TaskType.DATA_PROCESSING
    IMAGE_PROCESSING = TaskType.IMAGE_PROCESSING
    TEXT_ANALYSIS = TaskType.TEXT_ANALYSIS
    MODEL_INFERENCE = TaskType.MODEL_INFERENCE
    DATA_EXTRACTION = TaskType.DATA_EXTRACTION
    FILE_UPLOAD = TaskType.FILE_UPLOAD
    FILE_DOWNLOAD = TaskType.FILE_DOWNLOAD
    API_CALL = TaskType.API_CALL
    DATABASE_QUERY = TaskType.DATABASE_QUERY
    CUSTOM = TaskType.CUSTOM
    
    __all__ = [
        # 服务类
        "QueueServiceStub",
        # 请求消息
        "CreateQueueRequest",
        "QueueExistsRequest",
        "GetQueueInfoRequest",
        "ClearQueueRequest",
        "SubmitTaskRequest",
        "BatchSubmitTasksRequest",
        "SubmitTaskItem",
        "GetTaskRequest",
        "QueryTaskRequest",
        "UpdateTaskStatusRequest",
        "DeleteTaskRequest",
        "BatchDeleteTasksRequest",
        "CancelTaskRequest",
        "RetryTaskRequest",
        "ListTasksRequest",
        "GetTaskStatsRequest",
        "HealthCheckRequest",
        "StreamQueueReportsRequest",
        # 响应消息
        "CreateQueueResponse",
        "QueueExistsResponse",
        "GetQueueInfoResponse",
        "ClearQueueResponse",
        "SubmitTaskResponse",
        "BatchSubmitTasksResponse",
        "GetTaskResponse",
        "QueryTaskResponse",
        "UpdateTaskStatusResponse",
        "DeleteTaskResponse",
        "BatchDeleteTasksResponse",
        "CancelTaskResponse",
        "RetryTaskResponse",
        "ListTasksResponse",
        "GetTaskStatsResponse",
        "HealthCheckResponse",
        # 数据模型
        "Task",
        # 枚举类型
        "TaskStatus",
        "TaskType",
        # 枚举值
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "UNKNOWN",
        "DATA_PROCESSING",
        "IMAGE_PROCESSING",
        "TEXT_ANALYSIS",
        "MODEL_INFERENCE",
        "DATA_EXTRACTION",
        "FILE_UPLOAD",
        "FILE_DOWNLOAD",
        "API_CALL",
        "DATABASE_QUERY",
        "CUSTOM",
        # 原始模块（向后兼容）
        "queue_service_pb2",
        "queue_service_pb2_grpc",
    ]
except ImportError:
    # gRPC 代码还未生成
    __all__ = []

# 从 agent_queues 包导入客户端类
# 使用 from ... import ... 确保 IDE 可以正确跳转到源代码
# 注意：为了 IDE 能够正确跳转，这里使用完整的导入路径
try:
    # 直接从源文件导入，确保 IDE 可以跳转
    # 使用 as 别名然后重新赋值，保持 __module__ 属性指向原始模块
    from agent_queues.agent_queue import (
        PrivateAgentTasksQueue as _PrivateAgentTasksQueue,
        AgentClient as _AgentClient,
        create_client as _create_client,
        AgentQueue as _AgentQueue,
    )
    from agent_queues.agent_queue_manager import (
        AgentQueueManager as _AgentQueueManager,
        create_manager as _create_manager,
    )
    from agent_queues.agent_queue_report import (
        AgentQueueReportClient as _AgentQueueReportClient,
        AgentQueueReport as _AgentQueueReport,
        QueueReport as _QueueReport,
        create_report_client as _create_report_client,
    )
    
    # 重新导出，保持向后兼容
    # 这样 IDE 可以正确识别原始模块位置
    PrivateAgentTasksQueue = _PrivateAgentTasksQueue
    AgentClient = _AgentClient
    create_client = _create_client
    AgentQueue = _AgentQueue
    AgentQueueManager = _AgentQueueManager
    create_manager = _create_manager
    AgentQueueReportClient = _AgentQueueReportClient
    AgentQueueReport = _AgentQueueReport
    QueueReport = _QueueReport
    create_report_client = _create_report_client
    
    __all__.extend([
        "PrivateAgentTasksQueue",
        "AgentClient",
        "create_client",
        "AgentQueue",
        "AgentQueueManager",
        "create_manager",
        "AgentQueueReportClient",
        "AgentQueueReport",
        "QueueReport",
        "create_report_client",
    ])
except ImportError:
    pass

# 导出配置模块
try:
    from agent_queues.settings import ClientSettings, get_settings
    # 创建全局配置实例
    settings = ClientSettings()
    __all__.extend(["settings", "ClientSettings", "get_settings"])
except ImportError:
    pass

# 导出拦截器
try:
    from agent_queues.retry_interceptor import RetryInterceptor, create_retry_interceptor
    __all__.extend(["RetryInterceptor", "create_retry_interceptor"])
except ImportError:
    pass

# ========== 工具函数 ==========

def get_proto_file_path() -> str:
    """
    获取 proto 接口文件路径
    
    返回 proto 文件的完整路径，方便用户查看接口定义。
    
    Returns:
        proto 文件的完整路径
    
    示例:
        from agent_queues import get_proto_file_path
        proto_path = get_proto_file_path()
        with open(proto_path, 'r', encoding='utf-8') as f:
            print(f.read())
    """
    import os
    return os.path.join(os.path.dirname(__file__), 'queue_service.proto')

def get_proto_content() -> str:
    """
    获取 proto 接口文件内容
    
    直接返回 proto 文件的文本内容，方便用户查看接口定义。
    
    Returns:
        proto 文件的文本内容
    
    示例:
        from agent_queues import get_proto_content
        proto_content = get_proto_content()
        print(proto_content)
    """
    import os
    proto_path = os.path.join(os.path.dirname(__file__), 'queue_service.proto')
    with open(proto_path, 'r', encoding='utf-8') as f:
        return f.read()

# 导出工具函数
__all__.extend([
    "get_proto_file_path",
    "get_proto_content",
])
