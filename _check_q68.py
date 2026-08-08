# -*- coding: utf-8 -*-
"""检查第14章 id68 题干与生化全库的匹配详情"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

def normalize(s):
    return re.sub(r'[\s，。？！、,.:："\u201c\u201d\'()（）【】\[\]]', '', s or '')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学'
html = open(os.path.join(BASE, '生物化学题库', '湖南大学题库系统-剑指湖大一战成硕.html'), encoding='utf-8', errors='ignore').read()

q14 = json.load(open(os.path.join(BASE, '细胞生物学题库', '第十四章', 'questions.json'), encoding='utf-8'))
target = None
for q in q14:
    if q['id'] == 68:
        target = q['question']
tn = normalize(target)
print('id68 题干:', target)
print('normalized:', tn, 'len:', len(tn))

pat = re.compile(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"')
matches = [m for m in pat.finditer(html) if normalize(m.group(1)) == tn or (len(normalize(m.group(1))) >= 8 and normalize(m.group(1))[:12] == tn[:12])]
print('HTML 中匹配条数:', len(matches))
for m in matches[:5]:
    seg = html[max(0, m.start()-800):m.start()]
    chap = re.findall(r'"(?:chapter|chapterName|章节|title)"\s*:\s*"([^"]{1,40})"', seg)
    print('  上下文章节线索:', chap[-2:] if chap else '无', '| 匹配题干:', m.group(1)[:50])
