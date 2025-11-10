#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author     :zhaoyukai
# @Time       :2025/11/6 13:47

"""

"""
import os
import platform

from dotenv import load_dotenv

system = platform.system()

try:
    load_dotenv(os.path.join(os.getcwd(), '.env'))
    if system == 'Windows':
        load_dotenv(os.path.join(os.getcwd(), '.env.dev'))
    if system == 'Linux':
        load_dotenv(os.path.join(os.getcwd(), '.env.prod'))
except:
    pass
