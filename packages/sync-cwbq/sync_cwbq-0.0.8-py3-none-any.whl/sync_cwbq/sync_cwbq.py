#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author     :zhaoyukai
# @Time       :2025/11/6 13:47

"""

"""
import os

from urllib.parse import quote_plus
from celery import Celery

mongo_uri = f"mongodb://{os.getenv('MONGO_USER')}:{quote_plus(os.getenv('MONGO_PASS'))}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}"
redis_uri = f"redis://:{quote_plus(os.getenv('REDIS_PASS'))}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
redis_broker = os.getenv('REDIS_BROKER') if os.getenv('REDIS_BROKER') else 9
redis_backend = os.getenv('REDIS_BACKEND') if os.getenv('REDIS_BACKEND') else 10

app = Celery(
    'sync_odps_worker',
    broker=f"{redis_uri}/{redis_broker}",
    backend=f"{redis_uri}/{redis_backend}",
    include=['tasks'],
    worker_prefetch_multiplier=1,  # 每次预取的任务数量
    worker_max_tasks_per_child=7  # 每个worker进程执行100个任务后重启
)