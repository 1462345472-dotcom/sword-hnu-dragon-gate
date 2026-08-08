# 阶段 B 实施计划:52 章全量重审 + 细胞补题至 3000

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 全部 52 章(生化 36 + 细胞 16)逐题过 12 条质量标准重审,不合格修正或重出;细胞 16 章补题至 ~3000 题(两科均衡 ~47:53)。

**Architecture:** 每章 5 步流水线:自动扫描(疑点清单)→ agent 全量重审(12 条标准逐题判定)→ 自检+查重 → 主会话抽验导入(更新臻至版 HTML 该章对象)→ 验证提交(指纹+浏览器+备份优化版)。生化 1-14 重点重审 → 生化 15-36 轻量核对 → 细胞重审+补题,分段推进,每章用户抽审。

**Tech Stack:** Python 3.12、臻至版 HTML(JS 对象字面量)、schema_validator.py、inject_chapter.py(更新复用)、verify_chapter.py、review_scanner.py(新建)。

## Global Constraints

- UI 零改动:CSS 指纹(96e3aad4f8cf0d80)每章验证,变化即停
- 知识基准:生化=朱圣庚第四版(考纲规定)/细胞=丁明孝第五版,冲突以考纲教材为准
- 每章完成后备份"…生化NN章优化版.html / 细胞NN章优化版.html"(全部保留)
- 每章抽审:修正样题(2-3)+ 重出样题(2-3)+ 新补题(每题型 1-2),认可才导入
- 不合格处理:能修则修(知识错误/格式),救不了重出(题干含糊/解析空洞/硬错)
- 每章产出重审报告.md:保留 N/修正 M/重出 K/补漏 L 逐项记录
- 修正/新题与全库(含生化/细胞)跨章查重 0 重复
- 细胞补题:每章 ~190 题,multi 15-20%、short 10-15%、名解每章 15-20 个、名解 30-80 字
- 不做任何 UI 改动;不崩溃(每章独立文件,注入前自动备份,失败回滚)

---

### Task 1: 重审疑点扫描器 `review_scanner.py`

**Files:**
- Create: `review_scanner.py`
- Create: `test_review_scanner.py`

**Interfaces:**
- Consumes: 某章 questions.json/terms.json、考纲考点清单(`docs/superpowers/specs/考纲考点清单.json`)
- Produces: `scan_chapter(questions, terms, syllabus_points) -> dict`(疑点清单:格式问题/知识疑点/考纲缺口),CLI:`python review_scanner.py <章目录>` 输出疑点清单文件

- [ ] **Step 1: 写失败测试**

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python test_review_scanner.py`
Expected: FAIL(ImportError)

- [ ] **Step 3: 实现扫描器**

```python
# review_scanner.py
# -*- coding: utf-8 -*-
"""章节重审疑点扫描器:格式问题/知识疑点/考纲缺口。"""
import json, re, os, sys

def scan_chapter(questions, terms, syllabus_points):
    r = {'format': [], 'knowledge': [], 'syllabus_gap': []}
    # 格式问题
    ids = [q.get('id') for q in questions]
    if ids != list(range(1, len(questions) + 1)):
        r['format'].append(f"id 不连续: {ids[:5]}...")
    for q in questions:
        t = q.get('type')
        if t in ('choice', 'multi'):
            opts = q.get('options', {})
            vals = list(opts.values())
            if len(vals) != len(set(vals)):
                r['format'].append(f"Q{q.get('id')}: 选项重复 {q.get('question','')[:30]}")
            if t == 'multi' and len(vals) < 4:
                r['format'].append(f"Q{q.get('id')}: multi 选项不足4")
            if q.get('answer') not in opts:
                r['format'].append(f"Q{q.get('id')}: 答案不在选项内")
        elif t == 'truefalse':
            if str(q.get('answer')).lower() not in ('true', 'false'):
                r['format'].append(f"Q{q.get('id')}: truefalse 答案非法 '{q.get('answer')}'")
        elif t == 'short':
            if not q.get('answer') or not re.search(r'[①②③]', str(q.get('answer'))):
                r['format'].append(f"Q{q.get('id')}: short 答案未分点")
        if not q.get('explanation') or len(str(q.get('explanation'))) < 10:
            r['format'].append(f"Q{q.get('id')}: 解析过短/为空")
        # 知识疑点:年代类
        if t != 'short' and re.search(r'(19\d{2}|20\d{2})年', str(q.get('question'))):
            r['knowledge'].append(f"Q{q.get('id')}: 疑似年代题")
    for t in terms:
        d = t.get('definition', '')
        if not (30 <= len(d) <= 80):
            r['format'].append(f"术语 '{t.get('term','')}': 名解 {len(d)} 字(需30-80)")
    # 考纲缺口(topic 与考纲条目匹配)
    have_topics = {q.get('topic', '') for q in questions if q.get('topic')}
    for sp in syllabus_points:
        pt = sp.get('point', '')
        if any(k in pt for k in ('考试', '题型', '参考教材')):
            continue
        if not any(topic and topic in pt for topic in have_topics) and not any(pt[:8] in str(topic) for topic in have_topics):
            r['syllabus_gap'].append(f"考纲条目未覆盖: {pt[:40]}")
    return r

