"""验证打包后的包内容是否正确"""
import sys
import zipfile
from pathlib import Path

def verify_package(wheel_path):
    """验证 wheel 包的内容"""
    print("=" * 60)
    print("验证打包内容")
    print("=" * 60)
    print(f"\n检查文件: {wheel_path}\n")
    
    if not Path(wheel_path).exists():
        print(f"❌ 错误: 文件不存在: {wheel_path}")
        return False
    
    required_files = {
        # 核心文件
        'agent_queues/__init__.py': '客户端主模块（导出所有接口定义）',
        'agent_queues/agent_queue.py': 'PrivateAgentTasksQueue 类',
        'agent_queues/queue_service.proto': 'Proto 接口定义文件（agent 需要查看）',
        'agent_queues/queue_service_pb2.py': '生成的 gRPC 消息代码（接口定义）',
        'agent_queues/queue_service_pb2_grpc.py': '生成的 gRPC 服务代码（接口定义）',
        
        # 配置模块
        'agent_queues/settings.py': '配置设置类',
        'agent_queues/config/grpc.yaml': '默认配置文件',
        
        # 拦截器模块
        'agent_queues/retry_interceptor.py': '重试拦截器',
        
        # 其他客户端模块（agent 可能需要查看）
        'agent_queues/agent_queue_manager.py': '队列管理器类',
        'agent_queues/agent_queue_report.py': '队列报告客户端类',
    }
    
    with zipfile.ZipFile(wheel_path, 'r') as z:
        files = z.namelist()
        
        print("检查必需文件:")
        print("-" * 60)
        all_found = True
        for file_path, description in required_files.items():
            # 在 wheel 中，文件可能在 .data/ 目录下
            found = any(file_path in f for f in files)
            status = "✓" if found else "✗"
            print(f"  {status} {file_path:<40} {description}")
            if not found:
                all_found = False
                # 显示相似的文件名
                similar = [f for f in files if file_path.split('/')[-1] in f]
                if similar:
                    print(f"      相似文件: {similar[:3]}")
        
        print("\n" + "-" * 60)
        if all_found:
            print("✓ 所有必需文件都已包含在包中")
        else:
            print("❌ 部分必需文件缺失，请检查打包配置")
        
        # 显示所有 client 相关文件
        client_files = sorted([f for f in files if 'agent_queues/' in f])
        print(f"\n包中包含的 client 文件 ({len(client_files)} 个):")
        for f in client_files:
            print(f"  {f}")
        
        return all_found

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 尝试查找最新的 wheel 文件
        dist_dir = Path("dist")
        if dist_dir.exists():
            wheels = sorted(dist_dir.glob("*.whl"), key=lambda p: p.stat().st_mtime, reverse=True)
            if wheels:
                wheel_path = wheels[0]
                print(f"自动使用最新的 wheel 文件: {wheel_path}\n")
            else:
                print("用法: python scripts/verify_package.py <wheel_file>")
                print("示例: python scripts/verify_package.py dist/agent_queue-0.1.2-py3-none-any.whl")
                sys.exit(1)
        else:
            print("用法: python scripts/verify_package.py <wheel_file>")
            sys.exit(1)
    else:
        wheel_path = sys.argv[1]
    
    success = verify_package(wheel_path)
    sys.exit(0 if success else 1)

