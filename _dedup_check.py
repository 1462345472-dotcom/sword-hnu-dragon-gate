# -*- coding: utf-8 -*-
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
html = open('生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html', encoding='utf-8', errors='ignore').read()
existing = re.findall(r'"question"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
print('HTML 已有题干:', len(existing))
import glob, argparse
ap = argparse.ArgumentParser()
ap.add_argument('--chapters', nargs='+', default=['第十九章'], help='待查重章节目录名')
args = ap.parse_args()
all_new = []
for ch in args.chapters:
    p = f'生物化学题库/{ch}/questions.json'
    try:
        qs = json.load(open(p, encoding='utf-8'))
        all_new.extend(qs)
        print(f'检查章节 {ch}: {len(qs)} 题')
    except Exception as e:
        print(f'{ch}: {e}')
def norm(s):
    return re.sub(r'[\s，。？！、,.:：“”\'()（）【】]', '', s or '')
ne = set(norm(t) for t in existing)
dup_count = 0
for q in all_new:
    if norm(q.get('question', '')) in ne:
        dup_count += 1
        print('重复:', q.get('question', '')[:45])
print(f'全部新题 {len(all_new)} 与 HTML 已有题重复: {dup_count} 条')