def main():
    d = sys.argv[1]
    qs = json.load(open(os.path.join(d, 'questions.json'), encoding='utf-8'))
    ts = json.load(open(os.path.join(d, 'terms.json'), encoding='utf-8'))
    sp = []
    sp_path = 'docs/superpowers/specs/考纲考点清单.json'
    if os.path.exists(sp_path):
        sp = json.load(open(sp_path, encoding='utf-8'))
    r = scan_chapter(qs, ts, sp)
    out = os.path.join(d, '疑点清单.json')
    json.dump(r, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"格式问题 {len(r['format'])} | 知识疑点 {len(r['knowledge'])} | 考纲缺口 {len(r['syllabus_gap'])} → {out}")

if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python test_review_scanner.py`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add review_scanner.py test_review_scanner.py
git commit -m "feat: 重审疑点扫描器(格式/知识/考纲缺口三通道)"
```

---

### Task 2: 生化 1-14 章全量重审(重点批,分 4 小批)

**Files:**
- Modify: 各章 `questions.json`/`terms.json`(修正后覆盖,原文件留 `.bak`)
- Modify: 臻至版 HTML(更新该章对象 + stats)
- Create: 各章 `重审报告.md`、`疑点清单.json`

**Interfaces:**
- Consumes: Task 1 的 review_scanner.py、考纲教材(朱圣庚第四版)、12 条判定细则
- Produces: 每章重审报告 + 修正后数据 + HTML 更新 + "…生化NN章优化版.html"备份

**每章标准重审工作流(本任务及后续任务共用的 SOP)**:
- [ ] **Step 1**: 运行 `python review_scanner.py "生物化学题库/第X章"` 生成疑点清单
- [ ] **Step 2**: dispatch 重审 agent(每小批 2-3 章并行,agent 只改数据文件不碰 HTML),prompt 含:疑点清单路径、12 条判定细则、教材基准(朱圣庚第四版)、修正规则(能修则修/救不了重出/考纲缺口补题)、重审报告.md 格式
- [ ] **Step 3**: agent 自检(schema_validator 0 违规 + `python _dedup_check.py --chapters 第X章` 0 重复)
- [ ] **Step 4**: 主会话抽验(修正样题/重出样题/补题各抽看)→ 用户抽审
- [ ] **Step 5**: 导入更新(复用 inject 思路更新该章对象 + stats)→ verify_chapter.py 断言(对象数/总题数/指纹一致)
- [ ] **Step 6**: 备份 `湖南大学题库已推进到生化NN章优化版.html` → 浏览器加载检查 → git 提交(`refactor: 第X章重审(保留N/修正M/重出K/补漏L)`)

**分批(生化 1-14)**:
- 小批 A: 第 1+2、3、4 章(共 3 个章对象,309 题)
- 小批 B: 第 5、6、7 章(259 题)
- 小批 C: 第 8、9、10 章(218 题)
- 小批 D: 第 11、12、13、14 章(258 题)

