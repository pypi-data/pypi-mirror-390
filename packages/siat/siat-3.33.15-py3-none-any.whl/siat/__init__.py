# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块
作者：王德宏，北京外国语大学国际商学院
版权：2021-2025(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
# 设置全局缓存
import siat.cache_init as cache_init

#==============================================================================
from siat.allin import *

from importlib.metadata import version, PackageNotFoundError

pkg_name="siat"
try:
    current_version = version(pkg_name)
    version_info=f"  Successfully enabled {pkg_name} v{current_version} caching edition"
except PackageNotFoundError:
    # 处理包未找到的情况
    version_info=f"  Package {pkg_name} not found or not installed"

print(version_info)
#==============================================================================
# 处理stooq.py修复问题：
# 改为在security_prices.py中使用monkey patch对stooq.py进行override，不灵
# 改为自编程序直接抓取tooq.com网站历史数据
#==============================================================================

#==============================================================================
#==============================================================================
# 调试用：函数调用追踪（树状缩进，仅记录 siat 包内部函数，可选记录参数）
import sys, os, inspect

_call_stack = []   # 保存调用链
_logfile = "siat_call_log.txt"
_pkg_root = os.path.abspath(__path__[0])  # siat 包的根目录绝对路径
_log_args = False  # 是否记录参数

def _safe_repr(val, maxlen=80):
    """安全打印参数，避免过大内容"""
    try:
        import pandas as pd
        if isinstance(val, pd.DataFrame):
            return f"<DataFrame shape={val.shape}>"
        if isinstance(val, pd.Series):
            return f"<Series shape={val.shape}>"
    except ImportError:
        pass

    text = repr(val)
    if len(text) > maxlen:
        text = text[:maxlen] + "...(truncated)"
    return text

def _trace_calls(frame, event, arg):
    if event == "call":
        code = frame.f_code
        func_name = code.co_name
        filename = os.path.abspath(code.co_filename)

        # 只跟踪 siat 包目录下的函数，并且跳过 <lambda>
        if filename.startswith(_pkg_root) and func_name != "<lambda>":
            module = os.path.splitext(os.path.basename(filename))[0]
            callee = f"{module}.{func_name}"

            # 如果启用参数记录
            param_str = ""
            if _log_args:
                args_info = inspect.getargvalues(frame)
                params = []
                for name in args_info.args:
                    if name in args_info.locals:
                        val = args_info.locals[name]
                        params.append(f"{name}={_safe_repr(val)}")
                if args_info.varargs:
                    vargs = args_info.locals.get(args_info.varargs, ())
                    params.append(f"*{args_info.varargs}={_safe_repr(vargs)}")
                if args_info.keywords:
                    kwargs = args_info.locals.get(args_info.keywords, {})
                    params.append(f"**{args_info.keywords}={_safe_repr(kwargs)}")
                param_str = ", ".join(params)

            indent = "    " * len(_call_stack)
            with open(_logfile, "a", encoding="utf-8") as f:
                if _log_args and param_str:
                    f.write(f"{indent}{callee}({param_str})\n")
                else:
                    f.write(f"{indent}{callee}()\n")

            _call_stack.append(callee)
            return _trace_calls

    elif event == "return":
        filename = os.path.abspath(frame.f_code.co_filename)
        if filename.startswith(_pkg_root) and _call_stack:
            _call_stack.pop()

    return _trace_calls

def start_trace_calls(logfile="siat_call_log.txt", log_args=False):
    """
    手动开启函数调用追踪（树状缩进，仅记录 siat 包内部函数）。
    参数:
        logfile: 日志文件路径
        log_args: 是否记录函数入口参数值 (默认 False)
        
    示例：
        如果需要记录被调用函数的入口参数
            start_trace_calls(log_args=True)
        仅仅记录函数的调用链式关系：
            start_trace_calls()
        追踪完毕后：
            stop_trace_calls()
    """
    global _logfile, _log_args
    _logfile = logfile
    _log_args = log_args
    with open(_logfile, "w", encoding="utf-8") as f:
        f.write("=== Start tracing siat function calls ===\n")
    sys.settrace(_trace_calls)
    print(f"[siat] Function call tracing started, logging to {_logfile}, log_args={_log_args}")

def stop_trace_calls():
    """
    停止函数调用追踪，并显示日志文件的绝对路径。
    """
    sys.settrace(None)
    abs_path = os.path.abspath(_logfile)
    print(f"[siat] Function call tracing stopped. Log file saved at:\n  {abs_path}")


