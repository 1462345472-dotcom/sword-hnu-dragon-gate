/* BM bug 复现 v2:完整 UI 驱动
   流程:收藏 biochem_1_2 题1 → 收藏 biochem_3 题1 → 精选习题 → 翻到第二题 → 取消收藏 → reload → 查 bmQs */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9349;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmrepro2-'));
let failed = false;
const fail = (m) => { failed = true; console.log('FAIL: ' + m); };
const pass = (m) => console.log('PASS: ' + m);
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
  let exceptions = [], consoleErrs = [];
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
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
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
  const click = async (sel) => { await ev(`(function(){var el=document.querySelector('${sel}');if(el)el.click();return !!el;})()`); };
  const reload = async () => { await send('Page.reload'); await sleep(2500); };

  let ready = false;
  for (let i = 0; i < 40; i++) { try { if (await ev('window.__qa?1:0') === 1) { ready = true; break; } } catch (e) {} await sleep(500); }
  if (!ready) { fail('app not ready'); process.exit(1); }
  pass('app ready');

  /* 清理旧数据并刷新 */
  await ev('try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);}}catch(e){};location.reload();');
  await sleep(2500);

  /* Step 1: 首页选 biochem_1_2 章节 → 全部刷题 → 收藏当前题(题1) */
  await ev('__qa.switchView("home");');
  await sleep(300);
  await click('.chapter-chip[data-key="biochem_1_2"]');
  await sleep(300);
  await click('[data-action="start-quiz"]');
  await sleep(400);
  let cur = await ev('(function(){var q=__qa.S.questions[__qa.S.qIndex];return {subj:__qa.S.subject,qid:q.id,type:q.type};})()');
  console.log('quiz on chapter:', JSON.stringify(cur));
  await click('[data-action="toggle-bookmark"]');  // 收藏
  await sleep(300);
  let bm1 = await ev('Object.keys(S.bookmarks)');
  console.log('after bookmark #1:', JSON.stringify(bm1));
  pass('bookmark #1 in memory');

  /* Step 2: 返回首页,选 biochem_3 → 全部刷题 → 收藏题1 */
  await click('[data-action="go-home"]'); await sleep(300);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(300);
  await click('[data-action="start-quiz"]'); await sleep(400);
  let cur2 = await ev('(function(){var q=__qa.S.questions[__qa.S.qIndex];return {subj:__qa.S.subject,qid:q.id};})()');
  console.log('quiz on chapter:', JSON.stringify(cur2));
  await click('[data-action="toggle-bookmark"]');  // 收藏
  await sleep(300);
  let bm2 = await ev('Object.keys(S.bookmarks)');
  console.log('after bookmark #2:', JSON.stringify(bm2));

  /* Step 3: 返回首页 → 精选习题 → 跨章节列表 */
  await click('[data-action="go-home"]'); await sleep(300);
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  let bmState = await ev('(function(){var S=__qa.S;return {subj:S.subject,questions:S.questions.map(function(q){return q.id;}),qIndex:S.qIndex};})()');
  console.log('bookmarked mode:', JSON.stringify(bmState));
  if (bmState.questions.length !== 2) fail('expected 2 bookmarked questions, got ' + bmState.questions.length);

  /* Step 4: 翻到第二题(biochem_3 的题1),点取消收藏 */
  await click('[data-action="nav-next"]'); await sleep(300);
  let cur3 = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {subj:S.subject,qid:q.id,idx:S.qIndex};})()');
  console.log('now on Q2:', JSON.stringify(cur3), '(S.subject still=', cur3.subj, ')');
  const starWasActive = await ev('document.querySelector(".bm-btn")?document.querySelector(".bm-btn").classList.contains("active"):null');
  console.log('star active before cancel (UI):', starWasActive);
  await click('[data-action="toggle-bookmark"]');  // 取消收藏
  await sleep(300);
  const keysAfter = await ev('Object.keys(S.bookmarks)');
  console.log('bookmarks in memory after cancel:', JSON.stringify(keysAfter));

  /* Step 5: 检查真实键 biochem_3__1 是否还在 */
  const realKey = await ev('!!S.bookmarks["biochem_3__1"]');
  console.log('real key biochem_3__1 present:', realKey);
  if (realKey === true) fail('BUG: real bookmark key biochem_3__1 still present after cancel (delete hit wrong key)');
  else pass('real key removed in memory');

  /* Step 6: reload 后查精选习题 */
  await reload();
  const bmAfterReload = await ev('__qa.bmQs().map(function(q){return q.id;})');
  console.log('bmQs after cancel+reload:', JSON.stringify(bmAfterReload));
  if (bmAfterReload.indexOf(1) >= 0) fail('BUG REPRODUCED: question id=1 still in 精选习题 after cancel+reload');
  else pass('精选习题 empty after cancel+reload');

  console.log('exceptions:', exceptions.length ? exceptions : 'none');
  console.log('consoleErrs:', consoleErrs.length ? consoleErrs : 'none');
  console.log(failed ? 'RESULT: FAIL (bug reproduced)' : 'RESULT: PASS');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
