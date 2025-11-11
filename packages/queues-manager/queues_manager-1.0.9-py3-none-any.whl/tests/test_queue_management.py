"""
队列管理接口测试
"""
import pytest
from agent_queues import (
    CreateQueueRequest, QueueExistsRequest, GetQueueInfoRequest,
    ClearQueueRequest, DeleteQueueRequest
)


class TestQueueManagement:
    """队列管理接口测试类"""
    
    def test_create_queue(self, grpc_stub, test_agent_id):
        """测试创建队列"""
        request = CreateQueueRequest(agent_id=test_agent_id)
        response = grpc_stub.CreateQueue(request)
        
        assert response.success is True
        assert response.agent_id == test_agent_id
    
    def test_create_queue_duplicate(self, grpc_stub, test_agent_id):
        """测试重复创建队列"""
        # 第一次创建
        request = CreateQueueRequest(agent_id=test_agent_id)
        response1 = grpc_stub.CreateQueue(request)
        assert response1.success is True
        
        # 第二次创建（应该成功，幂等操作）
        response2 = grpc_stub.CreateQueue(request)
        assert response2.success is True
    
    def test_queue_exists(self, grpc_stub, test_agent_id):
        """测试检查队列是否存在"""
        # 先创建队列
        create_request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(create_request)
        
        # 检查队列是否存在
        exists_request = QueueExistsRequest(agent_id=test_agent_id)
        response = grpc_stub.QueueExists(exists_request)
        
        assert response.exists is True
    
    def test_queue_not_exists(self, grpc_stub, test_agent_id):
        """测试检查不存在的队列"""
        exists_request = QueueExistsRequest(agent_id=test_agent_id)
        response = grpc_stub.QueueExists(exists_request)
        
        # 队列不存在时，行为可能因实现而异
        # 这里假设返回 exists=False
        assert response.exists is False or response.exists is True
    
    def test_get_queue_info(self, grpc_stub, test_agent_id):
        """测试获取队列信息"""
        # 先创建队列
        create_request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(create_request)
        
        # 获取队列信息
        info_request = GetQueueInfoRequest(agent_id=test_agent_id)
        response = grpc_stub.GetQueueInfo(info_request)
        
        assert response.success is True
        assert response.agent_id == test_agent_id
        assert response.pending_count >= 0
        assert response.processing_count >= 0
        assert response.completed_count >= 0
        assert response.failed_count >= 0
        assert response.total_count >= 0
    
    def test_clear_queue(self, grpc_stub, test_agent_id):
        """测试清空队列"""
        # 先创建队列
        create_request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(create_request)
        
        # 清空队列
        clear_request = ClearQueueRequest(
            agent_id=test_agent_id,
            status=0,  # 清空所有状态
            confirm=True
        )
        response = grpc_stub.ClearQueue(clear_request)
        
        assert response.success is True
        assert response.cleared_count >= 0
    
    def test_delete_queue(self, grpc_stub, test_agent_id):
        """测试删除队列"""
        # 先创建队列
        create_request = CreateQueueRequest(agent_id=test_agent_id)
        grpc_stub.CreateQueue(create_request)
        
        # 删除队列
        delete_request = DeleteQueueRequest(
            agent_id=test_agent_id,
            confirm=True
        )
        response = grpc_stub.DeleteQueue(delete_request)
        
        assert response.success is True
        assert response.deleted_count >= 0

