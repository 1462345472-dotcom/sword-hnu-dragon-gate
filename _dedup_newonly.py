# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】\[\]]', '', s or '')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'
html = open(BASE + r'\生物化学题库\湖南大学题库系统-剑指湖大一战成硕.html', encoding='utf-8', errors='ignore').read()
bio_existing = re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
bio_ns = set(normalize(t) for t in bio_existing)
bio_pre = set(n[:12] for n in bio_ns if len(n) >= 8)
print('生化HTML全库题干: %d 条' % len(bio_existing))

# 新增题 id 范围;94/95/107/108 为修改题
new_ids3 = list(range(118, 191))
new_ids4 = list(range(112, 194)) + [94, 95, 107, 108]

for ch, new_ids in [('第三章', new_ids3), ('第四章', new_ids4)]:
    qs = json.load(open('%s\\细胞生物学题库\\%s\\questions.json' % (BASE, ch), encoding='utf-8'))
    new_qs = [q for q in qs if q['id'] in new_ids]
    dups = []
    for q in new_qs:
        n = normalize(q.get('question', ''))
        if n in bio_ns or n[:12] in bio_pre:
            dups.append(q.get('question', '')[:45])
    print('[%s] 新增/修改题 %d 条, 与生化全库重复: %d 条' % (ch, len(new_qs), len(dups)))
    for d in dups:
        print('  重复:', d)
