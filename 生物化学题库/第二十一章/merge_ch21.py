# -*- coding: utf-8 -*-
"""合并第二十一章分片为 questions.json,重排id,并做基础自检"""
import json, sys, os
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

base = os.path.dirname(os.path.abspath(__file__))
parts = ['_part_a.json', '_part_b.json', '_part_c.json', '_part_d.json', '_part_e.json']

all_q = []
for p in parts:
    with open(os.path.join(base, p), encoding='utf-8') as f:
        chunk = json.load(f)
        all_q.extend(chunk)
    print(f'{p}: {len(chunk)} 题')

# 重排 id
for i, q in enumerate(all_q):
    q['id'] = i + 1

with open(os.path.join(base, 'questions.json'), 'w', encoding='utf-8') as f:
    json.dump(all_q, f, ensure_ascii=False, indent=1)

print('total:', len(all_q))
print('types:', dict(Counter(q['type'] for q in all_q)))
print('topics:', len(set(q['topic'] for q in all_q)))
# 基础自检
ids = [q['id'] for q in all_q]
assert ids == list(range(1, len(all_q) + 1)), 'id 不连续'
assert len(set(ids)) == len(ids), 'id 重复'
for q in all_q:
    if q['type'] in ('choice', 'multi'):
        assert set(q['answer']) <= set(q['options'].keys()), f"Q{q['id']} 答案不在选项中"
    if q['type'] == 'multi':
        assert len(q['answer']) == len(set(q['answer'])), f"Q{q['id']} 多选答案重复"
        assert len(q['answer']) >= 2, f"Q{q['id']} 多选答案过少"
    if q['type'] == 'truefalse':
        assert q['answer'] in ('true', 'false'), f"Q{q['id']} TF答案非法"
print('基础自检通过')
