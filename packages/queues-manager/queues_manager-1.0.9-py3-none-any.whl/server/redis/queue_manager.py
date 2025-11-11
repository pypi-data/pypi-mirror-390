"""队列管理器 - 使用字典存储任务，统一使用 proto 定义"""
import json
import logging
import time
import uuid
from typing import Dict, List, Optional, Any, Tuple

import redis
from server.settings import settings

# 从 proto 导入状态枚举值
try:
    from agent_queues import queue_service_pb2
    PENDING = queue_service_pb2.PENDING
    PROCESSING = queue_service_pb2.PROCESSING
    COMPLETED = queue_service_pb2.COMPLETED
    FAILED = queue_service_pb2.FAILED
except ImportError:
    # 如果 proto 未生成，使用默认值
    PENDING = 0
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3

logger = logging.getLogger(__name__)


class QueueManager:
    """基于 Redis 的队列管理器 - 使用字典存储任务"""
    
    def __init__(self):
        """初始化队列管理器"""
        # 使用配置的 Redis 连接参数（包含连接池、SSL、超时等配置）
        redis_kwargs = settings.get_redis_connection_kwargs()
        
        # 提取连接池相关参数
        pool_kwargs = {
            "host": redis_kwargs.pop("host"),
            "port": redis_kwargs.pop("port"),
            "db": redis_kwargs.pop("db"),
            "password": redis_kwargs.pop("password"),
            "max_connections": redis_kwargs.pop("max_connections", 50),
            "retry_on_timeout": redis_kwargs.pop("retry_on_timeout", True),
            "health_check_interval": redis_kwargs.pop("health_check_interval", 30),
            "socket_connect_timeout": redis_kwargs.pop("socket_connect_timeout", 5),
            "socket_timeout": redis_kwargs.pop("socket_timeout", 5),
            "socket_keepalive": redis_kwargs.pop("socket_keepalive", True),
            "decode_responses": redis_kwargs.pop("decode_responses", False),
            "encoding": redis_kwargs.pop("encoding", "utf-8"),
            "encoding_errors": redis_kwargs.pop("encoding_errors", "strict"),
        }
        
        # 处理 socket_keepalive_options（需要将字符串键转换为 socket 常量）
        # Windows 上可能不支持这些选项，直接跳过
        socket_keepalive_opts = redis_kwargs.pop("socket_keepalive_options", {})
        if socket_keepalive_opts:
            import sys
            if sys.platform != "win32":
                # 只在非 Windows 系统上设置 socket_keepalive_options
                import socket
                keepalive_opts = {}
                socket_const_map = {
                    "TCP_KEEPIDLE": getattr(socket, "TCP_KEEPIDLE", None),
                    "TCP_KEEPINTVL": getattr(socket, "TCP_KEEPINTVL", None),
                    "TCP_KEEPCNT": getattr(socket, "TCP_KEEPCNT", None),
                }
                for key, value in socket_keepalive_opts.items():
                    socket_const = socket_const_map.get(key)
                    if socket_const is not None:
                        keepalive_opts[socket_const] = int(value)
                if keepalive_opts:
                    pool_kwargs["socket_keepalive_options"] = keepalive_opts
            else:
                # Windows 上跳过 socket_keepalive_options
                logger.debug("socket_keepalive_options skipped on Windows platform")
        
        # 添加 SSL 相关配置（如果存在）
        ssl_keys = ["ssl", "ssl_cert_reqs", "ssl_ca_certs", "ssl_certfile", "ssl_keyfile", "ssl_check_hostname"]
        for key in ssl_keys:
            if key in redis_kwargs:
                pool_kwargs[key] = redis_kwargs.pop(key)
        
        # 创建连接池（提升性能和稳定性）
        from redis.connection import ConnectionPool
        pool = ConnectionPool(**pool_kwargs)
        
        self.redis_client = redis.Redis(connection_pool=pool)
        self.task_prefix = settings.TASK_PREFIX
    
    def _get_queue_key(self, agent_id: str) -> str:
        """获取队列键名（优先级队列，使用Sorted Set）"""
        return f"{self.task_prefix}:{agent_id}:queue"
    
    def _get_task_key(self, task_id: str) -> str:
        """获取任务键名"""
        return f"{self.task_prefix}:task:{task_id}"
    
    def _get_task_status_key(self, agent_id: str, status: int) -> str:
        """获取任务状态集合键名"""
        return f"{self.task_prefix}:{agent_id}:status:{status}"
    
    def _get_idempotency_key(self, agent_id: str, client_request_id: str) -> str:
        """获取幂等性键名（用于存储 client_request_id 到 task_id 的映射）"""
        return f"{self.task_prefix}:{agent_id}:idempotency:{client_request_id}"
    
    def _calculate_priority_score(self, priority: int, created_at: int) -> float:
        """
        计算优先级分数（用于Sorted Set排序）
        
        分数 = priority * 1000000000 + (999999999 - created_at)
        这样高优先级任务分数更高，同优先级下先创建的任务优先
        
        Args:
            priority: 任务优先级（0-9）
            created_at: 创建时间戳（秒）
        
        Returns:
            优先级分数
        """
        # 限制优先级范围
        priority = max(0, min(9, priority))
        # 使用大数确保优先级占主导，时间戳作为次要排序
        # 999999999 - created_at 确保同优先级下先创建的任务优先
        return priority * 1000000000.0 + (999999999 - created_at)
    
    def submit_task(self, task_dict: Dict[str, Any]) -> Tuple[bool, Optional[str], bool]:
        """
        提交任务到队列（支持优先级排序和幂等性检查）
        
        Args:
            task_dict: 任务字典，包含 task_id, agent_id, task_type, payload, status, priority, client_request_id 等
        
        Returns:
            (是否成功, 任务ID, 是否是新任务)
            - 如果成功且是新任务：(True, task_id, True)
            - 如果成功但是已存在的任务（幂等性）：(True, existing_task_id, False)
            - 如果失败：(False, None, False)
        """
        try:
            agent_id = task_dict["agent_id"]
            client_request_id = task_dict.get("client_request_id")
            
            # 幂等性检查：如果提供了 client_request_id，检查是否已存在
            if client_request_id:
                existing_task_id = self._check_idempotency(agent_id, client_request_id)
                if existing_task_id:
                    # 任务已存在，返回已存在的任务ID
                    logger.info(
                        f"Task with client_request_id {client_request_id} already exists: {existing_task_id} "
                        f"(idempotency check passed)"
                    )
                    return True, existing_task_id, False
            
            # 创建新任务
            task_id = task_dict.get("task_id") or str(uuid.uuid4())
            status = task_dict.get("status", PENDING)
            priority = task_dict.get("priority", 5)  # 默认优先级为5
            
            # 确保任务字典包含必要字段
            task_dict["task_id"] = task_id
            task_dict["status"] = status
            task_dict["priority"] = priority
            created_at = int(time.time())
            task_dict.setdefault("created_at", created_at)
            task_dict.setdefault("updated_at", created_at)
            
            # 保存任务详情
            task_key = self._get_task_key(task_id)
            task_data = json.dumps(task_dict)
            # 如果 TASK_RESULT_EXPIRES 为 None，则不设置过期时间（任务不过期）
            if settings.TASK_RESULT_EXPIRES is None:
                self.redis_client.set(task_key, task_data)
            else:
                self.redis_client.set(task_key, task_data, ex=settings.TASK_RESULT_EXPIRES)
            
            # 添加到优先级队列（使用Sorted Set，按优先级排序）
            queue_key = self._get_queue_key(agent_id)
            priority_score = self._calculate_priority_score(priority, created_at)
            # 使用 zadd 添加到有序集合，分数越高优先级越高
            self.redis_client.zadd(queue_key, {task_id: priority_score})
            
            # 添加到状态集合
            status_key = self._get_task_status_key(agent_id, status)
            self.redis_client.sadd(status_key, task_id)
            
            # 存储幂等性映射（如果提供了 client_request_id）
            if client_request_id:
                self._store_idempotency_mapping(agent_id, client_request_id, task_id)
            
            logger.info(f"Task {task_id} submitted to queue for agent {agent_id} with priority {priority}")
            return True, task_id, True
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            return False, None, False
    
    def _check_idempotency(self, agent_id: str, client_request_id: str) -> Optional[str]:
        """
        检查幂等性：根据 client_request_id 查找是否已存在任务
        
        Args:
            agent_id: Agent ID
            client_request_id: 客户端请求ID
        
        Returns:
            如果已存在，返回已存在的任务ID；否则返回 None
        """
        try:
            idempotency_key = self._get_idempotency_key(agent_id, client_request_id)
            existing_task_id = self.redis_client.get(idempotency_key)
            
            if existing_task_id:
                # 如果 task_id 是 bytes，转换为字符串
                if isinstance(existing_task_id, bytes):
                    existing_task_id = existing_task_id.decode('utf-8')
                elif not isinstance(existing_task_id, str):
                    existing_task_id = str(existing_task_id)
                
                # 验证任务是否仍然存在（任务可能处于任何状态，只要存在即可）
                task_key = self._get_task_key(existing_task_id)
                if self.redis_client.exists(task_key):
                    logger.debug(f"Found existing task {existing_task_id} for client_request_id {client_request_id}")
                    return existing_task_id
                else:
                    # 任务已不存在，清理过期的幂等性映射
                    logger.warning(f"Task {existing_task_id} not found, cleaning up idempotency mapping")
                    self.redis_client.delete(idempotency_key)
                    return None
            
            return None
        except Exception as e:
            logger.error(f"Failed to check idempotency for {client_request_id}: {e}")
            return None
    
    def _store_idempotency_mapping(self, agent_id: str, client_request_id: str, task_id: str):
        """
        存储幂等性映射：client_request_id -> task_id
        
        Args:
            agent_id: Agent ID
            client_request_id: 客户端请求ID
            task_id: 任务ID
        """
        try:
            idempotency_key = self._get_idempotency_key(agent_id, client_request_id)
            
            # 存储映射，过期时间与任务相同
            if settings.TASK_RESULT_EXPIRES is None:
                self.redis_client.set(idempotency_key, task_id)
            else:
                self.redis_client.set(idempotency_key, task_id, ex=settings.TASK_RESULT_EXPIRES)
        except Exception as e:
            logger.error(f"Failed to store idempotency mapping for {client_request_id}: {e}")
    
    def get_task(self, agent_id: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """
        从队列获取任务（按优先级排序，高优先级优先）
        
        使用 Redis Sorted Set 实现优先级队列，高优先级任务优先被获取。
        
        Args:
            agent_id: Agent ID
            timeout: 超时时间（秒），0表示不等待
        
        Returns:
            任务字典，如果没有任务则返回 None
        """
        try:
            queue_key = self._get_queue_key(agent_id)
            
            # 使用 Sorted Set 的 zpopmax 获取最高优先级的任务（分数最高的）
            # 如果没有任务，返回 None
            if timeout > 0:
                # 阻塞式获取：循环检查直到有任务或超时
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # 尝试获取最高优先级的任务
                    result = self.redis_client.zpopmax(queue_key, count=1)
                    if result:
                        task_id = result[0][0] if isinstance(result[0], tuple) else result[0]
                        break
                    # 等待一小段时间后重试
                    time.sleep(0.1)
                else:
                    # 超时
                    return None
            else:
                # 非阻塞式获取：直接获取最高优先级的任务
                result = self.redis_client.zpopmax(queue_key, count=1)
                if not result:
                    return None
                task_id = result[0][0] if isinstance(result[0], tuple) else result[0]
            
            # 如果 task_id 是 bytes，转换为字符串
            if isinstance(task_id, bytes):
                task_id = task_id.decode('utf-8')
            
            # 获取任务详情
            task_dict = self.get_task_by_id(task_id, agent_id)
            if not task_dict:
                return None
            
            # 更新任务状态为处理中
            if task_dict.get("status") == PENDING:
                self._update_task_status_internal(task_dict, PROCESSING)
            
            return task_dict
        except Exception as e:
            logger.error(f"Failed to get task for agent {agent_id}: {e}")
            return None
    
    def get_task_by_id(self, task_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        根据任务ID获取任务
        
        Args:
            task_id: 任务ID
            agent_id: Agent ID
        
        Returns:
            任务字典，如果不存在则返回 None
        """
        try:
            task_key = self._get_task_key(task_id)
            task_data = self.redis_client.get(task_key)
            if not task_data:
                return None
            
            task_dict = json.loads(task_data)
            
            # 验证 agent_id 是否匹配
            if task_dict.get("agent_id") != agent_id:
                logger.warning(f"Task {task_id} does not belong to agent {agent_id}")
                return None
            
            return task_dict
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    def update_task_status(
        self,
        task_id: str,
        agent_id: str,
        status: int,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            agent_id: Agent ID
            status: 新状态（proto TaskStatus 枚举值）
            result: 任务结果（可选）
            error_message: 错误信息（可选）
        
        Returns:
            是否成功
        """
        try:
            task_dict = self.get_task_by_id(task_id, agent_id)
            if not task_dict:
                return False
            
            old_status = task_dict.get("status", PENDING)
            task_dict["status"] = status
            task_dict["updated_at"] = int(time.time())
            if result is not None:
                task_dict["result"] = result
            if error_message is not None:
                task_dict["error_message"] = error_message
            
            # 更新 Redis 中的任务数据
            task_key = self._get_task_key(task_id)
            task_data = json.dumps(task_dict)
            # 如果 TASK_RESULT_EXPIRES 为 None，则不设置过期时间（任务不过期）
            if settings.TASK_RESULT_EXPIRES is None:
                self.redis_client.set(task_key, task_data)
            else:
                self.redis_client.set(task_key, task_data, ex=settings.TASK_RESULT_EXPIRES)
            
            # 更新状态集合
            if old_status != status:
                old_status_key = self._get_task_status_key(agent_id, old_status)
                new_status_key = self._get_task_status_key(agent_id, status)
                self.redis_client.srem(old_status_key, task_id)
                self.redis_client.sadd(new_status_key, task_id)
            
            logger.info(f"Task {task_id} status updated to {status}")
            return True
        except Exception as e:
            logger.error(f"Failed to update task {task_id} status: {e}")
            return False
    
    def list_tasks(
        self,
        agent_id: str,
        status: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        列出任务
        
        Args:
            agent_id: Agent ID
            status: 任务状态（可选，None 表示所有状态）
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            (任务列表, 总数)
        """
        try:
            if status is not None:
                # 从状态集合获取
                status_key = self._get_task_status_key(agent_id, status)
                task_ids = list(self.redis_client.smembers(status_key))
            else:
                # 获取所有任务（通过扫描）
                pattern = f"{self.task_prefix}:task:*"
                task_ids = []
                for key in self.redis_client.scan_iter(match=pattern):
                    task_data = self.redis_client.get(key)
                    if task_data:
                        task_dict = json.loads(task_data)
                        if task_dict.get("agent_id") == agent_id:
                            task_ids.append(task_dict.get("task_id"))
            
            # 分页
            total = len(task_ids)
            task_ids = task_ids[offset:offset + limit]
            
            # 获取任务详情
            tasks = []
            for task_id in task_ids:
                task_dict = self.get_task_by_id(task_id, agent_id)
                if task_dict:
                    tasks.append(task_dict)
            
            return tasks, total
        except Exception as e:
            logger.error(f"Failed to list tasks for agent {agent_id}: {e}")
            return [], 0
    
    def queue_exists(self, agent_id: str) -> bool:
        """
        检查队列是否存在
        
        Args:
            agent_id: Agent ID
        
        Returns:
            队列是否存在
        """
        try:
            # 检查队列键是否存在
            queue_key = self._get_queue_key(agent_id)
            if self.redis_client.exists(queue_key):
                return True
            
            # 如果队列键不存在，检查状态集合是否存在
            for status in [PENDING, PROCESSING, COMPLETED, FAILED]:
                status_key = self._get_task_status_key(agent_id, status)
                if self.redis_client.exists(status_key):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to check queue existence for agent {agent_id}: {e}")
            return False
    
    def create_queue(self, agent_id: str) -> bool:
        """
        创建 agent 私有任务队列（如果不存在）
        
        此方法保证创建私有化任务队列的过程一致：
        1. 先检查队列是否存在
        2. 如果存在，直接返回成功（幂等性保证）
        3. 如果不存在，初始化队列结构后返回成功
        
        这样可以避免重复创建队列，提高系统的健壮性和幂等性。
        
        Args:
            agent_id: Agent ID
        
        Returns:
            是否成功（如果队列已存在也返回 True）
        """
        try:
            # 步骤1：先检查队列是否存在
            if self.queue_exists(agent_id):
                logger.info(f"Queue for agent {agent_id} already exists, skipping creation")
                return True
            
            # 步骤2：队列不存在，初始化队列结构
            # 初始化状态集合（为每个状态创建空集合）
            for status in [PENDING, PROCESSING, COMPLETED, FAILED]:
                status_key = self._get_task_status_key(agent_id, status)
                # 创建空集合（如果不存在）
                # 使用 placeholder 技巧确保集合被创建
                self.redis_client.sadd(status_key, "placeholder")
                self.redis_client.srem(status_key, "placeholder")
            
            # 初始化队列键（优先级队列使用 Sorted Set）
            # 队列会在第一次添加任务时自动创建，这里只是确保键存在
            queue_key = self._get_queue_key(agent_id)
            self.redis_client.exists(queue_key)
            
            logger.info(f"Queue created for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create queue for agent {agent_id}: {e}", exc_info=True)
            return False
    
    def get_queue_info(self, agent_id: str) -> Dict[str, Any]:
        """
        获取队列信息（根据 agentID 路由）
        
        Args:
            agent_id: Agent ID
        
        Returns:
            队列信息字典，包含各状态的任务数量
        """
        try:
            info = {
                "agent_id": agent_id,
                "pending_count": 0,
                "processing_count": 0,
                "completed_count": 0,
                "failed_count": 0,
                "total_count": 0,
            }
            
            # 统计各状态的任务数量
            status_map = {
                PENDING: "pending_count",
                PROCESSING: "processing_count",
                COMPLETED: "completed_count",
                FAILED: "failed_count",
            }
            
            for status, key in status_map.items():
                status_key = self._get_task_status_key(agent_id, status)
                count = self.redis_client.scard(status_key)
                info[key] = count
                info["total_count"] += count
            
            return info
        except Exception as e:
            logger.error(f"Failed to get queue info for agent {agent_id}: {e}")
            return {
                "agent_id": agent_id,
                "pending_count": 0,
                "processing_count": 0,
                "completed_count": 0,
                "failed_count": 0,
                "total_count": 0,
            }
    
    def _update_task_status_internal(self, task_dict: Dict[str, Any], status: int):
        """内部方法：更新任务状态（不更新 Redis）"""
        old_status = task_dict.get("status", PENDING)
        task_dict["status"] = status
        task_dict["updated_at"] = int(time.time())
        
        # 更新状态集合
        agent_id = task_dict["agent_id"]
        task_id = task_dict["task_id"]
        old_status_key = self._get_task_status_key(agent_id, old_status)
        new_status_key = self._get_task_status_key(agent_id, status)
        self.redis_client.srem(old_status_key, task_id)
        self.redis_client.sadd(new_status_key, task_id)
    
    def delete_task(self, task_id: str, agent_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            agent_id: Agent ID
        
        Returns:
            是否成功
        """
        try:
            task_dict = self.get_task_by_id(task_id, agent_id)
            if not task_dict:
                return False
            
            status = task_dict.get("status", PENDING)
            
            # 从状态集合中删除
            status_key = self._get_task_status_key(agent_id, status)
            self.redis_client.srem(status_key, task_id)
            
            # 从优先级队列中删除（如果还在队列中，使用Sorted Set的zrem）
            queue_key = self._get_queue_key(agent_id)
            self.redis_client.zrem(queue_key, task_id)
            
            # 删除任务详情
            task_key = self._get_task_key(task_id)
            self.redis_client.delete(task_key)
            
            logger.info(f"Task {task_id} deleted for agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def clear_queue(self, agent_id: str, status: Optional[int] = None) -> int:
        """
        清空队列（删除所有任务，但保留队列结构）
        
        Args:
            agent_id: Agent ID
            status: 任务状态（可选，None 表示清空所有状态）
        
        Returns:
            清空的任务数量
        """
        try:
            if status is not None:
                # 清空指定状态的任务
                status_key = self._get_task_status_key(agent_id, status)
                task_ids = list(self.redis_client.smembers(status_key))
                for task_id in task_ids:
                    self.delete_task(task_id, agent_id)
                return len(task_ids)
            else:
                # 清空所有状态的任务
                total = 0
                for status in [PENDING, PROCESSING, COMPLETED, FAILED]:
                    status_key = self._get_task_status_key(agent_id, status)
                    task_ids = list(self.redis_client.smembers(status_key))
                    for task_id in task_ids:
                        if self.delete_task(task_id, agent_id):
                            total += 1
                return total
        except Exception as e:
            logger.error(f"Failed to clear queue for agent {agent_id}: {e}")
            return 0
    
    def delete_queue(self, agent_id: str) -> int:
        """
        删除队列（完全删除队列，包括所有任务和队列结构）
        
        Args:
            agent_id: Agent ID
        
        Returns:
            删除的任务数量
        """
        try:
            # 先清空所有任务
            deleted_count = self.clear_queue(agent_id)
            
            # 删除队列键（列表）
            queue_key = self._get_queue_key(agent_id)
            self.redis_client.delete(queue_key)
            
            # 删除所有状态集合键
            for status in [PENDING, PROCESSING, COMPLETED, FAILED]:
                status_key = self._get_task_status_key(agent_id, status)
                self.redis_client.delete(status_key)
            
            logger.info(f"Queue deleted for agent {agent_id}, {deleted_count} tasks removed")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to delete queue for agent {agent_id}: {e}")
            return 0


# 全局队列管理器实例
queue_manager = QueueManager()
