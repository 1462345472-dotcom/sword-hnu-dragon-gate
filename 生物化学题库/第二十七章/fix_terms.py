# -*- coding: utf-8 -*-
import sys, io, re
sys.stdout.reconfigure(encoding='utf-8')
p = '生物化学题库/第二十七章/terms_batch.py'
s = io.open(p, encoding='utf-8').read()

new_defs = {
 6: '不以现成的嘌呤碱为原料,而以5-磷酸核糖、氨基酸(甘氨酸、天冬氨酸、谷氨酰胺)、一碳单位和CO2等简单物质为原料,经酶促反应逐步成环合成嘌呤核苷酸,先生成IMP的过程。',
 7: '利用游离的嘌呤或嘌呤核苷,经简单的反应(如APRT、HGPRT催化与PRPP反应)合成嘌呤核苷酸的过程,过程简单耗能少,弥补脑、骨髓等组织不能从头合成核苷酸的不足。',
 8: '5-磷酸核糖焦磷酸,由5-磷酸核糖经磷酸核糖焦磷酸激酶催化、ATP提供磷酸基团生成,是5-磷酸核糖的活性供体,参与核苷酸合成及His、Trp的合成。',
 9: '嘌呤核苷酸从头合成的第一个产物,在PRPP基础上逐步组装嘌呤环而成,再转变为AMP(需GTP和天冬氨酸)或GMP(需NAD+和谷氨酰胺)。',
 12: '动物嘧啶核苷酸从头合成途径前三个酶(氨甲酰磷酸合成酶、天冬氨酸转氨甲酰酶和二氢乳清酸酶)融合形成的多功能酶,由三条相同多肽链亚基组成,每亚基含三个反应活性中心。',
 13: '催化核糖核苷二磷酸(NDP)还原为脱氧核糖核苷二磷酸(dNDP)的酶,含R1、R2两个亚基,活性部位在二者界面,需Mg2+,氢的最终给体为NADPH。',
 14: '广泛参与氧化还原反应的小分子蛋白质,含一对巯基,给出两个氢后变为二硫化物型,再经硫氧还蛋白还原酶(含FAD)催化被NADPH还原,循环传递氢。',
 16: '催化dUMP甲基化生成dTMP的酶,甲基供体为N5,N10-亚甲基四氢叶酸(给出亚甲基并还原成甲基,自身变为二氢叶酸)。',
 18: '次黄嘌呤的结构类似物,在体内经磷酸核糖化生成6-MP核苷酸,抑制IMP转变为AMP及GMP,并反馈抑制嘌呤合成调节酶,是重要的抗癌药物。',
}
for tid, d in new_defs.items():
    pattern = r'(\{"id": %d,.*?"definition": ")[^"]*(", "chapter")' % tid
    s2 = re.sub(pattern, lambda m: m.group(1) + d + m.group(2), s, count=1)
    assert s2 != s, f'id {tid} not replaced'
    s = s2
io.open(p, 'w', encoding='utf-8').write(s)
print('replaced', len(new_defs))
