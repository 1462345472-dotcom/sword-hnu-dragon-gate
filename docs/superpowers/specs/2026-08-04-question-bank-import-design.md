# 题库数据精准导入 · 设计规范

## 背景

湖南大学考研题库系统（`feature/hnu-motion-redesign` 分支）已完成重设计，29个章节共2549道题目 + 516条术语需要精准导入到单文件HTML应用中。此前多次导入中途失败，需一套完整的数据验证、修正、构建流程确保一次成功。

## 范围

- **科目**：生物化学（第1-14章）、细胞生物学（第1-16章）
- **题型**：单选（choice）、判断（truefalse）、多选（multi）
- **输出**：单文件 `生物化学题库/湖南大学题库系统.html`
- **不做**：第15-31章（后续再做）

## 诊断发现的问题

### 问题1：判断题答案大小写不匹配（500题）

JSON中判断题答案为Python风格 `True`/`False`，但JS代码做严格比较 `v==='true'`，导致所有判断题无法正确评分。

```json
// JSON (错误)
{ "type": "truefalse", "answer": "True" }

// JS期望
v === 'true'  // "True" !== "true" → 永远为 false
```

### 问题2：多选题类型无系统支持（583题）

583道题 `type` 为 `"multi"`，答案格式为多字母拼接（如 `"ABC"`）。JS只过滤 `choice` 和 `truefalse`，这些题目在系统中完全不可见。

```json
{ "type": "multi", "answer": "ABC", "options": { "A": "...", "B": "...", "C": "..." } }
```

## 设计方案

### 第一步：数据修正脚本

**目标**：批量修正29个 `questions.json` 中判断题答案大小写。

**操作**：
- 遍历所有章节的 `questions.json`
- 对 `type==='truefalse'` 的题目，将 `answer` 从 `True`/`False` 转为 `true`/`false`
- 修正前后做 JSON 结构完整性校验
- 先备份（git已追踪，可回退）

**校验规则**（每道题必过）：
| 检查项 | 规则 |
|--------|------|
| 文件存在 | questions.json 可读 |
| JSON解析 | 合法JSON，顶层为数组 |
| 必填字段 | id、type、question、answer 存在且非空 |
| choice验证 | options存在、answer在options键中 |
| truefalse验证 | answer为 `true` 或 `false`（修正后） |
| multi验证 | answer每个字母都在options键中 |
| ID唯一性 | 同章内无重复id |

**容错**：任一检查失败 → 打印文件名+题目ID+具体错误 → 终止，不写回。

### 第二步：JS功能补全（src_js.txt）

**改动点**（6处）：

| # | 代码位置 | 改动内容 |
|---|---------|---------|
| 1 | 模式过滤 `L199-200` | 新增 `else if(mode==='multi')` 过滤 |
| 2 | `typeLabel` `L431` | 增加 `t==='multi'?'多选'` 分支 |
| 3 | 选项渲染 `L579-595` | 新增 multi 分支：勾选框 + 确认按钮 |
| 4 | `submitAnswer` `L268-276` | multi答案排序后比较 |
| 5 | 答案比较 `L773` | truefalse 加 `toLowerCase()` 双保险 |
| 6 | UI入口 | 章节页增加"多选题"模式入口 |

**多选题交互设计**：
- 选项渲染为可勾选按钮（视觉上区别于单选圆点）
- 点击选项切换选中/取消状态
- 至少选中1项后显示"确认提交"按钮
- 提交时：选中字母排序拼接（如 `"CAB"`→`"ABC"`）→ 与answer严格比较

**防御性设计**：
- truefalse比较：`String(v).toLowerCase()==='true'`
- multi已提交不可更改（与choice/truefalse一致，`locked`机制复用）

### 第三步：构建脚本加固（build_unified.py）

**改造 `load_data()`**：数据加载后、构建前插入强制验证关卡。

```
加载JSON → 验证关卡 → 归一化 → 构建
```

**验证关卡**（所有章节全过才放行）：
1. 每个章节 questions.json 存在且可解析
2. 每道题必填字段完整
3. choice 的 answer 在 options 中
4. truefalse 的 answer 为 `true`/`false`
5. multi 的 answer 每个字符都是有效选项键
6. 同章ID无重复
7. 术语 terms.json 存在且可解析（不存在则警告不阻断）

**失败处理**：打印精确错误列表 → `sys.exit(1)` → 不生成HTML

**归一化**（验证通过后）：
- truefalse answer 强制 `.lower()` → 双保险
- 空 tags → `[]`
- 空 difficulty → `1`
- 术语格式统一（支持 dict 和 list 两种旧格式）

### 第四步：构建输出

- 输出路径：`生物化学题库/湖南大学题库系统.html`
- 构建报告：打印章节数、总题数、题型分布、术语数、文件大小

## 技术约束

- **不改变现有数据模型**：`id/type/question/options/answer/explanation/difficulty/tags` 结构不变
- **不改变现有CSS**：multi选项复用现有颜色系统（剑/指/湖/大），新增少量样式
- **JS保持ES5兼容**：不引入箭头函数、模板字符串等新语法
- **图片嵌入行为不变**：logo/emblem/bg 三张图 base64 嵌入

## 测试策略

执行计划中每步完成后验证：
1. 数据修正后：运行验证脚本，确认0错误
2. JS改动后：手动验证三种题型渲染和评分逻辑
3. 构建后：打开HTML，分别进入三种模式刷题，验证评分、错题、进度保存
4. 回归检查：确认练习模式、考试模式、错题本、收藏、术语表功能正常

## 涉及文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `生物化学题库/*/questions.json` (13章) | 修改 | truefalse答案修正 |
| `细胞生物学题库/*/questions.json` (16章) | 修改 | truefalse答案修正 |
| `src_js.txt` | 修改 | 6处JS改动 |
| `build_unified.py` | 修改 | 添加验证关卡+归一化 |
| `生物化学题库/湖南大学题库系统.html` | 生成 | 构建输出 |
