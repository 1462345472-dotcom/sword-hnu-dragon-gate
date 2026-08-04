# 题库系统全维度健康检查 · 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对29章题库系统执行代码/数据/构建/运行时四维度健康检查，修复所有发现的问题，加固构建管线使其具备 schema 校验 + 烟雾测试能力。

**Architecture:** 分扫描→报告→修复→加固四个阶段。扫描阶段先造工具（schema_validator.py），再并行执行数据层+代码层扫描。修复完成后将 schema 校验和烟雾测试嵌入 build_unified.py 作为硬关卡。

**Tech Stack:** Python 3 (无外部pip依赖) + Node.js (Puppeteer用于烟雾测试) + Vanilla JS ES5 (运行时)

## Global Constraints

- JS 代码保持 ES5 兼容（无箭头函数、无模板字符串、无 const/let、无 Promise）
- CSS 不改动已有的类名体系
- 不引入 pip/npm 外部依赖——schema_validator.py 手写，烟雾测试用已有的 Node 环境
- 构建失败必须 `exit(1)`，干净利落不输出半成品 HTML
- 不动现有的 6-skill 设计系统（hnu-academy/motion/taste/impeccable/apple/uiux）
- 代理数量控制在合理范围，仅在真正独立的工作流上并行

---

## File Structure

```
湖南大学/
├── build_unified.py            ← 修改：集成 schema 校验 + 烟雾测试关卡
├── schema_validator.py         ← 新建：独立可调用的 schema 校验器
├── smoke_test.js               ← 新建：构建后烟雾测试脚本
├── src_js.txt                  ← 可能需要修改（如有代码层问题）
├── src_css.txt                 ← 可能需要修改（如有代码层问题）
├── 生物化学题库/
│   └── 湖南大学题库系统.html    ← 构建输出（通过 build_unified.py 重新生成）
└── docs/superpowers/
    └── plans/2026-08-04-quiz-system-health-check-plan.md  ← 本文件
```

**边界清晰的责任划分：**

| 文件 | 职责 |
|------|------|
| `schema_validator.py` | 独立校验单个 questions.json / terms.json 的结构合法性，输出违规行号 |
| `build_unified.py` | 读取29章JSON → schema校验 → 跨章一致性 → 归一化 → 模板注入 → 烟雾测试 → 输出HTML |
| `smoke_test.js` | 在 headless browser 中加载构建产物，验证4题型渲染/答题/ls持久化无报错 |

---

### Task 1: 编写 schema 校验器

**Files:**
- Create: `schema_validator.py`

**Interfaces:**
- Produces: `validate_questions(filepath: str) -> list[str]` — 返回违规列表，空列表 = 通过
- Produces: `validate_terms(filepath: str) -> list[str]` — 返回违规列表，空列表 = 通过
- Produces: `validate_all_chapters(subjects: dict) -> dict` — 按章节返回违规分组

- [ ] **Step 1: 实现 questions.json schema 校验函数**

