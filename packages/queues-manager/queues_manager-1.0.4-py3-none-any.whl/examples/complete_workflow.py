"""
完整工作流示例 - 演示一个完整的任务处理工作流

场景：模拟一个数据处理 Agent，从队列中获取任务，处理任务，更新状态
"""
import json
import time
import threading
from agent_queues import PrivateAgentTasksQueue
from agent_queues import (
    DATA_PROCESSING, IMAGE_PROCESSING, TEXT_ANALYSIS,
    PENDING, PROCESSING, COMPLETED, FAILED
)


class TaskProcessor:
    """任务处理器 - 模拟 Agent 处理任务"""
    
    def __init__(self, agent_id: str, queue: PrivateAgentTasksQueue):
        self.agent_id = agent_id
        self.queue = queue
        self.running = False
        self.processed_count = 0
        self.failed_count = 0
    
    def process_task(self, task_payload: str):
        """
        处理任务
        
        Returns:
            tuple: (success, result_or_error) 处理结果
        """
        try:
            payload = json.loads(task_payload)
            task_type = payload.get("type", "unknown")
            
            # 模拟不同类型的任务处理
            if task_type == "data_processing":
                # 模拟数据处理
                time.sleep(0.5)
                result = {
                    "status": "processed",
                    "output": f"Processed data: {payload.get('data', '')}",
                    "timestamp": int(time.time())
                }
                return True, json.dumps(result)
            
            elif task_type == "image_processing":
                # 模拟图像处理
                time.sleep(1.0)
                result = {
                    "status": "processed",
                    "image_size": payload.get("size", "unknown"),
                    "timestamp": int(time.time())
                }
                return True, json.dumps(result)
            
            elif task_type == "text_analysis":
                # 模拟文本分析
                time.sleep(0.3)
                result = {
                    "status": "analyzed",
                    "word_count": len(payload.get("text", "").split()),
                    "timestamp": int(time.time())
                }
                return True, json.dumps(result)
            
            else:
                return False, f"Unknown task type: {task_type}"
        
        except Exception as e:
            return False, str(e)
    
    def run(self, max_tasks: int = None):
        """运行任务处理循环"""
        self.running = True
        print(f"[处理器] 开始处理任务 (Agent: {self.agent_id})")
        
        while self.running:
            try:
                # 从队列获取任务
                get_response = self.queue.get_task(self.agent_id, timeout=5)
                
                if not get_response.success or not get_response.task.task_id:
                    # 没有任务，继续等待
                    continue
                
                task = get_response.task
                print(f"[处理器] 获取到任务: {task.task_id}")
                
                # 处理任务
                success, result = self.process_task(task.payload)
                
                if success:
                    # 更新任务状态为已完成
                    update_response = self.queue.update_task_status(
                        task_id=task.task_id,
                        agent_id=self.agent_id,
                        status=COMPLETED,
                        result=result
                    )
                    
                    if update_response.success:
                        self.processed_count += 1
                        print(f"[处理器] ✓ 任务完成: {task.task_id} (总计: {self.processed_count})")
                    else:
                        print(f"[处理器] ✗ 状态更新失败: {update_response.message}")
                else:
                    # 更新任务状态为失败
                    update_response = self.queue.update_task_status(
                        task_id=task.task_id,
                        agent_id=self.agent_id,
                        status=FAILED,
                        error_message=result
                    )
                    
                    if update_response.success:
                        self.failed_count += 1
                        print(f"[处理器] ✗ 任务失败: {task.task_id} - {result}")
                
                # 如果设置了最大任务数，检查是否达到
                if max_tasks and (self.processed_count + self.failed_count) >= max_tasks:
                    print(f"[处理器] 达到最大任务数 ({max_tasks})，停止处理")
                    break
            
            except Exception as e:
                print(f"[处理器] ✗ 处理异常: {e}")
                time.sleep(1)  # 发生错误时等待1秒再继续
        
        print(f"[处理器] 处理完成 (成功: {self.processed_count}, 失败: {self.failed_count})")
    
    def stop(self):
        """停止处理"""
        self.running = False


