"""Agent 队列实时报表客户端 - 提供多个 agent 的实时队列信息和状态监控"""
import time
import threading
import logging
from typing import List, Optional, Callable, Dict, Any
from queue import Queue, Empty
from agent_queues.agent_queue import PrivateAgentTasksQueue
from agent_queues.settings import ClientSettings
# 导入默认配置实例（从 __init__.py 导出）
try:
    from agent_queues import settings as default_settings
    # 确保是 ClientSettings 实例，而不是模块
    if not isinstance(default_settings, ClientSettings):
        default_settings = ClientSettings()
except (ImportError, AttributeError):
    default_settings = ClientSettings()

logger = logging.getLogger(__name__)


class AgentQueueReport:
    """Agent 队列报表数据类"""
    
    def __init__(self, agent_id: str, data: Dict[str, Any]):
        self.agent_id = agent_id
        self.timestamp = data.get("timestamp", 0)
        self.queue_exists = data.get("queue_exists", False)
        self.pending_count = data.get("pending_count", 0)
        self.processing_count = data.get("processing_count", 0)
        self.completed_count = data.get("completed_count", 0)
        self.failed_count = data.get("failed_count", 0)
        self.total_count = data.get("total_count", 0)
        self.success_rate = data.get("success_rate", 0)
        self.completion_rate = data.get("completion_rate", 0)
        self.health = data.get("health", "UNKNOWN")
        self.health_message = data.get("health_message", "")
        self.recent_tasks = data.get("recent_tasks", [])
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "queue_exists": self.queue_exists,
            "pending_count": self.pending_count,
            "processing_count": self.processing_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "total_count": self.total_count,
            "success_rate": self.success_rate,
            "completion_rate": self.completion_rate,
            "health": self.health,
            "health_message": self.health_message,
            "recent_tasks": self.recent_tasks
        }


class QueueReport:
    """队列报表数据类（包含多个 Agent）"""
    
    def __init__(self, data: Dict[str, Any]):
        self.timestamp = data.get("timestamp", 0)
        self.agent_reports = [
            AgentQueueReport(report["agent_id"], report)
            for report in data.get("agent_reports", [])
        ]
        self.total_agents = data.get("total_agents", 0)
        self.active_agents = data.get("active_agents", 0)
        self.total_pending = data.get("total_pending", 0)
        self.total_processing = data.get("total_processing", 0)
        self.total_completed = data.get("total_completed", 0)
        self.total_failed = data.get("total_failed", 0)
        self.total_tasks = data.get("total_tasks", 0)
        self.global_success_rate = data.get("global_success_rate", 0)
        self.global_completion_rate = data.get("global_completion_rate", 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "agent_reports": [report.to_dict() for report in self.agent_reports],
            "total_agents": self.total_agents,
            "active_agents": self.active_agents,
            "total_pending": self.total_pending,
            "total_processing": self.total_processing,
            "total_completed": self.total_completed,
            "total_failed": self.total_failed,
            "total_tasks": self.total_tasks,
            "global_success_rate": self.global_success_rate,
            "global_completion_rate": self.global_completion_rate
        }
    
    def get_agent_report(self, agent_id: str) -> Optional[AgentQueueReport]:
        """获取指定 Agent 的报表"""
        for report in self.agent_reports:
            if report.agent_id == agent_id:
                return report
        return None


