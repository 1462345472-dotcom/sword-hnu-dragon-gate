# inject_chapter.py
# -*- coding: utf-8 -*-
"""把新章节数据对象插入臻至版 HTML 的章节字典(biochem_14 之后)。
关键安全点:只插入一个对象;用 JSONDecoder.raw_decode 精确定位插入点。"""
import json, sys, re

def build_chapter_obj(chapter_key, label, questions, terms):
    qty = {"choice": 0, "truefalse": 0, "multi": 0, "short": 0}
    for q in questions:
        qty[q.get("type", "")] = qty.get(q.get("type", ""), 0) + 1
    stats = {"total": len(questions), **qty, "terms": len(terms)}
    obj = {
        "key": chapter_key, "name": "生物化学", "code": "338",
        "chapterLabel": label, "questions": questions,
        "terms": terms, "stats": stats,
    }
    return json.dumps(obj, ensure_ascii=False, indent=1)

def inject(html, obj_text, after_key):
    """在 after_key 对象结束后插入 ,"key":{...};返回新 html"""
    dec = json.JSONDecoder()
    m = re.search(r'"' + re.escape(after_key) + r'"\s*:\s*\{', html)
    if not m:
        raise ValueError(f"未找到章节 {after_key}")
    _, endpos = dec.raw_decode(html[m.start() + m.group(0).rfind('{'):])
    insert_at = m.start() + m.group(0).rfind('{') + endpos
    key_m = re.search(r'"key"\s*:\s*"([^"]+)"', obj_text)
    if not key_m:
        raise ValueError("obj_text 缺少 key 字段")
    key = key_m.group(1)
    return html[:insert_at] + ',"' + key + '":' + obj_text + html[insert_at:]

def main():
    key = "biochem_15"
    label = "15 新陈代谢总论"
    questions = json.load(open("生物化学题库/第十五章/questions.json", encoding="utf-8"))
    terms = json.load(open("生物化学题库/第十五章/terms.json", encoding="utf-8"))
    for t in terms:
        t["chapter"] = key
    obj_text = build_chapter_obj(key, label, questions, terms)
    path = "生物化学题库/湖南大学题库系统-臻至版.html"
    html = open(path, encoding="utf-8", errors="ignore").read()
    new_html = inject(html, obj_text, after_key="biochem_14")
    # CHAPTER_NAMES 同步
    m = re.search(r'CHAPTER_NAMES\s*=\s*\{', new_html)
    if m:
        new_html = new_html[:m.end()] + '"' + key + '":"第十五章 新陈代谢总论",' + new_html[m.end():]
    open(path, "w", encoding="utf-8").write(new_html)
    print(f"已插入 {key}({len(questions)} 题, {len(terms)} 术语)")

if __name__ == "__main__":
    main()
