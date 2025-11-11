"""
高级使用示例 - 演示 Agent Queue 的高级功能

包括：
- 批量提交任务
- 任务重试
- 任务取消
- 错误处理
- 幂等性
- 任务处理循环
"""
import json
import time
import random
from agent_queues import PrivateAgentTasksQueue
from agent_queues import (
    DATA_PROCESSING, IMAGE_PROCESSING, TEXT_ANALYSIS, CUSTOM,
    PENDING, PROCESSING, COMPLETED, FAILED,
    SubmitTaskItem
)


def main():
    # 创建客户端
    queue = PrivateAgentTasksQueue(
        grpc_host="localhost",
        grpc_port=50051
    )
    
    agent_id = "demo_agent_002"
    
    try:
        # 1. 创建队列
        print("=" * 60)
        print("高级功能示例")
        print("=" * 60)
        
        create_response = queue.create_queue(agent_id)
        if not create_response.success:
            print(f"队列创建失败: {create_response.message}")
            return
        
        print(f"✓ 队列创建成功: {agent_id}\n")
        
        # 2. 批量提交任务
        print("2. 批量提交任务")
        print("-" * 60)
        
        tasks = [
            SubmitTaskItem(
                type=DATA_PROCESSING,
                payload=json.dumps({"id": i, "data": f"task_{i}", "action": "process"}),
                priority=5 + i if i < 3 else 5  # 前3个任务优先级递增
            )
            for i in range(5)
        ]
        
        batch_response = queue.batch_submit_tasks(agent_id, tasks)
        if batch_response.success:
            print(f"✓ 成功提交 {batch_response.success_count} 个任务")
            print(f"  任务ID列表: {batch_response.task_ids[:3]}...")  # 只显示前3个
        else:
            print(f"✗ 批量提交失败: {batch_response.message}")
        
        # 3. 任务处理循环
        print("\n3. 任务处理循环")
        print("-" * 60)
        
        processed_count = 0
        max_tasks = 3  # 最多处理3个任务
        
        while processed_count < max_tasks:
            # 获取任务
            get_response = queue.get_task(agent_id, timeout=2)
            
            if not get_response.success or not get_response.task.task_id:
                print("  队列中没有更多任务")
                break
            
            task = get_response.task
            print(f"  处理任务: {task.task_id}")
            
            # 模拟任务处理
            try:
                # 模拟处理时间
                time.sleep(0.5)
                
                # 随机决定成功或失败（用于演示）
                if random.random() > 0.3:  # 70% 成功率
                    # 任务成功
                    result = json.dumps({
                        "result": "success",
                        "processed_at": int(time.time()),
                        "task_id": task.task_id
                    })
                    queue.update_task_status(
                        task_id=task.task_id,
                        agent_id=agent_id,
                        status=COMPLETED,
                        result=result
                    )
                    print(f"    ✓ 任务完成: {task.task_id}")
                else:
                    # 任务失败
                    queue.update_task_status(
                        task_id=task.task_id,
                        agent_id=agent_id,
                        status=FAILED,
                        error_message="模拟处理失败"
                    )
                    print(f"    ✗ 任务失败: {task.task_id}")
                
                processed_count += 1
                
            except Exception as e:
                print(f"    ✗ 处理异常: {e}")
                queue.update_task_status(
                    task_id=task.task_id,
                    agent_id=agent_id,
                    status=FAILED,
                    error_message=str(e)
                )
        
        # 4. 查看失败的任务
        print("\n4. 查看失败的任务")
        print("-" * 60)
        
        failed_response = queue.get_tasks_by_status(agent_id, status=FAILED, limit=10)
        if failed_response.success and failed_response.total > 0:
            print(f"找到 {failed_response.total} 个失败的任务")
            for task in failed_response.tasks:
                print(f"  - {task.task_id}: {task.error_message}")
                
                # 5. 重试失败的任务
                print(f"\n5. 重试失败的任务: {task.task_id}")
                print("-" * 60)
                
                retry_response = queue.retry_task(task.task_id, agent_id)
                if retry_response.success:
                    print(f"✓ 重试成功，新任务ID: {retry_response.new_task_id}")
                else:
                    print(f"✗ 重试失败: {retry_response.message}")
        else:
            print("没有失败的任务")
        
        # 6. 使用自定义任务类型
        print("\n6. 使用自定义任务类型")
        print("-" * 60)
        
        custom_payload = json.dumps({
            "custom_type": "my_custom_task",
            "data": "custom data",
            "action": "custom_action"
        })
        
        custom_response = queue.submit_task(
            agent_id=agent_id,
            task_type=CUSTOM,
            payload=custom_payload,
            custom_task_type="my_custom_task"
        )
        
        if custom_response.success:
            print(f"✓ 自定义任务提交成功: {custom_response.task_id}")
        else:
            print(f"✗ 自定义任务提交失败: {custom_response.message}")
        
        # 7. 任务取消
        print("\n7. 任务取消")
        print("-" * 60)
        
        # 提交一个任务用于取消
        cancel_task_response = queue.submit_task(
            agent_id=agent_id,
            task_type=DATA_PROCESSING,
            payload=json.dumps({"action": "cancel_me"})
        )
        
        if cancel_task_response.success:
            cancel_task_id = cancel_task_response.task_id
            print(f"提交任务用于取消: {cancel_task_id}")
            
            # 取消任务
            cancel_response = queue.cancel_task(
                task_id=cancel_task_id,
                agent_id=agent_id,
                reason="演示任务取消功能"
            )
            
            if cancel_response.success:
                print(f"✓ 任务取消成功: {cancel_task_id}")
            else:
                print(f"✗ 任务取消失败: {cancel_response.message}")
        
        # 8. 批量删除任务
        print("\n8. 批量删除任务")
        print("-" * 60)
        
        # 获取一些已完成的任务
        completed_response = queue.get_tasks_by_status(agent_id, status=COMPLETED, limit=5)
        if completed_response.success and completed_response.total > 0:
            task_ids = [task.task_id for task in completed_response.tasks[:3]]  # 只删除前3个
            print(f"准备删除 {len(task_ids)} 个已完成的任务")
            
            delete_response = queue.batch_delete_tasks(agent_id, task_ids)
            if delete_response.success:
                print(f"✓ 成功删除 {delete_response.deleted_count} 个任务")
            else:
                print(f"✗ 批量删除失败: {delete_response.message}")
        else:
            print("没有已完成的任务可删除")
        
        # 9. 获取最终统计信息
        print("\n9. 最终统计信息")
        print("-" * 60)
        
        final_stats = queue.get_task_stats(agent_id)
        if final_stats.success:
            print(f"总任务数: {final_stats.total_count}")
            print(f"待处理: {final_stats.pending_count}")
            print(f"处理中: {final_stats.processing_count}")
            print(f"已完成: {final_stats.completed_count}")
            print(f"失败: {final_stats.failed_count}")
        
        # 10. 清空队列（可选）
        print("\n10. 清空队列（演示）")
        print("-" * 60)
        print("注意：实际使用中请谨慎使用清空操作")
        # 取消注释以下代码来清空队列
        # clear_response = queue.clear_queue(agent_id, status=0, confirm=True)
        # if clear_response.success:
        #     print(f"✓ 已清空 {clear_response.cleared_count} 个任务")
        
        print("\n" + "=" * 60)
        print("高级功能示例执行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        queue.close()


if __name__ == "__main__":
    main()

