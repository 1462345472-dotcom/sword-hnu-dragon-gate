# 阶段 C 实施计划:代码全方位升级(UI 完全不变)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对臻至版 HTML(单文件,51 对象/5844 题/951 术语)做代码层升级:启动解析、渲染、进度存储、索引、健壮性、数据层——UI 完全不变(CSS 指纹 96e3aad4f8cf0d80 全程保持)。

**Architecture:** 保持单文件内嵌架构;JS 层做懒初始化(题目数据按需解析)、渲染最小化、分章存储、索引预建、错误兜底、状态封装;每项优化独立提交、可回滚,浏览器实测验证。

**Tech Stack:** 原生 JS(单文件 HTML)、Edge headless 浏览器实测、verify_chapter.py(数据完整性)、Python 脚本(基线测量)。

## Global Constraints

- **UI 零改动**:不碰任何 CSS/HTML 结构;CSS 指纹每步验证必须一致(96e3aad4f8cf0d80)
- 保持单文件内嵌(不破坏离线可用)
- 每项优化:备份 → 改 → 功能验证 → 浏览器实测 → git 提交;失败即回滚该改动
- 功能无回归:51 章做题全流程(4 题型)、名词解释页、错题本、书签
- 数据完整性:每次改动后 verify_chapter.py 断言通过(51 对象/5844 题/951 术语)

---

### Task 1: 基线性能测量

**Files:**
- Create: `perf_baseline.py`(测量工具)

**Interfaces:**
- Produces: `perf_baseline.py`(Edge headless 测量页面加载耗时、JS 执行时间)

- [ ] **Step 1: 写基线测量脚本**

```python
# perf_baseline.py
# -*- coding: utf-8 -*-
"""测量臻至版 HTML 加载性能基线:用 Edge headless 计时。"""
import subprocess, time, re, sys
sys.stdout.reconfigure(encoding='utf-8')

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html"

def measure(times=3):
    results = []
    for i in range(times):
        t0 = time.time()
        subprocess.run([EDGE, "--headless", "--disable-gpu", "--dump-dom", URL],
                       capture_output=True, timeout=120)
        results.append(time.time() - t0)
    return results

if __name__ == "__main__":
    r = measure()
    print(f"加载耗时 {len(r)} 次: {[round(x,2) for x in r]} 秒, 平均 {round(sum(r)/len(r),2)} 秒")
```

- [ ] **Step 2: 运行并记录基线**

Run: `python perf_baseline.py`
Expected: 输出 3 次加载耗时与平均(记录为基线,后续每项优化后对比)

- [ ] **Step 3: 提交**

```bash
git add perf_baseline.py
git commit -m "perf: 基线测量脚本 + 加载耗时基线(记录)"
```

---

### Task 2: 启动解析优化(懒初始化)

**Files:**
- Modify: `生物化学题库/湖南大学题库系统-臻至版.html`(JS 部分,不动 CSS/HTML 结构)

**Interfaces:**
- Consumes: 现状 `QUESTION_BANKS` 全量对象;`getBank(subjectKey)` 读取函数
- Produces: 懒初始化——`QUESTION_BANKS` 定义保持,但增加 `_banksReady` 标记与按需解析路径

- [ ] **Step 1: 定位当前解析路径**

在 HTML 中找 `QUESTION_BANKS` 定义与 `getBank`/`allQs` 函数,确认当前全量解析位置

- [ ] **Step 2: 实现懒初始化(最小侵入)**

方案:保持 `var QUESTION_BANKS = {...}` 字面量不变(数据形式不动),但将"启动时立即全量遍历/统计"改为按需——检查是否有启动即遍历 QUESTION_BANKS 的代码(如统计总题数、渲染首页),如有改为懒计算(首次需要时再遍历,结果缓存)。

注意:JS 引擎解析 10MB 字面量本身耗时无法避免(数据内嵌),优化目标是**减少启动时的额外遍历与 DOM 工作**。若当前启动无全量遍历,本任务记录"无需改动"结论并提交说明。

- [ ] **Step 3: 功能验证**

Run: Edge headless dump-dom,确认:首页渲染正常、51 章节键出现、无 JS 错误
Run: `python verify_chapter.py` 断言通过
Run: `python perf_baseline.py` 对比基线

- [ ] **Step 4: 浏览器实测 + 提交**

```bash
git add 生物化学题库/湖南大学题库系统-臻至版.html
git commit -m "perf: 启动解析优化(懒计算统计,减少启动遍历)"
```

---

### Task 3: 渲染性能优化

**Files:**
- Modify: HTML(JS 渲染函数,UI 视觉不变)

