# test_review_scanner.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from review_scanner import scan_chapter

def test_scan():
    qs = [
        {"id": 1, "type": "choice", "question": "三羧酸循环的限速酶是?", "options": {"A": "a", "B": "b", "C": "a", "D": "d"}, "answer": "A", "explanation": "解析", "difficulty": 2, "topic": "TCA"},
        {"id": 2, "type": "short", "question": "简答?", "answer": "不分点", "explanation": "解析", "difficulty": 2, "topic": "TCA"},
        {"id": 3, "type": "truefalse", "question": "判断?", "answer": "True", "explanation": "", "difficulty": 2, "topic": "别处"},
    ]
    ts = [{"id": 1, "term": "t", "name": "t", "definition": "太短", "chapter": "x"}]
    r = scan_chapter(qs, ts, [])
    assert any('选项重复' in str(x) for x in r['format']), '未检出选项重复'
    assert any('名解' in str(x) for x in r['format']), '未检出名解长度'
    assert any('True' in str(x) for x in r['format']), '未检出答案大小写'
    print('test_scan PASS')

if __name__ == '__main__':
    test_scan()
