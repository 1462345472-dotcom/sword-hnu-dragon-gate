# -*- coding: utf-8 -*-
"""第二十九章 合并出题批次 → questions.json / terms.json"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gen_ch29_a import QA
from gen_ch29_b import QB
from gen_ch29_c import QC
from gen_ch29_d import QD
from gen_ch29_terms import TERMS

questions = QA + QB + QC + QD

# id 连续性校验
ids = [q['id'] for q in questions]
assert ids == list(range(1, len(questions) + 1)), 'id不连续: %s' % ids

with open(os.path.join(HERE, 'questions.json'), 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'terms.json'), 'w', encoding='utf-8') as f:
    json.dump(TERMS, f, ensure_ascii=False, indent=1)

from collections import Counter
c = Counter(q['type'] for q in questions)
print('题目总数:', len(questions))
for t in ['choice', 'truefalse', 'multi', 'short']:
    print('  %-9s %3d  (%4.1f%%)' % (t, c.get(t, 0), 100.0 * c.get(t, 0) / len(questions)))
print('术语总数:', len(TERMS))
print('已写出 questions.json / terms.json')
