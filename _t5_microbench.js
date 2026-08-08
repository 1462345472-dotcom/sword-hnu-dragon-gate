/* Task 5 微基准:findBankForQ / wrongQs 重算 / 题型过滤 — before(全量遍历) vs after(索引) */
const fs = require('fs');
const vm = require('vm');

function makeEl(){return {classList:{add(){},remove(){}},style:{setProperty(){}},setAttribute(){},appendChild(){},
  remove(){},addEventListener(){},removeChild(){},innerHTML:'',textContent:'',scrollTop:0,
  querySelector:()=>null,querySelectorAll:()=>[]};}
function makeSandbox(){
  const sb={
    document:{createElement:makeEl,getElementById:()=>null,querySelector:()=>null,querySelectorAll:()=>[],
      body:{appendChild(){},removeChild(){}},documentElement:{style:{setProperty(){}}},addEventListener(){}},
    localStorage:{getItem:()=>null,setItem(){},removeItem(){},key:()=>null,length:0},
    location:{href:''},confirm:()=>false,alert(){},setTimeout:(f)=>{},clearTimeout(){},setInterval(){},
    requestAnimationFrame:()=>{},navigator:{userAgent:'node'},console,
  };
  sb.window=sb; vm.createContext(sb); return sb;
}
function load(src,exports){
  const code=fs.readFileSync(src,'utf8');
  const i0=code.indexOf('window.__qa='); const i1=code.indexOf('};',i0);
  const v=code.substring(0,i0)+exports+code.substring(i1+2);
  const sb=makeSandbox();
  vm.runInContext(v,sb);
  return sb;
}
const after=load('_t5_script_0.js','window.__qa2={findBankForQ:findBankForQ,wrongQs:wrongQs,bmQs:bmQs,startQuiz:startQuiz,S:S,ak:ak,invalidate:invalidateRuntimeCaches};');
const before=load('_t5_script_before.js','window.__qa2={findBankForQ:findBankForQ,wrongQs:wrongQs,bmQs:bmQs,startQuiz:startQuiz,S:S,ak:ak,invalidate:invalidateRuntimeCaches};');

function bench(name, fn, iters){
  for(let i=0;i<50;i++)fn(); /* 预热 */
  const t0=process.hrtime.bigint();
  for(let i=0;i<iters;i++)fn();
  const ms=Number(process.hrtime.bigint()-t0)/1e6;
  return ms;
}

/* 1. findBankForQ × 3000 次(交替不同 id) */
const ids=[1,5,50,100,190,196,250,99,42,7];
{
  const it=3000;
  const b=bench('before',()=>{ids.forEach(x=>before.__qa2.findBankForQ(x));},it);
  const a=bench('after',()=>{ids.forEach(x=>after.__qa2.findBankForQ(x));},it);
  console.log('findBankForQ('+it+'×10 id): before '+b.toFixed(1)+'ms  after '+a.toFixed(1)+'ms  加速 '+(b/a).toFixed(1)+'x');
}

/* 2. wrongQs 重算(invalidate 后,3 个章节有错题) */
{
  const st={};
  [['biochem_1_2',1],['biochem_1_2',5],['biochem_1_2',9],['biochem_10',2],['cellbio_3',10]].forEach(p=>{st[after.__qa2.ak(p[0],p[1])]=true;});
  const it=200;
  const fnB=()=>{before.__qa2.S.wrongSet=st;before.__qa2.invalidate();return before.__qa2.wrongQs();};
  const fnA=()=>{after.__qa2.S.wrongSet=st;after.__qa2.invalidate();return after.__qa2.wrongQs();};
  const b=bench('before',fnB,it);
  const a=bench('after',fnA,it);
  const rb=fnB(),ra=fnA();
  console.log('wrongQs 重算('+it+'×): before '+b.toFixed(1)+'ms  after '+a.toFixed(1)+'ms  加速 '+(b/a).toFixed(1)+'x  (结果一致:'+(JSON.stringify(rb.map(q=>q.id))===JSON.stringify(ra.map(q=>q.id)))+')');
}

/* 3. 空错题集重算(首页渲染路径) */
{
  const it=200;
  const fnB=()=>{before.__qa2.S.wrongSet={};before.__qa2.invalidate();return before.__qa2.wrongQs();};
  const fnA=()=>{after.__qa2.S.wrongSet={};after.__qa2.invalidate();return after.__qa2.wrongQs();};
  const b=bench('before',fnB,it);
  const a=bench('after',fnA,it);
  console.log('wrongQs 空集('+it+'×): before '+b.toFixed(1)+'ms  after '+a.toFixed(1)+'ms  加速 '+(b/a).toFixed(1)+'x');
}

/* 4. startQuiz 题型过滤(choice) */
{
  const it=300;
  const fnB=()=>{before.__qa2.startQuiz('biochem_5','choice');};
  const fnA=()=>{after.__qa2.startQuiz('biochem_5','choice');};
  const b=bench('before',fnB,it);
  const a=bench('after',fnA,it);
  console.log('startQuiz(choice,biochem_5)('+it+'×): before '+b.toFixed(1)+'ms  after '+a.toFixed(1)+'ms  加速 '+(b/a).toFixed(1)+'x');
}
