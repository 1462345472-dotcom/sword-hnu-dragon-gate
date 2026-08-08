// _task3_test.mjs — Task 3 功能验证:运行期缓存(命中/失效/成就语义) + UI 交互路径(做题/错题/书签/切章/名词)
// 用法: node _task3_test.mjs [html路径]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 9334;
const HTML = process.argv[2] ? resolve(process.argv[2]) : resolve('生物化学题库/湖南大学题库系统-臻至版.html');
const url = pathToFileURL(HTML).href;
const profile = mkdtempSync(join(tmpdir(), 'edge-t3-'));

const proc = spawn(EDGE, [
  '--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
  `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, 'about:blank'
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getWsUrl() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json/list`);
      const list = await r.json();
      const page = list.find(t => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error('CDP endpoint not reachable');
}

function connect(wsUrl) {
  return new Promise((resolve_, reject) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    const listeners = new Map();
    ws.onopen = () => resolve_({
      send(method, params = {}) {
        return new Promise((res, rej) => {
          const mid = ++id;
          pending.set(mid, { res, rej });
          ws.send(JSON.stringify({ id: mid, method, params }));
        });
      },
      on(method, cb) { listeners.set(method, cb); },
      close() { ws.close(); }
    });
    ws.onerror = e => reject(e);
    ws.onmessage = ev => {
      const msg = JSON.parse(ev.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
      } else if (msg.method && listeners.has(msg.method)) {
        listeners.get(msg.method)(msg.params);
      }
    };
  });
}

const INJECT = `
  window.__errs = [];
  window.addEventListener('error', function(e){ window.__errs.push('error: ' + (e.message||'') ); });
  window.addEventListener('unhandledrejection', function(e){ window.__errs.push('rejection: ' + (e.reason||'') ); });
  try { localStorage.setItem('hnu_academy_visited','1'); } catch(e){}
  try { localStorage.setItem('hnu_academy_s', JSON.stringify({wrongSet:{},bookmarks:{},bestStreak:0,achievements:{},course:'biochemistry',subject:'biochem_1_2',termFilter:'all'})); } catch(e){}
`;

