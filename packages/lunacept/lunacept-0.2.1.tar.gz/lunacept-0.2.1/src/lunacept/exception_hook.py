#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : exception_hook.py
@Author  : LorewalkerZhou
@Time    : 2025/8/16 20:22
@Desc    : 
"""
import functools
import inspect
import sys
import threading
import types

from .instrumentor import run_instrument
from .parse import create_luna_frame
from .output import print_exception

_INSTALLED = False


def _collect_frames(exc_traceback):
    tb = exc_traceback
    frame_list = []
    from .config import MAX_TRACE_DEPTH
    while tb:
        frame = tb.tb_frame
        luna_frame = create_luna_frame(frame, tb.tb_lasti)
        frame_list.append(luna_frame)
        tb = tb.tb_next
    if len(frame_list) > MAX_TRACE_DEPTH:
        skip = len(frame_list) - MAX_TRACE_DEPTH
        frame_list = frame_list[skip:]
    return frame_list


def _excepthook(exc_type, exc_value, exc_traceback):
    frame_list = _collect_frames(exc_traceback)
    print_exception(exc_type, exc_value, exc_traceback, frame_list)


def _threading_excepthook(exc):
    _excepthook(exc.exc_type, exc.exc_value, exc.exc_traceback)


def install():
    """Take over exception printing for main thread and subthreads"""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    
    sys.excepthook = _excepthook
    threading.excepthook = _threading_excepthook

    caller_frame = sys._getframe(1)
    mod = sys.modules[caller_frame.f_globals["__name__"]]
    modules = [mod]

    for mod in modules:
        for name, obj in list(vars(mod).items()):
            if inspect.isfunction(obj):
                setattr(mod, name, run_instrument(obj))


def capture_exceptions(func: types.FunctionType, reraise=False):
    """
    Decorator to automatically capture  and display exceptions.
    """
    try:
        instruct_func = run_instrument(func)
    except Exception as e:
        print(f"[lunacept] Failed to instrument {func.__name__}: {e}")
        instruct_func = func

    # Step 2. 包装运行时异常处理
    @functools.wraps(instruct_func)
    def wrapper(*args, **kwargs):
        try:
            return instruct_func(*args, **kwargs)
        except Exception as exc:
            exc_type = type(exc)
            exc_value = exc
            exc_traceback = exc.__traceback__
            frame_list = _collect_frames(exc_traceback)
            print_exception(exc_type, exc_value, exc_traceback, frame_list)
            if reraise:
                raise
            return None

    return wrapper
