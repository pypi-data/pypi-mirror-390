"""任务处理器"""
import logging
from typing import Any, Dict, Tuple
from server.celery.app import celery_app
from server.redis.queue_manager import queue_manager

# 从 proto 导入状态枚举值
try:
    from agent_queues import queue_service_pb2
    PROCESSING = queue_service_pb2.PROCESSING
    COMPLETED = queue_service_pb2.COMPLETED
    FAILED = queue_service_pb2.FAILED
except ImportError:
    # 如果 proto 未生成，使用默认值
    PROCESSING = 1
    COMPLETED = 2
    FAILED = 3

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="tasks.process_task")
def process_task(self, task_id: str, agent_id: str):
    """处理任务的 Celery 任务"""
    try:
        # 获取任务
        task_dict = queue_manager.get_task_by_id(task_id, agent_id)
        if not task_dict:
            logger.error(f"Task {task_id} not found")
            return {"success": False, "error": "Task not found"}
        
        # 更新状态为处理中
        queue_manager.update_task_status(task_id, agent_id, PROCESSING)
        
        # 这里可以根据 task_type 调用不同的处理函数
        # 目前只是一个示例
        logger.info(f"Processing task {task_id} of type {task_dict.get('task_type')}")
        
        # 模拟任务处理
        result = {
            "task_id": task_id,
            "processed": True,
            "payload": task_dict.get("payload")
        }
        
        # 更新状态为已完成
        queue_manager.update_task_status(
            task_id,
            agent_id,
            COMPLETED,
            result=result
        )
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Failed to process task {task_id}: {e}")
        # 更新状态为失败
        queue_manager.update_task_status(
            task_id,
            agent_id,
            FAILED,
            error_message=str(e)
        )
        return {"success": False, "error": str(e)}


def submit_task_async(task_dict: Dict[str, Any]) -> Tuple[str, bool]:
    """
    异步提交任务到队列并自动触发 Celery 处理（支持幂等性检查）
    
    此函数将任务提交到队列，并自动触发 Celery Worker 处理任务。
    如果任务已存在（通过 client_request_id 检查），则不会重复处理。
    
    Args:
        task_dict: 任务字典，必须包含 agent_id
        
    Returns:
        (task_id, is_new_task)
        - task_id: 任务ID（新任务或已存在任务的ID）
        - is_new_task: 是否是新任务（True=新任务，False=已存在的任务）
        
    Raises:
        Exception: 如果提交失败
    """
    success, task_id, is_new_task = queue_manager.submit_task(task_dict)
    if not success:
        raise Exception("Failed to submit task")
    
    agent_id = task_dict.get("agent_id")
    if not agent_id:
        raise Exception("agent_id is required")
    
    # 只有新任务才触发 Celery 处理
    # 如果是已存在的任务（幂等性），不需要重复处理
    if is_new_task:
        # 自动触发 Celery 处理
        try:
            process_task.delay(task_id, agent_id)
            logger.info(f"Task {task_id} submitted and Celery task triggered for agent {agent_id}")
        except Exception as e:
            # 如果 Celery 不可用，记录警告但不影响任务提交
            logger.warning(f"Failed to trigger Celery task for {task_id}: {e}. Task is still in queue.")
    
    return task_id, is_new_task
