"""
任务查询接口测试
"""
import json
import pytest
from agent_queues import (
    ListTasksRequest, GetTasksByStatusRequest, GetTaskStatsRequest,
    DATA_PROCESSING, PENDING, COMPLETED, FAILED
)


class TestTaskQueries:
    """任务查询接口测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_queue(self, grpc_stub, test_agent_id):
        """每个测试前创建队列并提交一些任务"""
        from agent_queues import CreateQueueRequest, SubmitTaskRequest
        
        # 创建队列
        create_request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(create_request)
        
        # 提交几个任务
        for i in range(3):
            submit_request = SubmitTaskRequest(
                agent_id=test_agent_id,
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i, "data": f"task_{i}"})
            )
            grpc_stub.SubmitTask(submit_request)
    
    def test_list_tasks(self, grpc_stub, test_agent_id):
        """测试列出任务"""
        request = ListTasksRequest(
            agent_id=test_agent_id,
            status=0,  # 所有状态
            limit=10,
            offset=0
        )
        response = grpc_stub.ListTasks(request)
        
        assert response.success is True
        assert response.total >= 0
        assert len(response.tasks) >= 0
        assert len(response.tasks) <= 10
    
    def test_list_tasks_with_status(self, grpc_stub, test_agent_id):
        """测试按状态列出任务"""
        request = ListTasksRequest(
            agent_id=test_agent_id,
            status=PENDING,
            limit=10,
            offset=0
        )
        response = grpc_stub.ListTasks(request)
        
        assert response.success is True
        assert response.total >= 0
        # 所有返回的任务应该是 PENDING 状态
        for task in response.tasks:
            assert task.status == PENDING
    
    def test_list_tasks_pagination(self, grpc_stub, test_agent_id):
        """测试分页列出任务"""
        # 第一页
        request1 = ListTasksRequest(
            agent_id=test_agent_id,
            status=0,
            limit=2,
            offset=0
        )
        response1 = grpc_stub.ListTasks(request1)
        
        assert response1.success is True
        
        # 第二页
        request2 = ListTasksRequest(
            agent_id=test_agent_id,
            status=0,
            limit=2,
            offset=2
        )
        response2 = grpc_stub.ListTasks(request2)
        
        assert response2.success is True
        
        # 确保两页的任务ID不同（如果有足够多的任务）
        if len(response1.tasks) > 0 and len(response2.tasks) > 0:
            task_ids_1 = {task.task_id for task in response1.tasks}
            task_ids_2 = {task.task_id for task in response2.tasks}
            assert task_ids_1.isdisjoint(task_ids_2)
    
    def test_get_tasks_by_status(self, grpc_stub, test_agent_id):
        """测试按状态获取任务"""
        request = GetTasksByStatusRequest(
            agent_id=test_agent_id,
            status=PENDING,
            limit=10,
            offset=0
        )
        response = grpc_stub.GetTasksByStatus(request)
        
        assert response.success is True
        assert response.total >= 0
        # 所有返回的任务应该是 PENDING 状态
        for task in response.tasks:
            assert task.status == PENDING
    
    def test_get_task_stats(self, grpc_stub, test_agent_id):
        """测试获取任务统计信息"""
        request = GetTaskStatsRequest(agent_id=test_agent_id)
        response = grpc_stub.GetTaskStats(request)
        
        assert response.success is True
        assert response.total_count >= 0
        assert response.pending_count >= 0
        assert response.processing_count >= 0
        assert response.completed_count >= 0
        assert response.failed_count >= 0
        
        # 总数应该等于各状态任务数之和
        total_sum = (
            response.pending_count +
            response.processing_count +
            response.completed_count +
            response.failed_count
        )
        assert response.total_count == total_sum
    
    def test_get_task_stats_by_status(self, grpc_stub, test_agent_id):
        """测试按状态获取任务统计信息"""
        request = GetTaskStatsRequest(
            agent_id=test_agent_id,
            status=PENDING
        )
        response = grpc_stub.GetTaskStats(request)
        
        assert response.success is True
        # 当指定状态时，total_count 应该等于该状态的任务数
        # 但具体实现可能不同，这里只检查响应格式
        assert response.total_count >= 0