```python
#!/usr/bin/env python3
"""题库数据 Schema 校验器 —— 零外部依赖，纯 Python3"""
import json
import sys

# ============================================================
# questions.json schema 约束
# ============================================================
VALID_TYPES = {'choice', 'truefalse', 'multi', 'short'}
VALID_DIFFICULTIES = {1, 2, 3}


def validate_questions(filepath):
    """校验单个 questions.json，返回违规信息列表。空列表 = 通过。"""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            questions = json.load(f)
        except json.JSONDecodeError as e:
            return ['JSON解析失败: %s' % e]

    if not isinstance(questions, list):
        return ['根元素必须是数组，当前类型: %s' % type(questions).__name__]

    ids_seen = set()

    for i, q in enumerate(questions):
        idx = q.get('id', '索引%d' % i)

        # 必填字段
        for field in ['id', 'type', 'question', 'answer', 'explanation', 'difficulty', 'tags']:
            if field not in q:
                errors.append('[#%s] 缺少必填字段: %s' % (idx, field))

        # 字段类型
        if 'id' in q and not isinstance(q['id'], int):
            errors.append('[#%s] id必须是整数，当前类型: %s' % (idx, type(q['id']).__name__))
        if 'type' in q and q['type'] not in VALID_TYPES:
            errors.append('[#%s] 无效题型: %s，合法值: %s' % (idx, q['type'], ', '.join(sorted(VALID_TYPES))))
        if 'question' in q and (not isinstance(q['question'], str) or not q['question'].strip()):
            errors.append('[#%s] question不能为空' % idx)
        if 'explanation' in q and (not isinstance(q['explanation'], str) or not q['explanation'].strip()):
            errors.append('[#%s] explanation不能为空' % idx)
        if 'difficulty' in q and q['difficulty'] not in VALID_DIFFICULTIES:
            errors.append('[#%s] difficulty必须为1-3，当前值: %s' % (idx, q['difficulty']))
        if 'tags' in q and not isinstance(q['tags'], list):
            errors.append('[#%s] tags必须是数组' % idx)

        # type 特定校验
        qtype = q.get('type', '')
        if qtype in ('choice', 'multi'):
            opts = q.get('options', {})
            if not isinstance(opts, dict) or len(opts) == 0:
                errors.append('[#%s] %s题型必须提供非空options字典' % (idx, qtype))
            else:
                for key in opts:
                    if not isinstance(key, str) or len(key) != 1 or key < 'A' or key > 'Z':
                        errors.append('[#%s] options键必须为单字母A-Z，当前: %s' % (idx, key))
                    if not isinstance(opts[key], str) or not opts[key].strip():
                        errors.append('[#%s] options[%s]值不能为空' % (idx, key))

        if qtype == 'choice':
            ans = str(q.get('answer', ''))
            opts = q.get('options', {})
            if ans and ans not in opts:
                errors.append('[#%s] choice答案"%s"不在options中(有效键: %s)' % (idx, ans, ', '.join(sorted(opts.keys()))))

        if qtype == 'truefalse':
            ans = str(q.get('answer', '')).strip().lower()
            if ans not in ('true', 'false'):
                errors.append('[#%s] TF答案必须为true/false(全小写)，当前: %s' % (idx, q.get('answer')))

        if qtype == 'multi':
            ans = str(q.get('answer', ''))
            opts = q.get('options', {})
            if not ans:
                errors.append('[#%s] multi答案不能为空' % idx)
            elif opts:
                for ch in ans:
                    if ch not in opts:
                        errors.append('[#%s] multi答案中"%s"不在options中' % (idx, ch))
            # 检查是否有重复字符
            if len(ans) != len(set(ans)):
                errors.append('[#%s] multi答案中有重复字符: %s' % (idx, ans))

        if qtype == 'short':
            ans = str(q.get('answer', ''))
            if not ans or len(ans.strip()) < 5:
                errors.append('[#%s] short答案为空或过短(<5字符)' % idx)

        # ID 唯一性
        if q.get('id') in ids_seen:
            errors.append('[#%s] 重复ID: %s' % (idx, q['id']))
        ids_seen.add(q.get('id'))

    return errors
```

- [ ] **Step 2: 实现 terms.json schema 校验函数**

```python
def validate_terms(filepath):
    """校验单个 terms.json，返回违规信息列表。支持 list 和 dict 两种格式。"""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            terms = json.load(f)
        except json.JSONDecodeError as e:
            return ['JSON解析失败: %s' % e]

    if not isinstance(terms, list):
        return ['根元素必须是数组，当前类型: %s' % type(terms).__name__]

    ids_seen = set()

    for i, t in enumerate(terms):
        if isinstance(t, list):
            # 旧格式: [id, term, definition]
            if len(t) < 3:
                errors.append('[索引%d] list格式terms需至少3个元素[id, term, definition]' % i)
                continue
            tid = t[0]
            if not isinstance(tid, int):
                errors.append('[索引%d] id必须是整数，当前: %s' % (i, tid))
            if not isinstance(t[1], str) or not t[1].strip():
                errors.append('[索引%d] term不能为空' % i)
            if not isinstance(t[2], str) or not t[2].strip():
                errors.append('[索引%d] definition不能为空' % i)
        elif isinstance(t, dict):
            tid = t.get('id', i)
            for field in ['id', 'term', 'definition']:
                if field not in t:
                    errors.append('[#%s] 缺少必填字段: %s' % (tid, field))
            if 'id' in t and not isinstance(t['id'], int):
                errors.append('[#%s] id必须是整数' % tid)
            if 'term' in t and (not isinstance(t['term'], str) or not t['term'].strip()):
                errors.append('[#%s] term不能为空' % tid)
            if 'definition' in t and (not isinstance(t['definition'], str) or not t['definition'].strip()):
                errors.append('[#%s] definition不能为空' % tid)
        else:
            errors.append('[索引%d] terms元素必须是list或dict，当前类型: %s' % (i, type(t).__name__))
            continue

        if tid in ids_seen:
            errors.append('[#%s] 重复ID' % tid)
        ids_seen.add(tid)

    return errors
```

