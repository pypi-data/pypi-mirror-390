"""发布脚本 - 构建并上传包到 PyPI"""
import subprocess
import sys
import shutil
from pathlib import Path
import os

# 尝试加载 .env 文件（如果存在且安装了 python-dotenv）
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Loaded environment variables from {env_file}")
except ImportError:
    # python-dotenv 未安装，跳过
    pass

# 尝试加载本地凭证文件（如果存在）
# 上传时会自动从此文件获取 token
_pypi_credentials = None
try:
    credentials_file = Path(__file__).parent / "pypi_credentials.py"
    if credentials_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("pypi_credentials", credentials_file)
        _pypi_credentials = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_pypi_credentials)
        print(f"✓ 已加载 PyPI 凭证文件: {credentials_file}")
        print(f"  上传时将自动从此文件获取 token")
except Exception as e:
    # 凭证文件不存在或加载失败，使用其他方式
    pass


def run_command(cmd, check=True):
    """运行命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result.returncode == 0


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"Removing {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"Removing {path}")
                path.unlink()


def generate_grpc_code():
    """生成 gRPC Python 代码"""
    print("\n" + "=" * 60)
    print("Generating gRPC code from proto files...")
    print("=" * 60)
    
    proto_file = Path("agent_queues") / "queue_service.proto"
    output_dir = Path("agent_queues")
    
    if not proto_file.exists():
        print(f"Error: Proto file not found at {proto_file}")
        return False
    
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
    else:
        print("No existing generated files found, will generate fresh code")
    
    # 检查 grpc_tools 是否可用
    try:
        import grpc_tools.protoc
    except ImportError:
        print("Error: 'grpcio-tools' not found. Install it with:")
        print("  pip install grpcio-tools")
        return False
    
    # 使用绝对路径
    proto_file_abs = proto_file.resolve()
    output_dir_abs = output_dir.resolve()
    
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"--proto_path={proto_file_abs.parent}",
        f"--python_out={output_dir_abs}",
        f"--grpc_python_out={output_dir_abs}",
        str(proto_file_abs.name)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=proto_file_abs.parent, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error generating gRPC code:")
        print(result.stderr)
        return False
    
    # 检查生成的文件
    pb2_file = output_dir / "queue_service_pb2.py"
    pb2_grpc_file = output_dir / "queue_service_pb2_grpc.py"
    
    if not pb2_file.exists() or not pb2_grpc_file.exists():
        print("Error: Generated files not found!")
        print(f"Expected: {pb2_file}, {pb2_grpc_file}")
        return False
    
    # 修复生成的 gRPC 代码中的导入语句（使用相对导入）
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
        try:
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
        except ImportError:
            print("Warning: grpc module not found, skipping version check")
    
    print("✓ gRPC code generated successfully!")
    print(f"  - {pb2_file}")
    print(f"  - {pb2_grpc_file}")
    return True


def build_package():
    """构建包"""
    print("\n" + "=" * 60)
    print("Building package...")
    print("=" * 60)
    
    # 检查 build 是否已安装
    try:
        import build
    except ImportError:
        print("Error: 'build' package not found. Install it with:")
        print("  pip install build")
        return False
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 构建包
    if not run_command([sys.executable, "-m", "build"]):
        print("Build failed!")
        return False
    
    print("\n✓ Build successful!")
    return True


def upload_to_pypi(test=True, client_only=False):
    """上传到 PyPI"""
    print("\n" + "=" * 60)
    print(f"Uploading to {'Test PyPI' if test else 'PyPI'}...")
    print("=" * 60)
    
    # 检查 twine 是否已安装
    try:
        import twine
    except ImportError:
        print("Error: 'twine' package not found. Install it with:")
        print("  pip install twine")
        return False
    
    # 检查 dist 目录
    dist_dir = Path("dist")
    if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
        print("Error: No distribution files found. Run build first.")
        return False
    
    # 如果指定客户端模式，只上传客户端包
    wheel_files = list(dist_dir.glob("*.whl"))
    if client_only:
        # 客户端包名称应该包含 "queues_manager" 或 "queues-manager"，不包含 "server"
        client_wheels = [
            w for w in wheel_files 
            if ("queues_manager" in w.name or "queues-manager" in w.name) 
            and "server" not in w.name.lower()
        ]
        if not client_wheels:
            print("⚠ 警告: 未找到客户端包文件")
            print(f"  dist 目录中的文件: {[w.name for w in wheel_files]}")
            print("  请确保使用 --client-only 模式构建")
            return False
        upload_files = [str(w) for w in client_wheels]
        print(f"✓ 找到客户端包: {[w.name for w in client_wheels]}")
    else:
        upload_files = [str(w) for w in wheel_files]
    
    # 上传
    repo_url = "https://test.pypi.org/legacy/" if test else "https://upload.pypi.org/legacy/"
    
    # 认证优先级：1. 凭证文件（默认） 2. 环境变量（可选覆盖） 3. .pypirc 文件
    # 默认使用 scripts/pypi_credentials.py 中的配置，环境变量可以覆盖
    
    username = None
    password = None
    
    # 1. 默认使用凭证文件（scripts/pypi_credentials.py）
    if _pypi_credentials:
        if test:
            username = getattr(_pypi_credentials, "TEST_PYPI_USERNAME", None) or getattr(_pypi_credentials, "PYPI_USERNAME", None)
            password = getattr(_pypi_credentials, "TEST_PYPI_PASSWORD", None) or getattr(_pypi_credentials, "PYPI_PASSWORD", None)
        else:
            username = getattr(_pypi_credentials, "PYPI_USERNAME", None)
            password = getattr(_pypi_credentials, "PYPI_PASSWORD", None)
    
    # 2. 环境变量可以覆盖凭证文件（可选）
    username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
    password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
    
    # 如果设置了环境变量，则使用环境变量（覆盖凭证文件）
    env_username = os.getenv(username_key) or os.getenv("TWINE_USERNAME")
    env_password = os.getenv(password_key) or os.getenv("TWINE_PASSWORD")
    
    if env_username:
        username = env_username
    if env_password:
        password = env_password
    
    has_env = username and password
    
    # 检查是否有 .pypirc 文件（备用方式）
    pypirc_path = Path.home() / ".pypirc"
    has_pypirc = pypirc_path.exists()
    
    if not has_env and not has_pypirc:
        print("\n⚠ 警告: 未找到认证配置")
        print("请选择以下方式之一配置认证：")
        print("\n【方式 1】使用凭证文件（默认推荐）：")
        print("  编辑 scripts/pypi_credentials.py，填入你的 PyPI 凭证")
        print("  PYPI_USERNAME = \"__token__\"")
        print("  PYPI_PASSWORD = \"pypi-your-api-token\"")
        print("\n【方式 2】使用环境变量（可选，会覆盖凭证文件）：")
        username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
        password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
        print(f"  export {username_key}=__token__")
        print(f"  export {password_key}=pypi-your-api-token")
        print("\n【方式 3】使用 .pypirc 文件：")
        print("  创建 ~/.pypirc 文件（Windows: %USERPROFILE%\\.pypirc）")
        print("\n获取 API token: https://pypi.org/manage/account/token/")
        return False
    
    # 构建上传命令
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--repository-url", repo_url,
    ] + upload_files
    
    # 如果使用凭证文件或环境变量，需要设置环境变量供 twine 使用
    if has_env:
        # 临时设置环境变量供 twine 使用
        env = os.environ.copy()
        username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
        password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
        env[username_key] = username
        env[password_key] = password
        
        # 显示使用的认证方式
        if env_username or env_password:
            print("✓ 使用环境变量进行认证（覆盖凭证文件）")
        elif _pypi_credentials:
            print("✓ 自动从 scripts/pypi_credentials.py 获取 token 进行认证")
        else:
            print("✓ 使用已配置的认证信息")
        
        # 使用修改后的环境变量运行命令
        import subprocess
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, env=env, check=False)
        if result.returncode != 0:
            print(f"\nUpload to {'Test PyPI' if test else 'PyPI'} failed!")
            print("\n请检查：")
            print("  1. PyPI 账户和 API token 是否正确")
            print(f"  2. 凭证配置是否正确（检查 scripts/pypi_credentials.py 或环境变量）")
            print("\n获取 API token: https://pypi.org/manage/account/token/")
            return False
        print(f"\n✓ Upload to {'Test PyPI' if test else 'PyPI'} successful!")
        return True
    
    # 如果使用 .pypirc，twine 会自动读取
    # 不需要在命令行中传递凭证（更安全）
    if not run_command(cmd, check=False):
        print(f"\nUpload to {'Test PyPI' if test else 'PyPI'} failed!")
        print("\n请检查：")
        print("  1. PyPI 账户和 API token 是否正确")
        print("  2. ~/.pypirc 文件配置是否正确")
        print("\n获取 API token: https://pypi.org/manage/account/token/")
        return False
    
    print(f"\n✓ Upload to {'Test PyPI' if test else 'PyPI'} successful!")
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build and publish package to PyPI")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Upload to Test PyPI instead of PyPI"
    )
    parser.add_argument(
        "--build-only",
        action="store_true",
        help="Only build the package, don't upload"
    )
    parser.add_argument(
        "--upload-only",
        action="store_true",
        help="Only upload, skip build (assumes dist/ already exists)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directories before building"
    )
    parser.add_argument(
        "--client-only",
        action="store_true",
        help="Build and upload client package only (proto definitions, no server code)"
    )
    
    args = parser.parse_args()
    
    # 如果指定了客户端模式，使用客户端配置
    if args.client_only:
        client_config = Path("pyproject.client.toml")
        if not client_config.exists():
            print("Error: pyproject.client.toml not found!")
            sys.exit(1)
        
        # 备份原始配置
        original_config = Path("pyproject.toml")
        backup_config = Path("pyproject.toml.backup")
        if original_config.exists():
            shutil.copy(original_config, backup_config)
            print(f"Backed up pyproject.toml to pyproject.toml.backup")
        
        # 使用客户端配置
        shutil.copy(client_config, original_config)
        print("Using client-only configuration (pyproject.client.toml)")
        
        try:
            if args.clean:
                clean_build_dirs()
            
            if not args.upload_only:
                # 在构建客户端包之前，先生成 gRPC 代码
                if not generate_grpc_code():
                    print("Error: Failed to generate gRPC code!")
                    sys.exit(1)
                
                if not build_package():
                    sys.exit(1)
                
                # 验证包内容
                print("\n" + "=" * 60)
                print("Verifying package contents...")
                print("=" * 60)
                wheel_files = list(Path("dist").glob("*.whl"))
                if wheel_files:
                    verify_script = Path("scripts/verify_package.py")
                    if verify_script.exists():
                        result = subprocess.run(
                            [sys.executable, str(verify_script), str(wheel_files[0])],
                            capture_output=True,
                            text=True
                        )
                        print(result.stdout)
                        if result.returncode != 0:
                            print("Warning: Package verification found issues!")
                            print(result.stderr)
                    else:
                        print("Note: verify_package.py not found, skipping verification")
            
            if not args.build_only:
                if not upload_to_pypi(test=args.test, client_only=True):
                    sys.exit(1)
        finally:
            # 恢复原始配置
            if backup_config.exists():
                shutil.copy(backup_config, original_config)
                backup_config.unlink()
                print("Restored original pyproject.toml")
    else:
        # 正常模式（包含服务端）- 但默认只上传客户端包
        print("⚠ 警告: 未指定 --client-only，但服务端包不应上传到 PyPI")
        print("  使用 --client-only 参数上传客户端包")
        print("  服务端代码应通过 Docker 或其他方式部署，不上传到 PyPI")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()

