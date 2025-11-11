"""综合测试用例 - 覆盖所有接口和功能"""
import pytest
import uuid
import json
from agent_queues import PrivateAgentTasksQueue, create_manager
from agent_queues import (
    DATA_PROCESSING, IMAGE_PROCESSING, CUSTOM,
    PENDING, PROCESSING, COMPLETED, FAILED
)


class TestComprehensive:
    """综合功能测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        queue = PrivateAgentTasksQueue()
        try:
            response = queue.health_check()
            assert response is not None
            assert hasattr(response, 'status')
            print(f"✓ 健康检查成功，状态: {response.status}")
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_full_task_lifecycle(self):
        """测试完整任务生命周期"""
        queue = PrivateAgentTasksQueue()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        client_request_id = f"req_{uuid.uuid4()}"
        
        try:
            # 1. 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 2. 提交任务（带优先级和幂等性）
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test"}',
                priority=9,
                client_request_id=client_request_id
            )
            assert submit_response.success
            task_id = submit_response.task_id
            print(f"✓ 任务提交成功，任务ID: {task_id}")
            
            # 3. 查询任务
            query_response = queue.query_task(task_id, agent_id)
            assert query_response.success
            assert query_response.task.task_id == task_id
            assert query_response.task.priority == 9
            assert query_response.task.client_request_id == client_request_id
            print(f"✓ 任务查询成功，优先级: {query_response.task.priority}")
            
            # 4. 获取任务（按优先级）
            get_response = queue.get_task(agent_id, timeout=1)
            assert get_response.success
            assert get_response.task.task_id == task_id
            print(f"✓ 任务获取成功")
            
            # 5. 更新任务状态
            update_response = queue.update_task_status(
                task_id=task_id,
                agent_id=agent_id,
                status=PROCESSING,
                result='{"processed": true}'
            )
            assert update_response.success
            print(f"✓ 任务状态更新成功")
            
            # 6. 再次查询验证状态
            query_response2 = queue.query_task(task_id, agent_id)
            assert query_response2.task.status == PROCESSING
            print(f"✓ 任务状态验证成功")
            
            # 7. 完成任务
            queue.update_task_status(
                task_id=task_id,
                agent_id=agent_id,
                status=COMPLETED,
                result='{"result": "success"}'
            )
            
            # 8. 验证幂等性
            retry_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "different"}',
                priority=5,
                client_request_id=client_request_id
            )
            assert retry_response.success
            assert retry_response.task_id == task_id  # 应该返回已存在的任务ID
            print(f"✓ 幂等性验证成功")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_batch_operations(self):
        """测试批量操作"""
        queue = PrivateAgentTasksQueue()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        
        try:
            # 创建队列
            queue.create_queue(agent_id)
            
            # 批量提交任务
            from agent_queues import SubmitTaskItem
            tasks = [
                SubmitTaskItem(
                    type=DATA_PROCESSING,
                    payload=json.dumps({"id": i, "data": f"task_{i}"}),
                    priority=i % 10
                )
                for i in range(5)
            ]
            
            batch_response = queue.batch_submit_tasks(agent_id, tasks)
            assert batch_response.success
            assert len(batch_response.task_ids) == 5
            assert batch_response.success_count == 5
            print(f"✓ 批量提交成功，提交了 {batch_response.success_count} 个任务")
            
            # 验证优先级排序
            retrieved_priorities = []
            for _ in range(5):
                get_response = queue.get_task(agent_id, timeout=1)
                if get_response.success:
                    retrieved_priorities.append(get_response.task.priority)
            
            # 应该按优先级从高到低
            assert retrieved_priorities == sorted(retrieved_priorities, reverse=True)
            print(f"✓ 优先级排序验证成功: {retrieved_priorities}")
            
            # 批量删除任务
            task_ids = batch_response.task_ids
            batch_delete_response = queue.batch_delete_tasks(agent_id, task_ids)
            assert batch_delete_response.success
            print(f"✓ 批量删除成功，删除了 {batch_delete_response.deleted_count} 个任务")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_agent_queue_manager(self):
        """测试 Agent Queue Manager"""
        manager = create_manager()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        client_request_id = f"req_{uuid.uuid4()}"
        
        try:
            # 分配任务（自动创建队列）
            result = manager.assign_task(
                target_agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload={"data": "test"},
                priority=8,
                client_request_id=client_request_id
            )
            assert result["success"]
            task_id = result["task_id"]
            print(f"✓ Manager 分配任务成功，任务ID: {task_id}")
            
            # 验证队列自动创建
            queue = manager.queue_client
            exists_response = queue.queue_exists(agent_id)
            assert exists_response.exists
            print(f"✓ 队列自动创建验证成功")
            
            # 负载均衡分配
            result2 = manager.assign_task_with_load_balance(
                candidate_agents=[agent_id, f"{agent_id}_2"],
                task_type=DATA_PROCESSING,
                payload={"data": "load_balance"},
                priority=7
            )
            assert result2["success"]
            print(f"✓ 负载均衡分配成功")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            manager.queue_client.close()
    
    def test_task_status_transitions(self):
        """测试任务状态转换"""
        queue = PrivateAgentTasksQueue()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        
        try:
            queue.create_queue(agent_id)
            
            # 提交任务
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test"}'
            )
            task_id = submit_response.task_id
            
            # 验证初始状态
            query_response = queue.query_task(task_id, agent_id)
            assert query_response.task.status == PENDING
            
            # PENDING -> PROCESSING
            queue.update_task_status(task_id, agent_id, PROCESSING)
            query_response = queue.query_task(task_id, agent_id)
            assert query_response.task.status == PROCESSING
            
            # PROCESSING -> COMPLETED
            queue.update_task_status(task_id, agent_id, COMPLETED, result='{"result": "ok"}')
            query_response = queue.query_task(task_id, agent_id)
            assert query_response.task.status == COMPLETED
            
            print(f"✓ 任务状态转换测试成功: PENDING -> PROCESSING -> COMPLETED")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_retry_task(self):
        """测试重试任务"""
        queue = PrivateAgentTasksQueue()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        client_request_id = f"req_{uuid.uuid4()}"
        
        try:
            queue.create_queue(agent_id)
            
            # 提交任务并标记为失败
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test"}'
            )
            task_id = submit_response.task_id
            
            queue.update_task_status(
                task_id=task_id,
                agent_id=agent_id,
                status=FAILED,
                error_message="Test error"
            )
            
            # 重试任务
            retry_response = queue.retry_task(
                task_id=task_id,
                agent_id=agent_id,
                client_request_id=client_request_id
            )
            assert retry_response.success
            new_task_id = retry_response.new_task_id
            assert new_task_id != task_id
            print(f"✓ 任务重试成功，新任务ID: {new_task_id}")
            
            # 验证新任务
            query_response = queue.query_task(new_task_id, agent_id)
            assert query_response.task.status == PENDING
            assert query_response.task.client_request_id == client_request_id
            print(f"✓ 重试任务验证成功")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_queue_management(self):
        """测试队列管理功能"""
        queue = PrivateAgentTasksQueue()
        agent_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        
        try:
            # 创建队列
            create_response = queue.create_queue(agent_id)
            assert create_response.success
            
            # 检查队列是否存在
            exists_response = queue.queue_exists(agent_id)
            assert exists_response.exists
            
            # 获取队列信息
            info_response = queue.get_queue_info(agent_id)
            assert info_response.success
            assert hasattr(info_response, 'pending_count')
            print(f"✓ 队列信息获取成功")
            
            # 提交一些任务
            for i in range(3):
                queue.submit_task(
                    agent_id=agent_id,
                    task_type=DATA_PROCESSING,
                    payload=json.dumps({"id": i})
                )
            
            # 再次获取队列信息
            info_response2 = queue.get_queue_info(agent_id)
            assert info_response2.pending_count >= 3
            
            # 清空队列
            clear_response = queue.clear_queue(agent_id, confirm=True)
            assert clear_response.success
            
            # 验证队列已清空
            info_response3 = queue.get_queue_info(agent_id)
            assert info_response3.pending_count == 0
            print(f"✓ 队列清空成功")
            
            # 删除队列
            delete_response = queue.delete_queue(agent_id, confirm=True)
            assert delete_response.success
            print(f"✓ 队列删除成功")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

