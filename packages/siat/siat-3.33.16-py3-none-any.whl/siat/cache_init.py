# -*- coding: utf-8 -*-

import datetime
import os
import requests
import requests_cache
import sqlite3 #Python自带，无需安装

# ✅ 控制缓存失效时间（单位：天）
CACHE_EXPIRE_DAYS = 1  # 0=当日午夜，1=次日午夜，3=三天后午夜
"""
if CACHE_EXPIRE_DAYS == 0:
    print("  Caching lasts till midnight today")
else:
    print(f"  Caching lasts till midnight after {CACHE_EXPIRE_DAYS} day(s)")
"""

# ✅ 控制缓存文件大小阈值（单位：MB）
CACHE_SIZE_LIMIT_MB = 100
#print(f"  Caching clean-up when exceeding {CACHE_SIZE_LIMIT_MB}MB")

# ✅ 日志文件路径
LOG_FILE = os.path.join(os.path.dirname(__file__), "siat_cache_log.txt")

# ✅ 缓存数据库路径（requests_cache 会生成 siat_cache.sqlite）
CACHE_DB = os.path.join(os.path.dirname(__file__), "siat_cache.sqlite")

# ✅ 命中率统计变量
total_requests = 0
cache_hits = 0

def get_expire_time():
    """返回失效时间：今天 + N 天 的午夜"""
    target_day = datetime.date.today() + datetime.timedelta(days=CACHE_EXPIRE_DAYS)
    return datetime.datetime.combine(target_day, datetime.time.max)

def log(message):
    """写入日志文件"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def clean_expired_cache_if_needed():
    """仅当缓存文件超过阈值时清理过期条目"""
    if os.path.exists(CACHE_DB):
        size_mb = os.path.getsize(CACHE_DB) / (1024 * 1024)
        if size_mb > CACHE_SIZE_LIMIT_MB:
            try:
                conn = sqlite3.connect(CACHE_DB)
                cursor = conn.cursor()
                now_ts = datetime.datetime.now().timestamp()
                deleted = cursor.execute("DELETE FROM responses WHERE expires < ?", (now_ts,)).rowcount
                conn.commit()
                conn.close()
                log(f"*** 清理过期缓存条目：{deleted} 条（当前大小：{size_mb:.2f}MB）")
            except Exception as e:
                log(f"*** 清理缓存失败：{e}")

def record_cache_stats(response):
    """记录命中率信息"""
    global total_requests, cache_hits
    total_requests += 1
    if getattr(response, "from_cache", False):
        cache_hits += 1
        log(f"*** 缓存命中：{response.url}")
    else:
        log(f"📡 实时请求：{response.url}")
    hit_rate = (cache_hits / total_requests) * 100 if total_requests else 0
    log(f"*** 当前命中率：{cache_hits}/{total_requests} = {hit_rate:.2f}%")

# ✅ 安装全局缓存（自动生效）
requests_cache.install_cache(
    cache_name=os.path.splitext(CACHE_DB)[0],
    backend='sqlite',
    expire_after=get_expire_time()
)

# ✅ 清理过期缓存（仅当文件过大）
clean_expired_cache_if_needed()

# ✅ 自动挂钩 requests 的响应处理
_original_send = requests.Session.send

def _wrapped_send(self, request, **kwargs):
    response = _original_send(self, request, **kwargs)
    record_cache_stats(response)
    return response

requests.Session.send = _wrapped_send

"""
寻找缓存和日志文件的位置
import os
print("缓存文件路径：", os.path.join(os.getcwd(), "siat_cache.sqlite"))
print("日志文件路径：", os.path.join(os.getcwd(), "siat_cache_log.txt"))
"""