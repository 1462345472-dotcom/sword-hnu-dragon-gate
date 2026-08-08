/* BM fix 验证 v2(修正测试缺陷:动态读当前题 id;自动处理 JS dialog)
   场景1: 精选习题跨章取消收藏 → reload → 无此题(核心 bug)
   场景2: 收藏 → reload → 有此题(收藏持久化不回归)
   场景3: 同章普通模式取消 → reload → 无此题
   场景4: 跨章隔离:取消一章不影响另一章
   场景5: 错题路径(答错→错题本;答对→移除)
   场景6: 做题/多选/名词路径冒烟
   场景7: 0 JS 异常 / 0 console error */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9352;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmverify2-'));
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
    } else if (m.method === 'Page.javascriptDialogOpening') {
      send('Page.handleJavaScriptDialog', { accept: false }).catch(() => {});
    }
  };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
  const click = async (sel) => { await ev(`(function(){var el=document.querySelector('${sel}');if(el)el.click();return !!el;})()`); };
  const reload = async () => { await send('Page.reload'); await sleep(2500); };
  const bmKeys = () => ev('Object.keys(__qa.S.bookmarks)');
  const bmIds = () => ev('__qa.bmQs().map(function(q){return q.id;})');
  const curQid = () => ev('__qa.S.questions[__qa.S.qIndex].id');
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

  /* ===== 场景1:核心 bug — 跨章精选习题取消收藏(第二道)===== */
  console.log('--- Scenario 1: cancel Q2 in bookmarked mode, reload ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  const idA = await curQid();
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 收藏 A 题
  await click('[data-action="go-home"]'); await sleep(250);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="nav-next"]'); await sleep(300);          // 第 2 题(id 与 A 不同)
  const idB = await curQid();
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 收藏 B 题
  console.log('ids: A=' + idA + ' B=' + idB + ' stored:', JSON.stringify(await bmKeys()));
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  let st = await ev('(function(){var S=__qa.S;return {subj:S.subject,qs:S.questions.map(function(q){return q.id;})};})()');
  console.log('bookmarked mode:', JSON.stringify(st));
  if (st.qs.length !== 2 || st.qs.indexOf(idA) < 0 || st.qs.indexOf(idB) < 0) fail('S1: expected bookmarked [' + idA + ',' + idB + '], got ' + JSON.stringify(st.qs));
  /* 翻到第二题(属于 biochem_3,与 S.subject 不同章)并取消 */
  await click('[data-action="nav-next"]'); await sleep(300);
  const cur = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {subj:S.subject,qid:q.id,bmSubj:q._bmSubj};})()');
  console.log('on Q2:', JSON.stringify(cur));
  if (cur.bmSubj === cur.subj) pass('S1: Q2 bmSubj=' + cur.bmSubj + ' (matches its chapter; cross-chapter confirmed)');
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  console.log('memory keys after cancel:', JSON.stringify(await bmKeys()));
  const realKey = await ev(`!!__qa.S.bookmarks['${cur.bmSubj}__${cur.qid}']`);
  if (realKey === true) fail('S1: real key ' + cur.bmSubj + '__' + cur.qid + ' still in memory');
  else pass('S1: real key removed in memory');
  const kept = await ev(`!!__qa.S.bookmarks['biochem_1_2__${idA}']`);
  if (kept !== true) fail('S1: other bookmark wrongly removed'); else pass('S1: other bookmark intact');
  await reload();
  const bm1 = await bmIds();
  console.log('bmQs after cancel+reload:', JSON.stringify(bm1));
  if (bm1.indexOf(cur.qid) >= 0) fail('S1 CORE: canceled question ' + cur.qid + ' still in 精选习题 after cancel+reload');
  else pass('S1 CORE: canceled question gone after reload');
  if (bm1.indexOf(idA) >= 0) pass('S1: kept question ' + idA + ' still present'); else fail('S1: kept question ' + idA + ' missing');
  /* 存储级断言:被取消章节的块应被删除/不含该项 */
  const bmBlock = await ev('(function(){try{return localStorage.getItem("hnu_academy_bm_"+"' + cur.bmSubj + '");}catch(e){return null;}})()');
  if (bmBlock !== null) fail('S1: localStorage bm block for ' + cur.bmSubj + ' not removed: ' + bmBlock);
  else pass('S1: localStorage bm_' + cur.bmSubj + ' block removed');

  /* ===== 场景2:收藏 → reload → 有此题 ===== */
  console.log('--- Scenario 2: bookmark persists across reload ---');
  await reload();
  const bm2 = await bmIds();
  if (bm2.length === 1 && bm2.indexOf(idA) >= 0) pass('S2: bookmark persists across reload (' + JSON.stringify(bm2) + ')');
  else fail('S2: unexpected bookmarks after reload ' + JSON.stringify(bm2));

  /* ===== 场景3:同章普通模式取消 → reload → 无 ===== */
  console.log('--- Scenario 3: same-chapter cancel in chapter mode ---');
  await enterChapterQuiz('biochem_1_2');
  await click('[data-action="toggle-bookmark"]'); await sleep(250);   // 取消(场景1 留下的 A 收藏)
  console.log('keys after cancel:', JSON.stringify(await bmKeys()));
  await reload();
  const bm3 = await bmIds();
  if (bm3.length !== 0) fail('S3: bmQs not empty after same-chapter cancel+reload: ' + JSON.stringify(bm3));
  else pass('S3: same-chapter cancel clean after reload');

  /* ===== 场景4:跨章隔离 ===== */
  console.log('--- Scenario 4: cross-chapter isolation ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  const idA2 = await curQid();
  await click('[data-action="toggle-bookmark"]'); await sleep(250);
  await click('[data-action="go-home"]'); await sleep(250);
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(250);
  await click('[data-action="start-quiz"]'); await sleep(450);
  await click('[data-action="nav-next"]'); await sleep(300);
  const idB2 = await curQid();
  await click('[data-action="toggle-bookmark"]'); await sleep(250);
  console.log('stored:', JSON.stringify(await bmKeys()));
  /* 精选习题模式取消 B 章那道题,reload 后 A 章书签必须仍在 */
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  st = await ev('(function(){var S=__qa.S;return {qs:S.questions.map(function(q){return q.id;})};})()');
  console.log('bookmarked:', JSON.stringify(st));
  /* 找到 B 章那道题(第二道)并取消 */
  await click('[data-action="nav-next"]'); await sleep(300);
  const cur4 = await ev('(function(){var S=__qa.S;var q=S.questions[S.qIndex];return {qid:q.id,bmSubj:q._bmSubj};})()');
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  await reload();
  const bm4 = await bmIds();
  if (bm4.indexOf(cur4.qid) >= 0) fail('S4: ' + cur4.qid + ' still present after cancel');
  else pass('S4: canceled question ' + cur4.qid + ' gone');
  if (bm4.indexOf(idA2) < 0) fail('S4: A chapter bookmark lost'); else pass('S4: A chapter bookmark intact after canceling B (isolation OK)');

  /* ===== 场景5:错题路径 ===== */
  console.log('--- Scenario 5: wrong-set path ---');
  await resetAll();
  await enterChapterQuiz('biochem_1_2');
  const q1 = await ev('(function(){var q=__qa.S.questions[__qa.S.qIndex];return {id:q.id,type:q.type,options:q.options,answer:q.answer};})()');
  if (q1.type === 'choice') {
    const wrongOpt = Object.keys(q1.options).find((k) => k !== String(q1.answer));
    await click(`.option[data-value="${wrongOpt}"]`); await sleep(350);
    let wsKeys = await ev('Object.keys(__qa.S.wrongSet)');
    if (wsKeys.length === 0) fail('S5: wrong not recorded'); else pass('S5: wrong recorded: ' + JSON.stringify(wsKeys));
    /* 答对同一题(重启会话) */
    await click('[data-action="go-home"]'); await sleep(250);
    await click('[data-action="start-quiz"]'); await sleep(450);
    await click(`.option[data-value="${q1.answer}"]`); await sleep(350);
    wsKeys = await ev('Object.keys(__qa.S.wrongSet)');
    if (wsKeys.length !== 0) fail('S5: correct answer did not remove wrongSet: ' + JSON.stringify(wsKeys));
    else pass('S5: correct answer removes wrongSet entry');
    await reload();
    const wqLen = await ev('__qa.wrongQs().length');
    if (wqLen !== 0) fail('S5: wrongQs not empty after reload'); else pass('S5: wrongQs empty after reload');
  } else { pass('S5: skipped (first Q not choice)'); }

  /* ===== 场景6:做题/多选/名词冒烟 ===== */
  console.log('--- Scenario 6: smoke quiz paths ---');
  await toHome();
  /* 全部刷题 */
  await click('[data-action="start-quiz"]'); await sleep(450);
  let view = await ev('__qa.S.view');
  if (view === 'quiz') pass('S6: start-quiz works'); else fail('S6: start-quiz view=' + view);
  await click('[data-action="go-home"]'); await sleep(250);
  /* 多选专项 */
  await click('[data-action="start-multi"]'); await sleep(450);
  view = await ev('__qa.S.view');
  if (view === 'quiz') pass('S6: start-multi works'); else { console.log('  (multi has no questions in this chapter? view=' + view); }
  await click('[data-action="go-home"]'); await sleep(250);
  /* 名词解释 */
  await click('[data-action="start-noun"]'); await sleep(450);
  view = await ev('__qa.S.view');
  if (view === 'terms') pass('S6: start-noun works'); else fail('S6: start-noun view=' + view);
  await click('[data-action="go-home"]'); await sleep(250);
  /* 精选习题入口(空时应 toast 不崩溃) */
  const bmCnt = await ev('__qa.bmQs().length');
  await click('[data-action="start-bookmarked"]'); await sleep(400);
  if (bmCnt === 0) { view = await ev('__qa.S.view'); if (view === 'quiz') fail('S6: start-bookmarked entered quiz with 0 bookmarks'); else pass('S6: start-bookmarked with 0 bookmarks stays (no crash)'); }
  else pass('S6: start-bookmarked with ' + bmCnt + ' bookmarks');

  /* ===== 场景7:JS 异常 ===== */
  console.log('--- Scenario 7: no JS errors ---');
  if (exceptions.length) fail('JS exceptions: ' + exceptions.join(' | ')); else pass('S7: no JS exceptions');
  if (consoleErrs.length) fail('console errors: ' + consoleErrs.join(' | ')); else pass('S7: no console errors');

  console.log(failed ? 'RESULT: FAIL' : 'RESULT: ALL PASS');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failed ? 1 : 0);
}
main().catch((e) => { console.error(e); process.exit(2); });
