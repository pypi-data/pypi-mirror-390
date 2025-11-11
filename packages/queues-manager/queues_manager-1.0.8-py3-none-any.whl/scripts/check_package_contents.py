"""检查打包后的包内容"""
import zipfile
import sys
from pathlib import Path

def check_wheel_contents(wheel_path):
    """检查 wheel 包的内容"""
    print(f"检查 wheel 包: {wheel_path}")
    print("=" * 60)
    
    with zipfile.ZipFile(wheel_path, 'r') as z:
        files = sorted(z.namelist())
        
        # 过滤出 client 相关的文件
        client_files = [f for f in files if f.startswith('agent_queues/')]
        
        print(f"\n找到 {len(client_files)} 个 agent_queues 相关文件:\n")
        for f in client_files:
            print(f"  {f}")
        
        # 检查关键文件
        key_files = [
            'agent_queues/__init__.py',
            'agent_queues/agent_queue.py',
            'agent_queues/queue_service.proto',
            'agent_queues/queue_service_pb2.py',
            'agent_queues/queue_service_pb2_grpc.py',
            'agent_queues/settings.py',
            'agent_queues/config/grpc.yaml',
        ]
        
        print("\n关键文件检查:")
        print("-" * 60)
        for key_file in key_files:
            # wheel 包中的路径格式是 package/... 或 .data/...
            found = any(key_file in f for f in files)
            status = "✓" if found else "✗"
            print(f"  {status} {key_file}")
        
        # 检查是否有 .data 目录（数据文件）
        data_files = [f for f in files if '.data/' in f]
        if data_files:
            print(f"\n数据文件 ({len(data_files)} 个):")
            for f in data_files[:10]:  # 只显示前10个
                print(f"  {f}")
            if len(data_files) > 10:
                print(f"  ... 还有 {len(data_files) - 10} 个文件")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/check_package_contents.py <wheel_file>")
        print("示例: python scripts/check_package_contents.py dist/agent_queue-0.1.2-py3-none-any.whl")
        sys.exit(1)
    
    wheel_path = Path(sys.argv[1])
    if not wheel_path.exists():
        print(f"错误: 文件不存在: {wheel_path}")
        sys.exit(1)
    
    check_wheel_contents(wheel_path)

