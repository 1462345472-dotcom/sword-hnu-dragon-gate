# test_extract_syllabus.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from extract_syllabus import extract_syllabus_points

def test_extract():
    text = "二、考试内容及范围\n9.糖的分解代谢和合成代谢\n(1) 糖的代谢途径\n(2) 糖的无氧分解"
    pts = extract_syllabus_points(text, "糖代谢")
    assert any("代谢途径" in p["point"] for p in pts), "未提取出考点"
    assert all(p["source"] == "考纲" for p in pts)
    print('test_extract PASS')

if __name__ == '__main__':
    test_extract()
