"""启动 Celery Worker 的辅助脚本

注意：推荐使用命令行方式启动 Celery Worker：
    celery -A implements.celery_app worker --loglevel=info

或者：
    celery -A implements.celery_app worker --loglevel=info --concurrency=4
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    print("=" * 60)
    print("Celery Worker 启动脚本")
    print("=" * 60)
    print("\n推荐使用以下命令启动 Celery Worker：")
    print("  celery -A server.celery.app worker --loglevel=info")
    print("\n或者使用并发模式：")
    print("  celery -A server.celery.app worker --loglevel=info --concurrency=4")
    print("\n查看所有选项：")
    print("  celery -A server.celery.app worker --help")
    print("=" * 60)
    sys.exit(0)

