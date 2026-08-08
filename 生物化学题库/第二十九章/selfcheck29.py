# -*- coding: utf-8 -*-
"""第二十九章 自检: id连续 / answer合法 / 名解30-80字 / topic覆盖 / 重复检查"""
import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

qs = json.load(open('questions.json', encoding='utf-8'))
ts = json.load(open('terms.json', encoding='utf-8'))
errors = []

# 1. id 连续
ids = [q['id'] for q in qs]
if ids != list(range(1, len(qs) + 1)):
    errors.append('id不连续')
else:
    print('id 1..%d 连续 OK' % len(qs))

# 2. answer 合法性
for q in qs:
    if q['type'] in ('choice', 'multi'):
        for ch in q['answer']:
            if ch not in q.get('options', {}):
                errors.append('#%d answer字符%s不在options' % (q['id'], ch))
        if q['type'] == 'multi' and len(q['answer']) < 2:
            errors.append('#%d multi答案少于2个选项' % q['id'])
    if q['type'] == 'truefalse':
        if q['answer'] not in ('true', 'false'):
            errors.append('#%d tf答案非法: %s' % (q['id'], q['answer']))
    if q['type'] == 'short':
        if len(q['answer']) < 5:
            errors.append('#%d short答案过短' % q['id'])
print('answer 合法性 OK' if not errors else errors)

# 3. 名解字数 30-80
for t in ts:
    n = len(t['definition'])
    if not (30 <= n <= 80):
        errors.append('术语#%d %s 定义字数%d 不在30-80' % (t['id'], t['term'], n))
print('名解字数检查完成')

# 4. topic 覆盖统计
topics = Counter(q['topic'] for q in qs)
print('topic 分布:')
for k, v in sorted(topics.items()):
    print('   %-14s %2d' % (k, v))

# 5. 本文件内题干重复
seen = set()
dup = []
for q in qs:
    s = q['question'].strip()
    if s in seen:
        dup.append('#%d %s' % (q['id'], s[:40]))
    seen.add(s)
print('文件内重复题干:', dup if dup else '无')

# 6. 术语与题干对应
term_names = [t['term'] for t in ts]
print('术语列表(%d):' % len(ts), '、'.join(term_names))

print('\n结果:', 'PASS' if not errors else 'FAIL %d 项' % len(errors))
for e in errors:
    print(' -', e)
