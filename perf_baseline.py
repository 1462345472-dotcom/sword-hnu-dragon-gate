# perf_baseline.py
# -*- coding: utf-8 -*-
"""测量臻至版 HTML 加载性能基线:用 Edge headless 计时。"""
import subprocess, time, re, sys
sys.stdout.reconfigure(encoding='utf-8')

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html"

def measure(times=3):
    results = []
    for i in range(times):
        t0 = time.time()
        subprocess.run([EDGE, "--headless", "--disable-gpu", "--dump-dom", URL],
                       capture_output=True, timeout=120)
        results.append(time.time() - t0)
    return results

if __name__ == "__main__":
    r = measure()
    print(f"加载耗时 {len(r)} 次: {[round(x,2) for x in r]} 秒, 平均 {round(sum(r)/len(r),2)} 秒")