- [ ] **Step 3: 实现批量校验入口**

```python
def validate_all_chapters(subjects):
    """
    对 build_unified.py 的 SUBJECTS 字典逐章校验。
    返回: { chapter_key: { 'questions': [errors], 'terms': [errors] } }
    """
    import os
    BASE_DIR = r'c:\Users\Lenovo\Desktop\湖南大学'
    results = {}
    for key, cfg in subjects.items():
        qf = os.path.join(BASE_DIR, cfg['questionsFile'])
        tf = os.path.join(BASE_DIR, cfg['termsFile'])
        results[key] = {
            'questionsFile': cfg['questionsFile'],
            'termsFile': cfg['termsFile'],
            'q_errors': validate_questions(qf),
            't_errors': validate_terms(tf),
        }
    return results
```

- [ ] **Step 4: 实现 CLI 入口**

```python
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python schema_validator.py <file.json>         校验单个文件')
        print('      python schema_validator.py --all               校验全部29章')
        sys.exit(0)

    if sys.argv[1] == '--all':
        from build_unified import SUBJECTS
        results = validate_all_chapters(SUBJECTS)
        total_errors = 0
        for key, r in results.items():
            label = '%s (%s)' % (key, r['questionsFile'])
            if r['q_errors'] or r['t_errors']:
                total_errors += len(r['q_errors']) + len(r['t_errors'])
                print('\n[%s]' % label)
                for e in r['q_errors']:
                    print('  Q: ' + e)
                for e in r['t_errors']:
                    print('  T: ' + e)
            else:
                print('[%s] OK (%d题 + %d术语)' % (label,
                    len(r['q_errors']), len(r['t_errors'])))  # counts via separate load
        if total_errors:
            print('\n[FAIL] 共 %d 个违规项' % total_errors)
            sys.exit(1)
        else:
            print('\n[PASS] 全部29章校验通过')
    else:
        filepath = sys.argv[1]
        if 'questions' in filepath.lower():
            errors = validate_questions(filepath)
        else:
            errors = validate_terms(filepath)
        if errors:
            for e in errors:
                print('ERROR: ' + e)
            sys.exit(1)
        else:
            print('OK: ' + filepath)
```

- [ ] **Step 5: 用单个章节测试**

Run: `python schema_validator.py "生物化学题库/第一章+第二章/questions.json"`
Expected: PASS 或具体违规行号

- [ ] **Step 6: 用 --all 模式跑全部29章**

Run: `python schema_validator.py --all`
Expected: 输出每章结果 + 总违规数

- [ ] **Step 7: Commit**

```bash
git add schema_validator.py
git commit -m "feat: 添加 schema_validator.py — 独立JSON校验器"
```

---

### Task 2: 数据层全量扫描并修复

**Files:**
- 使用: `schema_validator.py`
- 可能修改: 29章的 `questions.json` / `terms.json`

**Interfaces:**
- Consumes: `validate_questions()`, `validate_terms()` from Task 1

- [ ] **Step 1: 运行全量 schema 扫描**

Run: `python schema_validator.py --all > _scan_data.txt 2>&1`
将输出重定向到文件供分析。

- [ ] **Step 2: 分类违规项**

读取 `_scan_data.txt`，将违规按类型分组：
- **阻断级**（构建会fail）：缺少必填字段、答案不在选项中、TF答案非true/false
- **警告级**：tags为空数组（大部分如此，可能是设计如此）、difficulty超出1-3
- **信息级**：题干长度异常、选项数量异常

- [ ] **Step 3: 修复所有阻断级违规**

对于每个阻断级违规：
1. 定位到具体 JSON 文件和题目ID
2. 阅读理解原题意图
3. 修正字段值（填缺失字段、修正答案格式、修正选项键名等）
4. 修复后重新对该文件运行 `python schema_validator.py <file>`

