# -*- coding: utf-8 -*-
"""
功能：设置缓存策略，减少网络访问量，适应课堂演示环境
注意：尚未充分测试，暂时不启用！！！
作者：王德宏，北京外国语大学国际商学院
版权：2021-2025(C) 仅限教学使用，商业使用需要授权
联络：wdehong2000@163.com
"""

# 注意：本程序被当作subprocess运行，print不会输出信息！

from mitmproxy import http
import datetime
import os
import pickle

# ✅ 控制缓存失效时间（0=当日午夜，1=次日午夜，3=三天后午夜）
CACHE_EXPIRE_DAYS = 1

# ✅ 控制缓存文件大小阈值（单位：字节），100MB = 100 * 1024 * 1024
CACHE_SIZE_LIMIT = 100 * 1024 * 1024

# 缓存与日志文件路径（与 cache.py 同目录）
BASE_DIR = os.path.dirname(__file__)
CACHE_FILE = os.path.join(BASE_DIR, "proxy_cache.pkl")
LOG_FILE = os.path.join(BASE_DIR, "proxy_cache_log.txt")

# 加载磁盘缓存
try:
    with open(CACHE_FILE, "rb") as f:
        cache_store = pickle.load(f)
except (FileNotFoundError, EOFError):
    cache_store = {}

# ✅ 命中率统计变量
total_requests = 0
cache_hits = 0

def log(message: str):
    """将日志写入文件"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def save_cache():
    """将缓存写入磁盘"""
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache_store, f)

def get_expire_time():
    """根据设置返回失效时间（午夜）"""
    target_day = datetime.date.today() + datetime.timedelta(days=CACHE_EXPIRE_DAYS)
    return datetime.datetime.combine(target_day, datetime.time.max)

def clean_expired_cache_if_needed():
    """仅在缓存文件超过设定大小时清理过期条目"""
    if os.path.exists(CACHE_FILE) and os.path.getsize(CACHE_FILE) > CACHE_SIZE_LIMIT:
        now = datetime.datetime.now()
        expired_keys = [url for url, entry in cache_store.items() if entry['expire'] <= now]
        for url in expired_keys:
            del cache_store[url]
        save_cache()
        log(f"🧹 清理过期缓存条目：{len(expired_keys)}")

def request(flow: http.HTTPFlow) -> None:
    # 本函数由插件自动调用，每当发出网络请求时被激发
    global total_requests, cache_hits
    total_requests += 1

    clean_expired_cache_if_needed()

    url = flow.request.pretty_url
    now = datetime.datetime.now()

    if url in cache_store and cache_store[url]['expire'] > now:
        flow.response = cache_store[url]['response']
        cache_hits += 1
        log(f"✅ 缓存命中：{url}")
    else:
        log(f"📡 实时请求：{url}")

    # 记录命中率
    hit_rate = (cache_hits / total_requests) * 100 if total_requests else 0
    log(f"📊 当前命中率：{cache_hits}/{total_requests} = {hit_rate:.2f}%")

def response(flow: http.HTTPFlow) -> None:
    # 本函数由插件自动调用，每当收到网络返回数据时被激发
    url = flow.request.pretty_url
    expire = get_expire_time()

    cache_store[url] = {
        'response': flow.response,
        'expire': expire
    }

    save_cache()



