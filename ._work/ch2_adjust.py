# -*- coding: utf-8 -*-
"""第二章微调:删除2条与choice重复度高的tf,新增2条multi;terms补2条名解"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第二章'
qp = BASE + r'\questions.json'
tp = BASE + r'\terms.json'

qs = json.load(open(qp, encoding='utf-8'))

# 删除 ID 147(透析tf,与ID123重复) 与 ID 152(CO2培养箱tf,与ID129重复)
del_ids = {147, 152}
qs = [q for q in qs if q['id'] not in del_ids]
print('已删除 tf:', len(del_ids))

new = [
{"id":191,"type":"multi","question":"在研究某个蛋白质的功能时，常需要多种技术联用。下列技术组合与应用目的匹配正确的有？","options":{"A":"GFP融合蛋白——活细胞中实时追踪该蛋白的定位与动态","B":"免疫荧光或Western blot——检测该蛋白的表达与定位","C":"RNAi或CRISPR/Cas9——敲低或敲除该蛋白基因研究其功能","D":"免疫共沉淀（Co-IP）——鉴定与该蛋白相互作用的伙伴蛋白","E":"电子显微镜——直接测定该蛋白的氨基酸序列"},"answer":"ABCD","explanation":"E错误：电镜用于观察形态结构，测定氨基酸序列需蛋白质测序或质谱。A-D为研究蛋白功能的标准技术组合：GFP追踪定位、抗体检测表达、基因沉默研究功能、Co-IP发现互作蛋白。","difficulty":3,"tags":["技术综合","GFP","Western blot","RNAi","Co-IP"]},
{"id":192,"type":"multi","question":"细胞同步化是研究细胞周期的重要技术，下列描述正确的有？","options":{"A":"双胸苷（TdR）阻断法可将细胞同步于S期起始处","B":"秋水仙素或诺考达唑可阻断细胞于M期（中期）","C":"血清饥饿使细胞退出细胞周期进入G0/G1期","D":"有丝分裂摇落法（shake-off）收集处于分裂期的贴壁细胞","E":"细胞同步化只能用于动物细胞，不能用于酵母"},"answer":"ABCD","explanation":"E错误：酵母等微生物同样可同步化（如α因子阻断法、温度敏感突变体法）。A-D为常用同步化方法：双胸苷阻断S期、纺锤体毒物阻断M期、血清饥饿进入G0、摇落法物理收集M期细胞。","difficulty":3,"tags":["细胞同步化","双胸苷","秋水仙素","血清饥饿"]},
]

qs.extend(new)
json.dump(qs, open(qp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- terms 补充2条 ----
ts = json.load(open(tp, encoding='utf-8'))
ids = {t['id'] for t in ts}
nid = max(ids) + 1
ts.append({"id": nid, "term": "SDS-PAGE（十二烷基硫酸钠-聚丙烯酰胺凝胶电泳）", "definition": "在变性条件下按分子量大小分离蛋白质的电泳技术。SDS使蛋白质变性并带均匀负电荷，β-巯基乙醇还原二硫键，迁移率仅取决于分子量，用于分子量测定与纯度鉴定。", "chapter": "第一章"})
ts.append({"id": nid+1, "term": "Western blot（蛋白质印迹）", "definition": "将SDS-PAGE分离的蛋白质电转移至膜上，用特异性抗体杂交检测目标蛋白的技术。可检测特定蛋白的表达水平、分子量及修饰状态，常与免疫沉淀联用。", "chapter": "第一章"})
json.dump(ts, open(tp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('terms 新增2条, 共', len(ts))

from collections import Counter
c = Counter(x['type'] for x in qs)
print('题型分布:', dict(c), '总计', len(qs))
print('multi占比: %.1f%%  short占比: %.1f%%' % (c['multi']/len(qs)*100, c['short']/len(qs)*100))
