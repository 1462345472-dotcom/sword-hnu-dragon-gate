# -*- coding: utf-8 -*-
"""Task 5: 章节索引预建 — 精确替换臻至版 HTML 中的 JS 逻辑(UI/CSS 零改动)。
每处替换断言唯一匹配;全部成功才写回。"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = '生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html'

with open(PATH, encoding='utf-8') as f:
    html = f.read()

REPLACEMENTS = []

# ---- 替换 1:getQ 使用 byId 索引(O(章内)→O(1),null 语义保持) ----
REPLACEMENTS.append((
    'function getQ(id){var qs=allQs();for(var i=0;i<qs.length;i++){if(qs[i].id===id)return qs[i];}return null;}',
    'function getQ(id){var c=qbIdx().chapters[S.subject];return c&&c.byId[id]!==undefined?c.byId[id]:null;}'
))

# ---- 替换 2:插入章节索引构建(懒构建一次,QUESTION_BANKS 不可变→无失效) ----
INDEX_CODE = (
    '/* ===== 章节索引(Task 5):QUESTION_BANKS 不可变 -> 懒构建一次,遍历/过滤 O(n)->O(章内) =====\n'
    '   qbIdx(): chapters[key] = {byId:{qid->题}, byType:{题型->题数组(原序)}, termsByChapter:{chapter->术语数组(原序)}}\n'
    '            qidFirst = {qid->第一个含该id的章节key(按QUESTION_BANKS属性序,复刻findBankForQ语义)} */\n'
    'var _QB_IDX=null;\n'
    'function qbIdx(){\n'
    '  if(_QB_IDX!==null)return _QB_IDX;\n'
    '  var idx={chapters:{},qidFirst:{}};\n'
    '  var ks=Object.keys(QUESTION_BANKS);\n'
    '  for(var bi=0;bi<ks.length;bi++){\n'
    '    var bk=QUESTION_BANKS[ks[bi]];\n'
    '    var ch={byId:{},byType:{choice:[],truefalse:[],multi:[],short:[]},termsByChapter:{}};\n'
    '    var qarr=bk.questions||[];\n'
    '    for(var qi=0;qi<qarr.length;qi++){\n'
    '      var q=qarr[qi];\n'
    '      ch.byId[q.id]=q;\n'
    '      if(ch.byType[q.type])ch.byType[q.type].push(q);else ch.byType[q.type]=[q];\n'
    '      if(idx.qidFirst[q.id]===undefined)idx.qidFirst[q.id]=ks[bi];\n'
    '    }\n'
    '    var tarr=bk.terms||[];\n'
    '    for(var ti=0;ti<tarr.length;ti++){\n'
    '      var tm=tarr[ti];var tc=tm.chapter;\n'
    '      if(!ch.termsByChapter[tc])ch.termsByChapter[tc]=[];\n'
    '      ch.termsByChapter[tc].push(tm);\n'
    '    }\n'
    '    idx.chapters[ks[bi]]=ch;\n'
    '  }\n'
    '  _QB_IDX=idx;return idx;\n'
    '}\n'
    'function chQsByType(k,ft){var c=qbIdx().chapters[k];return c?(c.byType[ft]||[]):[];}\n'
    'function chTermsBy(k,ch){var c=qbIdx().chapters[k];return c?(c.termsByChapter[ch]||[]):[];}\n'
)
REPLACEMENTS.append((
    '/* ===== 统计 ===== */',
    INDEX_CODE + '/* ===== 统计 ===== */'
))

# ---- 替换 3:wrongQs 章节剪枝(输出顺序与全量遍历一致) ----
OLD_WQ = (
    'function wrongQs(){\n'
    '  if(_wrongQsCache!==null)return _wrongQsCache;\n'
    '  var r=[],ks=Object.keys(QUESTION_BANKS);\n'
    '  for(var j=0;j<ks.length;j++){\n'
    '    var qs=QUESTION_BANKS[ks[j]].questions;\n'
    '    for(var i=0;i<qs.length;i++){if(S.wrongSet[ak(ks[j],qs[i].id)])r.push(qs[i]);}\n'
    '  }\n'
    '  _wrongQsCache=r;return r;\n'
    '}'
)
NEW_WQ = (
    'function wrongQs(){\n'
    '  if(_wrongQsCache!==null)return _wrongQsCache;\n'
    '  var r=[];\n'
    '  /* 章节剪枝(Task 5):只遍历 wrongSet 触及的章节(按属性序),输出顺序与全量遍历一致 */\n'
    '  var ks=Object.keys(QUESTION_BANKS);\n'
    '  var wks=Object.keys(S.wrongSet);\n'
    '  var touched=[];\n'
    '  for(var t=0;t<wks.length;t++){\n'
    '    var sep=wks[t].indexOf(\'__\');\n'
    '    if(sep<0)continue;\n'
    '    var subj=wks[t].substring(0,sep);\n'
    '    if(QUESTION_BANKS[subj]&&touched.indexOf(subj)<0)touched.push(subj);\n'
    '  }\n'
    '  for(var j=0;j<ks.length;j++){\n'
    '    if(touched.indexOf(ks[j])<0)continue;\n'
    '    var qs=QUESTION_BANKS[ks[j]].questions;\n'
    '    for(var i=0;i<qs.length;i++){if(S.wrongSet[ak(ks[j],qs[i].id)])r.push(qs[i]);}\n'
    '  }\n'
    '  _wrongQsCache=r;return r;\n'
    '}'
)
REPLACEMENTS.append((OLD_WQ, NEW_WQ))

# ---- 替换 4:bmQs 章节剪枝 ----
OLD_BM = (
    'function bmQs(){\n'
    '  if(_bmQsCache!==null)return _bmQsCache;\n'
    '  var r=[],ks=Object.keys(QUESTION_BANKS);\n'
    '  for(var j=0;j<ks.length;j++){\n'
    '    var qs=QUESTION_BANKS[ks[j]].questions;\n'
    '    for(var i=0;i<qs.length;i++){if(S.bookmarks[ak(ks[j],qs[i].id)])r.push(qs[i]);}\n'
    '  }\n'
    '  _bmQsCache=r;return r;\n'
    '}'
)
NEW_BM = (
    'function bmQs(){\n'
    '  if(_bmQsCache!==null)return _bmQsCache;\n'
    '  var r=[];\n'
    '  /* 章节剪枝(Task 5):只遍历 bookmarks 触及的章节(按属性序),输出顺序与全量遍历一致 */\n'
    '  var ks=Object.keys(QUESTION_BANKS);\n'
    '  var wks=Object.keys(S.bookmarks);\n'
    '  var touched=[];\n'
    '  for(var t=0;t<wks.length;t++){\n'
    '    var sep=wks[t].indexOf(\'__\');\n'
    '    if(sep<0)continue;\n'
    '    var subj=wks[t].substring(0,sep);\n'
    '    if(QUESTION_BANKS[subj]&&touched.indexOf(subj)<0)touched.push(subj);\n'
    '  }\n'
    '  for(var j=0;j<ks.length;j++){\n'
    '    if(touched.indexOf(ks[j])<0)continue;\n'
    '    var qs=QUESTION_BANKS[ks[j]].questions;\n'
    '    for(var i=0;i<qs.length;i++){if(S.bookmarks[ak(ks[j],qs[i].id)])r.push(qs[i]);}\n'
    '  }\n'
    '  _bmQsCache=r;return r;\n'
    '}'
)
REPLACEMENTS.append((OLD_BM, NEW_BM))

# ---- 替换 5:startQuiz 题型过滤用 byType 索引 ----
REPLACEMENTS.append((
    '  else if(mode===\'choice\'||mode===\'truefalse\'||mode===\'multi\'||mode===\'short\'){\n'
    '    var qs=allQs();var ft=mode;\n'
    '    S.questions=qs.filter(function(q){return q.type===ft;});\n'
    '  }',
    '  else if(mode===\'choice\'||mode===\'truefalse\'||mode===\'multi\'||mode===\'short\'){\n'
    '    S.questions=chQsByType(S.subject,mode);\n'
    '  }'
))

# ---- 替换 6:resumeSavedProgress 题型过滤 ----
OLD_RSP = (
    '    else if(mode===\'choice\')src=src.filter(function(q){return q.type===\'choice\';});\n'
    '    else if(mode===\'truefalse\')src=src.filter(function(q){return q.type===\'truefalse\';});\n'
    '    else if(mode===\'multi\')src=src.filter(function(q){return q.type===\'multi\';});\n'
    '    else if(mode===\'short\')src=src.filter(function(q){return q.type===\'short\';});'
)
NEW_RSP = (
    '    else if(mode===\'choice\')src=chQsByType(subjectKey,\'choice\');\n'
    '    else if(mode===\'truefalse\')src=chQsByType(subjectKey,\'truefalse\');\n'
    '    else if(mode===\'multi\')src=chQsByType(subjectKey,\'multi\');\n'
    '    else if(mode===\'short\')src=chQsByType(subjectKey,\'short\');'
)
REPLACEMENTS.append((OLD_RSP, NEW_RSP))

# ---- 替换 7:startChapterMode 题型过滤 ----
REPLACEMENTS.append((
    '  var filtered=b.questions.filter(function(q){return q.type===filterType;});',
    '  var filtered=chQsByType(subjectKey,filterType);'
))

# ---- 替换 8:renderTerms 过滤用 termsByChapter 索引 ----
REPLACEMENTS.append((
    '  var filtered=filter===\'all\'?at:at.filter(function(t){return t.chapter===filter;});',
    '  var filtered=filter===\'all\'?at:chTermsBy(S.subject,filter);'
))

# ---- 替换 9:findBankForQ 用 qidFirst 索引(O(5844)→O(1)) ----
OLD_FB = (
    'function findBankForQ(qid){\n'
    '  var ks=Object.keys(QUESTION_BANKS);\n'
    '  for(var i=0;i<ks.length;i++){\n'
    '    var bk=QUESTION_BANKS[ks[i]];\n'
    '    for(var j=0;j<bk.questions.length;j++){if(bk.questions[j].id===qid)return bk;}\n'
    '  }\n'
    '  return null;\n'
    '}'
)
NEW_FB = (
    'function findBankForQ(qid){\n'
    '  /* 索引(Task 5):qidFirst 按 QUESTION_BANKS 属性序记录首次出现,复刻原全量遍历语义 */\n'
    '  var k=qbIdx().qidFirst[qid];\n'
    '  return k?QUESTION_BANKS[k]:null;\n'
    '}'
)
REPLACEMENTS.append((OLD_FB, NEW_FB))

# ---- 执行替换(断言唯一) ----
for i, (old, new) in enumerate(REPLACEMENTS, 1):
    cnt = html.count(old)
    if cnt != 1:
        print(f'替换 {i} 失败:匹配 {cnt} 次(期望 1)')
        sys.exit(1)
    html = html.replace(old, new)
    print(f'替换 {i} OK')

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('全部替换完成,已写回')
