"""
湖南大学 851 生物化学｜绪论+第一章 选择题+判断题题库 + 名词解释
"""
import json, os, base64

JSON_PATH  = r'c:\Users\Lenovo\Desktop\湖南大学\生物化学题库\绪论＋第一章\questions.json'
HTML_PATH  = r'c:\Users\Lenovo\Desktop\湖南大学\生物化学题库\绪论＋第一章\index.html'
LOGO_PATH  = r'c:\Users\Lenovo\Desktop\湖南大学-logo.svg'
TERMS_PATH = r'c:\Users\Lenovo\Desktop\湖南大学\生物化学题库\绪论＋第一章\terms.json'

with open(LOGO_PATH, 'rb') as f:
    logo_src = f'data:image/svg+xml;base64,{base64.b64encode(f.read()).decode("ascii")}'

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    all_qs = json.load(f)
with open(TERMS_PATH, 'r', encoding='utf-8') as f:
    terms = json.load(f)

qs_js = json.dumps(all_qs, ensure_ascii=False, indent=2)
terms_js = json.dumps(terms, ensure_ascii=False, indent=2)
total = len(all_qs)
choice_n = sum(1 for q in all_qs if q['type'] == 'choice')
tf_n = sum(1 for q in all_qs if q['type'] == 'truefalse')
easy_n = sum(1 for q in all_qs if q.get('difficulty') == 1)
mid_n  = sum(1 for q in all_qs if q.get('difficulty') == 2)
hard_n = sum(1 for q in all_qs if q.get('difficulty') == 3)

template = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>湖南大学 851 生物化学｜绪论+第一章 题库</title>
<style>
:root{
  --red:#8B1A2B;--red2:#A01E32;--red-light:#FDF0F2;
  --gold:#C4924A;--gold-light:#FFF8F0;
  --green:#2D8C4A;--green-light:#EDF8F0;
  --red-wrong:#D43D3D;--red-wrong-light:#FFF5F5;
  --bg:#F5F0EB;--card:#FFFCF9;--text:#1E1414;--grey:#8C7A6B;
  --border:#E8DDD3;--border2:#DDD0C2;
  --radius:16px;--radius-sm:10px;--touch:48px;
  --safe-bottom:env(safe-area-inset-bottom,12px);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:16px;-webkit-tap-highlight-color:transparent}
