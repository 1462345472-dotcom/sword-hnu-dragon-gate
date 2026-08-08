/* Task 5 语义等价性测试:修改后脚本(索引算法) vs 参考实现(原全量算法)
   断言:集合 + 顺序完全一致。失败 exit 1。 */
const fs = require('fs');
const vm = require('vm');

const QB_REF = JSON.parse(fs.readFileSync('_t5_qb_ref.json', 'utf8'));

/* ---------- 沙箱 stub ---------- */
function makeEl(){return {classList:{add(){},remove(){}},style:{setProperty(){}},setAttribute(){},appendChild(){},
  remove(){},addEventListener(){},removeChild(){},innerHTML:'',textContent:'',scrollTop:0,
  querySelector:()=>null,querySelectorAll:()=>[]};}
function makeSandbox(){
  const sb = {
    document:{createElement:makeEl,getElementById:()=>null,querySelector:()=>null,
      querySelectorAll:()=>[],body:{appendChild(){},removeChild(){}},
      documentElement:{style:{setProperty(){}}},addEventListener(){}},
    localStorage:{getItem:()=>null,setItem(){},removeItem(){},key:()=>null,length:0},
    location:{href:''},confirm:()=>false,alert(){},
    setTimeout:(f)=>{},clearTimeout(){},setInterval(){},requestAnimationFrame:()=>{},
    navigator:{userAgent:'node'},console,
  };
  sb.window = sb;
  vm.createContext(sb);
  return sb;
}

/* ---------- 加载修改后脚本,生成 __qa2(暴露索引函数) ---------- */
function loadScript(src, extraExports){
  const code = fs.readFileSync(src, 'utf8');
  const mark = 'window.__qa=';
  const i0 = code.indexOf(mark);
  const i1 = code.indexOf('};', i0);
  if(i0<0||i1<0){ console.log('找不到 __qa 钩子'); process.exit(1); }
  const variant = code.substring(0,i0) + extraExports + code.substring(i1+2);
  const sb = makeSandbox();
  try { vm.runInContext(variant, sb); }
  catch(e){ console.log('脚本加载失败:', e.message); process.exit(1); }
  return sb;
}

const after = loadScript('_t5_script_0.js', 'window.__qa2={qbIdx:qbIdx,chQsByType:chQsByType,chTermsBy:chTermsBy,getQ:getQ,findBankForQ:findBankForQ,allQs:allQs,allTerms:allTerms,QUESTION_BANKS:QUESTION_BANKS,S:S,wrongQs:wrongQs,bmQs:bmQs,ak:ak,startQuiz:startQuiz,invalidate:invalidateRuntimeCaches};');
const before = loadScript('_t5_script_before.js', 'window.__qa2={getQ:getQ,allQs:allQs,allTerms:allTerms,QUESTION_BANKS:QUESTION_BANKS,S:S,wrongQs:wrongQs,bmQs:bmQs,ak:ak,startQuiz:startQuiz,invalidate:invalidateRuntimeCaches};');

let fail = 0;
function check(name, ok, detail){
  if(ok){ console.log('  OK  ' + name); }
  else { console.log('  FAIL ' + name + ' :: ' + detail); fail++; }
}
const idSeq = (arr) => arr.map(q=>q.id).join(',');

/* ========== 1. findBankForQ:qidFirst 索引 vs 原全量遍历(全部 qid 1..max) ========== */
console.log('[1] findBankForQ 等价(全部 id 1..500)');
{
  const qa = after.__qa2;
  const refFind = (qid)=>{
    const ks=Object.keys(QB_REF);
    for(let i=0;i<ks.length;i++){const bk=QB_REF[ks[i]];
      for(let j=0;j<bk.questions.length;j++){if(bk.questions[j].id===qid)return bk;}}
    return null;
  };
  const ks = Object.keys(QB_REF);
  let maxId = 0;
  ks.forEach(k=>QB_REF[k].questions.forEach(q=>{if(q.id>maxId)maxId=q.id;}));
  const badIds = [];
  for(let id=1;id<=maxId;id++){
    const refB = refFind(id);
    const newB = qa.findBankForQ(id);
    const refK = refB?refB.key:null;
    const newK = newB?newB.key:null;
    if(refK!==newK){ badIds.push(id+':'+(refK||'null')+'/'+(newK||'null')); if(badIds.length>5)break; }
  }
  /* 不存在的 id */
  const missRef = refFind(maxId+1), missNew = qa.findBankForQ(maxId+1);
  if((missRef?missRef.key:null)!==(missNew?missNew.key:null))badIds.push('missing');
  check('findBankForQ 全 id 等价(1..'+maxId+')', badIds.length===0, badIds.join(' '));
}

/* ========== 2. getQ:byId vs 原线性(全部章节全部 id + 不存在 id) ========== */
console.log('[2] getQ 等价');
{
  const qa = after.__qa2;
  const refGet = (k,id)=>{const qs=QB_REF[k].questions;for(let i=0;i<qs.length;i++){if(qs[i].id===id)return qs[i];}return null;};
  let bad = 0;
  Object.keys(QB_REF).forEach(k=>{
    const prev = qa.S.subject; qa.S.subject = k;
    const qs = QB_REF[k].questions;
    qs.forEach(q=>{
      const r = refGet(k,q.id), n = qa.getQ(q.id);
      if((r?r.id:null)!==(n?n.id:null))bad++;
    });
    const r=refGet(k,99999), n=qa.getQ(99999);
    if((r?r.id:null)!==(n?n.id:null))bad++;
    qa.S.subject = prev;
  });
  check('getQ 全章节等价', bad===0, '不一致 '+bad+' 处');
}