**SOP 细化(agent prompt 必含)**:
- 12 条判定细则逐条列出(见设计文档第 6 节)
- 教材:朱圣庚《生物化学》第四版(考纲规定)
- 修正规则:知识错误→改答案/解析;格式→修字段;题干+解析均含糊/硬错→删除按考点重出;考纲缺口→补新题(topic 标注)
- 重审报告格式:保留 N/修正 M/重出 K/补漏 L + 每类样题
- 定期落盘(每 30 题)

- [ ] **Step 7**: 每小批完成后 git 提交(按小批粒度,每章一个 commit 记录)

---

### Task 3: 生化 15-36 章全量重审(轻量核对批,分 5 小批)

**Files:** 同 Task 2 结构

**Interfaces:** 同 Task 2(轻量模式)

- [ ] **Step 1**: 复用 SOP,轻量核对重点:跨章知识一致性(与邻章重复/口径冲突)、考纲教材精确性、抽验 agent 出题时的"教材补全"题是否正确
- [ ] **Step 2**: 分批:小批 A(15-18)、B(19-22)、C(23-26)、D(27-30)、E(31-36)
- [ ] **Step 3**: 每章产出重审报告 + 修正数据 + HTML 更新 + "…生化NN章优化版.html"备份 + git 提交

---

### Task 4: 细胞 16 章重审 + 补题至 ~3000(分 4 小批)

**Files:**
- Modify: `细胞生物学题库/第X章/questions.json`/`terms.json`(重审 + 补题)
- Modify: 臻至版 HTML(更新 cellbio_NN 对象)
- Create: 各章 `重审报告.md`、`补题报告.md`

**Interfaces:**
- Consumes: 丁明孝《细胞生物学》第五版、细胞课件(PDF/DOCX)、Task 1 扫描器
- Produces: 每章重审+补题后数据(每章 ~190 题)、HTML 更新、"…细胞NN章优化版.html"备份

- [ ] **Step 1**: 每章先重审(同 SOP,教材=丁明孝第五版)→ 再补题(目标 ~190 题/章)
- [ ] **Step 2**: 补题依据:细胞课件 + 丁明孝第五版(课件缺的按教材补);题型结构 choice/truefalse 为主、multi 15-20%、short 10-15%、名解 15-20 个(30-80 字)
- [ ] **Step 3**: 自检 + 跨科查重(`python _dedup_check.py --chapters 第X章` 含生化全库)0 重复
- [ ] **Step 4**: 主会话抽验 + 用户抽审(重出样题/新补题每题型 1-2)
- [ ] **Step 5**: 导入更新 cellbio_NN 对象 + stats → verify 断言 → 备份"细胞NN章优化版" → 浏览器检查 → git 提交(`refactor: 细胞第X章重审+补题(至N题)`)
- [ ] **Step 6**: 分批:小批 A(1-4)、B(5-8)、C(9-12)、D(13-16)

---

### Task 5: 最终全量验证与验收报告

**Files:**
- Create: `docs/superpowers/research/stage-B-complete-report.md`

- [ ] **Step 1**: 全量核对:52 对象、总题数(预期 ~6400:生化 3381+重审补漏 + 细胞 ~3000)、术语数、CSS 指纹
- [ ] **Step 2**: 浏览器全面实测:51+1 章节全部可达、4 题型可做题、无 JS 错误(Edge headless)
- [ ] **Step 3**: 两科比例核对(生化 vs 细胞 ≈ 47:53 ±5%)
- [ ] **Step 4**: 写阶段 B 验收报告并提交(`docs: 阶段B验收报告`)

---

## Self-Review

- **Spec coverage:** 设计 9 节全部覆盖:5 步流水线 → Task 1(扫描)+ Task 2/3/4(SOP 5 步);12 条细则 → SOP prompt 必含;细胞补题 → Task 4;质量关卡(抽审/指纹/备份/浏览器)→ SOP Step 4-6;验收标准 → Task 5。✅
- **Placeholder scan:** 无 TBD;SOP 是标准工作流定义(重审判定属 AI 判断任务,由 agent prompt 承载,与阶段 A 一致)。✅
- **Type consistency:** review_scanner.py 接口在 Task 1 定义,Task 2/3/4 引用一致;inject/verify/dedup 脚本沿用阶段 A 已用接口。✅
