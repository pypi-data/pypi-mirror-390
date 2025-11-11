"""
Pytest 配置和共享 fixtures
"""
import pytest
import redis
from agent_queues import PrivateAgentTasksQueue
from agent_queues import QueueServiceStub
import grpc


@pytest.fixture(scope="session")
def redis_client():
    """创建 Redis 客户端"""
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    
    # 测试连接
    try:
        client.ping()
    except redis.ConnectionError:
        pytest.skip("Redis is not available")
    
    yield client
    
    # 清理：关闭连接
    client.close()


@pytest.fixture(scope="session")
def grpc_channel():
    """创建 gRPC 通道"""
    channel = grpc.insecure_channel('localhost:50051')
    
    # 测试连接
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        pytest.skip("gRPC server is not available")
    
    yield channel
    
    # 清理：关闭通道
    channel.close()


@pytest.fixture
def grpc_stub(grpc_channel):
    """创建 gRPC stub"""
    from agent_queues import QueueServiceStub
    return QueueServiceStub(grpc_channel)


@pytest.fixture
def queue_client():
    """创建队列客户端"""
    client = PrivateAgentTasksQueue(
        grpc_host="localhost",
        grpc_port=50051
    )
    yield client
    client.close()


@pytest.fixture
def test_agent_id():
    """生成测试用的 agent_id"""
    import uuid
    return f"test_agent_{uuid.uuid4().hex[:8]}"


@pytest.fixture(autouse=True)
def cleanup_queue(redis_client, test_agent_id):
    """测试后清理队列数据"""
    yield
    
    # 清理测试数据
    try:
        # 删除队列相关的所有 key
        pattern = f"*{test_agent_id}*"
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass  # 忽略清理错误

