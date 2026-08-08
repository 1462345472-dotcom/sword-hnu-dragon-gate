# -*- coding: utf-8 -*-
"""细胞9-10章 跨科/全库查重: 新题 vs 生化全库 + 细胞全部章(含本章内部)"""
import re, json, os, sys

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'

def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】\'"《》\-—…·~～+＋×]', '', s or '')

def norm_wo_qmark(s):
    """去引导词与尾部动词,保留题干主体,用于跨题干查重"""
    t = norm(s)
    t = re.sub(r'[?？]$', '', t)
    t = re.sub(r'(正确的是|正确的有|错误的有|错误的是|不包括|包括|属于|不属于|描述正确的是|描述错误的是|其主要功能是|是指|是|为|有)$', '', t)
    t = re.sub(r'^(以下|下列|下列关于|关于|对于|关于)', '', t)
    return t

def load_chapter_qs(root, chapter):
    p = os.path.join(root, chapter, 'questions.json')
    if not os.path.exists(p):
        return []
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception:
        return []

def collect_all(root):
    """返回 {norm_q: [(chapter, raw_q)]}"""
    table = {}
    for ch in os.listdir(root):
        d = os.path.join(root, ch)
        if not os.path.isdir(d):
            continue
        for q in load_chapter_qs(root, ch):
            qq = norm(q.get('question', ''))
            table.setdefault(qq, []).append((ch, q))
            qq2 = norm_wo_qmark(q.get('question', ''))
            if qq2 and qq2 != qq:
                table.setdefault(qq2, []).append((ch, q))
    return table

bio_table = collect_all(os.path.join(BASE, '生物化学题库'))
cell_table = collect_all(os.path.join(BASE, '细胞生物学题库'))

print('生化全库 norm 题干(含主干):', len(bio_table))
print('细胞全库 norm 题干(含主干):', len(cell_table))

report = []
for ch in ['第九章', '第十章']:
    qs = load_chapter_qs(os.path.join(BASE, '细胞生物学题库'), ch)
    print('\n=== %s 共 %d 题 ===' % (ch, len(qs)))
    for q in qs:
        qq = norm(q.get('question', ''))
        qq2 = norm_wo_qmark(q.get('question', ''))
        # 跨库检查(排除本章自身)
        hits = []
        for tname, table in [('生化', bio_table), ('细胞', cell_table)]:
            for key in {qq, qq2}:
                if key in table:
                    for (src_ch, src_q) in table[key]:
                        if src_ch == ch:
                            continue  # 本章内部
                        hits.append('%s-%s(id=%s)' % (tname, src_ch, src_q.get('id')))
        if hits:
            report.append((ch, q['id'], q['question'][:40], hits))
            print('  重复[%s]: id=%d %s <-> %s' % (ch, q['id'], q['question'][:40], '; '.join(hits)))

    # 本章内部重复(两两比较 norm 主干)
    seen = {}
    for q in qs:
        key = norm_wo_qmark(q.get('question', ''))
        if key in seen:
            print('  章内重复: id=%d %s <-> id=%d %s' % (
                seen[key]['id'], seen[key]['question'][:40], q['id'], q['question'][:40]))
        seen[key] = q

print('\n共发现跨库重复 %d 条' % len(report))
