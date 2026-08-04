# 题库数据精准导入 · 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将29个章节共2549道题目精准导入题库系统HTML，修复判断题答案大小写问题，补全多选题功能，加固构建脚本。

**Architecture:** 分三步执行：①Python脚本批量修正29个JSON中truefalse答案 → ②JS端6处改动支持multi题型 + truefalse防御 → ③build_unified.py加验证关卡后构建。每步独立验证。

**Tech Stack:** Python 3, Vanilla JS (ES5), JSON, 单文件HTML

**Source Spec:** `docs/superpowers/specs/2026-08-04-question-bank-import-design.md`

## Global Constraints

- JS必须保持ES5兼容（无箭头函数、模板字符串、const/let）
- 不改变现有CSS类名体系，复用`.option`/`.tf-btn`/`.selected`/`.locked`/`.correct`/`.wrong`
- 不改变数据模型结构（id/type/question/options/answer/explanation/difficulty/tags）
- 构建失败必须`sys.exit(1)`，不生成损坏的HTML
- 图片嵌入（logo/emblem/bg）行为不变

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|------|------|
| `fix_truefalse.py` | 新建 | 批量修正29章truefalse答案 + 全量验证，用后删除 |
| `src_js.txt` | 修改 | JS核心逻辑，6处改动 |
| `src_css.txt` | 修改 | 新增multi选项样式（1处追加） |
| `build_unified.py` | 修改 | 添加验证关卡+归一化 |
| `生物化学题库/湖南大学题库系统.html` | 生成 | 构建输出 |

---

### Task 1: 数据修正 — 批量修正truefalse答案 + 全量验证

**Files:**
- Create: `fix_truefalse.py`（临时脚本，验证通过后删除）

**Interfaces:**
- Consumes: 29个 `questions.json` 文件
- Produces: 修正后的 questions.json（仅truefalse答案字段变化），终端输出修正报告

- [ ] **Step 1: 编写修正+验证脚本**