// ============ 阶段 A:缓存逻辑(命中/失效/成就语义) ============
const PHASE_A = `
(function(){
  var Q=window.__qa;
  var out={pass:true,checks:[]};
  var chk=function(name,cond,extra){out.checks.push({name:name,ok:!!cond,extra:(extra===undefined?'':String(extra))});if(!cond)out.pass=false;};
  var S=Q.S;
  S.subject='biochem_1_2';
  var qs=Q.getBank('biochem_1_2').questions;
  S.questions=qs;S.qIndex=0;S.answers={};S.revealed={};S.streak=0;S.wrongSet={};S.bookmarks={};S.achievements={};S._multiSelection={};
  window.__qa._invalidate=window.__qa.S&&function(){};
  var kf=function(id){return Q.ak('biochem_1_2',id);};
  var ansOf=function(q){return q.type==='truefalse'?String(q.answer).toLowerCase():(q.type==='short'?'done':q.answer);};
  var i;
  for(i=0;i<40;i++){var q=qs[i];S.answers[kf(q.id)]=ansOf(q);S.revealed[kf(q.id)]=true;}
  S.wrongSet[kf(qs[40].id)]=true;S.wrongSet[kf(qs[41].id)]=true;
  S.bookmarks[kf(qs[42].id)]=true;

  /* 1. wrongQs 首算全量 vs 二次缓存 */
  var t0=performance.now();var w1=Q.wrongQs();var tFirst=performance.now()-t0;
  t0=performance.now();var w2=Q.wrongQs();var tSecond=performance.now()-t0;
  chk('wrongQs 首算=2题',w1.length===2,w1.length);
  chk('wrongQs 二次缓存命中(结果一致,<2ms)',w2.length===2&&tSecond<2,'first='+tFirst.toFixed(2)+'ms second='+tSecond.toFixed(2)+'ms');

  /* 2. 答错新题 → wrongQs 必须更新(缓存失效正确) */
  S.qIndex=43;var q43=qs[43];
  var wOpt=null;for(var kk in q43.options){if(kk!==q43.answer){wOpt=kk;break;}}
  Q.submitAnswer(q43.id,(q43.type==='choice'?wOpt:(String(q43.answer)==='true'?'false':'true')));
  var w3=Q.wrongQs();
  chk('答错后 wrongQs 含新题(失效正确)',w3.length===3&&w3.some(function(x){return x.id===q43.id;}),'n='+w3.length);

  /* 3. bmQs 缓存 */
  t0=performance.now();var b1=Q.bmQs();var bt1=performance.now()-t0;
  t0=performance.now();var b2=Q.bmQs();var bt2=performance.now()-t0;
  chk('bmQs 首算=1题',b1.length===1,b1.length);
  chk('bmQs 二次缓存命中(<2ms)',b2.length===1&&bt2<2,'first='+bt1.toFixed(2)+'ms second='+bt2.toFixed(2)+'ms');

  /* 4. 收藏切换 → bmQs 更新(失效正确) */
  var k44=kf(qs[44].id);
  if(S.bookmarks[k44])delete S.bookmarks[k44];else S.bookmarks[k44]=true;
  Q.invalidate();
  var b3=Q.bmQs();
  chk('收藏新增后 bmQs 含新题(失效正确)',b3.length===2&&b3.some(function(x){return x.id===qs[44].id;}),'n='+b3.length);

  /* 5. 成就:累计 40 题答对 → 百题斩(threshold 100)不解锁 */
  Q.resetAch();
  S.achievements={};
  Q.checkAchievements();
  chk('累计40题:百题斩未解锁',!S.achievements['century']);

  /* 6. 补到 100 题答对 → 百题斩解锁(全量重算路径) */
  for(i=40;i<100;i++){var q2=qs[i];S.answers[kf(q2.id)]=ansOf(q2);S.revealed[kf(q2.id)]=true;}
  Q.resetAch();
  S.achievements={};
  Q.checkAchievements();
  chk('累计100题:百题斩解锁(全量重算)',!!S.achievements['century'],'achCnt='+Q.achCnt());
  chk('缓存计数=100',Q.achCnt()===100,Q.achCnt());

  /* 7. 增量维护:删 1 题答对记录 → 缓存置 null → 重算 99 → submitAnswer 答对 → 100 */
  var q0=qs[0];
  delete S.answers[kf(q0.id)];delete S.revealed[kf(q0.id)];
  Q.resetAch();
  Q.checkAchievements();
  chk('删除1题后全量重算=99',Q.achCnt()===99,Q.achCnt());
  S.qIndex=0;
  Q.submitAnswer(q0.id,ansOf(q0));
  chk('submitAnswer 答对后增量=100',Q.achCnt()===100,Q.achCnt());

  /* 8. 核心:startQuiz 清空 answers → 缓存必须失效(结果不能是旧的) */
  S.achievements={};
  S.qIndex=0;Q.startQuiz('biochem_1_2','all');
  chk('startQuiz 后三缓存全部失效(null)',Q.achCnt()===null&&Q.wrongCache()===null&&Q.bmCache()===null);
  Q.checkAchievements();
  chk('清空后重算=0 且百题斩不解锁',Q.achCnt()===0&&!S.achievements['century'],'n='+Q.achCnt());

  /* 9. resumeSavedProgress 恢复 answers → 缓存失效重算(用真实答案构造) */
  var qr1=qs[0],qr2=qs[1];
  var resAns={};resAns[kf(qr1.id)]=ansOf(qr1);resAns[kf(qr2.id)]=ansOf(qr2);
  S.savedProgress['biochem_1_2|all']={qIndex:3,answers:resAns,revealed:{},streak:1};
  S._pendingSubject='biochem_1_2';S._pendingMode='all';
  try{Q.resumeSavedProgress();}catch(e){chk('resume 无异常',false,e.message);}
  chk('resume 后成就缓存失效(null)',Q.achCnt()===null,'v='+Q.achCnt());
  Q.checkAchievements();
  chk('resume 后重算=恢复题数',Q.achCnt()===2,Q.achCnt());

  /* 9b. 核心回归(审查发现 Minor):resume 提前 return 路径(错题集空 → 行1475 return)
        该路径下原失效调用(清理+过滤后)不执行,成就缓存会基于旧 answers 残留 */
  S.questions=qs;S.qIndex=0;S.answers={};S.revealed={};S.streak=0;S.wrongSet={};S.bookmarks={};S.achievements={};S._multiSelection={};
  Q.invalidate();
  for(i=0;i<99;i++){var q9=qs[i];S.answers[kf(q9.id)]=ansOf(q9);S.revealed[kf(q9.id)]=true;}
  Q.checkAchievements();
  chk('预填:成就缓存=99',Q.achCnt()===99,Q.achCnt());
  S.wrongSet={}; /* 错题集为空 → mode=wrong 的续练恢复将提前 return */
  var resA={};resA[kf(qs[1].id)]=ansOf(qs[1]);
  S.savedProgress['biochem_1_2|wrong']={qIndex:0,answers:resA,revealed:{},streak:1};
  S._pendingSubject='biochem_1_2';S._pendingMode='wrong';
  Q.resumeSavedProgress();
  chk('提前 return 路径触发(错题列表空)',S.questions.length===0,S.questions.length);
  chk('修复:提前 return 后成就缓存失效(null)',Q.achCnt()===null,'v='+Q.achCnt());
  Q.checkAchievements();
  chk('提前 return 后重算=新answers答对数(1)',Q.achCnt()===1,Q.achCnt());
  chk('提前 return 后百题斩不解锁(无陈旧计数)',!S.achievements['century']);
  chk('resume 后 wrongQs 反映当前 wrongSet(0题)',Q.wrongQs().length===0);

  /* 10. clear-data 场景:wrongSet/bookmarks/achievements 全清 + 失效 */
  S.wrongSet={};S.bookmarks={};S.achievements={};
  Q.invalidate();
  chk('clear后 wrongQs 空',Q.wrongQs().length===0);
  chk('clear后 bmQs 空',Q.bmQs().length===0);
  var w4=Q.wrongQs();var w5=Q.wrongQs();
  chk('空结果缓存仍生效(不反复重算)',w4.length===0&&w5.length===0);
  return out;
})();
`;

