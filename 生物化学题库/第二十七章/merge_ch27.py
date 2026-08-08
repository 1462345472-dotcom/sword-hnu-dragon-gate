# -*- coding: utf-8 -*-
# 合并 batch1-4 生成 questions.json + terms.json
import sys, json, io, importlib.util
sys.stdout.reconfigure(encoding='utf-8')

def load(name):
    spec = importlib.util.spec_from_file_location(name, f'生物化学题库/第二十七章/{name}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

qs = []
for b in ['batch1', 'batch2', 'batch3', 'batch4', 'batch5']:
    mod = load(b)
    qs.extend(mod.QUESTIONS)
    print(f'{b}: {len(mod.QUESTIONS)} 题, 当前累计 {len(qs)}')

terms = load('terms_batch').TERMS

# truefalse 答案统一为 true/false
for x in qs:
    if x['type'] == 'truefalse' and x.get('answer') in ('A', 'B'):
        x['answer'] = 'true' if x['answer'] == 'A' else 'false'

# 按列表顺序统一重排 id(查重删除后保持连续)
for i, x in enumerate(qs, 1):
    x['id'] = i
tids = [t['id'] for t in terms]
assert tids == list(range(1, len(terms)+1)), 'term id 不连续'

json.dump(qs, io.open('生物化学题库/第二十七章/questions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(terms, io.open('生物化学题库/第二十七章/terms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

from collections import Counter
print('questions:', len(qs), '| terms:', len(terms))
print('题型分布:', dict(Counter(q['type'] for q in qs)))
print('难度分布:', dict(Counter(q['difficulty'] for q in qs)))
print('话题分布:')
for t, c in Counter(q['topic'] for q in qs).most_common():
    print(f'  {t}: {c}')