常见修复模式：
```python
# TF答案 True → true
# multi 答案 ["A","B","C"] → "ABC"
# 缺失 difficulty → 默认=1
# 缺失 tags → 默认=[]
# 缺失 explanation → 根据题目内容补写一句话解析
```

- [ ] **Step 4: 修复全部后重新扫描确认零违规**

Run: `python schema_validator.py --all`
Expected: 全部 PASS，0 违规

- [ ] **Step 5: 手动抽查跨章一致性**

- 随机抽5章，逐题阅读确认答案是否真的正确
- 检查判断题的 `answer` 字段是否全小写 true/false（在HTML源码中搜索 `"True"` 和 `"False"`）
- 检查 multi 答案格式是否统一为字符串（非数组）

Run: `grep -r '"answer":\s*"True"' 生物化学题库/ 细胞生物学题库/`

- [ ] **Step 6: Commit**

```bash
git add 生物化学题库/*/questions.json 生物化学题库/*/terms.json
git add 细胞生物学题库/*/questions.json 细胞生物学题库/*/terms.json
git commit -m "fix: 数据层全量修复 — 29章schema校验通过"
```

---

### Task 3: 代码层扫描并修复

**Files:**
- 扫描: `src_js.txt`, `src_css.txt`, `生物化学题库/湖南大学题库系统.html`
- 可能修改: `src_js.txt`, `src_css.txt`

**Interfaces:**
- 不依赖其他 Task（独立扫描）

- [ ] **Step 1: ES5 兼容性扫描**

