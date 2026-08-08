/* C18c 移除章节跳转下拉框,保留 chip 自动滚动定位 — Edge headless CDP 实测 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9343;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'c18cedge-'));

let exceptions = [];
let consoleErrs = [];
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
    if (r.result && r.result.exceptionDetails) throw new Error((r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description) || r.result.exceptionDetails.text);
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  const step = async (name, expr, expect) => {
    let v;
    try { v = await ev(expr); } catch (e) { fail('[' + name + '] exception: ' + e.message); return; }
    const ok = expect(v);
    console.log((ok ? 'PASS' : 'FAIL') + ' [' + name + '] ' + JSON.stringify(v));
    if (!ok) failed = true;
  };
  const assertEq = (name, got, want) => step(name, `(${got})`, (v) => JSON.stringify(v) === JSON.stringify(want));

  /* 1. 无下拉框:页面无任何 select / data-c18-nav */
  await assertEq('无 select 元素', 'document.querySelectorAll("select").length', 0);
  await assertEq('无 data-c18-nav', 'document.querySelectorAll("[data-c18-nav]").length', 0);

  /* 2. 章节键 51 */
  await assertEq('51 章节键', '__qa.qbKeys().length', 51);

  /* 3. 进入首页(跳过 splash) */
  await step('enter home', '(function(){if(__qa.S.view==="home")return "home";var b=document.querySelector("[data-action=enter]");if(b)b.click();return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);

  /* 4. 首页 chip 存在 + 当前章 chip 可见(容器内) */
  await step('chip 容器为滚动容器', '(function(){var hb=document.querySelector("#view-home .hero-bottom");return JSON.stringify({ov:getComputedStyle(hb).overflowX,scrollable:hb.scrollWidth>hb.clientWidth+2});})()',
    (v) => { const o = JSON.parse(v); return (o.ov === 'auto' || o.ov === 'scroll') && o.scrollable; });
  await step('默认 active chip 在可见区', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return JSON.stringify({key:c.getAttribute("data-key"),vis:L>=sl-1&&R<=sl+cw+1,sl:sl});})()',
    (v) => { const o = JSON.parse(v); return !!o.key && o.vis; });

  /* 5. 点远章 chip → 自动滚动定位到可见区(居中) */
  await step('点击 chip biochem_15', '(function(){document.querySelector(".chapter-chip[data-key=biochem_15]").click();return __qa.S.subject;})()', (v) => v === 'biochem_15');
  await sleep(200);
  await step('biochem_15 chip 可见+居中', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return JSON.stringify({sl:sl,L:L,R:R,cw:cw,vis:L>=sl-1&&R<=sl+cw+1,center:Math.abs(L-(sl+(cw-c.offsetWidth)/2))<=8});})()',
    (v) => { const o = JSON.parse(v); return o.vis && o.center; });

  /* 6. 相邻 chip 可点(当前 biochem_15 的前一 chip biochem_14) */
  await step('点击相邻 chip biochem_14', '(function(){var c=document.querySelector(".chapter-chip[data-key=biochem_14]");if(!c)return "missing";c.click();return JSON.stringify({subject:__qa.S.subject,active:document.querySelector(".chapter-chip.active").getAttribute("data-key")});})()',
    (v) => { const o = JSON.parse(v); return o.subject === 'biochem_14' && o.active === 'biochem_14'; });
  await step('biochem_14 chip 可见', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return L>=sl-1&&R<=sl+cw+1;})()', (v) => v === true);

  /* 7. 页面滚动后点远章 → 页面不跳(scrollY 不变)+ chip 可见 */
  await step('滚动到页底(平滑滚动落定)', '(function(){window.scrollTo(0,99999);return 1;})()', (v) => v === 1);
  await sleep(900);
  await step('页底位置>0', 'window.scrollY', (v) => v > 0);
  await ev('window.__c18test_scrollY=window.scrollY');
  await step('点击 chip biochem_36', '(function(){document.querySelector(".chapter-chip[data-key=biochem_36]").click();return __qa.S.subject;})()', (v) => v === 'biochem_36');
  await sleep(200);
  await step('biochem_36 可见+页不跳+滚动近末尾', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth,sw=hb.scrollWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return JSON.stringify({sl:sl,vis:L>=sl-1&&R<=sl+cw+1,scrollY:window.scrollY,preY:window.__c18test_scrollY,end:sl>=sw-cw-2});})()',
    (v) => { const o = JSON.parse(v); return o.vis && o.scrollY === o.preY && o.end; });

  /* 8. 切换科目 → 细胞 16 章,末章 chip 可见 */
  await step('切换细胞科目', '(function(){document.querySelector("[data-action=switch-course][data-course=cellbiology]").click();return __qa.S.course;})()', (v) => v === 'cellbiology');
  await sleep(200);
  await step('点击 chip cellbio_16', '(function(){document.querySelector(".chapter-chip[data-key=cellbio_16]").click();return __qa.S.subject;})()', (v) => v === 'cellbio_16');
  await sleep(200);
  await step('cellbio_16 chip 可见', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return L>=sl-1&&R<=sl+cw+1;})()', (v) => v === true);

  /* 9. 全部刷题路径 */
  await step('start-quiz', '(function(){document.querySelector("[data-action=start-quiz]").click();return JSON.stringify({view:__qa.S.view,mode:__qa.S.quizMode,n:__qa.S.questions.length,subject:__qa.S.subject});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'quiz' && o.mode === 'all' && o.n > 0 && o.subject === 'cellbio_16'; });
  await step('单题作答 submitAnswer', '(function(){var q=__qa.S.questions[0];var ans=(q.type==="truefalse")?"true":(q.type==="short")?"done":Object.keys(q.options)[0];__qa.submitAnswer(q.id,ans);return __qa.S.answers[__qa.ak(__qa.S.subject,q.id)]===ans;})()', (v) => v === true);

  /* 10. 多选路径 */
  await step('返回首页', '(function(){__qa.switchView("home");return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);
  await step('start-multi', '(function(){document.querySelector("[data-action=start-multi]").click();return JSON.stringify({view:__qa.S.view,mode:__qa.S.quizMode,n:__qa.S.questions.length});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'quiz' && o.mode === 'multi' && o.n > 0; });
  await sleep(200);
  await step('多选 toggle+confirm', '(function(){var q=__qa.S.questions[0];var tg=document.querySelector("[data-action=multi-toggle]");if(tg)tg.click();var sel=__qa.S._multiSelection&&__qa.S._multiSelection[q.id]?__qa.S._multiSelection[q.id].length:0;var cf=document.querySelector("[data-action=multi-confirm]");return JSON.stringify({sel:sel,hasConfirm:!!cf});})()',
    (v) => { const o = JSON.parse(v); return o.sel > 0 && o.hasConfirm === true; });

  /* 11. 名词解释路径 */
  await step('返回首页+名词解释', '(function(){__qa.switchView("home");return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);
  await step('start-noun', '(function(){document.querySelector("[data-action=start-noun]").click();return JSON.stringify({view:__qa.S.view,cards:document.querySelectorAll("#view-terms .term-card").length});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'terms' && o.cards > 0; });

  /* 12. 错题/书签无异常 */
  await step('wrongQs/bmQs 可用', '(function(){return JSON.stringify({w:__qa.wrongQs().length,b:__qa.bmQs().length});})()', (v) => /^\{/.test(v));

  /* 13. 回首页确认无 select + chip 定位仍正常 */
  await step('回首页', '(function(){__qa.switchView("home");return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);
  await assertEq('回首页后仍无 select', 'document.querySelectorAll("select").length', 0);
  await step('回首页后 active chip 可见', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return L>=sl-1&&R<=sl+cw+1;})()', (v) => v === true);

  /* 14. JS 错误统计 */
  console.log('JS exceptions: ' + exceptions.length + ' | console errors: ' + consoleErrs.length);
  if (exceptions.length > 0) { fail('发现 JS 异常: ' + exceptions.join(' || ')); }
  if (consoleErrs.length > 0) { console.log('console errors detail: ' + consoleErrs.join(' || ')); }

  ws.close(); edge.kill();
  console.log(failed ? '===== RESULT: FAIL =====' : '===== RESULT: ALL PASS =====');
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.log('FATAL: ' + e); process.exit(1); });