- [ ] **Step 1: 定位高频渲染函数**

`renderQuiz`/`renderHome`/`renderTerms` 的全量 innerHTML 重建路径

- [ ] **Step 2: 最小化更新**

原则:视觉输出完全一致,仅减少不必要的重建——如 renderQuiz 在"切选项"时若仅需更新选中态,避免整卡重建(用 classList 切换);renderHome 的进度环仅更新数值部分。**若某处改动会影响视觉输出,放弃该处(保持现状)**。

- [ ] **Step 3: 功能验证 + 浏览器实测 + 提交**

同 Task 2 Step 3-4;commit: `perf: 渲染最小化更新(UI视觉不变)`

---

### Task 4: 进度存储优化

**Files:**
- Modify: HTML(JS 状态存储逻辑)

- [ ] **Step 1: 定位存储代码**

`savedProgress`/`S.answers`/`localStorage` 读写位置

- [ ] **Step 2: 分章存储 + 合并**

答案进度按章节键分块存储,读时合并;写时只写变化章节。保持读取接口不变(其他代码无感)。

- [ ] **Step 3: 功能验证**(重点:恢复进度、错题本、书签) + 浏览器实测 + 提交

commit: `perf: 进度分章存储(localStorage读写优化)`

---

### Task 5: 索引优化

**Files:**
- Modify: HTML(JS)

- [ ] **Step 1: 定位过滤/遍历代码**

名词解释过滤(filter-terms)、章节切换的遍历

- [ ] **Step 2: 预建索引**

启动时(或首次需要时)建 `chapter → questionIds` 映射缓存;过滤操作只遍历本章。接口不变。

- [ ] **Step 3: 功能验证 + 浏览器实测 + 提交**

commit: `perf: 章节索引预建(过滤O(n)→O(章内))`

---

### Task 6: 逻辑健壮性

**Files:**
- Modify: HTML(JS)

- [ ] **Step 1: 数据解析兜底**

QUESTION_BANKS 解析异常时显示友好提示(而非白屏);getBank 返回 null 时 toast 提示

- [ ] **Step 2: 事件委托完整性**

核对 handleClick 所有 data-action case 均有实现(列出清单核对,缺失的补兜底)

- [ ] **Step 3: 状态管理封装**

answers/revealed/bookmarks 读写封装为统一函数(如 `getAnswer(subject,qid)`/`setAnswer(...)`),替换散落调用

- [ ] **Step 4: 功能验证**(重点:所有交互路径) + 浏览器实测 + 提交

commit: `feat: 健壮性(解析兜底/委托完整/状态封装)`

---

### Task 7: 数据层自检 + short 解析润色

**Files:**
- Modify: HTML(JS 自检)+ 各章 questions.json(short 题解析润色)

- [ ] **Step 1: 启动自检**

HTML 加载后自检:章节对象数与 stats 一致、关键字段存在;异常时 console 警告 + 界面提示

- [ ] **Step 2: short 解析润色**

对解析与答案复述冗余的 short 题,润色解析(补充实质讲解,不改变答案内容)。**数据层修改需同步 HTML 内嵌数据**(用 replace_chapter.py 更新)。

- [ ] **Step 3: 功能验证 + 浏览器实测 + 提交**

commit: `feat: 数据自检 + short解析润色`

---

### Task 8: 兼容性验证 + 最终实测 + 验收

**Files:**
- Create: `docs/superpowers/research/stage-C-complete-report.md`

- [ ] **Step 1: 全量回归**

浏览器实测:51 章节全部可进入、4 题型做题全流程、名词解释、错题本、书签、切章、多选交互
Run: `python verify_chapter.py --expect-objects 51 --expect-questions 5844 --expect-terms 951 --fingerprint 96e3aad4f8cf0d80`

- [ ] **Step 2: 性能对比**

Run: `python perf_baseline.py` 对比 Task 1 基线,记录提升幅度

- [ ] **Step 3: 写阶段 C 验收报告并提交**

commit: `docs: 阶段C验收报告(性能对比+UI零改动确认)`

---

## Self-Review

- **Spec coverage:** 设计 7 个优化项全部覆盖(Task 2-7)+ 基线(Task 1)+ 验收(Task 8)。✅
- **Placeholder scan:** 无 TBD;Task 2 含"若无需改动记录结论"的合理分支(基于实际代码检查)。✅
- **Type consistency:** verify_chapter.py/perf_baseline.py 接口在 Task 1 定义,后续任务引用一致。✅
- **风险控制:** 每任务独立提交可回滚;UI 视觉不变是硬约束(Task 3 明确"若影响视觉放弃该处")。✅
