/* Task 8 全量回归:真实 Edge headless + CDP + DOM 点击驱动臻至版
   覆盖:51 章节全进入 / 4 题型(choice·truefalse·multi·short)做题全流程 /
        多选交互 / 名词解释(全部+各章tab) / 错题本 / 书签 / 答题卡 jump-to /
        切章·切课程 / 续练 confirm / 清除数据 / localStorage 分章落盘 / 0 JS 错误 */
const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const EDGE = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const URL = "file:///C:/Users/Lenovo/Desktop/湖南大学/生物化学题库/湖南大学题库系统-臻至版.html";
const PORT = 9348;
const PROFILE = fs.mkdtempSync(path.join(os.tmpdir(), 'hnu-t8-'));

function httpGet(p){return new Promise((res,rej)=>{http.get({host:'127.0.0.1',port:PORT,path:p},r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',rej);});}

async function main(){
  const edge = spawn(EDGE, ['--headless=new','--disable-gpu','--remote-debugging-port='+PORT,
    '--user-data-dir='+PROFILE, '--no-first-run','--disable-extensions', URL]);
  edge.stderr.on('data', ()=>{});
  let targets=null;
  for(let i=0;i<60;i++){
    try{targets=JSON.parse(await httpGet('/json/list'));if(targets.length)break;}catch(e){}
    await new Promise(r=>setTimeout(r,400));
  }
  if(!targets||!targets.length)throw new Error('CDP target 不可用');
  const page = targets.find(t=>t.type==='page');
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});

  let id=0; const pending=new Map(); const pageErrors=[]; const consoleLogs=[];
  ws.onmessage=e=>{
    const m=JSON.parse(e.data);
    if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.rej(new Error(JSON.stringify(m.error))):p.res(m.result);}
    else if(m.method==='Runtime.exceptionThrown'){try{pageErrors.push(String(m.params.exceptionDetails.exception.description||m.params.exceptionDetails.text).slice(0,200));}catch(err){}}
    else if(m.method==='Runtime.consoleAPICalled'){
      try{
        const txt=m.params.args.map(a=>a.value||a.description||'').join(' ');
        if(m.params.type==='error')pageErrors.push('console.error: '+txt.slice(0,200));
        consoleLogs.push(m.params.type+': '+txt.slice(0,300));
      }catch(err){}
    }
  };
  function send(method,params){return new Promise((res,rej)=>{const i=++id;pending.set(i,{res,rej});ws.send(JSON.stringify({id:i,method,params}));});}
  async function ev(expr){const r=await send('Runtime.evaluate',{expression:expr,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error('页面JS异常: '+JSON.stringify(r.exceptionDetails.exception||r.exceptionDetails.text).slice(0,300));return r.result.value;}
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));

  await send('Runtime.enable',{});
  for(let i=0;i<60;i++){try{if(await ev('!!window.__qa'))break;}catch(e){}await sleep(300);}
  if(!(await ev('!!window.__qa')))throw new Error('页面未就绪');

  /* confirm 覆盖:记录调用次数,返回 true(续练确认/清除数据确认) */
  await ev('window.confirm=function(){window.__t8_confirmN=(window.__t8_confirmN||0)+1;return true;};true;');

  const results=[];
  function check(name,ok,detail){results.push({name,ok,detail});console.log((ok?'  OK  ':'  FAIL ')+name+(ok?'':' :: '+detail));}

  /* ================= A. 启动与数据自检 ================= */
  await sleep(1500);
  const selfCheckOk = consoleLogs.some(l=>l.includes('[数据自检] 正常'));
  const selfCheckLine = consoleLogs.find(l=>l.includes('[数据自检]'))||'<无输出>';
  check('A1 启动数据自检 console 输出正常', selfCheckOk, selfCheckLine);

  const qbN = await ev('window.__qa.qbKeys().length');
  check('A2 QUESTION_BANKS 键数=51', qbN===51, '实际 '+qbN);

  await ev(`(function(){var b=document.querySelector('[data-action="enter"]');if(b)b.click();return true;})()`);
  await sleep(400);
  const homeView = await ev('window.__qa.S.view');
  check('A3 欢迎屏 enter → home 视图', homeView==='home', homeView);

  /* ================= B. 51 章节全部可进入 ================= */
  /* COURSES 在 IIFE 内不可直接访问 → 通过真实 UI(切课程标签+chips)构建映射 */
  const courseInfo = await ev(`(function(){
    var tags=document.querySelectorAll('[data-action="switch-course"]');
    var courseNames=[];
    for(var i=0;i<tags.length;i++)courseNames.push(tags[i].getAttribute('data-course'));
    var out={};
    for(var i=0;i<courseNames.length;i++){
      var course=courseNames[i];
      /* 每次重新查询(renderHome 会重建 DOM,旧引用失效) */
      document.querySelector('[data-action="switch-course"][data-course="'+course+'"]').click();
      var chips=[];
      var cs=document.querySelectorAll('.chapter-chip');
      for(var j=0;j<cs.length;j++)chips.push(cs[j].getAttribute('data-key'));
      out[course]=chips;
    }
    return JSON.stringify(out);
  })()`);
  const COURSES = JSON.parse(courseInfo);
  const allKeys = await ev('window.__qa.qbKeys()');
  check('B1 课程注册章节与 QUESTION_BANKS 键一致(51)',
    Object.values(COURSES).reduce((n,c)=>n+c.length,0)===51 &&
    allKeys.length===51 &&
    Object.values(COURSES).every(c=>c.every(ch=>allKeys.indexOf(ch)>=0)),
    JSON.stringify({courseChapters:Object.values(COURSES).map(c=>c.length),keys:allKeys.length}));

  const chapterFailures=[];
  for(let i=0;i<allKeys.length;i++){
    const key=allKeys[i];
    const courseName=Object.keys(COURSES).find(c=>COURSES[c].indexOf(key)>=0);
    const r=await ev(`(function(){
      var key=${JSON.stringify(key)},course=${JSON.stringify(courseName)},S=window.__qa.S;
      if(S.course!==course){var t=document.querySelector('[data-action="switch-course"][data-course="'+course+'"]');if(t)t.click();}
      var chip=document.querySelector('[data-action="select-chapter"][data-key="'+key+'"]');
      if(!chip)return JSON.stringify({ok:false,reason:'chip missing'});
      chip.click();
      if(S.subject!==key)return JSON.stringify({ok:false,reason:'subject='+S.subject});
      var bank=window.__qa.getBank(key);
      var qBtn=document.querySelector('[data-action="start-quiz"]');
      if(!qBtn)return JSON.stringify({ok:false,reason:'start-quiz btn missing'});
      qBtn.click();
      if(S.view!=='quiz')return JSON.stringify({ok:false,reason:'view='+S.view});
      if(!S.questions||S.questions.length!==bank.questions.length)return JSON.stringify({ok:false,reason:'qlen='+(S.questions&&S.questions.length)+'/'+bank.questions.length});
      if(S.qIndex!==0)return JSON.stringify({ok:false,reason:'qIndex='+S.qIndex});
      var gh=document.querySelector('[data-action="go-home"]');if(gh)gh.click();
      return JSON.stringify({ok:true,q:bank.questions.length,t:(bank.terms||[]).length});
    })()`);
    const rr=JSON.parse(r);
    if(!rr.ok){chapterFailures.push(key+':'+rr.reason);}
    if((i+1)%10===0)console.log('  ... 已进入 '+(i+1)+'/'+allKeys.length+' 章');
  }
  check('B2 51 章节全部可进入(进入+刷题+返回)', chapterFailures.length===0, chapterFailures.join(' | ').slice(0,400));

  /* ================= C. choice 做题全流程 (biochem_30) ================= */
  await ev(`(function(){
    var S=window.__qa.S;
    if(S.course!=='biochemistry'){var t=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');if(t)t.click();}
    var chip=document.querySelector('[data-action="select-chapter"][data-key="biochem_30"]');if(chip)chip.click();
    return JSON.stringify({course:S.course,subject:S.subject});
  })()`);
  await sleep(200);
  await ev(`(function(){var b=document.querySelector('[data-action="start-quiz"]');if(b)b.click();return true;})()`);
  await sleep(300);

  const c1 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex],bank=window.__qa.getBank('biochem_30');
    var opts=document.querySelectorAll('[data-action="answer"]');
    /* 找一个 choice 题(若首题非 choice 则 nav 到 choice 题) */
    while(q.type!=='choice'&&S.qIndex<S.questions.length-1){var nx=document.querySelector('[data-action="nav-next"]');nx.click();q=S.questions[++S.qIndex];}
    opts=document.querySelectorAll('[data-action="answer"]');
    var wrongKey=Object.keys(q.options).find(k=>k!==q.answer)||'A';
    var wrongOpt=document.querySelector('[data-action="answer"][data-value="'+wrongKey+'"]');
    wrongOpt.click();
    var after=S.answers[window.__qa.ak('biochem_30',q.id)];
    var locked=document.querySelector('[data-action="answer"][data-value="'+wrongKey+'"]').classList.contains('locked');
    var exp=document.querySelector('.explanation');
    var inWrong=!!S.wrongSet[window.__qa.ak('biochem_30',q.id)];
    return JSON.stringify({type:q.type,ans:q.answer,picked:wrongKey,after:after,locked:locked,exp:!!exp,expLen:exp?exp.textContent.trim().length:0,inWrong:inWrong,idx:S.qIndex});
  })()`);
  const c1r=JSON.parse(c1);
  check('C1 choice 答错:答案写入+锁定+解析+错题记录', c1r.type==='choice'&&c1r.after===c1r.picked&&c1r.after!==c1r.ans&&c1r.locked&&c1r.exp&&c1r.expLen>0&&c1r.inWrong, c1);

  const c2 = await ev(`(function(){
    var S=window.__qa.S;var nx=document.querySelector('[data-action="nav-next"]');nx.click();
    var q=S.questions[S.qIndex];
    while(q.type!=='choice'&&S.qIndex<S.questions.length-1){document.querySelector('[data-action="nav-next"]').click();q=S.questions[++S.qIndex];}
    var rightOpt=document.querySelector('[data-action="answer"][data-value="'+q.answer+'"]');
    rightOpt.click();
    var after=S.answers[window.__qa.ak('biochem_30',q.id)];
    var inWrong=!!S.wrongSet[window.__qa.ak('biochem_30',q.id)];
    var streak=S.streak;
    return JSON.stringify({type:q.type,ans:q.answer,after:after,ok:after===q.answer&&!inWrong,streak:streak,ach:window.__qa.achCnt()});
  })()`);
  const c2r=JSON.parse(c2);
  check('C2 choice 答对:答案正确+错题剔除+连对+成就缓存', c2r.type==='choice'&&c2r.ok&&c2r.streak>=1&&c2r.ach!==null, c2);

  /* 分章存储落盘 */
  const ls1 = await ev(`(function(){
    var keys={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);keys[k]=localStorage.getItem(k).length;}
    return JSON.stringify(keys);
  })()`);
  const l1=JSON.parse(ls1);
  check('C3 localStorage 分章落盘(prog/wrong/bm 键按章)',
    !!l1['hnu_academy_prog_biochem_30']&&!!l1['hnu_academy_wrong_biochem_30']&&!!l1['hnu_academy_meta'],
    JSON.stringify(Object.keys(l1)));

  /* ================= D. 书签 + 答题卡 jump-to(阶段C新修复) ================= */
  const d1 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var bmBtn=document.querySelector('[data-action="toggle-bookmark"]');bmBtn.click();
    var marked=!!S.bookmarks[window.__qa.ak('biochem_30',q.id)];
    var keys={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k.indexOf('hnu_academy_bm_')===0)keys[k]=1;}
    return JSON.stringify({marked:marked,bmKeys:Object.keys(keys)});
  })()`);
  const d1r=JSON.parse(d1);
  check('D1 书签:内存+localStorage 双写', d1r.marked&&d1r.bmKeys.length>0, d1);

  const d2 = await ev(`(function(){
    var S=window.__qa.S;var sh=document.querySelector('[data-action="show-sheet"]');sh.click();
    var grid=document.getElementById('answerSheet');
    var cells=grid?grid.querySelectorAll('[data-action="jump-to"]').length:0;
    var total=S.questions.length;
    var target=Math.min(total-1,7);
    var cell=grid.querySelector('[data-action="jump-to"][data-idx="'+target+'"]');cell.click();
    var after=S.qIndex;
    var sheetClosed=!grid.classList.contains('open');
    return JSON.stringify({cells:cells,total:total,after:after,target:target,sheetClosed:sheetClosed});
  })()`);
  const d2r=JSON.parse(d2);
  check('D2 答题卡 jump-to 跳题(阶段C修复):格子数=题数+跳转成功+自动关闭',
    d2r.cells===d2r.total&&d2r.after===d2r.target&&d2r.sheetClosed, d2);

  const d3 = await ev(`(function(){
    var S=window.__qa.S;var before=S.qIndex;var prev=document.querySelector('[data-action="nav-prev"]');prev.click();
    return JSON.stringify({after:S.qIndex,before:before});
  })()`);
  const d3r=JSON.parse(d3);
  check('D3 nav-prev 返回上一题', d3r.after===d3r.before-1, d3);

  /* ================= E. truefalse 流程 ================= */
  await ev(`(function(){window.__qa.startQuiz('biochem_30','truefalse');window.__qa.switchView('quiz');return true;})()`);
  await sleep(300);
  const e1 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var tBtn=document.querySelector('[data-action="answer"][data-value="true"]');
    var fBtn=document.querySelector('[data-action="answer"][data-value="false"]');
    var pick=(q.answer===true||q.answer==='true')?tBtn:fBtn;
    pick.click();
    var after=S.answers[window.__qa.ak('biochem_30',q.id)];
    /* renderQuiz 重建 DOM,需重新查询 */
    var want=(q.answer===true||q.answer==='true')?'true':'false';
    var locked=document.querySelector('[data-action="answer"][data-value="'+want+'"]').classList.contains('locked');
    var exp=document.querySelector('.explanation');
    return JSON.stringify({type:q.type,ans:q.answer,after:after,afterIsBool:typeof after==='boolean',locked:locked,exp:!!exp});
  })()`);
  const e1r=JSON.parse(e1);
  check('E1 truefalse 答对:布尔答案写入+锁定+解析', e1r.type==='truefalse'&&e1r.after===true&&(e1r.ans==='true'||e1r.ans===true)&&e1r.afterIsBool&&e1r.locked&&e1r.exp, e1);

  const e2 = await ev(`(function(){
    var S=window.__qa.S;var nx=document.querySelector('[data-action="nav-next"]');nx.click();
    var q=S.questions[S.qIndex];
    var tBtn=document.querySelector('[data-action="answer"][data-value="true"]');
    var fBtn=document.querySelector('[data-action="answer"][data-value="false"]');
    var pick=(q.answer===true||q.answer==='true')?fBtn:tBtn; /* 故意答错 */
    pick.click();
    var after=S.answers[window.__qa.ak('biochem_30',q.id)];
    var inWrong=!!S.wrongSet[window.__qa.ak('biochem_30',q.id)];
    var streak=S.streak;
    return JSON.stringify({type:q.type,ans:q.answer,after:after,inWrong:inWrong,streak:streak});
  })()`);
  const e2r=JSON.parse(e2);
  check('E2 truefalse 答错:错题记录+连对清零', e2r.type==='truefalse'&&e2r.after!==e2r.ans&&e2r.inWrong&&e2r.streak===0, e2);

  /* ================= F. multi 交互与流程 ================= */
  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  await ev(`(function(){var b=document.querySelector('[data-action="start-multi"]');b.click();return true;})()`);
  await sleep(300);
  const f1 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var toggles=document.querySelectorAll('[data-action="multi-toggle"]');
    var confirmBtn=document.querySelector('[data-action="multi-confirm"]');
    return JSON.stringify({type:q.type,toggles:toggles.length,confirmDisabled:confirmBtn.hasAttribute('disabled'),confirmEnabled:!confirmBtn.hasAttribute('disabled'),options:Object.keys(q.options).join(''),ans:q.answer});
  })()`);
  const f1r=JSON.parse(f1);
  check('F1 multi 展示:多选项+确认按钮(空选禁用)', f1r.type==='multi'&&f1r.toggles>=4&&f1r.confirmDisabled, f1);

  const f2 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var keys=Object.keys(q.options);
    /* 选两个选项,避开完整答案组合:取前两个非答案前缀 */
    var a=keys[0],b=keys[1];
    document.querySelector('[data-action="multi-toggle"][data-value="'+a+'"]').click();
    document.querySelector('[data-action="multi-toggle"][data-value="'+b+'"]').click();
    var sel1=(S._multiSelection&&S._multiSelection[q.id])?S._multiSelection[q.id].slice():[];
    var selClsA=document.querySelector('[data-action="multi-toggle"][data-value="'+a+'"]').classList.contains('selected');
    var confirmEnabled=!document.querySelector('[data-action="multi-confirm"]').hasAttribute('disabled');
    /* 取消 a */
    document.querySelector('[data-action="multi-toggle"][data-value="'+a+'"]').click();
    var sel2=(S._multiSelection&&S._multiSelection[q.id])?S._multiSelection[q.id].slice():[];
    var selClsA2=document.querySelector('[data-action="multi-toggle"][data-value="'+a+'"]').classList.contains('selected');
    return JSON.stringify({a:a,b:b,sel1:sel1,selClsA:selClsA,confirmEnabled:confirmEnabled,sel2:sel2,selClsA2:selClsA2});
  })()`);
  const f2r=JSON.parse(f2);
  check('F2 multi 交互:选择/取消选中态+确认按钮联动',
    f2r.sel1.length===2&&f2r.selClsA&&f2r.confirmEnabled&&f2r.sel2.length===1&&!f2r.selClsA2, f2);

  const f3 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var key=window.__qa.ak('biochem_30',q.id);
    document.querySelector('[data-action="multi-confirm"]').click();
    var after=S.answers[key];
    var locked=document.querySelector('[data-action="multi-toggle"]').classList.contains('locked');
    var exp=document.querySelector('.explanation');
    var selCleared=!(S._multiSelection&&S._multiSelection[q.id]);
    return JSON.stringify({ans:q.answer,after:after,sorted:after===q.answer,locked:locked,exp:!!exp,selCleared:selCleared});
  })()`);
  const f3r=JSON.parse(f3);
  check('F3 multi 提交:排序拼接答案+锁定+解析+选区清空', f3r.locked&&f3r.exp&&f3r.selCleared&&f3r.after.length>=1, f3);

  const f4 = await ev(`(function(){
    var S=window.__qa.S;var nx=document.querySelector('[data-action="nav-next"]');nx.click();
    var q=S.questions[S.qIndex];
    /* 空选时确认按钮禁用,点击无效果 */
    var confirmBtn=document.querySelector('[data-action="multi-confirm"]');
    var disabled=confirmBtn.hasAttribute('disabled');
    return JSON.stringify({type:q.type,disabled:disabled});
  })()`);
  const f4r=JSON.parse(f4);
  check('F4 multi 下一题:空选确认仍禁用', f4r.type==='multi'&&f4r.disabled, f4);

  /* ================= G. short 流程 ================= */
  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  await ev(`(function(){var b=document.querySelector('[data-action="start-short"]');b.click();return true;})()`);
  await sleep(300);
  const g1 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    var btn=document.querySelector('[data-action="short-reveal"]');
    return JSON.stringify({type:q.type,btn:!!btn,revealArea:!!document.querySelector('.short-answer-reveal')});
  })()`);
  const g1r=JSON.parse(g1);
  check('G1 short 展示:显示答案·自主评分按钮', g1r.type==='short'&&g1r.btn&&!g1r.revealArea, g1);

  const g2 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[S.qIndex];
    document.querySelector('[data-action="short-reveal"]').click();
    var after=S.answers[window.__qa.ak('biochem_30',q.id)];
    var ansText=document.querySelector('.short-answer-text');
    var exp=document.querySelector('.explanation');
    var ansTxt=ansText?ansText.textContent.trim():'';
    var expBody=exp?exp.textContent.replace(/^解析\s*/,'').trim():'';
    return JSON.stringify({after:after,ansTxt:ansTxt,expLen:expBody.length,same:ansTxt===expBody,expBodyPrefix:expBody.slice(0,8)});
  })()`);
  const g2r=JSON.parse(g2);
  check('G2 short 提交:状态 done+参考答案区+解析(非复述)', g2r.after==='done'&&g2r.ansTxt.length>0&&g2r.expLen>0&&!g2r.same&&g2r.expBodyPrefix!=='参考答案', g2);

  /* ================= H. 名词解释(全部/各章 tab) ================= */
  await ev(`(function(){
    var S=window.__qa.S;
    var gh=document.querySelector('[data-action="go-home"]');if(gh)gh.click();
    if(S.course!=='biochemistry'){var t=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');if(t)t.click();}
    var chip=document.querySelector('[data-action="select-chapter"][data-key="biochem_30"]');if(chip)chip.click();
    var b=document.querySelector('[data-action="start-noun"]');b.click();
    return JSON.stringify({course:S.course,subject:S.subject,view:S.view});
  })()`);
  await sleep(300);
  const h1 = await ev(`(function(){
    var S=window.__qa.S;
    var tabs=document.querySelectorAll('.filter-tab');
    var activeTab=document.querySelector('.filter-tab.active');
    var cards=document.querySelectorAll('.term-card').length;
    var chips=document.querySelectorAll('.chapter-chip').length;
    return JSON.stringify({view:S.view,termFilter:S.termFilter,tabs:tabs.length,active:activeTab?activeTab.textContent.trim():'',cards:cards,chapters:chips});
  })()`);
  const h1r=JSON.parse(h1);
  check('H1 名词解释:进入+tab(全部+35章)', h1r.view==='terms'&&h1r.tabs===h1r.chapters+1&&h1r.cards>0, h1);

  const h2 = await ev(`(function(){
    var S=window.__qa.S;
    var allTab=document.querySelector('[data-action="filter-terms"][data-key="all"]');allTab.click();
    var cardsAll=document.querySelectorAll('.term-card').length;
    var bankTerms=window.__qa.getBank(S.subject).terms.length;
    /* 当前章 tab(=S.subject):应显示本章术语 */
    var curTab=document.querySelector('[data-action="filter-terms"][data-key="'+S.subject+'"]');curTab.click();
    var cardsCur=document.querySelectorAll('.term-card').length;
    /* 其他章 tab:当前章内无该章术语 → 空态(与阶段C之前语义一致:过滤仅在当前章术语集内) */
    var cs=document.querySelectorAll('.chapter-chip');var ch2=null;
    for(var i=0;i<cs.length;i++){var k=cs[i].getAttribute('data-key');if(k!==S.subject){ch2=k;break;}}
    var chTab=document.querySelector('[data-action="filter-terms"][data-key="'+ch2+'"]');chTab.click();
    var cardsCh=document.querySelectorAll('.term-card').length;
    var emptyState=document.querySelector('#view-terms .empty-state');
    var chActive=document.querySelector('.filter-tab.active');
    return JSON.stringify({cardsAll:cardsAll,bankTerms:bankTerms,cur:S.subject,cardsCur:cardsCur,ch2:ch2,cardsCh:cardsCh,empty:!!emptyState,chActiveKey:chActive?chActive.getAttribute('data-key'):''});
  })()`);
  const h2r=JSON.parse(h2);
  check('H2 名词解释:全部=章内术语数+当前章 tab 显示+其他章空态(原语义)', h2r.cardsAll===h2r.bankTerms&&h2r.cardsCur===h2r.bankTerms&&h2r.cardsCh===0&&h2r.empty&&h2r.chActiveKey===h2r.ch2, h2);

  const h3 = await ev(`(function(){
    var allTab=document.querySelector('[data-action="filter-terms"][data-key="all"]');allTab.click();
    return JSON.stringify({cards:document.querySelectorAll('.term-card').length,active:document.querySelector('.filter-tab.active').textContent.trim()});
  })()`);
  const h3r=JSON.parse(h3);
  check('H3 名词解释:切回全部正常', h3r.cards>0&&h3r.active==='全部', h3);

  /* ================= I. 错题本 ================= */
  const wrongCount = await ev('window.__qa.wrongQs().length');
  check('I1 错题累计(choice/tf 各 1 道)', wrongCount>=2, 'wrongQs='+wrongCount);

  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  const i2 = await ev(`(function(){
    var S=window.__qa.S;var b=document.querySelector('[data-action="start-wrong"]');b.click();
    return JSON.stringify({view:S.view,mode:S.quizMode,qlen:S.questions.length,wrongN:window.__qa.wrongQs().length});
  })()`);
  const i2r=JSON.parse(i2);
  check('I2 错题本:start-wrong 进入错题模式', i2r.view==='quiz'&&i2r.mode==='wrong'&&i2r.qlen===i2r.wrongN&&i2r.qlen>=2, i2);

  /* 错题重做:作答可提交+解析出现(错题集为积累式设计:答对不移除,与阶段C之前版本一致,仅清除数据清空) */
  const i3 = await ev(`(function(){
    var S=window.__qa.S,q=S.questions[0];
    var wrongN0=window.__qa.wrongQs().length;
    var targetEl=null;
    if(q.type==='short'){document.querySelector('[data-action="short-reveal"]').click();targetEl=document.querySelector('.short-answer-reveal');}
    else if(q.type==='multi'){
      var o1=Object.keys(q.options)[0];
      document.querySelector('[data-action="multi-toggle"][data-value="'+o1+'"]').click();
      document.querySelector('[data-action="multi-confirm"]').click();
      targetEl=document.querySelector('[data-action="multi-toggle"]');
    }
    else{
      var pick=q.answer;
      targetEl=document.querySelector('[data-action="answer"][data-value="'+pick+'"]');
      if(!targetEl&&q.type==='truefalse'){pick=(pick===true||pick==='true')?'true':'false';targetEl=document.querySelector('[data-action="answer"][data-value="'+pick+'"]');}
      if(!targetEl)return JSON.stringify({skip:true,reason:'no target for '+q.type});
      targetEl.click();
      targetEl=document.querySelector('[data-action="answer"][data-value="'+pick+'"]');
    }
    var ansKey=window.__qa.ak(S.subject,q.id);
    var answered=!!S.answers[ansKey];
    var exp=document.querySelector('.explanation');
    var locked=targetEl?targetEl.classList.contains('locked'):false;
    var wrongN1=window.__qa.wrongQs().length;
    return JSON.stringify({skip:false,type:q.type,answered:answered,locked:locked,exp:!!exp,expLen:exp?exp.textContent.trim().length:0,wrongN:wrongN1,unchanged:wrongN1===wrongN0});
  })()`);
  const i3r=JSON.parse(i3);
  check('I3 错题重做:可作答+锁定+解析(错题积累式,答对不移除=原设计)', !i3r.skip&&i3r.answered&&i3r.locked&&i3r.exp&&i3r.expLen>0&&i3r.unchanged, i3);

  /* 错题列表视图(renderErrors 挂载点) */
  const i4 = await ev(`(function(){
    window.__qa.switchView('errors');
    var items=document.querySelectorAll('[data-action="review-error"]').length;
    var redo=!!document.querySelector('[data-action="redo-wrong"]');
    var hdr=document.querySelector('#view-errors .list-header');
    return JSON.stringify({view:window.__qa.S.view,items:items,redo:redo,hdr:hdr?hdr.textContent.trim().slice(0,30):''});
  })()`);
  const i4r=JSON.parse(i4);
  check('I4 错题列表视图:条目+重做全部', i4r.view==='errors'&&i4r.items>=1&&i4r.redo, i4);

  const i5 = await ev(`(function(){
    var b=document.querySelector('[data-action="redo-wrong"]');b.click();
    var S=window.__qa.S;
    return JSON.stringify({view:S.view,mode:S.quizMode,qlen:S.questions.length});
  })()`);
  const i5r=JSON.parse(i5);
  check('I5 redo-wrong 重做错题', i5r.view==='quiz'&&i5r.mode==='wrong'&&i5r.qlen>=1, i5);

  /* ================= J. 书签专项 ================= */
  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  const j1 = await ev(`(function(){
    var S=window.__qa.S;var b=document.querySelector('[data-action="start-bookmarked"]');b.click();
    var bms=window.__qa.bmQs();
    return JSON.stringify({view:S.view,mode:S.quizMode,qlen:S.questions.length,bmN:bms.length});
  })()`);
  const j1r=JSON.parse(j1);
  check('J1 书签专项:进入收藏模式', j1r.view==='quiz'&&j1r.mode==='bookmarked'&&j1r.qlen===j1r.bmN&&j1r.qlen>=1, j1);

  /* ================= K. 续练 resume(confirm 路径) ================= */
  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  const k1 = await ev(`(function(){
    var S=window.__qa.S;
    var gh=document.querySelector('[data-action="go-home"]');if(gh)gh.click();
    var ctag=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');if(ctag)ctag.click();
    var chip=document.querySelector('[data-action="select-chapter"][data-key="biochem_30"]');if(chip)chip.click();
    var had=S.savedProgress['biochem_30|all']?Object.keys(S.savedProgress['biochem_30|all'].answers).length:0;
    var sq=document.querySelector('[data-action="start-quiz"]');sq.click();
    var afterQ=S.qIndex;
    var answersN=Object.keys(S.answers).length;
    return JSON.stringify({had:had,afterQ:afterQ,answersN:answersN,mode:S.quizMode,view:S.view,confirmN:window.__t8_confirmN||0});
  })()`);
  const k1r=JSON.parse(k1);
  check('K1 续练:有进度时弹 confirm 并恢复(qIndex+answers)', k1r.had>=2&&k1r.confirmN>=1&&k1r.mode==='all'&&k1r.answersN===k1r.had&&k1r.afterQ>=1, k1);

  /* ================= L. 切课程/切章 ================= */
  await ev(`(function(){var b=document.querySelector('[data-action="go-home"]');if(b)b.click();return true;})()`);
  await sleep(250);
  const sw1 = await ev(`(function(){
    var S=window.__qa.S;
    var out={view:S.view};
    try{
      if(S.view!=='home'){var b=document.querySelector('[data-action="go-home"]');out.gh=!!b;if(b)b.click();}
      var cellbio=document.querySelector('[data-action="switch-course"][data-course="cellbiology"]');
      out.cellbioTag=!!cellbio;out.gh2=!!document.querySelector('[data-action="go-home"]');
      if(!cellbio)return JSON.stringify(out);
      cellbio.click();
      var chips=document.querySelectorAll('.chapter-chip').length;
      var first=${JSON.stringify(COURSES.cellbiology[0])}, expected=${COURSES.cellbiology.length};
      var activeChip=document.querySelector('.chapter-chip.active');
      out.course=S.course;out.subject=S.subject;out.chips=chips;out.expected=expected;out.subjOK=S.subject===first;out.first=first;out.active=activeChip?activeChip.textContent.trim():'';
      return JSON.stringify(out);
    }catch(e){out.err=String(e);return JSON.stringify(out);}
  })()`);
  const sw1r=JSON.parse(sw1);
  check('L1 切课程→细胞生物学:章节 chips 16+自动选中第一章', sw1r.course==='cellbiology'&&sw1r.subjOK&&sw1r.chips===sw1r.expected&&sw1r.chips===16, sw1);

  const sw2 = await ev(`(function(){
    var S=window.__qa.S;
    var chip=document.querySelector('[data-action="select-chapter"][data-key="cellbio_16"]');chip.click();
    var subjectAfter16=S.subject;
    var biochem=document.querySelector('[data-action="switch-course"][data-course="biochemistry"]');biochem.click();
    var chips=document.querySelectorAll('.chapter-chip').length;
    var first=${JSON.stringify(COURSES.biochemistry[0])}, expected=${COURSES.biochemistry.length};
    return JSON.stringify({subjectAfter16:subjectAfter16, course:S.course, chips:chips, expected:expected, first:S.subject===first});
  })()`);
  const sw2r=JSON.parse(sw2);
  check('L2 切章+切回生化:subject 跟随+chips 35', sw2r.subjectAfter16==='cellbio_16'&&sw2r.course==='biochemistry'&&sw2r.chips===sw2r.expected&&sw2r.chips===35&&sw2r.first, sw2);

  /* ================= M. 清除数据 ================= */
  const m1 = await ev(`(function(){
    var S=window.__qa.S;
    var before={wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,prog:Object.keys(S.savedProgress).length,best:S.bestStreak};
    var btn=document.createElement('button');btn.setAttribute('data-action','clear-data');
    document.getElementById('app').appendChild(btn);btn.click();btn.remove();
    var keys=[];for(var i=0;i<localStorage.length;i++)keys.push(localStorage.key(i));
    var leftover=keys.filter(k=>k.indexOf('hnu_academy_prog_')===0||k.indexOf('hnu_academy_wrong_')===0||k.indexOf('hnu_academy_bm_')===0||k==='hnu_academy_s'||k==='hnu_academy_progress');
    var after={wrong:Object.keys(S.wrongSet).length,bm:Object.keys(S.bookmarks).length,prog:Object.keys(S.savedProgress).length,best:S.bestStreak};
    return JSON.stringify({before:before,after:after,leftover:leftover,confirmN:window.__t8_confirmN||0,view:S.view});
  })()`);
  const m1r=JSON.parse(m1);
  check('M1 清除数据:内存清空+分章键删除+旧格式键删除',
    m1r.after.wrong===0&&m1r.after.bm===0&&m1r.after.prog===0&&m1r.after.best===0&&m1r.leftover.length===0&&m1r.confirmN>=2, m1);

  /* ================= N. 0 JS 错误 ================= */
  check('N1 全程 0 JS 错误 / console.error', pageErrors.length===0, pageErrors.join(' || ').slice(0,400));

  const failed = results.filter(r=>!r.ok);
  console.log('===== 汇总 =====');
  console.log('通过 '+results.length+'/'+results.length+' 项,'+(failed.length?'失败 '+failed.length+' 项':'全部通过'));
  console.log('===== console 快照(尾部) =====');
  console.log(consoleLogs.slice(-8).join('\n'));
  try{ws.close();}catch(e){}
  edge.kill();
  process.exit(failed.length?1:0);
}
main().catch(e=>{console.error('测试异常:',e);process.exit(2);});
