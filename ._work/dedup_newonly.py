# -*- coding: utf-8 -*-
"""仅检查两章新增题与生化全库+细胞其他章的重复"""
import re, json, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】"`~·]', '', s or '')

existing = set()
html = open('生物化学题库/湖南大学题库系统-臻至版.html', encoding='utf-8', errors='ignore').read()
for t in re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html):
    existing.add(norm(t))
for p in glob.glob('生物化学题库/*/questions.json'):
    for q in json.load(open(p, encoding='utf-8')):
        existing.add(norm(q.get('question', '')))

cell_other = set()
for p in glob.glob('细胞生物学题库/*/questions.json'):
    ch = p.replace('\\', '/').split('/')[-2]
    if ch in ('第一章绪论', '第二章'):
        continue
    for q in json.load(open(p, encoding='utf-8')):
        cell_other.add(norm(q.get('question', '')))

total_dup = 0
for ch, start in [('第一章绪论', 107), ('第二章', 105)]:
    qs = json.load(open('细胞生物学题库/%s/questions.json' % ch, encoding='utf-8'))
    new = [q for q in qs if q['id'] >= start]
    d1 = [q for q in new if norm(q['question']) in existing]
    d2 = [q for q in new if norm(q['question']) in cell_other]
    for q in d1 + d2:
        print('[%s #%d] 重复: %s' % (ch, q['id'], q['question'][:40]))
    print('== %s: 新增%d题, 与生化库重复%d, 与细胞其他章重复%d' % (ch, len(new), len(d1), len(d2)))
    total_dup += len(d1) + len(d2)
print('[结论] 新增题重复总数:', total_dup)