body{
  font-family:"PingFang SC","Microsoft YaHei","Hiragino Sans GB",-apple-system,sans-serif;
  background:linear-gradient(180deg,#F5F0EB 0%,#EDE4D8 100%);
  background-attachment:fixed;color:var(--text);min-height:100vh;line-height:1.7;
  -webkit-font-smoothing:antialiased;
}
.container{max-width:860px;margin:0 auto;padding:clamp(10px,3vw,24px) clamp(8px,3vw,20px) calc(100px + var(--safe-bottom))}

/* 湖大品牌 */
.brand{
  background:linear-gradient(135deg,#6B101D,#8B1A2B 40%,#A01E32);
  color:#fff;border-radius:var(--radius);padding:clamp(20px,4vw,32px) clamp(16px,3vw,28px);
  margin-bottom:clamp(14px,3vw,20px);box-shadow:0 6px 28px rgba(107,16,29,.25);
  position:relative;overflow:hidden;
}
.brand::after{content:'';position:absolute;top:-40px;right:-40px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.04)}
.brand-top{display:flex;align-items:center;gap:14px;margin-bottom:8px;justify-content:center;flex-wrap:wrap}
.emblem{width:clamp(48px,10vw,64px);height:clamp(48px,10vw,64px);border-radius:50%;flex-shrink:0;box-shadow:0 3px 12px rgba(0,0,0,.25);object-fit:contain;background:#fff;padding:3px}
.brand-text{text-align:left}
.brand-school{font-size:clamp(.75rem,1.8vw,.85rem);opacity:.85;letter-spacing:1px}
.brand-title{font-size:clamp(1.15rem,3.5vw,1.55rem);font-weight:800;line-height:1.3}
.brand-sub{font-size:clamp(.72rem,1.8vw,.82rem);opacity:.75;margin-top:2px}
.brand-motto{text-align:center;font-size:clamp(.82rem,2vw,.95rem);font-weight:600;letter-spacing:3px;opacity:.9;margin-top:2px;border-top:1px solid rgba(255,255,255,.15);padding-top:10px}
.brand-motto span{margin:0 8px;opacity:.5}

/* 进度条 */
.progress-wrap{background:var(--card);border-radius:var(--radius);padding:clamp(10px,2vw,14px) clamp(14px,2vw,20px);margin-bottom:clamp(12px,3vw,18px);box-shadow:0 2px 10px rgba(0,0,0,.04);display:flex;align-items:center;gap:12px;flex-wrap:wrap;border:1px solid var(--border)}
.progress-outer{flex:1;height:clamp(7px,1.5vw,9px);background:var(--border);border-radius:5px;overflow:hidden;min-width:80px}
.progress-inner{height:100%;background:linear-gradient(90deg,var(--red),var(--red2));border-radius:5px;transition:width .35s}
.progress-text{font-weight:700;font-size:clamp(.78rem,2vw,.9rem);color:var(--red);white-space:nowrap}
.progress-tag{font-size:.72rem;background:var(--red-light);color:var(--red);padding:3px 10px;border-radius:12px;font-weight:600}

/* 题目卡片 */
.card{background:var(--card);border-radius:var(--radius);padding:clamp(18px,3vw,28px) clamp(14px,3vw,28px) clamp(16px,3vw,24px);margin-bottom:clamp(10px,2vw,14px);box-shadow:0 2px 12px rgba(0,0,0,.04);border:1px solid var(--border);transition:box-shadow .2s}
.card:active{box-shadow:0 4px 18px rgba(0,0,0,.06)}
.q-head{display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap}
.q-num{font-size:.78rem;font-weight:700;color:var(--red);letter-spacing:.5px}
.q-type{font-size:.7rem;padding:2px 8px;border-radius:10px;font-weight:700}
.q-type.choice{background:var(--red-light);color:var(--red)}
.q-type.tf{background:#F0F0FF;color:#4A4AC4}
.q-diff{font-size:.7rem;padding:3px 10px;border-radius:12px;font-weight:600}
.q-diff.easy{background:var(--green-light);color:#1A5C30}
.q-diff.mid{background:var(--gold-light);color:#8B6914}
.q-diff.hard{background:var(--red-wrong-light);color:#922B21}
.q-text{font-size:clamp(.95rem,2.2vw,1.12rem);font-weight:600;margin-bottom:clamp(14px,3vw,18px);line-height:1.8}

/* 错题收藏 */
.err-toggle{font-size:.78rem;padding:5px 12px;border-radius:14px;border:1.5px solid var(--border2);cursor:pointer;font-weight:600;transition:all .15s;background:var(--card);margin-left:auto;-webkit-tap-highlight-color:transparent;user-select:none;white-space:nowrap}
.err-toggle.on{background:#FFF5F5;border-color:#E88;color:var(--red-wrong)}
.err-toggle:active{transform:scale(.95)}

/* 选项（选择题） */
.options{display:flex;flex-direction:column;gap:clamp(7px,1.5vw,9px)}
.opt{display:flex;align-items:center;padding:clamp(12px,2vw,15px) clamp(12px,2vw,18px);border:2px solid var(--border);border-radius:var(--radius-sm);cursor:pointer;transition:all .15s;font-size:clamp(.88rem,2vw,.98rem);user-select:none;min-height:var(--touch);-webkit-tap-highlight-color:transparent;background:var(--card)}
.opt:active{transform:scale(.985)}
.opt.sel{border-color:var(--red);background:var(--red-light)}
.opt.ok{border-color:var(--green);background:var(--green-light);color:#1A5C30}
.opt.bad{border-color:var(--red-wrong);background:var(--red-wrong-light);color:#922B21}
.opt.done{pointer-events:none}
.opt-letter{width:clamp(28px,6vw,34px);height:clamp(28px,6vw,34px);min-width:clamp(28px,6vw,34px);border-radius:50%;background:var(--border);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:clamp(.78rem,2vw,.85rem);margin-right:clamp(8px,2vw,12px);transition:all .15s;flex-shrink:0;color:#666}
.opt.sel .opt-letter{background:var(--red);color:#fff}
.opt.ok .opt-letter{background:var(--green);color:#fff}
.opt.bad .opt-letter{background:var(--red-wrong);color:#fff}
.opt-label{flex:1;min-width:0}

/* 判断题按钮 */
.tf-row{display:flex;gap:clamp(10px,2vw,14px)}
.tf-btn{flex:1;padding:clamp(14px,3vw,18px);border-radius:var(--radius-sm);cursor:pointer;font-weight:700;font-size:clamp(.95rem,2vw,1.05rem);text-align:center;transition:all .15s;border:2px solid var(--border);background:var(--card);-webkit-tap-highlight-color:transparent;user-select:none}
.tf-btn:active{transform:scale(.97)}
.tf-btn.t{color:var(--green)}
.tf-btn.f{color:var(--red-wrong)}
.tf-btn.sel-t{border-color:var(--green);background:var(--green-light)}
.tf-btn.sel-f{border-color:var(--red-wrong);background:var(--red-wrong-light)}
.tf-btn.ok{border-color:var(--green);background:var(--green-light);color:#1A5C30}
.tf-btn.bad{border-color:var(--red-wrong);background:var(--red-wrong-light);color:#922B21}
.tf-btn.done{pointer-events:none}

/* 解析 */
.explain{margin-top:clamp(12px,2vw,16px);padding:clamp(12px,2vw,16px) clamp(14px,2vw,18px);background:var(--gold-light);border-left:4px solid var(--gold);border-radius:0 8px 8px 0;font-size:clamp(.82rem,1.8vw,.9rem);color:#6B4C08;line-height:1.75;display:none}
.explain.show{display:block}
.lock-hint{text-align:center;font-size:.78rem;color:var(--grey);margin-top:6px;display:flex;align-items:center;justify-content:center;gap:4px}

/* 导航 */
.nav-row{display:flex;justify-content:space-between;align-items:center;margin-top:clamp(10px,2vw,16px);gap:8px}
.btn{padding:clamp(10px,2vw,13px) clamp(16px,3vw,24px);border:none;border-radius:var(--radius-sm);font-size:clamp(.82rem,2vw,.93rem);font-weight:700;cursor:pointer;transition:all .15s;white-space:nowrap;min-height:var(--touch);-webkit-tap-highlight-color:transparent}
.btn:active{transform:scale(.96)}
.btn-go{background:var(--red);color:#fff;box-shadow:0 3px 10px rgba(139,26,43,.3)}
.btn-go:active{background:var(--red2)}
.btn-go:disabled{background:#D4B8BC;cursor:not-allowed;box-shadow:none;color:#fff}
.btn-ghost{background:var(--card);color:var(--red);border:2px solid var(--red)}
.btn-ghost:disabled{border-color:var(--border2);color:var(--border2);cursor:not-allowed}
.btn-sm{padding:8px 14px;font-size:.8rem;min-height:38px;border-radius:20px}
.btn-outline-danger{background:var(--card);color:var(--red-wrong);border:2px solid var(--red-wrong)}
.btn-outline-danger:active{background:var(--red-wrong-light)}
.nav-hint{font-size:clamp(.72rem,1.6vw,.82rem);color:var(--grey);text-align:center;flex:1;font-weight:500}

@media (max-width:767px){
  .nav-row{position:fixed;bottom:0;left:0;right:0;background:var(--card);padding:10px 10px calc(10px + var(--safe-bottom));box-shadow:0 -2px 20px rgba(0,0,0,.08);z-index:100;margin-top:0;border-top:1px solid var(--border)}
  .nav-hint{display:none}
  .btn{flex:1;text-align:center}
  .container{padding-bottom:calc(110px + var(--safe-bottom))}
}

/* 首页 */
.home-card{background:var(--card);border-radius:var(--radius);padding:clamp(20px,3vw,34px);box-shadow:0 4px 20px rgba(0,0,0,.05);text-align:center;border:1px solid var(--border)}
.home-stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}
.stat-chip{background:var(--bg);border-radius:var(--radius-sm);padding:12px 18px;font-weight:700;font-size:.85rem;min-width:80px}
.stat-chip b{color:var(--red);font-size:1.2rem}
.menu-title{font-size:clamp(1rem,2.5vw,1.2rem);font-weight:800;margin-bottom:20px;color:var(--red)}
.menu-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:clamp(10px,2vw,14px);margin-bottom:20px}
.menu-item{background:var(--bg);border:2px solid var(--border);border-radius:var(--radius);padding:clamp(14px,3vw,22px);cursor:pointer;transition:all .2s;text-align:center}
.menu-item:hover,.menu-item:active{border-color:var(--red);background:var(--red-light);transform:translateY(-2px)}
.menu-icon{font-size:clamp(1.6rem,4vw,2.2rem);margin-bottom:6px}
.menu-label{font-weight:700;font-size:clamp(.85rem,2vw,.98rem);margin-bottom:3px}
.menu-count{font-size:.75rem;color:var(--grey)}

/* 错题栏 */
.err-banner{background:linear-gradient(135deg,#FFF5F5,#FFEBEB);border:2px solid #F5C6CB;border-radius:var(--radius);padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}
.err-banner .err-info{font-size:.88rem;font-weight:600;color:#922B21}
.err-banner .err-info span{color:var(--red-wrong);font-weight:800}

/* 难度/子面板 */
.diff-grid{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:14px 0}
.diff-chip{padding:10px 22px;border-radius:24px;border:2px solid var(--border);cursor:pointer;font-weight:700;font-size:.88rem;transition:all .15s;background:var(--card)}
.diff-chip:active,.diff-chip.sel{color:#fff}
.diff-chip.ez{border-color:var(--green);color:#1A5C30}
.diff-chip.ez:active,.diff-chip.ez.sel{background:var(--green);color:#fff}
.diff-chip.md{border-color:var(--gold);color:#8B6914}
.diff-chip.md:active,.diff-chip.md.sel{background:var(--gold);color:#fff}
.diff-chip.hd{border-color:var(--red-wrong);color:#922B21}
.diff-chip.hd:active,.diff-chip.hd.sel{background:var(--red-wrong);color:#fff}
.back-row{margin-top:14px}
.section-label{text-align:center;font-size:.82rem;color:var(--grey);margin-bottom:10px}

/* 结果页 */
.result-card{background:var(--card);border-radius:var(--radius);padding:clamp(22px,4vw,36px) clamp(16px,3vw,30px);text-align:center;box-shadow:0 4px 24px rgba(0,0,0,.06);border:1px solid var(--border)}
.score-circle{width:clamp(100px,25vw,140px);height:clamp(100px,25vw,140px);border-radius:50%;color:#fff;display:inline-flex;flex-direction:column;align-items:center;justify-content:center;font-size:clamp(2rem,5vw,2.8rem);font-weight:900;margin:0 auto 16px;box-shadow:0 8px 32px rgba(139,26,43,.3)}
.score-circle small{font-size:.65rem;font-weight:500;opacity:.85}
.result-card h2{font-size:clamp(1.1rem,3vw,1.3rem);margin-bottom:8px}
.grade-text{font-size:clamp(.88rem,2.2vw,1rem);margin-bottom:16px;font-weight:600}
.stats{display:flex;justify-content:center;flex-wrap:wrap;gap:clamp(10px,3vw,28px);margin:10px 0;font-size:clamp(.82rem,2vw,.93rem)}
.review-list{text-align:left;margin-top:18px;max-height:55vh;overflow-y:auto}
.review-item{padding:clamp(8px,1.5vw,11px) 12px;margin-bottom:5px;background:var(--bg);border-radius:var(--radius-sm);font-size:clamp(.78rem,1.8vw,.86rem);cursor:pointer;transition:background .15s;line-height:1.55;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.review-item:hover,.review-item:active{background:var(--red-light)}
.result-actions{display:flex;gap:10px;justify-content:center;margin-top:20px;flex-wrap:wrap}

/* 名词解释页 */
.glossary-card{background:var(--card);border-radius:var(--radius);padding:clamp(18px,3vw,28px);box-shadow:0 4px 20px rgba(0,0,0,.05);border:1px solid var(--border)}
.glossary-card h2{font-size:clamp(1.1rem,3vw,1.3rem);text-align:center;color:var(--red);margin-bottom:20px}
.glossary-chapter{font-size:.8rem;color:var(--gold);text-align:center;margin-bottom:16px;font-weight:600}
.term-block{padding:clamp(12px,2vw,16px) 0;border-bottom:1px solid var(--border)}
.term-block:last-child{border-bottom:none}
.term-name{font-weight:800;font-size:clamp(.92rem,2vw,1.02rem);color:var(--red);margin-bottom:4px}
.term-def{font-size:clamp(.82rem,1.8vw,.9rem);color:var(--text);line-height:1.8}

@media (min-width:768px){
  .container{padding:28px 20px 40px}
  .opt:hover{border-color:var(--red);background:var(--red-light)}
  .tf-btn:hover{background:var(--bg)}
  .btn-go:hover{background:var(--red2);transform:translateY(-1px);box-shadow:0 5px 16px rgba(139,26,43,.4)}
  .btn-ghost:hover{background:var(--red-light)}
  .btn-outline-danger:hover{background:var(--red-wrong-light)}
  .nav-row{position:static;box-shadow:none;background:transparent;padding:0;border-top:none}
  .container{padding-bottom:40px}
}
</style>
</head>
<body>
<div class="container">
  <div class="brand">
    <div class="brand-top">
      <img class="emblem" src="__LOGO__" alt="校徽">
      <div class="brand-text">
        <div class="brand-school">湖南大学 · HUNAN UNIVERSITY</div>
        <div class="brand-title">生物化学｜绪论+第一章 题库</div>
        <div class="brand-sub">851 生物化学与细胞生物学 · 选择题 + 判断题</div>
      </div>
    </div>
    <div class="brand-motto">实 事 求 是<span>|</span>敢 为 人 先</div>
  </div>

  <div class="progress-wrap" id="progWrap" style="display:none">
    <div class="progress-outer"><div class="progress-inner" id="progBar" style="width:0%"></div></div>
    <span class="progress-text" id="progText">0 / __TOTAL__</span>
    <span class="progress-tag" id="progDiff" style="display:none"></span>
  </div>

  <div id="quiz"></div>

  <div class="nav-row" id="navRow" style="display:none">
    <button class="btn btn-ghost btn-sm" id="btnHome">&#x1F3E0;</button>
    <button class="btn btn-ghost" id="btnPrev">&#x25C0; 上一题</button>
    <span class="nav-hint" id="navHint">请选择答案</span>
    <button class="btn btn-go" id="btnNext" disabled>下一题 &#x25B6;</button>
  </div>
</div>

<script>
(function(){
"use strict";
var ALL_QS = __QUESTIONS__;
var ALL_TERMS = __TERMS__;
var TOTAL = ALL_QS.length;
var ERR_LS = 'biochem_err_v1';
var SCORE_LS = 'biochem_score_v1';
var DIFF_NAMES = {1:'\u7b80\u5355',2:'\u4e2d\u7b49',3:'\u56f0\u96be'};
var DIFF_ICONS = {1:'\u2b50',2:'\u{1F4D6}',3:'\u{1F525}'};

var QS = ALL_QS, idx = 0, answers = {}, done = {}, autoTimer = null, viewMode = 'home';
var errSet = (function(){
  try{ var r=localStorage.getItem(ERR_LS); return r?new Set(JSON.parse(r)):new Set(); }
  catch(e){ return new Set(); }
})();
function saveErr(){ try{ localStorage.setItem(ERR_LS, JSON.stringify([...errSet])); }catch(e){} }
function toggleErr(qid){ errSet.has(qid)?errSet.delete(qid):errSet.add(qid);saveErr();var et=document.getElementById('errBtn');if(et)updateErrBtn(et,qid);}
function updateErrBtn(el,qid){el.textContent=errSet.has(qid)?'\u2b50 \u5df2\u6536\u85cf':'\u2606 \u6536\u85cf\u5230\u9519\u9898\u96c6';el.className='err-toggle'+(errSet.has(qid)?' on':'');}
function getErrCount(){return errSet.size;}
function clearErrSet(){errSet.clear();saveErr();}
function getLastScore(){try{return localStorage.getItem(SCORE_LS);}catch(e){return null;}}
function saveLastScore(s){try{localStorage.setItem(SCORE_LS,s);}catch(e){}}

var quizEl=document.getElementById('quiz'),progWrap=document.getElementById('progWrap'),progBar=document.getElementById('progBar'),progText=document.getElementById('progText'),progDiff=document.getElementById('progDiff'),navRow=document.getElementById('navRow'),navHint=document.getElementById('navHint'),btnPrev=document.getElementById('btnPrev'),btnNext=document.getElementById('btnNext'),btnHome=document.getElementById('btnHome');

function prog(){
  var n=Object.keys(done).length,t=QS.length;
  progBar.style.width=Math.round(n/t*100)+'%';progText.textContent=n+' / '+t;
  if(viewMode==='diff'&&QS[0]){progDiff.style.display='';progDiff.textContent='\ud83c\udfaf '+DIFF_NAMES[QS[0].difficulty];}
  else progDiff.style.display='none';
}
function nav(){
  btnPrev.disabled=(idx===0);
  var q=QS[idx];if(!q)return;var ad=q.id in done;
  btnNext.disabled=!ad;
  if(!ad){navHint.textContent='\ud83d\udd12 \u8bf7\u5148\u9009\u62e9\u7b54\u6848';}
  else if(idx>=QS.length-1&&Object.keys(done).length===QS.length){btnNext.textContent='\u67e5\u770b\u6210\u7ee9 \ud83c\udfc6';navHint.textContent='\u5168\u90e8\u5b8c\u6210\uff01';}
  else{btnNext.textContent='\u4e0b\u4e00\u9898 \u25b6';navHint.textContent='';}
}
function showQuizUI(){progWrap.style.display='flex';navRow.style.display='flex';viewMode='quiz';}
function hideQuizUI(){progWrap.style.display='none';navRow.style.display='none';}

// ====== 渲染 ======
function render(i){
  if(i<0||i>=QS.length){showResult();return;}
  idx=i;showQuizUI();
  var q=QS[i],sel=answers[q.id]||null,ad=q.id in done;
  var dName=DIFF_NAMES[q.difficulty],dCls=q.difficulty===1?'easy':(q.difficulty===3?'hard':'mid');
  var isTF=(q.type==='truefalse');
  var typeLabel=isTF?'\u5224\u65ad\u9898':'\u9009\u62e9\u9898';
  var typeCls=isTF?'tf':'choice';

  var h='<div class="card"><div class="q-head">';
  h+='<span class="q-num">\u7b2c '+q.id+' \u9898</span>';
  h+='<span class="q-type '+typeCls+'">'+typeLabel+'</span>';
  h+='<span class="q-diff '+dCls+'">'+DIFF_ICONS[q.difficulty]+' '+dName+'</span>';
  h+='<button class="err-toggle'+(errSet.has(q.id)?' on':'')+'" id="errBtn">'+(errSet.has(q.id)?'\u2b50 \u5df2\u6536\u85cf':'\u2606 \u6536\u85cf\u5230\u9519\u9898\u96c6')+'</button>';
  h+='</div><div class="q-text">'+q.question+'</div>';

  if (isTF){
    var tCls='tf-btn t',fCls='tf-btn f';
    if (ad){tCls+=' done';fCls+=' done';if(q.answer===true)tCls+=' ok';else fCls+=' ok';if(sel===true&&q.answer!==true)tCls+=' bad';if(sel===false&&q.answer!==false)fCls+=' bad';}
    else if(sel===true)tCls+=' sel-t';else if(sel===false)fCls+=' sel-f';
    h+='<div class="tf-row"><div class="'+tCls+'" data-v="true">\u2705 \u6b63\u786e</div><div class="'+fCls+'" data-v="false">\u274c \u9519\u8bef</div></div>';
  } else {
    h+='<div class="options">';
    ['A','B','C','D'].forEach(function(L){
      var cls='opt';if(ad){cls+=' done';if(L===q.answer)cls+=' ok';else if(L===sel&&L!==q.answer)cls+=' bad';}
      else if(L===sel)cls+=' sel';
      h+='<div class="'+cls+'" data-l="'+L+'"><span class="opt-letter">'+L+'</span><span class="opt-label">'+q.options[L]+'</span></div>';
    });
    h+='</div>';
  }
  if(ad)h+='<div class="explain show"><strong>\ud83d\udcd6 \u89e3\u6790\uff1a</strong>'+q.explanation+'</div>';
  else h+='<div class="explain" id="exp'+q.id+'"></div>';
  if(!ad)h+='<div class="lock-hint">\ud83d\udd12 \u9009\u62e9\u7b54\u6848\u540e\u624d\u80fd\u524d\u5f80\u4e0b\u4e00\u9898</div>';
  h+='</div>';
  quizEl.innerHTML=h;

  var eb=document.getElementById('errBtn');if(eb)eb.addEventListener('click',function(e){e.stopPropagation();toggleErr(q.id);});
  if(!ad){
    if (isTF){
      quizEl.querySelectorAll('.tf-btn:not(.done)').forEach(function(o){
        o.addEventListener('click',function(){pickTF(q.id,o.getAttribute('data-v')==='true');});
      });
    } else {
      quizEl.querySelectorAll('.opt:not(.done)').forEach(function(o){
        o.addEventListener('click',function(){pick(q.id,o.getAttribute('data-l'));});
      });
    }
  }
  nav();prog();
}

// ====== 选择答案 ======
function pick(qid,L){_answer(qid,L);}
function pickTF(qid,v){_answer(qid,v);}
function _answer(qid,val){
  if(qid in done)return;
  answers[qid]=val;done[qid]=true;
  var q=QS.find(function(x){return x.id===qid;});if(!q)return;
  render(idx);
  var ed=document.getElementById('exp'+qid);
  if(ed){ed.className='explain show';ed.innerHTML='<strong>\ud83d\udcd6 \u89e3\u6790\uff1a</strong>'+q.explanation;}
  prog();nav();
  clearTimeout(autoTimer);
  if(idx<QS.length-1)autoTimer=setTimeout(function(){render(idx+1);},800);
  else if(Object.keys(done).length===QS.length)autoTimer=setTimeout(function(){showResult();},600);
}

// ====== 导航 ======
function prev(){clearTimeout(autoTimer);if(idx>0)render(idx-1);}
function next(){clearTimeout(autoTimer);var q=QS[idx];if(!q||!(q.id in done))return;if(idx>=QS.length-1&&Object.keys(done).length===QS.length)showResult();else if(idx<QS.length-1)render(idx+1);}

// ====== 成绩 ======
function showResult(){
  hideQuizUI();viewMode='result';
  var cor=0,wro=0;QS.forEach(function(q){
    if(q.type==='truefalse'){if(answers[q.id]===q.answer)cor++;else if(q.id in done)wro++;return;}
    if(answers[q.id]===q.answer)cor++;else if(q.id in done)wro++;
  });
  var tot=QS.length,una=tot-cor-wro,sc=Math.round(cor/tot*100);
  saveLastScore(String(sc));
  var gd,gc;
  if(sc>=90){gd='\ud83c\udfc5 \u592a\u68d2\u4e86\uff01\u638c\u63e1\u5f97\u975e\u5e38\u624e\u5b9e\uff01';gc='#2D8C4A'}
  else if(sc>=80){gd='\ud83d\udc4d \u8868\u73b0\u4f18\u79c0\uff01\u7ee7\u7eed\u5de9\u56fa\u8584\u5f31\u77e5\u8bc6\u70b9\u3002';gc='#8B1A2B'}
  else if(sc>=70){gd='\ud83d\udcda \u826f\u597d\u6c34\u5e73\uff0c\u5efa\u8bae\u9488\u5bf9\u9519\u9898\u5f3a\u5316\u590d\u4e60\u3002';gc='#C4924A'}
  else if(sc>=60){gd='\ud83d\udcd6 \u521a\u521a\u53ca\u683c\uff0c\u9700\u8981\u7cfb\u7edf\u56de\u987e\u672c\u7ae0\u5185\u5bb9\u3002';gc='#E67E22'}
  else{gd='\ud83d\udcaa \u8fd8\u9700\u52aa\u529b\uff0c\u5efa\u8bae\u91cd\u65b0\u68b3\u7406\u77e5\u8bc6\u70b9\u540e\u518d\u505a\u4e00\u904d\u3002';gc='#D43D3D'}

  var h='<div class="result-card">';
  h+='<h2>\ud83d\udcca \u7b54\u9898\u6210\u7ee9</h2>';
  h+='<div class="score-circle" style="background:linear-gradient(135deg,'+gc+','+gc+'dd)">'+sc+'<small>\u5206</small></div>';
  h+='<p class="grade-text" style="color:'+gc+'">'+gd+'</p>';
  h+='<div class="stats"><span style="color:#2D8C4A">\u2705 \u6b63\u786e\uff1a<b>'+cor+'</b></span><span style="color:#D43D3D">\u274c \u9519\u8bef\uff1a<b>'+wro+'</b></span>';
  if(una>0)h+='<span style="color:var(--grey)">\u23ed \u672a\u7b54\uff1a<b>'+una+'</b></span>';
  h+='</div>';
  h+='<p style="margin-top:6px;font-size:.82rem;color:var(--grey)">\u2b50 \u9519\u9898\u96c6\u5df2\u6536\u85cf <b style="color:var(--red)">'+getErrCount()+'</b> \u9898\uff08\u624b\u52a8\u6536\u85cf\uff09</p>';

  h+='<div class="review-list"><h3 style="text-align:center;margin-bottom:10px">\ud83d\udccb \u9010\u9898\u56de\u987e\uff08\u70b9\u51fb\u8df3\u8f6c\uff09</h3>';
  QS.forEach(function(q){
    var ua=answers[q.id],ok=ua===q.answer;
    var icon=ua?(ok?'\u2705':'\u274c'):'\u2b1c';
    var ansLabel=q.type==='truefalse'?(q.answer?'\u2705\u6b63\u786e':'\u274c\u9519\u8bef'):q.answer;
    var uaL=q.type==='truefalse'?(ua===true?'\u6b63\u786e':(ua===false?'\u9519\u8bef':'')):ua;
    h+='<div class="review-item" data-rid="'+q.id+'">'+icon+' <b>\u7b2c'+q.id+'\u9898</b> ';
    if(ua&&!ok)h+='<span style="color:#D43D3D">\uff08\u4f60\uff1a'+uaL+'\uff0c\u6b63\u786e\uff1a'+ansLabel+'\uff09</span>';
    else if(ua)h+='<span style="color:#2D8C4A">\uff08'+uaL+'\uff09</span>';
    else h+='<span style="color:var(--grey)">\uff08\u672a\u4f5c\u7b54\uff09</span>';
    h+='</div>';
  });
  h+='</div>';

  h+='<div class="result-actions">';
  h+='<button class="btn btn-go" id="btnRetry">\ud83d\udd04 \u91cd\u65b0\u505a\u9898</button>';
  if(wro>0)h+='<button class="btn btn-outline-danger" id="btnWrong">\ud83d\udcdd \u53ea\u505a\u9519\u9898</button>';
  h+='<button class="btn btn-ghost" id="btnHome2">\ud83c\udfe0 \u8fd4\u56de\u9996\u9875</button>';
  h+='</div></div>';
  quizEl.innerHTML=h;
  document.getElementById('btnRetry').addEventListener('click',retrySame);
  var bw=document.getElementById('btnWrong');if(bw)bw.addEventListener('click',doWrongOnly);
  document.getElementById('btnHome2').addEventListener('click',showHome);
  quizEl.querySelectorAll('.review-item').forEach(function(el){el.addEventListener('click',function(){reviewOne(parseInt(el.getAttribute('data-rid')));});});
}
function reviewOne(qid){viewMode='quiz';var found=-1;QS.forEach(function(q,i){if(q.id===qid)found=i;});if(found>=0)render(found);window.scrollTo({top:0,behavior:'smooth'});}
function retrySame(){idx=0;answers={};done={};quizEl.innerHTML='';showQuizUI();prog();render(0);}
function doWrongOnly(){var wl=QS.filter(function(q){return(q.id in done)&&answers[q.id]!==q.answer;});if(!wl.length){alert('\u6ca1\u6709\u9519\u9898\uff01\ud83c\udf89');return;}QS=wl;idx=0;answers={};done={};showQuizUI();prog();render(0);}

// ====== 首页 ======
function showHome(){
  hideQuizUI();viewMode='home';QS=ALL_QS;idx=0;answers={};done={};
  var errCount=getErrCount(),lastScore=getLastScore();
  var h='<div class="home-card">';
  if(lastScore){h+='<div class="home-stats"><div class="stat-chip">\ud83d\udcca \u4e0a\u6b21\u6210\u7ee9<br><b>'+lastScore+'\u5206</b></div><div class="stat-chip">\u2b50 \u9519\u9898\u96c6<br><b>'+errCount+'\u9898</b></div><div class="stat-chip">\ud83d\udcda \u9898\u5e93\u603b\u8ba1<br><b>'+TOTAL+'\u9898</b></div></div>';}
  h+='<div class="menu-title">\u27a1 \u9009\u62e9\u7ec3\u4e60\u6a21\u5f0f</div>';
  if(errCount>0){h+='<div class="err-banner"><span class="err-info">\ud83d\udccb \u4f60\u7684\u9519\u9898\u96c6\u4e2d\u6709 <span>'+errCount+'</span> \u9898\u5f85\u590d\u4e60</span><button class="btn btn-sm btn-outline-danger" id="btnClearErr">\u6e05\u7a7a\u9519\u9898\u96c6</button></div>';}
  h+='<div class="menu-grid">';
  h+='<div class="menu-item" id="menuAll"><div class="menu-icon">\ud83d\udcdd</div><div class="menu-label">\u5168\u90e8\u5237\u9898</div><div class="menu-count">\u5168\u90e8 '+TOTAL+' \u9898\uff08\u9009\u62e9+\u5224\u65ad\uff09</div></div>';
  h+='<div class="menu-item" id="menuChoice"><div class="menu-icon">\ud83d\udcda</div><div class="menu-label">\u9009\u62e9\u9898\u4e13\u9879</div><div class="menu-count">'+__CHOICE_N__+' \u9898\uff08A/B/C/D\uff09</div></div>';
  h+='<div class="menu-item" id="menuTF"><div class="menu-icon">\u2696\ufe0f</div><div class="menu-label">\u5224\u65ad\u9898\u4e13\u9879</div><div class="menu-count">'+__TF_N__+' \u9898\uff08\u6b63\u786e/\u9519\u8bef\uff09</div></div>';
  h+='<div class="menu-item" id="menuErr"><div class="menu-icon">\u2b50</div><div class="menu-label">\u6211\u7684\u9519\u9898\u96c6</div><div class="menu-count">'+errCount+' \u9898\uff08\u624b\u52a8\u6536\u85cf\uff09</div></div>';
  h+='<div class="menu-item" id="menuDiff"><div class="menu-icon">\ud83c\udfaf</div><div class="menu-label">\u6309\u96be\u5ea6\u5237\u9898</div><div class="menu-count">\u7b80\u5355('+__EASY__+') / \u4e2d\u7b49('+__MID__+') / \u56f0\u96be('+__HARD__+')</div></div>';
  h+='<div class="menu-item" id="menuGlossary"><div class="menu-icon">\ud83d\udcd6</div><div class="menu-label">\u540d\u8bcd\u89e3\u91ca</div><div class="menu-count">\u7eea\u8bba+\u7b2c\u4e00\u7ae0 \u00b7 '+__TERMS_N__+' \u6761</div></div>';
  h+='</div>';
  h+='<div id="diffPanel" style="display:none"><div class="section-label">\u9009\u62e9\u96be\u5ea6</div><div class="diff-grid"><div class="diff-chip ez" data-d="1">\u2b50 \u7b80\u5355\uff08'+__EASY__+'\uff09</div><div class="diff-chip md" data-d="2">\ud83d\udcd6 \u4e2d\u7b49\uff08'+__MID__+'\uff09</div><div class="diff-chip hd" data-d="3">\ud83d\udd25 \u56f0\u96be\uff08'+__HARD__+'\uff09</div></div><div class="back-row"><button class="btn btn-ghost btn-sm" id="btnDiffBack">\u2190 \u8fd4\u56de</button></div></div>';
  h+='<p style="margin-top:16px;font-size:.75rem;color:var(--grey)">\u2b50 \u70b9\u51fb\u2621\u53ef\u624b\u52a8\u6536\u85cf/\u53d6\u6d88\u9519\u9898 \u00b7 \u9010\u9898\u4f5c\u7b54\u624d\u80fd\u524d\u8fdb \u00b7 Esc\u56de\u9996\u9875 \u00b7 \u5de6\u53f3\u6ed1\u52a8\u5207\u9898</p>';
  h+='</div>';
  quizEl.innerHTML=h;

  document.getElementById('menuAll').addEventListener('click',function(){QS=ALL_QS;startQuiz();});
  document.getElementById('menuChoice').addEventListener('click',function(){QS=ALL_QS.filter(function(q){return q.type==='choice';});startQuiz();});
  document.getElementById('menuTF').addEventListener('click',function(){QS=ALL_QS.filter(function(q){return q.type==='truefalse';});startQuiz();});
  document.getElementById('menuErr').addEventListener('click',startErr);
  document.getElementById('menuDiff').addEventListener('click',function(){document.getElementById('diffPanel').style.display='block';document.querySelector('.menu-grid').style.display='none';var eb=document.querySelector('.err-banner');if(eb)eb.style.display='none';var hs=document.querySelector('.home-stats');if(hs)hs.style.display='none';});
  document.getElementById('menuGlossary').addEventListener('click',showGlossary);
  document.getElementById('btnDiffBack').addEventListener('click',showHome);
  var ec=document.getElementById('btnClearErr');if(ec)ec.addEventListener('click',function(){if(confirm('\u786e\u5b9a\u6e05\u7a7a\u6240\u6709\u9519\u9898\u8bb0\u5f55\uff1f')){clearErrSet();showHome();}});
  document.querySelectorAll('.diff-chip').forEach(function(c){c.addEventListener('click',function(){QS=ALL_QS.filter(function(q){return q.difficulty===parseInt(c.getAttribute('data-d'));});viewMode='diff';startQuiz();});});
}
function startQuiz(){viewMode='quiz';idx=0;answers={};done={};showQuizUI();prog();render(0);}
function startErr(){if(errSet.size===0){alert('\u9519\u9898\u96c6\u4e3a\u7a7a\uff0c\u70b9\u51fb\u2621\u53ef\u624b\u52a8\u6536\u85cf\u9519\u9898\uff01');return;}QS=ALL_QS.filter(function(q){return errSet.has(q.id);});startQuiz();}

// ====== 名词解释 ======
function showGlossary(){
  hideQuizUI();viewMode='glossary';
  var h='<div class="glossary-card"><h2>\ud83d\udcd6 \u540d\u8bcd\u89e3\u91ca</h2>';
  h+='<p class="glossary-chapter">\u7eea\u8bba+\u7b2c\u4e00\u7ae0 \u00b7 \u5171 '+ALL_TERMS.length+' \u6761</p>';
  ALL_TERMS.forEach(function(t){
    h+='<div class="term-block"><div class="term-name">'+t.id+'. '+t.term+'</div><div class="term-def">'+t.definition+'</div></div>';
  });
  h+='<div style="text-align:center;margin-top:24px"><button class="btn btn-ghost" id="btnGlossBack">\u2190 \u8fd4\u56de\u9996\u9875</button></div>';
  h+='</div>';
  quizEl.innerHTML=h;
  document.getElementById('btnGlossBack').addEventListener('click',showHome);
}

// ====== 按钮/键盘/触摸 ======
btnPrev.addEventListener('click',prev);
btnNext.addEventListener('click',next);
btnHome.addEventListener('click',function(){clearTimeout(autoTimer);showHome();});
document.addEventListener('keydown',function(e){
  if(navRow.style.display==='none')return;var q=QS[idx];if(!q)return;
  if(!(q.id in done)){
    if(q.type==='truefalse'){if(e.key==='1'||e.key==='t'){e.preventDefault();pickTF(q.id,true);}if(e.key==='2'||e.key==='f'){e.preventDefault();pickTF(q.id,false);}}
    else{var km={'1':'A','2':'B','3':'C','4':'D','a':'A','b':'B','c':'C','d':'D'};if(e.key in km){e.preventDefault();pick(q.id,km[e.key]);}}
  }
  if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();prev();}
  if((e.key==='ArrowRight'||e.key==='ArrowDown')&&(q.id in done)){e.preventDefault();next();}
  if(e.key==='Enter'&&(q.id in done)){e.preventDefault();next();}
  if(e.key==='Escape'||e.key==='h'){e.preventDefault();showHome();}
});
var tx=0,ty=0;
document.addEventListener('touchstart',function(e){tx=e.touches[0].clientX;ty=e.touches[0].clientY;},{passive:true});
document.addEventListener('touchend',function(e){if(navRow.style.display==='none')return;var dx=e.changedTouches[0].clientX-tx,dy=e.changedTouches[0].clientY-ty;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)){if(dx<-30)next();else if(dx>30)prev();}});

showHome();
})();
</script>
</body>
</html>"""

# 替换
html = template.replace('__QUESTIONS__', qs_js)
html = html.replace('__TERMS__', terms_js)
html = html.replace('__LOGO__', logo_src)
html = html.replace('__TOTAL__', str(total))
html = html.replace('__CHOICE_N__', str(choice_n))
html = html.replace('__TF_N__', str(tf_n))
html = html.replace('__TERMS_N__', str(len(terms)))
html = html.replace('__EASY__', str(easy_n))
html = html.replace('__MID__', str(mid_n))
html = html.replace('__HARD__', str(hard_n))

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'OK: index.html ({os.path.getsize(HTML_PATH)/1024:.1f} KB)')
print(f'   选择题:{choice_n} 判断题:{tf_n} 总计:{total} 名词解释:{len(terms)}')
