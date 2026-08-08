# test_review_scanner.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from review_scanner import scan_chapter, filter_syllabus, extract_topics, _syllabus_covered

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

def test_multi_combination_no_false_positive():
    qs = [
        {"id": 1, "type": "multi", "question": "多选?", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}, "answer": "ABD", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "酶"},
        {"id": 2, "type": "multi", "question": "多选?", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}, "answer": "ABCD", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "酶"},
    ]
    r = scan_chapter(qs, [], [])
    assert not any('答案不在选项内' in str(x) for x in r['format']), 'multi 组合答案被误报'
    assert not any('字符重复' in str(x) for x in r['format']), 'multi 合法答案被误报字符重复'
    print('test_multi_combination PASS')

def test_multi_dup_char_detected():
    qs = [{"id": 1, "type": "multi", "question": "多选?", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}, "answer": "AAB", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "酶"}]
    r = scan_chapter(qs, [], [])
    assert any('字符重复' in str(x) for x in r['format']), '未检出 multi 答案字符重复'
    print('test_multi_dup_char PASS')

def test_short_numbered_points_no_false_positive():
    qs = [{"id": 1, "type": "short", "question": "简答?", "answer": "(1)第一点\n(2)第二点\n(3)第三点", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "酶"}]
    r = scan_chapter(qs, [], [])
    assert not any('未分点' in str(x) for x in r['format']), 'short (1)(2)(3) 分点被误报'
    qs2 = [{"id": 2, "type": "short", "question": "简答?", "answer": "1.第一点 2.第二点 3.第三点", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "酶"}]
    r2 = scan_chapter(qs2, [], [])
    assert not any('未分点' in str(x) for x in r2['format']), 'short 1.2.3. 分点被误报'
    print('test_short_numbered_points PASS')

def test_filter_syllabus_topics():
    sp = [
        {'point': '酶的作用特点', 'source': '考纲', 'chapter_hint': ''},
        {'point': '糖的主要分类及其各自的代表', 'source': '考纲', 'chapter_hint': ''},
    ]
    f = filter_syllabus(sp, ['酶'])
    assert len(f) == 1 and '酶' in f[0]['point'], '主题词过滤未保留相关条目'
    f2 = filter_syllabus(sp, ['核酸'])
    assert len(f2) == 2, '无命中时应保留全部条目作为参考'
    f3 = filter_syllabus(sp, [])
    assert len(f3) == 2, 'topics 为空时不过滤'
    print('test_filter_syllabus_topics PASS')

def test_extract_topics():
    assert extract_topics('生物化学题库/第七章 酶动力学') == ['酶动力学'], '未从章目录名提取主题'
    assert extract_topics('生物化学题库/第七章') == [], '纯数字章名不应提取出主题'
    print('test_extract_topics PASS')

def test_syllabus_covered_bidirectional():
    assert _syllabus_covered('酶学', ['酶学总论']), 'topic 含考纲条目关键词(整串)未命中'
    assert _syllabus_covered('酶', ['影响酶促反应的因素']), '考纲条目含 topic 关键词未命中'
    assert _syllabus_covered('蛋白质合成的抑制剂', ['酶抑制']), '2字词共享未命中'
    assert not _syllabus_covered('糖类', ['酶动力学']), '无关条目被误判为覆盖'
    print('test_syllabus_covered PASS')

def test_old_format_terms_no_crash():
    qs = [{"id": 1, "type": "choice", "question": "问?", "options": {"A": "a", "B": "b"}, "answer": "A", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "x"}]
    ts = [[1, '肌红蛋白（Myoglobin）', '旧格式四元组定义文本', '第四章'],
          [2, '血红蛋白（Hemoglobin）', '旧格式四元组定义文本2', '第四章']]
    r = scan_chapter(qs, ts, [])
    assert any('结构异常' in str(x) and '四元组' in str(x) for x in r['format']), '未检出旧格式术语结构异常'
    print('test_old_format_terms PASS')

def test_non_dict_question_no_crash():
    qs = [{"id": 1, "type": "choice", "question": "问?", "options": {"A": "a", "B": "b"}, "answer": "A", "explanation": "足够长的解析文本", "difficulty": 2, "topic": "x"},
          [99, '旧格式题目四元组', 'x', '第四章']]
    r = scan_chapter(qs, [], [])
    assert any('结构异常' in str(x) for x in r['format']), '未检出非 dict 题目结构异常'
    print('test_non_dict_question PASS')

if __name__ == '__main__':
    test_scan()
    test_multi_combination_no_false_positive()
    test_multi_dup_char_detected()
    test_short_numbered_points_no_false_positive()
    test_filter_syllabus_topics()
    test_extract_topics()
    test_syllabus_covered_bidirectional()
    test_old_format_terms_no_crash()
    test_non_dict_question_no_crash()
    print('ALL TESTS PASS')
