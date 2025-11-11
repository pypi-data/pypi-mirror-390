"""任务优先级测试用例"""
import pytest
from agent_queues import PrivateAgentTasksQueue
from agent_queues import DATA_PROCESSING, PENDING


class TestTaskPriority:
    """任务优先级功能测试"""
    
    def test_priority_queue_ordering(self):
        """
        测试优先级队列排序
        
        场景：
        1. 提交多个不同优先级的任务
        2. 验证高优先级任务优先被获取
        """
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_priority"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue, server may not be running")
            
            # 提交不同优先级的任务（按低到高优先级）
            task_ids = []
            priorities = [1, 3, 5, 7, 9]
            
            for priority in priorities:
                submit_response = queue.submit_task(
                    agent_id=agent_id,
                    task_type=DATA_PROCESSING,
                    payload=f'{{"priority": {priority}, "data": "test_{priority}"}}',
                    priority=priority
                )
                if submit_response.success:
                    task_ids.append((submit_response.task_id, priority))
                    print(f"✓ 提交优先级 {priority} 的任务: {submit_response.task_id}")
                # 稍微延迟，确保时间戳不同
                import time
                time.sleep(0.05)
            
            # 等待任务添加到队列
            time.sleep(0.1)
            
            # 按优先级从高到低获取任务，验证顺序
            retrieved_priorities = []
            for _ in range(len(task_ids)):
                get_response = queue.get_task(agent_id, timeout=2)
                if get_response.success and get_response.task:
                    priority = get_response.task.priority
                    retrieved_priorities.append(priority)
                    print(f"✓ 获取到优先级 {priority} 的任务: {get_response.task.task_id}")
                else:
                    print(f"✗ 未能获取任务: {get_response.message if hasattr(get_response, 'message') else 'Unknown error'}")
            
            # 验证：获取的优先级应该是从高到低（9, 7, 5, 3, 1）
            assert len(retrieved_priorities) == len(priorities), \
                f"应该获取 {len(priorities)} 个任务，实际获取 {len(retrieved_priorities)} 个"
            expected_order = sorted(priorities, reverse=True)
            assert retrieved_priorities == expected_order, \
                f"优先级顺序不正确，期望: {expected_order}, 实际: {retrieved_priorities}"
            
            print("✓ 优先级队列排序测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_default_priority(self):
        """测试默认优先级（应该是5）"""
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_default_priority"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 提交任务（不指定优先级）
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"data": "test"}'
                # 不指定 priority，应该使用默认值5
            )
            
            if submit_response.success:
                # 等待任务添加到队列
                import time
                time.sleep(0.1)
                
                # 获取任务，验证优先级为5
                get_response = queue.get_task(agent_id, timeout=2)
                if get_response.success and get_response.task:
                    assert get_response.task.priority == 5, \
                        f"默认优先级应该是5，实际是: {get_response.task.priority}"
                    print("✓ 默认优先级测试通过")
                else:
                    pytest.skip(f"未能获取任务: {get_response.message if hasattr(get_response, 'message') else 'Unknown error'}")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_priority_range(self):
        """测试优先级范围（0-9）"""
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_priority_range"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 测试边界值
            test_priorities = [0, 5, 9]
            
            for priority in test_priorities:
                submit_response = queue.submit_task(
                    agent_id=agent_id,
                    task_type=DATA_PROCESSING,
                    payload=f'{{"priority": {priority}}}',
                    priority=priority
                )
                
                if submit_response.success:
                    # 等待任务添加到队列
                    import time
                    time.sleep(0.1)
                    
                    # 获取任务，验证优先级
                    get_response = queue.get_task(agent_id, timeout=2)
                    if get_response.success and get_response.task:
                        assert get_response.task.priority == priority, \
                            f"优先级应该是{priority}，实际是: {get_response.task.priority}"
                    else:
                        print(f"⚠ 未能获取优先级 {priority} 的任务")
            
            print("✓ 优先级范围测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_same_priority_fifo(self):
        """
        测试相同优先级下的FIFO顺序
        
        场景：
        1. 提交多个相同优先级的任务
        2. 验证同优先级下先提交的任务先被获取
        """
        queue = PrivateAgentTasksQueue()
        agent_id = "test_agent_same_priority"
        
        try:
            # 创建队列
            response = queue.create_queue(agent_id)
            if not response.success:
                pytest.skip("Failed to create queue")
            
            # 提交多个相同优先级的任务
            task_ids = []
            priority = 5
            
            for i in range(3):
                submit_response = queue.submit_task(
                    agent_id=agent_id,
                    task_type=DATA_PROCESSING,
                    payload=f'{{"index": {i}}}',
                    priority=priority
                )
                if submit_response.success:
                    task_ids.append(submit_response.task_id)
                    # 稍微延迟，确保时间戳不同
                    import time
                    time.sleep(0.1)
            
            # 等待任务添加到队列
            import time
            time.sleep(0.1)
            
            # 获取任务，验证顺序（应该按提交顺序）
            retrieved_ids = []
            for _ in range(len(task_ids)):
                get_response = queue.get_task(agent_id, timeout=2)
                if get_response.success and get_response.task:
                    retrieved_ids.append(get_response.task.task_id)
                else:
                    print(f"⚠ 未能获取任务")
            
            # 验证：同优先级下，先提交的任务先被获取
            assert len(retrieved_ids) == len(task_ids), \
                f"应该获取 {len(task_ids)} 个任务，实际获取 {len(retrieved_ids)} 个"
            assert retrieved_ids == task_ids, \
                f"同优先级下FIFO顺序不正确，期望: {task_ids}, 实际: {retrieved_ids}"
            
            print("✓ 同优先级FIFO测试通过")
            
        except Exception as e:
            if "UNAVAILABLE" in str(e) or "Connection" in str(e):
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

