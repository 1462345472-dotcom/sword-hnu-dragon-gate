# extract_syllabus.py
# -*- coding: utf-8 -*-
"""从考纲识别文本中提取结构化考点清单(按章节条目拆分,保留层级)。"""
import re, json, sys

# 非考点条目关键词(考试说明、题型说明),用于 main() 中过滤出干净的考点对照基线
NON_POINT_MARKERS = ("本考试", "考查目标", "参考教材", "名词解释", "填空题", "选择题", "问答题")

def extract_syllabus_points(text, chapter_hint=""):
    """把考纲文本按 数字编号条目 拆成考点列表。
    每项: {"point": 原文条目, "source": "考纲", "chapter_hint": chapter_hint}"""
    points = []
    for line in text.splitlines():
        line = line.strip()
        # 匹配 "9.糖的分解代谢和合成代谢"、"9、糖..."(点/顿号形式)或
        # "(1) 糖的代谢途径"、"(8)mRNA、tRNA、rRNA的转录后加工过程"(括号形式,允许零个分隔符)
        m = re.match(r'^(?:\((\d{1,2})\)|(\d{1,2})[.、])\s*(.+)$', line)
        if m and len(m.group(3)) >= 2:
            points.append({"point": m.group(3).strip(), "source": "考纲", "chapter_hint": chapter_hint})
    return points

def filter_non_points(points):
    """剔除明显非考点条目(考试说明、题型说明),得到干净的考点对照基线。"""
    return [p for p in points if not any(m in p["point"] for m in NON_POINT_MARKERS)]

def main():
    src = "338生物化学考纲_识别全文.txt"
    text = open(src, encoding="utf-8").read()
    pts = filter_non_points(extract_syllabus_points(text))
    with open("docs/superpowers/specs/考纲考点清单.json", "w", encoding="utf-8") as f:
        json.dump(pts, f, ensure_ascii=False, indent=2)
    print(f"提取 {len(pts)} 条考点 → docs/superpowers/specs/考纲考点清单.json")

if __name__ == "__main__":
    main()
