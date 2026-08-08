/* ============================================================
   湖南大学题库 · 臻至版 启用前全路径回归(最终验收)
   通过 Edge headless CDP 真实 DOM 点击驱动,只读测试(不改 HTML)
   覆盖 R1~R13:加载/首页/切章/做题/多选/答题卡/名词/错题本/书签/导出导入/结果统计/清除/持久化
   输出: _reg_results.json (PASS/FAIL 清单 + 证据)
============================================================ */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9365;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-reg-'));
const downloadDir = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-dl-'));

const results = [];
let failedCount = 0;
const pass = (id, m) => { results.push({id, ok: true,  m}); console.log('PASS ' + id + ': ' + m); };
const fail = (id, m) => { failedCount++; results.push({id, ok: false, m}); console.log('FAIL ' + id + ': ' + m); };
const info = (m) => console.log('  · ' + m);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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
  let dialogPolicy = 'dismiss';            // 'dismiss' | 'accept' (Page.handleJavaScriptDialog)
  let lastDialogMsg = '';
  let pendingFilePath = null;              // 待注入的导入文件路径
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

  const ev = async (expr) => {
    const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (r.result && r.result.exceptionDetails) { info('EVAL-ERR: ' + expr.slice(0, 120) + ' :: ' + (r.result.exceptionDetails.exception && r.result.exceptionDetails.exception.description || r.result.exceptionDetails.text)); }
    return r.result && r.result.result ? r.result.result.value : undefined;
  };
  const click = async (sel) => ev(`(function(){var el=document.querySelector('${sel}');if(!el)return false;el.click();return true;})()`);
  const clickText = async (rootSel, txt) => ev(`(function(){var root=document.querySelector('${rootSel}');if(!root)return false;var els=root.querySelectorAll('*');for(var i=0;i<els.length;i++){if(els[i].textContent.trim()===${JSON.stringify(txt)}&&els[i].children.length===0){els[i].click();return true;}}return false;})()`);
  const reload = async () => { await send('Page.reload'); await sleep(2600); };

  const ready = () => ev('window.__qa?1:0');
  const state = () => ev(`(function(){var S=__qa.S;return {view:S.view,subject:S.subject,index:S.qIndex,mode:S.quizMode,qCount:(S.questions?S.questions.length:0),ans:Object.keys(S.answers).length,revealed:Object.keys(S.revealed||{}).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,sp:Object.keys(S.savedProgress).length,streak:S.streak,best:S.bestStreak,termFilter:S.termFilter,course:S.course};})()`);
  const qinfo = () => ev(`(function(){var S=__qa.S;var q=S.questions[S.qIndex];if(!q)return null;return {id:q.id,type:q.type,answer:String(q.answer),bmSubj:q._bmSubj||null};})()`);
  const bankStat = () => ev(`(function(){var ks=__qa.qbKeys();var q=0,t=0;for(var i=0;i<ks.length;i++){var b=__qa.getBank(ks[i]);q+=(b.questions||[]).length;t+=(b.terms||[]).length;}return {chapters:ks.length,questions:q,terms:t};})()`);
  const wrongIds = () => ev(`__qa.wrongQs().map(function(q){return (q._bmSubj||__qa.S.subject)+'__'+q.id;})`);
  const bmIds = () => ev(`__qa.bmQs().map(function(q){return (q._bmSubj||__qa.S.subject)+'__'+q.id;})`);

  const toHome = async () => {
    const v = await ev('__qa.S.view');
    if (v === 'splash') { await click('[data-action="enter"]'); await sleep(350); }
    else { await click('[data-action="go-home"]'); await sleep(350); }
  };
  const selectChapter = async (ch) => {
    await toHome();
    await click('.chapter-chip[data-key="' + ch + '"]'); await sleep(300);
  };
  const startQuizCard = async (action) => {
    await toHome();
    await click('[data-action="' + action + '"]'); await sleep(500);
  };
  const resetAll = async () => {
    dialogPolicy = 'dismiss';
    await ev('try{for(var i=localStorage.length-1;i>=0;i--){var k=localStorage.key(i);if(k.indexOf("hnu_academy_")===0)localStorage.removeItem(k);}}catch(e){};location.reload();');
    await sleep(2600);
  };

  /* ---------- 等待就绪 ---------- */
  let ok = false;
  for (let i = 0; i < 60; i++) { try { if (await ready() === 1) { ok = true; break; } } catch (e) {} await sleep(500); }
  if (!ok) { fail('R1', '应用未就绪 (window.__qa 不可用)'); process.exit(1); }

  /* ============================================================
     R1 加载
  ============================================================ */
  console.log('===== R1 加载 =====');
  const bs = await bankStat();
  if (bs.chapters === 51 && bs.questions === 5844) pass('R1', '数据加载: 51 章 / ' + bs.questions + ' 题 / ' + bs.terms + ' 术语');
  else fail('R1', '数据规模不符: ' + JSON.stringify(bs));
  const v0 = await ev('__qa.S.view');
  if (v0 === 'splash' || v0 === 'home') pass('R1', '首屏视图正常 (view=' + v0 + ')');
  else fail('R1', '首屏视图异常 view=' + v0);

  /* ============================================================
     R2 首页:进度区 + 模块卡
  ============================================================ */
  console.log('===== R2 首页 =====');
  await toHome();
  const homeEls = await ev(`(function(){return {ring:!!document.getElementById('ringNum'),pi:!!document.querySelector('.progress-info .pi-stats'),cards:[].map.call(document.querySelectorAll('.module-card'),function(c){return c.getAttribute('data-action');}),expBar:document.querySelectorAll('#hnuExpBar button').length,chips:document.querySelectorAll('.chapter-chip').length,tags:[].map.call(document.querySelectorAll('.brand-tag'),function(t){return t.getAttribute('data-course');})};})()`);
  info('home: ' + JSON.stringify(homeEls));
  if (homeEls.ring && homeEls.pi) pass('R2', '进度区渲染 (ringNum + pi-stats)');
  else fail('R2', '进度区缺失: ' + JSON.stringify({ring: homeEls.ring, pi: homeEls.pi}));
  const needCards = ['start-quiz', 'start-multi', 'start-short', 'start-noun', 'start-wrong', 'start-bookmarked'];
  const missing = needCards.filter((a) => homeEls.cards.indexOf(a) < 0);
  if (missing.length === 0) pass('R2', '6 张模块卡存在: ' + needCards.join('/'));
  else fail('R2', '模块卡缺失: ' + missing.join(','));
  if (homeEls.expBar === 3) pass('R2', '导出/导入按钮栏 (3 按钮) 存在');
  else fail('R2', '导出/导入按钮栏数量=' + homeEls.expBar);
  if (homeEls.chips === 35 && homeEls.tags.indexOf('biochemistry') >= 0 && homeEls.tags.indexOf('cellbiology') >= 0)
    pass('R2', '章节 chip 35 个 (生化36编号含合并1+2章) + 课程标签 2 个渲染');
  else fail('R2', 'chip/课程标签渲染异常: ' + JSON.stringify({chips: homeEls.chips, tags: homeEls.tags}));

  /* 模块卡可点(在 biochem_10 上,该章 4 题型齐全) */
  await selectChapter('biochem_10');
  await startQuizCard('start-quiz');
  let st = await state();
  if (st.view === 'quiz' && st.subject === 'biochem_10' && st.qCount > 0) pass('R2', '全部刷题卡可点 → quiz 视图 (' + st.qCount + ' 题)');
  else fail('R2', '全部刷题卡点击异常: ' + JSON.stringify(st));
  await toHome();
  await startQuizCard('start-multi');
  st = await state();
  if (st.view === 'quiz') pass('R2', '多选专项卡可点 → quiz (题型过滤 multi)');
  else fail('R2', '多选专项卡点击异常 view=' + st.view);
  await toHome();
  await startQuizCard('start-short');
  st = await state();
  if (st.view === 'quiz') pass('R2', '简答模板卡可点 → quiz (题型过滤 short)');
  else fail('R2', '简答模板卡点击异常 view=' + st.view);
  await toHome();
  await startQuizCard('start-noun');
  st = await state();
  if (st.view === 'terms') pass('R2', '名词解释卡可点 → terms 视图');
  else fail('R2', '名词解释卡点击异常 view=' + st.view);
  /* 错题/精选:先制造一条错题 + 一条书签,再点卡片 */
  await toHome();
  await click('.chapter-chip[data-key="biochem_10"]'); await sleep(300);
  await click('[data-action="start-quiz"]'); await sleep(500);
  let qi = await qinfo();
  const wrongOpt = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wrongOpt + '"]'); await sleep(350);
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  await toHome();
  await click('[data-action="start-wrong"]'); await sleep(500);
  st = await state();
  if (st.view === 'quiz' && st.qCount === 1) pass('R2', '错题精炼卡可点 → 错题 1 题进入 quiz');
  else fail('R2', '错题精炼卡点击异常: ' + JSON.stringify(st));
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  st = await state();
  if (st.view === 'quiz' && st.qCount === 1) pass('R2', '精选习题卡可点 → 书签 1 题进入 quiz');
  else fail('R2', '精选习题卡点击异常: ' + JSON.stringify(st));
  await toHome();
  /* 注:本版 UI 为 6 模块卡(选择专项/判断专项并入题型过滤),无独立 8 卡 */
  info('note: 选择专项/判断专项无独立卡片(并入全部刷题+题型过滤),6 卡全可点');

  /* ============================================================
     R3 章节切换:chip 点击 / chip 自动滚动定位 / 切课程
  ============================================================ */
  console.log('===== R3 章节切换 =====');
  await selectChapter('biochem_5');
  st = await state();
  const act5 = await ev(`!!document.querySelector('.chapter-chip.active[data-key="biochem_5"]')`);
  if (st.subject === 'biochem_5' && act5) pass('R3', 'chip 点击选中 biochem_5 (active 类正确)');
  else fail('R3', 'chip 点击异常: ' + JSON.stringify(st) + ' act5=' + act5);
  /* chip 自动滚动:点最后一章,active chip 应被滚动进可视区 */
  await selectChapter('biochem_36');
  const scroll = await ev(`(function(){var hb=document.querySelector('.hero-bottom');var chip=hb?hb.querySelector('.chapter-chip.active'):null;if(!hb||!chip)return null;var hr=hb.getBoundingClientRect(),cr=chip.getBoundingClientRect();return {scrollable:hb.scrollWidth>hb.clientWidth+2,scrollLeft:hb.scrollLeft,chipInView:(cr.left>=hr.left-2&&cr.right<=hr.right+2),crLeft:Math.round(cr.left),crRight:Math.round(cr.right),hbLeft:Math.round(hr.left),hbRight:Math.round(hr.right)};})()`);
  info('chip scroll: ' + JSON.stringify(scroll));
  if (scroll && ((scroll.scrollable && scroll.scrollLeft > 0) || scroll.chipInView))
    pass('R3', 'chip 自动滚动定位: 选中 biochem_36 后 ' + (scroll.scrollLeft > 0 ? 'scrollLeft=' + scroll.scrollLeft : 'chip 已在可视区'));
  else fail('R3', 'chip 滚动定位失败: ' + JSON.stringify(scroll));
  /* 切课程 → 细胞生物学 */
  await click('.brand-tag[data-course="cellbiology"]'); await sleep(350);
  st = await state();
  const chipsCell = await ev(`(function(){var hb=document.querySelector('.hero-bottom');if(!hb)return 0;return hb.querySelectorAll('.chapter-chip').length;})()`);
  if (st.course === 'cellbiology' && st.subject === 'cellbio_1' && chipsCell === 16)
    pass('R3', '切课程 → cellbiology: subject=cellbio_1, chip 列表 16 章');
  else fail('R3', '切课程异常: ' + JSON.stringify(st) + ' chips=' + chipsCell);
  /* 切回生化 */
  await click('.brand-tag[data-course="biochemistry"]'); await sleep(350);
  st = await state();
  if (st.course === 'biochemistry' && st.subject === 'biochem_1_2') pass('R3', '切回 biochemistry: subject 恢复 biochem_1_2');
  else fail('R3', '切回课程异常: ' + JSON.stringify(st));

  /* ============================================================
     R4 做题全流程:choice / truefalse / short(+ R6 答题卡、R5 多选)
  ============================================================ */
  console.log('===== R4 做题全流程 =====');
  await resetAll();
  await toHome();
  /* ---- R4a choice 答错 ---- */
  await selectChapter('biochem_10');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  if (qi.type !== 'choice') fail('R4', 'biochem_10 Q1 非 choice: ' + JSON.stringify(qi));
  else pass('R4', 'choice 题就绪 (Q1 type=choice)');
  const wOpt = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  const ans = qi.answer;
  await click('.option[data-value="' + wOpt + '"]'); await sleep(400);
  st = await state();
  let ui = await ev(`(function(){var c=document.querySelector('.option.correct');var w=document.querySelector('.option.wrong');return {correctVal:c?c.getAttribute('data-value'):null,wrongVal:w?w.getAttribute('data-value'):null,exp:!!document.querySelector('.explanation'),locked:document.querySelectorAll('.option.locked').length};})()`);
  info('choice 答错后: ' + JSON.stringify(ui) + ' state=' + JSON.stringify(st));
  if (ui.correctVal === String(ans) && ui.wrongVal === wOpt && ui.exp && st.wrong === 1)
    pass('R4', 'choice 答错判定: 正确项标绿/错选标红/解析展示/进错题本');
  else fail('R4', 'choice 答错判定异常: ' + JSON.stringify(ui) + ' ans=' + ans + ' wOpt=' + wOpt);
  /* 下一题按钮 */
  const idx0 = st.index;
  await click('[data-action="nav-next"]'); await sleep(350);
  st = await state();
  if (st.view === 'quiz' && st.index === idx0 + 1) pass('R4', '下一题按钮: qIndex ' + idx0 + ' → ' + st.index);
  else fail('R4', '下一题按钮异常: ' + JSON.stringify(st));
  /* ---- R4b truefalse 答对 ---- */
  /* 跳到第一个 truefalse 题(答题卡跳题顺带验证,详见 R6 再正式验证) */
  const tfIdx = await ev(`(function(){var qs=__qa.getBank('biochem_10').questions;for(var i=0;i<qs.length;i++)if(qs[i].type==='truefalse')return i;return -1;})()`);
  await click('[data-action="show-sheet"]'); await sleep(300);
  await click('.sheet-num[data-idx="' + tfIdx + '"]'); await sleep(400);
  qi = await qinfo();
  if (qi.type !== 'truefalse') fail('R4', '跳题到 truefalse 失败: ' + JSON.stringify(qi));
  else pass('R4', 'truefalse 题就绪 (第 ' + (tfIdx + 1) + ' 题, answer=' + qi.answer + ')');
  const tfAns = qi.answer; // 'true' / 'false'
  const tfWrong = tfAns === 'true' ? 'false' : 'true';
  /* 先答错看判定 */
  await click('.tf-btn[data-value="' + tfWrong + '"]'); await sleep(350);
  st = await state();
  let tfui = await ev(`(function(){var t=document.querySelector('.tf-btn.correct');var w=document.querySelector('.tf-btn.wrong');return {correctVal:t?t.getAttribute('data-value'):null,wrongVal:w?w.getAttribute('data-value'):null};})()`);
  if (tfui.correctVal === tfAns && tfui.wrongVal === tfWrong && st.wrong === 2)
    pass('R4', 'truefalse 答错判定: 正确侧标绿/错选侧标红');
  else fail('R4', 'truefalse 答错判定异常: ' + JSON.stringify(tfui) + ' state=' + JSON.stringify(st));
  /* 下一题后,跳到下一个 truefalse 并答对 → streak>0 */
  await click('[data-action="nav-next"]'); await sleep(300);
  await click('[data-action="show-sheet"]'); await sleep(250);
  const tf2Idx = await ev(`(function(){var qs=__qa.getBank('biochem_10').questions;var S=__qa.S;var found=0;for(var i=S.qIndex;i<qs.length;i++){if(qs[i].type==='truefalse'){if(i===S.qIndex)continue;if(found++===0)return i;}}return -1;})()`);
  await click('.sheet-num[data-idx="' + tf2Idx + '"]'); await sleep(400);
  qi = await qinfo();
  await click('.tf-btn[data-value="' + qi.answer + '"]'); await sleep(350);
  st = await state();
  if (st.streak === 1 && st.wrong === 2)
    pass('R4', 'truefalse 答对判定: streak=1, 错题数不变(未新增)');
  else fail('R4', 'truefalse 答对判定异常: ' + JSON.stringify(st));
  /* ---- R4c short ---- */
  await toHome();
  await click('[data-action="start-short"]'); await sleep(500);
  st = await state();
  if (st.view !== 'quiz' || st.mode !== 'short') fail('R4', 'short 模式启动异常: ' + JSON.stringify(st));
  qi = await qinfo();
  await click('[data-action="short-reveal"]'); await sleep(400);
  st = await state();
  let su = await ev(`(function(){return {reveal:!!document.querySelector('.short-answer-reveal'),btnGone:!document.querySelector('.short-reveal-btn')};})()`);
  const sa = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];return __qa.S.answers[__qa.S.subject+'__'+q.id];})()`);
  if (su.reveal && su.btnGone && sa === 'done' && st.streak >= 1 && st.wrong === 2)
    pass('R4', 'short 题: 显示答案按钮 → 自主评分 done, 参考答案展示, streak 累计');
  else fail('R4', 'short 题异常: ' + JSON.stringify(su) + ' sa=' + sa + ' state=' + JSON.stringify(st));
  const lastLabel = await ev(`(function(){var b=document.querySelector('[data-action="nav-next"]');return b?b.textContent.trim():null;})()`);
  if (lastLabel === '下一题') pass('R4', 'short 会话 第1题 按钮文案=下一题');
  else fail('R4', '按钮文案异常: ' + lastLabel);

  /* ============================================================
     R5 多选交互 (biochem_10, 8 道 multi)
  ============================================================ */
  console.log('===== R5 多选交互 =====');
  await toHome();
  await click('[data-action="start-multi"]'); await sleep(500);
  st = await state();
  if (st.view !== 'quiz' || st.mode !== 'multi') fail('R5', '多选会话启动异常: ' + JSON.stringify(st));
  qi = await qinfo();
  const ansChars = qi.answer.split('');
  const allChars = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];return Object.keys(q.options);})()`);
  /* 1) 未选择时确认按钮 disabled */
  const dis1 = await ev(`(function(){var b=document.querySelector('.multi-confirm-btn');return b?b.disabled:null;})()`);
  /* 2) 选一个 → 选中态 + 按钮可用 */
  await click('.option.multi-option[data-value="' + ansChars[0] + '"]'); await sleep(300);
  const dis2 = await ev(`(function(){var b=document.querySelector('.multi-confirm-btn');return b?b.disabled:null;})()`);
  const selCnt = await ev(`document.querySelectorAll('.option.multi-option.selected').length`);
  /* 3) 取消该选择(还原),再构建错误组合: 答案缺一字母 + 一个多余字母(若存在) */
  await click('.option.multi-option[data-value="' + ansChars[0] + '"]'); await sleep(250);
  const wrongSel = ansChars.slice(0, ansChars.length - 1);
  const extra = allChars.filter((c) => ansChars.indexOf(c) < 0)[0];
  if (extra) wrongSel.push(extra);
  else wrongSel.push(ansChars[0]);
  const wrongStr = wrongSel.slice().sort().join('');
  for (const c of wrongSel) {
    await click('.option.multi-option[data-value="' + c + '"]'); await sleep(200);
  }
  await sleep(250);
  const finalSel = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var m=__qa.S._multiSelection||{};return ((m[q.id]||[]).slice().sort().join(''));})()`);
  info('multi 选择过程: dis1=' + dis1 + ' dis2=' + dis2 + ' selCnt=' + selCnt + ' finalSel=' + finalSel + ' answer=' + qi.answer);
  if (dis1 === true && dis2 === false && selCnt >= 1)
    pass('R5', '多选选择交互: 空选时确认按钮禁用, 勾选后启用, 选中态渲染');
  else fail('R5', '多选按钮/选中态异常: dis1=' + dis1 + ' dis2=' + dis2 + ' selCnt=' + selCnt);
  if (finalSel === wrongStr) {
    await click('[data-action="multi-confirm"]'); await sleep(400);
    st = await state();
    let mui = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var opts=[].map.call(document.querySelectorAll('.option.multi-option'),function(o){return {v:o.getAttribute('data-value'),locked:o.classList.contains('locked'),correct:o.classList.contains('correct'),wrong:o.classList.contains('wrong')};});return {opts:opts,btnGone:!document.querySelector('.multi-confirm-btn'),selCleared:(__qa.S._multiSelection&&__qa.S._multiSelection[q.id])?true:false};})()`);
    const wrongMarked = mui.opts.filter((o) => o.wrong).map((o) => o.v);
    const correctMarked = mui.opts.filter((o) => o.correct).map((o) => o.v);
    if (mui.btnGone && st.wrong === 3 && wrongMarked.length >= 1 && correctMarked.length === ansChars.length && !mui.selCleared)
      pass('R5', '多选错误组合提交: 确认按钮消失/选项锁定/错选标红/正确项标绿/进错题本/缓存清理');
    else fail('R5', '多选错误组合提交异常: ' + JSON.stringify(mui) + ' state=' + JSON.stringify(st));
  } else {
    info('finalSel=' + finalSel + ' wrongStr=' + wrongStr + ' → 直接提交当前选择');
    await click('[data-action="multi-confirm"]'); await sleep(400);
    st = await state();
    if (st.wrong === 3) pass('R5', '多选错误组合提交(备选路径) 进错题本');
    else fail('R5', '多选提交异常: ' + JSON.stringify(st));
  }
  /* 4) 下一道多选, 全部勾选正确答案 → 答对, 不入错题本 */
  await click('[data-action="nav-next"]'); await sleep(300);
  qi = await qinfo();
  if (qi.type !== 'multi') fail('R5', '第2道非多选: ' + JSON.stringify(qi));
  for (const c of qi.answer.split('')) { await click('.option.multi-option[data-value="' + c + '"]'); await sleep(200); }
  await click('[data-action="multi-confirm"]'); await sleep(400);
  st = await state();
  if (st.wrong === 3 && st.streak >= 1)
    pass('R5', '多选全对提交: 判定正确, streak 累计, 未新增错题');
  else fail('R5', '多选全对提交异常: ' + JSON.stringify(st));

  /* ============================================================
     R6 答题卡:打开 / jump-to 跳题
  ============================================================ */
  console.log('===== R6 答题卡 =====');
  await click('[data-action="show-sheet"]'); await sleep(350);
  const sheet = await ev(`(function(){var s=document.getElementById('answerSheet');var g=document.getElementById('sheetGrid');if(!s||!g)return null;return {open:s.classList.contains('open'),cells:g.querySelectorAll('.sheet-num').length,title:document.getElementById('sheetTitle').textContent,total:__qa.S.questions.length};})()`);
  info('sheet: ' + JSON.stringify(sheet));
  if (sheet && sheet.open && sheet.cells === sheet.total)
    pass('R6', '答题卡打开: ' + sheet.title + ', 格子数=' + sheet.cells);
  else fail('R6', '答题卡异常: ' + JSON.stringify(sheet));
  /* jump-to 到第 4 格 (idx=3) */
  await click('.sheet-num[data-idx="3"]'); await sleep(400);
  st = await state();
  const sheetClosed = await ev(`(function(){var s=document.getElementById('answerSheet');return s?!(s.classList.contains('open')):true;})()`);
  if (st.view === 'quiz' && st.index === 3 && sheetClosed)
    pass('R6', 'jump-to 跳题: 点击第 4 格 → qIndex=3, 答题卡关闭');
  else fail('R6', 'jump-to 跳题异常: ' + JSON.stringify(st) + ' closed=' + sheetClosed);
  /* 已答格子应有 correct/wrong 状态类 */
  const cellStates = await ev(`(function(){var g=document.getElementById('sheetGrid');if(!g)return null;return [].map.call(g.querySelectorAll('.sheet-num'),function(c){return c.className;}).filter(function(c){return c.indexOf('correct-ans')>=0||c.indexOf('wrong-ans')>=0;}).length;})()`);
  info('答题卡已答状态格子数: ' + cellStates);

  /* ============================================================
     R7 名词解释:全部/各章 tab 过滤
  ============================================================ */
  console.log('===== R7 名词解释 =====');
  await toHome();
  await click('[data-action="start-noun"]'); await sleep(500);
  st = await state();
  if (st.view !== 'terms') fail('R7', '名词视图未打开: ' + JSON.stringify(st));
  const terms1 = await ev(`(function(){var hdr=document.querySelector('.list-header p');var cards=document.querySelectorAll('.term-card').length;var h=__qa.getBank(__qa.S.subject);return {hdr:hdr?hdr.textContent:null,cards:cards,bankTerms:(h&&h.terms?h.terms.length:0)};})()`);
  /* 先点击「全部」tab(termFilter 可能被前序场景保留为某章) */
  await click('.filter-tab[data-key="all"]'); await sleep(350);
  const terms1b = await ev(`(function(){var hdr=document.querySelector('.list-header p');var tabs=[].map.call(document.querySelectorAll('.filter-tab'),function(t){return {k:t.getAttribute('data-key'),act:t.classList.contains('active')};});var cards=document.querySelectorAll('.term-card').length;var h=__qa.getBank(__qa.S.subject);return {hdr:hdr?hdr.textContent:null,cards:cards,bankTerms:(h&&h.terms?h.terms.length:0),tabs:tabs};})()`);
  info('terms(all): ' + JSON.stringify(terms1) + ' → ' + JSON.stringify(terms1b));
  const allTab = terms1b.tabs.find((t) => t.k === 'all');
  if (terms1b.hdr && terms1b.cards === terms1b.bankTerms && allTab && allTab.act)
    pass('R7', '全部 tab: ' + terms1b.hdr + ' 与题库术语数一致 (' + terms1b.cards + ' 张卡)');
  else fail('R7', '全部 tab 异常: ' + JSON.stringify(terms1b));
  /* 当前章 tab → 应有数据 */
  await click('.filter-tab[data-key="biochem_10"]'); await sleep(350);
  const terms2 = await ev(`(function(){var hdr=document.querySelector('.list-header p');var cards=document.querySelectorAll('.term-card').length;var act=document.querySelector('.filter-tab.active');return {hdr:hdr?hdr.textContent:null,cards:cards,act:act?act.getAttribute('data-key'):null};})()`);
  info('terms(biochem_10): ' + JSON.stringify(terms2));
  if (terms2.act === 'biochem_10' && terms2.cards > 0 && terms2.hdr && terms2.hdr.indexOf(String(terms2.cards)) >= 0)
    pass('R7', '本章 tab 过滤: ' + terms2.hdr);
  else fail('R7', '本章 tab 异常: ' + JSON.stringify(terms2));
  /* 另一章 tab → 空态不崩溃 */
  await click('.filter-tab[data-key="biochem_1_2"]'); await sleep(350);
  const terms3 = await ev(`(function(){var hdr=document.querySelector('.list-header p');var cards=document.querySelectorAll('.term-card').length;var empty=document.querySelector('.empty-state');var exp=empty?empty.textContent:null;return {cards:cards,empty:exp};})()`);
  info('terms(biochem_1_2): ' + JSON.stringify(terms3));
  /* 切课程后 tab 列表变化 */
  await toHome();
  await click('.brand-tag[data-course="cellbiology"]'); await sleep(300);
  await click('[data-action="start-noun"]'); await sleep(500);
  const terms4 = await ev(`(function(){var tabs=[].map.call(document.querySelectorAll('.filter-tab'),function(t){return t.getAttribute('data-key');});return {tabs:tabs,n:document.querySelectorAll('.term-card').length};})()`);
  info('terms(cell): tabs=' + JSON.stringify(terms4.tabs) + ' cards=' + terms4.n);
  if (terms4.tabs.length === 17 && terms4.tabs[0] === 'all' && terms4.tabs[1] === 'cellbio_1' && terms4.tabs[16] === 'cellbio_16')
    pass('R7', '切课程后术语 tab 刷新为 细胞16章+全部');
  else fail('R7', '切课程术语 tab 异常: ' + JSON.stringify(terms4));
  await toHome();
  await click('.brand-tag[data-course="biochemistry"]'); await sleep(300);

  /* ============================================================
     R8 错题本:答错进 → 错题重做 → 答对移除
  ============================================================ */
  console.log('===== R8 错题本 =====');
  await resetAll();
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  const q1id = qi.id;
  const wOpt1 = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wOpt1 + '"]'); await sleep(350);
  let wsKeys = await wrongIds();
  if (wsKeys.length === 1 && wsKeys[0] === 'biochem_1_2__' + q1id) pass('R8', '答错进错题本: ' + wsKeys[0]);
  else fail('R8', '答错未正确进错题本: ' + JSON.stringify(wsKeys));
  /* 错题重做(start-wrong) */
  await toHome();
  await click('[data-action="start-wrong"]'); await sleep(500);
  st = await state();
  let qi2 = await qinfo();
  if (st.view === 'quiz' && st.qCount === 1 && qi2.id === q1id) pass('R8', '错题重做: 进入错题 1 题 (id=' + q1id + ')');
  else fail('R8', '错题重做异常: ' + JSON.stringify(st) + ' q=' + JSON.stringify(qi2));
  /* 答对 → 立即移除 */
  await click('.option[data-value="' + qi2.answer + '"]'); await sleep(400);
  wsKeys = await wrongIds();
  st = await state();
  if (wsKeys.length === 0) pass('R8', '答对即移除: wrongQs() 为空, wrongSet=' + st.wrong);
  else fail('R8', '答对未移除错题: ' + JSON.stringify(wsKeys));
  /* reload 后保持空 */
  await reload();
  await toHome();
  wsKeys = await wrongIds();
  if (wsKeys.length === 0) pass('R8', 'reload 后错题本为空(移除已持久化)');
  else fail('R8', 'reload 后错题本仍有: ' + JSON.stringify(wsKeys));
  /* 再答错一条 → reload → 错题持久化 */
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  const wOpt2 = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wOpt2 + '"]'); await sleep(350);
  await reload();
  await toHome();
  wsKeys = await wrongIds();
  if (wsKeys.length === 1 && wsKeys[0] === 'biochem_1_2__' + q1id) pass('R8', '错题持久化: reload 后错题仍在 (' + wsKeys[0] + ')');
  else fail('R8', '错题持久化失败: ' + JSON.stringify(wsKeys));

  /* ============================================================
     R9 书签:收藏 → 精选可见 → 取消收藏 → reload 不再出现
  ============================================================ */
  console.log('===== R9 书签 =====');
  await resetAll();
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  const aId = qi.id;
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  /* 跨章收藏第二道 */
  await toHome();
  await click('.chapter-chip[data-key="biochem_3"]'); await sleep(300);
  await click('[data-action="start-quiz"]'); await sleep(500);
  await click('[data-action="nav-next"]'); await sleep(300);
  qi = await qinfo();
  const bId = qi.id;
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  let bkeys = await bmIds();
  info('收藏: ' + JSON.stringify(bkeys));
  if (bkeys.length === 2 && bkeys.indexOf('biochem_1_2__' + aId) >= 0 && bkeys.indexOf('biochem_3__' + bId) >= 0)
    pass('R9', '跨章收藏 2 题 (1_2 与 3 各 1)');
  else fail('R9', '收藏异常: ' + JSON.stringify(bkeys));
  /* 精选习题可见 */
  await toHome();
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  st = await state();
  const bmList = await ev(`(function(){return __qa.S.questions.map(function(q){return (q._bmSubj||__qa.S.subject)+'__'+q.id;});})()`);
  info('精选习题: ' + JSON.stringify(bmList));
  if (st.view === 'quiz' && bmList.length === 2 && bmList.indexOf('biochem_1_2__' + aId) >= 0 && bmList.indexOf('biochem_3__' + bId) >= 0)
    pass('R9', '精选习题含 2 题(跨章)');
  else fail('R9', '精选习题异常: ' + JSON.stringify(bmList));
  /* 翻到第二题(属 biochem_3)取消收藏 */
  await click('[data-action="nav-next"]'); await sleep(300);
  qi = await qinfo();
  if (qi.bmSubj === 'biochem_3') pass('R9', '精选模式第二题 _bmSubj=biochem_3 (跨章标识正确)');
  else fail('R9', '_bmSubj 异常: ' + JSON.stringify(qi));
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  const bmAfter = await bmIds();
  info('取消后: ' + JSON.stringify(bmAfter));
  if (bmAfter.length === 1 && bmAfter[0] === 'biochem_1_2__' + aId)
    pass('R9', '取消收藏: 仅剩 biochem_1_2 的题, biochem_3 的已移除');
  else fail('R9', '取消收藏异常: ' + JSON.stringify(bmAfter));
  /* reload → 被取消的不再出现 */
  await reload();
  await toHome();
  bkeys = await bmIds();
  if (bkeys.length === 1 && bkeys[0] === 'biochem_1_2__' + aId)
    pass('R9', 'reload 后精选仅剩 1 题(被取消的未复现)');
  else fail('R9', 'reload 后精选异常: ' + JSON.stringify(bkeys));
  /* 取消最后一题 → reload → 空 */
  await click('[data-action="start-bookmarked"]'); await sleep(500);
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  await reload();
  await toHome();
  bkeys = await bmIds();
  if (bkeys.length === 0) pass('R9', '全部取消 + reload 后精选为空(空态正常)');
  else fail('R9', '全取消后仍有: ' + JSON.stringify(bkeys));
  /* 空态点精选卡片 → toast 不崩溃 */
  await click('[data-action="start-bookmarked"]'); await sleep(400);
  st = await state();
  const toast1 = await ev(`(function(){var t=document.querySelector('.toast');return t?t.textContent:null;})()`);
  if (st.view === 'home' && toast1 === '暂无收藏 · 星标题目将在此练习') pass('R9', '空精选点卡 → toast 提示且不崩溃');
  else fail('R9', '空精选点卡异常: view=' + st.view + ' toast=' + toast1);

  /* ============================================================
     R10 导出 / 导入
  ============================================================ */
  console.log('===== R10 导出/导入 =====');
  await resetAll();
  /* 制造一点数据 */
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  await click('.option[data-value="' + qi.answer + '"]'); await sleep(350);      // 答对1题
  await click('[data-action="toggle-bookmark"]'); await sleep(300);              // 收藏
  await click('[data-action="nav-next"]'); await sleep(300);
  qi = await qinfo();
  const wOpt3 = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wOpt3 + '"]'); await sleep(350);          // 答错1题
  await toHome();
  const snap1 = await ev('__expimp.snapshot()');
  const snapObj = JSON.parse(snap1);
  const expJson = await ev('__expimp.exportData()');
  const expObj = JSON.parse(expJson);
  if (expObj.app === 'hnu-academy' && expObj.type === 'learning-data' && expObj.data && expObj.data.bookmarks && Object.keys(expObj.data.bookmarks).length === 1)
    pass('R10', '导出函数: 返回合法 learning-data JSON (bookmarks=1, answers=' + Object.keys(expObj.data.answers).length + ')');
  else fail('R10', '导出函数返回异常: ' + JSON.stringify(Object.keys(expObj)));
  /* 真实按钮 → 下载文件落盘 */
  await clickText('#hnuExpBar', '导出数据'); await sleep(1200);
  const dlFiles = fs.readdirSync(downloadDir).filter((f) => f.indexOf('hnu-academy-data-') === 0);
  if (dlFiles.length >= 1) pass('R10', '导出按钮 → 下载文件: ' + dlFiles.join(', '));
  else fail('R10', '导出按钮未产生下载文件 (dir=' + downloadDir + ', events=' + JSON.stringify(downloadEvents) + ')');
  const expBankJson = await ev('__expimp.exportBank()');
  const expBank = JSON.parse(expBankJson);
  if (expBank.type === 'bank-archive' && expBank.bankCount === 51 && expBank.questionCount === 5844)
    pass('R10', '导出题库归档: 51 章 / ' + expBank.questionCount + ' 题');
  else fail('R10', '题库归档异常: ' + JSON.stringify({bc: expBank.bankCount, qc: expBank.questionCount}));
  /* ---- 非法文件导入(不破坏) ---- */
  const beforeBad = await ev('(function(){return {ans:Object.keys(__qa.S.answers).length,wrong:Object.keys(__qa.S.wrongSet).length,bm:Object.keys(__qa.S.bookmarks).length,view:__qa.S.view};})()');
  const bad1 = await ev('__expimp.importData("not-json{{")');
  const bad2 = await ev('__expimp.importData(JSON.stringify({foo:1}))');
  const bad3 = await ev('__expimp.importData("[1,2,3]")');
  const bad4 = await ev('__expimp.importData(JSON.stringify({data:{answers:"bad"}}))');
  const afterBad = await ev('(function(){return {ans:Object.keys(__qa.S.answers).length,wrong:Object.keys(__qa.S.wrongSet).length,bm:Object.keys(__qa.S.bookmarks).length,view:__qa.S.view};})()');
  info('非法导入: ' + JSON.stringify({bad1, bad2, bad3, bad4}));
  if (bad1.ok === false && bad2.ok === false && bad3.ok === false && bad4.ok === false)
    pass('R10', '4 类非法文件均被拒绝 (非JSON/无字段/数组/字段格式错)');
  else fail('R10', '非法文件未被拒绝: ' + JSON.stringify({bad1, bad2, bad3, bad4}));
  if (JSON.stringify(beforeBad) === JSON.stringify(afterBad))
    pass('R10', '非法导入不破坏现有数据 (' + JSON.stringify(afterBad) + ')');
  else fail('R10', '非法导入改变了状态: ' + JSON.stringify({before: beforeBad, after: afterBad}));
  /* ---- 合法导入(真实文件选择器) ---- */
  const importFile = path.join(os.tmpdir(), 'hnu-import-test.json');
  fs.writeFileSync(importFile, snap1, 'utf8');
  /* 先污染状态 */
  await selectChapter('biochem_3');
  await click('[data-action="start-quiz"]'); await sleep(500);
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  const polluted = await ev('(function(){return {ans:Object.keys(__qa.S.answers).length,bm:Object.keys(__qa.S.bookmarks).length};})()');
  await toHome();
  /* 真实路径: 点「导入数据」→ 输入框挂载 → DOM.setFileInputFiles 注入文件 → change 触发导入 */
  const importBtnOk = await clickText('#hnuExpBar', '导入数据');
  await sleep(500);
  const doc = await send('DOM.getDocument', { depth: -1 });
  const qr = await send('DOM.querySelector', { nodeId: doc.result.root.nodeId, selector: 'input[type=file]' });
  if (qr.result && qr.result.nodeId) {
    await send('DOM.setFileInputFiles', { files: [importFile], nodeId: qr.result.nodeId }).catch((e) => info('setFileInputFiles err: ' + e));
  } else { info('file input not found in DOM'); }
  await sleep(1500);
  st = await ev('(function(){return {ans:Object.keys(__qa.S.answers).length,wrong:Object.keys(__qa.S.wrongSet).length,bm:Object.keys(__qa.S.bookmarks).length,view:__qa.S.view};})()');
  const bk = await ev('(function(){try{return !!localStorage.getItem("hnu_academy_backup");}catch(e){return false;}})()');
  const toastImp = await ev(`(function(){var t=document.querySelector('.toast');return t?t.textContent:null;})()`);
  info('合法导入: before=' + JSON.stringify(polluted) + ' after=' + JSON.stringify(st) + ' backup=' + bk + ' toast=' + toastImp);
  if (importBtnOk && st.ans === beforeBad.ans && st.bm === beforeBad.bm && bk)
    pass('R10', '合法导入(真实文件选择器): 状态回滚至快照, 备份键已建' + (toastImp ? ', toast=' + toastImp : ''));
  else fail('R10', '合法导入异常: ' + JSON.stringify({importBtnOk, polluted, st, bk, toastImp}));
  /* 导入后应用仍可正常做题 */
  await click('[data-action="start-quiz"]'); await sleep(500);
  st = await state();
  if (st.view === 'quiz') pass('R10', '导入后应用可继续做题(未破坏)');
  else fail('R10', '导入后做题异常: ' + JSON.stringify(st));

  /* ============================================================
     R11 结果页统计(今日/累计)
  ============================================================ */
  console.log('===== R11 结果页统计 =====');
  await resetAll();
  const statsBefore = await ev(`(function(){var t=JSON.parse(localStorage.getItem('hnu_academy_total')||'{}');var d=JSON.parse(localStorage.getItem('hnu_academy_daily_'+(function(){var x=new Date(),m=x.getMonth()+1,y=x.getFullYear(),day=x.getDate();return y+'-'+(m<10?'0'+m:m)+'-'+(day<10?'0'+day:day);})())||'{}');return {tc:t.totalCount||0,tk:t.totalCorrect||0,dc:d.totalCount||0,dk:d.totalCorrect||0};})()`);
  await selectChapter('biochem_10');
  await click('[data-action="start-short"]'); await sleep(500);
  st = await state();
  const shortTotal = st.qCount;
  for (let i = 0; i < shortTotal; i++) {
    await click('[data-action="short-reveal"]'); await sleep(220);
    if (i < shortTotal - 1) { await click('[data-action="nav-next"]'); await sleep(220); }
  }
  st = await state();
  const lastBtn = await ev(`(function(){var b=document.querySelector('[data-action="nav-next"]');return b?b.textContent.trim():null;})()`);
  if (st.view === 'quiz' && lastBtn === '完成') pass('R11', '末题按钮=完成 (' + shortTotal + ' 题 short 全答)');
  else fail('R11', '末题按钮异常: ' + lastBtn + ' view=' + st.view);
  await click('[data-action="nav-next"]'); await sleep(500);
  st = await state();
  if (st.view !== 'result') fail('R11', '完成 → 结果页未出现: view=' + st.view);
  const res = await ev(`(function(){var v=document.getElementById('view-result');var score=document.querySelector('.result-score-num');var sub=document.querySelector('.result-score-sub');var stats=[].map.call(document.querySelectorAll('.result-stats span'),function(s){return s.textContent.trim();});var acc=[].map.call(document.querySelectorAll('#view-result span'),function(s){return s.textContent;}).filter(function(t){return t.indexOf('今日已练')>=0||t.indexOf('累计已练')>=0;});return {score:score?score.textContent:null,sub:sub?sub.textContent:null,acc:acc};})()`);
  info('result: score=' + res.score + ' sub=' + res.sub + ' acc=' + JSON.stringify(res.acc));
  if (res.score === '100%' && res.sub === String(shortTotal) + ' / ' + shortTotal)
    pass('R11', '结果页本轮得分: 100% (' + shortTotal + '/' + shortTotal + ')');
  else fail('R11', '结果页得分异常: ' + JSON.stringify(res));
  const statsAfter = await ev(`(function(){var t=JSON.parse(localStorage.getItem('hnu_academy_total')||'{}');var d=JSON.parse(localStorage.getItem('hnu_academy_daily_'+(function(){var x=new Date(),m=x.getMonth()+1,y=x.getFullYear(),day=x.getDate();return y+'-'+(m<10?'0'+m:m)+'-'+(day<10?'0'+day:day);})())||'{}');return {tc:t.totalCount||0,tk:t.totalCorrect||0,dc:d.totalCount||0,dk:d.totalCorrect||0};})()`);
  const dT = statsAfter.tc - statsBefore.tc, dK = statsAfter.tk - statsBefore.tk;
  if (dT === shortTotal && dK === shortTotal)
    pass('R11', '统计落库: 累计 +' + dT + ' 题/答对 +' + dK + ' (今日同步 +' + (statsAfter.dc - statsBefore.dc) + ')');
  else fail('R11', '统计落库异常: delta=' + JSON.stringify({dT, dK, b: statsBefore, a: statsAfter}));
  const accTxt = res.acc.join(' ');
  if (accTxt.indexOf('今日已练') >= 0 && accTxt.indexOf('累计已练') >= 0)
    pass('R11', '结果页今日/累计统计行渲染: ' + accTxt);
  else fail('R11', '结果页统计行缺失: ' + accTxt);

  /* ============================================================
     R12 清除数据(confirm 取消/确认)
  ============================================================ */
  console.log('===== R12 清除数据 =====');
  await toHome();
  await ev(`(function(){var b=document.createElement('button');b.id='qaClearBtn';b.setAttribute('data-action','clear-data');b.style.display='none';document.getElementById('app').appendChild(b);return true;})()`);
  /* 取消确认 → 不清除 */
  dialogPolicy = 'dismiss';
  await click('#qaClearBtn'); await sleep(400);
  st = await state();
  const tStat1 = await ev(`(function(){try{return !!localStorage.getItem('hnu_academy_total');}catch(e){return false;}})()`);
  if (st.wrong === 0 && st.bm === 0 && st.ans === 0 && !tStat1)
    fail('R12', '取消确认后数据被清除(预期保留): ' + JSON.stringify(st));
  else pass('R12', '取消确认: 数据保留 (wrong=' + st.wrong + ' bm=' + st.bm + ' ans=' + st.ans + ' total存在=' + tStat1 + ')');
  /* 确认清除 → 全部归零 */
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  const wOpt4 = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wOpt4 + '"]'); await sleep(350);
  await click('[data-action="toggle-bookmark"]'); await sleep(300);
  await toHome();
  const beforeClear = await state();
  dialogPolicy = 'accept';
  await click('#qaClearBtn'); await sleep(500);
  dialogPolicy = 'dismiss';
  st = await state();
  const clearChecks = await ev(`(function(){var bad=[];for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf('hnu_academy_prog_')===0||k.indexOf('hnu_academy_wrong_')===0||k.indexOf('hnu_academy_bm_')===0||k==='hnu_academy_total')bad.push(k);}var t=document.querySelector('.toast');return {badKeys:bad,toast:t?t.textContent:null};})()`);
  info('清除前: ' + JSON.stringify(beforeClear) + ' 清除后: ' + JSON.stringify(st) + ' 残留键: ' + JSON.stringify(clearChecks));
  if (st.wrong === 0 && st.bm === 0 && st.ans === 0 && st.sp === 0 && st.best === 0 && clearChecks.badKeys.length === 0)
    pass('R12', '确认清除: 进度/错题/书签/连击全归零, 无残留存储键' + (clearChecks.toast ? ', toast=' + clearChecks.toast : ''));
  else fail('R12', '清除不彻底: ' + JSON.stringify({st, badKeys: clearChecks.badKeys}));
  await ev('(function(){var b=document.getElementById(' + JSON.stringify('qaClearBtn') + ');if(b)b.remove();return true;})()');

  /* ============================================================
     R13 reload 持久化:进度/错题/书签保持 + 续练弹窗
  ============================================================ */
  console.log('===== R13 reload 持久化 =====');
  await resetAll();
  await selectChapter('biochem_1_2');
  await click('[data-action="start-quiz"]'); await sleep(500);
  qi = await qinfo();
  const pQ1 = qi.id;
  const wOpt5 = await ev(`(function(){var q=__qa.S.questions[__qa.S.qIndex];var ks=Object.keys(q.options);return ks[0]===String(q.answer)?ks[1]:ks[0];})()`);
  await click('.option[data-value="' + wOpt5 + '"]'); await sleep(350);   // Q1 答错
  await click('[data-action="nav-next"]'); await sleep(300);
  qi = await qinfo();
  const pQ2 = qi.id;
  await click('[data-action="toggle-bookmark"]'); await sleep(300);       // Q2 收藏
  await click('.option[data-value="' + qi.answer + '"]'); await sleep(350); // Q2 答对
  const preReload = await state();
  const lsk = await ev(`(function(){var r={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf('hnu_academy_')===0)r[k]=localStorage.getItem(k).length;}return r;})()`);
  info('reload 前: ' + JSON.stringify(preReload) + ' keys=' + JSON.stringify(lsk));
  await reload();
  await toHome();
  st = await state();
  const persisted = await ev(`(function(){var S=__qa.S;return {wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,sp:Object.keys(S.savedProgress).length};})()`);
  if (persisted.wrong === 1 && persisted.bm === 1 && persisted.sp === 1)
    pass('R13', 'reload 后错题/书签/进度快照保持 (' + JSON.stringify(persisted) + ')');
  else fail('R13', 'reload 后状态丢失: ' + JSON.stringify(persisted));
  /* 续练弹窗:accept → 恢复 qIndex=1 与已答 2 题 */
  dialogPolicy = 'accept';
  await click('[data-action="start-quiz"]'); await sleep(600);
  dialogPolicy = 'dismiss';
  st = await state();
  info('续练恢复: ' + JSON.stringify(st) + ' dialogMsg=' + JSON.stringify(lastDialogMsg));
  const resumed = await ev(`(function(){var S=__qa.S;return {qId:S.questions[S.qIndex]?S.questions[S.qIndex].id:null,ans:Object.keys(S.answers).length,revealed:Object.keys(S.revealed||{}).length,first:S.questions[0]?S.questions[0].id:null};})()`);
  if (st.view === 'quiz' && st.index === 1 && resumed.ans === 2 && resumed.qId === pQ2)
    pass('R13', '续练弹窗(已完成2题) → 恢复至第2题, 已答记录完整');
  else fail('R13', '续练恢复异常: ' + JSON.stringify({st, resumed}));
  /* 错题重做路径仍可用 */
  await toHome();
  await click('[data-action="start-wrong"]'); await sleep(500);
  st = await state();
  qi = await qinfo();
  if (st.view === 'quiz' && st.qCount === 1 && qi.id === pQ1)
    pass('R13', 'reload 后错题重做: 仍是 Q1 (' + pQ1 + ')');
  else fail('R13', 'reload 后错题重做异常: ' + JSON.stringify(st) + ' q=' + JSON.stringify(qi));
  await click('.option[data-value="' + qi.answer + '"]'); await sleep(350);
  await reload();
  await toHome();
  wsKeys = await wrongIds();
  if (wsKeys.length === 0) pass('R13', '重做答对后 reload, 错题清零(终态一致)');
  else fail('R13', '重做后错题未清零: ' + JSON.stringify(wsKeys));

  /* ============================================================
     汇总:JS 异常 / console 错误
  ============================================================ */
  console.log('===== JS 异常 / console 错误 汇总 =====');
  const realErr = consoleErrs.filter((e) => e.indexOf('Failed to load resource') < 0);
  if (exceptions.length === 0) pass('ERR', '全程 0 次 JS 未捕获异常');
  else fail('ERR', 'JS 异常 ' + exceptions.length + ' 次: ' + exceptions.slice(0, 5).join(' | '));
  if (realErr.length === 0) pass('ERR', '全程 0 条 console error (过滤资源加载)' + (consoleErrs.length ? '; 资源类 ' + consoleErrs.length + ' 条' : ''));
  else fail('ERR', 'console error ' + realErr.length + ' 条: ' + realErr.slice(0, 5).join(' | '));

  fs.writeFileSync(path.join(__dirname, '_reg_results.json'), JSON.stringify({ failedCount, results, exceptions, consoleErrs }, null, 1), 'utf8');
  console.log('\n===== 最终: ' + (failedCount === 0 ? 'ALL PASS' : 'FAILED ' + failedCount + ' 项') + ' =====');
  console.log('结果文件: _reg_results.json');
  try { await send('Browser.close'); } catch (e) {}
  process.exit(failedCount === 0 ? 0 : 1);
}
main().catch((e) => { console.error(e); process.exit(2); });
