"""
客户端封装类测试
"""
import json
import pytest
from agent_queues import PrivateAgentTasksQueue
from agent_queues import DATA_PROCESSING, COMPLETED, FAILED


class TestClientWrapper:
    """客户端封装类测试"""
    
    @pytest.fixture(autouse=True)
    def setup_queue(self, queue_client, test_agent_id):
        """每个测试前创建队列"""
        response = queue_client.create_queue(test_agent_id)
        assert response.success is True
    
    def test_create_queue(self, queue_client, test_agent_id):
        """测试创建队列"""
        response = queue_client.create_queue(test_agent_id)
        assert response.success is True
    
    def test_queue_exists(self, queue_client, test_agent_id):
        """测试检查队列是否存在"""
        response = queue_client.queue_exists(test_agent_id)
        assert response.exists is True
    
    def test_get_queue_info(self, queue_client, test_agent_id):
        """测试获取队列信息"""
        response = queue_client.get_queue_info(test_agent_id)
        assert response.success is True
        assert response.agent_id == test_agent_id
    
    def test_submit_task(self, queue_client, test_agent_id):
        """测试提交任务"""
        payload = json.dumps({"data": "test"})
        response = queue_client.submit_task(
            agent_id=test_agent_id,
            task_type=DATA_PROCESSING,
            payload=payload
        )
        assert response.success is True
        assert response.task_id is not None
    
    def test_get_task(self, queue_client, test_agent_id):
        """测试获取任务"""
        # 先提交任务
        payload = json.dumps({"data": "test"})
        submit_response = queue_client.submit_task(
            agent_id=test_agent_id,
            task_type=DATA_PROCESSING,
            payload=payload
        )
        
        # 获取任务
        get_response = queue_client.get_task(test_agent_id, timeout=5)
        assert get_response.success is True
        assert get_response.task is not None
    
    def test_update_task_status(self, queue_client, test_agent_id):
        """测试更新任务状态"""
        # 先提交任务
        payload = json.dumps({"data": "test"})
        submit_response = queue_client.submit_task(
            agent_id=test_agent_id,
            task_type=DATA_PROCESSING,
            payload=payload
        )
        task_id = submit_response.task_id
        
        # 获取任务
        get_response = queue_client.get_task(test_agent_id, timeout=5)
        
        # 更新状态
        result = json.dumps({"result": "success"})
        update_response = queue_client.update_task_status(
            task_id=task_id,
            agent_id=test_agent_id,
            status=COMPLETED,
            result=result
        )
        assert update_response.success is True
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with PrivateAgentTasksQueue(grpc_host="localhost", grpc_port=50051) as queue:
            assert queue is not None
            assert queue.stub is not None
        # 退出上下文后，连接应该已关闭
    
    def test_batch_operations(self, queue_client, test_agent_id):
        """测试批量操作"""
        from agent_queues import SubmitTaskItem
        
        # 批量提交任务
        tasks = [
            SubmitTaskItem(
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i})
            )
            for i in range(3)
        ]
        
        batch_response = queue_client.batch_submit_tasks(test_agent_id, tasks)
        assert batch_response.success is True
        assert batch_response.success_count == 3
        
        # 批量删除任务
        delete_response = queue_client.batch_delete_tasks(
            test_agent_id,
            batch_response.task_ids
        )
        assert delete_response.success is True

