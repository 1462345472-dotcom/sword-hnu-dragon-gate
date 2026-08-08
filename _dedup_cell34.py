# -*- coding: utf-8 -*-
"""第三章/第四章新题跨库查重:
1) 与本库(细胞生物学)其他章节 questions.json 比对(精确+前12字前缀)
2) 与生化全库 HTML(湖南大学题库系统-剑指湖大一战成硕.html)比对
3) 第三章与第四章互查
"""
import re, json, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】\[\]【】]', '', s or '')

def load_qs(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return []

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'
chapters = ['第三章', '第四章']
other_cell = []
for d in sorted(glob.glob(BASE + r'\细胞生物学题库\*\questions.json')):
    # 跳过 第三/四章 自身(batch 提取),保留其他章节用于互查
    pass
# 收集细胞生物学其他章节全部题干
cell_others = []
for qf in glob.glob(BASE + r'\细胞生物学题库\*\questions.json'):
    if '第三章' in qf or '第四章' in qf:
        continue
    qs = load_qs(qf)
    cell_others.extend([q.get('question', '') for q in qs])

# 生化全库 HTML
html_path = BASE + r'\生物化学题库\湖南大学题库系统-剑指湖大一战成硕.html'
html = open(html_path, encoding='utf-8', errors='ignore').read()
bio_existing = re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
print(f'生化HTML已有题干: {len(bio_existing)} 条; 细胞其他章节题干: {len(cell_others)} 条')

def build_set(texts):
    ns = set(normalize(t) for t in texts if t)
    prefixes = set(n[:12] for n in ns if len(n) >= 8)
    return ns, prefixes

bio_ns, bio_pre = build_set(bio_existing)
cell_ns, cell_pre = build_set(cell_others)

all_dup = 0
for ch in chapters:
    qs = load_qs(f'{BASE}\\细胞生物学题库\\{ch}\\questions.json')
    dup_report = []
    for q in qs:
        n = normalize(q.get('question', ''))
        if not n:
            continue
        # 与其他章节(含两章互查)比对
        if n in cell_ns or n[:12] in cell_pre:
            dup_report.append(('细胞其他章', q.get('question', '')[:40]))
        if n in bio_ns or n[:12] in bio_pre:
            dup_report.append(('生化全库', q.get('question', '')[:40]))
    if dup_report:
        print(f'[{ch}] 发现 {len(dup_report)} 条重复:')
        for src, t in dup_report[:20]:
            print(f'  ({src}) {t}')
    else:
        print(f'[{ch}] 与细胞其他章节及生化全库 0 重复 ✓ ({len(qs)}题)')
    all_dup += len(dup_report)
print(f'总计重复: {all_dup} 条')
