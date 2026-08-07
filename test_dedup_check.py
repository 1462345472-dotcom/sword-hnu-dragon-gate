# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from dedup_check import dedup_check

def test_dedup():
    new = [{"question": "三羧酸循环的限速酶是？", "id": 1},
           {"question": "糖酵解的最终产物是？", "id": 2}]
    existing = ["三羧酸循环的限速酶是？", "完全无关的题"]
    dups = dedup_check(new, existing)
    assert len(dups) == 1 and dups[0]["id"] == 1, f"重复检测失败: {dups}"
    print('test_dedup PASS')

if __name__ == '__main__':
    test_dedup()
