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
    import argparse
    ap = argparse.ArgumentParser(description="向臻至版 HTML 注入一个生化章节对象")
    ap.add_argument("key", help="章节键,如 biochem_16")
    ap.add_argument("label", help="chapterLabel,如 16 生物能学")
    ap.add_argument("display_name", help="CHAPTER_NAMES 显示名,如 第十六章 生物能学")
    ap.add_argument("questions", help="questions.json 路径")
    ap.add_argument("terms", help="terms.json 路径")
    ap.add_argument("--after", default="biochem_14", help="插入到哪个章节之后(默认 biochem_14)")
    ap.add_argument("--backup", action="store_true", help="注入前先备份 HTML 到 .superpowers/sdd/backups/")
    args = ap.parse_args()

    questions = json.load(open(args.questions, encoding="utf-8"))
    terms = json.load(open(args.terms, encoding="utf-8"))
    for t in terms:
        t["chapter"] = args.key
    obj_text = build_chapter_obj(args.key, args.label, questions, terms)
    path = "生物化学题库/湖南大学题库系统-臻至版.html"
    html = open(path, encoding="utf-8", errors="ignore").read()
    if args.backup:
        import os, time
        os.makedirs(".superpowers/sdd/backups", exist_ok=True)
        bak = f".superpowers/sdd/backups/html_before_{args.key}.html"
        open(bak, "w", encoding="utf-8").write(html)
        print(f"已备份到 {bak}")
    new_html = inject(html, obj_text, after_key=args.after)
    # CHAPTER_NAMES 同步
    m = re.search(r'CHAPTER_NAMES\s*=\s*\{', new_html)
    if m:
        new_html = new_html[:m.end()] + '"' + args.key + '":"' + args.display_name + '",' + new_html[m.end():]
    open(path, "w", encoding="utf-8").write(new_html)
    print(f"已插入 {args.key}({len(questions)} 题, {len(terms)} 术语)")

if __name__ == "__main__":
    main()