// ============ 阶段 B:UI 交互路径(真实点击) ============
const PHASE_B = `
(async function(){
  var Q=window.__qa,S=Q.S;
  var out={pass:true,checks:[]};
  var chk=function(name,cond,extra){out.checks.push({name:name,ok:!!cond,extra:(extra===undefined?'':String(extra))});if(!cond)out.pass=false;};
  var sleep=function(ms){return new Promise(function(r){setTimeout(r,ms);});};
  var curQ=function(){return S.qIndex<S.questions.length?S.questions[S.qIndex]:null;};

  /* 1. 首页:51 章节键(两课程并集) */
  var chips=Array.from(document.querySelectorAll('#view-home [data-key]')).map(function(e){return e.getAttribute('data-key');});
  var brandTags=Array.from(document.querySelectorAll('.brand-tag[data-course]')).map(function(e){return e.getAttribute('data-course');});
  chk('首页章节 chips 存在(35+16)',chips.length===51||brandTags.length===2,'chips='+chips.length);

  /* 2. 全部刷题 */
  document.querySelector('.m-quiz').click();
  await sleep(400);
  chk('进入 quiz 视图',!!document.querySelector('section.view.active#view-quiz'));
  var q1=curQ();
  chk('第1题为 choice',q1.type==='choice',q1.type);

  /* 3. 第1题答错(选非答案选项) */
  var wrongKey=null;for(var k in q1.options){if(k!==q1.answer){wrongKey=k;break;}}
  document.querySelector('.option[data-value="'+wrongKey+'"]').click();
  await sleep(200);
  chk('答错后 revealed+locked',document.querySelectorAll('.option.locked').length>0);
  chk('答错后 wrongSet 记录1题',Object.keys(S.wrongSet).length===1,Object.keys(S.wrongSet).length);

  /* 4. 收藏第1题 */
  var bmBtn=document.querySelector('.bm-btn');
  bmBtn.click();
  await sleep(200);
  chk('书签按钮 active',document.querySelector('.bm-btn.active')!==null);
  chk('bookmarks 记录1题',Object.keys(S.bookmarks).length===1);
  var bmc=Q.bmQs();
  chk('bmQs=1题',bmc.length===1,bmc.length);

  /* 5. 下一题 → 按题型正确作答 */
  document.querySelector('[data-action="nav-next"]').click();
  await sleep(300);
  var q2=curQ();
  var act=function(){
    var q=curQ();if(!q)return 'no-q';
    if(q.type==='choice'){document.querySelector('.option[data-value="'+q.answer+'"]').click();return 'choice';}
    if(q.type==='truefalse'){document.querySelector('.tf-row [data-value="'+String(q.answer).toLowerCase()+'"]').click();return 'tf';}
    if(q.type==='multi'){var ks=Object.keys(q.options);document.querySelector('.option[data-value="'+ks[0]+'"]').click();document.querySelector('.option[data-value="'+ks[1]+'"]').click();var btn=document.querySelector('.multi-confirm-btn');if(btn&&!btn.disabled)btn.click();return 'multi';}
    if(q.type==='short'){var b=document.querySelector('.short-reveal-btn');if(b)b.click();return 'short';}
    return 'unknown';
  };
  var r=act();
  chk('第2题作答('+r+') 成功',['choice','tf','multi','short'].indexOf(r)>=0,r);

  /* 6. 连答 4 题(累计 5 连对) → 成就"磨剑"解锁 + 缓存命中验证 */
  var t0=performance.now();var wA=Q.wrongQs();var tW=performance.now()-t0;
  chk('wrongQs 缓存命中(<2ms)',tW<2,'ms='+tW.toFixed(2));
  chk('wrongQs=1题(仅第1题错)',wA.length===1,wA.length);
  for(var i2=0;i2<4;i2++){
    var hasNext=document.querySelector('[data-action="nav-next"]');
    if(!hasNext)break;
    hasNext.click();
    await sleep(300);
    var r2=act();
  }
  chk('连续作答无异常(仍在 quiz)',!!document.querySelector('section.view.active#view-quiz'));
  chk('5连对 streak=5',S.streak===5,'streak='+S.streak);
  chk('成就"磨剑"解锁(UI 路径)',!!S.achievements['sword_start']);
  chk('成就 toast 出现',!!document.querySelector('.achievement-toast'));

  /* 7. 答题卡 */
  document.querySelector('[data-action="show-sheet"]').click();
  await sleep(200);
  chk('答题卡渲染',document.querySelectorAll('#sheetOverlay .sheet-grid .sheet-dot, #answerSheet .sheet-grid .sheet-dot, .sheet-grid [data-action="jump-to"]').length>0);
  document.querySelector('[data-action="jump-to"]').click();
  await sleep(200);
  chk('答题卡跳转',document.querySelector('section.view.active#view-quiz')!==null);

  /* 8. 返回首页 → 错题本 */
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);
  chk('返回首页',!!document.querySelector('section.view.active#view-home'));
  document.querySelector('.m-wrong').click();
  await sleep(400);
  chk('错题练习启动(quiz)',!!document.querySelector('section.view.active#view-quiz'));
  chk('错题练习=1题',S.questions.length===1,S.questions.length);
  chk('错题正是第1题',S.questions[0].id===q1.id,S.questions[0].id);

  /* 9. 返回 → 收藏练习 */
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);
  document.querySelector('.m-book').click();
  await sleep(400);
  chk('收藏练习=1题',S.questions.length===1&&S.quizMode==='bookmarked',S.questions.length+'/'+S.quizMode);

  /* 10. 返回 → 名词解释 */
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);
  document.querySelector('.m-noun').click();
  await sleep(400);
  var termCards=document.querySelectorAll('.term-card, .term-item, [class*="term"]').length;
  chk('名词解释视图渲染',termCards>0,'cards='+termCards);
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);

  /* 11. 切章 + 切课程 */
  document.querySelector('.chapter-chip[data-key="biochem_7"]').click();
  await sleep(400);
  chk('切章后回首页',!!document.querySelector('section.view.active#view-home'));
  chk('切章后 subject 更新',S.subject==='biochem_7',S.subject);
  var tagC=document.querySelector('.brand-tag[data-course="cellbiology"]');
  if(tagC)tagC.click();
  await sleep(400);
  chk('切课程后 subject 更新',S.course==='cellbiology'&&S.subject==='cellbio_1',S.course+'/'+S.subject);

  /* 12. 题型渲染遍历:判断/多选/简答 各构造单题会话 + 真实点击 */
  var bk=Q.getBank('biochem_1_2').questions;
  var findQ=function(tp){for(var i=0;i<bk.length;i++){if(bk[i].type===tp)return bk[i];}return null;};
  var tpList=['truefalse','multi','short'];
  for(var ti=0;ti<tpList.length;ti++){
    var tp=tpList[ti];
    var tq=findQ(tp);
    S.subject='biochem_1_2';S.questions=[tq];S.qIndex=0;S.answers={};S.revealed={};S.streak=0;S._multiSelection={};
    Q.invalidate();
    Q.switchView('quiz');
    await sleep(200);
    if(tp==='truefalse'){
      document.querySelector('.tf-row [data-value="'+String(tq.answer).toLowerCase()+'"]').click();
      await sleep(150);
      chk('tf 作答后 locked',document.querySelectorAll('.tf-row .tf-btn.locked').length===2);
      chk('tf 正确类渲染',!!document.querySelector('.tf-row .tf-btn.correct'));
    }else if(tp==='multi'){
      var ms=tq.answer.split('');
      for(var mi=0;mi<ms.length;mi++){document.querySelector('.option[data-value="'+ms[mi]+'"]').click();await sleep(80);}
      var mbtn=document.querySelector('.multi-confirm-btn');
      chk('multi 确认按钮启用',!!mbtn&&!mbtn.disabled);
      mbtn.click();
      await sleep(150);
      chk('multi 正确类渲染',document.querySelectorAll('.option.multi-option.correct').length===ms.length,ms.join(''));
    }else if(tp==='short'){
      var sb=document.querySelector('.short-reveal-btn');
      chk('short 显示答案按钮',!!sb);
      sb.click();
      await sleep(150);
      chk('short 答案揭示渲染',!!document.querySelector('.short-answer-reveal'));
    }
  }

  /* 13. 多选专项真实入口 */
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);
  document.querySelector('.m-multi').click();
  await sleep(400);
  var multiAll=S.questions.every(function(x){return x.type==='multi';});
  chk('多选专项启动(全 multi)',S.quizMode==='multi'&&multiAll,S.quizMode+'/'+S.questions.length+'题');
  document.querySelector('[data-action="go-home"]').click();
  await sleep(300);

  /* 14. 错误收集 */
  out.errs=(window.__errs||[]).slice();
  out.active=document.querySelector('section.view.active')?document.querySelector('section.view.active').id:null;
  return out;
})();
`;

