"""
基础使用示例 - 演示 Agent Queue 的基本功能

运行前确保：
1. Redis 服务正在运行
2. gRPC 服务器已启动（python start.py）
3. 已安装依赖：pip install .
"""
import json
import time
from agent_queues import PrivateAgentTasksQueue
from agent_queues import (
    DATA_PROCESSING, IMAGE_PROCESSING, TEXT_ANALYSIS,
    PENDING, PROCESSING, COMPLETED, FAILED
)


def main():
    # 1. 创建客户端
    print("=" * 60)
    print("1. 创建客户端")
    print("=" * 60)
    
    queue = PrivateAgentTasksQueue(
        grpc_host="localhost",
        grpc_port=50051
    )
    
    agent_id = "demo_agent_001"
    
    try:
        # 2. 创建队列
        print("\n2. 创建队列")
        print("-" * 60)
        create_response = queue.create_queue(agent_id)
        if create_response.success:
            print(f"✓ 队列创建成功: {agent_id}")
        else:
            print(f"✗ 队列创建失败: {create_response.message}")
            return
        
        # 3. 检查队列是否存在
        print("\n3. 检查队列是否存在")
        print("-" * 60)
        exists_response = queue.queue_exists(agent_id)
        if exists_response.exists:
            print(f"✓ 队列存在: {agent_id}")
        else:
            print(f"✗ 队列不存在: {agent_id}")
        
        # 4. 获取队列信息
        print("\n4. 获取队列信息")
        print("-" * 60)
        info_response = queue.get_queue_info(agent_id)
        if info_response.success:
            print(f"待处理: {info_response.pending_count}")
            print(f"处理中: {info_response.processing_count}")
            print(f"已完成: {info_response.completed_count}")
            print(f"失败: {info_response.failed_count}")
            print(f"总计: {info_response.total_count}")
        
        # 5. 提交任务
        print("\n5. 提交任务")
        print("-" * 60)
        
        # 提交数据处理任务
        task1_payload = json.dumps({
            "data": "sample data",
            "action": "process",
            "timestamp": int(time.time())
        })
        
        submit_response = queue.submit_task(
            agent_id=agent_id,
            task_type=DATA_PROCESSING,
            payload=task1_payload,
            priority=5,  # 任务优先级（0-9，数字越大优先级越高）
            client_request_id=""  # 可选：用于幂等性，防止重复提交
        )
        
        if submit_response.success:
            task_id = submit_response.task_id
            print(f"✓ 任务提交成功，ID: {task_id}")
        else:
            print(f"✗ 任务提交失败: {submit_response.message}")
            return
        
        # 6. 查询任务
        print("\n6. 查询任务")
        print("-" * 60)
        query_response = queue.query_task(task_id, agent_id)
        if query_response.success:
            task = query_response.task
            print(f"任务ID: {task.task_id}")
            print(f"任务类型: {task.task_type}")
            print(f"状态: {task.status}")
            print(f"负载: {task.payload}")
            print(f"创建时间: {task.created_at}")
        
        # 7. 获取任务（从队列中拉取）
        print("\n7. 获取任务（从队列中拉取）")
        print("-" * 60)
        get_response = queue.get_task(agent_id, timeout=5)
        if get_response.success and get_response.task.task_id:
            task = get_response.task
            print(f"✓ 获取到任务: {task.task_id}")
            print(f"  状态: {task.status}")
            print(f"  负载: {task.payload}")
            
            # 8. 更新任务状态
            print("\n8. 更新任务状态")
            print("-" * 60)
            result = json.dumps({
                "result": "处理完成",
                "output": "success",
                "processed_at": int(time.time())
            })
            
            update_response = queue.update_task_status(
                task_id=task.task_id,
                agent_id=agent_id,
                status=COMPLETED,
                result=result
            )
            
            if update_response.success:
                print(f"✓ 任务状态更新成功: {task.task_id}")
            else:
                print(f"✗ 任务状态更新失败: {update_response.message}")
        else:
            print("✗ 队列中没有任务")
        
        # 9. 再次查询任务，查看更新后的状态
        print("\n9. 再次查询任务，查看更新后的状态")
        print("-" * 60)
        query_response = queue.query_task(task_id, agent_id)
        if query_response.success:
            task = query_response.task
            print(f"任务ID: {task.task_id}")
            print(f"状态: {task.status} ({'已完成' if task.status == COMPLETED else '其他'})")
            print(f"结果: {task.result}")
        
        # 10. 获取队列统计信息
        print("\n10. 获取队列统计信息")
        print("-" * 60)
        stats_response = queue.get_task_stats(agent_id)
        if stats_response.success:
            print(f"总任务数: {stats_response.total_count}")
            print(f"待处理: {stats_response.pending_count}")
            print(f"处理中: {stats_response.processing_count}")
            print(f"已完成: {stats_response.completed_count}")
            print(f"失败: {stats_response.failed_count}")
        
        # 11. 列出所有任务
        print("\n11. 列出所有任务")
        print("-" * 60)
        list_response = queue.list_tasks(agent_id, status=0, limit=10, offset=0)
        if list_response.success:
            print(f"找到 {list_response.total} 个任务")
            for task in list_response.tasks:
                status_name = {
                    PENDING: "待处理",
                    PROCESSING: "处理中",
                    COMPLETED: "已完成",
                    FAILED: "失败"
                }.get(task.status, "未知")
                print(f"  - {task.task_id}: {status_name}")
        
        print("\n" + "=" * 60)
        print("示例执行完成！")
        print("=" * 60)
        
    finally:
        # 关闭客户端连接
        queue.close()


if __name__ == "__main__":
    main()

