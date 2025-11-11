"""私有化 Agent 任务队列客户端 - 提供便捷的客户端创建方式，支持 agent 级别的配置"""
import grpc
from typing import Optional
from agent_queues.settings import ClientSettings
try:
    from agent_queues import settings as default_settings
    if not isinstance(default_settings, ClientSettings):
        default_settings = ClientSettings()
except (ImportError, AttributeError):
    default_settings = ClientSettings()
from agent_queues.queue_service_pb2_grpc import QueueServiceStub


class PrivateAgentTasksQueue:
    """
    私有化 Agent 任务队列客户端 - 封装 gRPC 客户端，支持 agent 级别的配置
    
    使用示例:
        # 使用默认配置
        queue = PrivateAgentTasksQueue()
        
        # 使用自定义配置
        queue = PrivateAgentTasksQueue(
            grpc_host="192.168.1.100",
            grpc_port=50052,
            grpc_timeout=60
        )
        
        # 使用配置文件
        queue = PrivateAgentTasksQueue(config_path="/path/to/config.yaml")
        
        # 基于默认配置覆盖部分配置
        queue = PrivateAgentTasksQueue(
            base_settings=default_settings,
            grpc_host="192.168.1.100"
        )
        
        # 使用客户端
        response = queue.create_queue("agent_001")
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        base_settings: Optional[ClientSettings] = None,
        grpc_host: Optional[str] = None,
        grpc_port: Optional[int] = None,
        grpc_timeout: Optional[float] = None,
        grpc_use_tls: Optional[bool] = None,
        **grpc_config_overrides
    ):
        """
        初始化私有化 Agent 任务队列客户端
        
        Args:
            config_path: 配置文件路径（可选）
            base_settings: 基础配置实例（可选），默认使用全局默认配置
            grpc_host: gRPC 服务器地址（可选，覆盖配置）
            grpc_port: gRPC 服务器端口（可选，覆盖配置）
            grpc_timeout: 超时时间（可选，覆盖配置）
            grpc_use_tls: 是否使用 TLS（可选，覆盖配置）
            **grpc_config_overrides: 其他 gRPC 配置覆盖项
                                    例如: grpc_keepalive_time=60, grpc_max_retry_attempts=5
        """
        # 确定基础配置
        if base_settings is None:
            base_settings = default_settings
        
        # 构建配置覆盖字典
        overrides = {}
        if grpc_host is not None:
            overrides['GRPC_HOST'] = grpc_host
        if grpc_port is not None:
            overrides['GRPC_PORT'] = grpc_port
        if grpc_timeout is not None:
            overrides['GRPC_TIMEOUT'] = grpc_timeout
        if grpc_use_tls is not None:
            overrides['GRPC_USE_TLS'] = grpc_use_tls
        
        # 处理其他配置覆盖（将 grpc_ 前缀转换为 GRPC_ 前缀）
        for key, value in grpc_config_overrides.items():
            if key.startswith('grpc_'):
                # 将 grpc_xxx 转换为 GRPC_XXX
                config_key = key.upper()
                overrides[config_key] = value
        
        # 创建配置实例
        if config_path is not None:
            # 如果指定了配置文件路径，从配置文件加载，然后应用覆盖
            self.settings = ClientSettings(config_path=config_path, **overrides)
        elif base_settings is not None:
            # 基于基础配置创建新配置，应用覆盖
            self.settings = base_settings.copy(**overrides)
        else:
            # 使用默认配置，应用覆盖
            self.settings = ClientSettings(base_settings=default_settings, **overrides)
        
        # 创建 gRPC 通道
        self.channel = self._create_channel()
        
        # 创建服务客户端
        self.stub = QueueServiceStub(self.channel)
    
    def _create_channel(self) -> grpc.Channel:
        """
        创建 gRPC 通道（支持重试和自动重连）
        
        通道会自动应用：
        - Keepalive 配置（自动检测连接状态）
        - 重试拦截器（自动重试失败的调用）
        - 连接重连配置（自动重连断开的连接）
        """
        address = self.settings.GRPC_ADDRESS
        options = self.settings.get_channel_options()
        credentials = self.settings.get_credentials()
        interceptors = self.settings.get_interceptors()
        
        # 如果有拦截器，使用拦截器包装通道
        if interceptors:
            if credentials is not None:
                # 使用安全通道
                channel = grpc.secure_channel(address, credentials, options=options)
            else:
                # 使用非安全通道
                channel = grpc.insecure_channel(address, options=options)
            
            # 使用拦截器包装通道
            from grpc import intercept_channel
            channel = intercept_channel(channel, *interceptors)
        else:
            # 没有拦截器，直接创建通道
            if credentials is not None:
                channel = grpc.secure_channel(address, credentials, options=options)
            else:
                channel = grpc.insecure_channel(address, options=options)
        
        return channel
    
    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    # ========== 健康检查接口 ==========
    
    def health_check(self):
        """健康检查"""
        from agent_queues import HealthCheckRequest
        return self.stub.HealthCheck(HealthCheckRequest())
    
    # ========== 队列管理接口 ==========
    
    def create_queue(self, agent_id: str):
        """
        创建队列（如果不存在）
        
        此方法会先检查队列是否存在，如果已存在则直接返回成功，不存在才创建新队列。
        这样可以避免重复创建队列，提高系统的健壮性。
        
        Args:
            agent_id: Agent ID
        
        Returns:
            CreateQueueResponse: 创建队列响应，包含以下字段：
                - success: 是否成功
                - agent_id: Agent ID
                - message: 消息
                - already_exists: 队列是否已存在（True=已存在，False=新创建）
        
        示例:
            # 创建队列（如果不存在）
            response = queue.create_queue("agent_001")
            if response.success:
                if response.already_exists:
                    print("队列已存在")
                else:
                    print("队列创建成功")
        """
        from agent_queues import CreateQueueRequest
        
        # 直接调用服务端接口，服务端会先检查是否存在，不存在才创建
        # 服务端会返回 already_exists 字段标识队列是已存在还是新创建的
        response = self.stub.CreateQueue(CreateQueueRequest(agent_id=agent_id))
        return response
    
    def queue_exists(self, agent_id: str):
        """检查队列是否存在"""
        from agent_queues import QueueExistsRequest
        return self.stub.QueueExists(QueueExistsRequest(agent_id=agent_id))
    
    def get_queue_info(self, agent_id: str):
        """获取队列信息"""
        from agent_queues import GetQueueInfoRequest
        return self.stub.GetQueueInfo(GetQueueInfoRequest(agent_id=agent_id))
    
    def get_queue(self, agent_id: str, create_if_not_exists: bool = False):
        """
        通过 agent ID 获取对应的私有化任务队列
        
        此方法会检查队列是否存在，如果不存在且 create_if_not_exists=True，则自动创建队列。
        返回一个 AgentQueue 对象，提供针对该 agent 的队列操作接口。
        
        Args:
            agent_id: Agent ID
            create_if_not_exists: 如果队列不存在，是否自动创建（默认 False）
        
        Returns:
            AgentQueue: 针对指定 agent 的队列对象
        
        示例:
            # 获取队列（如果不存在则创建）
            queue = client.get_queue("agent_001", create_if_not_exists=True)
            
            # 使用队列对象进行操作
            response = queue.submit_task(
                task_type=DATA_PROCESSING,
                payload='{"data": "test"}',
                priority=9
            )
            
            # 获取队列信息
            info = queue.get_info()
            print(f"队列中有 {info.pending_count} 个待处理任务")
        """
        # 检查队列是否存在
        exists_response = self.queue_exists(agent_id)
        
        if not exists_response.exists:
            if create_if_not_exists:
                # 自动创建队列
                create_response = self.create_queue(agent_id)
                if not create_response.success:
                    raise Exception(f"Failed to create queue for agent {agent_id}: {create_response.message}")
            else:
                raise ValueError(f"Queue for agent {agent_id} does not exist. Set create_if_not_exists=True to create it.")
        
        # 返回针对该 agent 的队列对象
        return AgentQueue(self, agent_id)
    
    def clear_queue(self, agent_id: str, status: int = 0, confirm: bool = True):
        """
        清空队列（根据 agentID 路由，可选按状态清空）
        
        Args:
            agent_id: Agent ID
            status: 任务状态（可选，0 表示清空所有状态）
            confirm: 确认标志（必须为 True 才能执行清空操作）
        
        Returns:
            ClearQueueResponse: 清空队列响应
        
        示例:
            # 清空所有任务
            response = queue.clear_queue("agent_001", confirm=True)
            
            # 只清空失败的任务
            from agent_queues import FAILED
            response = queue.clear_queue("agent_001", status=FAILED, confirm=True)
        """
        from agent_queues import ClearQueueRequest
        return self.stub.ClearQueue(ClearQueueRequest(
            agent_id=agent_id,
            status=status,
            confirm=confirm
        ))
    
    def delete_queue(self, agent_id: str, confirm: bool = True):
        """
        删除队列（完全删除队列，包括所有任务和队列本身）
        
        Args:
            agent_id: Agent ID
            confirm: 确认标志（必须为 True 才能执行删除操作）
        
        Returns:
            DeleteQueueResponse: 删除队列响应
        
        示例:
            # 删除整个队列
            response = queue.delete_queue("agent_001", confirm=True)
            if response.success:
                print(f"删除了 {response.deleted_count} 个任务")
        """
        from agent_queues import DeleteQueueRequest
        return self.stub.DeleteQueue(DeleteQueueRequest(
            agent_id=agent_id,
            confirm=confirm
        ))
    
    # ========== 任务操作接口 ==========
    
    def submit_task(self, agent_id: str, task_type: int, payload: str, custom_task_type: str = "", priority: int = 5, client_request_id: str = ""):
        """
        提交任务
        
        Args:
            agent_id: Agent ID
            task_type: 任务类型（枚举值）
            payload: 任务负载（JSON字符串）
            custom_task_type: 自定义任务类型（当 task_type 为 CUSTOM 时使用）
            priority: 任务优先级（0-9，数字越大优先级越高，默认5）
            client_request_id: 客户端请求ID（可选，用于幂等性）
        
        Returns:
            SubmitTaskResponse
        """
        from agent_queues import SubmitTaskRequest
        request = SubmitTaskRequest(
            agent_id=agent_id,
            type=task_type,
            task_type=custom_task_type,
            payload=payload,
            priority=priority
        )
        if client_request_id:
            request.client_request_id = client_request_id
        return self.stub.SubmitTask(request)
    
    def batch_submit_tasks(self, agent_id: str, tasks):
        """批量提交任务"""
        from agent_queues import BatchSubmitTasksRequest
        return self.stub.BatchSubmitTasks(BatchSubmitTasksRequest(
            agent_id=agent_id,
            tasks=tasks
        ))
    
    def get_task(self, agent_id: str, timeout: int = 0):
        """获取任务"""
        from agent_queues import GetTaskRequest
        return self.stub.GetTask(GetTaskRequest(agent_id=agent_id, timeout=timeout))
    
    def query_task(self, task_id: str, agent_id: str):
        """查询任务"""
        from agent_queues import QueryTaskRequest
        return self.stub.QueryTask(QueryTaskRequest(task_id=task_id, agent_id=agent_id))
    
    def update_task_status(self, task_id: str, agent_id: str, status: int, result: str = "", error_message: str = ""):
        """更新任务状态"""
        from agent_queues import UpdateTaskStatusRequest
        return self.stub.UpdateTaskStatus(UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=agent_id,
            status=status,
            result=result,
            error_message=error_message
        ))
    
    def delete_task(self, task_id: str, agent_id: str):
        """删除任务"""
        from agent_queues import DeleteTaskRequest
        return self.stub.DeleteTask(DeleteTaskRequest(task_id=task_id, agent_id=agent_id))
    
    def batch_delete_tasks(self, agent_id: str, task_ids: list, status: int = 0):
        """批量删除任务"""
        from agent_queues import BatchDeleteTasksRequest
        return self.stub.BatchDeleteTasks(BatchDeleteTasksRequest(
            agent_id=agent_id,
            task_ids=task_ids,
            status=status
        ))
    
    def cancel_task(self, task_id: str, agent_id: str, reason: str = ""):
        """取消任务"""
        from agent_queues import CancelTaskRequest
        return self.stub.CancelTask(CancelTaskRequest(
            task_id=task_id,
            agent_id=agent_id,
            reason=reason
        ))
    
    def retry_task(self, task_id: str, agent_id: str, client_request_id: str = ""):
        """
        重试任务
        
        Args:
            task_id: 任务ID
            agent_id: Agent ID
            client_request_id: 客户端请求ID（可选，用于幂等性）
        
        Returns:
            RetryTaskResponse
        """
        from agent_queues import RetryTaskRequest
        request = RetryTaskRequest(task_id=task_id, agent_id=agent_id)
        if client_request_id:
            request.client_request_id = client_request_id
        return self.stub.RetryTask(request)
    
    # ========== 任务查询接口 ==========
    
    def list_tasks(self, agent_id: str, status: int = 0, limit: int = 100, offset: int = 0):
        """列出任务"""
        from agent_queues import ListTasksRequest
        return self.stub.ListTasks(ListTasksRequest(
            agent_id=agent_id,
            status=status,
            limit=limit,
            offset=offset
        ))
    
    def get_task_stats(self, agent_id: str, status: int = 0):
        """获取任务统计信息"""
        from agent_queues import GetTaskStatsRequest
        return self.stub.GetTaskStats(GetTaskStatsRequest(agent_id=agent_id, status=status))
    
    def get_tasks_by_status(self, agent_id: str, status: int, limit: int = 100, offset: int = 0):
        """
        获取某个状态的任务（根据 agentID 和状态路由）
        
        Args:
            agent_id: Agent ID
            status: 任务状态（必填，不能为 0）
            limit: 限制数量（1-1000，默认 100）
            offset: 偏移量（>=0，默认 0）
        
        Returns:
            GetTasksByStatusResponse: 任务列表响应
        
        示例:
            # 获取所有待处理的任务
            from agent_queues import PENDING
            response = queue.get_tasks_by_status("agent_001", status=PENDING, limit=50)
            if response.success:
                print(f"找到 {response.total} 个待处理任务")
                for task in response.tasks:
                    print(f"任务 ID: {task.task_id}")
        """
        from agent_queues import GetTasksByStatusRequest
        return self.stub.GetTasksByStatus(GetTasksByStatusRequest(
            agent_id=agent_id,
            status=status,
            limit=limit,
            offset=offset
        ))


def create_client(
    config_path: Optional[str] = None,
    base_settings: Optional[ClientSettings] = None,
    **config_overrides
) -> PrivateAgentTasksQueue:
    """
    便捷函数：创建私有化 Agent 任务队列客户端
    
    Args:
        config_path: 配置文件路径（可选）
        base_settings: 基础配置实例（可选）
        **config_overrides: 配置覆盖项
        
    Returns:
        PrivateAgentTasksQueue 实例
        
    示例:
        # 使用默认配置
        queue = create_client()
        
        # 覆盖部分配置
        queue = create_client(grpc_host="192.168.1.100", grpc_port=50052)
        
        # 使用配置文件
        queue = create_client(config_path="/path/to/config.yaml")
    """
    return PrivateAgentTasksQueue(
        config_path=config_path,
        base_settings=base_settings,
        **config_overrides
    )


# 向后兼容：保留 AgentClient 作为别名
AgentClient = PrivateAgentTasksQueue


class AgentQueue:
    """
    针对特定 agent 的队列操作封装类
    
    通过 PrivateAgentTasksQueue.get_queue(agent_id) 获取此对象，
    提供针对特定 agent 的便捷队列操作接口。
    
    使用示例:
        # 获取队列对象
        client = PrivateAgentTasksQueue()
        queue = client.get_queue("agent_001", create_if_not_exists=True)
        
        # 提交任务（不需要再指定 agent_id）
        response = queue.submit_task(
            task_type=DATA_PROCESSING,
            payload='{"data": "test"}',
            priority=9
        )
        
        # 获取任务
        task = queue.get_task(timeout=5)
        
        # 获取队列信息
        info = queue.get_info()
    """
    
    def __init__(self, client: PrivateAgentTasksQueue, agent_id: str):
        """
        初始化 Agent 队列对象
        
        Args:
            client: PrivateAgentTasksQueue 客户端实例
            agent_id: Agent ID
        """
        self.client = client
        self.agent_id = agent_id
    
    # ========== 队列管理接口 ==========
    
    def get_info(self):
        """获取队列信息"""
        return self.client.get_queue_info(self.agent_id)
    
    def exists(self) -> bool:
        """检查队列是否存在"""
        response = self.client.queue_exists(self.agent_id)
        return response.exists
    
    def clear(self, status: int = 0, confirm: bool = True):
        """清空队列"""
        return self.client.clear_queue(self.agent_id, status=status, confirm=confirm)
    
    def delete(self, confirm: bool = True):
        """删除队列"""
        return self.client.delete_queue(self.agent_id, confirm=confirm)
    
    # ========== 任务操作接口 ==========
    
    def submit_task(self, task_type: int, payload: str, custom_task_type: str = "", priority: int = 5, client_request_id: str = ""):
        """提交任务"""
        return self.client.submit_task(
            agent_id=self.agent_id,
            task_type=task_type,
            payload=payload,
            custom_task_type=custom_task_type,
            priority=priority,
            client_request_id=client_request_id
        )
    
    def batch_submit_tasks(self, tasks):
        """批量提交任务"""
        return self.client.batch_submit_tasks(self.agent_id, tasks)
    
    def get_task(self, timeout: int = 0):
        """获取任务"""
        return self.client.get_task(self.agent_id, timeout=timeout)
    
    def query_task(self, task_id: str):
        """查询任务"""
        return self.client.query_task(task_id, self.agent_id)
    
    def update_task_status(self, task_id: str, status: int, result: str = "", error_message: str = ""):
        """更新任务状态"""
        return self.client.update_task_status(
            task_id=task_id,
            agent_id=self.agent_id,
            status=status,
            result=result,
            error_message=error_message
        )
    
    def delete_task(self, task_id: str):
        """删除任务"""
        return self.client.delete_task(task_id, self.agent_id)
    
    def batch_delete_tasks(self, task_ids: list, status: int = 0):
        """批量删除任务"""
        return self.client.batch_delete_tasks(self.agent_id, task_ids, status=status)
    
    def cancel_task(self, task_id: str, reason: str = ""):
        """取消任务"""
        return self.client.cancel_task(task_id, self.agent_id, reason=reason)
    
    def retry_task(self, task_id: str, client_request_id: str = ""):
        """重试任务"""
        return self.client.retry_task(task_id, self.agent_id, client_request_id=client_request_id)
    
    # ========== 任务查询接口 ==========
    
    def list_tasks(self, status: int = 0, limit: int = 100, offset: int = 0):
        """列出任务"""
        return self.client.list_tasks(self.agent_id, status=status, limit=limit, offset=offset)
    
    def get_task_stats(self, status: int = 0):
        """获取任务统计信息"""
        return self.client.get_task_stats(self.agent_id, status=status)
    
    def get_tasks_by_status(self, status: int, limit: int = 100, offset: int = 0):
        """获取某个状态的任务"""
        return self.client.get_tasks_by_status(self.agent_id, status=status, limit=limit, offset=offset)

