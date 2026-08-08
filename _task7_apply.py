# -*- coding: utf-8 -*-
"""Task 7: 向臻至版 HTML 注入启动数据自检(runDataSelfCheck)。
只动 <script> 内 JS:在 init() 前插入自检函数定义,在 init() 内 loadState() 后调用。
CSS/HTML 结构零改动(内联样式,不写入 <style>)。"""
import io

PATH = '生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html'

SELFCHECK_JS = r'''
/* Task 7 启动数据自检:章节对象数与 COURSES 一致、stats 与 questions/terms 一致、关键字段存在 */
function runDataSelfCheck(){
  try{
    var keys=Object.keys(QUESTION_BANKS);
    var expect={},ck,chs,i;
    for(ck in COURSES){
      chs=COURSES[ck].chapters;
      for(i=0;i<chs.length;i++)expect[chs[i]]=1;
    }
    var expKeys=Object.keys(expect),issues=[],qTypes=['choice','truefalse','multi','short'];
    /* 1. 章节对象数与 COURSES 注册一致 */
    if(keys.length!==expKeys.length)issues.push('章节对象数 '+keys.length+' ≠ COURSES 注册 '+expKeys.length);
    for(i=0;i<expKeys.length;i++){
      var k=expKeys[i],b=QUESTION_BANKS[k];
      if(!b||typeof b!=='object'){issues.push('缺少章节对象 '+k);continue;}
      if(!b.questions||!Array.isArray(b.questions)){issues.push(k+' 缺少 questions 数组');continue;}
      if(!b.terms||!Array.isArray(b.terms))issues.push(k+' 缺少 terms 数组');
      var st=b.stats||{};
      /* 2. stats 与 questions/terms 数量一致 */
      if(st.total!==b.questions.length)issues.push(k+' stats.total='+st.total+' ≠ questions='+b.questions.length);
      if(st.terms!==b.terms.length)issues.push(k+' stats.terms='+st.terms+' ≠ terms='+b.terms.length);
      /* 3. 每题关键字段 + 题型计数与 stats 一致 */
      var qc={choice:0,truefalse:0,multi:0,short:0},j,q;
      for(j=0;j<b.questions.length;j++){
        q=b.questions[j];
        if(!q||typeof q!=='object'){issues.push(k+' 第'+(j+1)+'题非对象');break;}
        if(q.type==null||q.question==null||q.answer==null)issues.push(k+' 题 id='+q.id+' 缺关键字段(type/question/answer)');
        if(qTypes.indexOf(q.type)>=0)qc[q.type]++;
      }
      for(j=0;j<qTypes.length;j++){
        var t=qTypes[j];
        if(st[t]!==qc[t])issues.push(k+' stats.'+t+'='+st[t]+' ≠ 实际 '+qc[t]);
      }
    }
    var totalQ=0;
    for(i=0;i<keys.length;i++)totalQ+=QUESTION_BANKS[keys[i]].questions.length;
    if(issues.length){
      console.warn('[数据自检] 发现 '+issues.length+' 项异常:');
      for(i=0;i<issues.length&&i<8;i++)console.warn('  - '+issues[i]);
      if(issues.length>8)console.warn('  - ...共 '+issues.length+' 项');
      var d=document.createElement('div');
      d.setAttribute('role','alert');
      d.style.cssText='position:fixed;right:16px;bottom:16px;z-index:99998;max-width:320px;padding:12px 16px;background:#8B1A2A;color:#fff;border-radius:10px;font-family:system-ui,sans-serif;font-size:13px;line-height:1.5;box-shadow:0 6px 24px rgba(0,0,0,.18);';
      d.innerHTML='<strong>数据自检警告</strong><br>发现 '+issues.length+' 项数据异常,详情见浏览器控制台。<br><span style="opacity:.75;font-size:12px">题库仍可正常使用,但建议重新生成数据。</span>';
      document.body.appendChild(d);
      setTimeout(function(){if(d.parentNode)d.parentNode.removeChild(d);},6000);
    }else{
      console.info('[数据自检] 正常: '+keys.length+' 章 / '+totalQ+' 题 / '+(function(){var t=0;for(i=0;i<keys.length;i++)t+=QUESTION_BANKS[keys[i]].terms.length;return t;})()+' 术语');
    }
  }catch(e){console.warn('[数据自检] 执行异常: ',e);}
}
'''

def main():
    html = open(PATH, encoding='utf-8', errors='ignore').read()
    marker_func = 'function init(){'
    assert html.count(marker_func) == 1, 'init() 标记应唯一'
    assert 'runDataSelfCheck' not in html, '已注入过,跳过'

    # 1) 在 init() 前插入函数定义
    idx = html.find(marker_func)
    html = html[:idx] + SELFCHECK_JS + '\n' + html[idx:]

    # 2) 在 init() 内 loadState(); 后插入调用
    anchor = 'function init(){\n  if(!dataReady()){showDataError();return;}\n  loadState();'
    assert html.count(anchor) == 1, 'init 内锚点应唯一'
    html = html.replace(anchor, anchor + '\n  setTimeout(runDataSelfCheck,0);')

    with io.open(PATH, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('注入完成: runDataSelfCheck 定义 + init 内调用')

if __name__ == '__main__':
    main()
