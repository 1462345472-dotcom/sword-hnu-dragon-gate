# -*- coding: utf-8 -*-
"""核实考纲缺口真假:缺口考点关键词是否出现在该章题目内容中"""
import json, sys, re, os
sys.stdout.reconfigure(encoding='utf-8')

syllabus = json.load(open('docs/superpowers/specs/细胞考纲考点清单.json', encoding='utf-8'))
cn = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16}

# 每个缺口考点的人工关键词(核心名词)
GAP_KEYWORDS = {
    '细胞生物学的概念及其发展历程': ['细胞生物学', '发展历程', '创立'],
    '其研究的总趋势与重点领域（包括细胞生物学领域的诺贝尔奖项）': ['诺贝尔', '重点领域', '总趋势'],
    '细胞学说内容及意义': ['细胞学说', '施莱登', '施旺'],
    '细胞的同一性和多样性（包括细胞的基本类型）': ['原核', '真核', '同一性', '多样性'],
    '病毒与细胞的相互关系': ['病毒', '噬菌体'],
    '细胞形态的观察方法': ['显微镜', '光镜', '电镜', '观察'],
    '细胞及其组分的分析方法': ['离心', '层析', '电泳', '组分'],
    '动植物细胞的体外培养与细胞工程': ['培养', '细胞工程', '融合', '杂交瘤'],
    '观察细胞的基本方法。研究细胞一般特征及生长、增殖、分化、凋亡等生理过程的基本实验手段': ['实验', '手段', '凋亡', '增殖'],
    'ATP驱动泵与主动运输及其生理意义': ['ATP', '泵', '主动运输', '钠钾', '钙泵'],
    '胞吞作用与胞吐作用，及其参与的生理过程': ['胞吞', '胞吐', '内吞', '外排'],
    '细胞内膜运输（包括囊泡运输的一般过程及COPI和COPI包被膜泡的装配及运输）': ['COPI', 'COPII', '囊泡', '包被'],
    '核仁与核体': ['核仁', '核体'],
}

def search_chapter(d, keywords):
    qf = f'细胞生物学题库/{d}/questions.json'
    if not os.path.exists(qf):
        return None, None
    qs = json.load(open(qf, encoding='utf-8'))
    hits = []
    for q in qs:
        text = str(q.get('question', '')) + str(q.get('explanation', '')) + str(q.get('topic', ''))
        for kw in keywords:
            if kw in text:
                hits.append((q.get('id'), kw, str(q.get('question', ''))[:40]))
                break
    return qs, hits

for d in ['第一章绪论', '第二章', '第三章', '第四章', '第五章', '第六章', '第七章', '第八章']:
    n = num = None
    m = re.match(r'第(.+?)章', d)
    n = cn.get(m.group(1), 99) if m else 99
    qs, _ = search_chapter(d, [''])  # 确保文件存在
    print(f'=== 细胞第{n}章({d}) ===')
    ch_points = [p['point'] for p in syllabus if p['chapter'] == f'cell_{n}']
    for pt in ch_points:
        kws = GAP_KEYWORDS.get(pt)
        if not kws:
            continue
        _, hits = search_chapter(d, kws)
        if hits:
            print(f'  ✅ {pt[:30]}... → 命中 {len(hits)} 题(首例: Q{hits[0][0]} {hits[0][1]})')
        else:
            print(f'  ❌ {pt[:30]}... → 全章无命中 = 真缺口?')
