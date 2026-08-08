/* Task 7 CDP 功能验证:真实 Edge headless + DOM 点击驱动臻至版
   重点:启动数据自检输出 / 简答题做题路径(展示·提交·查看解析)·解析已润色
   覆盖:51 章节键 / 0 JS 错误 / 自检 console 输出 / short 全链路 / 解析≠答案 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html";
const PORT = 9337;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t7-'));

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

  let id=0; const pending=new Map(); const pageErrors=[]; const consoleLogs=[];
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}
    else if(m.method==='Runtime.exceptionThrown'){try{pageErrors.push(String(m.params.exceptionDetails.exception.description||m.params.exceptionDetails.text).slice(0,200));}catch(err){}}
    else if(m.method==='Runtime.consoleAPICalled'){
      try{
        const txt=m.params.args.map(a=>a.value||a.description||'').join(' ');
        if(m.params.type==='error')pageErrors.push('console.error: '+txt.slice(0,200));
        consoleLogs.push(m.params.type+': '+txt.slice(0,300));
      }catch(err){}
    }
  };
  function send(method,params){return new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error('页面JS异常: '+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text).slice(0,300));return r.result.value;}
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));

  await send('Runtime.enable',{});
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa'))break;}catch(e){}await sleep(300);}
  if(!(await ev('!!window.__qa')))throw new Error('页面未就绪');

  const results=[];
  function check(name,ok,detail){results.push({name,ok,detail});console.log((ok?'  OK  ':'  FAIL ')+name+(ok?'':' :: '+detail));}

  /* ---------- 0. 启动数据自检输出 ---------- */
  await sleep(1500); /* 等 setTimeout(runDataSelfCheck,0) 输出 */
  const selfCheckOk = consoleLogs.some(l=>l.includes('[数据自检] 正常'));
  const selfCheckLine = consoleLogs.find(l=>l.includes('[数据自检]'))||'<无输出>';
  check('启动数据自检: console 输出正常', selfCheckOk, selfCheckLine);

  /* ---------- 1. 51 章节键 ---------- */
  const qbKeys = await ev('window.__qa.qbKeys().length');
  check('QUESTION_BANKS 键数 = 51', qbKeys===51, '实际 '+qbKeys);

  /* ---------- 2. 进入题库 + 切到 biochem_30 ---------- */
  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await sleep(400);
  const chipCount = await ev(`(function(){var S=window.__qa.S;return JSON.stringify({view:S.view,chips:document.querySelectorAll('.chapter-chip').length});})()`);
  const cc=JSON.parse(chipCount);
  check('home 视图 + 章节 chips 存在', cc.view==='home'&&cc.chips>=35, chipCount);
  await ev(`(function(){var el=document.querySelector('[data-action="select-chapter"][data-key="biochem_30"]');if(el)el.click();return !!el;})()`);
  await sleep(300);
  const subj = await ev('window.__qa.S.subject');
  check('选中 biochem_30', subj==='biochem_30', subj);

  /* ---------- 3. 简答题做题路径 ---------- */
  await ev(`(function(){var el=document.querySelector('[data-action="start-short"]');if(el)el.click();return !!el;})()`);
  await sleep(500);

  async function shortRound(round){
    /* 展示阶段:应为 short 题 + "显示答案·自主评分"按钮 */
    const show = await ev(`(function(){
      var S=window.__qa.S,q=S.questions[S.qIndex];
      var btn=document.querySelector('[data-action="short-reveal"]');
      return JSON.stringify({type:q&&q.type,revealBtn:!!btn,ansArea:!!document.querySelector('.short-answer-reveal'),qText:(q&&q.question||'').slice(0,40)});
    })()`);
    const sh=JSON.parse(show);
    check('简答第'+round+'轮 展示: short 题+显示答案按钮', sh.type==='short'&&sh.revealBtn&&!sh.ansArea, show);

    /* 提交:点击 short-reveal */
    await ev(`(function(){var el=document.querySelector('[data-action="short-reveal"]');if(el)el.click();return !!el;})()`);
    await sleep(400);

    /* 验证参考答案区与解析区 */
    const rev = await ev(`(function(){
      var S=window.__qa.S,q=S.questions[S.qIndex];
      var ansEl=document.querySelector('.short-answer-text');
      var expEl=document.querySelector('.explanation');
      var ansTxt=ansEl?ansEl.textContent.trim():'';
      var expTxt=expEl?expEl.textContent.trim():'';
      var ansKey=S.subject+'__'+q.id;
      /* .explanation 内含 label('解析')+正文,取正文部分比较 */
      var expBody=expTxt.replace(/^解析\s*/,'');
      return JSON.stringify({answered:S.answers[ansKey],ansTxt:ansTxt,expTxt:expTxt,
        same:ansTxt===expBody,expLen:expBody.length,expHasPrefix:/^参考答案[:：]/.test(expBody),
        ansExpected:ansTxt===q.answer,expExpected:expBody===q.explanation});
    })()`);
    const rv=JSON.parse(rev);
    check('简答第'+round+'轮 提交: 状态 done', rv.answered==='done', rev);
    check('简答第'+round+'轮 参考答案区=答案', rv.ansExpected&&rv.ansTxt.length>0, rev);
    check('简答第'+round+'轮 解析区=explanation', rv.expExpected&&rv.expLen>0, rev);
    check('简答第'+round+'轮 解析≠答案(已润色)', !rv.same&&!rv.expHasPrefix, '解析长度 '+rv.expLen);
    /* 下一题 */
    const nxt = await ev(`(function(){var S=window.__qa.S;var before=S.qIndex;var el=document.querySelector('[data-action="nav-next"]');if(el)el.click();return JSON.stringify({before:before,after:S.qIndex});})()`);
    await sleep(400);
    return JSON.parse(nxt);
  }

  const n1 = await shortRound(1);
  check('简答第1轮 可切下一题', n1.after===n1.before+1, JSON.stringify(n1));
  const n2 = await shortRound(2);
  check('简答第2轮 继续下一题', n2.after===n2.before+1, JSON.stringify(n2));

  /* ---------- 4. 数据自检的润色一致性:HTML 内嵌解析与答案不同 ---------- */
  const noDup = await ev(`(function(){
    var b=window.__qa.getBank('biochem_30');
    var bad=[];
    for(var i=0;i<b.questions.length;i++){
      var q=b.questions[i];
      if(q.type!=='short')continue;
      var a=(q.answer||'').replace(/^参考答案[:：]?/,'').replace(/\\s+/g,'');
      var e=(q.explanation||'').replace(/^参考答案[:：]?/,'').replace(/\\s+/g,'');
      if(a===e||q.explanation.indexOf('参考答案')===0)bad.push(q.id);
    }
    return JSON.stringify({short:b.stats.short,bad:bad});
  })()`);
  const nd=JSON.parse(noDup);
  check('biochem_30 全量: 无解析复述答案', nd.short===14&&nd.bad.length===0, noDup);

  /* ---------- 5. 统计 ---------- */
  const summary = await ev(`(function(){
    var ks=window.__qa.qbKeys(),tq=0,tt=0;
    for(var i=0;i<ks.length;i++){var b=window.__qa.getBank(ks[i]);tq+=b.questions.length;tt+=b.terms.length;}
    return JSON.stringify({objs:ks.length,q:tq,terms:tt});
  })()`);
  const sm=JSON.parse(summary);
  check('全库汇总 51/5844/951', sm.objs===51&&sm.q===5844&&sm.terms===951, summary);

  /* ---------- 6. 0 JS 错误 ---------- */
  check('0 JS 错误 / console.error', pageErrors.length===0, pageErrors.join(' || ').slice(0,300));

  const failed = results.filter(r=>!r.ok);
  console.log('===== 汇总 =====');
  console.log('通过 '+results.length+'/'+results.length+' 项,'+(failed.length?'失败 '+failed.length+' 项':'全部通过'));
  try{ws.close();}catch(e){}
  edge.kill();
  process.exit(failed.length?1:0);
}
main().catch(e=>{console.error('测试异常:',e);process.exit(2);});