/* ========== 3. chQsByType vs filter(全部章节 × 4 题型,含不存在题型) ========== */
console.log('[3] chQsByType 等价');
{
  const qa = after.__qa2;
  let bad = 0;
  Object.keys(QB_REF).forEach(k=>{
    ['choice','truefalse','multi','short'].forEach(ft=>{
      const ref = QB_REF[k].questions.filter(q=>q.type===ft);
      const nw = qa.chQsByType(k,ft);
      if(idSeq(ref)!==idSeq(nw))bad++;
    });
    if(qa.chQsByType(k,'essay')!==undefined && qa.chQsByType(k,'essay').length!==0)bad++;
  });
  check('chQsByType 全章节×题型等价', bad===0, '不一致 '+bad+' 处');
}

/* ========== 4. chTermsBy vs at.filter(全部章节 × 全部章节值) ========== */
console.log('[4] chTermsBy 等价');
{
  const qa = after.__qa2;
  let bad = 0;
  Object.keys(QB_REF).forEach(k=>{
    const at = QB_REF[k].terms||[];
    Object.keys(QB_REF).forEach(f=>{
      const ref = at.filter(t=>t.chapter===f);
      const nw = qa.chTermsBy(k,f);
      if(idSeq(ref)!==idSeq(nw))bad++;
    });
  });
  check('chTermsBy 全章节等价', bad===0, '不一致 '+bad+' 处');
}

/* ========== 5. wrongQs/bmQs 剪枝 vs 全量(随机状态序列等价) ========== */
console.log('[5] wrongQs/bmQs 剪枝等价');
{
  const refWrong = (S)=>{
    const r=[],ks=Object.keys(QB_REF);
    for(let j=0;j<ks.length;j++){const qs=QB_REF[ks[j]].questions;
      for(let i=0;i<qs.length;i++){if(S[ks[j]+'__'+qs[i].id])r.push(qs[i]);}}
    return r;
  };
  const states = [
    {},
    {'biochem_1_2__5':true},
    {'biochem_1_2__5':true,'biochem_1_2__3':true},
    {'cellbio_16__50':true,'biochem_36__1':true,'cellbio_1__1':true},
    {'old_chapter__7':true},                       /* 旧章节残留键 */
    {'biochem_1_2__99999':true},                   /* 章节存在但 id 不存在 */
    {'cellbio_3__1':true,'cellbio_3__190':true,'cellbio_3__2':true},
  ];
  /* 大规模随机态 */
  let big = {};
  for(let i=0;i<300;i++){
    const ks = Object.keys(QB_REF);
    const k = ks[Math.floor(Math.random()*ks.length)];
    const q = QB_REF[k].questions[Math.floor(Math.random()*QB_REF[k].questions.length)];
    big[k+'__'+q.id]=true;
  }
  states.push(big);

  for(const mode of ['wrong','bm']){
    let bad = 0;
    states.forEach((st,idx)=>{
      const S = before.__qa2.S;
      S[mode==='wrong'?'wrongSet':'bookmarks'] = JSON.parse(JSON.stringify(st));
      before.__qa2.invalidate();
      const ref = refWrong(S[mode==='wrong'?'wrongSet':'bookmarks']);
      const S2 = after.__qa2.S;
      S2[mode==='wrong'?'wrongSet':'bookmarks'] = JSON.parse(JSON.stringify(st));
      after.__qa2.invalidate();
      const fn = mode==='wrong'?after.__qa2.wrongQs:after.__qa2.bmQs;
      const nw = fn();
      if(idSeq(ref)!==idSeq(nw)){ bad++; console.log('   状态'+idx+' 不一致 ref='+idSeq(ref).slice(0,80)+' new='+idSeq(nw).slice(0,80)); }
    });
    check(mode+'Qs 剪枝等价('+states.length+' 状态)', bad===0, '不一致 '+bad+' 个状态');
  }
}

/* ========== 6. startQuiz 题型过滤:新(S.questions) vs 旧(startQuiz) 序列 ========== */
console.log('[6] startQuiz 题型过滤等价');
{
  let bad = 0;
  Object.keys(QB_REF).forEach(k=>{
    ['all','choice','truefalse','multi','short'].forEach(mode=>{
      before.__qa2.S.subject = k; before.__qa2.startQuiz(k,mode);
      const refSeq = idSeq(before.__qa2.S.questions);
      after.__qa2.S.subject = k; after.__qa2.startQuiz(k,mode);
      const newSeq = idSeq(after.__qa2.S.questions);
      if(refSeq!==newSeq){bad++;console.log('   '+k+' '+mode+' ref='+refSeq.slice(0,60)+' new='+newSeq.slice(0,60));}
    });
  });
  check('startQuiz 全章节×模式等价', bad===0, '不一致 '+bad+' 处');
}

/* ========== 7. 索引构建次数:懒构建,只建一次 ========== */
console.log('[7] 懒构建');
{
  const qa = after.__qa2;
  const before1 = qa.qbIdx();
  const before2 = qa.qbIdx();
  check('qbIdx 幂等(同一对象)', before1===before2, '');
  /* 索引内容自检:qidFirst 覆盖全部 id,chapters 覆盖 51 章 */
  const total = Object.values(QB_REF).reduce((a,b)=>a+b.questions.length,0);
  const idx = qa.qbIdx();
  let covered = 0;
  Object.keys(QB_REF).forEach(k=>{Object.keys(idx.chapters[k].byId).forEach(id=>{covered++;});});
  check('索引覆盖全部题(byId '+covered+'/'+total+')', covered===total, '');
  check('索引覆盖全部章节('+Object.keys(idx.chapters).length+')', Object.keys(idx.chapters).length===51, '');
}

console.log(fail===0 ? '\n全部等价性断言通过' : '\n存在 ' + fail + ' 项失败');
process.exit(fail===0?0:1);