```python
#!/usr/bin/env python3
"""修正判断题答案 True→true, False→false + 全量数据验证"""
import json, os, sys

BASE = r'c:\Users\Lenovo\Desktop\湖南大学'

CHAPTERS = [
    ('生物化学', '1+2', '生物化学题库/第一章+第二章'),
    ('生物化学', '3', '生物化学题库/第三章'),
    ('生物化学', '4', '生物化学题库/第四章'),
    ('生物化学', '5', '生物化学题库/第五章'),
    ('生物化学', '6', '生物化学题库/第六章'),
    ('生物化学', '7', '生物化学题库/第七章'),
    ('生物化学', '8', '生物化学题库/第八章'),
    ('生物化学', '9', '生物化学题库/第九章'),
    ('生物化学', '10', '生物化学题库/第十章'),
    ('生物化学', '11', '生物化学题库/第十一章'),
    ('生物化学', '12', '生物化学题库/第十二章'),
    ('生物化学', '13', '生物化学题库/第十三章'),
    ('生物化学', '14', '生物化学题库/第十四章'),
    ('细胞生物学', '1', '细胞生物学题库/第一章绪论'),
    ('细胞生物学', '2', '细胞生物学题库/第二章'),
    ('细胞生物学', '3', '细胞生物学题库/第三章'),
    ('细胞生物学', '4', '细胞生物学题库/第四章'),
    ('细胞生物学', '5', '细胞生物学题库/第五章'),
    ('细胞生物学', '6', '细胞生物学题库/第六章'),
    ('细胞生物学', '7', '细胞生物学题库/第七章'),
    ('细胞生物学', '8', '细胞生物学题库/第八章'),
    ('细胞生物学', '9', '细胞生物学题库/第九章'),
    ('细胞生物学', '10', '细胞生物学题库/第十章'),
    ('细胞生物学', '11', '细胞生物学题库/第十一章'),
    ('细胞生物学', '12', '细胞生物学题库/第十二章'),
    ('细胞生物学', '13', '细胞生物学题库/第十三章'),
    ('细胞生物学', '14', '细胞生物学题库/第十四章'),
    ('细胞生物学', '15', '细胞生物学题库/第十五章'),
    ('细胞生物学', '16', '细胞生物学题库/第十六章'),
]

errors = []
fixes = 0

for subject, ch_num, ch_dir in CHAPTERS:
    qf = os.path.join(BASE, ch_dir, 'questions.json')
    label = '%s 第%s章' % (subject, ch_num)

    # 1. 加载
    if not os.path.exists(qf):
        errors.append('[MISSING] %s: questions.json不存在' % label)
        continue
    try:
        with open(qf, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except Exception as e:
        errors.append('[PARSE] %s: %s' % (label, e))
        continue
    if not isinstance(questions, list):
        errors.append('[FORMAT] %s: 不是数组' % label)
        continue
    if len(questions) == 0:
        errors.append('[EMPTY] %s: 题目数为0' % label)
        continue

    # 2. 逐题验证 + 修正
    ids_seen = set()
    for q in questions:
        qid = q.get('id', '?')

        # 必填字段
        for field in ['id', 'type', 'question', 'answer']:
            if field not in q:
                errors.append('[%s #%s] 缺少字段: %s' % (label, qid, field))
            elif field == 'question' and (not q[field] or len(str(q[field]).strip()) < 2):
                errors.append('[%s #%s] question为空或过短' % (label, qid))
            elif field == 'answer' and not str(q[field]).strip():
                errors.append('[%s #%s] answer为空' % (label, qid))

        qtype = q.get('type', '')

        # 判断题：修正大小写
        if qtype == 'truefalse':
            ans = str(q['answer']).strip()
            if ans in ('True', 'true', 'TRUE'):
                q['answer'] = 'true'
                fixes += 1
            elif ans in ('False', 'false', 'FALSE'):
                q['answer'] = 'false'
                fixes += 1
            else:
                errors.append('[%s #%s] TF答案异常: %r' % (label, qid, ans))

        # 选择题：验证options
        if qtype == 'choice':
            if 'options' not in q or not isinstance(q.get('options'), dict):
                errors.append('[%s #%s] choice缺options' % (label, qid))
            else:
                ans = str(q.get('answer', ''))
                if ans and ans not in q['options']:
                    errors.append('[%s #%s] answer=%s不在options中: %s' % (
                        label, qid, ans, list(q['options'].keys())))

        # 多选题：验证answer每个字母在options中
        if qtype == 'multi':
            if 'options' not in q or not isinstance(q.get('options'), dict):
                errors.append('[%s #%s] multi缺options' % (label, qid))
            else:
                ans = str(q.get('answer', ''))
                opt_keys = list(q['options'].keys())
                for ch in ans:
                    if ch not in opt_keys:
                        errors.append('[%s #%s] multi answer中%s不在options中: %s' % (
                            label, qid, ch, opt_keys))

        # 题型合法性
        if qtype not in ('choice', 'truefalse', 'multi'):
            errors.append('[%s #%s] 无效题型: %s' % (label, qid, qtype))

        # ID重复检查
        if qid != '?' and qid in ids_seen:
            errors.append('[%s] 重复ID: %s' % (label, qid))
        ids_seen.add(qid)

    # 3. 有修正则写回
    if not errors:
        with open(qf, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print('  [OK] %s: %d题' % (label, len(questions)))

# 4. 报告
print()
total_q = 0
for _, _, ch_dir in CHAPTERS:
    qf = os.path.join(BASE, ch_dir, 'questions.json')
    if os.path.exists(qf):
        with open(qf, 'r', encoding='utf-8') as f:
            total_q += len(json.load(f))

print('===== 修正报告 =====')
print('章节: %d' % len(CHAPTERS))
print('总题数: %d' % total_q)
print('修正数(True→true): %d' % fixes)
print('错误: %d' % len(errors))

if errors:
    print('\n===== 错误详情 =====')
    for e in errors:
        print('  ERROR: ' + e)
    print('\n修正中止 - 请修复以上错误后重试')
    sys.exit(1)
else:
    print('\n全部通过 - 数据修正完成')
```

