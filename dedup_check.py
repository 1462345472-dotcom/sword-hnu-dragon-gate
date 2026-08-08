# -*- coding: utf-8 -*-
"""新题与已有题去重:题干去空白/标点后精确匹配 + 前 12 字前缀匹配。"""
import re

def normalize(q):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】]', '', q or '')

def dedup_check(questions, existing_texts):
    norm_existing = set(normalize(t) for t in existing_texts)
    prefixes = set(n[:12] for n in norm_existing if len(n) >= 8)
    dups = []
    for q in questions:
        n = normalize(q.get("question", ""))
        if not n: continue
        if n in norm_existing or n[:12] in prefixes:
            dups.append(q)
    return dups

def main():
    import json, re as _re
    new = json.load(open("生物化学题库/第十五章/questions.json", encoding="utf-8"))
    html = open("生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html", encoding="utf-8", errors="ignore").read()
    existing = _re.findall(r'"question":"((?:[^"\\]|\\.)*)"', html)
    dups = dedup_check(new, existing)
    print(f"已有题干 {len(existing)} 条, 新题 {len(new)} 条, 重复 {len(dups)} 条")
    for d in dups: print("重复:", d.get("question", "")[:40])

if __name__ == "__main__":
    main()
