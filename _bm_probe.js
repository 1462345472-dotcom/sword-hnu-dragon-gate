/* 探测:章节列表、每章第一题 id、COURSES 结构、__qa 可用接口 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9348;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const URL = pathToFileURL(FILE).href;
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'bmprobe-'));
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
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };

  for (let i = 0; i < 40; i++) { try { if (await ev('window.__qa?1:0') === 1) break; } catch (e) {} await sleep(500); }

  const chs = await ev('__qa.qbKeys()');
  console.log('chapter keys:', JSON.stringify(chs));
  const info = await ev('(function(){var ks=__qa.qbKeys();var out=[];for(var i=0;i<Math.min(ks.length,6);i++){var b=__qa.getBank(ks[i]);out.push({k:ks[i],n:b.questions.length,t:(b.terms||[]).length,first:b.questions[0].id,firstType:b.questions[0].type});}return out;})()');
  console.log('first chapters:', JSON.stringify(info, null, 1));
  const qaKeys = await ev('Object.keys(window.__qa)');
  console.log('__qa keys:', JSON.stringify(qaKeys));
  const courses = await ev('(function(){try{return Object.keys(COURSES);}catch(e){return "COURSES not global: "+e.message;}})()');
  console.log('COURSES:', JSON.stringify(courses));
  try { await send('Browser.close'); } catch (e) {}
  process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(2); });