- [ ] **Step 2: 执行修正脚本**

```bash
cd "c:\Users\Lenovo\Desktop\湖南大学"
python fix_truefalse.py
```

期望输出：29章节全部 `[OK]`，`错误: 0`，`sys.exit(0)`

- [ ] **Step 3: 再次运行验证确认0错误**

```bash
python fix_truefalse.py
```

第二次运行应显示 `修正数(True→true): 0`（已修正完毕），`错误: 0`

- [ ] **Step 3: 提交**

```bash
git add 生物化学题库/*/questions.json 细胞生物学题库/*/questions.json
git commit -m "fix: 统一判断题答案格式 True→true, False→false (500题)"
```

---

### Task 2: JS改动① — startQuiz + startChapterMode 支持 multi 过滤

**Files:**
- Modify: `src_js.txt:142-153` (startQuiz函数)
- Modify: `src_js.txt:232-248` (startChapterMode函数)

**Interfaces:**
- Consumes: QUESTION_BANKS 中的 questions（含multi题型）
- Produces: `startQuiz(key, 'multi')` 和 `startChapterMode(key, 'multi')` 正常工作

- [ ] **Step 1: 修改 startQuiz — 允许 multi 模式过滤**

编辑 `src_js.txt`，找到第146行：

```js
  else if(mode==='choice'||mode==='truefalse'){
```

替换为：

```js
  else if(mode==='choice'||mode==='truefalse'||mode==='multi'){
```

完整上下文（L142-153）：

```js
function startQuiz(key,mode){
  S.subject=key;S.quizMode=mode||'all';S.qIndex=0;S.answers={};S.revealed={};S.streak=0;
  if(mode==='wrong')S.questions=shuffle(wrongQs());
  else if(mode==='bookmarked')S.questions=shuffle(bmQs());
  else if(mode==='choice'||mode==='truefalse'||mode==='multi'){
    var qs=allQs();var ft=mode;
    S.questions=shuffle(qs.filter(function(q){return q.type===ft;}));
  }
  else S.questions=shuffle(allQs());
  if(S.questions.length===0){toast('没有可刷的题目');return false;}
  return true;
}
```

- [ ] **Step 2: 修改 startChapterMode — 允许 multi 过滤**

编辑 `src_js.txt`，第234行：

```js
  var filtered=b.questions.filter(function(q){return q.type===filterType;});
```

此行已将 `filterType` 传入比较，如果 `filterType==='multi'`，它会正确过滤 `q.type==='multi'`。**无需修改**。但需确认调用方 `data-action="start-multi"` 会传入 `'multi'`（Task 5处理）。

- [ ] **Step 3: 验证**

用grep确认改动无误：

```bash
grep -n "mode==='choice'||mode==='truefalse'||mode==='multi'" src_js.txt
```

期望：输出第146行匹配

---

### Task 3: JS改动② — typeLabel + renderQuiz 中 multi 渲染

**Files:**
- Modify: `src_js.txt:431` (typeLabel)
- Modify: `src_js.txt:554` (renderQuiz中isCorrect比较)
- Modify: `src_js.txt:570` (renderQuiz中点阵进度dot比较)
- Modify: `src_js.txt:579-595` (renderQuiz中选项渲染)
- Modify: `src_js.txt:644` (finishQuiz中correct计数)

- [ ] **Step 1: 修正 typeLabel**

`src_js.txt` 第431行，将：

```js
function typeLabel(t){return t==='choice'?'单选':'判断';}
```

替换为：

