# 取消收藏后书签题仍存在的根因修复报告

日期:2026-08-08
目标文件:`生物化学题库/湖南大学题库系统-臻至版.html`
备份:`生物化学题库/湖南大学题库系统-臻至版.html.bak_bmfix`

## 1. 复现现象

用户反馈:做题界面点收藏(星标)再取消,重新看"精选习题"(start-bookmarked/bmQs)时,那道题还在。

Edge headless CDP 实测(修复前):

```
Control A(同章模式):收藏 biochem_1_2__1 → 取消 → reload → bmQs 空          ✅ 正常
Repro B(跨章精选习题):
  收藏 biochem_1_2__1 + biochem_3__1 → 精选习题(S.subject=biochem_1_2)
  → 翻到第二题(biochem_3 的题 1)→ 点星标取消
  → 内存 keys:["biochem_3__1"]  ← 想删的 biochem_3__1 还在,
  → 反而误删了 biochem_1_2__1(另一道题的收藏!)
  → reload → bmQs 仍含 [1]                                                   ❌ BUG
```

结论:①同会话内取消后立即检查 —— 内存级删除命中错误键,真实键残留;②reload 后复活 —— 存储级:被取消章节的书签块从未被重写(脏标记打到了错误章节),旧块含该项 → loadState 重新合并进内存。二者是同一根因的两个表现。

## 2. 根因定位

分章存储本身(题面怀疑方向)没有问题:

- `persistFlagChunk`(L1364):**整块重建** —— 从内存 `setObj` 重新扫描该章节所有键重建块,空则 `removeItem`,并非与旧块合并;
- `loadState`(L1373):按块内容逐键合并进内存,块正确则加载正确;
- `saveState`(L1421):遍历脏章节块写回,失败保留脏标记重试,无吞写。

**真正的根因在键构造与跨章节模式的错位**:

1. `bmQs()` 精选习题列表是**跨章节**的(遍历全部 51 章的书签);
2. `start-bookmarked`(L2251)只把 `S.subject` 设为**第一道书签题**所在章节:`startQuizWithProgress(bmb.key,'bookmarked')`;
3. 用户在精选习题模式翻到**其它章节**的书签题并取消收藏时,`toggle-bookmark`(L2315)调用 `toggleBookmark(S.subject, cq.id)` 用**错误的章节前缀**构造键 `ak(subj,qId)=subj+'__'+qId`:
   - `delete` 命中的是 `S.subject+'__'+qid`(可能是另一道题的收藏,造成**误删**),真实键 `真实章节+'__'+qid` 纹丝不动;
   - `markDirty(_dirtyBm, subj)` 的脏标记同样打在错误章节 → 真实章节的书签块**从未被重写**,旧块残留 → reload 后 `loadState` 把该项加回 → "取消收藏后书签题仍然存在"。
4. 同根因连带:错题路径 `submitAnswer` 中 `ak(S.subject,qId)` 写入/移除 wrongSet,在精选错题/精选习题跨章模式下同样章节错位;`renderQuiz`/答题卡的星标显示 `isBookmarked(S.subject,q.id)` 同样错位(星标状态与实际数据不符)。

题目 id 跨章节重复(如每章都有 id=1)使问题更隐蔽:删除错误章节键时往往"恰好"删掉了另一道题的收藏。

## 3. 修复方案(最小改动,7 处)

让题目列表携带**真实所属章节**,书签/错题键操作一律用真实章节而非 `S.subject`:

1. `bmQs()`:push 时 `Object.assign({},qs[i])` 拷贝并附加 `_bmSubj=ks[j]`(不改题库原对象);
2. `wrongQs()`:同上(修错题路径同根因);
3. `toggle-bookmark` 处理器:`toggleBookmark(cq._bmSubj||S.subject,cq.id)`;
4. `renderQuiz` 星标:`isBookmarked(q._bmSubj||S.subject,q.id)`;
5. `showAnswerSheet` 答题卡星标:同上;
6. `submitAnswer` 答对移除错题:`var wsub=q._bmSubj||S.subject`,删除/脏标记用 `wsub`;
7. `submitAnswer` 答错加入错题:同上。

非跨章模式(普通章节刷题)下题目无 `_bmSubj`,回退 `S.subject`,行为与原来完全一致,零回归风险。

## 4. 验证数据

### 4.1 verify_chapter.py(数据完整性与指纹)

```
python verify_chapter.py --expect-objects 51 --expect-questions 5844 --expect-terms 951 --fingerprint 96e3aad4f8cf0d80
章节数: 51 | 题数: 5844 | 术语数: 951 | CSS指纹: 96e3aad4f8cf0d80
OK: 全部断言通过  (EXIT=0)
```

指纹 96e3aad4f8cf0d80 不变(仅 JS 逻辑改动,CSS 未动)。

### 4.2 Edge headless CDP 全路径回归(修复后)

```
S1 CORE: 精选习题跨章取消收藏 → reload → 无此题          PASS(核心 bug 已修复)
S1:      真实键从内存删除,其它收藏不受影响                PASS
S1:      localStorage bm_biochem_3 块已删除               PASS(存储级确认)
S2:      收藏 → reload → 精选习题仍含此题                 PASS(收藏持久化不回归)
S3:      同章普通模式取消 → reload → 无此题               PASS
S4:      跨章隔离:取消 B 章不影响 A 章书签                PASS
S5:      错题:答错入错题本 → 答对移除 → reload 后错题本空  PASS
S6:      做题/多选/名词/精选习题入口冒烟                  PASS
S7:      0 JS 异常 / 0 console error                      PASS
RESULT: ALL PASS
```

### 4.3 修复前后对比(同一复现流程)

| 检查点 | 修复前 | 修复后 |
|---|---|---|
| 取消收藏后内存真实键 | 残留 | 已删除 |
| 取消收藏后误删其它收藏 | 会(删到错键) | 不会 |
| reload 后精选习题含已取消题 | 是(BUG) | 否 |
| localStorage 块被正确重写/删除 | 否(旧块残留) | 是 |

## 5. 备注与边界

- `answers`(答题记录)在精选习题跨章模式下仍以 `S.subject` 为键,但读写一致、会话内自洽,且非本次用户报告范围,未改动(避免扩大风险面);
- 修复保持"非跨章回退 S.subject"语义,普通刷题路径与旧行为完全一致。
