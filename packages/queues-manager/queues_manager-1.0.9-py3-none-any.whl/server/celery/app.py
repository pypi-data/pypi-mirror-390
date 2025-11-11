"""Celery 应用初始化"""
from celery import Celery
from server.celery.celery_config import get_celery_config

# 创建 Celery 应用
celery_app = Celery("agent_queue")

# 加载配置
celery_app.conf.update(get_celery_config())

# 自动发现任务
celery_app.autodiscover_tasks(["server.celery"])

