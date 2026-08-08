/* Task 6 CDP 功能验证:真实 Edge headless + DOM 点击驱动臻至版
   重点:答题卡 jump-to 跳题实测(修复前无效 / 修复后必须可跳题)
   覆盖:51 章节键 / 0 JS 错误 / 答题卡跳题 / 做题 / 错题 / 书签 / 名词解释 / 切章 / 切课程 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html";
const PORT = 9336;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t6-'));

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
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa'))break;}catch(e){}await new Promise(r=>setTimeout(r,300));}
  if(!(await ev('!!window.__qa')))throw new Error('页面未就绪');

  const results=[];
  function check(name,ok,detail){results.push({name,ok,detail});console.log((ok?'  OK  ':'  FAIL ')+name+(ok?'':' :: '+detail));}

  /* ---------- 1. 进入题库(enter;若 visited 则在 home) ---------- */
  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await new Promise(r=>setTimeout(r,300));

  /* ---------- 2. 51 章节键:UI chip 统计(biochem 35 + cellbio 16) ---------- */
  await ev(`(function(){var el=document.querySelector('[data-action="switch-course"][data-course="cellbiology"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const cellChips = await ev(`(function(){var S=window.__qa.S;return JSON.stringify({course:S.course,chips:document.querySelectorAll('.chapter-chip').length});})()`);
  const cC=JSON.parse(cellChips);
  check('cellbiology 16 章节 chip', cC.course==='cellbiology'&&cC.chips===16, cellChips);
  await ev(`(function(){var el=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const bioChips = await ev(`(function(){var S=window.__qa.S;return JSON.stringify({course:S.course,chips:document.querySelectorAll('.chapter-chip').length});})()`);
  const bC=JSON.parse(bioChips);
  check('biochemistry 35 章节 chip', bC.course==='biochemistry'&&bC.chips===35, bioChips);
  check('51 章节键=35+16', bC.chips+cC.chips===51, 'bio='+bC.chips+' cell='+cC.chips);
  await ev(`(function(){var el=document.querySelector('[data-action="select-chapter"][data-key="biochem_1_2"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const hSubj = await ev(`(function(){var S=window.__qa.S;return S.subject;})()`);
  check('切章 select-chapter→biochem_1_2', hSubj==='biochem_1_2', hSubj);

  /* ---------- 4. 进入刷题 + 打开答题卡 ---------- */
  await ev(`(function(){var el=document.querySelector('[data-action="start-quiz"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,400));
  const quizIn = await ev(`(function(){var Q=window.__qa,S=Q.S;return JSON.stringify({view:S.view,subject:S.subject,n:S.questions.length,qIndex:S.qIndex});})()`);
  const qI=JSON.parse(quizIn);
  check('进入刷题视图', qI.view==='quiz'&&qI.n>0, quizIn);

  await ev(`(function(){var el=document.querySelector('[data-action="show-sheet"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const sheet = await ev(`(function(){
    var grid=document.getElementById('sheetGrid');
    var nums=document.querySelectorAll('[data-action="jump-to"]').length;
    var open=document.getElementById('answerSheet').className.indexOf('open')>=0;
    return JSON.stringify({nums:nums,open:open,grid:grid?grid.innerHTML.length:0});
  })()`);
  const sh=JSON.parse(sheet);
  check('答题卡打开且格数=会话题数', sh.open&&sh.nums===qI.n, sheet);

  /* ---------- 5. 答题卡 jump-to 实测(本任务核心修复点) ---------- */
  await ev(`(function(){
    var el=document.querySelector('[data-action="jump-to"][data-idx="4"]');
    if(el)el.click(); return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,400));
  const jumped = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var sheetEl=document.getElementById('answerSheet');
    var tag=document.querySelector('#view-quiz .q-tag-num');
    var qv=document.getElementById('view-quiz');
    return JSON.stringify({
      qIndex:S.qIndex,
      sheetOpen:sheetEl?sheetEl.className.indexOf('open')>=0:null,
      tag:tag?tag.textContent:'',
      curId:S.questions[S.qIndex]?S.questions[S.qIndex].id:null,
      expectId:S.questions[4]?S.questions[4].id:null,
      quizActive:qv?qv.className.indexOf('active')>=0:false
    });
  })()`);
  const jp=JSON.parse(jumped);
  check('jump-to 点击后 qIndex=4', jp.qIndex===4, 'qIndex='+jp.qIndex);
  check('jump-to 渲染第5题(题号标签)', jp.tag==='第5题', 'tag='+jp.tag);
  check('jump-to 后答题卡关闭', jp.sheetOpen===false, 'sheetOpen='+jp.sheetOpen);
  check('jump-to 当前题=questions[4]', jp.curId===jp.expectId, 'cur='+jp.curId+' expect='+jp.expectId);
  check('jump-to 后仍在 quiz 视图', jp.quizActive, JSON.stringify(jp));

  /* ---------- 6. 做题路径:答第 5 题 ---------- */
  await ev(`(function(){
    var q=window.__qa.S.questions[window.__qa.S.qIndex];
    var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
    if(q.type==='choice'||q.type==='truefalse'){
      var target=null;
      for(var i=0;i<opts.length;i++){if(opts[i].getAttribute('data-value')===String(q.answer)){target=opts[i];break;}}
      if(target){target.click();return 'clicked';}
    }else if(q.type==='multi'){
      var multi=document.querySelectorAll('#view-quiz [data-action="multi-toggle"]');
      if(multi.length){multi[0].click();
        var cb=document.querySelector('#view-quiz [data-action="multi-confirm"]');
        if(cb&&!cb.disabled){cb.click();return 'multi-confirm';}
      }
    }else if(q.type==='short'){
      var sb=document.querySelector('#view-quiz [data-action="short-reveal"]');
      if(sb){sb.click();return 'short-reveal';}
    }
    return 'none';
  })()`);
  await new Promise(r=>setTimeout(r,400));
  const ansNow = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var q=S.questions[S.qIndex];
    return JSON.stringify({answered:Q.isAnswered?Q.isAnswered(q.id):(S.answers[Q.ak(S.subject,q.id)]!==undefined),
      revealed:S.revealed[Q.ak(S.subject,q.id)]===true,
      wrongCount:Object.keys(S.wrongSet).length,
      streak:S.streak});
  })()`);
  const aN=JSON.parse(ansNow);
  check('做题后 answered=true', aN.answered===true, ansNow);
  check('做题后 revealed=true(解析显示)', aN.revealed===true, ansNow);

  /* ---------- 7. 书签路径 ---------- */
  await ev(`(function(){var el=document.querySelector('[data-action="toggle-bookmark"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const bmNow = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var q=S.questions[S.qIndex];
    var bm=S.bookmarks[Q.ak(S.subject,q.id)];
    var btn=document.querySelector('[data-action="toggle-bookmark"]');
    return JSON.stringify({bookmarked:!!bm,btnActive:btn?btn.className.indexOf('active')>=0:false});
  })()`);
  const bN=JSON.parse(bmNow);
  check('书签 toggle 后 bookmarks 记录', bN.bookmarked===true, bmNow);
  check('书签按钮 active 态', bN.btnActive===true, bmNow);

  /* ---------- 8. 错题路径:换未答题后故意答错 → 错题本 ---------- */
  await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var attempts=0;
    while(attempts<6){
      var q=S.questions[S.qIndex];
      var answered=S.answers[Q.ak(S.subject,q.id)]!==undefined;
      var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
      if(!answered&&opts.length>0){
        var wrongVal=null;
        if(q.type==='choice'){
          var keys=Object.keys(q.options);
          for(var i=0;i<keys.length;i++){if(String(keys[i])!==String(q.answer)){wrongVal=keys[i];break;}}
        }else if(q.type==='truefalse'){
          wrongVal=String(q.answer)==='true'?'false':'true';
        }
        if(wrongVal!==null){
          for(var i=0;i<opts.length;i++){if(opts[i].getAttribute('data-value')===String(wrongVal)){opts[i].click();return 'wrong-clicked';}}
        }
      }
      var nx=document.querySelector('[data-action="nav-next"]');
      if(nx){nx.click();}
      attempts++;
    }
    return 'exhausted';
  })()`);
  await new Promise(r=>setTimeout(r,400));
  const wrongNow = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var wqs=Q.wrongQs();
    return JSON.stringify({wrongCount:wqs.length,firstWrong:wqs[0]?wqs[0].id:null});
  })()`);
  const wN=JSON.parse(wrongNow);
  check('答错后错题集有记录', wN.wrongCount>=1, wrongNow);

  /* 错题本视图 */
  await ev(`(function(){var el=document.querySelector('[data-action="go-home"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const errNav = await ev(`(function(){
    var el=document.querySelector('[data-action="start-wrong"]');
    if(el)el.click();return !!el;
  })()`);
  await new Promise(r=>setTimeout(r,400));
  const errView = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({view:S.view,mode:S.quizMode,n:S.questions.length});
  })()`);
  const eV=JSON.parse(errView);
  check('错题精炼 start-wrong 进入 quiz', eV.view==='quiz'&&eV.mode==='wrong'&&eV.n>=1, errView);

  /* ---------- 9. 名词解释路径 ---------- */
  await ev(`(function(){var el=document.querySelector('[data-action="go-home"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  await ev(`(function(){var el=document.querySelector('[data-action="start-noun"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const terms = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var tabs=document.querySelectorAll('.filter-tab').length;
    var cards=document.querySelectorAll('.term-card').length;
    var b=Q.getBank(S.subject);
    return JSON.stringify({view:S.view,tabs:tabs,cards:cards,terms:b?b.terms.length:-1});
  })()`);
  const tN=JSON.parse(terms);
  check('名词解释视图(biochem tabs=36)', tN.view==='terms'&&tN.tabs===36, terms);
  check('名词解释卡数=当前章术语数', tN.cards===tN.terms, terms);
  await ev(`(function(){var el=document.querySelector('[data-action="filter-terms"][data-key="biochem_3"]');if(el)el.click();return !!el;})()`);
  await new Promise(r=>setTimeout(r,300));
  const termsF = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var cards=document.querySelectorAll('.term-card').length;
    var b=Q.getBank(S.subject);
    var exp=b?b.terms.filter(function(t){return t.chapter==='biochem_3';}).length:-1;
    return JSON.stringify({filter:S.termFilter,cards:cards,exp:exp});
  })()`);
  const tF=JSON.parse(termsF);
  check('filter-terms→biochem_3 过滤正确', tF.filter==='biochem_3'&&tF.cards===tF.exp, termsF);

  /* ---------- 10. 0 JS 错误 ---------- */
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