async function main() {
  const wsUrl = await getWsUrl();
  const cdp = await connect(wsUrl);
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: INJECT });

  const loaded = new Promise(r => cdp.on('Page.loadEventFired', r));
  await cdp.send('Page.navigate', { url });
  await Promise.race([loaded, sleep(60000)]);
  await sleep(1500);

  const evalJs = async (expr) => {
    const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    if (res.exceptionDetails) throw new Error('eval exception: ' + JSON.stringify(res.exceptionDetails).slice(0, 800));
    return res.result.value;
  };

  /* ---------- 阶段 A ---------- */
  console.log('===== 阶段 A:缓存逻辑 =====');
  const a = await evalJs(PHASE_A);
  for (const c of a.checks) {
    console.log((c.ok ? '  PASS' : '  FAIL') + ' | ' + c.name + (c.extra ? ' | ' + c.extra : ''));
  }

  /* ---------- 清状态,重新加载 → 阶段 B ---------- */
  await evalJs(`localStorage.clear()`);
  await cdp.send('Page.navigate', { url });
  await Promise.race([loaded, sleep(60000)]);
  await sleep(1500);

  console.log('===== 阶段 B:UI 交互路径 =====');
  const b = await evalJs(PHASE_B);
  for (const c of b.checks) {
    console.log((c.ok ? '  PASS' : '  FAIL') + ' | ' + c.name + (c.extra ? ' | ' + c.extra : ''));
  }
  const errsB = await evalJs(`JSON.stringify(window.__errs||[])`);

  const aPass = a.pass;
  const bPass = b.pass;
  const errs = JSON.parse(errsB);
  console.log('===== 汇总 =====');
  console.log('阶段A(缓存逻辑):', aPass ? 'PASS' : 'FAIL', `(${a.checks.length} checks)`);
  console.log('阶段B(UI路径):', bPass ? 'PASS' : 'FAIL', `(${b.checks.length} checks)`);
  console.log('JS错误数:', errs.length);
  if (errs.length) console.log('错误详情:', JSON.stringify(errs, null, 1));

  cdp.close();
  proc.kill();
  setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500);
  process.exit(aPass && bPass && errs.length === 0 ? 0 : 1);
}

main().catch(e => { console.error('FAIL:', e.message); proc.kill(); setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500); process.exit(1); });
