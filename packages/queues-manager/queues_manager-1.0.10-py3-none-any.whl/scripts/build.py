#!/usr/bin/env python3
"""
统一的构建和发布脚本

整合了 proto 校验、接口生成、构建、验证、上传等所有功能。

用法:
    # 完整流程：校验 -> 生成 -> 构建 -> 验证 -> 上传
    python scripts/build.py --all

    # 只生成 gRPC 代码
    python scripts/build.py --generate

    # 只构建包
    python scripts/build.py --build

    # 只验证包
    python scripts/build.py --verify

    # 只上传包
    python scripts/build.py --upload

    # 客户端包（只包含客户端代码）
    python scripts/build.py --all --client-only

    # 上传到测试 PyPI
    python scripts/build.py --all --test
"""
import subprocess
import sys
import shutil
import os
import zipfile
import argparse
from pathlib import Path
from typing import Optional, List, Tuple

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# 尝试加载本地凭证文件
_pypi_credentials = None
try:
    credentials_file = Path(__file__).parent / "pypi_credentials.py"
    if credentials_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("pypi_credentials", credentials_file)
        _pypi_credentials = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_pypi_credentials)
except Exception:
    pass


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def run_command(cmd: List[str], check: bool = True, capture_output: bool = False) -> Tuple[bool, str]:
    """运行命令"""
    print(f"运行: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    if capture_output:
        return result.returncode == 0, result.stdout + result.stderr
    return result.returncode == 0, ""


def check_proto_file() -> bool:
    """检查 proto 文件是否存在"""
    print_section("1. 检查 Proto 文件")
    
    proto_file = Path("agent_queues") / "queue_service.proto"
    if not proto_file.exists():
        print(f"❌ 错误: Proto 文件不存在: {proto_file}")
        return False
    
    print(f"✓ Proto 文件存在: {proto_file}")
    
    # 检查文件内容
    content = proto_file.read_text(encoding='utf-8')
    if 'service QueueService' not in content:
        print("⚠ 警告: Proto 文件中未找到 'service QueueService'")
        return False
    
    print(f"✓ Proto 文件内容有效 ({len(content)} 字符)")
    return True


def check_build_config() -> bool:
    """检查构建配置"""
    print_section("2. 检查构建配置")
    
    required_files = [
        "pyproject.toml",
        "README.md",
        "MANIFEST.in",
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    
    print("✓ 所有必需文件存在")
    
    # 检查 pyproject.toml
    try:
        import tomllib  # Python 3.11+
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
    except ImportError:
        try:
            import tomli
            with open("pyproject.toml", "rb") as f:
                config = tomli.load(f)
        except ImportError:
            print("⚠ 警告: 无法解析 pyproject.toml (需要 tomli)")
            return True
    
    project = config.get("project", {})
    if not project.get("name") or not project.get("version"):
        print("❌ pyproject.toml 配置不完整")
        return False
    
    print(f"✓ 项目配置: {project.get('name')} v{project.get('version')}")
    return True


def generate_grpc_code() -> bool:
    """生成 gRPC Python 代码"""
    print_section("3. 生成 gRPC 代码")
    
    proto_file = Path("agent_queues") / "queue_service.proto"
    output_dir = Path("agent_queues")
    
    if not proto_file.exists():
        print(f"❌ 错误: Proto 文件不存在: {proto_file}")
        return False
    
    # 检查 grpc_tools 是否可用
    try:
        import grpc_tools.protoc
    except ImportError:
        print("❌ 错误: 'grpcio-tools' 未安装")
        print("   安装: pip install grpcio-tools")
        return False
    
    # 清理已存在的生成文件（每次生成前都先删除旧的）
    print("清理旧的生成文件...")
    generated_files = [
        output_dir / "queue_service_pb2.py",
        output_dir / "queue_service_pb2_grpc.py",
        output_dir / "queue_service_pb2.pyi",
    ]
    
    deleted_files = []
    for file_path in generated_files:
        if file_path.exists():
            file_path.unlink()
            deleted_files.append(file_path.name)
            print(f"  ✓ 已删除: {file_path.name}")
    
    if deleted_files:
        print(f"✓ 已清理 {len(deleted_files)} 个旧的生成文件")
    else:
        print("✓ 没有找到旧的生成文件，将生成新文件")
    
    # 生成代码
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
    
    success, output = run_command(cmd, check=False, capture_output=True)
    if not success:
        print(f"❌ 生成 gRPC 代码失败:")
        print(output)
        return False
    
    # 检查生成的文件
    pb2_file = output_dir / "queue_service_pb2.py"
    pb2_grpc_file = output_dir / "queue_service_pb2_grpc.py"
    
    if not pb2_file.exists() or not pb2_grpc_file.exists():
        print("❌ 错误: 生成的文件不存在")
        return False
    
    # 修复导入语句
    if pb2_grpc_file.exists():
        print("修复导入语句...")
        content = pb2_grpc_file.read_text(encoding='utf-8')
        
        old_import = "import queue_service_pb2 as queue__service__pb2"
        new_import = """try:
    from . import queue_service_pb2 as queue__service__pb2
except ImportError:
    import queue_service_pb2 as queue__service__pb2"""
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            pb2_grpc_file.write_text(content, encoding='utf-8')
            print("✓ 导入语句已修复")
        
        # 更新版本号
        try:
            import grpc
            current_version = grpc.__version__
            version_parts = current_version.split('.')
            compatible_version = '.'.join(version_parts[:2]) + '.0' if len(version_parts) >= 2 else current_version
            
            if f"GRPC_GENERATED_VERSION = '{compatible_version}'" not in content:
                import re
                content = re.sub(
                    r"GRPC_GENERATED_VERSION = '[^']+'",
                    f"GRPC_GENERATED_VERSION = '{compatible_version}'",
                    content
                )
                pb2_grpc_file.write_text(content, encoding='utf-8')
                print(f"✓ 版本号已更新: {compatible_version}")
        except ImportError:
            pass
    
    print(f"✓ gRPC 代码生成成功")
    print(f"  - {pb2_file}")
    print(f"  - {pb2_grpc_file}")
    return True


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                print(f"删除目录: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"删除文件: {path}")
                path.unlink()
    
    # 特别处理 agent_queue.egg-info（如果存在）
    egg_info = Path("agent_queue.egg-info")
    if egg_info.exists():
        print(f"删除目录: {egg_info}")
        shutil.rmtree(egg_info)


def build_package(client_only: bool = False) -> bool:
    """构建包"""
    print_section("4. 构建包")
    
    # 检查 build 是否已安装
    try:
        import build
    except ImportError:
        print("❌ 错误: 'build' 包未安装")
        print("   安装: pip install build")
        return False
    
    # 构建前先清理旧的构建产物
    print("清理旧的构建产物...")
    clean_build_dirs()
    print("✓ 清理完成")
    
    # 如果指定客户端模式，使用客户端配置
    if client_only:
        client_config = Path("pyproject.client.toml")
        if not client_config.exists():
            print("❌ 错误: pyproject.client.toml 不存在")
            return False
        
        original_config = Path("pyproject.toml")
        backup_config = Path("pyproject.toml.backup")
        
        if original_config.exists():
            shutil.copy(original_config, backup_config)
            print("✓ 已备份 pyproject.toml")
        
        shutil.copy(client_config, original_config)
        print("✓ 使用客户端配置")
        
        try:
            success, _ = run_command([sys.executable, "-m", "build", "--wheel"])
            
            # 恢复原始配置
            if backup_config.exists():
                shutil.copy(backup_config, original_config)
                backup_config.unlink()
                print("✓ 已恢复原始配置")
            
            return success
        except Exception as e:
            # 恢复原始配置
            if backup_config.exists():
                shutil.copy(backup_config, original_config)
                backup_config.unlink()
            raise e
    else:
        return run_command([sys.executable, "-m", "build", "--wheel"])[0]


def verify_package(wheel_path: Optional[Path] = None) -> bool:
    """验证打包后的包内容"""
    print_section("5. 验证包内容")
    
    if wheel_path is None:
        dist_dir = Path("dist")
        if not dist_dir.exists():
            print("❌ 错误: dist 目录不存在")
            return False
        
        wheels = sorted(dist_dir.glob("*.whl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not wheels:
            print("❌ 错误: 未找到 wheel 文件")
            return False
        
        wheel_path = wheels[0]
        print(f"使用最新的 wheel 文件: {wheel_path}")
    
    if not wheel_path.exists():
        print(f"❌ 错误: 文件不存在: {wheel_path}")
        return False
    
    required_files = {
        'agent_queues/__init__.py': '客户端主模块',
        'agent_queues/agent_queue.py': 'PrivateAgentTasksQueue 类',
        'agent_queues/queue_service.proto': 'Proto 定义文件',
        'agent_queues/queue_service_pb2.py': '生成的 gRPC 代码',
        'agent_queues/queue_service_pb2_grpc.py': '生成的 gRPC 服务代码',
        'agent_queues/settings.py': '配置设置类',
        'agent_queues/config/grpc.yaml': '默认配置文件',
        'agent_queues/retry_interceptor.py': '重试拦截器',
    }
    
    with zipfile.ZipFile(wheel_path, 'r') as z:
        files = z.namelist()
        
        print("\n检查必需文件:")
        print("-" * 60)
        all_found = True
        for file_path, description in required_files.items():
            found = any(file_path in f for f in files)
            status = "✓" if found else "✗"
            print(f"  {status} {file_path:<40} {description}")
            if not found:
                all_found = False
        
        # 检查 proto 文件
        proto_files = [f for f in files if '.proto' in f]
        print(f"\n✓ 找到 {len(proto_files)} 个 proto 文件")
        
        # 检查源代码文件
        source_files = [f for f in files if f.endswith('.py') and 'agent_queues/' in f]
        print(f"✓ 找到 {len(source_files)} 个 Python 源代码文件")
    
    if all_found:
        print("\n✓ 所有必需文件都已包含在包中")
        return True
    else:
        print("\n❌ 部分必需文件缺失")
        return False


def upload_to_pypi(test: bool = False) -> bool:
    """上传到 PyPI"""
    print_section("6. 上传到 PyPI")
    
    # 检查 twine 是否已安装
    try:
        import twine
    except ImportError:
        print("❌ 错误: 'twine' 包未安装")
        print("   安装: pip install twine")
        return False
    
    # 检查 dist 目录
    dist_dir = Path("dist")
    if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
        print("❌ 错误: 未找到分发文件，请先构建包")
        return False
    
    repo_url = "https://test.pypi.org/legacy/" if test else "https://upload.pypi.org/legacy/"
    
    # 获取认证信息
    username = None
    password = None
    
    if _pypi_credentials:
        if test:
            username = getattr(_pypi_credentials, "TEST_PYPI_USERNAME", None) or getattr(_pypi_credentials, "PYPI_USERNAME", None)
            password = getattr(_pypi_credentials, "TEST_PYPI_PASSWORD", None) or getattr(_pypi_credentials, "PYPI_PASSWORD", None)
        else:
            username = getattr(_pypi_credentials, "PYPI_USERNAME", None)
            password = getattr(_pypi_credentials, "PYPI_PASSWORD", None)
    
    if not (username and password):
        username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
        password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
        username = username or os.getenv(username_key) or os.getenv("TWINE_USERNAME")
        password = password or os.getenv(password_key) or os.getenv("TWINE_PASSWORD")
    
    has_env = username and password
    pypirc_path = Path.home() / ".pypirc"
    has_pypirc = pypirc_path.exists()
    
    if not has_env and not has_pypirc:
        print("\n⚠ 警告: 未找到认证配置")
        print("请选择以下方式之一配置认证：")
        print("\n【方式 1】使用凭证文件（推荐）：")
        print("  编辑 scripts/pypi_credentials.py，填入你的 PyPI 凭证")
        print("\n【方式 2】使用环境变量：")
        username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
        password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
        print(f"  export {username_key}=__token__")
        print(f"  export {password_key}=pypi-your-api-token")
        print("\n【方式 3】使用 .pypirc 文件：")
        print("  创建 ~/.pypirc 文件")
        print("\n获取 API token: https://pypi.org/manage/account/token/")
        return False
    
    # 构建上传命令
    cmd = [
        sys.executable, "-m", "twine", "upload",
        "--repository-url", repo_url,
        "dist/*"
    ]
    
    if has_env:
        env = os.environ.copy()
        username_key = "TEST_TWINE_USERNAME" if test else "TWINE_USERNAME"
        password_key = "TEST_TWINE_PASSWORD" if test else "TWINE_PASSWORD"
        env[username_key] = username
        env[password_key] = password
        
        print(f"使用环境变量认证: {username_key}")
        result = subprocess.run(cmd, env=env, check=False, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"\n❌ 上传到 {'Test PyPI' if test else 'PyPI'} 失败")
            print(result.stdout)
            print(result.stderr)
            return False
        
        print(f"\n✓ 上传到 {'Test PyPI' if test else 'PyPI'} 成功")
        return True
    
    success, output = run_command(cmd, check=False, capture_output=True)
    if not success:
        print(f"\n❌ 上传到 {'Test PyPI' if test else 'PyPI'} 失败")
        print(output)
        return False
    
    print(f"\n✓ 上传到 {'Test PyPI' if test else 'PyPI'} 成功")
    return True


def test_installed_proto() -> bool:
    """测试安装后是否可以访问 proto 文件"""
    print_section("7. 测试安装后的 Proto 文件访问")
    
    try:
        from agent_queues import get_proto_file_path, get_proto_content
        proto_path = get_proto_file_path()
        
        if not Path(proto_path).exists():
            print(f"❌ 错误: Proto 文件不存在: {proto_path}")
            return False
        
        print(f"✓ Proto 文件路径: {proto_path}")
        
        proto_content = get_proto_content()
        if 'service QueueService' not in proto_content:
            print("❌ 错误: Proto 文件内容无效")
            return False
        
        print(f"✓ Proto 文件内容有效 ({len(proto_content)} 字符)")
        return True
    except ImportError as e:
        print(f"❌ 错误: 导入失败: {e}")
        print("   请先安装包: pip install -e .")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="统一的构建和发布脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（校验 -> 生成 -> 构建 -> 验证 -> 上传）
  python scripts/build.py --all

  # 只生成 gRPC 代码
  python scripts/build.py --generate

  # 只构建包
  python scripts/build.py --build

  # 只验证包
  python scripts/build.py --verify

  # 只上传包
  python scripts/build.py --upload

  # 客户端包（只包含客户端代码）
  python scripts/build.py --all --client-only

  # 上传到测试 PyPI
  python scripts/build.py --all --test

  # 清理构建目录
  python scripts/build.py --clean
        """
    )
    
    parser.add_argument("--all", action="store_true", help="执行完整流程（校验 -> 生成 -> 构建 -> 验证 -> 上传）")
    parser.add_argument("--check", action="store_true", help="检查 proto 文件和构建配置")
    parser.add_argument("--generate", action="store_true", help="生成 gRPC 代码")
    parser.add_argument("--build", action="store_true", help="构建包")
    parser.add_argument("--verify", action="store_true", help="验证包内容")
    parser.add_argument("--upload", action="store_true", help="上传包到 PyPI")
    parser.add_argument("--test-proto", action="store_true", help="测试安装后的 proto 文件访问")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--client-only", action="store_true", help="构建客户端包（只包含客户端代码）")
    parser.add_argument("--test", action="store_true", help="上传到 Test PyPI 而不是 PyPI")
    parser.add_argument("--wheel", type=str, help="指定要验证的 wheel 文件路径")
    
    args = parser.parse_args()
    
    # 如果没有指定任何操作，显示帮助
    if not any([args.all, args.check, args.generate, args.build, args.verify, 
                args.upload, args.test_proto, args.clean]):
        parser.print_help()
        return
    
    # 清理
    if args.clean:
        print_section("清理构建目录")
        clean_build_dirs()
        print("✓ 清理完成")
        return
    
    success = True
    
    # 完整流程
    if args.all:
        success &= check_proto_file()
        success &= check_build_config()
        success &= generate_grpc_code()
        success &= build_package(client_only=args.client_only)
        
        wheel_path = None
        if args.wheel:
            wheel_path = Path(args.wheel)
        
        success &= verify_package(wheel_path)
        
        if success and not args.test:
            print("\n⚠ 注意: 使用 --all 时默认不上传，如需上传请添加 --upload 或使用 --test 上传到测试 PyPI")
        elif success and args.upload:
            success &= upload_to_pypi(test=args.test)
    else:
        # 单独操作
        if args.check:
            success &= check_proto_file()
            success &= check_build_config()
        
        if args.generate:
            success &= generate_grpc_code()
        
        if args.build:
            success &= build_package(client_only=args.client_only)
        
        if args.verify:
            wheel_path = None
            if args.wheel:
                wheel_path = Path(args.wheel)
            success &= verify_package(wheel_path)
        
        if args.upload:
            success &= upload_to_pypi(test=args.test)
        
        if args.test_proto:
            success &= test_installed_proto()
    
    # 总结
    print_section("完成")
    if success:
        print("✓ 所有操作成功完成")
        sys.exit(0)
    else:
        print("❌ 部分操作失败，请检查上面的错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()

