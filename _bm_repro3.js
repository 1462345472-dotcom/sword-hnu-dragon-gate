/* BM bug 复现 v3:对照组(同章模式) + 跨章模式,精确观察内存键 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9350;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmrepro3-'));
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
  const bmKeys = () => ev('Object.keys(__qa.S.bookmarks)');
  const lsKeys = () => ev('(function(){var out=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf("hnu_academy_bm_")===0)out.push(k+"="+localStorage.getItem(k));}return out;})()');

  let ready = false;
  for (let i = 0; i < 40; i++) { try { if (await ev('window.__qa?1:0') === 1) { ready = true; break; } } catch (e) {} await sleep(500); }
  if (!ready) { fail('app not ready'); process.exit(1); }
  pass('app ready');
  await ev('try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);}}catch(e){};location.reload();');
  await sleep(2500);

  /* ===== 对照组 A:同章模式收藏→取消→reload ===== */
  console.log('--- Control A: same-chapter toggle in chapter mode ---');
  await ev('__qa.switchView("home");'); await sleep(200);
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(200);
  await click('[data-action="start-quiz"]'); await sleep(400);
  await click('[data-action="toggle-bookmark"]'); await sleep(200);
  console.log('after bookmark:', JSON.stringify(await bmKeys()));
  await click('[data-action="toggle-bookmark"]'); await sleep(200);
  console.log('after cancel:', JSON.stringify(await bmKeys()));
  await reload();
  console.log('after reload keys:', JSON.stringify(await bmKeys()));
  const bmA = await ev('__qa.bmQs().length');
  if (bmA !== 0) fail('Control A: bmQs not empty (' + bmA + ')'); else pass('Control A: same-chapter cancel works, bmQs empty after reload');

  /* ===== 复现 B:跨章精选习题模式取消收藏 ===== */
  console.log('--- Repro B: cross-chapter cancel in 精选习题 mode ---');
  /* 收藏 biochem_1_2 题1 和 biochem_3 题1(都在章节模式下做,键正确) */
  await ev('__qa.switchView("home");'); await sleep(200);
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(200);
  await click('[data-action="start-quiz"]'); await sleep(400);
  await click('[data-action="toggle-bookmark"]'); await sleep(200);
  await click('[data-action="go-home"]'); await sleep(200);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(200);
  await click('[data-action="start-quiz"]'); await sleep(400);
  await click('[data-action="toggle-bookmark"]'); await sleep(200);
  await click('[data-action="go-home"]'); await sleep(200);
  console.log('two bookmarks stored:', JSON.stringify(await bmKeys()));
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  const st = await ev('(function(){var S=__qa.S;return {subj:S.subject,qs:S.questions.map(function(q){return q.id;}),idx:S.qIndex};})()');
  console.log('精选习题 mode:', JSON.stringify(st));
  /* 翻到第二题(biochem_3 题1,S.subject 仍是 biochem_1_2) */
  await click('[data-action="nav-next"]'); await sleep(300);
  const cur = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {subj:S.subject,qid:q.id,idx:S.qIndex};})()');
  console.log('on Q2:', JSON.stringify(cur));
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  console.log('memory keys after cancel:', JSON.stringify(await bmKeys()));
  const realB = await ev('!!__qa.S.bookmarks["biochem_3__1"]');
  const realA = await ev('!!__qa.S.bookmarks["biochem_1_2__1"]');
  console.log('biochem_3__1 (should-be-removed):', realB, '| biochem_1_2__1 (should-stay):', realA);
  if (realB === true) fail('Repro B: real key biochem_3__1 NOT removed in memory (delete hit wrong key)');
  else pass('Repro B memory: real key removed');
  if (realA === false) fail('Repro B: biochem_1_2__1 was WRONGLY removed (collateral damage)');
  else pass('Repro B memory: other bookmark intact');
  console.log('ls bm_ blocks:', JSON.stringify(await lsKeys()));
  await reload();
  const bmB = await ev('__qa.bmQs().map(function(q){return q.id;})');
  console.log('bmQs after cancel+reload:', JSON.stringify(bmB));
  if (bmB.indexOf(1) >= 0) fail('Repro B CONFIRMED: question still in 精选习题 after cancel+reload');
  else pass('Repro B: gone after cancel+reload');

  /* ===== 对照 C:精选习题模式,取消第一道题(S.subject 章节匹配)===== */
  console.log('--- Control C: cancel Q1 in 精选习题 mode (subject matches) ---');
  await click('[data-action="go-home"]'); await sleep(200);
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  const stC = await ev('(function(){var S=__qa.S;return {subj:S.subject,qs:S.questions.map(function(q){return q.id;})};})()');
  console.log('精选习题 mode:', JSON.stringify(stC));
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  console.log('memory keys after cancel Q1:', JSON.stringify(await bmKeys()));
  const curC = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {subj:S.subject,qid:q.id};})()');
  console.log('on Q1:', JSON.stringify(curC));
  const realC = await ev('!!__qa.S.bookmarks["biochem_1_2__1"]');
  if (realC === true) fail('Control C: biochem_1_2__1 not removed'); else pass('Control C: matching-subject cancel works in memory');

  console.log('--- summary ---');
  console.log('exceptions:', exceptions.length ? exceptions : 'none');
  console.log('consoleErrs:', consoleErrs.length ? consoleErrs : 'none');
  console.log(failed ? 'RESULT: FAIL (bug reproduced)' : 'RESULT: PASS');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
