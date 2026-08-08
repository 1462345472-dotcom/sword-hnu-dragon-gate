# -*- coding: utf-8 -*-
"""Task 5 性能对比:修改前(备份) vs 修改后(索引版),Edge headless --dump-dom 加载计时,各 3 次。"""
import subprocess, time, sys, statistics
sys.stdout.reconfigure(encoding='utf-8')

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FILES = {
    "before(全量遍历)": "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/_臻至版_task5_backup.html",
    "after(章节索引)": "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html",
}

def measure(url, times=3):
    rs = []
    for _ in range(times):
        t0 = time.time()
        subprocess.run([EDGE, "--headless", "--disable-gpu", "--dump-dom", url],
                       capture_output=True, timeout=120)
        rs.append(time.time() - t0)
    return rs

for name, url in FILES.items():
    r = measure(url)
    print(f"{name}: {[round(x,2) for x in r]} 秒, 平均 {round(statistics.mean(r),2)} 秒")
