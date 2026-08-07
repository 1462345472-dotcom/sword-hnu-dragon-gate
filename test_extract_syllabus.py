# test_extract_syllabus.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from extract_syllabus import extract_syllabus_points, filter_non_points

def test_extract():
    # 覆盖三种编号形式:点形式 "9.糖...",括号+空格 "(1) 糖...",括号无空格紧凑 "(9)逆转录..."
    text = ("二、考试内容及范围\n"
            "9.糖的分解代谢和合成代谢\n"
            "(1) 糖的代谢途径\n"
            "(2) 糖的无氧分解\n"
            "(9)逆转录的过程\n"
            "(1)基因表达调控的基本原理")
    pts = extract_syllabus_points(text, "糖代谢")
    assert any("代谢途径" in p["point"] for p in pts), "未提取出考点"
    assert any("逆转录" in p["point"] for p in pts), "无空格紧凑格式未提取出考点"
    assert any("基因表达调控的基本原理" in p["point"] for p in pts), "无空格紧凑格式未提取出考点"
    assert all(p["source"] == "考纲" for p in pts)
    print('test_extract PASS')

def test_full_syllabus():
    src = "338生物化学考纲_识别全文.txt"
    text = open(src, encoding="utf-8").read()
    pts = extract_syllabus_points(text)
    assert len(pts) >= 85, f"真实考纲编号条目 {len(pts)} 条 < 85,提取不完整"
    clean = filter_non_points(pts)
    assert 80 <= len(clean) <= 92, f"过滤后 {len(clean)} 条不在 80-92 范围"
    markers = ("本考试", "考查目标", "名词解释", "填空题", "选择题", "问答题")
    assert all(not any(mk in p["point"] for mk in markers) for p in clean), "过滤后仍含非考点条目"
    print(f'test_full_syllabus PASS (原始 {len(pts)} 条 → 过滤后 {len(clean)} 条)')

if __name__ == '__main__':
    test_extract()
    test_full_syllabus()
