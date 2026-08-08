/* Task 7 自检异常分支验证:加载 stats 被损坏的临时 HTML,期望 console.warn + 界面提示条 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/_t7_broken.html";
const PORT = 9338;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t7b-'));

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
  const page = targets.find(t=>t.type==='page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let id=0; const pending=new Map(); const warns=[]; const errors=[];
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}
    else if(m.method==='Runtime.consoleAPICalled'){
      try{
        const txt=m.params.args.map(a=>a.value||a.description||'').join(' ');
        if(m.params.type==='warning')warns.push(txt);
        if(m.params.type==='error')errors.push(txt);
      }catch(err){}
    }
  };
  function send(method,params){return new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});return r.result&&r.result.value;}
  await send('Runtime.enable',{});
  /* 等页面就绪(临时文件暴露了 __qa.runSelfCheck 入口) */
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa&&typeof window.__qa.runSelfCheck==="function"'))break;}catch(e){}await new Promise(r=>setTimeout(r,300));}
  await ev('window.__qa.runSelfCheck()');
  await new Promise(r=>setTimeout(r,400));

  const warnLine = warns.find(w=>w.includes('[数据自检]'));
  const warnDetail = warns.find(w=>w.includes('stats.total'));
  const bannerText = await ev(`(function(){var els=document.querySelectorAll('[role="alert"]');for(var i=0;i<els.length;i++){if(els[i].innerHTML.indexOf('数据自检警告')>=0)return els[i].textContent;}return '';})()`);
  const hasIssues = warnLine&&warnLine.includes('异常');
  console.log((warnLine&&warnDetail?'  OK  ':'  FAIL ')+'console.warn 含 stats.total 异常', warnDetail||warnLine||'<无>');
  console.log((bannerText?'  OK  ':'  FAIL ')+'界面提示条出现', bannerText||'<无>');
  console.log((errors.length===0?'  OK  ':'  FAIL ')+'异常分支无 JS error', errors.join('||'));
  try{ws.close();}catch(e){}
  edge.kill();
  process.exit(hasIssues&&bannerText&&errors.length===0?0:1);
}
main().catch(e=>{console.error('异常:',e);process.exit(2);});
