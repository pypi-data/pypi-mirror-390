#!/usr/bin/env python3
"""
合并 pyproject.common.toml 到 pyproject.toml 和 pyproject.client.toml

用法:
    python scripts/sync_config.py

功能:
    - 读取 pyproject.common.toml 的 [common] 配置
    - 合并到 pyproject.toml 和 pyproject.client.toml
    - 保持目标文件的其他配置不变
"""
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print("❌ 需要 tomli: pip install tomli")
        sys.exit(1)

try:
    import tomli_w
except ImportError:
    print("❌ 需要 tomli-w: pip install tomli-w")
    sys.exit(1)


def load_toml(file_path: Path):
    """加载 TOML"""
    with open(file_path, "rb") as f:
        return tomllib.load(f)


def save_toml(file_path: Path, data: dict):
    """保存 TOML"""
    with open(file_path, "wb") as f:
        tomli_w.dump(data, f)


def merge_common_config(target_config: dict, common: dict):
    """将 common 配置合并到目标配置"""
    # 更新 [tool.poetry]
    if "tool" not in target_config:
        target_config["tool"] = {}
    if "poetry" not in target_config["tool"]:
        target_config["tool"]["poetry"] = {}
    
    poetry = target_config["tool"]["poetry"]
    poetry["name"] = common.get("name", poetry.get("name"))
    poetry["version"] = common.get("version", poetry.get("version"))
    poetry["description"] = common.get("description", poetry.get("description"))
    poetry["readme"] = common.get("readme", poetry.get("readme"))
    poetry["license"] = common.get("license", poetry.get("license"))
    poetry["keywords"] = common.get("keywords", poetry.get("keywords", []))
    poetry["classifiers"] = common.get("classifiers", poetry.get("classifiers", []))
    
    # 更新 [tool.poetry.dependencies]
    if "dependencies" not in poetry:
        poetry["dependencies"] = {}
    poetry["dependencies"]["python"] = f"^{common.get('requires_python', '>=3.12').replace('>=', '')}"
    for dep in common.get("dependencies", []):
        if ">=" in dep:
            name, ver = dep.split(">=", 1)
            poetry["dependencies"][name.strip()] = f">={ver.strip()}"
    
    # 更新 [tool.poetry.group.dev.dependencies]
    if "group" not in poetry:
        poetry["group"] = {}
    if "dev" not in poetry["group"]:
        poetry["group"]["dev"] = {}
    if "dependencies" not in poetry["group"]["dev"]:
        poetry["group"]["dev"]["dependencies"] = {}
    for dep in common.get("dev_dependencies", []):
        if ">=" in dep:
            name, ver = dep.split(">=", 1)
            poetry["group"]["dev"]["dependencies"][name.strip()] = f">={ver.strip()}"
    
    # 更新 [tool.poetry.urls]
    if "urls" in common:
        if "urls" not in poetry:
            poetry["urls"] = {}
        poetry["urls"].update(common["urls"])
    
    # 更新 [project]
    if "project" not in target_config:
        target_config["project"] = {}
    project = target_config["project"]
    project["name"] = common.get("name", project.get("name"))
    project["version"] = common.get("version", project.get("version"))
    project["description"] = common.get("description", project.get("description"))
    project["readme"] = common.get("readme", project.get("readme"))
    project["requires-python"] = common.get("requires_python", project.get("requires-python"))
    project["license"] = {"text": common.get("license", "MIT")}
    project["authors"] = common.get("authors", project.get("authors", []))
    project["keywords"] = common.get("keywords", project.get("keywords", []))
    project["classifiers"] = common.get("classifiers", project.get("classifiers", []))
    project["dependencies"] = common.get("dependencies", project.get("dependencies", []))
    
    # 更新 [project.optional-dependencies]
    if "optional-dependencies" not in project:
        project["optional-dependencies"] = {}
    project["optional-dependencies"]["dev"] = common.get("dev_dependencies", [])
    
    # 更新 [project.urls]
    if "urls" in common:
        if "urls" not in project:
            project["urls"] = {}
        project["urls"].update(common["urls"])
    
    # 更新 [tool.setuptools]
    if "setuptools" in common:
        if "tool" not in target_config:
            target_config["tool"] = {}
        if "setuptools" not in target_config["tool"]:
            target_config["tool"]["setuptools"] = {}
        setuptools = target_config["tool"]["setuptools"]
        setuptools["packages"] = common["setuptools"].get("packages", setuptools.get("packages"))
        setuptools["include-package-data"] = common["setuptools"].get("include_package_data", setuptools.get("include-package-data"))
        if "package_data" in common["setuptools"]:
            if "package-data" not in setuptools:
                setuptools["package-data"] = {}
            setuptools["package-data"].update(common["setuptools"]["package_data"])
        if "package_dir" in common["setuptools"]:
            if "package-dir" not in setuptools:
                setuptools["package-dir"] = {}
            setuptools["package-dir"].update(common["setuptools"]["package_dir"])


def main():
    root = Path(__file__).parent.parent
    common_file = root / "pyproject.common.toml"
    client_file = root / "pyproject.client.toml"
    server_file = root / "pyproject.toml"
    
    if not common_file.exists():
        print(f"❌ {common_file} 不存在")
        sys.exit(1)
    
    print("合并公共配置...")
    common_config = load_toml(common_file)
    common = common_config.get("common", {})
    
    if not common:
        print("❌ 没有 [common] 配置")
        sys.exit(1)
    
    for file_path, name in [(client_file, "客户端"), (server_file, "服务端")]:
        if file_path.exists():
            print(f"  更新 {name}: {file_path.name}")
            config = load_toml(file_path)
            merge_common_config(config, common)
            save_toml(file_path, config)
        else:
            print(f"  ⚠ 跳过: {file_path.name} 不存在")
    
    print("✓ 完成")


if __name__ == "__main__":
    main()
