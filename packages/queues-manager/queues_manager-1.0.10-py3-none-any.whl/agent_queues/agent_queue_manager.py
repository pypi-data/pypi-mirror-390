"""私有化 Agent 任务队列管理器 - 方便其他 agent 分配任务给某个 agent"""
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from collections import defaultdict

from agent_queues.agent_queue import PrivateAgentTasksQueue

logger = logging.getLogger(__name__)


class AgentQueueManager:
    """
    私有化 Agent 任务队列管理器
    
    提供高级接口，方便其他 agent 分配任务给某个 agent，包括：
    - 任务分配和路由
    - 批量任务分配
    - 负载均衡
    - 任务分发策略
    - 队列状态监控
    
    使用示例:
        # 创建管理器
        manager = AgentQueueManager()
        
        # 分配单个任务给某个 agent
        result = manager.assign_task(
            target_agent_id="agent_001",
            task_type=DATA_PROCESSING,
            payload={"data": "test"}
        )
        
        # 批量分配任务
        results = manager.batch_assign_tasks(
            target_agent_id="agent_001",
            tasks=[
                {"type": DATA_PROCESSING, "payload": {"data": "task1"}},
                {"type": IMAGE_PROCESSING, "payload": {"data": "task2"}},
            ]
        )
        
        # 使用负载均衡分配任务
        result = manager.assign_task_with_load_balance(
            candidate_agents=["agent_001", "agent_002", "agent_003"],
            task_type=DATA_PROCESSING,
            payload={"data": "test"}
        )
    """
    
    def __init__(
        self,
        queue_client: Optional[PrivateAgentTasksQueue] = None,
        **queue_client_kwargs
    ):
        """
        初始化 Agent 任务队列管理器
        
        Args:
            queue_client: 队列客户端实例（可选），如果不提供则自动创建
            **queue_client_kwargs: 传递给 PrivateAgentTasksQueue 的参数
        """
        if queue_client is None:
            self.queue_client = PrivateAgentTasksQueue(**queue_client_kwargs)
        else:
            self.queue_client = queue_client
        
        # 任务分配统计
        self._assignment_stats = defaultdict(int)
    
    def _ensure_queue_exists(self, agent_id: str) -> Tuple[bool, Optional[str]]:
        """
        确保 agent 的队列存在，如果不存在则创建
        
        Args:
            agent_id: Agent ID
        
        Returns:
            (是否成功, 错误信息)
        """
        try:
            # 检查队列是否存在
            queue_info = self.queue_client.queue_exists(agent_id)
            if queue_info.exists:
                return True, None
            
            # 队列不存在，创建队列
            logger.info(f"Queue for agent {agent_id} does not exist, creating...")
            create_result = self.queue_client.create_queue(agent_id)
            if create_result.success:
                logger.info(f"Queue created successfully for agent {agent_id}")
                return True, None
            else:
                error_msg = f"Failed to create queue for agent {agent_id}: {create_result.message}"
                logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"Error checking/creating queue for agent {agent_id}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def assign_task(
        self,
        target_agent_id: str,
        task_type: int,
        payload: Union[Dict[str, Any], str],
        custom_task_type: str = "",
        priority: int = 5,
        client_request_id: str = "",
        ensure_queue_exists: bool = True
    ) -> Dict[str, Any]:
        """
        分配单个任务给指定的 agent
        
        如果 agent 的队列不存在，会自动创建队列后再分配任务。
        任务会按照优先级自动排序，高优先级任务优先被执行。
        
        Args:
            target_agent_id: 目标 agent ID
            task_type: 任务类型（枚举值）
            payload: 任务负载（字典或 JSON 字符串）
            custom_task_type: 自定义任务类型（当 task_type 为 CUSTOM 时使用）
            priority: 任务优先级（0-9，数字越大优先级越高，默认5）
            client_request_id: 客户端请求ID（可选，用于幂等性）
            ensure_queue_exists: 是否确保队列存在（如果不存在则创建，默认 True）
        
        Returns:
            分配结果字典，包含 success, task_id, message 等字段
        
        示例:
            result = manager.assign_task(
                target_agent_id="agent_001",
                task_type=DATA_PROCESSING,
                payload={"data": "test", "action": "process"},
                priority=9  # 高优先级
            )
            if result["success"]:
                print(f"任务已分配，任务ID: {result['task_id']}")
        """
        try:
            # 确保队列存在
            if ensure_queue_exists:
                success, error_msg = self._ensure_queue_exists(target_agent_id)
                if not success:
                    return {
                        "success": False,
                        "task_id": None,
                        "message": error_msg or f"Failed to ensure queue exists for agent {target_agent_id}",
                        "error": "QUEUE_CREATION_FAILED",
                        "target_agent_id": target_agent_id
                    }
            
            # 转换 payload
            if isinstance(payload, dict):
                payload_str = json.dumps(payload, ensure_ascii=False)
            else:
                payload_str = str(payload)
            
            # 提交任务
            response = self.queue_client.submit_task(
                agent_id=target_agent_id,
                task_type=task_type,
                payload=payload_str,
                custom_task_type=custom_task_type,
                priority=priority,
                client_request_id=client_request_id
            )
            
            # 更新统计
            if response.success:
                self._assignment_stats[target_agent_id] += 1
            
            return {
                "success": response.success,
                "task_id": response.task_id if response.success else None,
                "message": response.message,
                "target_agent_id": target_agent_id
            }
        except Exception as e:
            logger.error(f"Failed to assign task to agent {target_agent_id}: {e}")
            return {
                "success": False,
                "task_id": None,
                "message": str(e),
                "error": "ASSIGNMENT_FAILED",
                "target_agent_id": target_agent_id
            }
    
    def batch_assign_tasks(
        self,
        target_agent_id: str,
        tasks: List[Dict[str, Any]],
        ensure_queue_exists: bool = True
    ) -> Dict[str, Any]:
        """
        批量分配任务给指定的 agent
        
        如果 agent 的队列不存在，会自动创建队列后再分配任务。
        
        Args:
            target_agent_id: 目标 agent ID
            tasks: 任务列表，每个任务包含 type, payload, task_type(可选) 等字段
            ensure_queue_exists: 是否确保队列存在（如果不存在则创建，默认 True）
        
        Returns:
            批量分配结果，包含 success, results, summary 等字段
        
        示例:
            results = manager.batch_assign_tasks(
                target_agent_id="agent_001",
                tasks=[
                    {"type": DATA_PROCESSING, "payload": {"data": "task1"}},
                    {"type": IMAGE_PROCESSING, "payload": {"data": "task2"}},
                ]
            )
            print(f"成功: {results['summary']['success_count']}, 失败: {results['summary']['failure_count']}")
        """
        try:
            # 确保队列存在
            if ensure_queue_exists:
                success, error_msg = self._ensure_queue_exists(target_agent_id)
                if not success:
                    return {
                        "success": False,
                        "results": [],
                        "summary": {
                            "total": len(tasks),
                            "success_count": 0,
                            "failure_count": len(tasks)
                        },
                        "message": error_msg or f"Failed to ensure queue exists for agent {target_agent_id}",
                        "error": "QUEUE_CREATION_FAILED",
                        "target_agent_id": target_agent_id
                    }
            
            # 准备批量任务
            proto_tasks = []
            for task in tasks:
                task_type = task.get("type")
                payload = task.get("payload", {})
                custom_task_type = task.get("task_type", "")
                task_id = task.get("task_id", "")
                client_request_id = task.get("client_request_id", "")
                priority = task.get("priority", 5)  # 默认优先级为5
                
                # 转换 payload
                if isinstance(payload, dict):
                    payload_str = json.dumps(payload, ensure_ascii=False)
                else:
                    payload_str = str(payload)
                
                # 创建 proto SubmitTaskItem 对象
                from agent_queues import SubmitTaskItem
                proto_task = SubmitTaskItem(
                    type=task_type,
                    task_type=custom_task_type,
                    payload=payload_str,
                    task_id=task_id if task_id else None,
                    client_request_id=client_request_id if client_request_id else None,
                    priority=priority
                )
                proto_tasks.append(proto_task)
            
            # 批量提交
            response = self.queue_client.batch_submit_tasks(
                agent_id=target_agent_id,
                tasks=proto_tasks
            )
            
            # 更新统计
            if response.success:
                self._assignment_stats[target_agent_id] += len(proto_tasks)
            
            return {
                "success": response.success,
                "results": [
                    {
                        "task_id": task_id,
                        "success": True
                    }
                    for task_id in response.task_ids
                ] if response.success else [],
                "summary": {
                    "total": len(tasks),
                    "success_count": len(response.task_ids) if response.success else 0,
                    "failure_count": len(tasks) - len(response.task_ids) if response.success else len(tasks)
                },
                "message": response.message,
                "target_agent_id": target_agent_id
            }
        except Exception as e:
            logger.error(f"Failed to batch assign tasks to agent {target_agent_id}: {e}")
            return {
                "success": False,
                "results": [],
                "summary": {
                    "total": len(tasks),
                    "success_count": 0,
                    "failure_count": len(tasks)
                },
                "message": str(e),
                "error": "BATCH_ASSIGNMENT_FAILED",
                "target_agent_id": target_agent_id
            }
    
    def assign_task_with_load_balance(
        self,
        candidate_agents: List[str],
        task_type: int,
        payload: Union[Dict[str, Any], str],
        custom_task_type: str = "",
        priority: int = 5,
        client_request_id: str = "",
        strategy: str = "least_pending",
        load_balance_func: Optional[Callable[[List[str]], str]] = None,
        ensure_queue_exists: bool = True
    ) -> Dict[str, Any]:
        """
        使用负载均衡策略分配任务给候选 agent 之一
        
        如果选中的 agent 的队列不存在，会自动创建队列后再分配任务。
        
        Args:
            candidate_agents: 候选 agent ID 列表
            task_type: 任务类型
            payload: 任务负载
            custom_task_type: 自定义任务类型
            strategy: 负载均衡策略
                - "least_pending": 选择待处理任务最少的 agent（默认）
                - "round_robin": 轮询分配
                - "random": 随机选择
                - "custom": 使用自定义函数
            load_balance_func: 自定义负载均衡函数，接收 agent 列表，返回选中的 agent ID
            ensure_queue_exists: 是否确保队列存在（如果不存在则创建，默认 True）
        
        Returns:
            分配结果
        
        示例:
            result = manager.assign_task_with_load_balance(
                candidate_agents=["agent_001", "agent_002", "agent_003"],
                task_type=DATA_PROCESSING,
                payload={"data": "test"},
                strategy="least_pending"
            )
        """
        if not candidate_agents:
            return {
                "success": False,
                "task_id": None,
                "message": "No candidate agents provided",
                "error": "NO_CANDIDATES"
            }
        
        # 选择目标 agent
        if strategy == "custom" and load_balance_func:
            target_agent_id = load_balance_func(candidate_agents)
        elif strategy == "round_robin":
            target_agent_id = self._round_robin_select(candidate_agents)
        elif strategy == "random":
            import random
            target_agent_id = random.choice(candidate_agents)
        elif strategy == "least_pending":
            target_agent_id = self._select_least_pending_agent(candidate_agents)
        else:
            # 默认使用第一个
            target_agent_id = candidate_agents[0]
        
        # 分配任务（会自动确保队列存在）
        result = self.assign_task(
            target_agent_id=target_agent_id,
            task_type=task_type,
            payload=payload,
            custom_task_type=custom_task_type,
            priority=priority,
            client_request_id=client_request_id,
            ensure_queue_exists=ensure_queue_exists
        )
        
        result["selected_agent_id"] = target_agent_id
        result["strategy"] = strategy
        result["candidate_agents"] = candidate_agents
        
        return result
    
    def distribute_tasks(
        self,
        tasks: List[Dict[str, Any]],
        target_agents: Union[str, List[str]],
        distribution_strategy: str = "round_robin",
        ensure_queue_exists: bool = True
    ) -> Dict[str, Any]:
        """
        将任务列表分发给多个 agent
        
        如果目标 agent 的队列不存在，会自动创建队列后再分配任务。
        
        Args:
            tasks: 任务列表
            target_agents: 目标 agent ID 或 agent ID 列表
            distribution_strategy: 分发策略
                - "round_robin": 轮询分发
                - "random": 随机分发
                - "single": 所有任务发给单个 agent
            ensure_queue_exists: 是否确保队列存在（如果不存在则创建，默认 True）
        
        Returns:
            分发结果，包含每个 agent 的分配结果
        
        示例:
            results = manager.distribute_tasks(
                tasks=[
                    {"type": DATA_PROCESSING, "payload": {"data": "task1"}},
                    {"type": DATA_PROCESSING, "payload": {"data": "task2"}},
                ],
                target_agents=["agent_001", "agent_002"],
                distribution_strategy="round_robin"
            )
        """
        # 标准化 target_agents
        if isinstance(target_agents, str):
            target_agents = [target_agents]
        
        if not target_agents:
            return {
                "success": False,
                "results": {},
                "message": "No target agents provided"
            }
        
        # 分发任务
        agent_tasks = defaultdict(list)
        
        if distribution_strategy == "single":
            # 所有任务发给第一个 agent
            for task in tasks:
                agent_tasks[target_agents[0]].append(task)
        elif distribution_strategy == "random":
            import random
            for task in tasks:
                agent_id = random.choice(target_agents)
                agent_tasks[agent_id].append(task)
        else:  # round_robin
            for i, task in enumerate(tasks):
                agent_id = target_agents[i % len(target_agents)]
                agent_tasks[agent_id].append(task)
        
        # 批量分配给每个 agent（会自动确保队列存在）
        results = {}
        for agent_id, agent_task_list in agent_tasks.items():
            result = self.batch_assign_tasks(
                target_agent_id=agent_id,
                tasks=agent_task_list,
                ensure_queue_exists=ensure_queue_exists
            )
            results[agent_id] = result
        
        # 汇总
        total_success = sum(r.get("summary", {}).get("success_count", 0) for r in results.values())
        total_failure = sum(r.get("summary", {}).get("failure_count", 0) for r in results.values())
        
        return {
            "success": total_failure == 0,
            "results": results,
            "summary": {
                "total": len(tasks),
                "success_count": total_success,
                "failure_count": total_failure,
                "agents_used": list(results.keys())
            },
            "distribution_strategy": distribution_strategy
        }
    
    def get_agent_queue_status(self, agent_id: str) -> Dict[str, Any]:
        """
        获取 agent 队列状态
        
        Args:
            agent_id: Agent ID
        
        Returns:
            队列状态信息
        """
        try:
            queue_info = self.queue_client.get_queue_info(agent_id)
            return {
                "agent_id": agent_id,
                "exists": True,
                "pending_count": queue_info.pending_count,
                "processing_count": queue_info.processing_count,
                "completed_count": queue_info.completed_count,
                "failed_count": queue_info.failed_count,
                "total_count": queue_info.total_count
            }
        except Exception as e:
            logger.error(f"Failed to get queue status for agent {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "exists": False,
                "error": str(e)
            }
    
    def get_multiple_agents_status(self, agent_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        获取多个 agent 的队列状态
        
        Args:
            agent_ids: Agent ID 列表
        
        Returns:
            每个 agent 的状态字典
        """
        statuses = {}
        for agent_id in agent_ids:
            statuses[agent_id] = self.get_agent_queue_status(agent_id)
        return statuses
    
    def get_assignment_stats(self) -> Dict[str, int]:
        """
        获取任务分配统计信息
        
        Returns:
            每个 agent 的分配任务数量统计
        """
        return dict(self._assignment_stats)
    
    def reset_assignment_stats(self):
        """重置任务分配统计"""
        self._assignment_stats.clear()
    
    def _select_least_pending_agent(self, candidate_agents: List[str]) -> str:
        """选择待处理任务最少的 agent"""
        if not candidate_agents:
            raise ValueError("No candidate agents provided")
        
        if len(candidate_agents) == 1:
            return candidate_agents[0]
        
        # 获取所有候选 agent 的状态
        statuses = self.get_multiple_agents_status(candidate_agents)
        
        # 选择待处理任务最少的 agent
        best_agent = None
        min_pending = float('inf')
        
        for agent_id, status in statuses.items():
            if not status.get("exists", False):
                # 如果队列不存在，优先选择（待处理任务为0）
                return agent_id
            
            pending = status.get("pending_count", 0)
            if pending < min_pending:
                min_pending = pending
                best_agent = agent_id
        
        return best_agent or candidate_agents[0]
    
    def _round_robin_select(self, candidate_agents: List[str]) -> str:
        """轮询选择 agent"""
        if not hasattr(self, '_round_robin_index'):
            self._round_robin_index = {}
        
        # 为每个候选列表维护独立的索引
        agents_key = tuple(sorted(candidate_agents))
        if agents_key not in self._round_robin_index:
            self._round_robin_index[agents_key] = 0
        
        index = self._round_robin_index[agents_key]
        selected = candidate_agents[index % len(candidate_agents)]
        self._round_robin_index[agents_key] = (index + 1) % len(candidate_agents)
        
        return selected
    
    def close(self):
        """关闭管理器（关闭底层队列客户端）"""
        if self.queue_client:
            self.queue_client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


def create_manager(
    queue_client: Optional[PrivateAgentTasksQueue] = None,
    **queue_client_kwargs
) -> AgentQueueManager:
    """
    便捷函数：创建 Agent 任务队列管理器
    
    Args:
        queue_client: 队列客户端实例（可选）
        **queue_client_kwargs: 传递给 PrivateAgentTasksQueue 的参数
    
    Returns:
        AgentQueueManager 实例
    
    示例:
        # 使用默认配置
        manager = create_manager()
        
        # 使用自定义配置
        manager = create_manager(grpc_host="192.168.1.100", grpc_port=50052)
    """
    return AgentQueueManager(queue_client=queue_client, **queue_client_kwargs)