```js
function typeLabel(t){return t==='choice'?'单选':t==='truefalse'?'判断':'多选';}
```

- [ ] **Step 2: 修正 renderQuiz 中 answer 比较逻辑**

`src_js.txt` 第554行，将：

```js
  var ua=S.answers[q.id];var isCorrect=(ua===q.answer);
```

替换为：

```js
  var ua=S.answers[q.id];
  var isCorrect;
  if(q.type==='multi'){
    isCorrect=(ua===q.answer);
  }else if(q.type==='truefalse'){
    isCorrect=(String(ua).toLowerCase()===String(q.answer).toLowerCase());
  }else{
    isCorrect=(ua===q.answer);
  }
```

- [ ] **Step 3: 修正点阵进度dot的比较（multi需排序后比较）**

`src_js.txt` 第570行，将：

```js
    else{var aid=S.questions[d].id;if(S.answers[aid]!==undefined){dotCls+=S.answers[aid]===S.questions[d].answer?' done':' wrong-dot';}}
```

替换为：

```js
    else{var aid=S.questions[d].id;if(S.answers[aid]!==undefined){
      var dotQ=S.questions[d];var dotCorrect;
      if(dotQ.type==='multi'){
        dotCorrect=(S.answers[aid]===dotQ.answer);
      }else if(dotQ.type==='truefalse'){
        dotCorrect=(String(S.answers[aid]).toLowerCase()===String(dotQ.answer).toLowerCase());
      }else{
        dotCorrect=(S.answers[aid]===dotQ.answer);
      }
      dotCls+=dotCorrect?' done':' wrong-dot';
    }}
```

- [ ] **Step 4: 在 renderQuiz 中添加 multi 选项渲染**

`src_js.txt` 第579-595行是选项渲染区域。在 `if(q.type==='choice'){...}else{...}` 块中添加 multi 分支。

将整个选项渲染块（L579-595）替换为：

```js
  var optsHTML='';
  if(q.type==='choice'){
    var lts=Object.keys(q.options);optsHTML='<div class="options-list">';
    for(var i=0;i<lts.length;i++){
      var lt=lts[i],txt=q.options[lt],cls='option '+colorClassMap[i];
      if(revealed){cls+=' locked';if(lt===q.answer)cls+=' correct';else if(lt===ua&&!isCorrect)cls+=' wrong';}
      else if(ua===lt)cls+=' selected';
      optsHTML+='<div class="'+cls+'" data-action="answer" data-value="'+lt+'"><span class="option-letter">'+letterMap[i]+'</span><span class="option-text">'+txt+'</span></div>';
    }
    optsHTML+='</div>';
  }else if(q.type==='multi'){
    var lts=Object.keys(q.options);optsHTML='<div class="options-list">';
    var selectedSet=ua?ua.split(''):[];
    for(var i=0;i<lts.length;i++){
      var lt=lts[i],txt=q.options[lt],cls='option multi-option '+colorClassMap[i];
      if(revealed){cls+=' locked';
        if(q.answer.indexOf(lt)>=0)cls+=' correct';
        else if(selectedSet.indexOf(lt)>=0&&q.answer.indexOf(lt)<0)cls+=' wrong';
      }else if(selectedSet.indexOf(lt)>=0)cls+=' selected';
      optsHTML+='<div class="'+cls+'" data-action="multi-toggle" data-value="'+lt+'"><span class="option-letter">'+letterMap[i]+'</span><span class="option-text">'+txt+'</span></div>';
    }
    optsHTML+='</div>';
    if(!revealed){
      optsHTML+='<div class="multi-confirm-wrap"><button class="btn btn-primary multi-confirm-btn" data-action="multi-confirm"'+(selectedSet.length===0?' disabled':'')+'>确认提交</button></div>';
    }
  }else{
    var tCls='tf-btn',fCls='tf-btn';
    if(revealed){tCls+=' locked';fCls+=' locked';
      if(q.answer===true||q.answer==='true')tCls+=' correct';else fCls+=' correct';
      if((ua===true||ua==='true')&&!isCorrect)tCls+=' wrong';if((ua===false||ua==='false')&&!isCorrect)fCls+=' wrong';
    }else if(ua===true||ua==='true')tCls+=' selected-t';else if(ua===false||ua==='false')fCls+=' selected-f';
    optsHTML='<div class="tf-row"><div class="'+tCls+'" data-action="answer" data-value="true"><span class="option-letter opt-jian" style="display:inline-flex;margin-right:8px;vertical-align:middle">剑</span>正确</div><div class="'+fCls+'" data-action="answer" data-value="false"><span class="option-letter opt-zhi" style="display:inline-flex;margin-right:8px;vertical-align:middle">指</span>错误</div></div>';
  }
```

