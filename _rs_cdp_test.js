/* 结果页累计统计(今日/累计) — Edge headless CDP 实测 v2
   覆盖:做题累计(对错混合)→结果页展示;第二轮累加;跨天归零(旧键忽略);
   清除数据归零;全路径回归(做题/多选/名词/错题/书签/导出导入);0 JS 错误 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9358;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'rsedge2-'));

let exceptions = [];
let consoleErrs = [];
let failed = false;
const fail = (m) => { failed = true; console.log('FAIL: ' + m); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const trunc = (s, n) => { s = String(s); return s.length > n ? s.substring(0, n) + '…(' + s.length + ')' : s; };

function getJson(url) {
  return new Promise((res, rej) => {
    http.get(url, (r) => { let d = ''; r.on('data', (c) => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej);
  });
}

async function main() {
  const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile, URL], { stdio: 'ignore' });
  let targets = null;
  for (let i = 0; i < 60; i++) {
    try { targets = await getJson('http://127.0.0.1:' + PORT + '/json'); if (targets && targets.length) break; } catch (e) {}
    await sleep(500);
  }
  if (!targets) { fail('CDP port not reachable'); process.exit(1); }
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => {
    const id = nextId++; const t = setTimeout(() => { pending.delete(id); res({ error: { message: 'CDP send timeout: ' + method } }); }, 20000);
    pending.set(id, (m) => { clearTimeout(t); res(m); });
    try { ws.send(JSON.stringify({ id, method, params })); } catch (e) { clearTimeout(t); pending.delete(id); res({ error: { message: 'ws send failed: ' + e.message } }); }
  });
  ws.onerror = (e) => { console.log('WS ERROR: ' + (e.message || 'unknown')); };
  ws.onclose = () => { console.log('WS CLOSED'); };
  ws.onmessage = (ev2) => {
    const m = JSON.parse(ev2.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      exceptions.push((d.exception && d.exception.description) || d.text || 'exception');
    } else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
      consoleErrs.push(m.params.args.map((a) => a.value || a.description || '').join(' '));
    }
  };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable'); await send('Page.enable');

  let ready = false;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await send('Runtime.evaluate', { expression: 'window.__qa?1:0', returnByValue: true });
      if (r.result && r.result.result && r.result.result.value === 1) { ready = true; break; }
    } catch (e) {}
    await sleep(500);
  }
  if (!ready) { fail('page did not load __qa'); process.exit(1); }
  console.log('page loaded, __qa ready');

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.error) throw new Error('CDP: ' + (r.error.message || 'error'));
    if (r.result && r.result.exceptionDetails) throw new Error((r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description) || r.result.exceptionDetails.text);
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  const step = async (name, expr, expect) => {
    let v;
    try { v = await ev(expr); } catch (e) { fail('[' + name + '] exception: ' + e.message); return; }
    const ok = expect(v);
    console.log((ok ? 'PASS' : 'FAIL') + ' [' + name + '] ' + trunc(v, 220));
    if (!ok) failed = true;
  };
  const assertEq = (name, got, want) => step(name, `(${got})`, (v) => v === want);

  const DAILY_KEY = `(function(){var d=new Date(),m=d.getMonth()+1,y=d.getFullYear(),day=d.getDate();return 'hnu_academy_daily_'+y+'-'+(m<10?'0'+m:m)+'-'+(day<10?'0'+day:day);})()`;

  /* ============ 0. 环境:confirm 放行 + 清空统计键(全新起点) ============ */
  await step('0.1 清理统计键+confirm放行',
    `(function(){window.confirm=function(){return true;};
      var rm=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k==='hnu_academy_total'||k.indexOf('hnu_academy_daily_')===0)rm.push(k);}
      for(var j=0;j<rm.length;j++)localStorage.removeItem(rm[j]);
      var n=0;for(var x=0;x<localStorage.length;x++){var k2=localStorage.key(x);if(k2==='hnu_academy_total'||k2.indexOf('hnu_academy_daily_')===0)n++;}
      return n;})()`, (v) => v === 0);
  await step('0.2 进入首页', `(function(){if(__qa.S.view==='home')return 'home';
    var b=document.querySelector('[data-action=enter]');if(b)b.click();return __qa.S.view;})()`, (v) => v === 'home');
  await sleep(200);

  /* ============ A. 第一轮:2 题(1 对 1 错)→ 结果页 ============ */
  await step('A1 startQuiz biochem_1_2(all)', `(function(){var ok=__qa.startQuiz('biochem_1_2','all');return JSON.stringify({ok:ok,n:__qa.S.questions.length});})()`,
    (v) => { const o = JSON.parse(v); return o.ok === true && o.n > 0; });
  await step('A2 第1题答对(返回true=答对)',
    `(function(){var q=__qa.S.questions[0];var r=__qa.submitAnswer(q.id,q.answer);return JSON.stringify({r:r,type:q.type});})()`,
    (v) => { const o = JSON.parse(v); return o.r === true; });
  await step('A3 第2题答错(返回false=答错,预期)',
    `(function(){var q=__qa.S.questions[1];var ua='';if(q.type==='short')ua='skip';else if(q.type==='truefalse')ua=String(q.answer).toLowerCase()==='true'?'false':'true';else{var ks=Object.keys(q.options);for(var i=0;i<ks.length;i++){if(String(ks[i]).toLowerCase()!==String(q.answer).toLowerCase()){ua=ks[i];break;}}}
      var r=__qa.submitAnswer(q.id,ua);return JSON.stringify({r:r,type:q.type,ua:ua,answer:q.answer});})()`,
    (v) => { const o = JSON.parse(v); return o.r === false; });
  await step('A4 切到结果页', `(function(){__qa.switchView('result');return __qa.S.view;})()`, (v) => v === 'result');
  await sleep(150);
  await step('A5 结果页显示 今日2/答对1 + 累计2/50%',
    `(function(){var t=document.querySelector('#view-result .result-view');return t?t.innerText:'';})()`,
    (v) => v.indexOf('今日已练 2 题') >= 0 && v.indexOf('答对 1 题') >= 0 &&
           v.indexOf('累计已练 2 题') >= 0 && v.indexOf('累计正确率 50%') >= 0);
  await step('A6 localStorage 累计={2,1} 今日={2,1}',
    `(function(){var t=JSON.parse(localStorage.getItem('hnu_academy_total'));var d=JSON.parse(localStorage.getItem(${DAILY_KEY}));
      return JSON.stringify({t:JSON.stringify(t),d:JSON.stringify(d)});})()`,
    (v) => v === '{"t":"{\\"totalCount\\":2,\\"totalCorrect\\":1}","d":"{\\"totalCount\\":2,\\"totalCorrect\\":1}"}');

  /* ============ B. 第二轮:3 题 → 累加(调试每题对错) ============ */
  await step('B1 startQuiz 第二轮', `(function(){var ok=__qa.startQuiz('biochem_1_2','all');return JSON.stringify({ok:ok,n:__qa.S.questions.length});})()`,
    (v) => { const o = JSON.parse(v); return o.ok === true && o.n > 0; });
  await step('B2 三题提交明细(提交前推进 qIndex,模拟真实逐题作答)',
    `(function(){var qs=__qa.S.questions;var res=[];
      for(var i=0;i<3;i++){__qa.S.qIndex=i;var q=qs[i];var r=__qa.submitAnswer(q.id,q.answer);
        res.push({i:i,id:q.id,type:q.type,answer:q.answer,r:r});}
      return JSON.stringify(res);})()`,
    (v) => { const o = JSON.parse(v); return o.length === 3 && o[0].r === true && o[1].r === true && o[2].r === true; });
  await step('B3 切到结果页', `(function(){__qa.switchView('result');return __qa.S.view;})()`, (v) => v === 'result');
  await sleep(150);
  await step('B4 结果页显示 今日5/答对4 + 累计5/80%',
    `(function(){var t=document.querySelector('#view-result .result-view');return t?t.innerText:'';})()`,
    (v) => v.indexOf('今日已练 5 题') >= 0 && v.indexOf('答对 4 题') >= 0 &&
           v.indexOf('累计已练 5 题') >= 0 && v.indexOf('累计正确率 80%') >= 0);
  await step('B5 localStorage 累计={5,4}',
    `(function(){return localStorage.getItem('hnu_academy_total');})()`, (v) => v === '{"totalCount":5,"totalCorrect":4}');

  /* ============ C. 跨天逻辑:旧日期键被忽略,今日从 0 重计,累计保留 ============ */
  await step('C1 注入旧天数据 2000-01-01={99,50}',
    `(function(){localStorage.setItem('hnu_academy_daily_2000-01-01',JSON.stringify({totalCount:99,totalCorrect:50}));return localStorage.getItem('hnu_academy_daily_2000-01-01');})()`,
    (v) => v === '{"totalCount":99,"totalCorrect":50}');
  await step('C2 今日键≠2000-01-01 且格式 YYYY-MM-DD', DAILY_KEY, (v) => v !== 'hnu_academy_daily_2000-01-01' && /^hnu_academy_daily_20\d\d-\d\d-\d\d$/.test(v));
  await send('Page.reload', { ignoreCache: true });
  ready = false;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await send('Runtime.evaluate', { expression: 'window.__qa?1:0', returnByValue: true });
      if (r.result && r.result.result && r.result.result.value === 1) { ready = true; break; }
    } catch (e) {}
    await sleep(500);
  }
  if (!ready) { fail('reload: __qa not ready'); process.exit(1); }
  await sleep(300);
  await step('C3 刷新后:同日数据保留(2026-08-08键={5,4}),旧天2000-01-01键完全隔离不参与累计',
    `(function(){var d=new Date();var ds='hnu_academy_daily_'+d.getFullYear()+'-'+((d.getMonth()+1)<10?'0'+(d.getMonth()+1):(d.getMonth()+1))+'-'+(d.getDate()<10?'0'+d.getDate():d.getDate());
      var today=JSON.parse(localStorage.getItem(ds))||{totalCount:0,totalCorrect:0};
      var total=JSON.parse(localStorage.getItem('hnu_academy_total'));
      var old=JSON.parse(localStorage.getItem('hnu_academy_daily_2000-01-01'));
      return JSON.stringify({today:JSON.stringify(today),total:JSON.stringify(total),old:JSON.stringify(old)});})()`,
    (v) => v === '{"today":"{\\"totalCount\\":5,\\"totalCorrect\\":4}","total":"{\\"totalCount\\":5,\\"totalCorrect\\":4}","old":"{\\"totalCount\\":99,\\"totalCorrect\\":50}"}');

  /* ============ D. 清除数据:统计键删除 + 结果页归零 ============ */
  await step('D1 clear-data 触发(reload 后重新覆写 confirm 放行)',
    `(function(){window.confirm=function(){return true;};
      var btn=document.createElement('button');btn.setAttribute('data-action','clear-data');
      document.getElementById('app').appendChild(btn);btn.click();btn.remove();return __qa.S.view;})()`, (v) => v === 'home');
  await sleep(200);
  await step('D2 统计键已删除(累计键+真实当天键均 null)',
    `(function(){var d=new Date();var ds='hnu_academy_daily_'+d.getFullYear()+'-'+((d.getMonth()+1)<10?'0'+(d.getMonth()+1):(d.getMonth()+1))+'-'+(d.getDate()<10?'0'+d.getDate():d.getDate());
      return JSON.stringify({t:localStorage.getItem('hnu_academy_total'),d:localStorage.getItem(ds)});})()`,
    (v) => v === '{"t":null,"d":null}');
  await step('D3 清除后结果页显示 今日0/累计0/0%',
    `(function(){__qa.switchView('result');var t=document.querySelector('#view-result .result-view');return t?t.innerText:'';})()`,
    (v) => v.indexOf('今日已练 0 题') >= 0 && v.indexOf('累计已练 0 题') >= 0 && v.indexOf('累计正确率 0%') >= 0);

  /* ============ E. 全路径回归(做题/多选/名词/错题/书签/导出导入) ============ */
  await step('E1 返回首页', `(function(){__qa.switchView('home');return __qa.S.view;})()`, (v) => v === 'home');
  await sleep(150);
  await step('E2 单选+判断路径', `(function(){__qa.startQuiz('biochem_1_2','all');
    var q=__qa.S.questions[0];var r1=__qa.submitAnswer(q.id,q.answer);return JSON.stringify({r1:r1});})()`,
    (v) => { const o = JSON.parse(v); return o.r1 === true; });
  await step('E3 书签 toggle(先切 quiz 视图渲染按钮)', `(function(){__qa.switchView('quiz');
    var b=document.querySelector('[data-action=toggle-bookmark]');if(b)b.click();
    return Object.keys(__qa.S.bookmarks).length;})()`, (v) => v >= 1);
  await step('E4 多选 toggle+confirm',
    `(function(){__qa.switchView('home');document.querySelector('[data-action=start-multi]').click();
      var q=__qa.S.questions[0];var tg=document.querySelector('[data-action=multi-toggle]');if(tg)tg.click();
      var sel=(__qa.S._multiSelection&&__qa.S._multiSelection[q.id])?__qa.S._multiSelection[q.id].length:0;
      var cf=document.querySelector('[data-action=multi-confirm]');
      return JSON.stringify({mode:__qa.S.quizMode,sel:sel,hasConfirm:!!cf});})()`,
    (v) => { const o = JSON.parse(v); return o.mode === 'multi' && o.sel > 0 && o.hasConfirm === true; });
  await step('E5 名词解释', `(function(){__qa.switchView('home');document.querySelector('[data-action=start-noun]').click();
    return document.querySelectorAll('#view-terms .term-card').length;})()`, (v) => v > 0);
  await step('E6 错题本路径(先答错一题,再进 wrong 模式)', `(function(){
    __qa.startQuiz('biochem_1_2','all');__qa.S.qIndex=0;var q=__qa.S.questions[0];
    var ua='';if(q.type==='short')ua='skip';else if(q.type==='truefalse')ua=String(q.answer).toLowerCase()==='true'?'false':'true';
    else{var ks=Object.keys(q.options);for(var i=0;i<ks.length;i++){if(String(ks[i]).toLowerCase()!==String(q.answer).toLowerCase()){ua=ks[i];break;}}}
    __qa.submitAnswer(q.id,ua);
    __qa.switchView('home');var r=__qa.startQuiz('biochem_1_2','wrong');
    return JSON.stringify({ok:r,wrongN:Object.keys(__qa.S.wrongSet).length});})()`,
    (v) => { const o = JSON.parse(v); return o.ok === true && o.wrongN > 0; });
  await step('E7 错题本视图', `(function(){__qa.switchView('errors');return document.querySelector('#view-errors').innerText.length>0;})()`, (v) => v === true);
  await step('E8 导出数据 JSON(data.wrongSet/data.bookmarks 存在)', `(function(){var j=window.__expimp.exportData();var o=JSON.parse(j);
    return typeof j==='string'&&o&&o.type==='learning-data'&&o.data&&typeof o.data.wrongSet==='object'&&typeof o.data.bookmarks==='object';})()`, (v) => v === true);
  await step('E9 导入数据(先清后导:wrongSet 恢复一致)',
    `(function(){var j=window.__expimp.exportData();var o=JSON.parse(j);
      var savedWrong=JSON.stringify(o.data.wrongSet);
      __qa.S.wrongSet={};__qa.invalidate();
      window.__expimp.importData(j);
      return JSON.stringify({wrongEq:JSON.stringify(__qa.S.wrongSet)===savedWrong});})()`,
    (v) => { const o = JSON.parse(v); return o.wrongEq === true; });

  /* ============ C4. 跨天 mock(放最后:副作用可能阻塞主线程,已验证断言后单独确认) ============ */
  await step('C4 跨天 mock:覆写 window.Date 返回 2099-01-01 → 提交 1 题 → 新键从 0 新计={1,1}(E9 导入已清统计),累计={1,1}',
    `(function(){
      var RD=window.Date;
      var MD=function(){var a=arguments;if(a.length)return new RD(a[0],a[1]||0,a[2]||1);return new RD(2099,0,1);};
      MD.now=function(){return new RD(2099,0,1).getTime();};MD.prototype=RD.prototype;
      window.Date=MD;
      __qa.startQuiz('biochem_1_2','all');var q=__qa.S.questions[0];__qa.submitAnswer(q.id,q.answer);
      window.Date=RD;
      var t=JSON.parse(localStorage.getItem('hnu_academy_total'));
      var dd=JSON.parse(localStorage.getItem('hnu_academy_daily_2099-01-01'));
      return JSON.stringify({t:JSON.stringify(t),dd:JSON.stringify(dd)});})()`,
    (v) => v === '{"t":"{\\"totalCount\\":1,\\"totalCorrect\\":1}","dd":"{\\"totalCount\\":1,\\"totalCorrect\\":1}"}');

  /* ============ F. 汇总 JS 错误 ============ */
  await sleep(400);
  console.log('\n=== JS exceptions: ' + exceptions.length + ' ===');
  exceptions.forEach((e) => console.log('  EXC: ' + trunc(e, 300)));
  console.log('=== console errors: ' + consoleErrs.length + ' ===');
  consoleErrs.forEach((e) => console.log('  ERR: ' + trunc(e, 300)));

  edge.kill();
  if (exceptions.length || consoleErrs.length) fail('JS 错误非零');
  console.log(failed ? '\nRESULT: FAILED' : '\nRESULT: ALL PASSED');
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
