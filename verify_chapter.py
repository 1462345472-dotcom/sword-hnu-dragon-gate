# verify_chapter.py
# -*- coding: utf-8 -*-
"""臻至版 HTML 导入验证:解析全部章节对象,核对数量/题数/指纹。
用法: python verify_chapter.py [--expect-objects N] [--expect-questions N] [--expect-terms N] [--fingerprint HEX16]
不传参数时仅输出现状;传参数时逐项断言,全部通过 exit 0,否则 exit 1。"""
import re, sys, json, hashlib, argparse

def load_state():
    html = open('生物化学题库/湖南大学题库系统-臻至版.html', encoding='utf-8', errors='ignore').read()
    dec = json.JSONDecoder()
    objs = {}
    for m in re.finditer(r'"((?:biochem|cellbio)_[0-9_]+)"\s*:\s*\{', html):
        key = m.group(1)
        try:
            obj, _ = dec.raw_decode(html[m.start() + m.group(0).rfind('{'):])
        except Exception:
            continue
        objs[key] = obj
    tq = sum(len(o.get('questions', [])) for o in objs.values())
    tt = sum(len(o.get('terms', [])) for o in objs.values())
    styles = ''.join(re.findall(r'<style[^>]*>.*?</style>', html, re.S))
    fp = hashlib.sha256(styles.encode('utf-8')).hexdigest()[:16]
    return len(objs), tq, tt, fp, sorted(objs.keys())

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--expect-objects', type=int, default=None)
    ap.add_argument('--expect-questions', type=int, default=None)
    ap.add_argument('--expect-terms', type=int, default=None)
    ap.add_argument('--fingerprint', default=None)
    args = ap.parse_args()
    n, tq, tt, fp, keys = load_state()
    print(f'章节对象: {n} | 总题数: {tq} | 总术语: {tt} | CSS指纹: {fp}')
    fails = []
    if args.expect_objects is not None and n != args.expect_objects:
        fails.append(f'对象数 {n} != 期望 {args.expect_objects}')
    if args.expect_questions is not None and tq != args.expect_questions:
        fails.append(f'题数 {tq} != 期望 {args.expect_questions}')
    if args.expect_terms is not None and tt != args.expect_terms:
        fails.append(f'术语 {tt} != 期望 {args.expect_terms}')
    if args.fingerprint and fp != args.fingerprint:
        fails.append(f'指纹 {fp} != 期望 {args.fingerprint}')
    if fails:
        print('FAIL:', '; '.join(fails))
        sys.exit(1)
    print('OK: 全部断言通过')

if __name__ == '__main__':
    main()
