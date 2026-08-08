/* Task 5 renderTerms 视觉输出对比:修改前后脚本在 stub DOM 下渲染,innerHTML 必须逐字节一致 */
const fs = require('fs');
const vm = require('vm');

function makeEl(){return {classList:{add(){},remove(){}},style:{setProperty(){}},setAttribute(){},appendChild(){},
  remove(){},addEventListener(){},removeChild(){},innerHTML:'',textContent:'',scrollTop:0,
  querySelector:()=>null,querySelectorAll:()=>[]};}

function loadWithDom(src, viewName){
  const code = fs.readFileSync(src, 'utf8');
  const i0 = code.indexOf('window.__qa=');
  const i1 = code.indexOf('};', i0);
  const variant = code.substring(0,i0) +
    'window.__qa2={renderTerms:renderTerms,S:S,allTerms:allTerms,COURSES:COURSES,CHAPTER_NAMES:CHAPTER_NAMES,ICONS:ICONS,switchView:switchView};' +
    code.substring(i1+2);
  const el = makeEl();
  const sb = {
    document:{createElement:makeEl,getElementById:(id)=>id===viewName?el:null,querySelector:()=>null,
      querySelectorAll:()=>[],body:{appendChild(){},removeChild(){}},
      documentElement:{style:{setProperty(){}}},addEventListener(){}},
    localStorage:{getItem:()=>null,setItem(){},removeItem(){},key:()=>null,length:0},
    location:{href:''},confirm:()=>false,alert(){},
    setTimeout:(f)=>{},clearTimeout(){},setInterval(){},requestAnimationFrame:()=>{},
    navigator:{userAgent:'node'},console,
  };
  sb.window = sb;
  vm.createContext(sb);
  try { vm.runInContext(variant, sb); }
  catch(e){ console.log('加载失败:', e.message); process.exit(1); }
  return {qa: sb.__qa2, el};
}

const before = loadWithDom('_t5_script_before.js', 'view-terms');
const after  = loadWithDom('_t5_script_0.js', 'view-terms');

/* 场景:全部 51 章节 × filter ∈ {all} ∪ 全部章节 key,外加 cellbio 课程 */
const scenes = [];
['biochemistry','cellbiology'].forEach(course=>{
  const chs = before.qa.COURSES[course].chapters;
  chs.forEach(subject=>{
    scenes.push({course, subject, filter:'all'});
    chs.forEach(f=>scenes.push({course, subject, filter:f}));
  });
});

let fail = 0;
for(const sc of scenes){
  before.qa.S.course=sc.course; before.qa.S.subject=sc.subject; before.qa.S.termFilter=sc.filter;
  after.qa.S.course=sc.course; after.qa.S.subject=sc.subject; after.qa.S.termFilter=sc.filter;
  before.qa.renderTerms(); after.qa.renderTerms();
  const b = before.el.innerHTML, a = after.el.innerHTML;
  if(b!==a){ fail++; if(fail<=5) console.log('场景差异 course='+sc.course+' subject='+sc.subject+' filter='+sc.filter); }
}
console.log('renderTerms 场景数: '+scenes.length+', 差异: '+fail);
process.exit(fail===0?0:1);
