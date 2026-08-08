# -*- coding: utf-8 -*-
"""Task 6 逻辑健壮性:对臻至版 HTML 的 <script> 块实施 9 项修改。
全部替换均在 JS 内,不触碰任何 <style> 内容(CSS 指纹不变)。
每项替换断言原文唯一出现,否则中止。"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = r'生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html'
html = open(PATH, encoding='utf-8', errors='ignore').read()
orig = html

EDITS = []  # (name, old, new)

# ============ 修改 1:getBank 防御 + 状态封装函数组 ============
EDITS.append((
    'getBank防御+状态封装',
    """function getBank(k){return QUESTION_BANKS[k];}""",
    """/* Task 6 健壮性:getBank 防御 —— 数据异常时返回 null,由调用方兜底提示(不改变正常路径行为) */
function getBank(k){try{return QUESTION_BANKS&&QUESTION_BANKS[k]||null;}catch(e){return null;}}
/* ===== 状态访问封装(Task 6):统一 answers/revealed/bookmarks 读写入口 =====
   行为与原散落调用完全一致,仅统一入口;批量快照(loadState/saveQuizProgress/resume 清理)保持整体对象操作 */
function getAnswer(subj,qId){return S.answers[ak(subj,qId)];}
function setAnswer(subj,qId,v){S.answers[ak(subj,qId)]=v;}
function delAnswer(subj,qId){delete S.answers[ak(subj,qId)];}
function isAnsweredBy(subj,qId){return S.answers[ak(subj,qId)]!==undefined;}
function getRevealed(subj,qId){return S.revealed[ak(subj,qId)]===true;}
function setRevealed(subj,qId,v){S.revealed[ak(subj,qId)]=v;}
function delRevealed(subj,qId){delete S.revealed[ak(subj,qId)];}
function isBookmarked(subj,qId){return !!S.bookmarks[ak(subj,qId)];}
function toggleBookmark(subj,qId){
  if(S.bookmarks[ak(subj,qId)]){delete S.bookmarks[ak(subj,qId)];}else{S.bookmarks[ak(subj,qId)]=true;}
  invalidateRuntimeCaches();markDirty(_dirtyBm,subj);saveState();
}"""
))

# ============ 修改 2:isAnswered/isRevealed 走封装 ============
EDITS.append((
    'isAnswered/isRevealed走封装',
    """function isAnswered(qId){return S.answers[ak(S.subject,qId)]!==undefined;}
function isRevealed(qId){return S.revealed[ak(S.subject,qId)]===true;}""",
    """function isAnswered(qId){return isAnsweredBy(S.subject,qId);}
