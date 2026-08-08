# review_scanner.py
# -*- coding: utf-8 -*-
"""章节重审疑点扫描器:格式问题/知识疑点/考纲缺口。"""
import json, re, os, sys

def scan_chapter(questions, terms, syllabus_points):
    r = {'format': [], 'knowledge': [], 'syllabus_gap': []}
    # 格式问题
    ids = [q.get('id') for q in questions]
    if ids != list(range(1, len(questions) + 1)):
        r['format'].append(f"id 不连续: {ids[:5]}...")
    for q in questions:
        t = q.get('type')
        if t in ('choice', 'multi'):
            opts = q.get('options', {})
            vals = list(opts.values())
            if len(vals) != len(set(vals)):
                r['format'].append(f"Q{q.get('id')}: 选项重复 {q.get('question','')[:30]}")
            if t == 'multi' and len(vals) < 4:
                r['format'].append(f"Q{q.get('id')}: multi 选项不足4")
            if q.get('answer') not in opts:
                r['format'].append(f"Q{q.get('id')}: 答案不在选项内")
        elif t == 'truefalse':
            if str(q.get('answer')) not in ('true', 'false'):
                r['format'].append(f"Q{q.get('id')}: truefalse 答案非法 '{q.get('answer')}'")
        elif t == 'short':
            if not q.get('answer') or not re.search(r'[①②③]', str(q.get('answer'))):
                r['format'].append(f"Q{q.get('id')}: short 答案未分点")
        if not q.get('explanation') or len(str(q.get('explanation'))) < 10:
            r['format'].append(f"Q{q.get('id')}: 解析过短/为空")
        # 知识疑点:年代类
        if t != 'short' and re.search(r'(19\d{2}|20\d{2})年', str(q.get('question'))):
            r['knowledge'].append(f"Q{q.get('id')}: 疑似年代题")
    for t in terms:
        d = t.get('definition', '')
        if not (30 <= len(d) <= 80):
            r['format'].append(f"术语 '{t.get('term','')}': 名解 {len(d)} 字(需30-80)")
    # 考纲缺口(topic 与考纲条目匹配)
    have_topics = {q.get('topic', '') for q in questions if q.get('topic')}
    for sp in syllabus_points:
        pt = sp.get('point', '')
        if any(k in pt for k in ('考试', '题型', '参考教材')):
            continue
        if not any(topic and topic in pt for topic in have_topics) and not any(pt[:8] in str(topic) for topic in have_topics):
            r['syllabus_gap'].append(f"考纲条目未覆盖: {pt[:40]}")
    return r

def main():
    d = sys.argv[1]
    qs = json.load(open(os.path.join(d, 'questions.json'), encoding='utf-8'))
    ts = json.load(open(os.path.join(d, 'terms.json'), encoding='utf-8'))
    sp = []
    sp_path = 'docs/superpowers/specs/考纲考点清单.json'
    if os.path.exists(sp_path):
        sp = json.load(open(sp_path, encoding='utf-8'))
    r = scan_chapter(qs, ts, sp)
    out = os.path.join(d, '疑点清单.json')
    json.dump(r, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"格式问题 {len(r['format'])} | 知识疑点 {len(r['knowledge'])} | 考纲缺口 {len(r['syllabus_gap'])} → {out}")

if __name__ == '__main__':
    main()
