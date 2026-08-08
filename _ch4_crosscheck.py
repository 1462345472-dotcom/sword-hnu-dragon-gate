# -*- coding: utf-8 -*-
"""第四章跨章查重:同章内重复 + 与其他章节 questions.json 之间重复。"""
import re, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】]', '', s or '')

BASE = '生物化学题库'
q4 = json.load(open(f'{BASE}/第四章/questions.json', encoding='utf-8'))
n4 = [norm(q['question']) for q in q4]

# 1. 同章内重复
from collections import Counter
c = Counter(n4)
inner = [q for q, cnt in c.items() if cnt > 1]
print(f'同章内重复题干: {len(inner)} {inner if inner else "(无)"}')

# 2. 跨章重复:第四章 vs 其他章目录
total_other = 0
cross = []
for d in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, d)
    if not os.path.isdir(p) or d == '第四章':
        continue
    qf = os.path.join(p, 'questions.json')
    if not os.path.exists(qf):
        continue
    try:
        oq = json.load(open(qf, encoding='utf-8'))
    except Exception as e:
        print(f'{d}: 读取失败 {e}')
        continue
    if not isinstance(oq, list):
        continue
    total_other += len(oq)
    for q in oq:
        if not isinstance(q, dict) or 'question' not in q:
            continue
        n = norm(q['question'])
        if n in set(n4):
            cross.append((d, q.get('id'), q.get('question', '')[:40]))

print(f'其他章节总题数: {total_other}')
print(f'跨章重复: {len(cross)} 条')
for d, i, q in cross:
    print(f'  {d} #{i}: {q}')
