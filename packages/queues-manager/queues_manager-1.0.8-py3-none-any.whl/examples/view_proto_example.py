#!/usr/bin/env python3
"""
查看 proto 接口定义文件的示例

演示如何访问和查看 proto 接口定义文件
"""
import os

def example_1_use_helper_function():
    """示例1: 使用工具函数（推荐）"""
    print("=" * 60)
    print("示例1: 使用工具函数获取 proto 文件")
    print("=" * 60)
    
    from agent_queues import get_proto_file_path, get_proto_content
    
    # 方法1: 获取文件路径
    proto_path = get_proto_file_path()
    print(f"\n✓ Proto 文件路径: {proto_path}")
    
    # 方法2: 直接获取文件内容
    proto_content = get_proto_content()
    print(f"✓ Proto 文件内容长度: {len(proto_content)} 字符")
    print(f"\n前 500 个字符:")
    print("-" * 60)
    print(proto_content[:500])
    print("-" * 60)


def example_2_direct_access():
    """示例2: 直接访问文件"""
    print("\n" + "=" * 60)
    print("示例2: 直接访问 proto 文件")
    print("=" * 60)
    
    import agent_queues
    
    # 获取 agent_queues 包目录
    client_dir = os.path.dirname(agent_queues.__file__)
    proto_path = os.path.join(client_dir, 'queue_service.proto')
    
    print(f"\n✓ Agent Queues 包目录: {client_dir}")
    print(f"✓ Proto 文件路径: {proto_path}")
    
    if os.path.exists(proto_path):
        print("✓ 文件存在")
        with open(proto_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ 文件大小: {len(content)} 字符")
            print(f"✓ 包含服务定义: {'service QueueService' in content}")
    else:
        print("❌ 文件不存在")


def example_3_importlib_resources():
    """示例3: 使用 importlib.resources (Python 3.9+)"""
    print("\n" + "=" * 60)
    print("示例3: 使用 importlib.resources")
    print("=" * 60)
    
    try:
        from importlib import resources
        
        # 读取 proto 文件内容
        proto_content = resources.read_text('agent_queues', 'queue_service.proto')
        print(f"\n✓ 成功读取 proto 文件")
        print(f"✓ 内容长度: {len(proto_content)} 字符")
        print(f"✓ 包含服务定义: {'service QueueService' in proto_content}")
    except ImportError:
        print("\n⚠ 需要 Python 3.9+ 才能使用 importlib.resources")
    except Exception as e:
        print(f"\n❌ 读取失败: {e}")


def example_4_find_in_ide():
    """示例4: 在 IDE 中查找文件"""
    print("\n" + "=" * 60)
    print("示例4: 在 IDE 中查找 proto 文件")
    print("=" * 60)
    
    from agent_queues import get_proto_file_path
    
    proto_path = get_proto_file_path()
    print(f"\n在 IDE 中查找文件:")
    print(f"  1. 使用文件搜索功能（Ctrl+P 或 Cmd+P）")
    print(f"  2. 搜索: queue_service.proto")
    print(f"  3. 或者直接打开路径:")
    print(f"     {proto_path}")
    print(f"\n在 VS Code 中:")
    print(f"  - 按 Ctrl+P，输入: queue_service.proto")
    print(f"  - 或者在资源管理器中导航到: {os.path.dirname(proto_path)}")
    print(f"\n在 PyCharm 中:")
    print(f"  - 按 Ctrl+Shift+N，输入: queue_service.proto")
    print(f"  - 或者使用 Navigate -> File")


def example_5_view_specific_service():
    """示例5: 查看特定服务定义"""
    print("\n" + "=" * 60)
    print("示例5: 查看特定服务定义")
    print("=" * 60)
    
    from agent_queues import get_proto_content
    
    proto_content = get_proto_content()
    
    # 查找服务定义
    if 'service QueueService' in proto_content:
        lines = proto_content.split('\n')
        in_service = False
        service_lines = []
        
        for line in lines:
            if 'service QueueService' in line:
                in_service = True
            if in_service:
                service_lines.append(line)
                if line.strip() == '}':
                    break
        
        print("\nQueueService 服务定义:")
        print("-" * 60)
        print('\n'.join(service_lines))
        print("-" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Proto 接口文件访问示例")
    print("=" * 60)
    
    try:
        example_1_use_helper_function()
        example_2_direct_access()
        example_3_importlib_resources()
        example_4_find_in_ide()
        example_5_view_specific_service()
        
        print("\n" + "=" * 60)
        print("✓ 所有示例执行完成")
        print("=" * 60)
        print("\n提示:")
        print("  - 推荐使用 get_proto_file_path() 和 get_proto_content()")
        print("  - 这些函数会自动找到 proto 文件的位置")
        print("  - 在 IDE 中可以使用文件搜索功能查找 queue_service.proto")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

