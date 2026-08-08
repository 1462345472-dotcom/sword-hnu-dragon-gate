# -*- coding: utf-8 -*-
"""第二十二章 批次合并脚本:组装 questions.json / terms.json,重排 id"""
import sys, json, importlib.util
sys.stdout.reconfigure(encoding='utf-8')

base = r'C:\Users\Lenovo\Desktop\湖南大学\生物化学题库\第二十二章'

def load(name):
    spec = importlib.util.spec_from_file_location(name, f'{base}\\{name}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.questions

all_q = []
for b in ['_ch22_batch1', '_ch22_batch2', '_ch22_batch3', '_ch22_batch4', '_ch22_batch5']:
    qs = load(b)
    print(f'{b}: {len(qs)} 题')
    all_q.extend(qs)

# 重排 id
for i, q in enumerate(all_q, start=1):
    q['id'] = i
    q['options'] = {k: v for k, v in q.get('options', {}).items()}
    assert 'topic' in q, f"Q{i} 缺 topic: {q['question'][:30]}"

with open(f'{base}\\questions.json', 'w', encoding='utf-8') as f:
    json.dump(all_q, f, ensure_ascii=False, indent=1)
print(f'questions.json: {len(all_q)} 题')

# terms
spec = importlib.util.spec_from_file_location('_ch22_terms', f'{base}\\_ch22_terms.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
terms = m.terms
for i, t in enumerate(terms, start=1):
    t['id'] = i
with open(f'{base}\\terms.json', 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=1)
print(f'terms.json: {len(terms)} 个')

from collections import Counter
c = Counter(q['type'] for q in all_q)
total = len(all_q)
for t in ['choice', 'truefalse', 'multi', 'short']:
    n = c.get(t, 0)
    print(f'{t}: {n} ({100.0*n/total:.1f}%)')
print(f'total: {total}, multi比例: {100.0*c.get("multi",0)/total:.1f}%, short比例: {100.0*c.get("short",0)/total:.1f}%')
