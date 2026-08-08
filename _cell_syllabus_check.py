# -*- coding: utf-8 -*-
"""细胞考纲覆盖检查:细胞各章题目 topic vs 851 考纲条目"""
import json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

syllabus = json.load(open('docs/superpowers/specs/细胞考纲考点清单.json', encoding='utf-8'))
cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16}

dirs = [d for d in os.listdir('细胞生物学题库') if os.path.isdir(f'细胞生物学题库/{d}') and '章' in d]
def num(d):
    m = re.match(r'第(.+?)章', d)
    return cn.get(m.group(1), 99) if m else 99

for d in sorted(dirs, key=num):
    n = num(d)
    qf = f'细胞生物学题库/{d}/questions.json'
    if not os.path.exists(qf):
        continue
    qs = json.load(open(qf, encoding='utf-8'))
    topics = set()
    for q in qs:
        t = q.get('topic', '')
        if t:
            topics.add(t)
    # 本章考纲条目
    ch_points = [p['point'] for p in syllabus if p['chapter'] == f'cell_{n}']
    if not ch_points:
        continue
    gaps = []
    for pt in ch_points:
        if len(pt) < 4:
            continue
        # 匹配:考纲条目关键词是否被某 topic 包含,或 topic 关键词被条目包含
        covered = False
        for t in topics:
            if pt in t or t in pt:
                covered = True
                break
            # 取条目前 8 字做宽松匹配
            if len(pt) >= 8 and pt[:8] in t:
                covered = True
                break
        if not covered:
            gaps.append(pt)
    if gaps:
        print(f'细胞第{n}章({d}): {len(qs)}题, 考纲缺口 {len(gaps)} 条:')
        for g in gaps:
            print(f'   - {g[:60]}')
    else:
        print(f'细胞第{n}章({d}): {len(qs)}题, 考纲覆盖 ✅')
