/* BM fix 验证:完整回归
   场景1: 精选习题跨章取消收藏 → reload → 无此题(核心 bug)
   场景2: 精选习题跨章取消第一道题 → reload → 无此题
   场景3: 收藏 → reload → 有此题(收藏持久化不回归)
   场景4: 同章普通模式取消 → reload → 无此题
   场景5: 跨章隔离:取消一章不影响另一章
   场景6: 错题路径(答错→错题本→答对→移除)
   场景7: 0 JS 异常 / 0 console error
   使用不同章节的不同 id 题避免同 id 混淆 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9351;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmverify-'));
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
  const bmIds = () => ev('__qa.bmQs().map(function(q){return q.id;})');
  const toHome = async () => {
    const v = await ev('__qa.S.view');
    if (v === 'splash') { await click('[data-action="enter"]'); await sleep(300); }
    else { await click('[data-action="go-home"]'); await sleep(300); }
  };
  const enterChapterQuiz = async (ch) => {
    await toHome();
    await click('.chapter-chip[data-key="' + ch + '"]'); await sleep(250);
    await click('[data-action="start-quiz"]'); await sleep(450);
  };
  const resetAll = async () => {
    await ev('try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);}}catch(e){};location.reload();');
    await sleep(2500);
  };

  let ready = false;
  for (let i = 0; i < 40; i++) { try { if (await ev('window.__qa?1:0') === 1) { ready = true; break; } } catch (e) {} await sleep(500); }
  if (!ready) { fail('app not ready'); process.exit(1); }
  pass('app ready');

  /* 选择 biochem_1_2 题1 与 biochem_3 题2(不同 id,避免混淆) */
  const sel = await ev('(function(){return {idA:__qa.getBank("biochem_1_2").questions[0].id,idB:__qa.getBank("biochem_3").questions[1].id};})()');
  const idA = sel.idA, idB = sel.idB;
  console.log('ids: A(biochem_1_2)=' + idA + ' B(biochem_3)=' + idB);

  /* ===== 场景1:核心 bug — 跨章精选习题取消收藏(取消第二道)===== */
  console.log('--- Scenario 1: cancel Q2 in bookmarked mode, reload ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 收藏 A 题
  await click('[data-action="go-home"]'); await sleep(250);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 收藏 B 题
  console.log('stored:', JSON.stringify(await bmKeys()));
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  let st = await ev('(function(){var S=__qa.S;return {subj:S.subject,qs:S.questions.map(function(q){return q.id;})};})()');
  console.log('bookmarked mode:', JSON.stringify(st));
  if (st.subj === 'biochem_1_2' && st.qs.length === 2) pass('S1: cross-chapter bookmarked list loaded (subj=' + st.subj + ')');
  else fail('S1: unexpected bookmarked state ' + JSON.stringify(st));
  /* 翻到第二题并取消 */
  await click('[data-action="nav-next"]'); await sleep(300);
  const cur = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {subj:S.subject,qid:q.id,bmSubj:q._bmSubj};})()');
  console.log('on Q2:', JSON.stringify(cur));
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  console.log('memory keys after cancel:', JSON.stringify(await bmKeys()));
  const b3 = await ev('!!__qa.S.bookmarks["biochem_3__' + idB + '"]');
  const a1 = await ev('!!__qa.S.bookmarks["biochem_1_2__' + idA + '"]');
  if (b3 === true) fail('S1: real key biochem_3__' + idB + ' still in memory');
  else pass('S1: real key removed in memory');
  if (a1 !== true) fail('S1: other bookmark biochem_1_2__' + idA + ' wrongly removed');
  else pass('S1: other bookmark intact');
  await reload();
  const bm1 = await bmIds();
  console.log('bmQs after cancel+reload:', JSON.stringify(bm1));
  if (bm1.indexOf(idB) >= 0) fail('S1 CORE: ' + idB + ' STILL in 精选习题 after cancel+reload');
  else pass('S1 CORE: canceled question gone after reload');
  if (bm1.indexOf(idA) < 0) fail('S1: kept question ' + idA + ' missing after reload');
  else pass('S1: kept question ' + idA + ' still present after reload');

  /* ===== 场景2:跨章取消第一道题 ===== */
  console.log('--- Scenario 2: cancel Q1 in bookmarked mode, reload ---');
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  st = await ev('(function(){var S=__qa.S;return {subj:S.subject,qs:S.questions.map(function(q){return q.id;})};})()');
  console.log('bookmarked mode:', JSON.stringify(st));
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  const aNow = await ev('!!__qa.S.bookmarks["biochem_1_2__' + idA + '"]');
  if (aNow === true) fail('S2: Q1 real key not removed'); else pass('S2: Q1 removed in memory');
  await reload();
  const bm2 = await bmIds();
  if (bm2.indexOf(idA) >= 0) fail('S2: ' + idA + ' still in 精选习题 after cancel+reload');
  else pass('S2: canceled Q1 gone after reload');
  if (bm2.indexOf(idB) >= 0) pass('S2: kept Q2 ' + idB + ' still present (isolation OK)');
  else fail('S2: kept Q2 wrongly missing');

  /* ===== 场景3:收藏 → reload → 有此题 ===== */
  console.log('--- Scenario 3: bookmark persists across reload ---');
  await enterChapterQuiz('biochem_3');
  await click('[data-action="toggle-bookmark"]'); await sleep(250);
  await reload();
  const bm3 = await bmIds();
  if (bm3.indexOf(idB) < 0) fail('S3: bookmarked question lost after reload'); else pass('S3: bookmark persists (still in 精选习题)');

  /* ===== 场景4:同章普通模式取消 → reload → 无 ===== */
  console.log('--- Scenario 4: same-chapter cancel in chapter mode ---');
  await toHome();
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 收藏(新题,若此前已收藏则取消)
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 取消
  await reload();
  const bm4 = await bmIds();
  if (bm4.indexOf(idA) >= 0) fail('S4: same-chapter canceled question still present');
  else pass('S4: same-chapter cancel clean after reload');

  /* ===== 场景5:跨章隔离 — 取消章节A的书签,章节B的书签不受影响 ===== */
  console.log('--- Scenario 5: cross-chapter isolation ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  await click('[data-action="toggle-bookmark"]'); await sleep(250);
  await click('[data-action="go-home"]'); await sleep(250);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="toggle-bookmark"]'); await sleep(250);
  await reload();
  let isoBm = await bmIds();
  if (isoBm.indexOf(idA) < 0 || isoBm.indexOf(idB) < 0) fail('S5: setup failed ' + JSON.stringify(isoBm));
  /* 直接通过 UI 在章节模式取消 A 的书签 */
  await toHome();
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 取消 A
  await reload();
  isoBm = await bmIds();
  if (isoBm.indexOf(idA) >= 0) fail('S5: A still present after cancel');
  else pass('S5: A removed, isolated');
  if (isoBm.indexOf(idB) < 0) fail('S5: B wrongly lost after canceling A');
  else pass('S5: B untouched (isolation OK)');

  /* ===== 场景6:错题路径 ===== */
  console.log('--- Scenario 6: wrong-set path (answer wrong → in 错题本; answer right → removed) ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  /* 答错第一题 */
  const q1 = await ev('(function(){var q=__qa.S.questions[__qa.S.qIndex];return {id:q.id,type:q.type,options:q.options,answer:q.answer};})()');
  let wrongOpt = null;
  if (q1.type === 'choice') { wrongOpt = Object.keys(q1.options).find((k) => k !== String(q1.answer)); }
  if (wrongOpt !== null) {
    await click(`.option[data-value="${wrongOpt}"]`); await sleep(300);
    let wsKeys = await ev('Object.keys(__qa.S.wrongSet)');
    if (wsKeys.length === 0) fail('S6: wrong question not recorded'); else pass('S6: wrong question recorded: ' + JSON.stringify(wsKeys));
    /* 答对同一题(重开) */
    await click('[data-action="go-home"]'); await sleep(250);
    await click('[data-action="start-quiz"]'); await sleep(450);
    const ansVal = await ev('(function(){var q=__qa.S.questions[__qa.S.qIndex];return {id:q.id,ans:q.answer};})()');
    if (q1.type === 'choice') { await click(`.option[data-value="${ansVal.ans}"]`); await sleep(300); }
    else { await click('[data-action="answer"][data-value="true"]'); await sleep(300); }
    wsKeys = await ev('Object.keys(__qa.S.wrongSet)');
    if (wsKeys.length !== 0) fail('S6: correct answer did not remove from wrongSet: ' + JSON.stringify(wsKeys));
    else pass('S6: correct answer removes wrongSet entry');
    await reload();
    const wq = await ev('__qa.wrongQs().length');
    if (wq !== 0) fail('S6: wrongQs not empty after fix'); else pass('S6: wrongQs empty after reload (cross-chapter key fix holds)');
  } else {
    pass('S6: skipped (question type not choice on first question)');
  }

  /* ===== 场景7:JS 异常检查 ===== */
  console.log('--- Scenario 7: no JS errors ---');
  if (exceptions.length) fail('JS exceptions: ' + exceptions.join(' | ')); else pass('S7: no JS exceptions');
  if (consoleErrs.length) fail('console errors: ' + consoleErrs.join(' | ')); else pass('S7: no console errors');

  console.log(failed ? 'RESULT: FAIL' : 'RESULT: ALL PASS');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