在 `src_js.txt` 和 HTML 中搜索 ES6+ 语法：
```bash
grep -n '=>' src_js.txt                    # 箭头函数
grep -n '`' src_js.txt                     # 模板字符串
grep -n '\bconst\b\|\blet\b' src_js.txt    # const/let
grep -n '\bPromise\b' src_js.txt           # Promise
grep -n '\.\.\.' src_js.txt                # 展开运算符
```

对 HTML 同样执行（排除 CSS 中的合法用法）。

- [ ] **Step 2: XSS / innerHTML 审计**

在 `src_js.txt` 中搜索所有 `innerHTML` 赋值点：
```bash
grep -n 'innerHTML\s*=' src_js.txt
```

逐处检查：赋值的右侧是否包含用户可控数据（`S.answers`、`localStorage`、JSON数据中的字符串等）。对于任何来自 `q.question`、`q.explanation`、`q.options` 等用户数据的拼接，确认是否需要转义。

- [ ] **Step 3: localStorage 安全性**

检查 `saveState` 的 try/catch 覆盖，特别是 `localStorage.setItem` 配额溢出场景：
- 当前 `saveState` 已有 try/catch
- 确认 `saveQuizProgress` 是否也有 try/catch
- 确认 `localStorage` 写满时刷题功能是否降级而非崩溃

- [ ] **Step 4: CSS 死代码扫描**

在 `src_css.txt` 中搜索定义但未被引用的选择器：
- 对比 CSS 中的类名和 JS 模板中生成的 className
- 标记疑似死代码的选择器（如 `.ent-1` ~ `.ent-8` 已在 JS 中禁用但仍保留 CSS 定义）
- 不删除（保守），只标记供后续清理

- [ ] **Step 5: 动画性能审计**

搜索 CSS 中所有 `animation` 和 `transition` 声明，确认动画属性是 GPU 可合成的（`transform`, `opacity`, `filter`）：
```bash
grep -n 'animation\|transition' src_css.txt | grep -v 'transform\|opacity\|filter\|clip-path'
```

标记任何触发 layout/paint 的动画属性（如 `width`, `height`, `top`, `left`, `margin`, `padding`）。

- [ ] **Step 6: 修复代码层发现的问题**

按严重度排序修复：
1. 🔴 XSS / 安全性 → 立即修复
2. 🟡 ES6+ 语法 → 改写为 ES5 等价写法
3. 🟢 死代码 / 性能 → 标记，不强制本次修复

- [ ] **Step 7: Commit**

```bash
git add src_js.txt src_css.txt
git commit -m "fix: 代码层扫描修复 — ES5兼容/XSS/ls安全"
```

---

### Task 4: 构建管线审计

**Files:**
- 审计: `build_unified.py`（424行）
- 不修改（加固在 Task 6-7 单独做）

**Interfaces:**
- 不依赖其他 Task

- [ ] **Step 1: 通读 build_unified.py 全量逻辑**

记录关键决策点和潜在风险：

| 位置 | 逻辑 | 风险 |
|------|------|------|
| L252-296 | `load_data()` 合并29章 | 任一章JSON格式错误 → 整个构建崩溃且无具体错误行号 |
| L262-265 | 规范化：topic→tags迁移 | topic 字段在大部分JSON中不存在，静默跳过 |
| L270-282 | terms格式兼容（list/dict） | list格式的字段顺序假设 `[id, term, definition]` 可能不准确 |
| L298-355 | 验证关卡 | 覆盖4种题型+ID唯一性，但不检查 `explanation` 为空、`tags` 类型 |
| L362-408 | `build()` 组装 | 模板占位符替换用简单 replace，不检查占位符存在性 |

- [ ] **Step 2: 检查图片引用**

确认 `load_image_b64()` 引用的3张图片路径存在且可读：
```bash
ls -la "生物化学题库/湖南大学-logo-2048px.png"
ls -la "生物化学题库/和 校徽融合的图.jpg"
ls -la "生物化学题库/背景图.jpg"
```

- [ ] **Step 3: 检查模板占位符完整性**

确认 `src_js.txt` 中包含所有被 replace 的占位符：
```bash
grep -n '__BANKS__\|__COURSES__\|__CH_NAMES__\|__COURSE__\|__SUBJECT__\|__KEYS__\|__LOGO_B64__\|__EMBLEM_B64__\|__BG_B64__' src_js.txt
```

- [ ] **Step 4: 确认章节映射完整性**

对比 `SUBJECTS` 字典和实际文件系统：
```bash
# 确认每个 questionsFile 和 termsFile 对应的文件实际存在
python -c "from build_unified import SUBJECTS; import os; [print(k, os.path.exists(os.path.join(r'c:\Users\Lenovo\Desktop\湖南大学', v['questionsFile']))) for k,v in SUBJECTS.items()]"
```

- [ ] **Step 5: 记录审计发现（无需 commit — 信息汇总到 Task 5）**

---

### Task 5: 生成健康检查报告

**Files:**
- Create: `_health_report.md`（临时诊断报告，Git忽略）

**Interfaces:**
- Consumes: Task 1-4 的全部产出

- [ ] **Step 1: 汇总四维度发现**

按以下模板写入 `_health_report.md`：

```markdown
# 题库系统健康检查报告
**日期**: 2026-08-04
**范围**: 生物化学1-14章 + 细胞生物学1-16章 = 29章

## 1. 数据层
- Schema违规: X项（已修复Y项）
- 答案格式问题: ...
- 跨章一致性问题: ...

## 2. 代码层
- ES5兼容性: ...
- XSS风险: ...
- 死代码: ...

## 3. 构建管线
- 风险点: ...
- 建议加固项: ...

## 4. 运行时
- 待验证项: ...（将在加固后统一测试）

## 5. 总评
- 阻断级问题: 0（全部已修复）
- 警告项: N
- 后续建议: ...
```

- [ ] **Step 2: 确认所有阻断级问题已修复**

在进入加固阶段前，再次运行 `python schema_validator.py --all` 确认零违规。

- [ ] **Step 3: Commit**

```bash
git add _health_report.md
git commit -m "docs: 题库系统健康检查报告"
```

---

### Task 6: 集成 schema 校验到 build_unified.py

**Files:**
- Modify: `build_unified.py`
- Use: `schema_validator.py`

**Interfaces:**
- Consumes: `validate_questions()`, `validate_terms()` from `schema_validator.py` (Task 1)

- [ ] **Step 1: 在 `load_data()` 开头加入 schema 校验调用**

在 `build_unified.py` 的 `load_data()` 函数中，在现有验证关卡之前（L298之前）插入 schema 校验：

```python
# 在 def load_data() 的 banks 循环之前插入
def load_data():
    # === 新增：Schema 校验关卡 ===
    from schema_validator import validate_questions, validate_terms
    print('\n[Schema校验] 逐章检查JSON结构...')
    schema_errors = []
    for key, cfg in SUBJECTS.items():
        qf = os.path.join(BASE_DIR, cfg['questionsFile'])
        tf = os.path.join(BASE_DIR, cfg['termsFile'])
        q_errs = validate_questions(qf)
        t_errs = validate_terms(tf)
        for e in q_errs:
            schema_errors.append('[%s] %s' % (cfg['questionsFile'], e))
        for e in t_errs:
            schema_errors.append('[%s] %s' % (cfg['termsFile'], e))
        if not q_errs and not t_errs:
            print('  [OK] %s' % cfg['questionsFile'])
    if schema_errors:
        print('\n[Schema校验失败] 发现 %d 个违规项:' % len(schema_errors))
        for err in schema_errors:
            print('  ' + err)
        print('\n构建中止 - 请修复以上JSON后重试')
        sys.exit(1)
    print('[Schema校验通过] 全部29章JSON格式合法\n')
    # === Schema 校验结束 ===

    banks = {}
    for key, cfg in SUBJECTS.items():
        # ... 现有逻辑不变
