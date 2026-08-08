# -*- coding: utf-8 -*-
"""跨科查重:细胞生物学第一章绪论/第二章 全部题 vs 生化HTML全库+生化各章JSON+细胞生物其他章节"""
import re, json, sys, glob
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】\"\'`~·]', '', s or '')

# ---- 收集所有"已有"题干 ----
existing = set()

# 1. 生化 HTML
html = open('生物化学题库/湖南大学题库系统-臻至版.html', encoding='utf-8', errors='ignore').read()
hits = re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
for t in hits:
    existing.add(norm(t))
print('生化HTML题干:', len(hits))

# 2. 生化各章 JSON
for p in glob.glob('生物化学题库/*/questions.json'):
    try:
        qs = json.load(open(p, encoding='utf-8'))
        for q in qs:
            existing.add(norm(q.get('question', '')))
    except Exception as e:
        print('跳过', p, e)
print('生化JSON章节数:', len(glob.glob('生物化学题库/*/questions.json')))

# 3. 细胞生物学其他章节(排除第一章绪论、第二章)
cell_other = {}
for p in glob.glob('细胞生物学题库/*/questions.json'):
    ch = p.replace('\\', '/').split('/')[-2]
    if ch in ('第一章绪论', '第二章'):
        continue
    qs = json.load(open(p, encoding='utf-8'))
    for q in qs:
        cell_other[norm(q.get('question', ''))] = ch
print('细胞生物其他章节覆盖:', len(set(cell_other.values())), '个章节')

# ---- 检查目标章 ----
all_dup = 0
for ch in ['第一章绪论', '第二章']:
    qs = json.load(open(f'细胞生物学题库/{ch}/questions.json', encoding='utf-8'))
    new_ids = set(range(107, 500)) if ch == '第一章绪论' else set(range(105, 500))
    dup_bio = 0; dup_cell = 0
    for q in qs:
        n = norm(q.get('question', ''))
        if n in existing:
            dup_bio += 1
            print(f'[{ch} #{q["id"]}] 与生化库重复: {q["question"][:40]}')
        if n in cell_other:
            dup_cell += 1
            print(f'[{ch} #{q["id"]}] 与细胞生物{cell_other[n]}重复: {q["question"][:40]}')
    all_dup += dup_bio + dup_cell
    print(f'== {ch}: 共{len(qs)}题, 与生化库重复{dup_bio}, 与细胞生物其他章重复{dup_cell}')

print('\n[结论] 总重复:', all_dup)
