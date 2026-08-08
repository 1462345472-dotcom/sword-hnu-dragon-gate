/* R12 清除数据修复复测(clear-fix)
   聚焦验证:清除数据后 S.answers/S.revealed/_multiSelection/S.streak 内存清零、
   首页 UI 归零(0/105 题、ring 0%)、localStorage 无残留、再答一题正常、
   0 JS 错误、做题/多选/名词/书签/导出导入全路径正常。
   顺序:多选/名词冒烟 → 答2题造进度 → 清除 → 全零断言 → 再答1题 → 导出导入。
   用法: node _r12_clearfix_test.js */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9368;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-r12fix-'));
const downloadDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-r12fix-dl-'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let fails = 0;
const pass = (id, m) => console.log('PASS ' + id + ': ' + m);
const fail = (id, m) => { fails++; console.log('FAIL ' + id + ': ' + m); };
const info = (m) => console.log('  · ' + m);

function getJson(url) {
  return new Promise((res, rej) => {
    http.get(url, (r) => { let d = ''; r.on('data', (c) => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej);
  });
}

async function main() {
  const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--window-size=1100,900', '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile, URL],
    { stdio: 'ignore' });
  let targets = null;
  for (let i = 0; i < 80; i++) {
    try { targets = await getJson('http://127.0.0.1:' + PORT + '/json'); if (targets && targets.length) break; } catch (e) {}
    await sleep(500);
  }
  if (!targets) { console.error('Edge CDP not reachable'); process.exit(2); }
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
  let exceptions = [], consoleErrs = [];
  let dialogPolicy = 'dismiss';
  let lastDialogMsg = '';
  let pendingFilePath = null;
  let downloadEvents = [];
  ws.onmessage = (evt) => {
    const m = JSON.parse(evt.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method === 'Runtime.exceptionThrown') {
      const d = m.params.exceptionDetails;
      exceptions.push((d.exception && d.exception.description) || d.text || 'exception');
    } else if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') {
      consoleErrs.push(m.params.args.map((a) => a.value || a.description || '').join(' '));
    } else if (m.method === 'Page.javascriptDialogOpening') {
      lastDialogMsg = m.params.message || '';
      send('Page.handleJavaScriptDialog', { accept: dialogPolicy === 'accept' }).catch(() => {});
    } else if (m.method === 'Page.fileChooserOpened') {
      if (pendingFilePath && m.params.backendNodeId) {
        send('DOM.setFileInputFiles', { files: [pendingFilePath], backendNodeId: m.params.backendNodeId }).catch(() => {});
      }
    } else if (m.method === 'Browser.downloadWillBegin') {
      downloadEvents.push(m.params.suggestedFilename || '');
    }
  };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable'); await send('Page.enable'); await send('DOM.enable');
  await send('Browser.setDownloadBehavior', { behavior: 'allow', downloadPath: downloadDir, eventsEnabled: true });
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
  const click = async (sel) => ev(`(function(){var el=document.querySelector('${sel}');if(!el)return false;el.click();return true;})()`);
  for (let i = 0; i < 60; i++) { try { if (await ev('window.__qa?1:0') === 1) break; } catch (e) {} await sleep(500); }
  if (!(await ev('window.__qa?1:0'))) { console.error('__qa not ready'); process.exit(2); }

  /* ---- 进入首页、切章 ---- */
  await click('[data-action="enter"]'); await sleep(400);
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(300);

  /* ---- A. 多选冒烟(前置,避免 startQuiz 重置答题进度) ---- */
  await click('[data-action="start-multi"]'); await sleep(500);
  const mv = await ev(`(function(){var S=__qa.S;if(S.view!=='quiz')return null;var q=S.questions[S.qIndex];return q&&q.type==='multi'?Object.keys(q.options).slice(0,2):null;})()`);
  if (!mv) { info('多选专项未进入 multi 题列表,跳过'); }
  else {
    await click('.option.multi-option[data-value="' + mv[0] + '"]'); await sleep(300);
    await click('.option.multi-option[data-value="' + mv[1] + '"]'); await sleep(300);
    const msel = await ev(`(function(){var S=__qa.S;var k=Object.keys(S._multiSelection||{});return {keys:k,sel:k.length?S._multiSelection[k[0]]:[]};})()`);
    if (msel.keys.length > 0 && msel.sel.length === 2) pass('A1', '多选路径: _multiSelection=' + JSON.stringify(msel.sel));
    else fail('A1', '多选路径异常: ' + JSON.stringify(msel));
  }
  await click('[data-action="go-home"]'); await sleep(400);

  /* ---- B. 名词抽背冒烟 ---- */
  await click('[data-action="start-noun"]'); await sleep(400);
  const nounView = await ev('__qa.S.view');
  if (nounView === 'terms') pass('B1', '名词抽背路径: 视图切换至 terms');
  else fail('B1', '名词抽背视图异常: ' + nounView);
  await click('[data-action="go-home"]'); await sleep(400);

  /* ---- C. 做题:答对 Q1、答错 Q2、收藏 Q2 ---- */
  await click('[data-action="start-quiz"]'); await sleep(500);
  let qi = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];return {id:q.id,type:q.type,answer:q.answer};})()`);
  if (qi.type !== 'choice') fail('C1', '第一题非单选题: ' + JSON.stringify(qi)); else pass('C1', '进入刷题,第一题 type=' + qi.type);
  await click('.option[data-value="' + qi.answer + '"]'); await sleep(400);   // 答对
  let stA = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,rev:Object.keys(S.revealed).length,streak:S.streak};})()`);
  if (stA.ans === 1 && stA.rev === 1 && stA.streak === 1) pass('C2', '答对第1题: answers=1 revealed=1 streak=1');
  else fail('C2', '答对第1题状态异常: ' + JSON.stringify(stA));
  await click('[data-action="nav-next"]'); await sleep(300);
  const wrongOpt = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wrongOpt + '"]'); await sleep(400);    // 答错
  await click('[data-action="toggle-bookmark"]'); await sleep(300);           // 收藏
  stA = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,streak:S.streak,best:S.bestStreak,sp:Object.keys(S.savedProgress).length};})()`);
  if (stA.ans === 2 && stA.wrong === 1 && stA.bm === 1 && stA.streak === 0 && stA.best === 1 && stA.sp >= 1)
    pass('C3', '答错第2题+收藏: answers=2 wrong=1 bm=1 best=1 sp=' + stA.sp);
  else fail('C3', '答错第2题状态异常: ' + JSON.stringify(stA));
  await click('[data-action="go-home"]'); await sleep(400);

  /* ---- D. 清除前状态快照(应显示已练 2/105) ---- */
  const before = await ev(`(function(){var S=__qa.S;var ring=document.getElementById('ringNum');var pi=document.querySelector('.pi-stats');return {ans:Object.keys(S.answers).length,rev:Object.keys(S.revealed||{}).length,msel:Object.keys(S._multiSelection||{}).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,sp:Object.keys(S.savedProgress).length,streak:S.streak,best:S.bestStreak,ach:Object.keys(S.achievements).length,ring:ring?ring.textContent:null,pi:pi?pi.textContent:null};})()`);
  info('清除前: ' + JSON.stringify(before));
  if (before.ans === 2 && before.pi && before.pi.indexOf('2/105') >= 0)
    pass('D1', '清除前首页显示进度: pi="' + before.pi + '"');
  else fail('D1', '清除前状态异常: ' + JSON.stringify(before));

  /* ---- E. 清除数据(确认) ---- */
  await ev(`(function(){var b=document.createElement('button');b.id='qaClearBtn';b.setAttribute('data-action','clear-data');b.style.display='none';document.getElementById('app').appendChild(b);return true;})()`);
  dialogPolicy = 'accept';
  await click('#qaClearBtn'); await sleep(600);
  dialogPolicy = 'dismiss';
  const dlg = lastDialogMsg;

  /* ---- F. 清除后:内存 + UI + localStorage ---- */
  const after = await ev(`(function(){var S=__qa.S;var ring=document.getElementById('ringNum');var pi=document.querySelector('.pi-stats');var bad=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf('hnu_academy_prog_')===0||k.indexOf('hnu_academy_wrong_')===0||k.indexOf('hnu_academy_bm_')===0||k==='hnu_academy_s'||k==='hnu_academy_progress'||k==='hnu_academy_total')bad.push(k);}var t=document.querySelector('.toast');return {ans:Object.keys(S.answers).length,rev:Object.keys(S.revealed||{}).length,msel:Object.keys(S._multiSelection||{}).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,sp:Object.keys(S.savedProgress).length,streak:S.streak,best:S.bestStreak,ach:Object.keys(S.achievements).length,ring:ring?ring.textContent:null,pi:pi?pi.textContent:null,lsBad:bad,toast:t?t.textContent:null,view:S.view};})()`);
  info('清除后: ' + JSON.stringify(after));
  const zero = after.ans === 0 && after.rev === 0 && after.msel === 0 && after.wrong === 0 && after.bm === 0 && after.sp === 0 && after.streak === 0 && after.best === 0 && after.ach === 0;
  if (zero && after.lsBad.length === 0)
    pass('F1', '清除数据: answers/revealed/_multiSelection/streak/wrong/bm/best/ach/sp 内存全零, 无 prog/wrong/bm/total 存储残留');
  else fail('F1', '清除不彻底: ' + JSON.stringify({st: after, badKeys: after.lsBad}));
  if (dlg.indexOf('清除') >= 0) pass('F2', '确认弹窗文案: ' + dlg);
  else fail('F2', '确认弹窗未触发或文案异常: ' + dlg);
  if (after.pi && after.pi.indexOf('0/105') >= 0 && after.ring === '0%')
    pass('F3', '首页归零: pi="' + after.pi + '" ring=' + after.ring);
  else fail('F3', '首页未归零: pi=' + after.pi + ' ring=' + after.ring);
  if (after.toast && after.toast.indexOf('数据已清除') >= 0) pass('F4', '清除 toast: ' + after.toast);
  else fail('F4', '清除 toast 缺失: ' + after.toast);
  await ev('(function(){var b=document.getElementById(' + JSON.stringify('qaClearBtn') + ');if(b)b.remove();return true;})()');

  /* ---- G. 再答一题正常 ---- */
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];return {id:q.id,type:q.type,answer:q.answer};})()`);
  const qBefore = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,msel:Object.keys(S._multiSelection||{}).length};})()`);
  if (qBefore.ans !== 0) fail('G1', '重开刷题应零进度,实际 answers=' + qBefore.ans); else pass('G1', '清除后重开刷题: 零进度启动');
  await click('.option[data-value="' + qi.answer + '"]'); await sleep(400);
  const qAfter = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,rev:Object.keys(S.revealed).length,streak:S.streak,correct:document.querySelector('.option.correct')?'y':'n'};})()`);
  if (qAfter.ans === 1 && qAfter.rev === 1 && qAfter.streak === 1 && qAfter.correct === 'y')
    pass('G2', '再答一题正常: answers=1 revealed=1 streak=1 正确项高亮');
  else fail('G2', '再答一题异常: ' + JSON.stringify(qAfter));
  await click('[data-action="go-home"]'); await sleep(400);

  /* ---- H. 导出/导入路径 ---- */
  const btnCount = await ev(`(function(){var b=document.getElementById('hnuExpBar');return b?b.querySelectorAll('button').length:0;})()`);
  if (btnCount < 3) fail('H1', '导出栏按钮缺失: ' + btnCount); else pass('H1', '导出栏存在 (' + btnCount + ' 按钮)');
  await click('#hnuExpBar button:nth-child(1)'); await sleep(800);
  if (downloadEvents.length >= 1) pass('H2', '导出下载触发: ' + downloadEvents[0]);
  else fail('H2', '导出未触发下载事件');
  /* 导入:走真实导入代码路径(直接调用 __expimp.importData)+ fileChooser UI 注入冒烟 */
  const expJson = await ev(`(function(){var s=__qa.S;return JSON.stringify({type:'learning-data',data:{answers:s.answers,wrongSet:s.wrongSet,bookmarks:s.bookmarks,achievements:s.achievements,savedProgress:s.savedProgress,bestStreak:s.bestStreak,streak:s.streak,course:s.course,subject:s.subject,termFilter:s.termFilter}});})()`);
  const impRet = await ev(`(function(){var r=window.__expimp.importData(${JSON.stringify(expJson)});return {ok:!!(r&&r.ok),msg:r&&r.msg};})()`);
  const impState = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length};})()`);
  if (impRet.ok && impState.ans === 1 && impState.wrong === 0 && impState.bm === 0)
    pass('H3', '导入路径正常: ' + JSON.stringify(impRet) + ' → ' + JSON.stringify(impState));
  else fail('H3', '导入异常: ' + JSON.stringify(impRet) + ' state=' + JSON.stringify(impState));
  const impFile = path.join(os.tmpdir(), 'hnu-r12fix-import.json');
  fs.writeFileSync(impFile, expJson, 'utf8');
  pendingFilePath = impFile;
  await click('#hnuExpBar button:nth-child(2)'); await sleep(1000);
  pendingFilePath = null;
  const chooserToast = await ev(`(function(){var t=document.querySelector('.toast');return t?t.textContent:null;})()`);
  info('fileChooser 注入冒烟 toast: ' + chooserToast);

  /* ---- I. 0 JS 错误 ---- */
  if (exceptions.length === 0 && consoleErrs.length === 0) pass('I1', '全程 0 JS 异常 / 0 console error');
  else fail('I1', 'JS 异常: ' + JSON.stringify({exceptions: exceptions.slice(0, 3), consoleErrs: consoleErrs.slice(0, 3)}));

  console.log('==== RESULT: ' + (fails === 0 ? 'PASS' : 'FAIL (' + fails + ')') + ' ====');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(fails === 0 ? 0 : 1);
}
main().catch((e) => { console.error(e); process.exit(2); });
