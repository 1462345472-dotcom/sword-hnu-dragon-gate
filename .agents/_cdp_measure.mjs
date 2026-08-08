// _cdp_measure.mjs — 量化启动成本:Parse/Script 耗时 + 各遍历函数耗时
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 9444;
const HTML = process.argv[2] ? resolve(process.argv[2]) : resolve('生物化学题库/湖南大学题库系统-臻至版.html');
const url = pathToFileURL(HTML).href;
const profile = mkdtempSync(join(tmpdir(), 'edge-measure-'));

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

const INJECT = `
  window.__errs = [];
  window.addEventListener('error', function(e){ window.__errs.push('error: ' + (e.message||'') ); });
  try { localStorage.setItem('hnu_academy_visited','1'); } catch(e){}
  try { localStorage.setItem('hnu_academy_s', JSON.stringify({wrongSet:{},bookmarks:{},bestStreak:0,achievements:{},course:'biochemistry',subject:'biochem_1_2',termFilter:'all'})); } catch(e){}
`;

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

async function main() {
  const wsUrl = await getWsUrl();
  const cdp = await connect(wsUrl);
  await cdp.send('Page.enable');
  await cdp.send('Runtime.enable');
  await cdp.send('Performance.enable');
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: INJECT });
  const loaded = new Promise(r => cdp.on('Page.loadEventFired', r));
  const tStart = Date.now();
  await cdp.send('Page.navigate', { url });
  await Promise.race([loaded, sleep(60000)]);
  await sleep(1200);
  const wallMs = Date.now() - tStart;

  const metrics = await cdp.send('Performance.getMetrics');
  const md = {};
  for (const m of metrics.metrics) md[m.name] = m.value;
  const keys = ['Timestamp', 'ScriptDuration', 'ParseDuration', 'LayoutDuration', 'RecalcStyleDuration', 'TaskDuration', 'JSHeapUsedSize', 'DOMCount'];
  console.log('—— 启动度量(wall ' + wallMs + 'ms)——');
  for (const k of keys) {
    if (md[k] === undefined) { console.log(' ', k + ': n/a'); continue; }
    console.log(' ', k + ':', k === 'JSHeapUsedSize' ? Math.round(md[k] / 1048576) + 'MB' : md[k].toFixed(2));
  }

  const expr = `JSON.stringify((() => {
    const bench = (fn) => { const t0 = performance.now(); const v = fn(); return { ms: +(performance.now() - t0).toFixed(3), r: typeof v === 'number' ? v : (v && v.length !== undefined ? v.length : 'n/a') }; };
    const out = {};
    out.parseKeys = bench(() => Object.keys(__perf.QUESTION_BANKS).length);
    out.chStats_once = bench(() => { const s = __perf.chStats('biochem_1_2'); return s.t; });
    out.wrongQs_all = bench(() => __perf.wrongQs().length);
    out.bmQs_all = bench(() => __perf.bmQs().length);
    out.findBankForQ = bench(() => { const b = __perf.findBankForQ('biochem_1_2_q1'); return b ? b.key : 'miss'; });
    out.getBank_lookup = bench(() => { let x = 0; for (let i = 0; i < 1000; i++) x += __perf.getBank('biochem_7').questions.length; return x; });
    out.errs = window.__errs || [];
    return out;
  })())`;
  const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true });
  if (res.exceptionDetails) {
    console.error('EVAL异常:', JSON.stringify(res.exceptionDetails, null, 1));
    process.exit(1);
  }
  const data = JSON.parse(res.result.value);
  console.log('—— 遍历函数耗时——');
  for (const [k, v] of Object.entries(data)) {
    if (k === 'errs') continue;
    console.log(' ', k + ':', v.ms + 'ms (返回 ' + v.r + ')');
  }
  console.log('JS错误数:', data.errs.length);
  if (data.errs.length) console.log('错误:', JSON.stringify(data.errs));
  cdp.close();
  proc.kill();
  setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500);
  process.exit(0);
}

main().catch(e => { console.error('FAIL:', e.message); proc.kill(); setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500); process.exit(1); });
