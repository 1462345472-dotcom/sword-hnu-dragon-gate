# -*- coding: utf-8 -*-
"""题库全量归档生成器
从《湖南大学题库系统-臻至版.html》提取 QUESTION_BANKS(51 章 questions+terms),
生成 生物化学题库/题库全量归档.json —— 与 HTML 内"导出题库数据"按钮产物同构,
保证 HTML 万一损坏可用本归档重建题库数据。
"""
import io
import json
import os
import re
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, '生物化学题库', '湖南大学题库系统-臻至版.html')
OUT = os.path.join(BASE, '生物化学题库', '题库全量归档.json')


def extract_banks(data):
    """带字符串跳转的花括号配对,提取 var QUESTION_BANKS = {...}; 的对象字面量。"""
    m = re.search(r'var QUESTION_BANKS = ', data)
    if not m:
        raise RuntimeError('QUESTION_BANKS declaration not found in ' + SRC)
    start = m.end()
    depth = 0
    i = start
    n = len(data)
    in_str = False
    while i < n:
        c = data[i]
        if in_str:
            if c == '\\' and i + 1 < n:
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return data[start:i + 1]
        i += 1
    raise RuntimeError('QUESTION_BANKS braces unbalanced')


def main():
    data = open(SRC, encoding='utf-8').read()
    seg = extract_banks(data)
    banks = json.loads(seg)
    qc = sum(len(b.get('questions', [])) for b in banks.values())
    tc = sum(len(b.get('terms', [])) for b in banks.values())
    archive = {
        'app': 'hnu-academy',
        'type': 'bank-archive',
        'version': 1,
        'exportedAt': datetime.now().isoformat(),
        'bankCount': len(banks),
        'questionCount': qc,
        'termCount': tc,
        'banks': banks,
    }
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(archive, f, ensure_ascii=False, indent=1)
    print('OK: %d banks / %d questions / %d terms -> %s (%.1f MB)'
          % (len(banks), qc, tc, OUT, os.path.getsize(OUT) / 1e6))


if __name__ == '__main__':
    main()
    sys.exit(0)
