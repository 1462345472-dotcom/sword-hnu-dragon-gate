# -*- coding: utf-8 -*-
"""第九章微调: 删 Q19(与Q60章内重复), Q26题干解耦生化, 重排id"""
import json

P = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第九章\questions.json'
with open(P, encoding='utf-8') as f:
    qs = json.load(f)

# 1. 删除 Q19 (活性染色质蛋白组成"不包括"choice, 与Q60 multi 完全同考点)
before = len(qs)
qs = [q for q in qs if q['id'] != 19]
print('删除 Q19(与Q60章内重复):', before, '->', len(qs))

# 2. Q26 题干解耦(避免与生化第三十章82题"端粒的主要功能是?"主干撞车)
for q in qs:
    if q['id'] == 26:
        q['question'] = '关于端粒，下列说法错误的是？'
        print('Q26 题干已改为:', q['question'])

# 3. 重排 id
qs = sorted(qs, key=lambda q: q['id'])
for new_id, q in enumerate(qs, start=1):
    q['id'] = new_id

with open(P, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)

import collections
print('最终题数:', len(qs))
print('题型分布:', dict(collections.Counter(q['type'] for q in qs)))
print('topic分布:', dict(collections.Counter(q['topic'] for q in qs)))
print('id连续:', [q['id'] for q in qs] == list(range(1, len(qs) + 1)))
