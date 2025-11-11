#!/usr/bin/env python3
"""测试安装后是否可以访问 proto 文件"""
import sys
import os

def test_proto_access():
    """测试 proto 文件访问"""
    print("=" * 60)
    print("测试安装后 proto 文件访问")
    print("=" * 60)
    
    try:
        # 方法1: 使用工具函数
        print("\n方法1: 使用 get_proto_file_path()")
        try:
            from agent_queues import get_proto_file_path, get_proto_content
            proto_path = get_proto_file_path()
            print(f"  ✓ Proto 文件路径: {proto_path}")
            
            if os.path.exists(proto_path):
                print(f"  ✓ 文件存在")
                with open(proto_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  ✓ 文件大小: {len(content)} 字符")
            else:
                print(f"  ❌ 文件不存在")
                return False
        except ImportError as e:
            print(f"  ❌ 导入失败: {e}")
            return False
        
        # 方法2: 直接访问
        print("\n方法2: 直接访问文件")
        try:
            import agent_queues
            client_dir = os.path.dirname(agent_queues.__file__)
            proto_path2 = os.path.join(client_dir, 'queue_service.proto')
            print(f"  ✓ 计算的文件路径: {proto_path2}")
            
            if os.path.exists(proto_path2):
                print(f"  ✓ 文件存在")
                with open(proto_path2, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"  ✓ 文件大小: {len(content)} 字符")
                    print(f"  ✓ 包含 'service QueueService': {'service QueueService' in content}")
            else:
                print(f"  ❌ 文件不存在")
                return False
        except Exception as e:
            print(f"  ❌ 访问失败: {e}")
            return False
        
        # 方法3: 使用 get_proto_content()
        print("\n方法3: 使用 get_proto_content()")
        try:
            proto_content = get_proto_content()
            print(f"  ✓ 成功获取内容")
            print(f"  ✓ 内容大小: {len(proto_content)} 字符")
            print(f"  ✓ 包含 'service QueueService': {'service QueueService' in proto_content}")
        except Exception as e:
            print(f"  ❌ 获取内容失败: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！proto 文件可以正常访问")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_proto_access()
    sys.exit(0 if success else 1)

