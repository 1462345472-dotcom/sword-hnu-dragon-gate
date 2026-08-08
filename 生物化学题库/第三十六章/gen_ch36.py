# -*- coding: utf-8 -*-
"""第三十六章 数据合并生成:questions.json + terms.json + schema 自检"""
import json, sys, io, importlib.util

BASE = r"C:\Users\Lenovo\Desktop\湖南大学\生物化学题库\第三十六章"
sys.stdout.reconfigure(encoding="utf-8")

def load_part(name):
    spec = importlib.util.spec_from_file_location(name, f"{BASE}\\{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.Q

qs = []
for p in ["_ch36_part1", "_ch36_part2", "_ch36_part3"]:
    qs.extend(load_part(p))

for i, q in enumerate(qs, 1):
    q["id"] = i

with io.open(f"{BASE}\\questions.json", "w", encoding="utf-8") as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)

spec = importlib.util.spec_from_file_location("_ch36_terms", f"{BASE}\\_ch36_terms.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
terms = mod.T
for i, t in enumerate(terms, 1):
    t["id"] = i
with io.open(f"{BASE}\\terms.json", "w", encoding="utf-8") as f:
    json.dump(terms, f, ensure_ascii=False, indent=1)

print("questions:", len(qs), "| terms:", len(terms))

# schema 自检
import subprocess
r = subprocess.run([sys.executable, r"C:\Users\Lenovo\Desktop\湖南大学\schema_validator.py"],
                   capture_output=True, text=True, encoding="gbk", errors="replace")
print(r.stdout[-3000:] if len(r.stdout) > 3000 else r.stdout)
if r.returncode != 0:
    print(r.stderr[-1500:])

# 题型统计
from collections import Counter
print("题型分布:", dict(Counter(q["type"] for q in qs)))
print("难度分布:", dict(Counter(q["difficulty"] for q in qs)))
# 名解字数检查 30-80
for t in terms:
    n = len(t["definition"])
    if not (30 <= n <= 80):
        print(f"[名解字数异常] {t['term']}: {n} 字")
print("名解字数检查完成")
