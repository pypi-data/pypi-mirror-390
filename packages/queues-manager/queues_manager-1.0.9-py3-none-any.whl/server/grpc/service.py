"""gRPC 服务实现"""
import json
import logging
from typing import Optional
import grpc
from concurrent import futures

# 注意：需要先运行 python -m grpc_tools.protoc 生成 Python 代码
# 这里假设生成的代码在 interface 目录下
try:
    from agent_queues import queue_service_pb2, queue_service_pb2_grpc
except ImportError:
    # 如果还没有生成，先创建一个占位符
    logging.warning("gRPC generated code not found. Please run: python scripts/generate_grpc.py")
    queue_service_pb2 = None
    queue_service_pb2_grpc = None

from server.settings import settings
from server.redis.queue_manager import queue_manager

# 尝试导入 Celery 处理函数（如果可用）
try:
    from server.celery.handlers import submit_task_async
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    submit_task_async = None
    logging.warning("Celery handlers not available. Tasks will not be auto-processed.")

logger = logging.getLogger(__name__)


class QueueServiceServicer(queue_service_pb2_grpc.QueueServiceServicer if queue_service_pb2_grpc else object):
    """队列服务实现"""
    
    @classmethod
    def _get_type_enum_to_str(cls):
        """获取任务类型枚举到字符串的映射"""
        if queue_service_pb2 is None:
            return {}
        return {
            queue_service_pb2.UNKNOWN: "unknown",
            queue_service_pb2.DATA_PROCESSING: "data_processing",
            queue_service_pb2.IMAGE_PROCESSING: "image_processing",
            queue_service_pb2.TEXT_ANALYSIS: "text_analysis",
            queue_service_pb2.MODEL_INFERENCE: "model_inference",
            queue_service_pb2.DATA_EXTRACTION: "data_extraction",
            queue_service_pb2.FILE_UPLOAD: "file_upload",
            queue_service_pb2.FILE_DOWNLOAD: "file_download",
            queue_service_pb2.API_CALL: "api_call",
            queue_service_pb2.DATABASE_QUERY: "database_query",
        }
    
    @classmethod
    def _get_type_str_to_enum(cls):
        """获取任务类型字符串到枚举的映射"""
        if queue_service_pb2 is None:
            return {}
        return {
            "unknown": queue_service_pb2.UNKNOWN,
            "data_processing": queue_service_pb2.DATA_PROCESSING,
            "image_processing": queue_service_pb2.IMAGE_PROCESSING,
            "text_analysis": queue_service_pb2.TEXT_ANALYSIS,
            "model_inference": queue_service_pb2.MODEL_INFERENCE,
            "data_extraction": queue_service_pb2.DATA_EXTRACTION,
            "file_upload": queue_service_pb2.FILE_UPLOAD,
            "file_download": queue_service_pb2.FILE_DOWNLOAD,
            "api_call": queue_service_pb2.API_CALL,
            "database_query": queue_service_pb2.DATABASE_QUERY,
        }
    
    @classmethod
    def _enum_to_type_str(cls, type_enum: int) -> str:
        """将任务类型枚举转换为字符串"""
        return cls._get_type_enum_to_str().get(type_enum, "unknown")
    
    @classmethod
    def _type_str_to_enum(cls, type_str: str) -> int:
        """将任务类型字符串转换为枚举"""
        if queue_service_pb2 is None:
            return 99
        return cls._get_type_str_to_enum().get(type_str, queue_service_pb2.CUSTOM)
    
    def _task_dict_to_proto(self, task_dict: dict) -> queue_service_pb2.Task:
        """将任务字典转换为 proto 消息"""
        # 处理 payload
        payload = task_dict.get("payload", {})
        payload_str = json.dumps(payload) if isinstance(payload, dict) else str(payload)
        
        # 处理 result
        result = task_dict.get("result")
        result_str = json.dumps(result) if result and isinstance(result, dict) else (result or "")
        
        # 处理任务类型
        # 如果字典中有 type 字段（枚举值），直接使用；否则根据 task_type 字符串推断
        task_type_enum = task_dict.get("type")
        if task_type_enum is None:
            # 根据 task_type 字符串推断枚举值
            task_type_str = task_dict.get("task_type", "unknown")
            task_type_enum = self._type_str_to_enum(task_type_str)
        else:
            task_type_str = task_dict.get("task_type", self._enum_to_type_str(task_type_enum))
        
        return queue_service_pb2.Task(
            task_id=task_dict.get("task_id", ""),
            agent_id=task_dict.get("agent_id", ""),
            type=task_type_enum,
            task_type=task_type_str,
            payload=payload_str,
            status=task_dict.get("status", queue_service_pb2.PENDING),
            created_at=task_dict.get("created_at", 0),
            updated_at=task_dict.get("updated_at", 0),
            result=result_str,
            error_message=task_dict.get("error_message") or "",
            client_request_id=task_dict.get("client_request_id") or "",
            priority=task_dict.get("priority", 5),  # 默认优先级为5
        )
    
    
    def UpdateTaskStatus(
        self,
        request: queue_service_pb2.UpdateTaskStatusRequest,
        context
    ) -> queue_service_pb2.UpdateTaskStatusResponse:
        """更新任务状态"""
        try:
            # 解析 result
            result = None
            if request.result:
                try:
                    result = json.loads(request.result)
                except json.JSONDecodeError:
                    result = {"raw": request.result}
            
            success = queue_manager.update_task_status(
                request.task_id,
                request.agent_id,
                request.status,  # 直接使用 proto 的状态值（整数）
                result=result,
                error_message=request.error_message if request.error_message else None
            )
            
            if success:
                return queue_service_pb2.UpdateTaskStatusResponse(
                    success=True,
                    message="Task status updated successfully"
                )
            else:
                return queue_service_pb2.UpdateTaskStatusResponse(
                    success=False,
                    message="Task not found or update failed"
                )
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.UpdateTaskStatusResponse(
                success=False,
                message=f"Failed to update task status: {str(e)}"
            )
    
    def QueryTask(self, request: queue_service_pb2.QueryTaskRequest, context) -> queue_service_pb2.QueryTaskResponse:
        """查询任务"""
        try:
            task_dict = queue_manager.get_task_by_id(request.task_id, request.agent_id)
            
            if not task_dict:
                return queue_service_pb2.QueryTaskResponse(
                    success=False,
                    task=queue_service_pb2.Task(),
                    message="Task not found"
                )
            
            return queue_service_pb2.QueryTaskResponse(
                success=True,
                task=self._task_dict_to_proto(task_dict),
                message="Task found"
            )
        except Exception as e:
            logger.error(f"Failed to query task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.QueryTaskResponse(
                success=False,
                task=queue_service_pb2.Task(),
                message=f"Failed to query task: {str(e)}"
            )
    
    def CreateQueue(self, request: queue_service_pb2.CreateQueueRequest, context) -> queue_service_pb2.CreateQueueResponse:
        """
        创建 agent 私有任务队列（如果不存在）
        
        此方法保证创建私有化任务队列的过程一致：
        1. 先检查队列是否存在
        2. 如果存在，直接返回成功（already_exists=True）
        3. 如果不存在，创建新队列后返回成功（already_exists=False）
        
        这样可以避免重复创建队列，提高系统的健壮性和幂等性。
        """
        try:
            # 步骤1：先检查队列是否存在
            queue_exists = queue_manager.queue_exists(request.agent_id)
            
            if queue_exists:
                # 步骤2：队列已存在，直接返回成功
                logger.info(f"Queue for agent {request.agent_id} already exists, returning success")
                return queue_service_pb2.CreateQueueResponse(
                    success=True,
                    agent_id=request.agent_id,
                    message=f"Queue for agent {request.agent_id} already exists",
                    already_exists=True
                )
            
            # 步骤3：队列不存在，创建新队列
            # queue_manager.create_queue() 内部也会先检查再创建，保证幂等性
            success = queue_manager.create_queue(request.agent_id)
            
            if success:
                logger.info(f"Queue created for agent {request.agent_id}")
                return queue_service_pb2.CreateQueueResponse(
                    success=True,
                    agent_id=request.agent_id,
                    message=f"Queue created for agent {request.agent_id}",
                    already_exists=False
                )
            else:
                logger.error(f"Failed to create queue for agent {request.agent_id}")
                return queue_service_pb2.CreateQueueResponse(
                    success=False,
                    agent_id=request.agent_id,
                    message=f"Failed to create queue for agent {request.agent_id}",
                    already_exists=False
                )
        except Exception as e:
            logger.error(f"Failed to create queue for agent {request.agent_id}: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.CreateQueueResponse(
                success=False,
                agent_id=request.agent_id,
                message=f"Failed to create queue: {str(e)}",
                already_exists=False
            )
    
    def GetQueueInfo(self, request: queue_service_pb2.GetQueueInfoRequest, context) -> queue_service_pb2.GetQueueInfoResponse:
        """
        获取队列信息（根据 agentID 路由）
        
        根据 agentID 路由找到对应的私有化任务队列，返回队列统计信息。
        """
        try:
            info = queue_manager.get_queue_info(request.agent_id)
            
            return queue_service_pb2.GetQueueInfoResponse(
                success=True,
                agent_id=info["agent_id"],
                pending_count=info.get("pending_count", 0),
                processing_count=info.get("processing_count", 0),
                completed_count=info.get("completed_count", 0),
                failed_count=info.get("failed_count", 0),
                total_count=info.get("total_count", 0),
                message="Queue info retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Failed to get queue info: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.GetQueueInfoResponse(
                success=False,
                agent_id=request.agent_id,
                pending_count=0,
                processing_count=0,
                completed_count=0,
                failed_count=0,
                total_count=0,
                message=f"Failed to get queue info: {str(e)}"
            )
    
    def SubmitTask(self, request: queue_service_pb2.SubmitTaskRequest, context) -> queue_service_pb2.SubmitTaskResponse:
        """
        提交任务到某个 agent 的私有化任务队列（根据 agentID 路由）
        
        根据 agentID 路由找到对应的私有化任务队列，然后添加任务。
        """
        try:
            # 确保队列存在（如果不存在则创建）
            queue_manager.create_queue(request.agent_id)
            
            # 解析 payload
            try:
                payload = json.loads(request.payload) if request.payload else {}
            except json.JSONDecodeError:
                payload = {"raw": request.payload}
            
            # 创建任务字典
            # 处理任务类型：如果 type 是 CUSTOM，使用 task_type 字符串；否则使用枚举值
            if request.type == queue_service_pb2.CUSTOM:
                task_type_str = request.task_type if request.task_type else "custom"
            else:
                task_type_str = self._enum_to_type_str(request.type)
            
            task_dict = {
                "agent_id": request.agent_id,
                "type": request.type,  # 保存枚举值
                "task_type": task_type_str,  # 保存字符串类型
                "payload": payload,
                "status": queue_service_pb2.PENDING,
                "priority": request.priority if request.priority > 0 else 5,  # 默认优先级为5
            }
            
            # 如果提供了 client_request_id，添加到任务字典（用于幂等性）
            if request.client_request_id:
                task_dict["client_request_id"] = request.client_request_id
            
            # 提交任务（如果 Celery 可用，会自动触发处理）
            if CELERY_AVAILABLE:
                task_id, is_new_task = submit_task_async(task_dict)
            else:
                # 回退到直接提交（不触发 Celery）
                success, task_id, is_new_task = queue_manager.submit_task(task_dict)
                if not success:
                    raise Exception("Failed to submit task")
            
            # 构建响应消息
            if is_new_task:
                message = "Task submitted successfully" + (" and queued for processing" if CELERY_AVAILABLE else "")
            else:
                message = f"Task already exists (idempotency check passed), task_id: {task_id}"
            
            return queue_service_pb2.SubmitTaskResponse(
                success=True,
                task_id=task_id,
                message=message
            )
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.SubmitTaskResponse(
                success=False,
                task_id="",
                message=f"Failed to submit task: {str(e)}"
            )
    
    def GetTask(self, request: queue_service_pb2.GetTaskRequest, context) -> queue_service_pb2.GetTaskResponse:
        """
        从某个 agent 的私有化任务队列获取任务（根据 agentID 路由，主动拉取）
        
        根据 agentID 路由找到对应的私有化任务队列，然后从队列中获取任务。
        """
        try:
            task_dict = queue_manager.get_task(request.agent_id, timeout=request.timeout)
            
            if not task_dict:
                return queue_service_pb2.GetTaskResponse(
                    success=False,
                    task=queue_service_pb2.Task(),
                    message="No task available"
                )
            
            return queue_service_pb2.GetTaskResponse(
                success=True,
                task=self._task_dict_to_proto(task_dict),
                message="Task retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Failed to get task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.GetTaskResponse(
                success=False,
                task=queue_service_pb2.Task(),
                message=f"Failed to get task: {str(e)}"
            )
    
    def ListTasks(self, request: queue_service_pb2.ListTasksRequest, context) -> queue_service_pb2.ListTasksResponse:
        """
        列出某个 agent 的私有化任务队列中的所有任务（根据 agentID 路由）
        
        根据 agentID 路由找到对应的私有化任务队列，然后列出队列中的任务。
        """
        try:
            status = None
            if request.status != 0:  # 0 表示所有状态
                status = request.status  # 直接使用 proto 的状态值（整数）
            
            tasks, total = queue_manager.list_tasks(
                request.agent_id,
                status=status,
                limit=request.limit if request.limit > 0 else 100,
                offset=request.offset
            )
            
            proto_tasks = [self._task_dict_to_proto(task_dict) for task_dict in tasks]
            
            return queue_service_pb2.ListTasksResponse(
                success=True,
                tasks=proto_tasks,
                total=total,
                message=f"Found {total} tasks"
            )
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.ListTasksResponse(
                success=False,
                tasks=[],
                total=0,
                message=f"Failed to list tasks: {str(e)}"
            )
    
    def GetTasksByStatus(self, request: queue_service_pb2.GetTasksByStatusRequest, context) -> queue_service_pb2.GetTasksByStatusResponse:
        """
        获取某个状态的任务（根据 agentID 和状态路由）
        
        根据 agentID 和任务状态获取任务列表。
        """
        try:
            # 验证状态参数（0 表示 PENDING，是有效状态）
            # 只检查是否为有效的状态值（0=PENDING, 1=PROCESSING, 2=COMPLETED, 3=FAILED）
            valid_statuses = [
                queue_service_pb2.PENDING,
                queue_service_pb2.PROCESSING,
                queue_service_pb2.COMPLETED,
                queue_service_pb2.FAILED
            ]
            if request.status not in valid_statuses:
                return queue_service_pb2.GetTasksByStatusResponse(
                    success=False,
                    tasks=[],
                    total=0,
                    status=request.status,
                    message=f"Invalid status: {request.status}. Valid statuses are: PENDING(0), PROCESSING(1), COMPLETED(2), FAILED(3)."
                )
            
            tasks, total = queue_manager.list_tasks(
                request.agent_id,
                status=request.status,
                limit=request.limit if request.limit > 0 else 100,
                offset=request.offset
            )
            
            proto_tasks = [self._task_dict_to_proto(task_dict) for task_dict in tasks]
            
            return queue_service_pb2.GetTasksByStatusResponse(
                success=True,
                tasks=proto_tasks,
                total=total,
                status=request.status,
                message=f"Found {total} tasks with status {request.status}"
            )
        except Exception as e:
            logger.error(f"Failed to get tasks by status: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.GetTasksByStatusResponse(
                success=False,
                tasks=[],
                total=0,
                status=request.status,
                message=f"Failed to get tasks by status: {str(e)}"
            )
    
    def QueueExists(self, request: queue_service_pb2.QueueExistsRequest, context) -> queue_service_pb2.QueueExistsResponse:
        """检查队列是否存在（根据 agentID 路由）"""
        try:
            # 使用 queue_manager 的 queue_exists 方法检查
            queue_exists = queue_manager.queue_exists(request.agent_id)
            
            return queue_service_pb2.QueueExistsResponse(
                exists=queue_exists,
                message="Queue exists" if queue_exists else "Queue does not exist"
            )
        except Exception as e:
            logger.error(f"Failed to check queue existence: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.QueueExistsResponse(
                exists=False,
                message=f"Failed to check queue existence: {str(e)}"
            )
    
    def ClearQueue(self, request: queue_service_pb2.ClearQueueRequest, context) -> queue_service_pb2.ClearQueueResponse:
        """清空队列（根据 agentID 路由，可选按状态清空）"""
        try:
            # 检查确认标志
            if not request.confirm:
                return queue_service_pb2.ClearQueueResponse(
                    success=False,
                    cleared_count=0,
                    message="Clear operation requires confirm=true"
                )
            
            status = None
            if request.status != 0:  # 0 表示清空所有状态
                status = request.status
            
            cleared_count = queue_manager.clear_queue(request.agent_id, status=status)
            
            return queue_service_pb2.ClearQueueResponse(
                success=True,
                cleared_count=cleared_count,
                message=f"Cleared {cleared_count} tasks"
            )
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.ClearQueueResponse(
                success=False,
                cleared_count=0,
                message=f"Failed to clear queue: {str(e)}"
            )
    
    def DeleteQueue(self, request: queue_service_pb2.DeleteQueueRequest, context) -> queue_service_pb2.DeleteQueueResponse:
        """删除队列（根据 agentID 路由，完全删除队列包括所有任务和队列本身）"""
        try:
            # 检查确认标志
            if not request.confirm:
                return queue_service_pb2.DeleteQueueResponse(
                    success=False,
                    deleted_count=0,
                    message="Delete operation requires confirm=true"
                )
            
            deleted_count = queue_manager.delete_queue(request.agent_id)
            
            return queue_service_pb2.DeleteQueueResponse(
                success=True,
                deleted_count=deleted_count,
                message=f"Deleted queue with {deleted_count} tasks"
            )
        except Exception as e:
            logger.error(f"Failed to delete queue: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.DeleteQueueResponse(
                success=False,
                deleted_count=0,
                message=f"Failed to delete queue: {str(e)}"
            )
    
    def BatchSubmitTasks(self, request: queue_service_pb2.BatchSubmitTasksRequest, context) -> queue_service_pb2.BatchSubmitTasksResponse:
        """批量提交任务到某个 agent 的私有化任务队列（根据 agentID 路由）"""
        try:
            # 确保队列存在
            queue_manager.create_queue(request.agent_id)
            
            task_ids = []
            failed_count = 0
            results = []  # 每个任务的详细结果
            
            for index, task_item in enumerate(request.tasks):
                try:
                    # 解析 payload
                    try:
                        payload = json.loads(task_item.payload) if task_item.payload else {}
                    except json.JSONDecodeError:
                        payload = {"raw": task_item.payload}
                    
                    # 处理任务类型
                    if task_item.type == queue_service_pb2.CUSTOM:
                        task_type_str = task_item.task_type if task_item.task_type else "custom"
                    else:
                        task_type_str = self._enum_to_type_str(task_item.type)
                    
                    task_dict = {
                        "agent_id": request.agent_id,
                        "type": task_item.type,
                        "task_type": task_type_str,
                        "payload": payload,
                        "status": queue_service_pb2.PENDING,
                        "priority": task_item.priority if task_item.priority > 0 else 5,  # 默认优先级为5
                    }
                    
                    # 如果指定了 task_id，使用它
                    if task_item.task_id:
                        task_dict["task_id"] = task_item.task_id
                    
                    # 如果提供了 client_request_id，添加到任务字典（用于幂等性）
                    if task_item.client_request_id:
                        task_dict["client_request_id"] = task_item.client_request_id
                    
                    # 提交任务（如果 Celery 可用，会自动触发处理）
                    try:
                        if CELERY_AVAILABLE:
                            task_id, is_new_task = submit_task_async(task_dict)
                            task_ids.append(task_id)
                            results.append(queue_service_pb2.BatchSubmitTaskResult(
                                index=index,
                                task_id=task_id,
                                success=True
                            ))
                        else:
                            # 回退到直接提交（不触发 Celery）
                            success, task_id, is_new_task = queue_manager.submit_task(task_dict)
                            if success:
                                task_ids.append(task_id)
                                results.append(queue_service_pb2.BatchSubmitTaskResult(
                                    index=index,
                                    task_id=task_id,
                                    success=True
                                ))
                            else:
                                failed_count += 1
                                results.append(queue_service_pb2.BatchSubmitTaskResult(
                                    index=index,
                                    task_id="",
                                    success=False,
                                    error=queue_service_pb2.ErrorDetail(
                                        code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                                        message="Failed to submit task"
                                    )
                                ))
                    except Exception as e:
                        logger.error(f"Failed to submit task in batch: {e}")
                        failed_count += 1
                        results.append(queue_service_pb2.BatchSubmitTaskResult(
                            index=index,
                            task_id="",
                            success=False,
                            error=queue_service_pb2.ErrorDetail(
                                code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                                message=str(e)
                            )
                        ))
                except Exception as e:
                    logger.error(f"Failed to submit task in batch: {e}")
                    failed_count += 1
                    results.append(queue_service_pb2.BatchSubmitTaskResult(
                        index=index,
                        task_id="",
                        success=False,
                        error=queue_service_pb2.ErrorDetail(
                            code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                            message=str(e)
                        )
                    ))
            
            return queue_service_pb2.BatchSubmitTasksResponse(
                success=len(task_ids) > 0,
                task_ids=task_ids,
                success_count=len(task_ids),
                failed_count=failed_count,
                results=results,
                message=f"Submitted {len(task_ids)} tasks, {failed_count} failed"
            )
        except Exception as e:
            logger.error(f"Failed to batch submit tasks: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            # 创建失败结果列表
            failed_results = [
                queue_service_pb2.BatchSubmitTaskResult(
                    index=i,
                    task_id="",
                    success=False,
                    error=queue_service_pb2.ErrorDetail(
                        code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                        message=str(e)
                    )
                )
                for i in range(len(request.tasks))
            ]
            return queue_service_pb2.BatchSubmitTasksResponse(
                success=False,
                task_ids=[],
                success_count=0,
                failed_count=len(request.tasks),
                results=failed_results,
                message=f"Failed to batch submit tasks: {str(e)}"
            )
    
    def DeleteTask(self, request: queue_service_pb2.DeleteTaskRequest, context) -> queue_service_pb2.DeleteTaskResponse:
        """删除任务（根据 agentID 和 taskID）"""
        try:
            success = queue_manager.delete_task(request.task_id, request.agent_id)
            
            return queue_service_pb2.DeleteTaskResponse(
                success=success,
                message="Task deleted successfully" if success else "Task not found or delete failed"
            )
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.DeleteTaskResponse(
                success=False,
                message=f"Failed to delete task: {str(e)}"
            )
    
    def BatchDeleteTasks(self, request: queue_service_pb2.BatchDeleteTasksRequest, context) -> queue_service_pb2.BatchDeleteTasksResponse:
        """批量删除任务（根据 agentID 和 taskID 列表）"""
        try:
            deleted_count = 0
            failed_count = 0
            results = []  # 每个任务的删除结果
            
            # 如果指定了状态，先过滤任务
            if request.status != 0:  # 0 表示不限制状态
                # 获取指定状态的所有任务
                tasks, _ = queue_manager.list_tasks(request.agent_id, status=request.status, limit=10000, offset=0)
                task_ids_to_delete = {task["task_id"] for task in tasks}
                # 只删除在请求列表中的任务
                task_ids_to_delete = task_ids_to_delete.intersection(set(request.task_ids))
            else:
                task_ids_to_delete = set(request.task_ids)
            
            # 删除任务并记录每个任务的结果
            for task_id in request.task_ids:
                # 检查是否在要删除的列表中
                if task_id not in task_ids_to_delete:
                    # 任务不在要删除的列表中（可能因为状态不匹配）
                    results.append(queue_service_pb2.BatchDeleteTaskResult(
                        task_id=task_id,
                        success=False,
                        error=queue_service_pb2.ErrorDetail(
                            code=queue_service_pb2.ERROR_TASK_NOT_FOUND,
                            message="Task not found or status does not match"
                        )
                    ))
                    failed_count += 1
                    continue
                
                try:
                    if queue_manager.delete_task(task_id, request.agent_id):
                        deleted_count += 1
                        results.append(queue_service_pb2.BatchDeleteTaskResult(
                            task_id=task_id,
                            success=True
                        ))
                    else:
                        failed_count += 1
                        results.append(queue_service_pb2.BatchDeleteTaskResult(
                            task_id=task_id,
                            success=False,
                            error=queue_service_pb2.ErrorDetail(
                                code=queue_service_pb2.ERROR_TASK_NOT_FOUND,
                                message="Task not found or delete failed"
                            )
                        ))
                except Exception as e:
                    logger.error(f"Failed to delete task {task_id}: {e}")
                    failed_count += 1
                    results.append(queue_service_pb2.BatchDeleteTaskResult(
                        task_id=task_id,
                        success=False,
                        error=queue_service_pb2.ErrorDetail(
                            code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                            message=str(e)
                        )
                    ))
            
            return queue_service_pb2.BatchDeleteTasksResponse(
                success=deleted_count > 0,
                deleted_count=deleted_count,
                failed_count=failed_count,
                results=results,
                message=f"Deleted {deleted_count} tasks, {failed_count} failed"
            )
        except Exception as e:
            logger.error(f"Failed to batch delete tasks: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            # 创建失败结果列表
            failed_results = [
                queue_service_pb2.BatchDeleteTaskResult(
                    task_id=task_id,
                    success=False,
                    error=queue_service_pb2.ErrorDetail(
                        code=queue_service_pb2.ERROR_INTERNAL_ERROR,
                        message=str(e)
                    )
                )
                for task_id in request.task_ids
            ]
            return queue_service_pb2.BatchDeleteTasksResponse(
                success=False,
                deleted_count=0,
                failed_count=len(request.task_ids),
                results=failed_results,
                message=f"Failed to batch delete tasks: {str(e)}"
            )
    
    def CancelTask(self, request: queue_service_pb2.CancelTaskRequest, context) -> queue_service_pb2.CancelTaskResponse:
        """取消任务（根据 agentID 和 taskID）"""
        try:
            # 获取任务
            task_dict = queue_manager.get_task_by_id(request.task_id, request.agent_id)
            if not task_dict:
                return queue_service_pb2.CancelTaskResponse(
                    success=False,
                    message="Task not found"
                )
            
            # 只有 PENDING 或 PROCESSING 状态的任务可以取消
            current_status = task_dict.get("status", queue_service_pb2.PENDING)
            if current_status not in [queue_service_pb2.PENDING, queue_service_pb2.PROCESSING]:
                return queue_service_pb2.CancelTaskResponse(
                    success=False,
                    message=f"Cannot cancel task with status {current_status}"
                )
            
            # 更新任务状态为 FAILED，并记录取消原因
            error_message = request.reason if request.reason else "Task cancelled"
            success = queue_manager.update_task_status(
                request.task_id,
                request.agent_id,
                queue_service_pb2.FAILED,
                error_message=error_message
            )
            
            return queue_service_pb2.CancelTaskResponse(
                success=success,
                message="Task cancelled successfully" if success else "Failed to cancel task"
            )
        except Exception as e:
            logger.error(f"Failed to cancel task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.CancelTaskResponse(
                success=False,
                message=f"Failed to cancel task: {str(e)}"
            )
    
    def RetryTask(self, request: queue_service_pb2.RetryTaskRequest, context) -> queue_service_pb2.RetryTaskResponse:
        """重试任务（根据 agentID 和 taskID，将失败任务重新提交）"""
        try:
            # 获取原任务
            task_dict = queue_manager.get_task_by_id(request.task_id, request.agent_id)
            if not task_dict:
                return queue_service_pb2.RetryTaskResponse(
                    success=False,
                    new_task_id="",
                    message="Task not found"
                )
            
            # 只有 FAILED 状态的任务可以重试
            if task_dict.get("status") != queue_service_pb2.FAILED:
                return queue_service_pb2.RetryTaskResponse(
                    success=False,
                    new_task_id="",
                    message="Only failed tasks can be retried"
                )
            
            # 创建新任务（使用原任务的配置，但重置状态）
            new_task_dict = {
                "agent_id": task_dict["agent_id"],
                "type": task_dict.get("type", queue_service_pb2.UNKNOWN),
                "task_type": task_dict.get("task_type", "unknown"),
                "payload": task_dict.get("payload", {}),
                "status": queue_service_pb2.PENDING,
                "priority": task_dict.get("priority", 5),  # 保持原任务的优先级
            }
            
            # 如果提供了 client_request_id，使用它
            if request.client_request_id:
                new_task_dict["client_request_id"] = request.client_request_id
            
            # 提交新任务（如果 Celery 可用，会自动触发处理）
            if CELERY_AVAILABLE:
                new_task_id, is_new_task = submit_task_async(new_task_dict)
            else:
                # 回退到直接提交（不触发 Celery）
                success, new_task_id, is_new_task = queue_manager.submit_task(new_task_dict)
                if not success:
                    return queue_service_pb2.RetryTaskResponse(
                        success=False,
                        new_task_id="",
                        message="Failed to submit retry task"
                    )
            
            return queue_service_pb2.RetryTaskResponse(
                success=True,
                new_task_id=new_task_id,
                message=f"Task retried successfully, new task ID: {new_task_id}" + (" and queued for processing" if CELERY_AVAILABLE else "")
            )
        except Exception as e:
            logger.error(f"Failed to retry task: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.RetryTaskResponse(
                success=False,
                new_task_id="",
                message=f"Failed to retry task: {str(e)}"
            )
    
    def HealthCheck(self, request: queue_service_pb2.HealthCheckRequest, context) -> queue_service_pb2.HealthCheckResponse:
        """健康检查"""
        import time
        try:
            # 检查 Redis 连接
            queue_manager.redis_client.ping()
            redis_ok = True
            redis_status = "connected"
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            redis_ok = False
            redis_status = f"error: {str(e)}"
        
        # 返回健康状态
        if redis_ok:
            return queue_service_pb2.HealthCheckResponse(
                status=queue_service_pb2.HealthCheckResponse.SERVING,
                version="0.1.1",
                timestamp=int(time.time() * 1000),
                details={"redis": redis_status}
            )
        else:
            return queue_service_pb2.HealthCheckResponse(
                status=queue_service_pb2.HealthCheckResponse.NOT_SERVING,
                version="0.1.1",
                timestamp=int(time.time() * 1000),
                details={"redis": redis_status}
            )
    
    def GetTaskStats(self, request: queue_service_pb2.GetTaskStatsRequest, context) -> queue_service_pb2.GetTaskStatsResponse:
        """获取任务统计信息（根据 agentID 路由）"""
        try:
            info = queue_manager.get_queue_info(request.agent_id)
            
            # 如果指定了状态，只返回该状态的统计
            if request.status != 0:  # 0 表示所有状态
                status_map = {
                    queue_service_pb2.PENDING: "pending_count",
                    queue_service_pb2.PROCESSING: "processing_count",
                    queue_service_pb2.COMPLETED: "completed_count",
                    queue_service_pb2.FAILED: "failed_count",
                }
                status_key = status_map.get(request.status, "total_count")
                total_count = info.get(status_key, 0)
                
                return queue_service_pb2.GetTaskStatsResponse(
                    success=True,
                    total_count=total_count,
                    pending_count=info["pending_count"] if request.status == queue_service_pb2.PENDING else 0,
                    processing_count=info["processing_count"] if request.status == queue_service_pb2.PROCESSING else 0,
                    completed_count=info["completed_count"] if request.status == queue_service_pb2.COMPLETED else 0,
                    failed_count=info["failed_count"] if request.status == queue_service_pb2.FAILED else 0,
                    message="Task stats retrieved successfully"
                )
            else:
                # 返回所有状态的统计
                return queue_service_pb2.GetTaskStatsResponse(
                    success=True,
                    total_count=info["total_count"],
                    pending_count=info["pending_count"],
                    processing_count=info["processing_count"],
                    completed_count=info["completed_count"],
                    failed_count=info["failed_count"],
                    message="Task stats retrieved successfully"
                )
        except Exception as e:
            logger.error(f"Failed to get task stats: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return queue_service_pb2.GetTaskStatsResponse(
                success=False,
                total_count=0,
                pending_count=0,
                processing_count=0,
                completed_count=0,
                failed_count=0,
                message=f"Failed to get task stats: {str(e)}"
            )
    
    def StreamQueueReports(self, request: queue_service_pb2.StreamQueueReportsRequest, context):
        """
        实时监控多个 agent 的队列信息（流式返回）
        
        通过流式协议实时返回多个 agent 的队列报表信息，包括任务数量、完成情况、多状态展示等。
        """
        import time as time_module
        
        try:
            agent_ids = list(request.agent_ids) if request.agent_ids else []
            update_interval = max(1, min(60, request.update_interval_seconds or 5))
            include_task_details = request.include_task_details
            
            # 如果没有指定 agent_ids，需要获取所有 agent（这里简化处理，实际可能需要从 Redis 获取）
            # 目前如果为空，则不返回任何数据
            if not agent_ids:
                logger.warning("No agent_ids specified in StreamQueueReports request")
                return
            
            logger.info(f"Starting stream reports for {len(agent_ids)} agents, interval={update_interval}s")
            
            while context.is_active():
                try:
                    # 获取每个 agent 的报表
                    agent_reports = []
                    total_pending = 0
                    total_processing = 0
                    total_completed = 0
                    total_failed = 0
                    total_tasks = 0
                    total_finished = 0
                    
                    for agent_id in agent_ids:
                        try:
                            # 检查队列是否存在
                            exists_response = self.QueueExists(
                                queue_service_pb2.QueueExistsRequest(agent_id=agent_id),
                                context
                            )
                            
                            if not exists_response.exists:
                                # 队列不存在，创建空的报表
                                agent_report = queue_service_pb2.AgentQueueReport(
                                    agent_id=agent_id,
                                    timestamp=int(time_module.time() * 1000),
                                    queue_exists=False,
                                    health=queue_service_pb2.AgentQueueReport.UNKNOWN,
                                    health_message="Queue does not exist"
                                )
                                agent_reports.append(agent_report)
                                continue
                            
                            # 获取队列信息
                            info_response = self.GetQueueInfo(
                                queue_service_pb2.GetQueueInfoRequest(agent_id=agent_id),
                                context
                            )
                            
                            if not info_response.success:
                                continue
                            
                            # 计算完成情况
                            completed = info_response.completed_count
                            failed = info_response.failed_count
                            pending = info_response.pending_count
                            processing = info_response.processing_count
                            total = info_response.total_count
                            
                            total_finished_item = completed + failed
                            total_finished += total_finished_item
                            total_pending += pending
                            total_processing += processing
                            total_completed += completed
                            total_failed += failed
                            total_tasks += total
                            
                            # 计算成功率
                            success_rate = 0
                            if total_finished_item > 0:
                                success_rate = int((completed / total_finished_item) * 100)
                            
                            # 计算完成率
                            completion_rate = 0
                            if total > 0:
                                completion_rate = int((total_finished_item / total) * 100)
                            
                            # 判断健康状态
                            health = queue_service_pb2.AgentQueueReport.HEALTHY
                            health_message = "队列运行正常"
                            
                            if failed > 0:
                                failure_rate = (failed / total_finished_item) * 100 if total_finished_item > 0 else 0
                                if failure_rate > 50:
                                    health = queue_service_pb2.AgentQueueReport.CRITICAL
                                    health_message = f"失败率过高: {failure_rate:.1f}%"
                                elif failure_rate > 20:
                                    health = queue_service_pb2.AgentQueueReport.WARNING
                                    health_message = f"失败率较高: {failure_rate:.1f}%"
                            
                            if pending > 1000:
                                if health == queue_service_pb2.AgentQueueReport.HEALTHY:
                                    health = queue_service_pb2.AgentQueueReport.WARNING
                                health_message = f"队列积压严重: {pending} 个待处理任务"
                            
                            # 获取最近的任务（如果需要）
                            recent_tasks = []
                            if include_task_details:
                                try:
                                    list_response = self.ListTasks(
                                        queue_service_pb2.ListTasksRequest(
                                            agent_id=agent_id,
                                            status=0,
                                            limit=10,
                                            offset=0
                                        ),
                                        context
                                    )
                                    if list_response.success:
                                        recent_tasks = list_response.tasks[:10]
                                except Exception as e:
                                    logger.warning(f"Failed to get recent tasks for {agent_id}: {e}")
                            
                            # 创建 Agent 报表
                            agent_report = queue_service_pb2.AgentQueueReport(
                                agent_id=agent_id,
                                timestamp=int(time_module.time() * 1000),
                                queue_exists=True,
                                pending_count=pending,
                                processing_count=processing,
                                completed_count=completed,
                                failed_count=failed,
                                total_count=total,
                                success_rate=success_rate,
                                completion_rate=completion_rate,
                                health=health,
                                health_message=health_message,
                                recent_tasks=recent_tasks
                            )
                            agent_reports.append(agent_report)
                            
                        except Exception as e:
                            logger.error(f"Failed to get report for agent {agent_id}: {e}")
                            # 创建错误报表
                            agent_report = queue_service_pb2.AgentQueueReport(
                                agent_id=agent_id,
                                timestamp=int(time_module.time() * 1000),
                                queue_exists=False,
                                health=queue_service_pb2.AgentQueueReport.UNKNOWN,
                                health_message=f"Error: {str(e)}"
                            )
                            agent_reports.append(agent_report)
                    
                    # 计算全局统计
                    active_agents = len([r for r in agent_reports if r.total_count > 0])
                    
                    global_success_rate = 0
                    if total_finished > 0:
                        global_success_rate = int((total_completed / total_finished) * 100)
                    
                    global_completion_rate = 0
                    if total_tasks > 0:
                        global_completion_rate = int((total_finished / total_tasks) * 100)
                    
                    # 创建队列报表
                    report = queue_service_pb2.QueueReport(
                        timestamp=int(time_module.time() * 1000),
                        agent_reports=agent_reports,
                        total_agents=len(agent_ids),
                        active_agents=active_agents,
                        total_pending=total_pending,
                        total_processing=total_processing,
                        total_completed=total_completed,
                        total_failed=total_failed,
                        total_tasks=total_tasks,
                        global_success_rate=global_success_rate,
                        global_completion_rate=global_completion_rate
                    )
                    
                    # 发送报表
                    yield report
                    
                    # 等待下一次更新
                    time_module.sleep(update_interval)
                    
                except Exception as e:
                    logger.error(f"Error in stream reports loop: {e}")
                    # 发送错误报表
                    error_report = queue_service_pb2.QueueReport(
                        timestamp=int(time_module.time() * 1000),
                        agent_reports=[],
                        total_agents=0,
                        active_agents=0,
                        message=f"Error: {str(e)}"
                    )
                    yield error_report
                    time_module.sleep(update_interval)
                    
        except Exception as e:
            logger.error(f"Failed to stream queue reports: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))


def serve():
    """启动 gRPC 服务器"""
    if queue_service_pb2_grpc is None:
        logger.error("gRPC generated code not found. Please generate it first.")
        return
    
    # 构建服务器选项
    server_options = []
    
    # 消息大小限制
    server_options.append(('grpc.max_receive_message_length', settings.GRPC_MAX_RECEIVE_MESSAGE_LENGTH))
    server_options.append(('grpc.max_send_message_length', settings.GRPC_MAX_SEND_MESSAGE_LENGTH))
    
    # 并发流限制
    if settings.GRPC_MAX_CONCURRENT_STREAMS is not None:
        server_options.append(('grpc.max_concurrent_streams', settings.GRPC_MAX_CONCURRENT_STREAMS))
    
    # Keepalive 配置
    server_options.append(('grpc.keepalive_time_ms', settings.GRPC_KEEPALIVE_TIME * 1000))
    server_options.append(('grpc.keepalive_timeout_ms', settings.GRPC_KEEPALIVE_TIMEOUT * 1000))
    server_options.append(('grpc.keepalive_permit_without_calls', settings.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS))
    server_options.append(('grpc.http2.max_pings_without_data', settings.GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA))
    server_options.append(('grpc.http2.min_time_between_pings_ms', settings.GRPC_HTTP2_MIN_TIME_BETWEEN_PINGS_MS))
    server_options.append(('grpc.http2.min_ping_interval_without_data_ms', settings.GRPC_HTTP2_MIN_PING_INTERVAL_WITHOUT_DATA_MS))
    
    # 连接超时
    server_options.append(('grpc.so_reuseport', 1 if settings.GRPC_SO_REUSEPORT else 0))
    
    # 接收/发送缓冲区
    if settings.GRPC_SO_RCVBUF is not None:
        server_options.append(('grpc.so_rcvbuf', settings.GRPC_SO_RCVBUF))
    if settings.GRPC_SO_SNDBUF is not None:
        server_options.append(('grpc.so_sndbuf', settings.GRPC_SO_SNDBUF))
    
    # 并发 RPC 限制
    if settings.GRPC_MAX_CONCURRENT_RPCS_PER_CONNECTION is not None:
        server_options.append(('grpc.max_concurrent_rpcs_per_connection', settings.GRPC_MAX_CONCURRENT_RPCS_PER_CONNECTION))
    
    # 创建线程池执行器
    executor = futures.ThreadPoolExecutor(
        max_workers=settings.GRPC_MAX_WORKERS,
        thread_name_prefix=settings.GRPC_THREAD_POOL_PREFIX
    )
    
    # 创建 gRPC 服务器
    server = grpc.server(executor, options=server_options)
    
    # 添加服务
    queue_service_pb2_grpc.add_QueueServiceServicer_to_server(
        QueueServiceServicer(), server
    )
    
    # 添加健康检查服务（如果启用）
    if settings.GRPC_ENABLE_HEALTH_CHECK:
        try:
            from grpc_health.v1 import health_pb2_grpc, health
            health_servicer = health.HealthServicer()
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
            # 设置服务状态为 SERVING
            health_servicer.set("queue_service", health_pb2_grpc.HealthCheckResponse.SERVING)
            logger.info("Health check service enabled")
        except ImportError:
            logger.warning("grpc-health-checking not installed, health check service disabled")
    
    # 添加反射服务（如果启用，用于调试）
    if settings.GRPC_ENABLE_REFLECTION:
        try:
            from grpc_reflection.v1alpha import reflection
            SERVICE_NAMES = (
                queue_service_pb2.DESCRIPTOR.services_by_name['QueueService'].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, server)
            logger.info("gRPC reflection service enabled")
        except ImportError:
            logger.warning("grpcio-reflection not installed, reflection service disabled")
    
    # 监听地址
    listen_addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    
    # 添加端口（支持 TLS 或非 TLS）
    if settings.GRPC_USE_TLS:
        if not settings.GRPC_TLS_CERT_FILE or not settings.GRPC_TLS_KEY_FILE:
            logger.error("TLS enabled but certificate or key file not configured")
            return
        
        # 读取证书和私钥
        with open(settings.GRPC_TLS_CERT_FILE, 'rb') as f:
            certificate_chain = f.read()
        with open(settings.GRPC_TLS_KEY_FILE, 'rb') as f:
            private_key = f.read()
        
        # 创建服务器凭证
        server_credentials = grpc.ssl_server_credentials(
            [(private_key, certificate_chain)],
            root_certificates=None,
            require_client_auth=settings.GRPC_TLS_CLIENT_AUTH
        )
        
        # 如果启用客户端认证，加载 CA 证书
        if settings.GRPC_TLS_CLIENT_AUTH and settings.GRPC_TLS_CA_CERTS:
            with open(settings.GRPC_TLS_CA_CERTS, 'rb') as f:
                root_certificates = f.read()
            server_credentials = grpc.ssl_server_credentials(
                [(private_key, certificate_chain)],
                root_certificates=root_certificates,
                require_client_auth=True
            )
        
        server.add_secure_port(listen_addr, server_credentials)
        logger.info(f"gRPC server (TLS) started on {listen_addr}")
    else:
        server.add_insecure_port(listen_addr)
        logger.info(f"gRPC server started on {listen_addr}")
    
    # 启动服务器
    server.start()
    
    logger.info(f"Server options: max_workers={settings.GRPC_MAX_WORKERS}, "
                f"max_receive_message_length={settings.GRPC_MAX_RECEIVE_MESSAGE_LENGTH}, "
                f"keepalive_time={settings.GRPC_KEEPALIVE_TIME}s")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
    finally:
        # 优雅关闭
        logger.info("Stopping gRPC server...")
        server.stop(grace=5)  # 给 5 秒时间完成正在处理的请求
        executor.shutdown(wait=True)
        logger.info("gRPC server stopped")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 确保可以找到项目根目录
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    serve()