def main():
    print("=" * 60)
    print("完整工作流示例")
    print("=" * 60)
    
    # 创建客户端
    queue = PrivateAgentTasksQueue(
        grpc_host="localhost",
        grpc_port=50051
    )
    
    agent_id = "workflow_agent_001"
    
    try:
        # 1. 创建队列
        print("\n1. 创建队列")
        print("-" * 60)
        create_response = queue.create_queue(agent_id)
        if not create_response.success:
            print(f"队列创建失败: {create_response.message}")
            return
        print(f"✓ 队列创建成功: {agent_id}")
        
        # 2. 提交多个任务
        print("\n2. 提交任务")
        print("-" * 60)
        
        tasks = [
            {
                "type": "data_processing",
                "data": "sample data 1",
                "action": "process"
            },
            {
                "type": "image_processing",
                "size": "1920x1080",
                "format": "jpg"
            },
            {
                "type": "text_analysis",
                "text": "This is a sample text for analysis."
            },
            {
                "type": "data_processing",
                "data": "sample data 2",
                "action": "process"
            },
            {
                "type": "text_analysis",
                "text": "Another text to analyze."
            }
        ]
        
        task_ids = []
        for i, task_data in enumerate(tasks):
            payload = json.dumps(task_data)
            
            # 根据任务类型选择对应的枚举值
            task_type_map = {
                "data_processing": DATA_PROCESSING,
                "image_processing": IMAGE_PROCESSING,
                "text_analysis": TEXT_ANALYSIS
            }
            task_type = task_type_map.get(task_data["type"], DATA_PROCESSING)
            
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=task_type,
                payload=payload,
                priority=7 if task_type == DATA_PROCESSING else 5,  # 数据处理任务优先级更高
                client_request_id=""  # 可选：用于幂等性
            )
            
            if submit_response.success:
                task_ids.append(submit_response.task_id)
                print(f"✓ 任务 {i+1} 提交成功: {submit_response.task_id}")
            else:
                print(f"✗ 任务 {i+1} 提交失败: {submit_response.message}")
        
        print(f"\n总共提交了 {len(task_ids)} 个任务")
        
        # 3. 启动任务处理器（在后台线程中运行）
        print("\n3. 启动任务处理器")
        print("-" * 60)
        
        processor = TaskProcessor(agent_id, queue)
        processor_thread = threading.Thread(target=processor.run, args=(len(task_ids),))
        processor_thread.daemon = True
        processor_thread.start()
        
        # 4. 监控任务处理进度
        print("\n4. 监控任务处理进度")
        print("-" * 60)
        
        max_wait_time = 30  # 最多等待30秒
        start_time = time.time()
        
        while processor_thread.is_alive():
            time.sleep(2)
            
            # 获取队列统计信息
            stats_response = queue.get_task_stats(agent_id)
            if stats_response.success:
                print(f"[监控] 待处理: {stats_response.pending_count}, "
                      f"处理中: {stats_response.processing_count}, "
                      f"已完成: {stats_response.completed_count}, "
                      f"失败: {stats_response.failed_count}")
            
            # 检查超时
            if time.time() - start_time > max_wait_time:
                print(f"[监控] 达到最大等待时间 ({max_wait_time}秒)，停止监控")
                processor.stop()
                break
        
        # 等待处理器完成
        processor_thread.join(timeout=5)
        
        # 5. 查看最终结果
        print("\n5. 最终结果")
        print("-" * 60)
        
        final_stats = queue.get_task_stats(agent_id)
        if final_stats.success:
            print(f"总任务数: {final_stats.total_count}")
            print(f"待处理: {final_stats.pending_count}")
            print(f"处理中: {final_stats.processing_count}")
            print(f"已完成: {final_stats.completed_count}")
            print(f"失败: {final_stats.failed_count}")
        
        # 列出所有已完成的任务
        print("\n6. 已完成的任务详情")
        print("-" * 60)
        
        completed_response = queue.get_tasks_by_status(agent_id, status=COMPLETED, limit=10)
        if completed_response.success and completed_response.total > 0:
            print(f"找到 {completed_response.total} 个已完成的任务:")
            for task in completed_response.tasks:
                print(f"\n  任务ID: {task.task_id}")
                print(f"  类型: {task.task_type}")
                print(f"  结果: {task.result}")
        
        print("\n" + "=" * 60)
        print("完整工作流示例执行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        queue.close()


if __name__ == "__main__":
    main()