- [ ] **Step 5: 修正 finishQuiz 中 correct 计数**

`src_js.txt` 第644行，将：

```js
  for(var i=0;i<total;i++){if(S.answers[qs[i].id]===qs[i].answer)correct++;}
```

替换为：

```js
  for(var i=0;i<total;i++){
    var fq=qs[i];var fa=S.answers[fq.id];
    if(fq.type==='truefalse'){
      if(String(fa).toLowerCase()===String(fq.answer).toLowerCase())correct++;
    }else{
      if(fa===fq.answer)correct++;
    }
  }
```

- [ ] **Step 6: 同样修正第658行的 correct 计数**

查找 `src_js.txt` 第658行附近的另一个correct计数循环（历史记录中），做同样修正：

```js
  for(var i=0;i<total;i++){
    var hq=qs[i];var ha=S.answers[hq.id];
    if(hq.type==='truefalse'){
      if(String(ha).toLowerCase()===String(hq.answer).toLowerCase())correct++;
    }else{
      if(ha===hq.answer)correct++;
    }
  }
```

- [ ] **Step 7: 提交**

```bash
git add src_js.txt
git commit -m "feat: JS支持multi题型 + truefalse大小写防御 + typeLabel修正"
```

---

### Task 4: JS改动③ — 事件处理：multi-toggle + multi-confirm + start-multi

**Files:**
- Modify: `src_js.txt:770-784` (事件分发switch-case，新增case)

**Interfaces:**
- Consumes: DOM事件 `data-action="multi-toggle"` 和 `data-action="multi-confirm"`
- Produces: 多选题选中状态管理、提交、评分

- [ ] **Step 1: 在事件分发中添加 multi-toggle 和 multi-confirm case**

`src_js.txt` 事件处理switch中，在 `case'answer':` 块之后（约L784之后），添加：

```js
    case'multi-toggle':
      if(a.classList.contains('locked'))return;
      var mv=a.getAttribute('data-value');var mq=curQ();if(!mq)return;
      if(!S._multiSelection)S._multiSelection={};
      if(!S._multiSelection[mq.id])S._multiSelection[mq.id]=[];
      var msel=S._multiSelection[mq.id];
      var mIdx=msel.indexOf(mv);
      if(mIdx>=0){msel.splice(mIdx,1);}else{msel.push(mv);}
      renderQuiz();
      break;
    case'multi-confirm':
      var mq2=curQ();if(!mq2)return;
      var sel=(S._multiSelection&&S._multiSelection[mq2.id])?S._multiSelection[mq2.id].slice():[];
      if(sel.length===0)return;
      sel.sort();var uaStr=sel.join('');
      var mCorrect=submitAnswer(mq2.id,uaStr);
      delete S._multiSelection[mq2.id];
      renderQuiz();
      var mqEl=document.querySelector('.option.multi-option.correct');
      if(mqEl)setTimeout(function(){mqEl.scrollIntoView({behavior:'smooth',block:'nearest'});},150);
      break;
```

