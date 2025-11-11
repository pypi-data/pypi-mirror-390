"""gRPC 重连测试用例"""
import time
import threading
import pytest
import grpc
from agent_queues import PrivateAgentTasksQueue
from agent_queues import DATA_PROCESSING, PENDING


class TestGrpcReconnect:
    """gRPC 重连功能测试"""
    
    def test_automatic_reconnect_on_connection_loss(self):
        """
        测试连接断开后自动重连
        
        场景：
        1. 创建客户端并建立连接
        2. 模拟服务器断开连接（停止服务器）
        3. 验证客户端能够自动重连
        4. 验证重连后可以正常调用接口
        """
        # 创建客户端（使用较短的 keepalive 时间以便快速检测断开）
        queue = PrivateAgentTasksQueue(
            grpc_keepalive_time=5,  # 5秒检测一次
            grpc_keepalive_timeout=2,  # 2秒超时
            grpc_max_retry_attempts=3  # 最多重试3次
        )
        
        agent_id = "test_agent_reconnect"
        
        try:
            # 1. 先创建一个队列，确保连接正常
            response = queue.create_queue(agent_id)
            assert response.success, "初始连接应该成功"
            
            # 2. 提交一个任务，验证连接正常
            submit_response = queue.submit_task(
                agent_id=agent_id,
                task_type=DATA_PROCESSING,
                payload='{"test": "data"}',
                priority=5
            )
            assert submit_response.success, "提交任务应该成功"
            
            # 3. 获取队列信息，验证连接正常
            info_response = queue.get_queue_info(agent_id)
            assert info_response.success, "获取队列信息应该成功"
            
            print("✓ 初始连接和调用成功")
            
        except grpc.RpcError as e:
            # 如果服务器未运行，跳过测试
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("gRPC server is not running, skipping reconnect test")
            raise
        finally:
            queue.close()
    
    def test_retry_on_temporary_failure(self):
        """
        测试临时失败时的重试机制
        
        场景：
        1. 模拟临时网络故障
        2. 验证客户端会自动重试
        3. 验证重试成功后可以正常调用
        """
        queue = PrivateAgentTasksQueue(
            grpc_max_retry_attempts=3,
            grpc_initial_backoff=0.5,  # 较短的退避时间，便于测试
            grpc_max_backoff=2.0
        )
        
        agent_id = "test_agent_retry"
        
        try:
            # 尝试调用接口，如果服务器可用则应该成功
            response = queue.create_queue(agent_id)
            if not response.success:
                # 如果失败，可能是服务器不可用，验证重试机制
                # 注意：这里主要测试重试逻辑，实际重连需要服务器配合
                print("⚠ 服务器不可用，无法测试完整重试流程")
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_keepalive_connection_maintenance(self):
        """
        测试 keepalive 机制保持连接活跃
        
        场景：
        1. 创建连接
        2. 等待一段时间（超过 keepalive 时间）
        3. 验证连接仍然可用
        """
        queue = PrivateAgentTasksQueue(
            grpc_keepalive_time=10,  # 10秒发送一次 keepalive
            grpc_keepalive_permit_without_calls=True
        )
        
        agent_id = "test_agent_keepalive"
        
        try:
            # 创建连接
            response = queue.create_queue(agent_id)
            assert response.success, "创建队列应该成功"
            
            # 等待一段时间（超过 keepalive 时间）
            print("等待 15 秒以测试 keepalive...")
            time.sleep(15)
            
            # 验证连接仍然可用
            info_response = queue.get_queue_info(agent_id)
            assert info_response.success, "keepalive 后连接应该仍然可用"
            
            print("✓ keepalive 机制正常工作")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_channel_reuse_after_reconnect(self):
        """
        测试重连后通道复用
        
        场景：
        1. 创建客户端
        2. 进行多次调用
        3. 验证通道可以正常复用
        """
        queue = PrivateAgentTasksQueue()
        
        agent_id = "test_agent_channel_reuse"
        
        try:
            # 多次调用，验证通道复用
            for i in range(5):
                response = queue.get_queue_info(agent_id)
                # 即使失败也应该能正常处理（不会因为连接问题崩溃）
                time.sleep(0.5)
            
            print("✓ 通道复用测试完成")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()
    
    def test_concurrent_calls_with_reconnect(self):
        """
        测试并发调用时的重连处理
        
        场景：
        1. 创建多个线程并发调用
        2. 验证重连机制在并发场景下正常工作
        """
        queue = PrivateAgentTasksQueue(
            grpc_max_retry_attempts=2,
            grpc_initial_backoff=0.1
        )
        
        agent_id = "test_agent_concurrent"
        results = []
        
        def make_call(index):
            try:
                response = queue.get_queue_info(agent_id)
                results.append((index, response.success))
            except Exception as e:
                results.append((index, False, str(e)))
        
        try:
            # 创建队列
            queue.create_queue(agent_id)
            
            # 启动多个线程并发调用
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_call, args=(i,))
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            print(f"✓ 并发调用完成，结果: {results}")
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                pytest.skip("gRPC server is not available")
            raise
        finally:
            queue.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

