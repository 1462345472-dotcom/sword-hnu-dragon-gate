# test_inject_chapter.py
# -*- coding: utf-8 -*-
import sys, json; sys.stdout.reconfigure(encoding='utf-8')
from inject_chapter import build_chapter_obj, inject

def test_inject():
    html = '{"biochem_14":{"key":"biochem_14","questions":[],"terms":[],"stats":{}},"cellbio_1":{}}'
    obj = build_chapter_obj("biochem_15", "15 新陈代谢总论",
                            [{"id":1,"type":"choice","question":"q?"}], [])
    out = inject(html, obj, after_key="biochem_14")
    assert '"biochem_15"' in out, "未插入 biochem_15"
    assert out.index('"biochem_15"') > out.index('"biochem_14"') and out.index('"biochem_15"') < out.index('"cellbio_1"'), "插入位置错误"
    # 顶层必须是合法 JSON,且 biochem_15 是顶层键(防止只插入对象体、漏键前缀)
    parsed = json.loads(out)
    assert set(parsed.keys()) == {"biochem_14", "biochem_15", "cellbio_1"}, f"顶层键错误: {list(parsed.keys())}"
    assert parsed["biochem_15"]["stats"]["total"] == 1, "biochem_15 stats 错误"
    print('test_inject PASS')

if __name__ == '__main__':
    test_inject()
