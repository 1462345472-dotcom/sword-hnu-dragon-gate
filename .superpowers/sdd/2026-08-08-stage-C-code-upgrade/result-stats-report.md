# 结果页增强:累计学习统计(方案 B — 仅结果页)报告

- **日期**: 2026-08-08
- **目标文件**: `生物化学题库/湖南大学题库系统-臻至版.html`
- **提交**: 见 git log(`feat: 结果页累计统计(今日/累计刷题与正确率)`)
- **分支**: `feature/hnu-motion-redesign`
- **备份**: `生物化学题库/湖南大学题库系统-臻至版.html.bak_resultstats`(修改前 cp)
- **约束落实**: CSS 指纹 `96e3aad4f8cf0d80` 不变(零 `<style>` 改动,新样式全内联);首页零改动;既有 JS 逻辑仅新增 1 行埋点调用,行为零回归

## 一、数据模型(简化版,localStorage 持久化)

| 维度 | 键 | 结构 | 语义 |
|---|---|---|---|
| 累计 | `hnu_academy_total` | `{totalCount, totalCorrect}` | 自功能上线起累计,不跨天重置 |
| 今日 | `hnu_academy_daily_YYYY-MM-DD` | `{totalCount, totalCorrect}` | 按日期键存储;跨天后读到新键(不存在→`{0,0}`),自动从 0 新计 |

- 键名前缀与既有 `sk()`(`hnu_academy_`)一致,与现有分章键(`prog_`/`wrong_`/`bm_`)互不冲突。
- 每次 `submitAnswer`(通过守卫 `isAnswered` 拦截重复提交)在 `saveQuizProgress();saveState();` 之后调用 `_statsRecord(correct)`:count+1,答对则 correct+1;累计键与今日键同步写入。
- 写入全部 try/catch 包裹:**localStorage 写入失败不阻断主流程**(答题/保存进度照常)。
- 读取容错:`_statsRead` 对缺失/损坏 JSON 一律返回 `{totalCount:0,totalCorrect:0}`,不抛错。
- 清除数据:`clear-data` 分支在既有清空逻辑后调用 `_statsClear()`(删除累计键 + 当天键)。

## 二、展示设计(结果页,内联样式,低调不突兀)

位于现有 `result-stats`(正确/错误/连对)统计块下方、错题速览上方,一行两段:

- **今日**:`今日已练 X 题 · 答对 Y 题`
- **累计**:`累计已练 M 题 · 累计正确率 N%`(N = round(totalCorrect/totalCount*100),totalCount=0 时显示 0%)

样式全部内联 style:`font-size:.72rem; color:var(--ink-faint)`(既有主题次级色变量),数字用 `<b>` 加 `color:var(--ink-soft)` 加重;`display:flex;flex-wrap:wrap;justify-content:center;max-width:320px`(与 result-stats 同宽对齐)。**未新增/修改任何 `<style>` 规则**,CSS 指纹不变。

渲染时机:`renderResult()`(finishQuiz → switchView('result') 时)同步从存储读取快照 `_statsSnapshot()`;`clear-data` 后结果页显示 0/0%。

## 三、代码位置(共 4 处,19 行新增)

1. `submitAnswer` 末尾(埋点):`_statsRecord(correct);` — 唯一一行对既有函数的改动
2. `finishQuiz` 之后:独立存储模块(`_statsDateStr/_statsDailyKey/_statsRead/_statsWrite/_statsRecord/_statsSnapshot/_statsClear`,`_STATS_TOTAL_KEY` 常量)
3. `renderResult`:`var _ss=_statsSnapshot();var _tpct=...` + 内联统计行拼接
4. `handleClick` 的 `clear-data` 分支:`_statsClear();`

## 四、验证数据

### 1. 结构/指纹校验(`verify_chapter.py`)

```
章节对象: 51 | 总题数: 5844 | 总术语: 951 | CSS指纹: 96e3aad4f8cf0d80
OK: 全部断言通过
```

指纹与修改前一致(`<style>` 块零改动);`node --check` 提取内联 JS 语法校验通过。

### 2. Edge headless CDP 实测(`_rs_cdp_test.js`,27 项断言全部 PASS)

Edge `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --headless=new --remote-debugging-port=9358`,file:// 加载,`Runtime.evaluate` 驱动 + 真实 DOM 点击(书签/多选/名词/错题/清除按钮均真实路径),全程监听 `Runtime.exceptionThrown` / `console.error`:

| 断言组 | 结果 |
|---|---|
| 0.1-0.2 清理统计键、进入首页 | PASS |
| A1-A6 第一轮 2 题(1 对 1 错)→ 结果页显示「今日已练 2 题 · 答对 1 题 / 累计已练 2 题 · 累计正确率 50%」,localStorage 累计与今日键均为 `{totalCount:2,totalCorrect:1}`,与答题判定完全一致 | PASS |
| B1-B5 第二轮 3 题全对 → 结果页「今日已练 5 题 · 答对 4 题 / 累计已练 5 题 · 累计正确率 80%」,累计键 `{5,4}`(累加正确) | PASS |
| C1-C3 注入旧天键 `hnu_academy_daily_2000-01-01={99,50}` → 今日统计完全不受污染(隔离);`Page.reload` 后同日数据保留(持久化) | PASS |
| D1-D3 `clear-data` → 累计键与当天键均删除,结果页归零显示「今日已练 0 题 / 累计已练 0 题 / 累计正确率 0%」 | PASS |
| E1-E9 全路径回归:单选/判断作答、书签 toggle、多选 toggle+confirm、名词解释、错题本(wrong 模式+错题视图)、导出 JSON(learning-data 结构)、导入恢复 wrongSet 一致 | PASS |
| C4 跨天 mock:覆写 `window.Date` 返回 2099-01-01 → 提交 1 题 → 新键 `hnu_academy_daily_2099-01-01` 从 0 新计 `{1,1}`(跨天自动归零),累计键同步 +1(持续累加) | PASS |
| 全程 Runtime.exceptionThrown = 0,console.error = 0 | PASS |

### 3. 回归说明

- 首页(renderHome/chip/hero)零改动;既有 23 个 `data-action` 路径经 E 段回归全部正常。
- 既有 JS 逻辑仅新增 `_statsRecord(correct);` 一行调用(在 `saveState()` 之后、`return correct;` 之前),不改变任何现有语句行为。
- 导入数据(importData)为既有行为:会清空所有 `hnu_academy_*` localStorage 键(含统计键),属"导入=整体覆盖"语义,本次未改动;如需统计跨导入保留可后续迭代。

## 五、备注

- 测试脚本 `_rs_cdp_test.js`(仓库根目录,临时工件未提交,同既往约定)。
- 中途失败的数轮测试均为测试脚本自身问题(端口占用、`submitAnswer` 依赖 `curQ()` 需推进 qIndex、reload 后 confirm 覆写丢失、导出 JSON 结构为 `data.wrongSet` 嵌套),与目标功能无关;修正脚本后 27 项全绿。
- 备份 `.bak_resultstats` 供回滚。
