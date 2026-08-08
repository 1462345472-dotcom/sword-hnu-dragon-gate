# -*- coding: utf-8 -*-
"""跨科查重: 细胞5/6章题目 vs 生化全库 + 细胞其他章(题干归一化精确匹配 + 前12字前缀)"""
import json, io, sys, re, os, glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\Users\Lenovo\Desktop\湖南大学'

def normalize(q):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】]', '', q or '')

def load_all_questions(dirs):
    out = []
    for d in dirs:
        for p in glob.glob(os.path.join(BASE, d, '*', 'questions.json')):
            try:
                qs = json.load(open(p, encoding='utf-8'))
                out.extend(qs)
            except Exception as e:
                print('跳过', p, e)
    return out

# 生化全库
bio = load_all_questions(['生物化学题库'])
# 细胞其他章(排除5、6章)
cell_others = []
for d in os.listdir(os.path.join(BASE, '细胞生物学题库')):
    p = os.path.join(BASE, '细胞生物学题库', d, 'questions.json')
    if d in ('第五章', '第六章') or not os.path.exists(p):
        continue
    try:
        cell_others.extend(json.load(open(p, encoding='utf-8')))
    except Exception:
        pass

bio_texts = [normalize(q.get('question', '')) for q in bio]
bio_prefixes = set(n[:12] for n in bio_texts if len(n) >= 8)
cell_texts = [normalize(q.get('question', '')) for q in cell_others]
cell_prefixes = set(n[:12] for n in cell_texts if len(n) >= 8)

print(f'生化全库: {len(bio)} 题 | 细胞其他章: {len(cell_others)} 题')

issues = []
for ch in ['第五章', '第六章']:
    qs = json.load(open(os.path.join(BASE, '细胞生物学题库', ch, 'questions.json'), encoding='utf-8'))
    for q in qs:
        n = normalize(q.get('question', ''))
        if not n:
            continue
        if n in bio_texts or n[:12] in bio_prefixes:
            issues.append((ch, q['id'], '与生化库重复', q['question'][:40]))
        if n in cell_texts or n[:12] in cell_prefixes:
            issues.append((ch, q['id'], '与细胞其他章重复', q['question'][:40]))
print('跨科重复:', len(issues))
for it in issues:
    print(' ', it)
if not issues:
    print('PASS: 两章题目与生化全库及细胞其他章 0 重复')
