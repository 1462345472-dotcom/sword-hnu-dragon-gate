# -*- coding: utf-8 -*-
"""15/16章 vs 全部章节 跨章查重"""
import json, glob, os, re, sys

def norm(s):
    return re.sub(r'[\s,，。、;；:：?？()（）【】\[\]"\'"\'\.．·\-—]+', '', s)

def sim(a, b):
    sa, sb = norm(a), norm(b)
    if not sa or not sb:
        return 0.0
    inter = len(set(sa) & set(sb))
    return inter / min(len(sa), len(sb))

ch15 = json.load(open('生物化学题库/第十五章/questions.json', encoding='utf-8'))
ch16 = json.load(open('生物化学题库/第十六章/questions.json', encoding='utf-8'))

others = []
for p in glob.glob('生物化学题库/*/questions.json'):
    if '第十五章' in p or '第十六章' in p:
        continue
    with open(p, encoding='utf-8') as f:
        try:
            qs = json.load(f)
        except Exception:
            continue
    ch = os.path.basename(os.path.dirname(p))
    for q in qs:
        others.append((ch, q.get('id'), q.get('question', ''), q.get('type', '')))

results = []
for ch_name, qs in [('第十五章', ch15), ('第十六章', ch16)]:
    for q in qs:
        qtext = q.get('question', '')
        for (och, oid, otext, otype) in others:
            sc = sim(qtext, otext)
            if sc > 0.72 and len(norm(qtext)) > 15:
                results.append((sc, ch_name, q['id'], q['type'], och, oid, otype, qtext, otext))

results.sort(key=lambda x: -x[0])
for r in results:
    print('%.2f | %sQ%d(%s) vs %sQ%d(%s)' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
    print('    A: %s' % r[7][:70])
    print('    B: %s' % r[8][:70])
print('total pairs:', len(results))
