/* jump-to 行为对照:备份版(修改前) vs 新版,验证答题卡跳题在两种版本下行为一致 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const FILES = {
  before: "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/_臻至版_task5_backup.html",
  after:  "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html",
};
const PORT = 9335;

function httpGet(p){return new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:PORT,path:p},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}

async function runScenario(name, URL){
  const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t5j-'));
  const edge = spawn(EDGE, ['--headless=new','--disable-gpu','--remote-debugging-port='+PORT,
    '--user-data-dir='+PROFILE, '--no-first-run','--disable-extensions', URL]);
  edge.stderr.on('data',()=>{});
  let targets=null;
  for(let i=0;i<60;i++){
    try{targets=JSON.parse(await httpGet('/json/list'));if(targets.length)break;}catch(e){}
    await new Promise(r=>setTimeout(r,400));
  }
  if(!targets||!targets.length)throw new Error('no target');
  const page=targets.find(t=>t.type==='page');
  const ws=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let id=0;const pending=new Map();
  ws.onmessage=e=>{const m=JSON.parse(e.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}};
  function send(method,params){return new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});return r.result?r.result.value:null;}
  await send('Runtime.enable',{});
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa'))break;}catch(e){}await new Promise(r=>setTimeout(r,300));}
  const out = await ev(`(async function(){
    var Q=window.__qa,S=Q.S;
    var results={};
    /* 进入 biochem,选 biochem_5,开始刷题 */
    var enter=document.querySelector('[data-action="enter"]');if(enter)enter.click();
    await new Promise(r=>setTimeout(r,250));
    var chip=document.querySelector('[data-action="select-chapter"][data-key="biochem_5"]');
    if(chip)chip.click();
    await new Promise(r=>setTimeout(r,250));
    var sq=document.querySelector('[data-action="start-quiz"]');
    if(sq)sq.click();
    await new Promise(r=>setTimeout(r,400));
    results.q0={view:S.view,n:S.questions.length,qIndex:S.qIndex};
    /* 打开答题卡 */
    var ss=document.querySelector('[data-action="show-sheet"]');
    if(ss)ss.click();
    await new Promise(r=>setTimeout(r,250));
    var sheet=document.getElementById('answerSheet');
    results.sheetOpen = sheet?sheet.className.indexOf('open')>=0:false;
    results.sheetNums = document.querySelectorAll('#sheetGrid [data-action="jump-to"]').length;
    /* 点击第 3 格 */
    var g3=document.querySelectorAll('#sheetGrid [data-action="jump-to"]')[2];
    results.g3exists = !!g3;
    if(g3)g3.click();
    await new Promise(r=>setTimeout(r,350));
    results.after = {qIndex:S.qIndex, progress:(document.querySelector('.quiz-progress-num')||{}).textContent||''};
    /* 再试第 5 格 */
    var g5=document.querySelectorAll('#sheetGrid [data-action="jump-to"]')[4];
    if(g5)g5.click();
    await new Promise(r=>setTimeout(r,350));
    results.after5 = {qIndex:S.qIndex};
    return JSON.stringify(results);
  })()`);
  ws.close();edge.kill();
  try{fs.rmSync(PROFILE,{recursive:true,force:true});}catch(e){}
  console.log('['+name+'] '+out);
  return JSON.parse(out);
}

(async()=>{
  const b = await runScenario('before', FILES.before);
  const a = await runScenario('after', FILES.after);
  const same = JSON.stringify(b)===JSON.stringify(a);
  console.log('jump-to 行为一致(before==after): ' + same);
  if(!same){console.log('差异!before='+JSON.stringify(b)+' after='+JSON.stringify(a));process.exit(1);}
  process.exit(0);
})().catch(e=>{console.error('FAIL:',e.message);process.exit(1);});
