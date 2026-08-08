# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout.reconfigure(encoding='utf-8')
p = '生物化学题库/第二十七章/terms_batch.py'
s = io.open(p, encoding='utf-8').read()

# 每个需要替换的 id 及其新定义(必须与原文不同,且 30<=len<=80)
new_defs = {
 2: '原核生物中识别外源DNA双螺旋中4-8个碱基对组成的具二重旋转对称性的回文序列,并在某位点特异切割DNA双链,产生粘性末端或平末端的酶,是基因工程常用工具酶。',
 6: '不以现成的嘌呤碱为原料,而以5-磷酸核糖、氨基酸、一碳单位和CO2等简单物质为原料,经一系列酶促反应逐步成环合成嘌呤核苷酸、先生成IMP的过程。',
 7: '利用游离的嘌呤或嘌呤核苷,经简单反应合成嘌呤核苷酸的过程,耗能少,可弥补脑、骨髓等组织不能从头合成核苷酸的不足。',
 8: '5-磷酸核糖焦磷酸,由5-磷酸核糖经磷酸核糖焦磷酸激酶催化、ATP供磷酸基生成,是5-磷酸核糖的活性供体,参与核苷酸合成及His、Trp的合成。',
 9: '嘌呤核苷酸从头合成的第一个产物,在PRPP基础上组装嘌呤环而成,再转变为AMP(需GTP和天冬氨酸)或GMP(需NAD+和谷氨酰胺)。',
 12: '动物嘧啶核苷酸从头合成途径前三个酶(氨甲酰磷酸合成酶、天冬氨酸转氨甲酰酶和二氢乳清酸酶)融合成的多功能酶,由三条相同多肽链组成,每亚基含三个活性中心。',
 13: '催化核糖核苷二磷酸(NDP)还原为脱氧核糖核苷二磷酸(dNDP)的酶,含R1、R2两个亚基,活性部位在二者界面,需Mg2+,氢的最终给体为NADPH。',
 14: '广泛参与氧化还原反应的小分子蛋白质,含一对巯基,给出两个氢后变为二硫化物型,由硫氧还蛋白还原酶(含FAD)催化被NADPH还原,循环传递氢。',
 16: '催化dUMP甲基化生成dTMP的酶,甲基供体为N5,N10-亚甲基四氢叶酸,给出亚甲基并还原成甲基后自身变为二氢叶酸。',
 18: '次黄嘌呤的结构类似物,在体内经磷酸核糖化生成6-MP核苷酸,抑制IMP转变为AMP及GMP,并反馈抑制嘌呤合成调节酶,是重要的抗癌药物。',
}
for tid, d in new_defs.items():
    L = len(d)
    assert 30 <= L <= 80, f'id {tid} new def len {L} out of range'
    pattern = r'(\{"id": %d,.*?"definition": ")[^"]*(", "chapter")' % tid
    s2 = re.sub(pattern, lambda m: m.group(1) + d + m.group(2), s, count=1)
    assert s2 != s, f'id {tid} not replaced (same text?)'
    s = s2
    print(f'id {tid}: replaced, len={L}')
io.open(p, 'w', encoding='utf-8').write(s)
print('ALL DONE')
