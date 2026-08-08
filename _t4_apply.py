# -*- coding: utf-8 -*-
"""Task 4: 进度分章存储 —— 精确替换臻至版 HTML 的存储层 JS(UI 零改动)。
仅替换 JS 存储逻辑,不触碰任何 CSS/HTML 结构。替换前校验原文唯一存在。"""
import io, sys

PATH = r'生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html'

with io.open(PATH, encoding='utf-8') as f:
    html = f.read()

state = {'html': html}
def rep(old, new, tag):
    n = state['html'].count(old)
    if n != 1:
        print(f'[FAIL] {tag}: 原文匹配 {n} 次(需恰好 1 次), 中止')
        sys.exit(1)
    state['html'] = state['html'].replace(old, new)
    print(f'[OK] {tag}')

# ---- 1. 核心存储层:sk 保留,loadState/saveState 重写为分章存储 + 旧数据迁移 ----
rep(
"/* ===== localStorage ===== */\nfunction sk(k){return 'hnu_academy_'+k;}\nfunction loadState(){\n  try{var r=localStorage.getItem(sk('s'));if(r){var d=JSON.parse(r);\n  S.wrongSet=d.wrongSet||{};S.bookmarks=d.bookmarks||{};S.bestStreak=d.bestStreak||0;\n  S.achievements=d.achievements||{};\n  if(d.course)S.course=d.course;\n  if(d.subject)S.subject=d.subject;\n  if(d.termFilter)S.termFilter=d.termFilter;\n  }}catch(e){}\n  try{var p=localStorage.getItem(sk('progress'));if(p){S.savedProgress=JSON.parse(p);}}catch(e){}\n}\nfunction saveState(){\n  try{localStorage.setItem(sk('s'),JSON.stringify({\n    wrongSet:S.wrongSet,bookmarks:S.bookmarks,bestStreak:S.bestStreak,\n    achievements:S.achievements,\n    course:S.course,subject:S.subject,termFilter:S.termFilter\n  }));}catch(e){}\n  try{localStorage.setItem(sk('progress'),JSON.stringify(S.savedProgress));}catch(e){}\n}",
";/* ===== localStorage(Task 4 分章存储):答案进度/错题/书签按章节键分块\n   (hnu_academy_prog_{章} / wrong_{章} / bm_{章}),读时合并、写时只写变化章节;\n   旧单块格式(hnu_academy_s / hnu_academy_progress)读取时自动迁移,不丢已有进度。\n   对外接口 loadState()/saveState() 不变,内存数据模型不变,UI 零改动。 ===== */\nfunction sk(k){return 'hnu_academy_'+k;}\nvar _dirtyProg={},_dirtyWrong={},_dirtyBm={},_oldKeys=[];\nfunction markDirty(setObj,subj){if(subj)setObj[subj]=true;}\n/* 章节进度块:savedProgress 中 \"subject|mode\" → {mode:{qIndex,streak,timestamp,answers,revealed}} */\nfunction persistProgChunk(subj){\n  var out={},pre=subj+'|';\n  for(var pk in S.savedProgress){\n    if(pk.indexOf(pre)!==0)continue;\n    var s=S.savedProgress[pk];\n    out[pk.slice(pre.length)]={qIndex:s.qIndex||0,streak:s.streak||0,timestamp:s.timestamp,answers:s.answers||{},revealed:s.revealed||{}};\n  }\n  try{\n    if(Object.keys(out).length===0)localStorage.removeItem(sk('prog_'+subj));\n    else localStorage.setItem(sk('prog_'+subj),JSON.stringify(out));\n  }catch(e){}\n}\n/* 错题/书签章节块:全局 \"subj__qId\" → {qId:true} */\nfunction persistFlagChunk(setObj,prefix,subj){\n  var pre=subj+'__',out={};\n  for(var k in setObj){if(k.indexOf(pre)===0)out[k.slice(pre.length)]=true;}\n  try{\n    if(Object.keys(out).length===0)localStorage.removeItem(sk(prefix+subj));\n    else localStorage.setItem(sk(prefix+subj),JSON.stringify(out));\n  }catch(e){}\n}\nfunction loadState(){\n  /* 新格式:meta(小对象) + 分章块,逐键合并 */\n  try{var m=localStorage.getItem(sk('meta'));if(m){var d=JSON.parse(m);\n  S.bestStreak=d.bestStreak||0;S.achievements=d.achievements||{};\n  if(d.course)S.course=d.course;\n  if(d.subject)S.subject=d.subject;\n  if(d.termFilter)S.termFilter=d.termFilter;\n  }}catch(e){}\n  try{\n    for(var i=0;i<localStorage.length;i++){\n      var k=localStorage.key(i);if(!k)continue;\n      var v=localStorage.getItem(k);if(!v)continue;\n      if(k.indexOf(sk('prog_'))===0){\n        var subj=k.slice(sk('prog_').length),blk=JSON.parse(v);\n        for(var mode in blk){var b=blk[mode];\n          S.savedProgress[subj+'|'+mode]={qIndex:b.qIndex||0,answers:b.answers||{},revealed:b.revealed||{},streak:b.streak||0,timestamp:b.timestamp};\n        }\n      }else if(k.indexOf(sk('wrong_'))===0){\n        var wb=JSON.parse(v),wsub=k.slice(sk('wrong_').length);\n        for(var qid in wb)S.wrongSet[wsub+'__'+qid]=true;\n      }else if(k.indexOf(sk('bm_'))===0){\n        var bb=JSON.parse(v),bsub=k.slice(sk('bm_').length);\n        for(var qid2 in bb)S.bookmarks[bsub+'__'+qid2]=true;\n      }\n    }\n  }catch(e){}\n  /* 旧单块格式迁移:合并入内存 → 打标全量落盘新格式 → 由 saveState 删除旧键 */\n  try{var r=localStorage.getItem(sk('s'));if(r){var d=JSON.parse(r);\n  for(var k2 in (d.wrongSet||{}))S.wrongSet[k2]=true;\n  for(var k3 in (d.bookmarks||{}))S.bookmarks[k3]=true;\n  if(d.bestStreak>S.bestStreak)S.bestStreak=d.bestStreak;\n  for(var a in (d.achievements||{}))S.achievements[a]=true;\n  if(!S.course&&d.course)S.course=d.course;\n  if(!S.subject&&d.subject)S.subject=d.subject;\n  if(!S.termFilter&&d.termFilter)S.termFilter=d.termFilter;\n  _oldKeys.push(sk('s'));\n  }}catch(e){}\n  try{var p=localStorage.getItem(sk('progress'));if(p){var dp=JSON.parse(p);\n  for(var pk in dp)S.savedProgress[pk]=dp[pk];\n  _oldKeys.push(sk('progress'));\n  }}catch(e){}\n  if(_oldKeys.length){\n    for(var kb in S.savedProgress)markDirty(_dirtyProg,kb.split('|')[0]);\n    for(var kw in S.wrongSet)markDirty(_dirtyWrong,kw.indexOf('__')>0?kw.slice(0,kw.indexOf('__')):kw);\n    for(var kbm in S.bookmarks)markDirty(_dirtyBm,kbm.indexOf('__')>0?kbm.slice(0,kbm.indexOf('__')):kbm);\n    saveState();\n  }\n}\nfunction saveState(){\n  /* meta 小对象全量写;进度/错题/书签仅增量写变化章节 */\n  try{localStorage.setItem(sk('meta'),JSON.stringify({\n    bestStreak:S.bestStreak,achievements:S.achievements,\n    course:S.course,subject:S.subject,termFilter:S.termFilter\n  }));}catch(e){}\n  var k;\n  for(k in _dirtyProg)persistProgChunk(k);\n  for(k in _dirtyWrong)persistFlagChunk(S.wrongSet,'wrong_',k);\n  for(k in _dirtyBm)persistFlagChunk(S.bookmarks,'bm_',k);\n  _dirtyProg={};_dirtyWrong={};_dirtyBm={};\n  /* 新格式已落盘,删除旧单块键(幂等) */\n  if(_oldKeys.length){try{for(var i=0;i<_oldKeys.length;i++)localStorage.removeItem(_oldKeys[i]);}catch(e){}_oldKeys=[];}\n}",
'核心存储层(loadState/saveState)')

