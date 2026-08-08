# -*- coding: utf-8 -*-
"""task-6b 多选修复验证脚本: CSS指纹 / diff / 数据统计 / <script>提取"""
import hashlib, json, re, sys

BEFORE = r'C:\Users\Lenovo\Desktop\湖南大学\.superpowers\sdd\2026-08-07-biochem-15-36-import\html_before_multifix.html'
AFTER  = r'C:\Users\Lenovo\Desktop\湖南大学\生物化学题库\湖南大学题库系统-剑指湖大一战成硕.html'
CSS_BASELINE = '96e3aad4f8cf0d80'

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

b, a = read(BEFORE), read(AFTER)

print('=== 1. CSS 指纹 ===')
def css_md5(html):
    styles = re.findall(r'<style[^>]*>(.*?)</style>', html, re.S)
    return hashlib.md5(''.join(styles).encode('utf-8')).hexdigest()
cb, ca = css_md5(b), css_md5(a)
print('before :', cb)
print('after  :', ca)
print('baseline:', CSS_BASELINE)
print('CSS unchanged:', ca == CSS_BASELINE and cb == CSS_BASELINE)

print()
print('=== 2. 行级 diff (before vs after) ===')
bl = b.split('\n'); al = a.split('\n')
diff_lines = []
for i in range(max(len(bl), len(al))):
    bv = bl[i] if i < len(bl) else '<EOF>'
    av = al[i] if i < len(al) else '<EOF>'
    if bv != av:
        diff_lines.append((i+1, bv, av))
print('changed line count:', len(diff_lines))
for ln, bv, av in diff_lines:
    print(f'--- line {ln} (before) ---')
    print(bv[:220])
    print(f'--- line {ln} (after) ---')
    print(av[:220])

print()
print('=== 3. 数据统计 (QUESTION_BANKS) ===')
def parse_banks(html):
    i = html.find('var QUESTION_BANKS = ')
    if i < 0: raise SystemExit('QUESTION_BANKS not found')
    j = html.find('{', i + len('var QUESTION_BANKS = '))
    # 栈匹配大括号
    depth, k = 0, j
    while k < len(html):
        if html[k] == '{': depth += 1
        elif html[k] == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    obj = json.loads(html[j:k+1])
    return obj

ob, oa = parse_banks(b), parse_banks(a)
def stats(banks):
    nch = len(banks)
    nq = sum(len(v.get('questions', [])) for v in banks.values())
    nt = sum(len(v.get('terms', [])) for v in banks.values())
    return nch, nq, nt
print('before : 章节=%d 题=%d 术语=%d' % stats(ob))
print('after  : 章节=%d 题=%d 术语=%d' % stats(oa))
print('数据不变:', stats(ob) == stats(oa))

print()
print('=== 4. 提取 <script> 供 node --check ===')
scripts = re.findall(r'<script[^>]*>(.*?)</script>', a, re.S)
print('script blocks:', len(scripts))
with open(r'C:\Users\Lenovo\Desktop\湖南大学\_extracted_scripts_multifix.js', 'w', encoding='utf-8') as f:
    for s in scripts:
        f.write(s + '\n;\n')
print('written _extracted_scripts_multifix.js, total chars:', sum(len(s) for s in scripts))
