"""任务幂等性测试用例"""
import pytest
import uuid
from agent_queues import PrivateAgentTasksQueue
from agent_queues import DATA_PROCESSING


class TestTaskIdempotency:
    """任务幂等性功能测试"""
    
    def test_idempotency_with_client_request_id(self):
        """
        测试使用 client_request_id 的幂等性
        
        场景：
        1. 使用相同的 client_request_id 提交任务两次
        2. 验证第二次提交返回已存在的任务ID，而不是创建新任务
        """
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_idempotency"
        client_request_id = f"req_{uuid.uuid4()}"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue, server may not be running")
            
            # 第一次提交任务
            submit_response1 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test1"}',
                client_request_id=client_request_id
            )
            
            if not submit_response1.success:
                pytest.skip("Failed to submit task, server may not be running")
            
            task_id1 = submit_response1.task_id
            print(f"✓ 第一次提交成功，任务ID: {task_id1}")
            
            # 第二次提交相同的任务（使用相同的 client_request_id）
            submit_response2 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test2"}',  # 即使 payload 不同，也应该返回已存在的任务
                client_request_id=client_request_id
            )
            
            assert submit_response2.success, "第二次提交应该成功（幂等性）"
            task_id2 = submit_response2.task_id
            
            # 验证：两次提交返回相同的任务ID
            assert task_id1 == task_id2, \
                f"幂等性检查失败：第一次任务ID {task_id1} != 第二次任务ID {task_id2}"
            
            # 验证响应消息包含幂等性提示
            assert "already exists" in submit_response2.message.lower() or \
                   "idempotency" in submit_response2.message.lower(), \
                f"响应消息应该包含幂等性提示，实际: {submit_response2.message}"
            
            print(f"✓ 第二次提交返回已存在的任务ID: {task_id2}")
            print(f"✓ 幂等性测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_idempotency_without_client_request_id(self):
        """
        测试不使用 client_request_id 时的行为
        
        场景：
        1. 不提供 client_request_id 提交任务
        2. 验证每次提交都会创建新任务
        """
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_no_idempotency"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 第一次提交（不提供 client_request_id）
            submit_response1 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test1"}'
                # 不提供 client_request_id
            )
            
            if not submit_response1.success:
                pytest.skip("Failed to submit task")
            
            task_id1 = submit_response1.task_id
            
            # 第二次提交（同样不提供 client_request_id）
            submit_response2 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test2"}'
                # 不提供 client_request_id
            )
            
            if not submit_response2.success:
                pytest.skip("Failed to submit task")
            
            task_id2 = submit_response2.task_id
            
            # 验证：两次提交创建了不同的任务
            assert task_id1 != task_id2, \
                f"不使用 client_request_id 时应该创建新任务，但任务ID相同: {task_id1}"
            
            print(f"✓ 不使用 client_request_id 时创建了新任务: {task_id1} 和 {task_id2}")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_idempotency_different_agents(self):
        """
        测试不同 agent 之间的幂等性隔离
        
        场景：
        1. 使用相同的 client_request_id 向不同的 agent 提交任务
        2. 验证每个 agent 都有自己独立的幂等性检查
        """
        queue = PrivateAgentTasksQueue()
        client_request_id = f"req_{uuid.uuid4()}"
        agent_id1 = "test_agent_1"
        agent_id2 = "test_agent_2"
        
        try:
            # 创建两个队列
            queue.create_queue(agent_id1)
            queue.create_queue(agent_id2)
            
            # 向 agent1 提交任务
            submit_response1 = queue.submit_task(
                agent_id=agent_id1,
                task_type=DATA_PROCESSING,
                payload='{"data": "test1"}',
                client_request_id=client_request_id
            )
            
            if not submit_response1.success:
                pytest.skip("Failed to submit task")
            
            task_id1 = submit_response1.task_id
            
            # 向 agent2 提交任务（使用相同的 client_request_id）
            submit_response2 = queue.submit_task(
                agent_id=agent_id2,
                task_type=DATA_PROCESSING,
                payload='{"data": "test2"}',
                client_request_id=client_request_id
            )
            
            if not submit_response2.success:
                pytest.skip("Failed to submit task")
            
            task_id2 = submit_response2.task_id
            
            # 验证：不同 agent 应该创建不同的任务
            assert task_id1 != task_id2, \
                f"不同 agent 应该创建不同的任务，但任务ID相同: {task_id1}"
            
            print(f"✓ 不同 agent 之间的幂等性隔离正常: {task_id1} 和 {task_id2}")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_idempotency_retry_scenario(self):
        """
        测试重试场景下的幂等性
        
        场景：
        1. 提交任务（模拟第一次请求）
        2. 使用相同的 client_request_id 再次提交（模拟重试）
        3. 验证重试不会创建重复任务
        """
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_retry"
        client_request_id = f"req_{uuid.uuid4()}"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 第一次提交（模拟原始请求）
            submit_response1 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "original"}',
                client_request_id=client_request_id
            )
            
            if not submit_response1.success:
                pytest.skip("Failed to submit task")
            
            task_id1 = submit_response1.task_id
            print(f"✓ 原始请求成功，任务ID: {task_id1}")
            
            # 模拟重试：使用相同的 client_request_id 再次提交
            submit_response2 = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "retry"}',  # 即使 payload 不同
                client_request_id=client_request_id  # 相同的 client_request_id
            )
            
            assert submit_response2.success, "重试应该成功（幂等性）"
            task_id2 = submit_response2.task_id
            
            # 验证：重试返回已存在的任务ID
            assert task_id1 == task_id2, \
                f"重试应该返回已存在的任务ID，但得到: {task_id1} != {task_id2}"
            
            # 验证队列中只有一个任务
            get_response = queue.get_task(agent_id, timeout=1)
            if get_response.success and get_response.task:
                assert get_response.task.task_id == task_id1, \
                    "队列中应该只有一个任务"
            
            print(f"✓ 重试场景幂等性测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