# ---- 2. clearSavedProgress:删 pk 后打标章节 ----
rep("function clearSavedProgress(){\n  var pk=progressKey(S._pendingSubject,S._pendingMode);\n  delete S.savedProgress[pk];saveState();\n}",
"function clearSavedProgress(){\n  var pk=progressKey(S._pendingSubject,S._pendingMode);\n  delete S.savedProgress[pk];markDirty(_dirtyProg,S._pendingSubject);saveState();\n}",
'clearSavedProgress')

# ---- 3. startFreshQuiz:删 pk 后打标章节 ----
rep("  var pk=progressKey(subjectKey,mode);\n  delete S.savedProgress[pk];saveState();\n  if(!startQuiz(subjectKey,mode))return;",
"  var pk=progressKey(subjectKey,mode);\n  delete S.savedProgress[pk];markDirty(_dirtyProg,subjectKey);saveState();\n  if(!startQuiz(subjectKey,mode))return;",
'startFreshQuiz')

# ---- 4. saveQuizProgress:保存快照后打标章节 ----
rep("  S.savedProgress[pk]={\n    qIndex:S.qIndex,\n    answers:S.answers,\n    revealed:S.revealed,\n    streak:S.streak,\n    timestamp:new Date().toISOString()\n  };\n  saveState();",
"  S.savedProgress[pk]={\n    qIndex:S.qIndex,\n    answers:S.answers,\n    revealed:S.revealed,\n    streak:S.streak,\n    timestamp:new Date().toISOString()\n  };\n  markDirty(_dirtyProg,S.subject);\n  saveState();",
'saveQuizProgress')

