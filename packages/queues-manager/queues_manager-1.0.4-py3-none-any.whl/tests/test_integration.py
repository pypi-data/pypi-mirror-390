"""
集成测试 - 测试完整的工作流程
"""
import json
import pytest
from agent_queues import PrivateAgentTasksQueue
from agent_queues import (
    DATA_PROCESSING, IMAGE_PROCESSING, TEXT_ANALYSIS,
    PENDING, PROCESSING, COMPLETED, FAILED
)


class TestIntegration:
    """集成测试类"""
    
    def test_complete_workflow(self, queue_client, test_agent_id):
        """测试完整的工作流程"""
        # 1. 创建队列
        create_response = queue_client.create_queue(test_agent_id)
        assert create_response.success is True
        
        # 2. 提交任务
        payload = json.dumps({"data": "test", "action": "process"})
        submit_response = queue_client.submit_task(
            agent_id=test_agent_id,
            task_type=DATA_PROCESSING,
            payload=payload
        )
        assert submit_response.success is True
        task_id = submit_response.task_id
        
        # 3. 查询任务
        query_response = queue_client.query_task(task_id, test_agent_id)
        assert query_response.success is True
        assert query_response.task.task_id == task_id
        assert query_response.task.status == PENDING
        
        # 4. 获取任务
        get_response = queue_client.get_task(test_agent_id, timeout=5)
        assert get_response.success is True
        assert get_response.task.task_id == task_id
        
        # 5. 更新任务状态
        result = json.dumps({"result": "success"})
        update_response = queue_client.update_task_status(
            task_id=task_id,
            agent_id=test_agent_id,
            status=COMPLETED,
            result=result
        )
        assert update_response.success is True
        
        # 6. 再次查询任务，确认状态已更新
        query_response2 = queue_client.query_task(task_id, test_agent_id)
        assert query_response2.success is True
        assert query_response2.task.status == COMPLETED
        assert query_response2.task.result == result
        
        # 7. 获取统计信息
        stats_response = queue_client.get_task_stats(test_agent_id)
        assert stats_response.success is True
        assert stats_response.completed_count >= 1
    
    def test_multiple_agents_isolation(self, queue_client):
        """测试多个 agent 之间的隔离"""
        import uuid
        
        agent_id_1 = f"agent_{uuid.uuid4().hex[:8]}"
        agent_id_2 = f"agent_{uuid.uuid4().hex[:8]}"
        
        # 为两个 agent 创建队列
        queue_client.create_queue(agent_id_1)
        queue_client.create_queue(agent_id_2)
        
        # 为 agent_1 提交任务
        payload1 = json.dumps({"agent": "1", "data": "test1"})
        submit1 = queue_client.submit_task(
            agent_id=agent_id_1,
            task_type=DATA_PROCESSING,
            payload=payload1
        )
        task_id_1 = submit1.task_id
        
        # 为 agent_2 提交任务
        payload2 = json.dumps({"agent": "2", "data": "test2"})
        submit2 = queue_client.submit_task(
            agent_id=agent_id_2,
            task_type=DATA_PROCESSING,
            payload=payload2
        )
        task_id_2 = submit2.task_id
        
        # 从 agent_1 获取任务，应该只能获取到 agent_1 的任务
        get1 = queue_client.get_task(agent_id_1, timeout=5)
        assert get1.success is True
        assert get1.task.task_id == task_id_1
        assert get1.task.agent_id == agent_id_1
        
        # 从 agent_2 获取任务，应该只能获取到 agent_2 的任务
        get2 = queue_client.get_task(agent_id_2, timeout=5)
        assert get2.success is True
        assert get2.task.task_id == task_id_2
        assert get2.task.agent_id == agent_id_2
    
    def test_task_retry_workflow(self, queue_client, test_agent_id):
        """测试任务重试工作流"""
        # 1. 提交任务
        payload = json.dumps({"data": "test"})
        submit_response = queue_client.submit_task(
            agent_id=test_agent_id,
            task_type=DATA_PROCESSING,
            payload=payload
        )
        task_id = submit_response.task_id
        
        # 2. 获取任务
        get_response = queue_client.get_task(test_agent_id, timeout=5)
        
        # 3. 标记为失败
        update_response = queue_client.update_task_status(
            task_id=task_id,
            agent_id=test_agent_id,
            status=FAILED,
            error_message="Test failure"
        )
        assert update_response.success is True
        
        # 4. 重试任务
        retry_response = queue_client.retry_task(task_id, test_agent_id)
        assert retry_response.success is True
        
        # 5. 如果有新任务ID，验证新任务存在
        if retry_response.new_task_id:
            query_response = queue_client.query_task(
                retry_response.new_task_id,
                test_agent_id
            )
            assert query_response.success is True
            assert query_response.task.status == PENDING
    
    def test_batch_processing_workflow(self, queue_client, test_agent_id):
        """测试批量处理工作流"""
        from agent_queues import SubmitTaskItem
        
        # 1. 批量提交任务
        tasks = [
            SubmitTaskItem(
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i, "data": f"task_{i}"})
            )
            for i in range(5)
        ]
        
        batch_response = queue_client.batch_submit_tasks(test_agent_id, tasks)
        assert batch_response.success is True
        assert batch_response.success_count == 5
        
        # 2. 处理所有任务
        processed_count = 0
        while processed_count < 5:
            get_response = queue_client.get_task(test_agent_id, timeout=2)
            if not get_response.success or not get_response.task.task_id:
                break
            
            task = get_response.task
            # 更新为已完成
            queue_client.update_task_status(
                task_id=task.task_id,
                agent_id=test_agent_id,
                status=COMPLETED,
                result=json.dumps({"result": "success"})
            )
            processed_count += 1
        
        assert processed_count == 5
        
        # 3. 验证统计信息
        stats_response = queue_client.get_task_stats(test_agent_id)
        assert stats_response.success is True
        assert stats_response.completed_count >= 5

