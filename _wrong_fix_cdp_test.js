/* 错题本"答对即移除"CDP 功能验证:真实 Edge headless + __qa 状态驱动 + 关键 DOM 真实路径
   覆盖:答错进错题本 / 答对即移除(普通模式)/ 错题重做模式答对移除 / 答错仍在 /
   跨章隔离(ak 命名空间)/ reload 持久化 / 缓存失效 / 常规路径回归 / 0 JS 错误 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html";
const PORT = 9344;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-wrong-'));
const LOGFILE = path.join(__dirname, '_wrong_fix_progress.log');
function log(msg){fs.appendFileSync(LOGFILE, new Date().toISOString()+' '+msg+'\n');console.log(msg);}
const watchdog=setTimeout(()=>{log('FATAL: 看门狗超时,强制退出');process.exit(2);},240000);

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
  ws.onclose=()=>{log('WS CLOSED');for(const p of pending.values())p.rej(new Error('WS closed'));pending.clear();};
  function send(method,params){return new Promise((res,rej)=>{
    const i=++id;const timer=setTimeout(()=>{pending.delete(i);rej(new Error('CDP send 超时('+method+')'));},15000);
    pending.set(i,{res:v=>{clearTimeout(timer);res(v);},rej:e=>{clearTimeout(timer);rej(e);}});
    try{ws.send(JSON.stringify({id:i,method,params}));}catch(e){clearTimeout(timer);pending.delete(i);rej(e);}
  });}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error('页面JS异常: '+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text).slice(0,300));return r.result.value;}
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  async function waitFor(expr,ms){for(let i=0;i<ms/200;i++){try{if(await ev(expr))return true;}catch(e){}await sleep(200);}return false;}

  await send('Runtime.enable',{});
  if(!(await waitFor('!!window.__qa',20000)))throw new Error('页面未就绪');

  const results=[];
  function check(name,ok,detail){results.push({name,ok,detail});log((ok?'  OK  ':'  FAIL ')+name+(ok?'':' :: '+detail));}

  /* 会话辅助:开新会话(全部刷题)并切到 quiz 视图 */
  const NEWQZ=(k)=>`(function(){var Q=window.__qa;Q.startQuiz('${k}','all');Q.switchView('quiz');return true;})()`;
  /* 直接提交(正确/错误)当前指定题 */
  const SUB=(k,idx,cmp)=>`(function(){var Q=window.__qa,S=Q.S;Q.startQuiz('${k}','all');Q.switchView('quiz');S.qIndex=${idx};var q=S.questions[${idx}];
    var val;if(${cmp}){val=q.answer;}else{val=(q.type==='truefalse')?(String(q.answer).toLowerCase()==='true'?'false':'true'):(Object.keys(q.options).find(function(kk){return String(kk)!==String(q.answer);}));}
    return Q.submitAnswer(q.id,val);})()`;

  log('== S0 进入题库 ==');
  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await sleep(300);

  log('== S1 答错进错题本(真实 DOM 路径) ==');
  const mk = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    Q.startQuiz('biochem_1_2','all');Q.switchView('quiz');
    var list=S.questions,idx=-1;
    for(var i=0;i<list.length;i++){if(list[i].type==='choice'||list[i].type==='truefalse'){idx=i;break;}}
    return JSON.stringify({idx:idx,total:list.length,qid:idx>=0?list[idx].id:null,type:idx>=0?list[idx].type:null});
  })()`);
  const mkP=JSON.parse(mk);
  if(mkP.idx<0)throw new Error('biochem_1_2 无 choice/truefalse 题');
  const TQID=mkP.qid;
  check('会话建立(目标题已定位)', mkP.total>0&&mkP.idx>=0, mk);

  /* 真实路径:答题卡 jump-to → 点击错误选项 */
  await ev(`(function(){var el=document.querySelector('[data-action="show-sheet"]');if(el)el.click();return !!el;})()`);
  await sleep(250);
  const jum = await ev(`(function(){var el=document.querySelector('[data-action="jump-to"][data-idx="${mkP.idx}"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  const wrongA = await ev(`(function(){
    var Q=window.__qa,S=Q.S,q=S.questions[S.qIndex];
    var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
    var wrongVal=null,keys=Object.keys(q.options||{});
    if(q.type==='truefalse'){wrongVal=String(q.answer).toLowerCase()==='true'?'false':'true';}
    else{for(var i=0;i<keys.length;i++){if(String(keys[i])!==String(q.answer)){wrongVal=keys[i];break;}}}
    var clicked=false;
    if(wrongVal!==null){for(var i=0;i<opts.length;i++){if(opts[i].getAttribute('data-value')===String(wrongVal)){opts[i].click();clicked=true;break;}}}
    return JSON.stringify({clicked:clicked,type:q.type,qid:q.id,answer:String(q.answer),wrongVal:String(wrongVal),opts:opts.length});
  })()`);
  const wA=JSON.parse(wrongA);
  check('jump-to 渲染目标题', jum===true, 'jum='+jum);
  check('答错选项已点击', wA.clicked===true, wrongA);
  await sleep(400);
  const afterWrong = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var cache=Q.wrongCache();
    var wqs=Q.wrongQs();
    return JSON.stringify({inSet:!!S.wrongSet[Q.ak(S.subject,'${TQID}')],wqsHas:wqs.some(function(q){return String(q.id)===String(${TQID});}),wc:Object.keys(S.wrongSet).length,cache:cache});
  })()`);
  const aW=JSON.parse(afterWrong);
  check('答错后该题进入 wrongSet', aW.inSet===true, afterWrong);
  check('答错后 wrongQs() 包含该题', aW.wqsHas===true, afterWrong);
  check('答错后错题总数=1', aW.wc===1, afterWrong);

  log('== S2 答对移除(普通刷题模式,真实 DOM 路径) ==');
  await ev(NEWQZ('biochem_1_2'));
  await sleep(200);
  await ev(`(function(){var el=document.querySelector('[data-action="show-sheet"]');if(el)el.click();return !!el;})()`);
  await sleep(250);
  await ev(`(function(){var el=document.querySelector('[data-action="jump-to"][data-idx="${mkP.idx}"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  const correctA = await ev(`(function(){
    var Q=window.__qa,S=Q.S,q=S.questions[S.qIndex];
    var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
    var clicked=false;
    for(var i=0;i<opts.length;i++){if(opts[i].getAttribute('data-value')===String(q.answer)){opts[i].click();clicked=true;break;}}
    return JSON.stringify({clicked:clicked,type:q.type,qid:q.id});
  })()`);
  const cA=JSON.parse(correctA);
  check('正确选项已点击', cA.clicked===true, correctA);
  await sleep(400);
  const afterCorrect = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var cache=Q.wrongCache();
    var wqs=Q.wrongQs();
    return JSON.stringify({inSet:!!S.wrongSet[Q.ak(S.subject,'${TQID}')],wqsHas:wqs.some(function(q){return String(q.id)===String(${TQID});}),wc:Object.keys(S.wrongSet).length,cache:cache});
  })()`);
  const aC=JSON.parse(afterCorrect);
  check('【核心】答对后 wrongSet 移除该题', aC.inSet===false, afterCorrect);
  check('【核心】答对后 wrongQs() 不含该题', aC.wqsHas===false, afterCorrect);
  check('【核心】答对后错题总数=0', aC.wc===0, afterCorrect);
  check('【核心】移除后 wrongQs 缓存已失效(null)', aC.cache===null, afterCorrect);

  log('== S3 答错仍在(不因答错被移除/重复答错不重复计数) ==');
  await ev(SUB('biochem_1_2',mkP.idx,false));
  await sleep(250);
  await ev(SUB('biochem_1_2',mkP.idx,false));
  await sleep(250);
  const stillWrong = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({inSet:!!S.wrongSet[Q.ak(S.subject,'${TQID}')],wc:Object.keys(S.wrongSet).length});
  })()`);
  const sW=JSON.parse(stillWrong);
  check('重复答错仍在错题本(不重复计数)', sW.inSet===true&&sW.wc===1, stillWrong);

  log('== S4 错题重做模式:答对移除 + 会话正常流转(真实 DOM 路径) ==');
  await ev(`(function(){var el=document.querySelector('[data-action="go-home"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  const wrongMode = await ev(`(function(){
    var el=document.querySelector('[data-action="start-wrong"]');
    if(!el)return 'no-btn';
    el.click();return 'clicked';
  })()`);
  await sleep(500);
  const wmState = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({view:S.view,mode:S.quizMode,subject:S.subject,n:S.questions.length,hasT:S.questions.some(function(q){return String(q.id)===String(${TQID});}),q0:S.questions[0]?S.questions[0].id:null});
  })()`);
  const wmS=JSON.parse(wmState);
  check('错题重做模式进入(wrong)', wrongMode==='clicked'&&wmS.mode==='wrong'&&wmS.n>=1, wmState);
  check('错题重做会话包含该错题', wmS.hasT===true, wmState);
  await ev(`(function(){
    var Q=window.__qa,S=Q.S,q=S.questions[S.qIndex];
    var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
    for(var i=0;i<opts.length;i++){if(opts[i].getAttribute('data-value')===String(q.answer)){opts[i].click();break;}}
    return JSON.stringify({qid:q.id,opts:opts.length});
  })()`);
  await sleep(400);
  const wmAfter = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({inSet:!!S.wrongSet[Q.ak(S.subject,'${TQID}')],wc:Object.keys(S.wrongSet).length,
      sessionStillHas:S.questions.some(function(q){return String(q.id)===String(${TQID});}),qIndex:S.qIndex,n:S.questions.length});
  })()`);
  const wmA=JSON.parse(wmAfter);
  check('【核心】错题重做答对后 wrongSet 移除', wmA.inSet===false&&wmA.wc===0, wmAfter);
  check('错题重做答对后当前会话快照仍含该题(正常流转)', wmA.sessionStillHas===true, wmAfter);
  /* 正常流转:nav-next 可用且可前进 */
  const navFlow = await ev(`(function(){var el=document.querySelector('[data-action="nav-next"]');if(!el)return 'no-btn';el.click();return 'clicked';})()`);
  await sleep(250);
  check('答对后 nav-next 正常流转', navFlow==='clicked', navFlow);
  /* 错题清空后:再开 wrong 模式无题可刷 */
  const wmEmpty = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    var ok=Q.startQuiz('biochem_1_2','wrong');
    return JSON.stringify({ok:ok,n:S.questions.length,wqs:Q.wrongQs().length});
  })()`);
  const wmE=JSON.parse(wmEmpty);
  check('错题清空后 wrong 模式无题可刷', wmE.ok===false&&wmE.n===0&&wmE.wqs===0, wmEmpty);

  log('== S5 跨章隔离 ==');
  /* 再造一道错题于 biochem_1_2 */
  await ev(SUB('biochem_1_2',mkP.idx,false));
  await sleep(250);
  /* biochem_3:找不同 qid 的第一道 choice/tf 题,答错 → 答对 */
  const cross = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    Q.startQuiz('biochem_3','all');Q.switchView('quiz');
    var tgt=-1;
    for(var i=0;i<S.questions.length;i++){if((S.questions[i].type==='choice'||S.questions[i].type==='truefalse')&&String(S.questions[i].id)!==String(${TQID})){tgt=i;break;}}
    if(tgt<0)return JSON.stringify({err:'no-target',n:S.questions.length});
    var q=S.questions[tgt];S.qIndex=tgt;
    var wrongVal=(q.type==='truefalse')?(String(q.answer).toLowerCase()==='true'?'false':'true'):(Object.keys(q.options).find(function(k){return String(k)!==String(q.answer);}));
    Q.submitAnswer(q.id,wrongVal);
    return JSON.stringify({ok:true,qid:q.id});
  })()`);
  const cros=JSON.parse(cross);
  check('biochem_3 造错题成功', cros.ok===true, cross);
  if(cros.ok){
    /* 在 biochem_3 答对它 → 仅移除 biochem_3 的条目 */
    const iso = await ev(`(function(){
      var Q=window.__qa,S=Q.S;
      var ch1Key=Q.ak('biochem_1_2','${TQID}');
      var ch3Key=Q.ak('biochem_3','${cros.qid}');
      var before={ch1:!!S.wrongSet[ch1Key],ch3:!!S.wrongSet[ch3Key]};
      Q.startQuiz('biochem_3','all');Q.switchView('quiz');
      var tgt=-1;for(var i=0;i<S.questions.length;i++){if(String(S.questions[i].id)===String(${cros.qid})){tgt=i;break;}}
      var submitted=false;
      if(tgt>=0){S.qIndex=tgt;var q=S.questions[tgt];submitted=Q.submitAnswer(q.id,q.answer);}
      return JSON.stringify({before:before,ch1After:!!S.wrongSet[ch1Key],ch3After:!!S.wrongSet[ch3Key],submitted:submitted});
    })()`);
    const isoP=JSON.parse(iso);
    check('答对前两章条目均存在', isoP.before.ch1===true&&isoP.before.ch3===true, iso);
    check('biochem_3 答对后仅其自身错题移除', isoP.ch3After===false, iso);
    check('跨章隔离:biochem_1_2 错题不受他章答对影响', isoP.ch1After===true, iso);
  }

  log('== S6 reload 持久化 ==');
  const beforeReload = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({ch1Wrong:!!S.wrongSet[Q.ak('biochem_1_2','${TQID}')],
      chunk:localStorage.getItem('hnu_academy_wrong_biochem_1_2')});
  })()`);
  const bR=JSON.parse(beforeReload);
  check('reload 前错题已落盘(chunk 存在)', bR.ch1Wrong===true&&bR.chunk!==null, beforeReload);
  await ev('location.reload();true');
  await sleep(1500);
  if(!(await waitFor('!!window.__qa',20000)))throw new Error('reload 后页面未就绪');
  const afterReload1 = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({ch1Wrong:!!S.wrongSet[Q.ak('biochem_1_2','${TQID}')],wc:Object.keys(S.wrongSet).length});
  })()`);
  const aR1=JSON.parse(afterReload1);
  check('reload 后错题仍在(持久化正常)', aR1.ch1Wrong===true&&aR1.wc>=1, afterReload1);
  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await sleep(300);
  await ev(`(function(){var Q=window.__qa,S=Q.S;Q.startQuiz('biochem_1_2','all');Q.switchView('quiz');
    var tgt=-1;for(var i=0;i<S.questions.length;i++){if(String(S.questions[i].id)===String(${TQID})){tgt=i;break;}}
    if(tgt<0)return 'not-found';
    S.qIndex=tgt;var q=S.questions[tgt];
    var opts=document.querySelectorAll('#view-quiz [data-action="answer"]');
    for(var j=0;j<opts.length;j++){if(opts[j].getAttribute('data-value')===String(q.answer)){opts[j].click();break;}}
    return 'clicked';})()`);
  await sleep(400);
  await ev('location.reload();true');
  await sleep(1500);
  if(!(await waitFor('!!window.__qa',20000)))throw new Error('reload2 后页面未就绪');
  const afterReload2 = await ev(`(function(){
    var Q=window.__qa,S=Q.S;
    return JSON.stringify({inSet:!!S.wrongSet[Q.ak('biochem_1_2','${TQID}')],
      wc:Object.keys(S.wrongSet).length,
      chunk:localStorage.getItem('hnu_academy_wrong_biochem_1_2'),
      chunkHas:(function(){try{var v=localStorage.getItem('hnu_academy_wrong_biochem_1_2');if(!v)return false;return JSON.parse(v)[String(${TQID})]===true;}catch(e){return 'err';}})()});
  })()`);
  const aR2=JSON.parse(afterReload2);
  check('【核心】答对移除后 reload 状态保持(不在错题本)', aR2.inSet===false&&aR2.wc===0, afterReload2);
  check('移除后 localStorage 分章块不再含该题', aR2.chunkHas===false, afterReload2);

  log('== S7 常规路径回归 ==');
  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await sleep(300);
  /* 多选专项(真实 DOM 路径,无存档 → 无续练弹窗) */
  const multi = await ev(`(function(){var el=document.querySelector('[data-action="start-multi"]');if(el)el.click();return !!el;})()`);
  await sleep(400);
  const mState = await ev(`(function(){var Q=window.__qa,S=Q.S;
    var toggles=document.querySelectorAll('#view-quiz [data-action="multi-toggle"]');
    return JSON.stringify({mode:S.quizMode,toggles:toggles.length,hasConfirm:!!document.querySelector('#view-quiz [data-action="multi-confirm"]')});
  })()`);
  const mS=JSON.parse(mState);
  check('多选专项进入', multi===true&&mS.mode==='multi'&&mS.toggles>=2&&mS.hasConfirm, mState);
  await ev(`(function(){var el=document.querySelector('#view-quiz [data-action="multi-toggle"]');if(el)el.click();var cb=document.querySelector('#view-quiz [data-action="multi-confirm"]');if(cb&&!cb.disabled)cb.click();return true;})()`);
  await sleep(400);
  const multiDone = await ev(`(function(){var Q=window.__qa,S=Q.S,q=S.questions[S.qIndex];
    return JSON.stringify({answered:S.answers[Q.ak(S.subject,q.id)]!==undefined});})()`);
  check('多选作答落库', JSON.parse(multiDone).answered===true, multiDone);
  /* 名词解释 */
  await ev(`(function(){var el=document.querySelector('[data-action="go-home"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  await ev(`(function(){var el=document.querySelector('[data-action="start-noun"]');if(el)el.click();return !!el;})()`);
  await sleep(400);
  const noun = await ev(`(function(){var Q=window.__qa,S=Q.S;
    return JSON.stringify({view:S.view,cards:document.querySelectorAll('.term-card').length,tabs:document.querySelectorAll('.filter-tab').length});
  })()`);
  const nS=JSON.parse(noun);
  check('名词解释路径正常', nS.view==='terms'&&nS.cards>0&&nS.tabs>0, noun);
  /* 书签(API 开会话避免续练弹窗) */
  await ev(`(function(){var el=document.querySelector('[data-action="go-home"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  await ev(`(function(){var Q=window.__qa;Q.startQuiz('biochem_1_2','all');Q.switchView('quiz');return true;})()`);
  await sleep(300);
  await ev(`(function(){var el=document.querySelector('[data-action="toggle-bookmark"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  const bm = await ev(`(function(){var Q=window.__qa,S=Q.S;
    var q=S.questions[S.qIndex];var key=Q.ak(S.subject,q.id);
    var btn=document.querySelector('[data-action="toggle-bookmark"]');
    return JSON.stringify({bm:!!S.bookmarks[key],btn:btn?btn.className.indexOf('active')>=0:false});
  })()`);
  const bmP=JSON.parse(bm);
  check('书签 toggle 正常', bmP.bm===true&&bmP.btn===true, bm);

  log('== S8 0 JS 错误 ==');
  check('0 JS 错误 / 0 console error', pageErrors.length===0, pageErrors.join(' | '));

  log('===PAGE_ERRORS===');
  log(JSON.stringify(pageErrors));
  const fails=results.filter(r=>!r.ok);
  log(fails.length===0?'\n全部 CDP 功能断言通过('+results.length+' 项)':'\n'+fails.length+' 项失败');
  clearTimeout(watchdog);
  ws.close();
  edge.kill();
  try{fs.rmSync(PROFILE,{recursive:true,force:true});}catch(e){}
  process.exit(fails.length===0?0:1);
}
main().catch(e=>{log('CDP FAIL:'+e.message);clearTimeout(watchdog);process.exit(1);});