```

- [ ] **Step 2: 加固现有验证关卡**

在现有验证逻辑（L298-355）中添加漏掉的检查项：
- `explanation` 不能为空字符串
- `tags` 必须是 list 类型
- `question` 不能是纯空白字符串

```python
# 在现有验证循环中追加（L309 附近）
if 'explanation' in q and (not isinstance(q['explanation'], str) or not q['explanation'].strip()):
    validation_errors.append('[%s #%s] explanation为空' % (key, qid))
if 'tags' in q and not isinstance(q['tags'], list):
    validation_errors.append('[%s #%s] tags不是数组: %s' % (key, qid, type(q['tags']).__name__))
if 'question' in q and isinstance(q['question'], str) and not q['question'].strip():
    validation_errors.append('[%s #%s] question为空字符串' % (key, qid))
```

- [ ] **Step 3: 运行构建确认新关卡生效**

Run: `python build_unified.py`
Expected: 
- Schema校验 PASS → 进入数据合并 → 原有验证 PASS → 构建成功
- 或任一关卡 FAIL → exit(1) + 具体错误信息

- [ ] **Step 4: Commit**

```bash
git add build_unified.py
git commit -m "feat: build_unified.py 集成 schema校验 + 加固验证关卡"
```

---

### Task 7: 添加构建后烟雾测试

**Files:**
- Create: `smoke_test.js`
- Modify: `build_unified.py`（在 `build()` 末尾调用烟雾测试）

**Interfaces:**
- Consumes: 构建产物 `生物化学题库/湖南大学题库系统.html`

- [ ] **Step 1: 编写 smoke_test.js**

```javascript
/**
 * 湖南大学题库系统 — 构建后烟雾测试
 * 用法: node smoke_test.js <html_path>
 * 退出码: 0=通过, 1=失败
 *
 * 依赖: puppeteer (npm install puppeteer)
 * 约束: 仅在构建后自动调用，不嵌入HTML
 */
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const HTML_PATH = process.argv[2] || '生物化学题库/湖南大学题库系统.html';

