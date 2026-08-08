# -*- coding: utf-8 -*-
"""第十三、十四章补题查重:新增/修改题 vs 生化全库 + 细胞已入库章 + 章内自重复"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】\[\]]', '', s or '')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'

# ---- 1. 生化全库(HTML) ----
html_path = os.path.join(BASE, '生物化学题库', '湖南大学题库系统-剑指湖大一战成硕.html')
html = open(html_path, encoding='utf-8', errors='ignore').read()
bio_existing = re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
bio_ns = set(normalize(t) for t in bio_existing)
bio_pre = set(n[:12] for n in bio_ns if len(n) >= 8)
print('生化全库题干: %d 条' % len(bio_existing))

# ---- 2. 细胞已入库章(build_unified SUBJECTS 中的细胞章节, 排除 13/14) ----
sys.path.insert(0, BASE)
from build_unified import SUBJECTS
cell_existing = {}
for key, cfg in SUBJECTS.items():
    qf = os.path.join(BASE, cfg['questionsFile'])
    if '细胞生物学题库' not in cfg['questionsFile']:
        continue
    if '第十三章' in cfg['questionsFile'] or '第十四章' in cfg['questionsFile']:
        continue
    if not os.path.exists(qf):
        continue
    qs = json.load(open(qf, encoding='utf-8'))
    for q in qs:
        n = normalize(q.get('question', ''))
        if n:
            cell_existing[n] = '%s#%s' % (key, q.get('id'))
print('细胞已入库章节(除13/14)题干: %d 条' % len(cell_existing))

# ---- 3. 检查两章全部题(含新增) ----
def norm_key(n):
    return (n in bio_ns, n[:12] in bio_pre if len(n) >= 8 else False)

for ch in ['第十三章', '第十四章']:
    qs = json.load(open(os.path.join(BASE, '细胞生物学题库', ch, 'questions.json'), encoding='utf-8'))
    seen = {}
    dups_bio, dups_cell, dups_self = [], [], []
    for q in qs:
        n = normalize(q.get('question', ''))
        if not n:
            continue
        if n in seen:
            dups_self.append((q['id'], seen[n]))
        seen[n] = q['id']
        if n in bio_ns or (len(n) >= 8 and n[:12] in bio_pre):
            dups_bio.append(q['id'])
        if n in cell_existing:
            dups_cell.append((q['id'], cell_existing[n]))
    print('[%s] 共%d题: 与生化全库重复%d条 %s; 与细胞已入库章重复%d条 %s; 章内自重复%d条 %s'
          % (ch, len(qs), len(dups_bio), dups_bio, len(dups_cell), dups_cell, len(dups_self), dups_self))

# ---- 4. 两章互查 ----
q13 = json.load(open(os.path.join(BASE, '细胞生物学题库', '第十三章', 'questions.json'), encoding='utf-8'))
q14 = json.load(open(os.path.join(BASE, '细胞生物学题库', '第十四章', 'questions.json'), encoding='utf-8'))
n13 = {normalize(q.get('question','')): q['id'] for q in q13}
cross = []
for q in q14:
    n = normalize(q.get('question',''))
    if n and n in n13:
        cross.append((q['id'], n13[n]))
print('第十三章 vs 第十四章 互查重复: %d 条 %s' % (len(cross), cross))

# ---- 5. 精确口径:新增+修改题 vs 生化全库 + 细胞已入库章 ----
targets = {'第十三章': list(range(102, 133)) + [72], '第十四章': list(range(86, 108)) + [68]}
for ch, ids in targets.items():
    qs = json.load(open(os.path.join(BASE, '细胞生物学题库', ch, 'questions.json'), encoding='utf-8'))
    new = [q for q in qs if q['id'] in ids]
    db, dc = [], []
    for q in new:
        n = normalize(q.get('question', ''))
        if n in bio_ns or (len(n) >= 8 and n[:12] in bio_pre):
            db.append(q['id'])
        if n in cell_existing:
            dc.append((q['id'], cell_existing[n]))
    print('[%s] 新增/修改题 %d 条: 与生化全库重复 %d %s; 与细胞已入库章重复 %d %s'
          % (ch, len(new), len(db), db, len(dc), dc))
