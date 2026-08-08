# -*- coding: utf-8 -*-
"""扫描 臻至版.html script 顶层语句,定位启动即执行代码"""
import sys

p = '生物化学题库/湖南大学题库系统-臻至版.html'
raw = open(p, 'rb').read().decode('utf-8')
lines = raw.split('\n')
body = lines[1256:2280]  # script 内容 1257..2280 行

depth = 0
in_string = False
str_ch = None
prev = ''
out = []
for idx, l in enumerate(body):
    s = l
    for ch in s:
        if in_string:
            if ch == str_ch and prev != '\\':
                in_string = False
        else:
            if ch in ('"', "'", '`'):
                in_string = True
                str_ch = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
        prev = ch
    if depth > 0:
        continue
    st = s.strip()
    if not st or st.startswith('/*') or st.startswith('//') or st.startswith('*'):
        continue
    if st == '})();' or st == '(function(){' or st == '"use strict";':
        out.append(f"{idx+1257}: [struct] {st}")
        continue
    if st.startswith('function '):
        out.append(f"{idx+1257}: [fn] {st[:60]}")
        continue
    out.append(f"{idx+1257}: [TOP] {st[:80]}")

sys.stdout.write('\n'.join(out))
