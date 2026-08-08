# -*- coding: utf-8 -*-
"""第二十章 全量自检"""
import json, sys, os
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

base = os.path.dirname(os.path.abspath(__file__))
qs = json.load(open(os.path.join(base, 'questions.json'), encoding='utf-8'))
ts = json.load(open(os.path.join(base, 'terms.json'), encoding='utf-8'))

errors = []

# id 连续
ids = [q['id'] for q in qs]
if ids != list(range(1, len(qs) + 1)):
    errors.append('id 不连续')
if len(set(ids)) != len(ids):
    errors.append('id 重复')

# 必填字段
for q in qs:
    for f in ['id', 'type', 'question', 'answer', 'explanation', 'difficulty', 'tags']:
        if f not in q:
            errors.append(f"Q{q['id']} 缺 {f}")
    if q['type'] not in ('choice', 'truefalse', 'multi', 'short'):
        errors.append(f"Q{q['id']} 非法题型 {q['type']}")
    if not isinstance(q['difficulty'], int) or q['difficulty'] not in (1, 2, 3):
        errors.append(f"Q{q['id']} 难度非法")

    if q['type'] == 'choice':
        if 'options' not in q or q['answer'] not in q['options']:
            errors.append(f"Q{q['id']} choice 答案不在 options")
        if len(q['options']) < 4:
            errors.append(f"Q{q['id']} choice 选项不足4")
    elif q['type'] == 'multi':
        if 'options' not in q:
            errors.append(f"Q{q['id']} multi 缺 options")
            continue
        if len(q['options']) < 4:
            errors.append(f"Q{q['id']} multi 选项不足4")
        ans = q['answer']
        if len(ans) != len(set(ans)):
            errors.append(f"Q{q['id']} multi 答案重复字符")
        for ch in ans:
            if ch not in q['options']:
                errors.append(f"Q{q['id']} multi 答案 {ch} 不在 options")
    elif q['type'] == 'truefalse':
        if q['answer'] not in ('true', 'false'):
            errors.append(f"Q{q['id']} truefalse 答案非法")
    elif q['type'] == 'short':
        if 'options' in q:
            errors.append(f"Q{q['id']} short 不应有 options")

# topic 非空
for q in qs:
    if not q.get('topic'):
        errors.append(f"Q{q['id']} 缺 topic")

# terms 校验
for t in ts:
    n = len(t.get('definition', ''))
    if not (30 <= n <= 80):
        errors.append(f"term[{t.get('id')}] {t.get('term')} 定义 {n} 字超出30-80")
    if t.get('chapter') != 'biochem_20':
        errors.append(f"term[{t.get('id')}] chapter 非 biochem_20")
    for f in ['id', 'term', 'name', 'definition', 'chapter']:
        if f not in t:
            errors.append(f"term[{t.get('id')}] 缺 {f}")

if not (15 <= len(ts) <= 20):
    errors.append(f"terms 数量 {len(ts)} 不在15-20")

# 题型统计
types = Counter(q['type'] for q in qs)
total = len(qs)
multi_pct = types['multi'] / total * 100
short_pct = types['short'] / total * 100
print('题量:', total)
print('题型:', dict(types))
print(f'multi占比: {multi_pct:.1f}% (要求15-20%)')
print(f'short占比: {short_pct:.1f}% (要求10-15%)')
print('terms:', len(ts))

if errors:
    print('发现违规:')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print('全量自检通过: 0 违规')
