// Task 4 分章存储 CDP 功能验证:通过 window.__qa 钩子 + 真实 DOM 点击驱动臻至版
// 覆盖:旧数据迁移 / 做题写块 / 书签写块 / reload 恢复 / 续练恢复 / 清除数据
const http = require('http');
const PORT = 9333;

function httpGet(path) {
  return new Promise((resolve, reject) => {
    http.get({host: '127.0.0.1', port: PORT, path}, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    }).on('error', reject);
  });
}

async function main() {
  let targets = null;
  for (let i = 0; i < 50; i++) {
    try { targets = JSON.parse(await httpGet('/json/list')); if (targets.length) break; } catch (e) {}
    await new Promise(r => setTimeout(r, 300));
  }
  if (!targets || !targets.length) throw new Error('CDP target not available');
  const page = targets.find(t => t.type === 'page');
  if (!page) throw new Error('no page target');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let id = 0;
  const pending = new Map();
  const loadWaiters = [];
  let defaultCtx = null;
  let mainFrameId = null;
  const ctxCache = [];
  const pageErrors = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.rej(new Error(JSON.stringify(m.error))) : p.res(m.result);
    } else if (m.method === 'Page.loadEventFired') {
      const w = loadWaiters.shift(); if (w) w();
    } else if (m.method === 'Runtime.executionContextCreated') {
      const c = m.params.context;
      if (c.auxData && c.auxData.isDefault === true) {
        ctxCache.push(c);
        if (mainFrameId !== null && c.auxData.frameId === mainFrameId) defaultCtx = c.id;
      }
    } else if (m.method === 'Runtime.exceptionThrown') {
      try { pageErrors.push(String(m.params.exceptionDetails.exception.description || m.params.exceptionDetails.text).slice(0, 200)); } catch (err) {}
    }
  };
  function send(method, params) {
    return new Promise((res, rej) => {
      const i = ++id; pending.set(i, {res, rej});
      ws.send(JSON.stringify({id: i, method, params}));
    });
  }
  async function ev(expr) {
    const params = {expression: expr, returnByValue: true, awaitPromise: true};
    if (defaultCtx) params.contextId = defaultCtx;
    const r = await send('Runtime.evaluate', params);
    if (r.exceptionDetails) throw new Error('EVAL EXC: ' + JSON.stringify(r.exceptionDetails).slice(0, 600));
    return r.result ? r.result.value : undefined;
  }
  async function reload() {
    const w = new Promise(res => loadWaiters.push(res));
    await send('Page.reload', {ignoreCache: true});
    await w;
    await new Promise(r => setTimeout(r, 400));
  }

  await send('Page.enable', {});
  await send('Runtime.enable', {});
  const ft = await send('Page.getFrameTree', {});
  mainFrameId = ft.frameTree.frame.id;
  for (let i = 0; i < 50 && defaultCtx === null; i++) {
    for (const c of ctxCache) {
      if (c.auxData && c.auxData.frameId === mainFrameId && c.auxData.isDefault === true) defaultCtx = c.id;
    }
    if (defaultCtx === null) await new Promise(r => setTimeout(r, 100));
  }
  if (defaultCtx === null) throw new Error('main frame default context not found');

  // ===== 阶段 1:预置旧单块格式数据,reload 触发迁移 =====
  const seeded = await ev(`(function(){
    try{
      localStorage.clear();
      var wrong={};wrong['biochem_15__old_w1']=true;wrong['cellbio_3__old_w2']=true;
      var bm={};bm['biochem_15__old_b1']=true;
      localStorage.setItem('hnu_academy_s',JSON.stringify({wrongSet:wrong,bookmarks:bm,bestStreak:7,
        achievements:{sword_start:true},course:'生物化学',subject:'biochem_15',termFilter:'all'}));
      var prog={};prog['biochem_15|all']={qIndex:2,answers:{'biochem_15__old_a1':'A'},
        revealed:{'biochem_15__old_a1':true},streak:1,timestamp:'2026-01-01T00:00:00.000Z'};
      localStorage.setItem('hnu_academy_progress',JSON.stringify(prog));
      localStorage.setItem('hnu_academy_visited','1');
      return 'SEEDED';
    }catch(e){return 'SEED_ERR:'+e.message;}
  })()`);
  await reload();

  // ===== 阶段 2:迁移断言 + 做题 + 书签 + 分章键断言(全部走 __qa + 真实点击) =====
  const s2 = await ev(`(function(){
    var out={};
    function R(n,v){out[n]=v;}
    try{
      var Q=window.__qa,S=Q.S;
      R('qa_ok',!!S&&typeof Q.startQuiz==='function'&&typeof Q.submitAnswer==='function');
      R('banks',Object.keys(Q.getBank?{x:1}:(S.banks||{})).length>0);
      R('mig_wrong',S.wrongSet['biochem_15__old_w1']===true&&S.wrongSet['cellbio_3__old_w2']===true);
      R('mig_bm',S.bookmarks['biochem_15__old_b1']===true);
      R('mig_prog',!!(S.savedProgress['biochem_15|all']&&S.savedProgress['biochem_15|all'].answers['biochem_15__old_a1']==='A'));
      R('mig_meta',S.bestStreak===7&&S.achievements.sword_start===true); /* subject 恢复沿用原版:仅当 S.subject 为空时生效 */
      R('mig_meta_detail',JSON.stringify({bs:S.bestStreak,ach:S.achievements,subj:S.subject}));
      var keys=[];for(var i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
      R('has_prog',keys.indexOf('hnu_academy_prog_biochem_15')>=0);
      R('has_wrong',keys.indexOf('hnu_academy_wrong_biochem_15')>=0);
      R('has_bm',keys.indexOf('hnu_academy_bm_biochem_15')>=0);
      R('has_meta',keys.indexOf('hnu_academy_meta')>=0);
      R('old_gone',keys.indexOf('hnu_academy_s')<0&&keys.indexOf('hnu_academy_progress')<0);
      var prog=JSON.parse(localStorage.getItem('hnu_academy_prog_biochem_15'));
      R('blk_prog',!!(prog.all&&prog.all.answers['biochem_15__old_a1']==='A'&&prog.all.qIndex===2));
      var wb=JSON.parse(localStorage.getItem('hnu_academy_wrong_biochem_15'));
      var wb2=JSON.parse(localStorage.getItem('hnu_academy_wrong_cellbio_3'));
      R('blk_wrong',wb.old_w1===true&&wb2&&wb2.old_w2===true);
      // 做题:通过 __qa 真实函数路径(必答错)
      var b=window.__qa_getBank?null:null;
      var q=null;
      // getBank 不在 __qa 时从 S 侧取:通过 __qa.ak 无帮助,直接读 QUESTION_BANKS? IIFE 内不可见。
      // 用暴露的 startQuiz 后 S.questions[0] 作为当前题
      Q.startQuiz('biochem_15','all');
      q=S.questions[0];
      var ua=q.type==='truefalse'?(q.answer?'false':'true'):'x';
      Q.submitAnswer(q.id,ua);
      Q.submitAnswer(q.id,ua);
      // 书签:真实 DOM 点击委托路径
      window.confirm=function(){return true;};
      var btn=document.createElement('button');btn.setAttribute('data-action','toggle-bookmark');
      document.getElementById('app').appendChild(btn);btn.click();btn.remove();
      var prog2=JSON.parse(localStorage.getItem('hnu_academy_prog_biochem_15'));
      R('ans_written',!!(prog2.all&&prog2.all.answers['biochem_15__'+q.id]===ua&&Object.keys(prog2.all.answers).length===1)); /* answers 为当前会话覆盖,与原版一致 */
      var wb3=JSON.parse(localStorage.getItem('hnu_academy_wrong_biochem_15'));
      R('wrong_written',wb3[q.id]===true);
      var bb=JSON.parse(localStorage.getItem('hnu_academy_bm_biochem_15'));
      R('bm_written',bb[q.id]===true);
      R('other_intact',JSON.parse(localStorage.getItem('hnu_academy_wrong_cellbio_3')).old_w2===true);
      R('mem_ok',S.wrongSet['biochem_15__'+q.id]===true&&S.bookmarks['biochem_15__'+q.id]===true&&Object.keys(S.answers).length===1);
      var meta=JSON.parse(localStorage.getItem('hnu_academy_meta'));
      R('meta_ok',!!(meta&&typeof meta.bestStreak==='number'));
      window.__t4qid=q.id;
      R('qid',q.id);R('ua',ua);R('keys',keys);
    }catch(e){R('EXC',String(e)+' @ '+(e.stack||''));}
    return JSON.stringify(out);
  })()`);

  await reload();

  // ===== 阶段 3:reload 恢复 + 续练恢复(真实 UI 路径)+ 清除数据(真实 UI 路径) =====
  let qidFromS2 = null;
  try { qidFromS2 = JSON.parse(s2).qid; } catch (e) {}
  const s3 = await ev(`(function(){
    var out={};
    function R(n,v){out[n]=v;}
    var qid=${qidFromS2};
    try{
      var Q=window.__qa,S=Q.S;
      R('rest_wrong',S.wrongSet['biochem_15__old_w1']===true&&S.wrongSet['cellbio_3__old_w2']===true&&S.wrongSet['biochem_15__'+qid]===true);
      R('rest_bm',S.bookmarks['biochem_15__old_b1']===true&&S.bookmarks['biochem_15__'+qid]===true);
      R('rest_prog',!!(S.savedProgress['biochem_15|all']&&S.savedProgress['biochem_15|all'].answers['biochem_15__'+qid]!==undefined));
      R('rest_meta',S.bestStreak===7&&S.achievements.sword_start===true);
      // 续练恢复:真实 UI 点击(start-quiz → confirm true → resume)
      window.confirm=function(){return true;};
      var btn2=document.createElement('button');btn2.setAttribute('data-action','start-quiz');btn2.setAttribute('data-key','biochem_15');
      document.getElementById('app').appendChild(btn2);btn2.click();btn2.remove();
      R('resume_subj',S.subject==='biochem_15');
      R('resume_ans',S.answers['biochem_15__'+qid]!==undefined);
      R('resume_qIndex',typeof S.qIndex==='number');
      // 清除数据:真实 UI 点击(confirm true)
      var btn3=document.createElement('button');btn3.setAttribute('data-action','clear-data');
      document.getElementById('app').appendChild(btn3);btn3.click();btn3.remove();
      var keys=[];for(var i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
      var has=false;for(var j=0;j<keys.length;j++){
        if(keys[j].indexOf('hnu_academy_prog_')===0||keys[j].indexOf('hnu_academy_wrong_')===0||keys[j].indexOf('hnu_academy_bm_')===0
          ||keys[j]==='hnu_academy_s'||keys[j]==='hnu_academy_progress')has=true;
      }
      R('cleared',!has); /* meta 会由 saveState 重写为空状态,与原版 clear-data 行为一致 */
      R('mem_cleared',Object.keys(S.wrongSet).length===0&&Object.keys(S.bookmarks).length===0&&Object.keys(S.savedProgress).length===0&&S.bestStreak===0);
      R('keys',keys);
    }catch(e){R('EXC',String(e)+' @ '+(e.stack||''));}
    return JSON.stringify(out);
  })()`);

  console.log('===STAGE2===');
  console.log(s2);
  console.log('===STAGE3===');
  console.log(s3);
  // ===== 阶段 4(I-1):迁移落盘写失败 → 旧键保留;恢复后下次加载重试成功 =====
  await ev(`(function(){
    try{
      localStorage.clear();
      var wrong={};wrong['biochem_15__old_w1']=true;
      localStorage.setItem('hnu_academy_s',JSON.stringify({wrongSet:wrong,bookmarks:{},bestStreak:3,
        achievements:{},course:'生物化学',subject:'biochem_15',termFilter:'all'}));
      localStorage.setItem('hnu_academy_progress',JSON.stringify({'biochem_15|all':{qIndex:1,
        answers:{'biochem_15__old_a1':'A'},revealed:{},streak:0,timestamp:'2026-01-01T00:00:00.000Z'}}));
      localStorage.setItem('hnu_academy_visited','1');
      return 'SEEDED4';
    }catch(e){return 'SEED4_ERR:'+e.message;}
  })()`);
  const scr = await send('Page.addScriptToEvaluateOnNewDocument',
    {source: 'try{localStorage.setItem=function(k,v){throw new Error("QUOTA_TEST");};}catch(e){}'});
  await reload();
  const s4a = await ev(`(function(){
    var out={};
    var keys=[];for(var i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
    out.old_keys_kept = keys.indexOf('hnu_academy_s')>=0 && keys.indexOf('hnu_academy_progress')>=0;
    out.new_keys_absent = keys.indexOf('hnu_academy_meta')<0 && keys.indexOf('hnu_academy_prog_biochem_15')<0;
    var Q=window.__qa,S=Q.S;
    out.mem_merged = S.wrongSet['biochem_15__old_w1']===true &&
      !!(S.savedProgress['biochem_15|all']&&S.savedProgress['biochem_15|all'].answers['biochem_15__old_a1']==='A');
    out.keys = keys;
    return JSON.stringify(out);
  })()`);
  await send('Page.removeScriptToEvaluateOnNewDocument', {identifier: scr.identifier});
  await reload();
  const s4b = await ev(`(function(){
    var out={};
    var keys=[];for(var i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
    out.old_gone = keys.indexOf('hnu_academy_s')<0 && keys.indexOf('hnu_academy_progress')<0;
    out.new_present = keys.indexOf('hnu_academy_meta')>=0 && keys.indexOf('hnu_academy_prog_biochem_15')>=0;
    var wb=JSON.parse(localStorage.getItem('hnu_academy_wrong_biochem_15')||'{}');
    out.data_intact = wb.old_w1===true;
    var Q=window.__qa,S=Q.S;
    out.mem_intact = S.wrongSet['biochem_15__old_w1']===true && S.bestStreak===3;
    return JSON.stringify(out);
  })()`);
  console.log('===STAGE4A(写失败时旧键保留)===');
  console.log(s4a);
  console.log('===STAGE4B(恢复后迁移重试成功)===');
  console.log(s4b);

  console.log('===PAGE_ERRORS===');
  console.log(JSON.stringify(pageErrors));
  ws.close();
  process.exit(0);
}

main().catch(e => { console.error('CDP FAIL:', e.message); process.exit(1); });
