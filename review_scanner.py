# review_scanner.py
# -*- coding: utf-8 -*-
"""章节重审疑点扫描器:格式问题/知识疑点/考纲缺口。"""
import json, re, os, sys

def _answer_ok(t, ans, opts):
    """校验答案与选项的对应关系:multi 组合答案拆字符逐个检查,并查字符重复。"""
    if t == 'multi':
        chars = str(ans)
        bad = [c for c in chars if c not in opts]
        if bad:
            return f"答案不在选项内 '{ans}'"
        if len(set(chars)) != len(chars):
            return f"multi 答案字符重复 '{ans}'"
        return None
    if ans not in opts:
        return "答案不在选项内"
    return None

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
            msg = _answer_ok(t, q.get('answer'), opts)
            if msg:
                r['format'].append(f"Q{q.get('id')}: {msg}")
        elif t == 'truefalse':
            if str(q.get('answer')) not in ('true', 'false'):
                r['format'].append(f"Q{q.get('id')}: truefalse 答案非法 '{q.get('answer')}'")
        elif t == 'short':
            if not q.get('answer') or not re.search(r'[①②③]|\(\d+\)|\d+[.、]', str(q.get('answer'))):
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
    # 考纲缺口(topic 与考纲条目双向匹配)
    have_topics = [str(q.get('topic', '')) for q in questions if q.get('topic')]
    for sp in syllabus_points:
        pt = sp.get('point', '')
        if any(k in pt for k in ('考试', '题型', '参考教材')):
            continue
        if not _syllabus_covered(pt, have_topics):
            r['syllabus_gap'].append(f"考纲条目未覆盖: {pt[:40]}")
    return r

_STOP_CHARS = set('的了和与及或其等在是并这那之,，、。()（）;；:：""\'\' ')

def _bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)
            if not any(c in _STOP_CHARS for c in s[i:i + 2])}

def _syllabus_covered(pt, topics):
    """双向匹配:考纲条目含 topic 关键词,或 topic 含考纲条目关键词;
    再放宽一层:双方共享任意 2 字实义词片段。"""
    for topic in topics:
        if not topic:
            continue
        if topic in pt or pt in topic:
            return True
    pt_grams = _bigrams(pt)
    for topic in topics:
        if topic and _bigrams(topic) & pt_grams:
            return True
    return False

def extract_topics(chapter_dir):
    """从章目录名提取主题关键词,如 '第七章 酶动力学' → ['酶动力学'];
    纯数字章名(如 '第七章')返回空列表。"""
    name = os.path.basename(chapter_dir)
    m = re.sub(r'^第[一二三四五六七八九十百千0-9]+章', '', name)
    m = re.sub(r'^[一二三四五六七八九十百千0-9]+\+', '', m)
    return [p for p in re.split(r'[+\s\-、,，]', m) if p]

def filter_syllabus(syllabus_points, topics):
    """按章节主题关键词过滤考纲条目:考纲条目 point 含任一关键词 → 保留;
    无任何命中时保留全部条目作为参考;topics 为空时不过滤。"""
    if not topics:
        return syllabus_points
    kept = [x for x in syllabus_points
            if any(t and t in str(x.get('point', '')) for t in topics)]
    return kept if kept else syllabus_points

def main():
    d = sys.argv[1]
    qs = json.load(open(os.path.join(d, 'questions.json'), encoding='utf-8'))
    ts = json.load(open(os.path.join(d, 'terms.json'), encoding='utf-8'))
    topics = []
    if '--topics' in sys.argv:
        i = sys.argv.index('--topics')
        topics = [p for p in re.split(r'[,，、\s]+', sys.argv[i + 1]) if p]
    else:
        topics = extract_topics(d)
    sp = []
    sp_path = 'docs/superpowers/specs/考纲考点清单.json'
    if os.path.exists(sp_path):
        sp = filter_syllabus(json.load(open(sp_path, encoding='utf-8')), topics)
    r = scan_chapter(qs, ts, sp)
    out = os.path.join(d, '疑点清单.json')
    json.dump(r, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"格式问题 {len(r['format'])} | 知识疑点 {len(r['knowledge'])} | 考纲缺口 {len(r['syllabus_gap'])} → {out}")

if __name__ == '__main__':
    main()