function isRevealed(qId){return getRevealed(S.subject,qId);}"""
))

# ============ 修改 3:submitAnswer 写点走封装 ============
EDITS.append((
    'submitAnswer写点封装',
    """  S.answers[ak(S.subject,qId)]=ua;S.revealed[ak(S.subject,qId)]=true;""",
    """  setAnswer(S.subject,qId,ua);setRevealed(S.subject,qId,true);"""
))

# ============ 修改 4:handleClick toggle-bookmark 走封装 ============
EDITS.append((
    'handleClick toggle-bookmark封装',
    """    case'toggle-bookmark':
      var cq=curQ();if(!cq)return;
      if(S.bookmarks[ak(S.subject,cq.id)])delete S.bookmarks[ak(S.subject,cq.id)];else S.bookmarks[ak(S.subject,cq.id)]=true;
      invalidateRuntimeCaches();markDirty(_dirtyBm,S.subject);saveState();renderQuiz();
      break;""",
    """    case'toggle-bookmark':
      var cq=curQ();if(!cq)return;
      toggleBookmark(S.subject,cq.id);renderQuiz();
      break;"""
))

# ============ 修改 5:handleClick 末尾加 default 兜底 ============
EDITS.append((
    'handleClick default兜底',
    """        hideSettings();
      }
      break;
  }
}""",
    """        hideSettings();
      }
      break;
    default:
      /* Task 6 兜底:未知 data-action 静默忽略,防止新增 action 无处理时异常 */
      break;
  }
}"""
))

# ============ 修改 6:startQuizWithProgress 入口 getBank null toast ============
EDITS.append((
    'startQuizWithProgress getBank兜底',
    """function startQuizWithProgress(subjectKey,mode){
  S._pendingSubject=subjectKey;S._pendingMode=mode||'all';""",
    """function startQuizWithProgress(subjectKey,mode){
  if(!getBank(subjectKey)){toast('章节数据未找到,请返回首页重试');return;}
  S._pendingSubject=subjectKey;S._pendingMode=mode||'all';"""
))

# ============ 修改 7:init 数据完整性兜底(白屏→友好提示) ============
EDITS.append((
    'init数据兜底',
    """function init(){
  loadState();""",
    """/* Task 6 兜底:QUESTION_BANKS 数据缺失/异常时显示友好提示,而非白屏 */
function dataReady(){
  try{
    if(typeof QUESTION_BANKS!=='object'||!QUESTION_BANKS)return false;
    return Object.keys(QUESTION_BANKS).length>0;
  }catch(e){return false;}
}
function showDataError(){
  var d=document.createElement('div');
  d.style.cssText='position:fixed;inset:0;display:flex;align-items:center;justify-content:center;padding:24px;text-align:center;font-family:system-ui,sans-serif;color:#8B1A2A;background:#F9F6F0;z-index:99999;';
  d.innerHTML='<div><h3 style="margin:0 0 12px;font-size:18px">题库数据加载异常</h3><p style="margin:0;color:#555;font-size:14px;line-height:1.6">题目数据缺失或格式异常,无法正常使用。<br>请重新下载完整的题库页面文件后重试。</p></div>';
  document.body.appendChild(d);
}
function init(){
  if(!dataReady()){showDataError();return;}
  loadState();"""
))

# ============ 修改 8:answerSheet 独立事件监听(核心 jump-to 修复) ============
EDITS.append((
    'handleSheetClick定义',
    """function hideSettings(){
  var overlay=document.getElementById('sheetOverlay');
  if(overlay)overlay.classList.remove('open');
  var sheet=document.getElementById('answerSheet');
  if(sheet)sheet.classList.remove('open');
}""",
    """function hideSettings(){
  var overlay=document.getElementById('sheetOverlay');
  if(overlay)overlay.classList.remove('open');
  var sheet=document.getElementById('answerSheet');
  if(sheet)sheet.classList.remove('open');
}

/* Task 6 修复:答题卡独立事件委托 —— answerSheet 挂在 document.body 下(不在 #app 内),
   #app 上的 handleClick 委托收不到其点击,导致 jump-to 跳题失效;
   此处为 body 增加监听,但仅当点击目标位于 answerSheet 内时处理 jump-to,其余一律忽略,
   不影响 #app 委托与 overlay 的 hideAnswerSheet 监听。 */
function handleSheetClick(e){
  var sheet=document.getElementById('answerSheet');
  if(!sheet||!sheet.contains(e.target))return;
  var a=e.target.closest('[data-action]');
  if(!a)return;
  if(a.getAttribute('data-action')==='jump-to'){
    var idx=parseInt(a.getAttribute('data-idx'),10);
    if(!isNaN(idx)&&idx>=0&&idx<S.questions.length){
      S.qIndex=idx;renderQuiz();hideAnswerSheet();
      var qv=$('view-quiz');if(qv)qv.scrollTop=0;
    }
  }
}"""
))

EDITS.append((
    'body注册handleSheetClick',
    """  /* 事件委托 */
  app.addEventListener('click',handleClick);""",
    """  /* 事件委托 */
  app.addEventListener('click',handleClick);
  /* Task 6 修复:answerSheet 位于 body 下,补充 body 级监听处理答题卡内 jump-to(仅此动作) */
  document.body.addEventListener('click',handleSheetClick);"""
))

# ============ 修改 9:纯读点替换(行为不变,统一入口) ============
EDITS.append((
    'chStats读点',
    """    if(S.answers[ak(key,qs[i].id)]!==undefined)a++;
    var sq=qs[i];var sa=S.answers[ak(key,sq.id)];""",
    """    if(isAnsweredBy(key,qs[i].id))a++;
    var sq=qs[i];var sa=getAnswer(key,sq.id);"""
))
EDITS.append((
    'bmQs读点',
    """    for(var i=0;i<qs.length;i++){if(S.bookmarks[ak(ks[j],qs[i].id)])r.push(qs[i]);}""",
    """    for(var i=0;i<qs.length;i++){if(isBookmarked(ks[j],qs[i].id))r.push(qs[i]);}"""
))
EDITS.append((
    '_calcTotalCorrect读点',
    """    for(var k=0;k<qs.length;k++){var aq=qs[k];var aa=S.answers[ak(ks[j],aq.id)];""",
    """    for(var k=0;k<qs.length;k++){var aq=qs[k];var aa=getAnswer(ks[j],aq.id);"""
))
EDITS.append((
    'renderQuiz读点',
    """  var ua=S.answers[ak(S.subject,q.id)];
  var isCorrect;""",
    """  var ua=getAnswer(S.subject,q.id);
  var isCorrect;"""
))
EDITS.append((
    'renderQuiz书签读点',
    """  var isBM=S.bookmarks[ak(S.subject,q.id)];""",
    """  var isBM=isBookmarked(S.subject,q.id);"""
))
EDITS.append((
    'showAnswerSheet读点',
    """      var shA=S.answers[ak(S.subject,q.id)];var shCorrect;""",
    """      var shA=getAnswer(S.subject,q.id);var shCorrect;"""
))
EDITS.append((
    'showAnswerSheet书签读点',
    """    if(S.bookmarks[ak(S.subject,q.id)])cls+=' bookmarked';""",
    """    if(isBookmarked(S.subject,q.id))cls+=' bookmarked';"""
))
EDITS.append((
    'finishQuiz读点',
    """  for(var i=0;i<total;i++){var fq=qs[i];var fa=S.answers[ak(S.subject,fq.id)];""",
    """  for(var i=0;i<total;i++){var fq=qs[i];var fa=getAnswer(S.subject,fq.id);"""
))
EDITS.append((
    'renderResult读点1',
    """    var rq=qs[i];var ra=S.answers[ak(S.subject,rq.id)];""",
    """    var rq=qs[i];var ra=getAnswer(S.subject,rq.id);"""
))
EDITS.append((
    'renderResult读点2',
    """wrongQs.map(function(q){var ua=S.answers[ak(S.subject,q.id)];var ans=""",
    """wrongQs.map(function(q){var ua=getAnswer(S.subject,q.id);var ans="""
))

# ============ 执行替换,逐项断言唯一 ============
fails = []
for name, old, new in EDITS:
    cnt = html.count(old)
    if cnt != 1:
        fails.append(f'{name}: 出现 {cnt} 次(期望 1)')
        continue
    html = html.replace(old, new, 1)
    print(f'  OK  {name}')

if fails:
    print('中止,以下替换未唯一:')
    for f in fails:
        print('  FAIL', f)
    sys.exit(1)

open(PATH, 'w', encoding='utf-8', newline='').write(html)
print(f'\n写入完成:{len(EDITS)} 项替换,文件 {len(orig)} -> {len(html)} 字节')