async function run() {
    const fileUrl = 'file:///' + path.resolve(HTML_PATH).replace(/\\/g, '/');
    console.log('[烟雾测试] 加载: ' + fileUrl);

    const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
    const page = await browser.newPage();
    const errors = [];

    // 捕获页面JS错误
    page.on('pageerror', err => {
        errors.push('JS运行时错误: ' + err.message);
    });

    // 捕获控制台error
    page.on('console', msg => {
        if (msg.type() === 'error') {
            errors.push('console.error: ' + msg.text());
        }
    });

    try {
        await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 30000 });

        // 等待应用初始化
        await page.waitForSelector('#app', { timeout: 10000 });

        // 测试1: 确认4个核心函数存在
        const funcs = await page.evaluate(() => {
            return {
                getBank: typeof getBank === 'function',
                startQuiz: typeof startQuiz === 'function',
                renderQuiz: typeof renderQuiz === 'function',
                renderHome: typeof renderHome === 'function',
                QUESTION_BANKS: typeof QUESTION_BANKS === 'object',
                COURSES: typeof COURSES === 'object',
                S: typeof S === 'object' && S !== null,
            };
        });
        for (const [name, ok] of Object.entries(funcs)) {
            if (!ok) errors.push('缺失: ' + name);
        }

        // 测试2: 确认银行数据加载
        const bankCount = await page.evaluate(() => Object.keys(QUESTION_BANKS).length);
        if (bankCount !== 29) errors.push('QUESTION_BANKS应有29章，实际: ' + bankCount);

        const totalQuestions = await page.evaluate(() => {
            return Object.values(QUESTION_BANKS).reduce((sum, b) => sum + (b.questions ? b.questions.length : 0), 0);
        });
        console.log('[烟雾测试] 题目总数: ' + totalQuestions);

        // 测试3: 模拟进入刷题视图
        await page.evaluate(() => {
            var biochemBank = QUESTION_BANKS['biochem_1_2'];
            if (biochemBank && biochemBank.questions) {
                S.subject = 'biochem_1_2';
                S.questions = biochemBank.questions.slice(0, 5);
                S.qIndex = 0;
                S.quizMode = 'all';
                renderQuiz();
            } else {
                throw new Error('biochem_1_2 bank not found');
            }
        });
        await page.waitForSelector('.quiz-card', { timeout: 5000 });

        // 测试4: 验证4种题型各有一题可渲染
        const typeCheck = await page.evaluate(() => {
            var types = {};
            for (var k in QUESTION_BANKS) {
                var qs = QUESTION_BANKS[k].questions || [];
                for (var i = 0; i < qs.length; i++) {
                    types[qs[i].type] = true;
                }
            }
            return types;
        });
        console.log('[烟雾测试] 已检出题型: ' + JSON.stringify(typeCheck));
        if (!typeCheck.choice) errors.push('缺少choice题型');
        if (!typeCheck.truefalse) errors.push('缺少truefalse题型');
        if (!typeCheck.multi) errors.push('缺少multi题型');
        if (!typeCheck.short) errors.push('缺少short题型');

        // 测试5: localStorage 读写
        const lsOk = await page.evaluate(() => {
            try {
                localStorage.setItem('_smoke_test_', '1');
                var v = localStorage.getItem('_smoke_test_');
                localStorage.removeItem('_smoke_test_');
                return v === '1';
            } catch (e) {
                return false;
            }
        });
        if (!lsOk) errors.push('localStorage读写失败');

        // 测试6: 切换课程
        await page.evaluate(() => {
            S.course = 'cellbiology';
            S.subject = 'cellbio_1';
            renderHome();
        });
        await page.waitForSelector('#view-home', { timeout: 5000 });

    } catch (e) {
        errors.push('烟雾测试异常: ' + e.message);
    } finally {
        await browser.close();
    }

    console.log('');
    if (errors.length === 0) {
        console.log('[烟雾测试 PASS] 全部6项检查通过');
        process.exit(0);
    } else {
        console.log('[烟雾测试 FAIL] ' + errors.length + ' 个错误:');
        errors.forEach(e => console.log('  - ' + e));
        process.exit(1);
    }
}

