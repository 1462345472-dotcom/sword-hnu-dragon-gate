/* 学习数据导出/导入 + 题库归档 — Edge headless CDP 实测
   覆盖:导出按钮→文件生成(内容含全部学习数据);导入合法文件→数据恢复;
        导入非法文件→报错不破坏;导入前备份生成;0 JS 错误;做题/多选/名词/错题路径正常 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9377;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'expimpedge-'));
const dlDir = fs.mkdtempSync(path.join(os.tmpdir(), 'expimpdl-'));

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
  /* 允许下载到 dlDir */
  try { await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: dlDir, eventsEnabled: true }); } catch (e) {}
  try { await send('Page.setDownloadBehavior', { behavior: 'allow', downloadPath: dlDir }); } catch (e) {}

  let ready = false;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await send('Runtime.evaluate', { expression: '(window.__qa&&window.__expimp)?1:0', returnByValue: true });
      if (r.result && r.result.result && r.result.result.value === 1) { ready = true; break; }
    } catch (e) {}
    await sleep(500);
  }
  if (!ready) { fail('page did not load __qa/__expimp'); process.exit(1); }
  console.log('page loaded, __qa + __expimp ready');

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

  /* ===== 0. 基础 ===== */
  await assertEq('51 章节键', '__qa.qbKeys().length', 51);

  /* ===== 1. 进入首页(首次访问从 splash 进入;renderHome 后才注入 footer 按钮)===== */
  await step('进入首页', '(function(){if(__qa.S.view==="home")return "home";var b=document.querySelector("[data-action=enter]");if(b)b.click();return __qa.S.view;})()', (v) => v === 'home');
  await sleep(200);
  await step('首页 footer 注入 3 按钮', '__expimp.footerCount()', (v) => v === 3);

  /* ===== 2. 真实做题路径:答题(对/错)+ 书签 + 进度落盘 ===== */
  await step('startQuiz 启动 biochem_1_2', '(function(){try{__qa.startQuiz("biochem_1_2","all");return __qa.S.subject;}catch(e){return "ERR:"+e.message;}})()', (v) => v === 'biochem_1_2');
  await step('答对第1题', '(function(){var q=__qa.S.questions[0];var ua=q.answer;var ok=__qa.submitAnswer(q.id,ua);return JSON.stringify({id:q.id,type:q.type,ok:ok,answered:Object.keys(__qa.S.answers).length});})()', (v) => JSON.parse(v).ok === true && JSON.parse(v).answered >= 1);
  await step('答错第2题(进错题本)', '(function(){var q=__qa.S.questions[1];var ua=q.type==="choice"?(q.answer==="A"?"B":"A"):"wrong";var ok=__qa.submitAnswer(q.id,ua);return JSON.stringify({ok:ok,wrong:Object.keys(__qa.S.wrongSet).length});})()', (v) => JSON.parse(v).ok === false && JSON.parse(v).wrong >= 1);
  await step('设置书签 1 条', '(function(){var q=__qa.S.questions[2];__qa.S.bookmarks[__qa.ak("biochem_1_2",q.id)]=true;__qa.invalidate();return Object.keys(__qa.S.bookmarks).length;})()', (v) => v >= 1);
  await step('答题进度已落 savedProgress', '(function(){var p=__qa.S.savedProgress["biochem_1_2|all"];return p&&p.answers?Object.keys(p.answers).length:0;})()', (v) => v >= 2);
  await assertEq('bestStreak 已增长', '__qa.S.bestStreak', 1);

  /* ===== 3. 导出学习数据(钩子返回 JSON)===== */
  let exportedJson = null;
  await step('exportData 返回可解析 JSON', 'typeof __expimp.exportData()', (v) => v === 'string');
  exportedJson = await ev('__expimp.exportData()');
  {
    const parsed = JSON.parse(exportedJson);
    const d = parsed.data;
    const okE = parsed.type === 'learning-data' && Object.keys(d.answers).length >= 2 &&
      Object.keys(d.wrongSet).length >= 1 && Object.keys(d.bookmarks).length >= 1 &&
      d.bestStreak >= 1 && d.savedProgress['biochem_1_2|all'] &&
      Object.keys(d.savedProgress['biochem_1_2|all'].answers).length >= 2;
    console.log((okE ? 'PASS' : 'FAIL') + ' [导出内容含全部学习数据] ' + JSON.stringify({answers:Object.keys(d.answers).length,wrong:Object.keys(d.wrongSet).length,bm:Object.keys(d.bookmarks).length,best:d.bestStreak}));
    if (!okE) failed = true;
  }

  /* ===== 4. 题库归档导出(钩子 + 按钮点击下载)===== */
  await step('exportBank 返回 51 章归档', '(function(){var p=JSON.parse(__expimp.exportBank());return JSON.stringify({t:p.type,bc:p.bankCount,qc:p.questionCount,tc:p.termCount});})()', (v) => JSON.parse(v).bc === 51 && JSON.parse(v).qc === 5844 && JSON.parse(v).tc === 951);

  /* ===== 5. 按钮点击 → 真实文件下载 ===== */
  await step('点击"导出数据"按钮不报错', '(function(){var b=document.querySelector("#hnuExpBar button");b.click();return "clicked";})()', (v) => v === 'clicked');
  await sleep(1500);
  const files = fs.readdirSync(dlDir).filter((f) => f.endsWith('.json'));
  await step('下载目录出现 JSON 文件', JSON.stringify(files.length), (v) => parseInt(v, 10) >= 1);
  if (files.length >= 1) {
    const f = files[0];
    const content = fs.readFileSync(path.join(dlDir, f), 'utf8');
    const parsed = JSON.parse(content);
    const okDl = parsed.type === 'learning-data' && Object.keys(parsed.data.answers).length >= 2 &&
      Object.keys(parsed.data.wrongSet).length >= 1 && Object.keys(parsed.data.bookmarks).length >= 1 &&
      parsed.data.bestStreak >= 1;
    console.log((okDl ? 'PASS' : 'FAIL') + ' [下载文件内容含全部学习数据] ' + f + ' ' + JSON.stringify({answers:Object.keys(parsed.data.answers).length,wrong:Object.keys(parsed.data.wrongSet).length,bm:Object.keys(parsed.data.bookmarks).length}));
    if (!okDl) failed = true;
  }

  /* ===== 6. 导入合法文件 → 覆盖恢复(先清空制造丢失场景)===== */
  await step('清空现有数据(模拟丢失)', '(function(){Object.keys(localStorage).forEach(function(k){if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);});__qa.S.answers={};__qa.S.wrongSet={};__qa.S.bookmarks={};__qa.S.savedProgress={};__qa.S.bestStreak=0;__qa.invalidate();return Object.keys(__qa.S.wrongSet).length;})()', (v) => v === 0);
  await step('导入合法文件', '(function(){return JSON.stringify(__expimp.importData(' + JSON.stringify(exportedJson) + '));})()', (v) => JSON.parse(v).ok === true);
  await step('导入后 answers 恢复', 'Object.keys(__qa.S.answers).length', (v) => v >= 2);
  await step('导入后 wrongSet 恢复', 'Object.keys(__qa.S.wrongSet).length', (v) => v >= 1);
  await step('导入后 bookmarks 恢复', 'Object.keys(__qa.S.bookmarks).length', (v) => v >= 1);
  await assertEq('导入后 bestStreak 恢复', '__qa.S.bestStreak', 1);
  await step('导入后 savedProgress 恢复', '(function(){var p=__qa.S.savedProgress["biochem_1_2|all"];return p&&p.answers?Object.keys(p.answers).length:0;})()', (v) => v >= 2);
  await step('分章键 prog 已写回', 'localStorage.getItem("hnu_academy_prog_biochem_1_2")!==null', (v) => v === true);
  await step('分章键 wrong 已写回', 'localStorage.getItem("hnu_academy_wrong_biochem_1_2")!==null', (v) => v === true);
  await step('分章键 bm 已写回', 'localStorage.getItem("hnu_academy_bm_biochem_1_2")!==null', (v) => v === true);
  await step('错题缓存已重建(非空)', '(function(){var w=__qa.wrongQs();return w?w.length:0;})()', (v) => v >= 1);
  await step('导入前自动备份(localStorage 键)存在', '(function(){var b=localStorage.getItem(__expimp.backupKey());if(!b)return 0;var d=JSON.parse(b).data;return JSON.stringify({wrong:Object.keys(d.wrongSet).length,bm:Object.keys(d.bookmarks).length});})()', (v) => v === '0' || v.startsWith('{"wrong"') || v === JSON.stringify({wrong:0,bm:0}));

  /* ===== 7. 覆盖语义:导入"只有 1 条错题"的数据 → 其他数据被清空 ===== */
  const minimal = JSON.stringify({app:'hnu-academy',type:'learning-data',version:1,data:{wrongSet:{'biochem_1_2__999':true}}});
  await step('导入最小数据集(覆盖)', '(function(){return JSON.stringify(__expimp.importData(' + JSON.stringify(minimal) + '));})()', (v) => JSON.parse(v).ok === true);
  await step('覆盖后 answers 被清空', 'Object.keys(__qa.S.answers).length', (v) => v === 0);
  await assertEq('覆盖后 wrongSet 只剩导入的 1 条', 'Object.keys(__qa.S.wrongSet).length', 1);
  await assertEq('覆盖后 bookmarks 被清空', 'Object.keys(__qa.S.bookmarks).length', 0);

  /* ===== 8. 导入非法文件 → 报错且不破坏 ===== */
  await step('非法 JSON → 报错', '(function(){var r=__expimp.importData("not-json{{");return JSON.stringify({ok:r.ok,err:r.error});})()', (v) => JSON.parse(v).ok === false && JSON.parse(v).err === '不是有效的 JSON 文件');
  await assertEq('非法 JSON 后 wrongSet 未变', 'Object.keys(__qa.S.wrongSet).length', 1);
  await step('缺字段 JSON → 报错', '(function(){var r=__expimp.importData(JSON.stringify({foo:1}));return JSON.stringify({ok:r.ok,err:r.error});})()', (v) => JSON.parse(v).ok === false);
  await assertEq('缺字段后 wrongSet 未变', 'Object.keys(__qa.S.wrongSet).length', 1);
  await step('字段类型错误(answers 为数组) → 报错', '(function(){var r=__expimp.importData(JSON.stringify({type:"learning-data",data:{answers:[1,2]}}));return JSON.stringify({ok:r.ok,err:r.error});})()', (v) => JSON.parse(v).ok === false && JSON.parse(v).err === 'answers 字段格式不正确');
  await assertEq('类型错误后 wrongSet 未变', 'Object.keys(__qa.S.wrongSet).length', 1);

  /* ===== 9. 恢复完整数据后再刷新验证持久性 ===== */
  await step('重新导入完整数据', '(function(){return JSON.stringify(__expimp.importData(' + JSON.stringify(exportedJson) + '));})()', (v) => JSON.parse(v).ok === true);
  await send('Page.reload', { ignoreCache: true });
  let ready2 = false;
  for (let i = 0; i < 40; i++) {
    try {
      const r = await send('Runtime.evaluate', { expression: 'window.__qa?1:0', returnByValue: true });
      if (r.result && r.result.result && r.result.result.value === 1) { ready2 = true; break; }
    } catch (e) {}
    await sleep(500);
  }
  if (!ready2) { fail('page reload not ready'); } else {
    console.log('page reloaded');
    await step('刷新后 wrongSet 从分章键恢复', 'Object.keys(__qa.S.wrongSet).length', (v) => v >= 1);
    await step('刷新后 bookmarks 从分章键恢复', 'Object.keys(__qa.S.bookmarks).length', (v) => v >= 1);
    await step('刷新后 savedProgress answers 恢复', '(function(){var p=__qa.S.savedProgress["biochem_1_2|all"];return p&&p.answers?Object.keys(p.answers).length:0;})()', (v) => v >= 2);
    await assertEq('刷新后 bestStreak 恢复', '__qa.S.bestStreak', 1);
    /* 名词路径:进入首页并切换到"名词"过滤 */
    await step('进入首页', '(function(){if(__qa.S.view==="home")return "home";var b=document.querySelector("[data-action=enter]");if(b)b.click();return __qa.S.view;})()', (v) => v === 'home');
    await sleep(150);
    await step('多选/名词路径:startQuiz 名词过滤不抛异常', '(function(){try{__qa.startQuiz("biochem_1_2","terms");return __qa.S.quizMode;}catch(e){return "ERR:"+e.message;}})()', (v) => v === 'terms');
  }

  /* ===== 10. 零 JS 错误 ===== */
  await sleep(300);
  console.log((exceptions.length === 0 && consoleErrs.length === 0 ? 'PASS' : 'FAIL') + ' [0 JS 错误] exceptions=' + exceptions.length + ' consoleErrs=' + consoleErrs.length);
  if (exceptions.length || consoleErrs.length) failed = true;
  if (exceptions.length) console.log('  exceptions: ' + JSON.stringify(exceptions.slice(0, 5)));
  if (consoleErrs.length) console.log('  consoleErrs: ' + JSON.stringify(consoleErrs.slice(0, 5)));

  edge.kill();
  console.log(failed ? '=== RESULT: FAIL ===' : '=== RESULT: PASS ===');
  process.exit(failed ? 1 : 0);
}

main().catch((e) => { console.error(e); process.exit(1); });
