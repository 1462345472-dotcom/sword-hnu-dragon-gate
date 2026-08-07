# -*- coding: utf-8 -*-
"""第十七章 题库数据生成脚本:合并数据分片 → questions.json / terms.json"""
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE)
from gen_data_p1 import PART1
from gen_data_p2 import PART2
from gen_data_p3 import PART3
from gen_data_p4 import PART4, TERMS

QUESTIONS = PART1 + PART2 + PART3 + PART4

def main():
    # 检查 id 连续
    ids = [q['id'] for q in QUESTIONS]
    assert ids == list(range(1, len(QUESTIONS) + 1)), 'id 不连续! %s' % ids

    # 检查 terms id
    tids = [t['id'] for t in TERMS]
    assert tids == list(range(1, len(TERMS) + 1)), 'terms id 不连续!'

    # 检查每项必有 topic(第十五章格式含 topic)
    missing_topic = [q['id'] for q in QUESTIONS if 'topic' not in q]
    assert not missing_topic, '缺少 topic: %s' % missing_topic

    # 统计题型
    from collections import Counter
    c = Counter(q['type'] for q in QUESTIONS)
    print('题型统计:', dict(c), '合计', len(QUESTIONS))
    print('terms 数量:', len(TERMS))

    with open(os.path.join(BASE, 'questions.json'), 'w', encoding='utf-8') as f:
        json.dump(QUESTIONS, f, ensure_ascii=False, indent=2)
    with open(os.path.join(BASE, 'terms.json'), 'w', encoding='utf-8') as f:
        json.dump(TERMS, f, ensure_ascii=False, indent=2)
    print('已写入 questions.json(%d题) / terms.json(%d个)' % (len(QUESTIONS), len(TERMS)))

if __name__ == '__main__':
    main()
