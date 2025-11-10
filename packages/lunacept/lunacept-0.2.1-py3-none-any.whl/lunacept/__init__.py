#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : __init__.py.py
@Author  : LorewalkerZhou
@Time    : 2025/8/16 20:21
@Desc    : 
"""
from .exception_hook import install, capture_exceptions
from .config import configure

__all__ = ["install", "configure", "capture_exceptions"]
