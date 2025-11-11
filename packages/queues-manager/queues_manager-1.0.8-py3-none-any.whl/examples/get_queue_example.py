"""
通过 agent ID 获取私有化任务队列的示例

演示如何使用 get_queue() 方法获取特定 agent 的队列对象，
并使用该对象进行队列操作。
"""
from agent_queues import PrivateAgentTasksQueue, AgentQueue
from agent_queues import DATA_PROCESSING, PENDING, COMPLETED, FAILED


def example_get_queue():
    """示例：获取队列并操作"""
    # 创建客户端
    client = PrivateAgentTasksQueue()
    
    try:
        # 方式1：获取队列（如果不存在则自动创建）
        agent_id = "agent_001"
        queue = client.get_queue(agent_id, create_if_not_exists=True)
        print(f"✓ 成功获取队列: {agent_id}")
        
        # 方式2：检查队列是否存在后再获取
        if client.queue_exists(agent_id).exists:
            queue = client.get_queue(agent_id)
            print(f"✓ 队列已存在，获取成功")
        else:
            print("✗ 队列不存在")
            return
        
        # 使用队列对象提交任务（不需要再指定 agent_id）
        response = queue.submit_task(
            task_type=DATA_PROCESSING,
            payload='{"data": "test", "action": "process"}',
            priority=9  # 高优先级
        )
        
        if response.success:
            print(f"✓ 任务提交成功，任务ID: {response.task_id}")
        else:
            print(f"✗ 任务提交失败: {response.message}")
        
        # 获取队列信息
        info = queue.get_info()
        if info.success:
            print(f"\n队列信息:")
            print(f"  - 待处理: {info.pending_count}")
            print(f"  - 处理中: {info.processing_count}")
            print(f"  - 已完成: {info.completed_count}")
            print(f"  - 失败: {info.failed_count}")
            print(f"  - 总计: {info.total_count}")
        
        # 获取任务
        task_response = queue.get_task(timeout=5)
        if task_response.success and task_response.task:
            task = task_response.task
            print(f"\n✓ 获取到任务:")
            print(f"  - 任务ID: {task.task_id}")
            print(f"  - 优先级: {task.priority}")
            print(f"  - 状态: {task.status}")
        
        # 列出所有任务
        list_response = queue.list_tasks(limit=10)
        if list_response.success:
            print(f"\n队列中的任务（前10个）:")
            for task in list_response.tasks:
                print(f"  - {task.task_id}: {task.status}")
        
        # 获取特定状态的任务
        pending_response = queue.get_tasks_by_status(status=PENDING, limit=5)
        if pending_response.success:
            print(f"\n待处理任务: {pending_response.total} 个")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        client.close()


def example_multiple_queues():
    """示例：管理多个 agent 的队列"""
    client = PrivateAgentTasksQueue()
    
    try:
        agent_ids = ["agent_001", "agent_002", "agent_003"]
        queues = {}
        
        # 获取多个队列
        for agent_id in agent_ids:
            try:
                queue = client.get_queue(agent_id, create_if_not_exists=True)
                queues[agent_id] = queue
                print(f"✓ 获取队列: {agent_id}")
            except Exception as e:
                print(f"✗ 获取队列失败 {agent_id}: {e}")
        
        # 向不同队列提交任务
        for agent_id, queue in queues.items():
            response = queue.submit_task(
                task_type=DATA_PROCESSING,
                payload=f'{{"agent": "{agent_id}", "data": "test"}}',
                priority=5
            )
            if response.success:
                print(f"✓ 向 {agent_id} 提交任务成功: {response.task_id}")
        
        # 获取所有队列的状态
        print("\n所有队列状态:")
        for agent_id, queue in queues.items():
            info = queue.get_info()
            if info.success:
                print(f"  {agent_id}: {info.pending_count} 待处理, {info.total_count} 总计")
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        client.close()


def example_queue_operations():
    """示例：队列的各种操作"""
    client = PrivateAgentTasksQueue()
    
    try:
        agent_id = "agent_demo"
        queue = client.get_queue(agent_id, create_if_not_exists=True)
        
        # 1. 提交任务
        print("1. 提交任务")
        response = queue.submit_task(
            task_type=DATA_PROCESSING,
            payload='{"test": "data"}',
            priority=7
        )
        print(f"   任务ID: {response.task_id}")
        
        # 2. 获取任务统计
        print("\n2. 获取任务统计")
        stats = queue.get_task_stats()
        if stats.success:
            print(f"   总计: {stats.total_count}")
            print(f"   待处理: {stats.pending_count}")
            print(f"   处理中: {stats.processing_count}")
            print(f"   已完成: {stats.completed_count}")
            print(f"   失败: {stats.failed_count}")
        
        # 3. 查询特定任务
        if response.success:
            print(f"\n3. 查询任务: {response.task_id}")
            query_response = queue.query_task(response.task_id)
            if query_response.success and query_response.task:
                task = query_response.task
                print(f"   状态: {task.status}")
                print(f"   优先级: {task.priority}")
        
        # 4. 清空队列（示例，实际使用时需要确认）
        # queue.clear(confirm=True)
        
        # 5. 删除队列（示例，实际使用时需要确认）
        # queue.delete(confirm=True)
        
    except Exception as e:
        print(f"✗ 错误: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    print("=" * 60)
    print("示例1: 获取队列并操作")
    print("=" * 60)
    example_get_queue()
    
    print("\n" + "=" * 60)
    print("示例2: 管理多个 agent 的队列")
    print("=" * 60)
    example_multiple_queues()
    
    print("\n" + "=" * 60)
    print("示例3: 队列的各种操作")
    print("=" * 60)
    example_queue_operations()

