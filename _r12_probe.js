/* R12 缺陷聚焦探针:清除数据后 S.answers 残留的用户可见影响 */
const {spawn} = require('child_process');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
const os = require('os');
const http = require('http');

const EDGE = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const PORT = 9367;
const FILE = path.resolve(__dirname, '生物化学题库/湖南大学题库系统-臻至版.html');
const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-r12-'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function getJson(url) {
  return new Promise((res, rej) => {
    http.get(url, (r) => { let d = ''; r.on('data', (c) => d += c); r.on('end', () => res(JSON.parse(d))); }).on('error', rej);
  });
}

async function main() {
  const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', '--no-first-run',
    '--window-size=1100,900', '--remote-debugging-port=' + PORT, '--user-data-dir=' + profile, pathToFileURL(FILE).href],
    { stdio: 'ignore' });
  let targets = null;
  for (let i = 0; i < 80; i++) {
    try { targets = await getJson('http://127.0.0.1:' + PORT + '/json'); if (targets && targets.length) break; } catch (e) {}
    await sleep(500);
  }
  const page = targets.find((t) => t.type === 'page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let nextId = 1; const pending = new Map();
  const send = (method, params = {}) => new Promise((res) => { const id = nextId++; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });
  let dialogPolicy = 'dismiss';
  ws.onmessage = (evt) => {
    const m = JSON.parse(evt.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
    else if (m.method === 'Page.javascriptDialogOpening') { send('Page.handleJavaScriptDialog', { accept: dialogPolicy === 'accept' }).catch(() => {}); }
  };
  await new Promise((r) => { ws.onopen = r; });
  await send('Runtime.enable'); await send('Page.enable');
  const ev = async (expr) => { const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true }); return r.result && r.result.result ? r.result.result.value : undefined; };
  const click = async (sel) => ev(`(function(){var el=document.querySelector('${sel}');if(!el)return false;el.click();return true;})()`);
  for (let i = 0; i < 60; i++) { try { if (await ev('window.__qa?1:0') === 1) break; } catch (e) {} await sleep(500); }

  await click('[data-action="enter"]'); await sleep(400);
  await click('.chapter-chip[data-key="biochem_1_2"]'); await sleep(300);
  await click('[data-action="start-quiz"]'); await sleep(500);
  /* 答对 2 题,制造进度 */
  await click('.option[data-value="D"]'); await sleep(350);
  await click('[data-action="nav-next"]'); await sleep(300);
  await click('.option[data-value="C"]'); await sleep(350);
  const before = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,ring:document.getElementById('ringNum')?document.getElementById('ringNum').textContent:null,pi:document.querySelector('.pi-stats')?document.querySelector('.pi-stats').textContent:null};})()`);
  await click('[data-action="go-home"]'); await sleep(400);
  const homeBefore = await ev(`(function(){return {ring:document.getElementById('ringNum')?document.getElementById('ringNum').textContent:null,pi:document.querySelector('.pi-stats')?document.querySelector('.pi-stats').textContent:null};})()`);
  /* 触发清除数据(确认) */
  await ev(`(function(){var b=document.createElement('button');b.id='c';b.setAttribute('data-action','clear-data');b.style.display='none';document.getElementById('app').appendChild(b);})()`);
  dialogPolicy = 'accept';
  await click('#c'); await sleep(600);
  const after = await ev(`(function(){var S=__qa.S;return {ans:Object.keys(S.answers).length,revealed:Object.keys(S.revealed||{}).length,wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,ring:document.getElementById('ringNum')?document.getElementById('ringNum').textContent:null,pi:document.querySelector('.pi-stats')?document.querySelector('.pi-stats').textContent:null,lsKeys:Object.keys(localStorage).filter(function(k){return k.indexOf('hnu_academy_')===0;})};})()`);
  console.log('before(quiz):', JSON.stringify(before));
  console.log('home before clear:', JSON.stringify(homeBefore));
  console.log('after clear  :', JSON.stringify(after));
  try { await send('Browser.close'); } catch (e) {}
  process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(2); });
