"""检查构建配置"""
import sys
from pathlib import Path


def check_files():
    """检查必要的文件是否存在"""
    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "MANIFEST.in",
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✓ All required files present")
        return True


def check_pyproject():
    """检查 pyproject.toml 配置"""
    try:
        import tomli
    except ImportError:
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            print("⚠ Warning: Cannot parse pyproject.toml (install tomli for Python < 3.11)")
            return True
    
    try:
        if sys.version_info >= (3, 11):
            import tomllib
            with open("pyproject.toml", "rb") as f:
                config = tomllib.load(f)
        else:
            import tomli
            with open("pyproject.toml", "rb") as f:
                config = tomli.load(f)
        
        project = config.get("project", {})
        
        issues = []
        
        if not project.get("name"):
            issues.append("Project name is missing")
        if not project.get("description"):
            issues.append("Project description is missing")
        if not project.get("version"):
            issues.append("Project version is missing")
        if not project.get("authors"):
            issues.append("Project authors are missing")
        
        if issues:
            print("❌ Issues in pyproject.toml:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✓ pyproject.toml configuration looks good")
            return True
            
    except Exception as e:
        print(f"⚠ Warning: Could not parse pyproject.toml: {e}")
        return True


def check_package_structure():
    """检查包结构"""
    required_dirs = ["server", "agent_queues"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print("⚠ Warning: Some package directories are missing:")
        for dir_name in missing_dirs:
            print(f"   - {dir_name}")
        return False
    else:
        print("✓ Package structure looks good")
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("Checking build configuration...")
    print("=" * 60)
    print()
    
    all_ok = True
    all_ok &= check_files()
    print()
    all_ok &= check_pyproject()
    print()
    all_ok &= check_package_structure()
    
    print()
    print("=" * 60)
    if all_ok:
        print("✓ All checks passed! Ready to build.")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

