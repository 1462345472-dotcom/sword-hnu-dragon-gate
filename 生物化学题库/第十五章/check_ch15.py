# -*- coding: utf-8 -*-
"""第十五章数据自检:字段/答案格式/名解长度/题型占比/考点覆盖/重复检测"""
import json, os
from collections import Counter

base = r'C:\Users\Lenovo\Desktop\湖南大学\生物化学题库\第十五章'
Q = json.load(open(os.path.join(base, 'questions.json'), encoding='utf-8'))
T = json.load(open(os.path.join(base, 'terms.json'), encoding='utf-8'))

errors = []
print('===== 1. 基础结构与答案格式 =====')
for q in Q:
    i = q['id']
    for f in ['id', 'topic', 'type', 'question', 'answer', 'explanation', 'difficulty', 'tags']:
        if f not in q:
            errors.append('[Q%d] 缺字段 %s' % (i, f))
    t = q['type']
    if t in ('choice', 'multi'):
        opts = q.get('options', {})
        if len(opts) < 4:
            errors.append('[Q%d] %s选项数<4: %d' % (i, t, len(opts)))
        for k in opts:
            if k not in 'ABCDEFGH' or not opts[k].strip():
                errors.append('[Q%d] options键异常: %s' % (i, k))
        for ch in str(q.get('answer', '')):
            if ch not in opts:
                errors.append('[Q%d] 答案"%s"不在options中' % (i, q.get('answer')))
    if t == 'truefalse':
        if str(q['answer']).lower() not in ('true', 'false'):
            errors.append('[Q%d] truefalse答案非法: %s' % (i, q['answer']))
    if t == 'short':
        if 'options' in q and q.get('options'):
            errors.append('[Q%d] short不应有options' % i)
        if len(str(q.get('answer', ''))) < 5:
            errors.append('[Q%d] short答案过短' % i)
    if q['difficulty'] not in (1, 2, 3):
        errors.append('[Q%d] difficulty非法: %s' % (i, q['difficulty']))

ids = [q['id'] for q in Q]
if ids != list(range(1, len(Q) + 1)):
    errors.append('id不连续: %s' % ids)
print('id连续: %s' % (ids == list(range(1, len(Q) + 1))))

print('===== 2. 题型分布 =====')
c = Counter(q['type'] for q in Q)
total = len(Q)
for t in ['choice', 'truefalse', 'multi', 'short']:
    n = c.get(t, 0)
    print('%s: %d (%.1f%%)' % (t, n, 100.0 * n / total))
print('total: %d, multi比例: %.1f%% (要求15-20%%), short比例: %.1f%% (要求10-15%%)' % (
    total, 100.0 * c.get('multi', 0) / total, 100.0 * c.get('short', 0) / total))
if not (0.15 <= c.get('multi', 0) / total <= 0.20):
    errors.append('multi比例不达标')
if not (0.10 <= c.get('short', 0) / total <= 0.15):
    errors.append('short比例不达标')

print('===== 3. 名词解释长度(30-80字) =====')
bad_terms = []
for t in T:
    n = len(t['definition'])
    if not (30 <= n <= 80):
        bad_terms.append((t['term'], n))
    print('%s: %d字 %s' % (t['term'], n, 'OK' if 30 <= n <= 80 else '!!超界'))
if bad_terms:
    errors.append('名解长度超界: %s' % bad_terms)
tids = [t['id'] for t in T]
if tids != list(range(1, len(T) + 1)):
    errors.append('terms id不连续')
for f in ['id', 'term', 'name', 'definition', 'chapter']:
    for t in T:
        if f not in t:
            errors.append('[T%d] terms缺字段 %s' % (t.get('id'), f))
        if f == 'chapter' and t['chapter'] != 'biochem_15':
            errors.append('[T%d] chapter错误: %s' % (t.get('id'), t['chapter']))

print('===== 4. 考点覆盖 =====')
# 考点 -> 题量映射(用 topic 关键词粗查,再人工核对)
topic_cnt = Counter(q['topic'] for q in Q)
for k, v in sorted(topic_cnt.items()):
    print('%s: %d题' % (k, v))

print('===== 5. 重复/近似题检测 =====')
qs = [q['question'] for q in Q]
dup = [x for x in set(qs) if qs.count(x) > 1]
print('完全重复题目: %d' % len(dup))
if dup:
    errors.append('重复题目: %s' % dup)

print('===== 6. terms数量 =====')
print('terms: %d (要求15-20)' % len(T))
if not (15 <= len(T) <= 20):
    errors.append('terms数量不达标')

print('===== 7. OCR残缺标注 =====')
ocr = [q['id'] for q in Q if any('OCR残缺补全' in x for x in q['tags'])]
print('带OCR残缺补全标签的题: %s (共%d题)' % (ocr, len(ocr)))

print()
if errors:
    print('!!! 自检发现 %d 处问题:' % len(errors))
    for e in errors:
        print(' -', e)
else:
    print('!!! 全部自检通过')
