# extract_syllabus.py
# -*- coding: utf-8 -*-
"""从考纲识别文本中提取结构化考点清单(按章节条目拆分,保留层级)。"""
import re, json, sys

def extract_syllabus_points(text, chapter_hint=""):
    """把考纲文本按 数字编号条目 拆成考点列表。
    每项: {"point": 原文条目, "source": "考纲", "chapter_hint": chapter_hint}"""
    points = []
    for line in text.splitlines():
        line = line.strip()
        # 匹配形如 "9.糖的分解代谢和合成代谢" 或 "(1) 糖的代谢途径" 的条目
        # 分隔符允许 "."、顿号或空白(简报原正则在 "(1) 后空格" 处不匹配,已修复)
        m = re.match(r'^\(?(\d{1,2})\)?[.、\s]+(.+)$', line)
        if m and len(m.group(2)) >= 2:
            points.append({"point": m.group(2).strip(), "source": "考纲", "chapter_hint": chapter_hint})
    return points

def main():
    src = "338生物化学考纲_识别全文.txt"
    text = open(src, encoding="utf-8").read()
    pts = extract_syllabus_points(text)
    with open("docs/superpowers/specs/考纲考点清单.json", "w", encoding="utf-8") as f:
        json.dump(pts, f, ensure_ascii=False, indent=2)
    print(f"提取 {len(pts)} 条考点 → docs/superpowers/specs/考纲考点清单.json")

if __name__ == "__main__":
    main()
