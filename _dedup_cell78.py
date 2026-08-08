# -*- coding: utf-8 -*-
"""跨科查重: 第七章/第八章 全部题目 vs 生化全库 + 细胞生物学已入库章节
精确查重(题干归一化完全相同) + 模糊查重(相似度>=0.85)"""
import json, glob, os, re
from difflib import SequenceMatcher

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'
TARGETS = ['第七章', '第八章']
EXCLUDED = ['第一章绪论', '第二章', '第三章', '第四章', '第五章', '第六章',
            '第九章', '第十章', '第十一章', '第十二章',
            '第十三章', '第十四章', '第十五章', '第十六章']

def norm(s):
    s = re.sub(r'[\s，。、；：！？（）()“”""\'\'·~~\-—]+', '', s)
    return s

# 收集对照库: 生化全库 + 细胞其他章节
bank = {}  # (type, norm_q) -> [(file, id)]
bank_raw = []  # (type, q) for fuzzy

def load_all():
    cnt = 0
    # 生化全库
    for f in sorted(glob.glob(os.path.join(BASE, '生物化学题库', '*', 'questions.json'))):
        try:
            with open(f, encoding='utf-8') as fh:
                qs = json.load(fh)
        except Exception:
            continue
        for q in qs:
            bank_raw.append((q.get('type'), q.get('question', '')))
            bank.setdefault((q.get('type'), norm(q.get('question', ''))), []).append((os.path.relpath(f, BASE), q.get('id')))
            cnt += 1
    # 细胞其他章节
    for ch in EXCLUDED:
        f = os.path.join(BASE, '细胞生物学题库', ch, 'questions.json')
        if not os.path.exists(f):
            continue
        with open(f, encoding='utf-8') as fh:
            qs = json.load(fh)
        for q in qs:
            bank_raw.append((q.get('type'), q.get('question', '')))
            bank.setdefault((q.get('type'), norm(q.get('question', ''))), []).append((os.path.relpath(f, BASE), q.get('id')))
            cnt += 1
    return cnt

def check_chapter(ch):
    f = os.path.join(BASE, '细胞生物学题库', ch, 'questions.json')
    with open(f, encoding='utf-8') as fh:
        qs = json.load(fh)
    exact_hits, fuzzy_hits = [], []
    for q in qs:
        key = (q.get('type'), norm(q.get('question', '')))
        src = bank.get(key, [])
        if src:
            exact_hits.append((q['id'], q['type'], q['question'][:40], src[:2]))
        # 模糊
        for bt, bq in bank_raw:
            if not bq or len(bq) < 15:
                continue
            r = SequenceMatcher(None, norm(q.get('question','')), norm(bq)).ratio()
            if r >= 0.85:
                fuzzy_hits.append((q['id'], q['type'], round(r, 2), q['question'][:30], bq[:30]))
                break
    return exact_hits, fuzzy_hits

def check_terms():
    """术语名重名检查"""
    terms = {}
    for ch in EXCLUDED + ['第七章', '第八章']:
        f = os.path.join(BASE, '细胞生物学题库', ch, 'terms.json')
        if not os.path.exists(f):
            continue
        with open(f, encoding='utf-8') as fh:
            ts = json.load(fh)
        for t in ts:
            name = t.get('term') if isinstance(t, dict) else t[1]
            terms.setdefault(name, []).append(ch)
    # 生化术语
    for f in sorted(glob.glob(os.path.join(BASE, '生物化学题库', '*', 'terms.json'))):
        with open(f, encoding='utf-8') as fh:
            ts = json.load(fh)
        for t in ts:
            name = t.get('term') if isinstance(t, dict) else t[1]
            terms.setdefault(name, []).append(os.path.basename(os.path.dirname(f)))
    return terms

n = load_all()
print('对照库题目总数:', n)

all_ok = True
for ch in TARGETS:
    exact, fuzzy = check_chapter(ch)
    print(f'\n===== {ch} =====')
    if exact:
        all_ok = False
        print('  [精确重复', len(exact), '条]')
        for e in exact[:10]:
            print('   ', e)
    else:
        print('  精确查重: 0 重复')
    if fuzzy:
        all_ok = False
        print('  [模糊重复(>=0.85)', len(fuzzy), '条]')
        for e in fuzzy[:10]:
            print('   ', e)
    else:
        print('  模糊查重(>=0.85): 0 重复')

# 章内查重
print('\n===== 章内查重 =====')
for ch in TARGETS:
    f = os.path.join(BASE, '细胞生物学题库', ch, 'questions.json')
    with open(f, encoding='utf-8') as fh:
        qs = json.load(fh)
    seen = {}
    dup = []
    for q in qs:
        k = norm(q['question'])
        if k in seen:
            dup.append((seen[k], q['id']))
        seen[k] = q['id']
    print(f'{ch}: 章内重复 {len(dup)} 条' + (str(dup) if dup else ''))

# 术语查重(生化+细胞全库)
print('\n===== 术语跨库查重(第七章/第八章 terms vs 全库) =====')
terms = check_terms()
for ch in ['第七章', '第八章']:
    f = os.path.join(BASE, '细胞生物学题库', ch, 'terms.json')
    with open(f, encoding='utf-8') as fh:
        ts = json.load(fh)
    for t in ts:
        name = t.get('term') if isinstance(t, dict) else t[1]
        dup = [c for c in terms[name] if c != ch]
        if dup:
            all_ok = False
            print(f'  [{ch}] {name} 与 {dup} 重名')

print('\n结论:', 'FAIL 存在重复' if not all_ok else 'PASS 0 重复')