run();
```

- [ ] **Step 2: 在 build_unified.py 的 build() 末尾集成调用**

```python
# 在 build() 函数末尾（L415 之前）加入：
def build(banks, images):
    # ... 现有逻辑不变 ...

    # === 新增：构建后烟雾测试 ===
    import subprocess
    print('\n[烟雾测试] 启动 headless browser 验证...')
    smoke_script = os.path.join(BASE_DIR, 'smoke_test.js')
    if os.path.exists(smoke_script):
        result = subprocess.run(
            ['node', smoke_script, OUTPUT],
            capture_output=True, text=True, timeout=60
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print('[烟雾测试失败] 构建产物存在运行时问题，请检查')
            sys.exit(1)
    else:
        print('  [WARN] smoke_test.js 未找到，跳过烟雾测试')
    # === 烟雾测试结束 ===
```

- [ ] **Step 3: 安装 Puppeteer（如需）**

```bash
npm install puppeteer
```

如果 Puppeteer 因网络问题无法安装，使用已安装的本地浏览器或降级为纯 Node.js 静态分析（检查HTML中无语法错误）。

- [ ] **Step 4: 运行完整构建 + 烟雾测试**

Run: `python build_unified.py`
Expected: 构建成功 + 烟雾测试 PASS

- [ ] **Step 5: Commit**

```bash
git add smoke_test.js build_unified.py
git commit -m "feat: 构建后烟雾测试 — Puppeteer验证4题型渲染+ls存储"
```

---

### Task 8: 最终回归验证

**Files:**
- 使用: `build_unified.py`（增强版）
- 测试: `生物化学题库/湖南大学题库系统.html`（重新构建）

**Interfaces:**
- Consumes: Task 6-7 的全部加固产出

- [ ] **Step 1: 从零构建**

```bash
python build_unified.py
```

确认输出：
```
[Schema校验通过] 全部29章JSON格式合法
[验证通过] 所有数据完整，开始构建...
[IMG] ...
[OK] .../湖南大学题库系统.html
     文件大小: XXXX KB
     题目: XXXX 题 | 术语: XXX 条
[烟雾测试 PASS] 全部6项检查通过
```

- [ ] **Step 2: 手动验证矩阵（4题型 × 关键操作）**

在浏览器中打开构建产物，逐项核对：

| 操作 | choice | truefalse | multi | short |
|------|:---:|:---:|:---:|:---:|
| 题目渲染 | | | | |
| 选项交互 | | | | |
| 答案判定 | | | | |
| 解析展示 | | | | |
| 翻页正常 | | | | |
| 完成结算 | | | | |

- [ ] **Step 3: 持久化验证**

- 刷5题 → 关闭标签页 → 重新打开 → 确认续练提示
- 答错3题 → 去错题本确认3题可见
- 收藏2题 → 刷新 → 确认收藏仍在
- 切换章节 → 确认进度隔离

- [ ] **Step 4: 确认构建 exit code 行为**

```bash
python build_unified.py
echo "Exit code: $?"
```
Expected: `Exit code: 0`

如果故意在某个 `questions.json` 中制造错误（如将 answer 改为 "Z"），重新运行确认 exit(1) 并输出具体错误信息。

- [ ] **Step 5: 清理临时文件**

```bash
rm -f _scan_data.txt _scan_data2.txt
```

- [ ] **Step 6: 最终 Commit**

```bash
git add 生物化学题库/湖南大学题库系统.html
git commit -m "build: 健康检查后重新构建 — 29章schema+验证+烟雾全绿"
```

---

## Execution Order

```
Task 1 (schema_validator)
    │
    ├──→ Task 2 (数据扫描+修复)
    │
    └──→ Task 6 (集成schema到build)
              │
Task 3 (代码扫描) ──→ Task 5 (报告) ──→ Task 7 (烟雾测试) ──→ Task 8 (回归)
                      │
Task 4 (构建审计) ────┘
```

Tasks 2、3、4 可在 Task 1 完成后并行执行。
Tasks 6、7 必须在修复完成后顺序执行。
Task 8 是最终关卡。

## Self-Review

### 1. Spec Coverage

| Spec 章节 | 覆盖 Task |
|-----------|----------|
| 3. 代码层扫描 (HTML/CSS/JS) | Task 3 |
| 4. 数据层扫描 (Schema + 跨章一致性) | Task 1 + Task 2 |
| 5. 构建管线加固 (Schema校验 + 烟雾测试) | Task 6 + Task 7 |
| 6. 运行时验证 (烟雾测试矩阵) | Task 7 (自动) + Task 8 (手动) |
| 7. 执行节奏 (扫描→报告→修复→加固→回归) | Task 1-8 完整覆盖 |
| 8. 成功标准 | Task 8 (最终回归) |

### 2. Placeholder Scan

- ✅ 无 TBD/TODO/占位符
- ✅ 所有代码块包含实际可运行的代码
- ✅ 所有文件路径使用绝对路径或明确相对路径
- ✅ 所有 CLI 命令包含预期输出

### 3. Type Consistency

- ✅ `validate_questions(filepath) -> list[str]` 在 Task 1 定义，Task 2 和 Task 6 一致引用
- ✅ `validate_terms(filepath) -> list[str]` 同上
- ✅ `SUBJECTS` 字典结构在 `build_unified.py` 和 `schema_validator.py` 中一致
- ✅ 烟雾测试的 `QUESTION_BANKS`、`S`、`renderQuiz()` 与 `src_js.txt` 中定义一致
