# -*- coding: utf-8 -*-
import sys, json, glob, re, os
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】]', '', s or '')

bank = {}
for f in sorted(glob.glob('生物化学题库/**/questions.json', recursive=True)):
    try:
        qs = json.load(open(f, encoding='utf-8'))
    except Exception:
        continue
    parts = f.replace(os.sep, '/').split('/')
    ch = parts[1] if len(parts) > 1 else f
    for q in qs:
        bank.setdefault(norm(q.get('question', '')), []).append((ch, q['id']))

total = sum(len(v) for v in bank.values())
print('全库题目总数:', total)

dups = {k: v for k, v in bank.items() if len(v) > 1 and all(c == '第七章' for c, _ in v)}
print('第七章章内重复:', len(dups))
for k, v in dups.items():
    print(' ', v)

new_ids = set(range(75, 86))
cross = 0
for k, v in bank.items():
    chapters = {c for c, _ in v}
    if len(chapters) > 1:
        for c, i in v:
            if c == '第七章' and i in new_ids:
                cross += 1
                print('跨章重复(新题):', i, k[:40], v)
print('新题 75-85 与其他章节数据重复:', cross)
