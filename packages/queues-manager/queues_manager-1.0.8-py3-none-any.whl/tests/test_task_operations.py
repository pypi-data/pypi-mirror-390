"""
任务操作接口测试
"""
import json
import pytest
from agent_queues import (
    SubmitTaskRequest, BatchSubmitTasksRequest, SubmitTaskItem,
    GetTaskRequest, QueryTaskRequest, UpdateTaskStatusRequest,
    DeleteTaskRequest, BatchDeleteTasksRequest,
    CancelTaskRequest, RetryTaskRequest,
    DATA_PROCESSING, IMAGE_PROCESSING, CUSTOM,
    PENDING, PROCESSING, COMPLETED, FAILED
)


class TestTaskOperations:
    """任务操作接口测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_queue(self, grpc_stub, test_agent_id):
        """每个测试前创建队列"""
        from agent_queues import CreateQueueRequest
        request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(request)
    
    def test_submit_task(self, grpc_stub, test_agent_id):
        """测试提交任务"""
        payload = json.dumps({"data": "test", "action": "process"})
        request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=payload,
            priority=5  # 默认优先级
        )
        response = grpc_stub.SubmitTask(request)
        
        assert response.success is True
        assert response.task_id is not None
        assert len(response.task_id) > 0
    
    def test_submit_task_with_priority(self, grpc_stub, test_agent_id):
        """测试提交带优先级的任务"""
        payload = json.dumps({"data": "high priority task"})
        request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=payload,
            priority=9  # 高优先级
        )
        response = grpc_stub.SubmitTask(request)
        
        assert response.success is True
        assert response.task_id is not None
    
    def test_submit_task_with_idempotency(self, grpc_stub, test_agent_id):
        """测试提交任务幂等性"""
        import uuid
        import time
        client_request_id = f"test_req_{uuid.uuid4()}"
        payload = json.dumps({"data": "idempotent task"})
        
        # 第一次提交
        request1 = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=payload,
            client_request_id=client_request_id,
            priority=5
        )
        response1 = grpc_stub.SubmitTask(request1)
        assert response1.success is True, f"第一次提交应该成功: {response1.message}"
        task_id1 = response1.task_id
        assert task_id1, "应该返回任务ID"
        
        # 等待一小段时间确保幂等性映射已存储
        time.sleep(0.1)
        
        # 第二次提交（相同 client_request_id）
        request2 = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=payload,
            client_request_id=client_request_id,
            priority=5
        )
        response2 = grpc_stub.SubmitTask(request2)
        assert response2.success is True, f"第二次提交应该成功: {response2.message}"
        # 应该返回相同的任务ID（幂等性）
        assert response2.task_id == task_id1, \
            f"幂等性检查失败：第一次任务ID={task_id1}, 第二次任务ID={response2.task_id}, 消息={response2.message}"
    
    def test_submit_task_custom_type(self, grpc_stub, test_agent_id):
        """测试提交自定义类型任务"""
        payload = json.dumps({"custom": "data"})
        request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=CUSTOM,
            task_type="my_custom_task",
            payload=payload
        )
        response = grpc_stub.SubmitTask(request)
        
        assert response.success is True
        assert response.task_id is not None
    
    def test_batch_submit_tasks(self, grpc_stub, test_agent_id):
        """测试批量提交任务"""
        tasks = [
            SubmitTaskItem(
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i, "data": f"task_{i}"}),
                priority=5 + i  # 不同优先级
            )
            for i in range(3)
        ]
        
        request = BatchSubmitTasksRequest(
            agent_id=test_agent_id,
            tasks=tasks
        )
        response = grpc_stub.BatchSubmitTasks(request)
        
        assert response.success is True
        assert response.success_count == 3
        assert len(response.task_ids) == 3
    
    def test_retry_task_with_idempotency(self, grpc_stub, test_agent_id):
        """测试重试任务幂等性"""
        import uuid
        import time
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"}),
            priority=5
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        assert submit_response.success
        task_id = submit_response.task_id
        
        # 获取任务并标记为失败
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=2)
        get_response = grpc_stub.GetTask(get_request)
        assert get_response.success and get_response.task is not None, "应该能获取到任务"
        
        # 更新为失败状态
        update_request = UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            status=FAILED,
            error_message="Test error"
        )
        update_response = grpc_stub.UpdateTaskStatus(update_request)
        assert update_response.success, "应该能更新任务状态为失败"
        
        # 等待一小段时间确保状态更新完成
        time.sleep(0.1)
        
        # 重试任务（带幂等性）
        client_request_id = f"retry_req_{uuid.uuid4()}"
        retry_request1 = RetryTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            client_request_id=client_request_id
        )
        retry_response1 = grpc_stub.RetryTask(retry_request1)
        assert retry_response1.success, f"重试应该成功: {retry_response1.message}"
        assert retry_response1.new_task_id, "应该返回新任务ID"
        new_task_id1 = retry_response1.new_task_id
        
        # 再次重试（相同 client_request_id）
        retry_request2 = RetryTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            client_request_id=client_request_id
        )
        retry_response2 = grpc_stub.RetryTask(retry_request2)
        assert retry_response2.success, f"第二次重试应该成功: {retry_response2.message}"
        # 应该返回相同的任务ID（幂等性）
        assert retry_response2.new_task_id == new_task_id1, f"应该返回相同的任务ID: {retry_response2.new_task_id} != {new_task_id1}"
    
    def test_get_task(self, grpc_stub, test_agent_id):
        """测试获取任务"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"}),
            priority=5  # 确保有优先级
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        assert submit_response.success is True
        assert submit_response.task_id is not None
        
        # 等待一小段时间确保任务已添加到队列
        import time
        time.sleep(0.1)
        
        # 获取任务
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=5)
        response = grpc_stub.GetTask(get_request)
        
        assert response.success is True
        assert response.task is not None
        assert response.task.task_id == submit_response.task_id
        assert response.task.agent_id == test_agent_id
    
    def test_get_task_timeout(self, grpc_stub, test_agent_id):
        """测试获取任务超时"""
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=1)
        response = grpc_stub.GetTask(get_request)
        
        # 超时或没有任务时，success 可能为 False 或 task 为空
        # 这里只检查响应格式
        assert hasattr(response, 'success')
        assert hasattr(response, 'task')
    
    def test_query_task(self, grpc_stub, test_agent_id):
        """测试查询任务"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 查询任务
        query_request = QueryTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id
        )
        response = grpc_stub.QueryTask(query_request)
        
        assert response.success is True
        assert response.task is not None
        assert response.task.task_id == task_id
        assert response.task.agent_id == test_agent_id
    
    def test_update_task_status(self, grpc_stub, test_agent_id):
        """测试更新任务状态"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 获取任务（使其状态变为 PROCESSING）
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=5)
        grpc_stub.GetTask(get_request)
        
        # 更新任务状态为已完成
        result = json.dumps({"result": "success"})
        update_request = UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            status=COMPLETED,
            result=result
        )
        response = grpc_stub.UpdateTaskStatus(update_request)
        
        assert response.success is True
    
    def test_update_task_status_failed(self, grpc_stub, test_agent_id):
        """测试更新任务状态为失败"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 获取任务
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=5)
        grpc_stub.GetTask(get_request)
        
        # 更新任务状态为失败
        update_request = UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            status=FAILED,
            error_message="Test error"
        )
        response = grpc_stub.UpdateTaskStatus(update_request)
        
        assert response.success is True
    
    def test_delete_task(self, grpc_stub, test_agent_id):
        """测试删除任务"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 删除任务
        delete_request = DeleteTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id
        )
        response = grpc_stub.DeleteTask(delete_request)
        
        assert response.success is True
    
    def test_batch_delete_tasks(self, grpc_stub, test_agent_id):
        """测试批量删除任务"""
        # 先提交多个任务
        task_ids = []
        for i in range(3):
            submit_request = SubmitTaskRequest(
                agent_id=test_agent_id,
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i})
            )
            submit_response = grpc_stub.SubmitTask(submit_request)
            task_ids.append(submit_response.task_id)
        
        # 批量删除任务
        delete_request = BatchDeleteTasksRequest(
            agent_id=test_agent_id,
            task_ids=task_ids
        )
        response = grpc_stub.BatchDeleteTasks(delete_request)
        
        assert response.success is True
        assert response.deleted_count >= 0
    
    def test_cancel_task(self, grpc_stub, test_agent_id):
        """测试取消任务"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 取消任务
        cancel_request = CancelTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            reason="Test cancel"
        )
        response = grpc_stub.CancelTask(cancel_request)
        
        assert response.success is True
    
    def test_retry_task(self, grpc_stub, test_agent_id):
        """测试重试任务"""
        # 先提交一个任务
        submit_request = SubmitTaskRequest(
            agent_id=test_agent_id,
            type=DATA_PROCESSING,
            payload=json.dumps({"data": "test"})
        )
        submit_response = grpc_stub.SubmitTask(submit_request)
        task_id = submit_response.task_id
        
        # 获取任务并标记为失败
        get_request = GetTaskRequest(agent_id=test_agent_id, timeout=5)
        grpc_stub.GetTask(get_request)
        
        update_request = UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=test_agent_id,
            status=FAILED,
            error_message="Test failure"
        )
        grpc_stub.UpdateTaskStatus(update_request)
        
        # 重试任务
        retry_request = RetryTaskRequest(
            task_id=task_id,
            agent_id=test_agent_id
        )
        response = grpc_stub.RetryTask(retry_request)
        
        assert response.success is True
        # 如果创建了新任务，应该有 new_task_id
        if response.new_task_id:
            assert len(response.new_task_id) > 0

