# replace_chapter.py
# -*- coding: utf-8 -*-
"""用重审后的数据替换臻至版 HTML 中的章节对象。
用法: python replace_chapter.py <key> <questions.json> <terms.json>
只替换目标对象的 questions/terms/stats,保留 key/name/code/chapterLabel,不动任何其他内容。"""
import json, re, sys

PATH = '生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html'

def build_obj(key, old_obj, questions, terms):
    qty = {"choice": 0, "truefalse": 0, "multi": 0, "short": 0}
    for q in questions:
        qty[q.get("type", "")] = qty.get(q.get("type", ""), 0) + 1
    obj = {
        "key": key,
        "name": old_obj.get("name", "生物化学"),
        "code": old_obj.get("code", "338"),
        "chapterLabel": old_obj.get("chapterLabel", ""),
        "questions": questions,
        "terms": terms,
        "stats": {"total": len(questions), **qty, "terms": len(terms)},
    }
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

def replace_chapter(html, key, questions, terms):
    m = re.search(r'"' + re.escape(key) + r'"\s*:\s*\{', html)
    if not m:
        raise ValueError(f'未找到章节 {key}')
    dec = json.JSONDecoder()
    start = m.start() + m.group(0).rfind('{')
    old_obj, endpos = dec.raw_decode(html[start:])
    new_text = build_obj(key, old_obj, questions, terms)
    return html[:start] + new_text + html[start + endpos:]

def main():
    key = sys.argv[1]
    qs = json.load(open(sys.argv[2], encoding='utf-8'))
    ts = json.load(open(sys.argv[3], encoding='utf-8'))
    for t in ts:
        t['chapter'] = key
    html = open(PATH, encoding='utf-8', errors='ignore').read()
    new_html = replace_chapter(html, key, qs, ts)
    open(PATH, 'w', encoding='utf-8').write(new_html)
    print(f'已替换 {key}: {len(qs)} 题, {len(ts)} 术语')

if __name__ == '__main__':
    main()
