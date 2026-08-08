// _cdp_check.mjs — Edge headless + CDP:模拟老用户(localStorage visited=1),校验 51 章节键 + JS 错误
// 用法: node _cdp_check.mjs [html路径]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const EDGE = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';
const PORT = 9333;
const HTML = process.argv[2] ? resolve(process.argv[2]) : resolve('生物化学题库/湖南大学题库系统-臻至版.html');
const url = pathToFileURL(HTML).href;
const profile = mkdtempSync(join(tmpdir(), 'edge-cdp-'));

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
  window.addEventListener('unhandledrejection', function(e){ window.__errs.push('rejection: ' + (e.reason||'') ); });
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
  await cdp.send('Page.addScriptToEvaluateOnNewDocument', { source: INJECT });

  const loaded = new Promise(r => cdp.on('Page.loadEventFired', r));
  await cdp.send('Page.navigate', { url });
  await Promise.race([loaded, sleep(60000)]);

  await sleep(1500); // 等 init 后渲染(含 animate-in timeout)

  const evalJs = async (expr) => {
    const res = await cdp.send('Runtime.evaluate', { expression: expr, returnByValue: true });
    if (res.exceptionDetails) throw new Error('eval exception: ' + JSON.stringify(res.exceptionDetails));
    return res.result.value;
  };

  const getChips = () => `JSON.stringify(Array.from(document.querySelectorAll('#view-home [data-key]')).map(e => e.getAttribute('data-key')).sort())`;
  const getErr = () => `JSON.stringify(window.__errs || [])`;

  const chips1 = JSON.parse(await evalJs(getChips()));
  const errs1 = JSON.parse(await evalJs(getErr()));

  // 模拟点击:切换到细胞生物学课程
  const r2 = await evalJs(`(() => {
    const tag = document.querySelector('.brand-tag[data-course="cellbiology"]');
    if (tag) { tag.click(); return 'clicked'; }
    return 'notfound';
  })()`);
  await sleep(600);
  const chips2 = JSON.parse(await evalJs(getChips()));
  const errs2 = JSON.parse(await evalJs(getErr()));

  // 模拟点击:切换章节 biochem_7
  const r3 = await evalJs(`(() => {
    const chip = document.querySelector('.chapter-chip[data-key="biochem_7"]');
    if (chip) { chip.click(); return 'clicked'; }
    return 'notfound';
  })()`);
  await sleep(600);
  const chips3 = JSON.parse(await evalJs(getChips()));
  const errs3 = JSON.parse(await evalJs(getErr()));

  const all = [...new Set([...chips1, ...chips2, ...chips3])].sort();
  const errs = [...errs1, ...errs2, ...errs3];
  const active = await evalJs(`(() => { const a = document.querySelector('section.view.active'); return a ? a.id : null; })()`);

  console.log('切换课程(cellbio):', r2, '| 切换章节(biochem_7):', r3);
  console.log('课程1(biochem)章节键:', chips1.length, '| 课程2(cellbio)章节键:', chips2.length);
  console.log('切换后仍在home:', active);
  console.log('章节键并集数量:', all.length);
  console.log('JS错误数:', errs.length);
  if (errs.length) console.log('错误详情:', JSON.stringify(errs, null, 1));
  cdp.close();
  proc.kill();
  setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500);
  process.exit(errs.length === 0 && all.length === 51 && active === 'view-home' ? 0 : 1);
}

main().catch(e => { console.error('FAIL:', e.message); proc.kill(); setTimeout(() => { try { rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch {} }, 500); process.exit(1); });
