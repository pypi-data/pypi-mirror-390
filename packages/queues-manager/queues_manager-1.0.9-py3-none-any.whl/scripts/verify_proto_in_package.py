#!/usr/bin/env python3
"""验证 proto 文件是否在包中"""
import zipfile
import sys
from pathlib import Path

def verify_proto_in_wheel(wheel_path):
    """验证 wheel 包中是否包含 proto 文件"""
    print("=" * 60)
    print("验证 proto 文件是否在包中")
    print("=" * 60)
    
    if not Path(wheel_path).exists():
        print(f"❌ 错误: 文件不存在: {wheel_path}")
        return False
    
    with zipfile.ZipFile(wheel_path, 'r') as z:
        files = z.namelist()
        
        # 查找 proto 文件
        proto_files = [f for f in files if '.proto' in f]
        
        print(f"\n找到 {len(proto_files)} 个 proto 文件:")
        for f in proto_files:
            info = z.getinfo(f)
            print(f"  ✓ {f} ({info.file_size} bytes)")
        
        # 检查主要的 proto 文件
        main_proto = 'agent_queues/queue_service.proto'
        if main_proto in files:
            print(f"\n✓ 主要 proto 文件存在: {main_proto}")
            content = z.read(main_proto).decode('utf-8')
            print(f"  - 文件大小: {len(content)} 字符")
            print(f"  - 包含 'service QueueService': {'service QueueService' in content}")
            print(f"  - 前 100 个字符: {content[:100]}...")
            return True
        else:
            print(f"\n❌ 主要 proto 文件不存在: {main_proto}")
            return False

if __name__ == "__main__":
    # 查找最新的 wheel 文件
    dist_dir = Path("dist")
    if dist_dir.exists():
        wheels = sorted(dist_dir.glob("agent_queue-*.whl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if wheels:
            wheel_path = wheels[0]
            print(f"使用最新的 wheel 文件: {wheel_path}\n")
            success = verify_proto_in_wheel(wheel_path)
            sys.exit(0 if success else 1)
        else:
            print("错误: 在 dist 目录中找不到 wheel 文件")
            sys.exit(1)
    else:
        print("错误: dist 目录不存在")
        sys.exit(1)

