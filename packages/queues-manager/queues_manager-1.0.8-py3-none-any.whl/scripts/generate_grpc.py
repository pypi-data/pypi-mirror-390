"""生成 gRPC Python 代码的脚本"""
import subprocess
import sys
from pathlib import Path

def generate_grpc_code():
    """生成 gRPC Python 代码"""
    proto_file = Path(__file__).parent.parent / "agent_queues" / "queue_service.proto"
    output_dir = Path(__file__).parent.parent / "agent_queues"
    
    if not proto_file.exists():
        print(f"Error: Proto file not found at {proto_file}")
        sys.exit(1)
    
    # 检查并删除已存在的生成文件，确保每次生成最新代码
    generated_files = [
        output_dir / "queue_service_pb2.py",
        output_dir / "queue_service_pb2_grpc.py",
        output_dir / "queue_service_pb2.pyi",  # 类型存根文件（如果存在）
    ]
    
    deleted_files = []
    for file_path in generated_files:
        if file_path.exists():
            file_path.unlink()
            deleted_files.append(file_path.name)
    
    if deleted_files:
        print(f"Cleaned up existing generated files: {', '.join(deleted_files)}")
    
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={proto_file.parent}",
        f"--python_out={output_dir}",
        f"--grpc_python_out={output_dir}",
        str(proto_file.name)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=proto_file.parent, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error generating gRPC code:")
        print(result.stderr)
        sys.exit(1)
    
    print("gRPC code generated successfully!")
    print(f"Output directory: {output_dir}")
    
    # 修复生成的 gRPC 代码中的导入语句（使用相对导入）
    pb2_grpc_file = output_dir / "queue_service_pb2_grpc.py"
    if pb2_grpc_file.exists():
        print("Fixing import statements in queue_service_pb2_grpc.py...")
        content = pb2_grpc_file.read_text(encoding='utf-8')
        
        # 替换绝对导入为相对导入（带 fallback）
        old_import = "import queue_service_pb2 as queue__service__pb2"
        new_import = """try:
    from . import queue_service_pb2 as queue__service__pb2
except ImportError:
    import queue_service_pb2 as queue__service__pb2"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            pb2_grpc_file.write_text(content, encoding='utf-8')
            print("✓ Import statements fixed")
        
        # 确保版本号与当前 grpcio 版本兼容
        import grpc
        current_version = grpc.__version__
        # 提取主版本号（如 1.74.0 -> 1.74.0）
        version_parts = current_version.split('.')
        compatible_version = '.'.join(version_parts[:2]) + '.0' if len(version_parts) >= 2 else current_version
        
        # 更新版本号
        if f"GRPC_GENERATED_VERSION = '{compatible_version}'" not in content:
            import re
            content = re.sub(
                r"GRPC_GENERATED_VERSION = '[^']+'",
                f"GRPC_GENERATED_VERSION = '{compatible_version}'",
                content
            )
            pb2_grpc_file.write_text(content, encoding='utf-8')
            print(f"✓ Version updated to {compatible_version} (compatible with grpcio {current_version})")

if __name__ == "__main__":
    generate_grpc_code()

