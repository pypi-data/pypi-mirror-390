# -*- coding: utf-8 -*-
"""
功能：一次性引入SIAT的所有模块，试图全面缓存所有网络请求
注意：本版本尚未调试通过，问题在于被访问的网站不信任设置的proxy（mitmproxy 的根证书）
    导致错误Client TLS handshake failed. The client does not trust the proxy's certificate
    解决方法：让系统或 Python 信任 mitmproxy 的根证书，将证书导入系统或 Python 信任链
    但需要较多的计算机操作，初学者很可能无法完成，导致课堂教学工作量暴增！
    暂时放弃！！！
作者：王德宏，北京外国语大学国际商学院
版权：2021-2025(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

#==============================================================================
#屏蔽所有警告性信息
import warnings; warnings.filterwarnings('ignore')
#==============================================================================
# 设置全局缓存
import os
import subprocess
import datetime
import socket
import sys

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(port_list):
    """从备用端口列表中选择第一个可用端口"""
    for port in port_list:
        if not is_port_in_use(port):
            return port
    raise RuntimeError(" All available ports are not available, please revise manually")

def start_proxy_with_cache():
    """自动启动 mitmproxy 并设置代理环境变量"""
    port_pool = [8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088]
    proxy_port = find_available_port(port_pool)

    # 启动 mitmproxy 缓存脚本（后台运行），调用后台程序cache.py
    cache_script = os.path.join(os.path.dirname(__file__), "cache.py")
    subprocess.Popen([
        sys.executable, "-m", "mitmdump",
        "-p", str(proxy_port),
        "-s", cache_script
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 设置环境变量
    cache_success=False
    try:
        os.environ['HTTP_PROXY'] = f"http://localhost:{proxy_port}"
        os.environ['HTTPS_PROXY'] = f"http://localhost:{proxy_port}"
        
        print(f"  Caching web-scraping initiated using port {proxy_port}")
        cache_success=True

    except:
        # macOS下可能需要权限
        print(f"  Caching web-scraping not initiated due to lack of permission")

    return cache_success

# 执行自动代理启动
cache_success=start_proxy_with_cache()

#==============================================================================
from siat.allin import *

from importlib.metadata import version, PackageNotFoundError

pkg_name="siat"
try:
    current_version = version(pkg_name)
    if cache_success:
        version_info=f"  Successfully enabled {pkg_name} v{current_version} with cache"
    else:
        version_info=f"  Successfully enabled {pkg_name} v{current_version} without cache"
        
except PackageNotFoundError:
    # 处理包未找到的情况
    version_info=f"  Package {pkg_name} not fully installed, please take a big bath for it"
    # 洗大澡指令：pip install siat --upgrade --forece-reinstall --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple
print(version_info)
#==============================================================================
# 处理pandas_datareader中stooq.py修复问题：
# 改为在security_prices.py中使用monkey patch对stooq.py进行override，不灵
# 改为自编程序直接抓取stooq.com网站历史数据
# 使用yfinance抓取数据需要设置vpn的IP地址和端口号，不同vpn可能不同
# 使用pandas_datareader中fama_french可能需要修改http为https
#==============================================================================