class AgentQueueReportClient:
    """
    Agent 队列实时报表客户端
    
    提供多个 agent 的实时私有化任务队列信息和状态监控，支持流式协议实时展示。
    
    使用示例:
        # 创建报表客户端
        report_client = AgentQueueReportClient()
        
        # 监控指定 agent
        def on_report(report: QueueReport):
            print(f"报表时间: {report.timestamp}")
            for agent_report in report.agent_reports:
                print(f"Agent {agent_report.agent_id}: "
                      f"待处理={agent_report.pending_count}, "
                      f"处理中={agent_report.processing_count}, "
                      f"已完成={agent_report.completed_count}, "
                      f"失败={agent_report.failed_count}")
        
        # 开始监控
        report_client.start_monitoring(
            agent_ids=["agent_001", "agent_002"],
            update_interval=5,
            callback=on_report
        )
        
        # 运行一段时间后停止
        time.sleep(60)
        report_client.stop_monitoring()
    """
    
    def __init__(
        self,
        queue_client: Optional[PrivateAgentTasksQueue] = None,
        config_path: Optional[str] = None,
        base_settings: Optional[ClientSettings] = None,
        **queue_client_kwargs
    ):
        """
        初始化报表客户端
        
        Args:
            queue_client: 队列客户端实例（可选，如果不提供则创建新的）
            config_path: 配置文件路径（可选）
            base_settings: 基础配置实例（可选）
            **queue_client_kwargs: 队列客户端配置参数
        """
        if queue_client is None:
            self.queue_client = PrivateAgentTasksQueue(
                config_path=config_path,
                base_settings=base_settings,
                **queue_client_kwargs
            )
            self._own_client = True
        else:
            self.queue_client = queue_client
            self._own_client = False
        
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._update_interval = 5  # 默认5秒
        self._agent_ids: List[str] = []
        self._callback: Optional[Callable[[QueueReport], None]] = None
        self._include_task_details = False
        self._stop_event = threading.Event()
    
    def get_single_agent_report(self, agent_id: str, include_task_details: bool = False) -> Optional[AgentQueueReport]:
        """
        获取单个 Agent 的队列报表
        
        Args:
            agent_id: Agent ID
            include_task_details: 是否包含任务详情
        
        Returns:
            AgentQueueReport 对象，如果队列不存在则返回 None
        """
        try:
            # 检查队列是否存在
            exists_response = self.queue_client.queue_exists(agent_id)
            if not exists_response.exists:
                return None
            
            # 获取队列信息
            info_response = self.queue_client.get_queue_info(agent_id)
            if not info_response.success:
                return None
            
            # 计算完成情况
            completed = info_response.completed_count
            failed = info_response.failed_count
            total_finished = completed + failed
            total = info_response.total_count
            
            success_rate = 0
            if total_finished > 0:
                success_rate = int((completed / total_finished) * 100)
            
            completion_rate = 0
            if total > 0:
                completion_rate = int((total_finished / total) * 100)
            
            # 判断健康状态
            health = "HEALTHY"
            health_message = "队列运行正常"
            
            if failed > 0:
                failure_rate = (failed / total_finished) * 100 if total_finished > 0 else 0
                if failure_rate > 50:
                    health = "CRITICAL"
                    health_message = f"失败率过高: {failure_rate:.1f}%"
                elif failure_rate > 20:
                    health = "WARNING"
                    health_message = f"失败率较高: {failure_rate:.1f}%"
            
            if info_response.pending_count > 1000:
                if health == "HEALTHY":
                    health = "WARNING"
                health_message = f"队列积压严重: {info_response.pending_count} 个待处理任务"
            
            # 获取最近的任务（如果需要）
            recent_tasks = []
            if include_task_details:
                try:
                    list_response = self.queue_client.list_tasks(
                        agent_id=agent_id,
                        status=0,  # 所有状态
                        limit=10,
                        offset=0
                    )
                    if list_response.success:
                        recent_tasks = [
                            {
                                "task_id": task.task_id,
                                "status": task.status,
                                "priority": task.priority,
                                "created_at": task.created_at,
                                "updated_at": task.updated_at
                            }
                            for task in list_response.tasks[:10]
                        ]
                except Exception as e:
                    logger.warning(f"Failed to get recent tasks for {agent_id}: {e}")
            
            report_data = {
                "agent_id": agent_id,
                "timestamp": int(time.time() * 1000),
                "queue_exists": True,
                "pending_count": info_response.pending_count,
                "processing_count": info_response.processing_count,
                "completed_count": info_response.completed_count,
                "failed_count": info_response.failed_count,
                "total_count": info_response.total_count,
                "success_rate": success_rate,
                "completion_rate": completion_rate,
                "health": health,
                "health_message": health_message,
                "recent_tasks": recent_tasks
            }
            
            return AgentQueueReport(agent_id, report_data)
            
        except Exception as e:
            logger.error(f"Failed to get report for agent {agent_id}: {e}")
            return None
    
    def get_multi_agent_report(
        self,
        agent_ids: List[str],
        include_task_details: bool = False
    ) -> QueueReport:
        """
        获取多个 Agent 的队列报表
        
        Args:
            agent_ids: Agent ID 列表（空列表表示获取所有已知的 agent）
            include_task_details: 是否包含任务详情
        
        Returns:
            QueueReport 对象
        """
        # 如果 agent_ids 为空，尝试获取所有 agent（需要服务端支持）
        # 目前实现：如果为空，返回空报表
        if not agent_ids:
            return QueueReport({
                "timestamp": int(time.time() * 1000),
                "agent_reports": [],
                "total_agents": 0,
                "active_agents": 0,
                "total_pending": 0,
                "total_processing": 0,
                "total_completed": 0,
                "total_failed": 0,
                "total_tasks": 0,
                "global_success_rate": 0,
                "global_completion_rate": 0
            })
        
        # 获取每个 agent 的报表
        agent_reports = []
        total_pending = 0
        total_processing = 0
        total_completed = 0
        total_failed = 0
        total_tasks = 0
        total_finished = 0
        
        for agent_id in agent_ids:
            report = self.get_single_agent_report(agent_id, include_task_details)
            if report:
                agent_reports.append(report)
                total_pending += report.pending_count
                total_processing += report.processing_count
                total_completed += report.completed_count
                total_failed += report.failed_count
                total_tasks += report.total_count
                total_finished += (report.completed_count + report.failed_count)
        
        # 计算全局统计
        active_agents = len([r for r in agent_reports if r.total_count > 0])
        
        global_success_rate = 0
        if total_finished > 0:
            global_success_rate = int((total_completed / total_finished) * 100)
        
        global_completion_rate = 0
        if total_tasks > 0:
            global_completion_rate = int((total_finished / total_tasks) * 100)
        
        report_data = {
            "timestamp": int(time.time() * 1000),
            "agent_reports": [r.to_dict() for r in agent_reports],
            "total_agents": len(agent_ids),
            "active_agents": active_agents,
            "total_pending": total_pending,
            "total_processing": total_processing,
            "total_completed": total_completed,
            "total_failed": total_failed,
            "total_tasks": total_tasks,
            "global_success_rate": global_success_rate,
            "global_completion_rate": global_completion_rate
        }
        
        return QueueReport(report_data)
    
    def start_monitoring(
        self,
        agent_ids: List[str],
        update_interval: int = 5,
        callback: Optional[Callable[[QueueReport], None]] = None,
        include_task_details: bool = False
    ):
        """
        开始实时监控多个 Agent 的队列信息
        
        Args:
            agent_ids: Agent ID 列表
            update_interval: 更新间隔（秒，最小1秒，最大60秒）
            callback: 回调函数，每次更新时调用，参数为 QueueReport 对象
            include_task_details: 是否包含任务详情
        """
        if self._monitoring:
            logger.warning("Monitoring is already running")
            return
        
        if update_interval < 1:
            update_interval = 1
        elif update_interval > 60:
            update_interval = 60
        
        self._agent_ids = agent_ids
        self._update_interval = update_interval
        self._callback = callback
        self._include_task_details = include_task_details
        self._monitoring = True
        self._stop_event.clear()
        
        # 启动监控线程
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"Started monitoring {len(agent_ids)} agents with {update_interval}s interval")
    
    def stop_monitoring(self):
        """停止实时监控"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        
        logger.info("Stopped monitoring")
    
    def _monitor_loop(self):
        """监控循环（在独立线程中运行）"""
        while self._monitoring and not self._stop_event.is_set():
            try:
                # 获取报表
                report = self.get_multi_agent_report(
                    self._agent_ids,
                    self._include_task_details
                )
                
                # 调用回调函数
                if self._callback:
                    try:
                        self._callback(report)
                    except Exception as e:
                        logger.error(f"Error in callback function: {e}")
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            # 等待下一次更新
            self._stop_event.wait(self._update_interval)
    
    def stream_reports(
        self,
        agent_ids: List[str],
        update_interval: int = 5,
        include_task_details: bool = False
    ):
        """
        流式获取报表（使用 gRPC 流式接口）
        
        Args:
            agent_ids: Agent ID 列表
            update_interval: 更新间隔（秒，最小1秒，最大60秒）
            include_task_details: 是否包含任务详情
        
        Yields:
            QueueReport 对象
        """
        try:
            from agent_queues import StreamQueueReportsRequest
            
            # 限制更新间隔范围
            update_interval = max(1, min(60, update_interval))
            
            # 创建流式请求
            request = StreamQueueReportsRequest(
                agent_ids=agent_ids,
                update_interval_seconds=update_interval,
                include_task_details=include_task_details
            )
            
            # 调用流式接口
            for proto_report in self.queue_client.stub.StreamQueueReports(request):
                # 转换为 QueueReport 对象
                agent_reports = []
                for proto_agent_report in proto_report.agent_reports:
                    agent_report_data = {
                        "agent_id": proto_agent_report.agent_id,
                        "timestamp": proto_agent_report.timestamp,
                        "queue_exists": proto_agent_report.queue_exists,
                        "pending_count": proto_agent_report.pending_count,
                        "processing_count": proto_agent_report.processing_count,
                        "completed_count": proto_agent_report.completed_count,
                        "failed_count": proto_agent_report.failed_count,
                        "total_count": proto_agent_report.total_count,
                        "success_rate": proto_agent_report.success_rate,
                        "completion_rate": proto_agent_report.completion_rate,
                        "health": proto_agent_report.health,
                        "health_message": proto_agent_report.health_message,
                        "recent_tasks": [
                            {
                                "task_id": task.task_id,
                                "status": task.status,
                                "priority": task.priority,
                                "created_at": task.created_at,
                                "updated_at": task.updated_at
                            }
                            for task in proto_agent_report.recent_tasks
                        ]
                    }
                    agent_reports.append(AgentQueueReport(proto_agent_report.agent_id, agent_report_data))
                
                report_data = {
                    "timestamp": proto_report.timestamp,
                    "agent_reports": [r.to_dict() for r in agent_reports],
                    "total_agents": proto_report.total_agents,
                    "active_agents": proto_report.active_agents,
                    "total_pending": proto_report.total_pending,
                    "total_processing": proto_report.total_processing,
                    "total_completed": proto_report.total_completed,
                    "total_failed": proto_report.total_failed,
                    "total_tasks": proto_report.total_tasks,
                    "global_success_rate": proto_report.global_success_rate,
                    "global_completion_rate": proto_report.global_completion_rate
                }
                
                yield QueueReport(report_data)
                
        except Exception as e:
            logger.error(f"Error in stream reports: {e}")
            raise
    
    def close(self):
        """关闭客户端"""
        self.stop_monitoring()
        if self._own_client:
            self.queue_client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 便捷函数
def create_report_client(
    agent_ids: Optional[List[str]] = None,
    update_interval: int = 5,
    **queue_client_kwargs
) -> AgentQueueReportClient:
    """
    创建报表客户端并开始监控
    
    Args:
        agent_ids: Agent ID 列表
        update_interval: 更新间隔（秒）
        **queue_client_kwargs: 队列客户端配置参数
    
    Returns:
        AgentQueueReportClient 实例
    """
    client = AgentQueueReportClient(**queue_client_kwargs)
    if agent_ids:
        client.start_monitoring(agent_ids, update_interval)
    return client

