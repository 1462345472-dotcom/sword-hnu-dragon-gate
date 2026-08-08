# -*- coding: utf-8 -*-
"""第十六章 生物能学 题目生成脚本:合并 QA/QB/QC/QD + TERMS,生成 questions.json 与 terms.json"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))

# 导入各数据段
sys.path.insert(0, BASE)
from ch16_q_a import QA
from ch16_q_b import QB
from ch16_q_c import QC
from ch16_q_d import QD
from ch16_terms import TERMS

ALL_RAW = QA + QB + QC + QD

# 赋 id 并做初步结构检查
questions = []
for i, q in enumerate(ALL_RAW, 1):
    item = dict(q)
    item['id'] = i
    questions.append(item)

terms = []
for i, t in enumerate(TERMS, 1):
    terms.append({
        "id": i,
        "term": t["term"],
        "name": t["name"],
        "definition": t["definition"],
        "chapter": "biochem_16",
    })

# ---- 自检 ----
errs = []
for q in questions:
    qt, qid = q['type'], q['id']
    if qt in ('choice', 'multi'):
        for k, v in q['options'].items():
            if not v.strip():
                errs.append('[#%d] 选项 %s 为空' % (qid, k))
    if qt == 'choice' and q['answer'] not in q['options']:
        errs.append('[#%d] choice答案不在options: %s' % (qid, q['answer']))
    if qt == 'multi':
        for ch in q['answer']:
            if ch not in q['options']:
                errs.append('[#%d] multi答案 %s 不在options' % (qid, ch))
    if qt == 'truefalse' and q['answer'].lower() not in ('true', 'false'):
        errs.append('[#%d] truefalse答案非法: %s' % (qid, q['answer']))
    if qt == 'short' and len(q['answer']) < 5:
        errs.append('[#%d] short答案过短' % qid)

for t in terms:
    n = len(t['definition'])
    if not (30 <= n <= 80):
        errs.append('[terms#%d] 定义长度 %d 超出30-80: %s' % (t['id'], n, t['term']))

if errs:
    print('自检发现 %d 个问题:' % len(errs))
    for e in errs:
        print(' ', e)
    sys.exit(1)

# ---- 题型统计 ----
from collections import Counter
print('总题数: %d' % len(questions))
print('题型分布:', dict(Counter(q['type'] for q in questions)))
for qt, cnt in Counter(q['type'] for q in questions).items():
    print('  %-9s %3d  %5.1f%%' % (qt, cnt, 100.0 * cnt / len(questions)))
print('terms: %d' % len(terms))

# ---- 写出 ----
with open(os.path.join(BASE, 'questions.json'), 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=1)
with open(os.path.join(BASE, 'terms.json'), 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=1)

print('已生成 questions.json (%d题) 与 terms.json (%d个)' % (len(questions), len(terms)))
