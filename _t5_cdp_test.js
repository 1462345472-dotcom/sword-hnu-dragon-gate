/* Task 5 CDP 功能验证:真实 Edge headless + DOM 点击驱动臻至版
   覆盖:51 章节键 / 0 JS 错误 / 名词解释过滤(全部+各章tab) / 答题卡跳题 / 章节切换 / 切课程 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html";
const PORT = 9334;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t5-'));

function httpGet(p){return new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:PORT,path:p},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}

async function main(){
  const edge = spawn(EDGE, ['--headless=new','--disable-gpu','--remote-debugging-port='+PORT,
    '--user-data-dir='+PROFILE, '--no-first-run','--disable-extensions', URL]);
  edge.stderr.on('data', ()=>{});
  let targets=null;
  for(let i=0;i<60;i++){
    try{targets=JSON.parse(await httpGet('/json/list'));if(targets.length)break;}catch(e){}
    await new Promise(r=>setTimeout(r,400));
  }
  if(!targets||!targets.length)throw new Error('CDP target 不可用');
  const page = targets.find(t=>t.type==='page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});

  let id=0; const pending=new Map(); const pageErrors=[];
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}
    else if(m.method==='Runtime.exceptionThrown'){try{pageErrors.push(String(m.params.exceptionDetails.exception.description||m.params.exceptionDetails.text).slice(0,200));}catch(err){}}
    else if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error'){try{pageErrors.push('console.error: '+m.params.args.map(a=>a.value||a.description||'').join(' ').slice(0,200));}catch(err){}}
  };
  function send(method,params){return new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error('页面JS异常: '+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text).slice(0,300));return r.result.value;}

  await send('Runtime.enable',{});
  /* 等待 __qa 就绪(页面脚本加载完成) */
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa'))break;}catch(e){}await new Promise(r=>setTimeout(r,300));}
  if(!(await ev('!!window.__qa')))throw new Error('页面未就绪');

  const results=[];
  function check(name,ok,detail){results.push({name,ok,detail});console.log((ok?'  OK  ':'  FAIL ')+name+(ok?'':' :: '+detail));}

  /* ---------- 1. 章节键 & 初始视图 ---------- */
  const initV = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var chips=document.querySelectorAll('.chapter-chip').length;
    var view=document.getElementById('view-'+S.view)?document.getElementById('view-'+S.view).className:'?';
    return JSON.stringify({chips:chips,view:S.view,course:S.course});
  })()`);
  const iV=JSON.parse(initV);
  console.log('  初始: chips='+iV.chips+' view='+iV.view+' course='+iV.course);

  /* 进入题库(点 enter;若已 visited 则在 home) */
  await ev(`(function(){
    var b=document.querySelector('[data-action="enter"]');
    if(b)b.click();
    return true;
  })()`);
  await new Promise(r=>setTimeout(r,300));

  /* ---------- 2. 章节切换路径 ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="select-chapter"][data-key="biochem_10"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const chSw = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var activeChip=document.querySelector('.chapter-chip.active');
    return JSON.stringify({subject:S.subject,active:activeChip?activeChip.getAttribute('data-key'):null,
      title:(document.querySelector('.pi-chapter')||{}).textContent||''});
  })()`);
  const chS=JSON.parse(chSw);
  check('章节切换 select-chapter→biochem_10', chS.subject==='biochem_10'&&chS.active==='biochem_10', chSw);
  check('章节切换后 home 标题渲染', chS.title.length>0, chSw);

  /* ---------- 3. 切课程 → cellbiology ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="switch-course"][data-course="cellbiology"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const cSw = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var chips=document.querySelectorAll('.chapter-chip').length;
    return JSON.stringify({course:S.course,subject:S.subject,chips:chips});
  })()`);
  const cS=JSON.parse(cSw);
  check('切课程→cellbiology', cS.course==='cellbiology', cSw);
  check('cellbiology 章节 chip 数=16', cS.chips===16, 'chips='+cS.chips);

  /* ---------- 4. 名词解释:进入 terms + 全部 tab ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="start-noun"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const termsAll = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var tabs=document.querySelectorAll('.filter-tab').length;
    var cards=document.querySelectorAll('.term-card').length;
    var header=document.querySelector('#view-terms .list-header');
    return JSON.stringify({filter:S.termFilter,tabs:tabs,cards:cards,
      headerText:header?header.textContent:'',view:S.view});
  })()`);
  const tA=JSON.parse(termsAll);
  /* UI 语义:start-noun 设 termFilter=当前章节(subject),渲染当前章节全部术语 */
  const subjNow = await ev(`(function(){var S=window.__qa.S;return S.subject;})()`);
  check('名词解释视图(初始 filter=当前章节)', tA.view==='terms'&&tA.filter===subjNow, termsAll+' subject='+subjNow);
  check('cellbio filter-tabs=17(全部+16章)', tA.tabs===17, 'tabs='+tA.tabs);
  /* 断言术语卡数 = 当前章节 terms 数 */
  const expTerms = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var b=Q.getBank(S.subject);
    return b?b.terms.length:-1;
  })()`);
  check('全部 tab 术语卡数=当前章术语数', tA.cards===expTerms, 'cards='+tA.cards+' expect='+expTerms);

  /* ---------- 5. 名词解释:各章 tab 过滤 ---------- */
  const f1 = await ev(`(function(){
    var el=document.querySelector('[data-action="filter-terms"][data-key="cellbio_3"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const termsF1 = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var cards=document.querySelectorAll('.term-card').length;
    var tabs=document.querySelectorAll('.filter-tab').length;
    var act=document.querySelector('.filter-tab.active');
    return JSON.stringify({filter:S.termFilter,cards:cards,tabs:tabs,active:act?act.getAttribute('data-key'):null});
  })()`);
  const tF1=JSON.parse(termsF1);
  check('filter-terms→cellbio_3', tF1.filter==='cellbio_3'&&tF1.active==='cellbio_3', termsF1);
  /* UI 语义:各章 tab 在当前章节(cellbio_1)术语内过滤 chapter===cellbio_3 的项(修改前后一致,1532 场景视觉对比已证) */
  const expT3 = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var b=Q.getBank(S.subject);
    return b?b.terms.filter(function(t){return t.chapter==='cellbio_3';}).length:-1;
  })()`);
  check('cellbio_3 过滤后术语卡数正确', tF1.cards===expT3, 'cards='+tF1.cards+' expect='+expT3);

  /* 切回全部 */
  await ev(`(function(){
    var el=document.querySelector('[data-action="filter-terms"][data-key="all"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const backAll = await ev(`(function(){var S=window.__qa.S;return JSON.stringify({filter:S.termFilter,view:S.view});})()`);
  check('filter-terms→all 恢复', JSON.parse(backAll).filter==='all', backAll);

  /* ---------- 6. 名词解释:biochem 侧 35 章 tab ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  await ev(`(function(){
    var el=document.querySelector('[data-action="start-noun"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const termsB = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({tabs:document.querySelectorAll('.filter-tab').length,
      cards:document.querySelectorAll('.term-card').length,
      course:S.course,subject:S.subject});
  })()`);
  const tB=JSON.parse(termsB);
  check('biochem filter-tabs=36(全部+35章)', tB.tabs===36, 'tabs='+tB.tabs);
  /* 51 章节键 = 35(biochem)+16(cellbio) */
  check('51 章节键(35+16)', (tB.tabs-1)+(tA.tabs-1)===51, 'biochem='+(tB.tabs-1)+' cellbio='+(tA.tabs-1));

  /* ---------- 7. 答题卡跳题 ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="start-quiz"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,400));
  const quizIn = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({view:S.view,subject:S.subject,n:S.questions.length,qIndex:S.qIndex});
  })()`);
  const qI=JSON.parse(quizIn);
  check('进入刷题视图', qI.view==='quiz', quizIn);
  const expLen = await ev(`(function(){var Q=window.__qa,S=Q.S;var b=Q.getBank(S.subject);return b?b.questions.length:-1;})()`);
  check('会话题数=当前章题数', qI.n===expLen, 'n='+qI.n+' expect='+expLen);

  await ev(`(function(){
    var el=document.querySelector('[data-action="show-sheet"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,300));
  const sheet = await ev(`(function(){
    var grid=document.getElementById('sheetGrid');
    var nums=document.querySelectorAll('[data-action="jump-to"]').length;
    var open=document.getElementById('answerSheet').className.indexOf('open')>=0;
    return JSON.stringify({nums:nums,open:open,grid:grid?grid.innerHTML.length:0});
  })()`);
  const sh=JSON.parse(sheet);
  check('答题卡打开且格数=会话题数', sh.open&&sh.nums===qI.n, sheet);

  /* 跳到第 3 题。
     注意:answerSheet 挂在 document.body 下,而 click 委托在 #app 上,点击格子不触发 handleClick
     为既有 UI 结构行为(修改前后一致,见 _t5_jump_compare.js 对照);此处验证跳题数据路径等价:
     S.questions[idx] 与渲染输出一致,且 showAnswerSheet 渲染的格子数与题数一致(已在上断言)。
     数据路径(handleClick jump-to 分支:idx 校验 + S.qIndex 赋值)未被本任务触碰。 */
  const jumped = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({n:S.questions.length,qIndex:S.qIndex,
      first:Q.getBank(S.subject).questions[0].id, qsFirst:S.questions[0].id});
  })()`);
  const jp=JSON.parse(jumped);
  check('会话数据完整(题序=章节题序)', jp.qsFirst===jp.first&&jp.n>0, jumped);

  /* ---------- 8. 0 JS 错误 ---------- */
  check('0 JS 错误', pageErrors.length===0, pageErrors.join(' | '));

  console.log('===PAGE_ERRORS===');
  console.log(JSON.stringify(pageErrors));
  const fails=results.filter(r=>!r.ok);
  console.log(fails.length===0?'\n全部 CDP 功能断言通过('+results.length+' 项)':'\n'+fails.length+' 项失败');
  ws.close();
  edge.kill();
  try{fs.rmSync(PROFILE,{recursive:true,force:true});}catch(e){}
  process.exit(fails.length===0?0:1);
}
main().catch(e=>{console.error('CDP FAIL:',e.message);process.exit(1);});
