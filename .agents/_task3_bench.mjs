// _task3_bench.mjs — 缓存收益量化:20 次调用 全量 vs 缓存命中
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 9335;
const HTML = resolve('生物化学题库/湖南大学题库系统-臻至版.html');
const url = pathToFileURL(HTML).href;
const profile = mkdtempSync(join(tmpdir(), 'edge-t3b-'));
const proc = spawn(EDGE, ['--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
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
  throw new Error('CDP not reachable');
}
function connect(wsUrl) {
  return new Promise((res_, rej) => {
    const ws = new WebSocket(wsUrl);
    let id = 0;
    const pending = new Map();
    const listeners = new Map();
    ws.onopen = () => res_({
      send(method, params = {}) {
        return new Promise((res, rej2) => {
          const mid = ++id;
          pending.set(mid, { res, rej: rej2 });
          ws.send(JSON.stringify({ id: mid, method, params }));
        });
      },
      on(method, cb) { listeners.set(method, cb); },
      close() { ws.close(); }
    });
    ws.onmessage = ev => {
      const msg = JSON.parse(ev.data);
      if (msg.id && pending.has(msg.id)) {
        const { res, rej2 } = pending.get(msg.id);
        pending.delete(msg.id);
        msg.error ? rej2(new Error(msg.error.message)) : res(msg.result);
      } else if (msg.method && listeners.has(msg.method)) {
        listeners.get(msg.method)(msg.params);
      }
    };
  });
}
const INJECT = `try { localStorage.setItem('hnu_academy_visited','1'); } catch(e){}`;

async function main() {
  const cdp = await connect(await getWsUrl());
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: INJECT });
  const loaded = new Promise(r => cdp.on('Page.loadEventFired', r));
  await cdp.send('Page.navigate', { url });
  await Promise.race([loaded, sleep(60000)]);
  await sleep(1500);
  const evalJs = async expr => {
    const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (res.exceptionDetails) throw new Error('eval exception: ' + JSON.stringify(res.exceptionDetails).slice(0, 500));
    return res.result.value;
  };
  const r = await evalJs(`(function(){
    var Q=window.__qa,S=Q.S;
    S.subject='biochem_1_2';
    var qs=Q.getBank('biochem_1_2').questions;
    S.questions=qs;S.qIndex=0;S.answers={};S.revealed={};S.streak=0;S.wrongSet={};S.bookmarks={};
    var kf=function(id){return Q.ak('biochem_1_2',id);};
    var i;
    for(i=0;i<30;i++){S.wrongSet[kf(qs[i].id)]=true;}
    for(i=0;i<20;i++){S.bookmarks[kf(qs[i].id)]=true;}
    var bench=function(fn,N){var t0=performance.now();for(var i=0;i<N;i++)fn();return (performance.now()-t0)/N;};
    // 全量(每次失效)
    var wCold=bench(function(){Q.invalidate();Q.wrongQs();},5);
    var bCold=bench(function(){Q.invalidate();Q.bmQs();},5);
    var aCold=bench(function(){Q.invalidate();Q.checkAchievements();},5);
    // 缓存命中(预热后)
    Q.invalidate();Q.wrongQs();Q.bmQs();Q.checkAchievements();
    var wHot=bench(function(){Q.wrongQs();},50);
    var bHot=bench(function(){Q.bmQs();},50);
    var aHot=bench(function(){Q.checkAchievements();},50);
    // 真实交互链:答对 20 题中 checkAchievements 总耗时(增量维护)
    var t0=performance.now();
    for(i=0;i<20;i++){S.qIndex=i;var q=qs[i];if(!S.answers[kf(q.id)]){S.answers[kf(q.id)]=(q.type==='truefalse'?String(q.answer).toLowerCase():(q.type==='short'?'done':q.answer));if(Q.achCnt()!==null){}Q.checkAchievements();}}
    var aInc=performance.now()-t0;
    return {wrongQs_cold_ms:wCold.toFixed(2),wrongQs_hot_ms:wHot.toFixed(3),
            bmQs_cold_ms:bCold.toFixed(2),bmQs_hot_ms:bHot.toFixed(3),
            checkAch_cold_ms:aCold.toFixed(2),checkAch_hot_ms:aHot.toFixed(3),
            ach_20answers_incremental_ms:aInc.toFixed(2)};
  })()`);
  console.log('=== 缓存收益量化(平均每次调用耗时) ===');
  console.log('wrongQs        冷(全量):' + r.wrongQs_cold_ms + 'ms → 热(缓存):' + r.wrongQs_hot_ms + 'ms');
  console.log('bmQs           冷(全量):' + r.bmQs_cold_ms + 'ms → 热(缓存):' + r.bmQs_hot_ms + 'ms');
  console.log('checkAchievements 冷(全量):' + r.checkAch_cold_ms + 'ms → 热(缓存):' + r.checkAch_hot_ms + 'ms');
  console.log('答对20题期间 checkAchievements 总耗时(增量):' + r.ach_20answers_incremental_ms + 'ms');
  cdp.close(); proc.kill();
  setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500);
  process.exit(0);
}
main().catch(e => { console.error('FAIL:', e.message); proc.kill(); process.exit(1); });