- [ ] **Step 2: 在所有恢复/新建路径中初始化 _multiSelection**

需要在3个位置添加 `S._multiSelection={};`：

**位置A** — `startQuizWithProgress` 直接恢复分支（约L195，`S.qIndex=saved.qIndex||0;` 之后）：
```js
    S._multiSelection={};
```

**位置B** — `resumeSavedProgress` 函数（约L180附近），在恢复状态赋值之后：
```js
    S._multiSelection={};
```

**位置C** — `startFreshQuiz` 函数，函数体内：
```js
  S._multiSelection={};
```

- [ ] **Step 3: 提交**

```bash
git add src_js.txt
git commit -m "feat: JS多选交互 — multi-toggle/multi-confirm事件处理"
```

---

### Task 5: UI入口 — 首页添加"多选专项"卡片

**Files:**
- Modify: `src_js.txt:528-529`（在"判断专项"卡片后插入"多选专项"卡片）

- [ ] **Step 1: 在判断专项卡片后插入多选专项卡片**

在 `src_js.txt` 第528行（`</div>` 关闭判断专项卡片）之后、第530行（错题集注释行）之前，插入：

```js

        '<!-- 意象：墨滴湘江 — 五色交辉·多元并蓄 -->'+
        '<div class="tab-debate tab-debate-ent" data-action="start-multi" role="button">'+
          '<div class="debate-row">'+
            '<div class="debate-left"><span class="debate-mark-t">A</span><span class="debate-mark-t" style="margin-left:2px">B</span></div>'+
            '<div class="debate-divider"></div>'+
            '<div class="debate-right"><span class="debate-mark-f">C</span><span class="debate-mark-f" style="margin-left:2px">D</span></div>'+
          '</div>'+
          '<div class="debate-title-row"><span class="debate-label">多选专项</span></div>'+
        '</div>'+

```

- [ ] **Step 2: 在事件处理中添加 start-multi case**

`src_js.txt` 第753行 `case'start-truefalse':` 块之后，添加：

```js
    case'start-multi':
      startChapterMode(S.subject,'multi');
      break;
```

- [ ] **Step 3: 提交**

```bash
git add src_js.txt
git commit -m "feat: 首页新增多选专项入口卡片"
```

---

### Task 6: CSS — 多选确认按钮样式

**Files:**
- Modify: `src_css.txt`（末尾追加）

- [ ] **Step 1: 在CSS末尾追加多选确认按钮样式**

在 `src_css.txt` 末尾追加：

```css
/* ============================================================
   多选专项 — 确认按钮
   ============================================================ */
.multi-confirm-wrap{text-align:center;margin-top:var(--s-3);}
.multi-confirm-btn{padding:10px 40px;font-size:.88rem;border-radius:var(--r-lg);}
.multi-confirm-btn:disabled{opacity:.35;pointer-events:none;}
```

- [ ] **Step 2: 提交**

```bash
git add src_css.txt
git commit -m "feat: 多选题确认按钮样式"
```

---

### Task 7: 构建脚本加固 — build_unified.py 添加验证关卡

**Files:**
- Modify: `build_unified.py:250-293` (load_data函数)

- [ ] **Step 1: 在 load_data 的数据加载循环后、return前插入验证关卡**

修改 `load_data()` 函数，在 `return banks` 之前插入验证逻辑。找到第286行附近（`banks[key] = {...}` 循环结束后，`return banks` 之前），插入：

