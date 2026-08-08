/* C18b 章节跳转下拉框优化(独立固定行+美化+免闪烁)— Edge headless CDP 实测 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9342;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'c18bedge-'));

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

  /* 1. 章节键 51 */
  await assertEq('51 章节键', '__qa.qbKeys().length', 51);

  /* 2. 进入首页(跳过 splash) */
  await step('enter home', '(function(){var b=document.querySelector("[data-action=enter]");if(b)b.click();return __qa.S.view;})()', (v) => v === 'home');

  /* 3. 下拉框存在 + 选项数(生化 35 + 占位 1) */
  await step('下拉框存在', '!!document.querySelector("[data-c18-nav]")', (v) => v === true);
  await assertEq('生化下拉选项数', 'document.querySelector("[data-c18-nav]").options.length', 36);
  await step('默认选中章一致', '(function(){var s=document.querySelector("[data-c18-nav]");return JSON.stringify({subject:__qa.S.subject,sel:s.value,active:document.querySelector(".chapter-chip.active").getAttribute("data-key")});})()',
    (v) => { const o = JSON.parse(v); return o.subject === 'biochem_1_2' && o.sel === 'biochem_1_2' && o.active === 'biochem_1_2'; });

  /* 3a. 独立固定行:下拉框不在 .hero-bottom 滚动容器内,行容器是 hero-bottom 的前一兄弟 */
  await step('独立固定行(非 chip 滚动容器)', '(function(){var s=document.querySelector("[data-c18-nav]");var hb=document.querySelector("#view-home .hero-bottom");var row=s.parentNode;return JSON.stringify({inHb:!!s.closest(".hero-bottom"),rowIsPrev:hb.previousElementSibling===row,rowTag:row.tagName,inHeroCard:!!s.closest(".hero-card"),rowDisplay:getComputedStyle(row).display});})()',
    (v) => { const o = JSON.parse(v); return !o.inHb && o.rowIsPrev && o.rowTag === 'DIV' && o.inHeroCard && o.rowDisplay === 'flex'; });

  /* 3b. 美化:appearance:none + 自定义 data-uri 箭头 + 选中项显示章节名 + 玻璃态可读配色 */
  await step('select 美化(隐藏原生箭头+自定义箭头)', '(function(){var s=document.querySelector("[data-c18-nav]");var cs=getComputedStyle(s);return JSON.stringify({app:cs.appearance||cs.webkitAppearance,bg:cs.backgroundImage.indexOf("data:image/svg+xml")>=0,pill:cs.borderRadius.indexOf("9999px")>=0,opt:s.selectedOptions[0].textContent,color:cs.color,bgColor:cs.backgroundColor,blur:cs.backdropFilter.indexOf("blur")>=0});})()',
    (v) => { const o = JSON.parse(v); return o.app === 'none' && o.bg && o.pill && !!o.opt && o.color.indexOf('255, 255, 255') >= 0 && o.bgColor.indexOf('255, 255, 255') >= 0 && o.blur; });
  await step('行内标签=章节跳转', '(function(){return document.querySelector("[data-c18-nav]").parentNode.querySelector("span").textContent;})()', (v) => v === '章节跳转');

  /* 3c. 免重建:连续两次 __c18nav.sync() 不重建 DOM,元素身份不变、全局唯一 */
  await step('免重建:sync 两次节点身份不变', '(function(){var first=document.querySelector("[data-c18-nav]");__c18nav.sync();var s2=document.querySelector("[data-c18-nav]");var v2=s2.selectedOptions[0].value;__c18nav.sync();var s3=document.querySelector("[data-c18-nav]");return JSON.stringify({same1:s2===first,same2:s3===s2,count:document.querySelectorAll("[data-c18-nav]").length,rows:document.querySelectorAll("#view-home [data-c18-nav]").length,sel:v2,subject:__qa.S.subject});})()',
    (v) => { const o = JSON.parse(v); return o.same1 && o.same2 && o.count === 1 && o.rows === 1 && o.sel === o.subject; });

  /* 3d. 固定行不随 chip 横向滚动(hero-bottom scrollLeft 变化,导航行位置不变) */
  await step('固定行不随 chip 滚动', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var row=document.querySelector("[data-c18-nav]").parentNode;hb.scrollLeft=0;var l1=row.getBoundingClientRect().left;hb.scrollLeft=2000;var l2=row.getBoundingClientRect().left;return JSON.stringify({l1:l1,l2:l2,same:l1===l2,sl:hb.scrollLeft});})()',
    (v) => { const o = JSON.parse(v); return o.same && o.sl > 0; });

  /* 4. 下拉框选中 biochem_15 → 切换成功 + chip 可见 */
  await step('下拉切换 biochem_15', '(function(){var s=document.querySelector("[data-c18-nav]");s.value="biochem_15";s.dispatchEvent(new Event("change",{bubbles:true}));return __qa.S.subject;})()', (v) => v === 'biochem_15');
  await sleep(150);
  await step('biochem_15 chip 可见+滚动', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return JSON.stringify({sl:sl,L:L,R:R,cw:cw,vis:L>=sl-1&&R<=sl+cw+1,opts:document.querySelector("[data-c18-nav]").selectedOptions[0].value});})()',
    (v) => { const o = JSON.parse(v); return o.vis && o.sl > 0 && o.opts === 'biochem_15'; });

  /* 5. 页面滚动后切远章 → window 不跳动 + chip 可见(自动滚动定位)
        注:html 有 scroll-behavior:smooth,scrollTo 为平滑动画,需等其落定后再读 scrollY */
  await step('滚动到页底(平滑滚动落定)', '(function(){window.scrollTo(0,99999);return 1;})()', (v) => v === 1);
  await sleep(900);
  await step('页底位置>0', 'window.scrollY', (v) => v > 0);
  await ev('window.__c18test_scrollY=window.scrollY');
  await step('下拉切换 biochem_36', '(function(){var s=document.querySelector("[data-c18-nav]");s.value="biochem_36";s.dispatchEvent(new Event("change",{bubbles:true}));return __qa.S.subject;})()', (v) => v === 'biochem_36');
  await sleep(300);
  await step('biochem_36 可见+页不跳+滚动近末尾', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth,sw=hb.scrollWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return JSON.stringify({sl:sl,L:L,R:R,cw:cw,sw:sw,vis:L>=sl-1&&R<=sl+cw+1,scrollY:window.scrollY,preY:window.__c18test_scrollY});})()',
    (v) => { const o = JSON.parse(v); return o.vis && o.scrollY === o.preY && o.sl >= o.sw - o.cw - 2; });

  /* 6. 点 chip(现有 select-chapter 路径)仍正常 + 下拉框选中跟随 + 不产生重复行 */
  await step('点击 chip biochem_20', '(function(){document.querySelector(".chapter-chip[data-key=biochem_20]").click();return __qa.S.subject;})()', (v) => v === 'biochem_20');
  await sleep(150);
  await assertEq('下拉选中跟随 chip', 'document.querySelector("[data-c18-nav]").selectedOptions[0].value', 'biochem_20');
  await step('renderHome 后下拉框唯一+仍在独立行', '(function(){var s=document.querySelector("[data-c18-nav]");var hb=document.querySelector("#view-home .hero-bottom");return JSON.stringify({count:document.querySelectorAll("[data-c18-nav]").length,rowPrev:hb.previousElementSibling===s.parentNode});})()',
    (v) => { const o = JSON.parse(v); return o.count === 1 && o.rowPrev; });

  /* 7. 切换科目 → 下拉框重建成细胞生物学 16 章 */
  await step('切换细胞科目', '(function(){document.querySelector("[data-action=switch-course][data-course=cellbiology]").click();return __qa.S.course;})()', (v) => v === 'cellbiology');
  await sleep(150);
  await step('细胞下拉选项数+首章选中', '(function(){var s=document.querySelector("[data-c18-nav]");return JSON.stringify({n:s.options.length,sel:s.selectedOptions[0].value,act:document.querySelector(".chapter-chip.active").getAttribute("data-key")});})()',
    (v) => { const o = JSON.parse(v); return o.n === 17 && o.sel === 'cellbio_1' && o.act === 'cellbio_1'; });
  await step('跳 cellbio_16 chip 可见', '(function(){var s=document.querySelector("[data-c18-nav]");s.value="cellbio_16";s.dispatchEvent(new Event("change",{bubbles:true}));return __qa.S.subject;})()', (v) => v === 'cellbio_16');
  await sleep(150);
  await step('cellbio_16 可见性', '(function(){var hb=document.querySelector("#view-home .hero-bottom");var c=hb.querySelector(".chapter-chip.active");var sl=hb.scrollLeft,cw=hb.clientWidth;var L=c.offsetLeft,R=L+c.offsetWidth;return L>=sl-1&&R<=sl+cw+1;})()', (v) => v === true);

  /* 8. 全部刷题路径 */
  await step('start-quiz', '(function(){document.querySelector("[data-action=start-quiz]").click();return JSON.stringify({view:__qa.S.view,mode:__qa.S.quizMode,n:__qa.S.questions.length,subject:__qa.S.subject});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'quiz' && o.mode === 'all' && o.n > 0 && o.subject === 'cellbio_16'; });
  await step('单题作答 submitAnswer', '(function(){var q=__qa.S.questions[0];var ans=(q.type==="truefalse")?"true":(q.type==="short")?"done":Object.keys(q.options)[0];__qa.submitAnswer(q.id,ans);return __qa.S.answers[__qa.ak(__qa.S.subject,q.id)]===ans;})()', (v) => v === true);

  /* 9. 多选路径 */
  await step('返回首页', '(function(){__qa.switchView("home");return __qa.S.view;})()', (v) => v === 'home');
  await sleep(150);
  await step('start-multi', '(function(){document.querySelector("[data-action=start-multi]").click();return JSON.stringify({view:__qa.S.view,mode:__qa.S.quizMode,n:__qa.S.questions.length});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'quiz' && o.mode === 'multi' && o.n > 0; });
  await sleep(150);
  await step('多选 toggle+confirm', '(function(){var q=__qa.S.questions[0];var tg=document.querySelector("[data-action=multi-toggle]");if(tg)tg.click();var sel=__qa.S._multiSelection&&__qa.S._multiSelection[q.id]?__qa.S._multiSelection[q.id].length:0;var cf=document.querySelector("[data-action=multi-confirm]");return JSON.stringify({sel:sel,hasConfirm:!!cf});})()',
    (v) => { const o = JSON.parse(v); return o.sel > 0 && o.hasConfirm === true; });

  /* 10. 名词解释路径 */
  await step('返回首页+名词解释', '(function(){__qa.switchView("home");return __qa.S.view;})()', (v) => v === 'home');
  await sleep(150);
  await step('start-noun', '(function(){document.querySelector("[data-action=start-noun]").click();return JSON.stringify({view:__qa.S.view,cards:document.querySelectorAll("#view-terms .term-card").length});})()',
    (v) => { const o = JSON.parse(v); return o.view === 'terms' && o.cards > 0; });

  /* 11. 错题/书签无异常 */
  await step('wrongQs/bmQs 可用', '(function(){return JSON.stringify({w:__qa.wrongQs().length,b:__qa.bmQs().length});})()', (v) => /^\{/.test(v));

  /* 12. JS 错误统计 */
  console.log('JS exceptions: ' + exceptions.length + ' | console errors: ' + consoleErrs.length);
  if (exceptions.length > 0) { fail('发现 JS 异常: ' + exceptions.join(' || ')); }
  if (consoleErrs.length > 0) { console.log('console errors detail: ' + consoleErrs.join(' || ')); }

  ws.close(); edge.kill();
  console.log(failed ? '===== RESULT: FAIL =====' : '===== RESULT: ALL PASS =====');
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.log('FATAL: ' + e); process.exit(1); });
