# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
q = json.load(io.open('生物化学题库/第二十七章/questions.json', encoding='utf-8'))
t = json.load(io.open('生物化学题库/第二十七章/terms.json', encoding='utf-8'))
errs = []

# 1. id 连续
ids = [x['id'] for x in q]
if ids != list(range(1, len(q)+1)):
    errs.append('questions id 不连续')
tids = [x['id'] for x in t]
if tids != list(range(1, len(t)+1)):
    errs.append('terms id 不连续')

# 2. answer 合法性与选项
for x in q:
    typ = x['type']
    ans = x['answer']
    opts = x.get('options', {})
    if typ == 'truefalse':
        if ans not in ('true', 'false'):
            errs.append(f'#{x["id"]} TF答案非法: {ans}')
        continue
    if typ == 'short':
        continue
    if not opts:
        errs.append(f'#{x["id"]} 缺少options')
        continue
    keys = sorted(opts.keys())
    if keys != ['A', 'B', 'C', 'D']:
        errs.append(f'#{x["id"]} 选项键不全: {keys}')
    if typ == 'choice':
        if ans not in opts:
            errs.append(f'#{x["id"]} choice答案不在选项中: {ans}')
    elif typ == 'multi':
        if not all(c in opts for c in ans):
            errs.append(f'#{x["id"]} multi答案字母非法: {ans}')
        if ''.join(sorted(ans)) != ans:
            errs.append(f'#{x["id"]} multi答案未按字母排序: {ans}')
        if len(ans) < 2:
            errs.append(f'#{x["id"]} multi答案少于2个: {ans}')
    elif typ == 'short':
        pass
    else:
        errs.append(f'#{x["id"]} 未知题型: {typ}')
    # 选项非空
    for k, v in opts.items():
        if not v.strip():
            errs.append(f'#{x["id"]} 选项{k}为空')

# 3. 必填字段(short 无 options)
for x in q:
    need = ['id', 'type', 'question', 'answer', 'explanation', 'difficulty', 'tags', 'topic']
    if x['type'] != 'short':
        need.append('options')
    for k in need:
        if k not in x:
            errs.append(f'#{x.get("id")} 缺少字段 {k}')
    if x.get('difficulty') not in (1, 2, 3):
        errs.append(f'#{x.get("id")} difficulty非法')

# 4. 名解 30-80 字
for x in t:
    d = x.get('definition', '')
    if not (30 <= len(d) <= 80):
        errs.append(f'term#{x.get("id")} 定义长度 {len(d)} 超限')
    for k in ['id', 'term', 'name', 'definition', 'chapter']:
        if k not in x:
            errs.append(f'term#{x.get("id")} 缺少字段 {k}')

# 5. 简答分点检查
for x in q:
    if x['type'] == 'short' and '①' not in x.get('answer', ''):
        errs.append(f'#{x["id"]} 简答未分点')

# 6. 时间/年代类检查
import re
for x in q:
    if re.search(r'19\d\d年|20\d\d年', x.get('question', '')):
        errs.append(f'#{x["id"]} 出现年代')

# 7. 题干含年份检查(选择类)
if errs:
    print('ERRORS:')
    for e in errs:
        print(' ', e)
    sys.exit(1)
print(f'PASS: {len(q)}题 + {len(t)}术语 全部自查通过')