```python
    # ============================================================
    # 验证关卡 — 任一失败立即终止
    # ============================================================
    print('\n[验证] 检查数据完整性...')
    validation_errors = []
    for key, bank in banks.items():
        qs = bank['questions']
        ids_seen = set()
        for q in qs:
            qid = q.get('id', '?')
            # 必填字段
            for field in ['id', 'type', 'question', 'answer']:
                if field not in q:
                    validation_errors.append('[%s #%s] 缺少字段: %s' % (key, qid, field))
            # choice验证
            if q.get('type') == 'choice':
                opts = q.get('options', {})
                ans = str(q.get('answer', ''))
                if not isinstance(opts, dict) or len(opts) == 0:
                    validation_errors.append('[%s #%s] choice缺少有效options' % (key, qid))
                elif ans and ans not in opts:
                    validation_errors.append('[%s #%s] answer=%s不在options中' % (key, qid, ans))
            # truefalse验证
            if q.get('type') == 'truefalse':
                ans = str(q.get('answer', '')).strip().lower()
                if ans not in ('true', 'false'):
                    validation_errors.append('[%s #%s] TF答案非true/false: %s' % (key, qid, ans))
            # multi验证
            if q.get('type') == 'multi':
                opts = q.get('options', {})
                ans = str(q.get('answer', ''))
                if not isinstance(opts, dict) or len(opts) == 0:
                    validation_errors.append('[%s #%s] multi缺少有效options' % (key, qid))
                else:
                    for ch in ans:
                        if ch not in opts:
                            validation_errors.append('[%s #%s] multi answer中%s不在options中' % (key, qid, ch))
            # 题型合法性
            if q.get('type') not in ('choice', 'truefalse', 'multi'):
                validation_errors.append('[%s #%s] 无效题型: %s' % (key, qid, q.get('type')))
            # ID唯一
            if qid != '?' and qid in ids_seen:
                validation_errors.append('[%s] 重复ID: %s' % (key, qid))
            ids_seen.add(qid)

    if validation_errors:
        print('\n[验证失败] 发现 %d 个错误:' % len(validation_errors))
        for err in validation_errors:
            print('  ERROR: ' + err)
        print('\n构建中止 - 请修复以上错误后重试')
        sys.exit(1)
    print('[验证通过] 所有数据完整，开始构建...\n')
```

在 `import json, os, sys, base64` 行确认已导入 `sys`（已在文件中）。

- [ ] **Step 2: 提交**

```bash
git add build_unified.py
git commit -m "feat: build_unified.py 添加构建前数据验证关卡"
```

---

### Task 8: 构建 + 全功能验证

**Files:**
- Generate: `生物化学题库/湖南大学题库系统.html`

- [ ] **Step 1: 执行构建**

```bash
cd "c:\Users\Lenovo\Desktop\湖南大学"
python build_unified.py
```

期望输出：
```
[验证通过] 所有数据完整，开始构建...
[OK] ...湖南大学题库(1).html
    文件大小: XXX KB
    题目: 2549 题 | 术语: 516 条
```

如果验证失败，终止并修复。

- [ ] **Step 2: 手动验证清单**

构建成功后，用浏览器打开HTML文件，逐项验证：

1. ✅ 首页显示两个科目选项卡
2. ✅ 章节切换正常（生物化学1-14章、细胞生物学1-16章皆可选）
3. ✅ "选择专项"入口 → 只显示单选题 → 正常答题评分
4. ✅ "判断专项"入口 → 只显示判断题 → 答案正确评判（不区分大小写）
5. ✅ "多选专项"入口 → 只显示多选题 → 勾选→确认→评分
6. ✅ "全部刷题"入口 → 三种题型混合出现
7. ✅ 错题集功能正常
8. ✅ 术语表正常显示
9. ✅ 收藏功能正常
10. ✅ 进度保存/恢复正常

- [ ] **Step 3: 提交构建产物**

```bash
git add "生物化学题库/湖南大学题库系统.html"
git commit -m "build: 2549题 516术语 多选功能上线"
```

---

### Task 9: 清理 — 删除临时脚本

- [ ] **Step 1: 删除临时脚本**

```bash
rm fix_truefalse.py
```

- [ ] **Step 2: 提交**

```bash
git add fix_truefalse.py  # 或 git rm
git commit -m "chore: 清理临时数据修正脚本"
```