# ---- 5. submitAnswer:答错写 wrongSet 后打标章节 ----
rep("  else{S.streak=0;S.wrongSet[ak(S.subject,qId)]=true;invalidateRuntimeCaches();}",
"  else{S.streak=0;S.wrongSet[ak(S.subject,qId)]=true;invalidateRuntimeCaches();markDirty(_dirtyWrong,S.subject);}",
'submitAnswer wrongSet')

# ---- 6. finishQuiz:删 pk 后打标章节 ----
rep("  var pk=progressKey(S.subject,S.quizMode);\n  delete S.savedProgress[pk];\n  checkAchievements();saveState();",
"  var pk=progressKey(S.subject,S.quizMode);\n  delete S.savedProgress[pk];\n  markDirty(_dirtyProg,S.subject);\n  checkAchievements();saveState();",
'finishQuiz')

# ---- 7. toggle-bookmark:改 bookmarks 后打标章节 ----
rep("      if(S.bookmarks[ak(S.subject,cq.id)])delete S.bookmarks[ak(S.subject,cq.id)];else S.bookmarks[ak(S.subject,cq.id)]=true;\n      invalidateRuntimeCaches();saveState();renderQuiz();",
"      if(S.bookmarks[ak(S.subject,cq.id)])delete S.bookmarks[ak(S.subject,cq.id)];else S.bookmarks[ak(S.subject,cq.id)]=true;\n      invalidateRuntimeCaches();markDirty(_dirtyBm,S.subject);saveState();renderQuiz();",
'toggle-bookmark')

# ---- 8. clear-data:清除时删除全部分章块键 + 旧键,防残留回灌 ----
rep("      if(confirm('确定清除所有学习数据？此操作不可恢复。')){\n        S.wrongSet={};S.bookmarks={};S.bestStreak=0;S.achievements={};\n        invalidateRuntimeCaches();saveState();toast('数据已清除');",
"      if(confirm('确定清除所有学习数据？此操作不可恢复。')){\n        S.wrongSet={};S.bookmarks={};S.bestStreak=0;S.achievements={};\n        invalidateRuntimeCaches();\n        /* 分章存储:删除全部进度/错题/书签/元数据键(含旧格式,防残留下次加载回灌) */\n        try{var rm=[];for(var li=0;li<localStorage.length;li++){var lk=localStorage.key(li);if(lk&&(lk.indexOf(sk('prog_'))===0||lk.indexOf(sk('wrong_'))===0||lk.indexOf(sk('bm_'))===0||lk===sk('meta')||lk===sk('s')||lk===sk('progress')))rm.push(lk);}\n        for(var ri=0;ri<rm.length;ri++)localStorage.removeItem(rm[ri]);}catch(e){}\n        _dirtyProg={};_dirtyWrong={};_dirtyBm={};\n        saveState();toast('数据已清除');",
'clear-data')

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(state['html'])
print('全部替换完成,已写回')
