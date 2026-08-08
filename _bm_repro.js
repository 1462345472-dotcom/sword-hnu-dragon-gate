/* BM bug 复现:收藏→取消→reload,验证精选习题跨章节场景 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9347;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmrepro-'));

let exceptions = [], consoleErrs = [], failed = false;
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
  if (!targets) { fail('CDP port not reachable'); process.exit(1); }
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
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
  const reload = async () => { await send('Page.reload'); await sleep(2500); };

  let ready = false;
  for (let i = 0; i < 40; i++) {
    try { if (await ev('window.__qa?1:0') === 1) { ready = true; break; } } catch (e) {}
    await sleep(500);
  }
  if (!ready) { fail('app not ready'); process.exit(1); }
  pass('app ready');

  /* 清理所有旧数据 */
  await ev('try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);}}catch(e){}; location.reload();');
  await sleep(2500);

  /* 取两个不同章节的第一题 */
  const chs = await ev('Object.keys(QUESTION_BANKS)');
  console.log('chapters:', JSON.stringify(chs));
  const sel = await ev('(function(){var ks=Object.keys(QUESTION_BANKS);var a=ks[0],b=ks[1];return {a:a,idA:QUESTION_BANKS[a].questions[0].id,b:b,idB:QUESTION_BANKS[b].questions[0].id};})()');
  console.log('selected:', JSON.stringify(sel));

  /* 场景1:普通章节模式(同章)收藏→取消→reload —— 对照组 */
  console.log('--- Scenario 1: same-chapter bookmark toggle (control) ---');
  await ev(`toggleBookmark('${sel.a}','${sel.idA}');`);
  let bm1 = await ev(`!!S.bookmarks['${sel.a}__${sel.idA}']`);
  if (bm1 !== true) fail('S1: bookmark not added in memory'); else pass('S1: bookmark added');
  await ev(`toggleBookmark('${sel.a}','${sel.idA}');`);
  bm1 = await ev(`!!S.bookmarks['${sel.a}__${sel.idA}']`);
  if (bm1 !== false) fail('S1: same-chapter unbookmark failed in memory'); else pass('S1: unbookmark removed from memory');
  await reload();
  bm1 = await ev(`!!S.bookmarks['${sel.a}__${sel.idA}']`);
  if (bm1 === true) fail('S1: same-chapter resurrected after reload'); else pass('S1: same-chapter clean after reload');

  /* 场景2:跨章节 —— 收藏A章题 + B章题,进入精选习题(S.subject=A),取消B章题 */
  console.log('--- Scenario 2: cross-chapter bookmark cancel in bookmarked mode ---');
  await ev(`toggleBookmark('${sel.a}','${sel.idA}');toggleBookmark('${sel.b}','${sel.idB}');`);
  let cnt = await ev(`Object.keys(S.bookmarks).length`);
  if (cnt !== 2) fail('S2: expected 2 bookmarks, got ' + cnt); else pass('S2: two bookmarks stored');
  await reload();
  const bmList = await ev(`bmQs().map(function(q){return q.id;})`);
  console.log('bmQs after reload:', JSON.stringify(bmList));
  if (bmList.indexOf(sel.idB) < 0) fail('S2: idB missing from bmQs before cancel'); else pass('S2: idB in bmQs');

  /* 模拟精选习题模式:start-bookmarked 会把 S.subject 设为第一题章节 */
  const mode = await ev(`(function(){var bm=bmQs();var bmb=findBankForQ(bm[0].id);if(bmb)startQuizWithProgress(bmb.key,'bookmarked');return {subj:S.subject,questions:S.questions.map(function(q){return q.id;})};})()`);
  console.log('bookmarked mode state:', JSON.stringify(mode));
  if (mode.questions.indexOf(sel.idB) < 0) fail('S2: idB not in quiz questions'); else pass('S2: idB in bookmarked quiz questions');
  if (mode.subj === sel.b) fail('S2: S.subject is B (would mask bug); pick earlier chapter'); else pass('S2: S.subject=' + mode.subj + ' (first bookmark chapter)');

  /* 用户刷到 idB(属于章节 B),点取消收藏 —— 代码路径 toggleBookmark(S.subject, cq.id) */
  await ev(`toggleBookmark(S.subject,'${sel.idB}');`);
  const realKeyStill = await ev(`!!S.bookmarks['${sel.b}__${sel.idB}']`);
  const wrongKeyNow = await ev(`!!S.bookmarks[S.subject+'__${sel.idB}']`);
  console.log('after cancel: realKey(B__idB)=' + realKeyStill + ' wrongKey(S.subject__idB)=' + wrongKeyNow);
  if (realKeyStill === true) { fail('BUG REPRODUCED: cross-chapter cancel did NOT remove real key B__' + sel.idB); }
  else pass('S2: real key removed in memory');

  await ev(`saveState();`);
  await reload();
  const bmList2 = await ev(`bmQs().map(function(q){return q.id;})`);
  console.log('bmQs after cancel+reload:', JSON.stringify(bmList2));
  if (bmList2.indexOf(sel.idB) >= 0) { fail('BUG REPRODUCED: idB still in bmQs after cancel+reload'); }
  else pass('S2: idB gone from bmQs after cancel+reload');

  /* 场景3:精选习题模式收藏新题(空星→实星)再取消 */
  console.log('--- Scenario 3: bookmark then cancel within bookmarked mode (fresh) ---');
  await ev(`toggleBookmark('${sel.a}','${sel.idA}');toggleBookmark('${sel.b}','${sel.idB}');`);
  await reload();
  await ev(`(function(){var bm=bmQs();var bmb=findBankForQ(bm[0].id);if(bmb)startQuizWithProgress(bmb.key,'bookmarked');})()`);
  /* 用户看到 idB 星标(UI 用 isBookmarked(S.subject,id)),点一下→取消 */
  const uiStarB = await ev(`isBookmarked(S.subject,'${sel.idB}')`);
  console.log('UI star state for idB (isBookmarked(S.subject,idB)) =', uiStarB, '(subject=' + (await ev('S.subject')) + ')');
  await ev(`toggleBookmark(S.subject,'${sel.idB}');`);
  const after1 = await ev(`!!S.bookmarks['${sel.b}__${sel.idB}']`);
  console.log('after toggle#1 (user intends cancel): realKey=' + after1);
  await ev(`toggleBookmark(S.subject,'${sel.idB}');`);
  const after2 = await ev(`!!S.bookmarks['${sel.b}__${sel.idB}']`);
  console.log('after toggle#2 (user intends cancel again): realKey=' + after2);
  await ev(`saveState();`);
  await reload();
  const bmList3 = await ev(`bmQs().map(function(q){return q.id;})`);
  console.log('bmQs after S3:', JSON.stringify(bmList3));
  if (bmList3.indexOf(sel.idB) >= 0) fail('S3: idB still in bmQs after cancel-cancel+reload');
  else pass('S3: idB gone after toggles+reload');

  console.log('--- summary ---');
  console.log('exceptions:', exceptions.length ? exceptions : 'none');
  console.log('consoleErrs:', consoleErrs.length ? consoleErrs : 'none');
  console.log(failed ? 'RESULT: FAIL (bug reproduced)' : 'RESULT: PASS (no bug)');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
