/* 补充:多选(multi)答题路径 + 名词(short)路径实测
   submitAnswer 判定基于 curQ()(S.qIndex 指向的当前题),须先定位目标题 index */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9378;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'expimpmulti-'));

let failed = false;
const fail = (m) => { failed = true; console.log('FAIL: ' + m); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
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
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
  ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable');
  let ready = false;
  for (let i = 0; i < 40; i++) {
    try { const r = await send('Runtime.evaluate', { expression: 'window.__qa?1:0', returnByValue: true }); if (r.result && r.result.result && r.result.result.value === 1) { ready = true; break; } } catch (e) {}
    await sleep(500);
  }
  if (!ready) { fail('page not ready'); edge.kill(); process.exit(1); }
  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result && r.result.exceptionDetails) throw new Error(r.result.exceptionDetails.text);
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  const step = async (name, expr, expect) => {
    let v; try { v = await ev(expr); } catch (e) { fail('[' + name + '] exception: ' + e.message); return; }
    const ok = expect(v);
    console.log((ok ? 'PASS' : 'FAIL') + ' [' + name + '] ' + JSON.stringify(v));
    if (!ok) failed = true;
  };

  await step('进入首页', '(function(){if(__qa.S.view==="home")return "home";var b=document.querySelector("[data-action=enter]");if(b)b.click();return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);
  await step('startQuiz 全题', '(function(){__qa.startQuiz("biochem_1_2","all");return __qa.S.questions.length;})()', (v) => v > 0);
  await step('多选答题(定位 index 后答对→ok:true,不计错题)', '(function(){var idx=-1;for(var i=0;i<__qa.S.questions.length;i++){if(__qa.S.questions[i].type==="multi"){idx=i;break;}}if(idx<0)return "no-multi";var q=__qa.S.questions[idx];__qa.S.qIndex=idx;var ok=__qa.submitAnswer(q.id,q.answer);return JSON.stringify({id:q.id,type:q.type,ok:ok,wrong:__qa.S.wrongSet[__qa.ak("biochem_1_2",q.id)]?1:0});})()', (v) => { const o = JSON.parse(v); return o.type === 'multi' && o.ok === true && o.wrong === 0; });
  await step('多选答错→进错题本', '(function(){var idx=-1;for(var i=0;i<__qa.S.questions.length;i++){if(__qa.S.questions[i].type==="multi"){idx=i;break;}}if(idx<0)return "no-multi";var q=__qa.S.questions[idx];var k=__qa.ak("biochem_1_2",q.id);var ua=q.answer;var alt=(ua[0]==="A"?"B":"A")+ua.slice(1);__qa.S.qIndex=idx;delete __qa.S.answers[k];delete __qa.S.revealed[k];__qa.invalidate();var ok=__qa.submitAnswer(q.id,alt);return JSON.stringify({ok:ok,wrong:__qa.S.wrongSet[k]?1:0});})()', (v) => { const o = JSON.parse(v); return o.ok === false && o.wrong === 1; });
  await step('名词题(startQuiz short)→ 首题 short 且答对', '(function(){__qa.startQuiz("biochem_1_2","short");var q=__qa.S.questions[0];if(!q)return "no-short";__qa.S.qIndex=0;var ok=__qa.submitAnswer(q.id,"done");return JSON.stringify({type:q.type,count:__qa.S.questions.length,ok:ok});})()', (v) => { const o = JSON.parse(v); return o.type === 'short' && o.ok === true; });

  edge.kill();
  console.log(failed ? '=== RESULT: FAIL ===' : '=== RESULT: PASS ===');
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(1); });
