# -*- coding: utf-8 -*-
"""第十五章 补题 10 题(id 59-68) — 全部基于课件/丁明孝第五版"""
import json

NEW = [
    {
        "topic": "细胞程序性死亡",
        "type": "choice",
        "question": "下列关于细胞程序性死亡的说法，正确的是？",
        "options": {
            "A": "只有细胞凋亡属于程序性死亡，细胞坏死均为被动性死亡",
            "B": "细胞凋亡、程序性坏死及植物细胞程序性死亡均受基因控制，属于程序性死亡",
            "C": "程序性坏死不受细胞内基因控制",
            "D": "细胞焦亡不属于细胞程序性死亡"
        },
        "answer": "B",
        "difficulty": 1,
        "explanation": "第五版教材认为细胞坏死看似由外界物理化学因素造成的被动性死亡，但外界因素只是'导火索'，会引发细胞内部信号传递再由程序控制死亡，归根结底也是基因控制的程序性死亡；细胞程序性死亡包括动物细胞的凋亡、程序性坏死及植物细胞的程序性死亡等。",
        "tags": ["细胞程序性死亡", "死亡形式", "基因调控"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "choice",
        "question": "植物细胞清除死亡细胞的方式与动物细胞凋亡相比，主要差异在于？",
        "options": {
            "A": "依靠巨噬细胞吞噬清除凋亡小体",
            "B": "利用液泡（溶酶体）中的水解酶消化分解死亡细胞",
            "C": "通过细胞脱落方式排出死亡细胞",
            "D": "死亡细胞直接由免疫细胞清除"
        },
        "answer": "B",
        "difficulty": 2,
        "explanation": "植物细胞被固定在细胞壁中，没有类似动物巨噬细胞的可移动细胞清除死亡残余物，因此往往利用液泡（溶酶体）中的水解酶消化分解死亡细胞，主要包括液泡破裂释放水解酶和液泡膜与细胞膜融合将水解酶释放到胞外两种方式。",
        "tags": ["植物细胞程序性死亡", "液泡", "水解酶"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "choice",
        "question": "植物细胞程序性死亡途径中发挥作用的蛋白酶metacaspase与动物caspase的主要区别是？",
        "options": {
            "A": "metacaspase的活性中心不含半胱氨酸残基",
            "B": "metacaspase切割精氨酸或赖氨酸形成的肽键，caspase切割天冬氨酸残基后的肽键",
            "C": "metacaspase只存在于线粒体基质中",
            "D": "metacaspase与caspase切割底物的位点完全相同"
        },
        "answer": "B",
        "difficulty": 2,
        "explanation": "metacaspase与动物caspase具有类似的酶活性中心（都含有半胱氨酸残基），但两者切割底物的位点不同：metacaspase切割精氨酸或赖氨酸形成的肽键，而caspase特异切割天冬氨酸残基后的肽键。",
        "tags": ["metacaspase", "caspase", "植物细胞程序性死亡"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "choice",
        "question": "细胞焦亡过程中，促使caspase-1前体发生同源活化并切割pro-IL1β、pro-IL18以诱导炎症的结构是？",
        "options": {
            "A": "凋亡复合体(apoptosome)",
            "B": "死亡诱导信号复合物(DISC)",
            "C": "炎性小体(inflammasome)",
            "D": "坏死复合物(necrosome)"
        },
        "answer": "C",
        "difficulty": 2,
        "explanation": "病原体入侵细胞时，一系列蛋白质组装形成炎性小体，促使caspase-1前体发生同源活化；活化的caspase-1切割pro-IL1β和pro-IL18产生有活性的IL1β和IL18诱导炎症，并切割GSDMD在质膜形成孔洞，最终导致细胞膨胀破裂死亡。",
        "tags": ["炎性小体", "细胞焦亡", "caspase-1"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "choice",
        "question": "肿瘤坏死因子(TNF)通过其主要受体TNFR1诱导细胞死亡，下列说法正确的是？",
        "options": {
            "A": "TNF只能诱导质膜破裂的细胞坏死",
            "B": "当细胞内凋亡信号通路受阻或不完整时，TNF诱导的细胞坏死现象变得非常明显",
            "C": "TNF诱导的坏死不受细胞内基因控制",
            "D": "TNF不能诱导炎症因子的表达"
        },
        "answer": "B",
        "difficulty": 2,
        "explanation": "TNF是多效细胞因子，通过TNFR1可诱导多种炎症因子的表达及某些敏感细胞的死亡，包括质膜保持完整的凋亡和质膜破裂的坏死两种形式；当细胞内的凋亡信号通路受阻或不完整时，TNF诱导的细胞坏死（程序性坏死）现象就变得非常明显。",
        "tags": ["TNF", "TNFR1", "程序性坏死"]
    },
    {
        "topic": "细胞凋亡",
        "type": "choice",
        "question": "caspase非依赖性细胞凋亡途径的关键执行分子是？",
        "options": {
            "A": "细胞色素c和APAF-1",
            "B": "凋亡诱导因子(AIF)和限制性内切核酸酶G(EndoG)",
            "C": "Smac和Htra2/Omi",
            "D": "FADD和caspase-8"
        },
        "answer": "B",
        "difficulty": 2,
        "explanation": "线粒体除释放细胞色素c外，还能向细胞质内释放凋亡诱导因子(AIF)和限制性内切核酸酶G(EndoG)等凋亡相关因子，它们进入细胞核直接切割核DNA，诱发不依赖caspase的细胞凋亡。",
        "tags": ["AIF", "EndoG", "caspase非依赖性凋亡"]
    },
    {
        "topic": "细胞自噬",
        "type": "truefalse",
        "question": "细胞中寿命较短的蛋白质（如调控蛋白）主要通过自噬-溶酶体途径降解，而寿命较长的蛋白质及细胞结构则通过泛素-蛋白酶体系统降解。",
        "answer": "false",
        "difficulty": 1,
        "explanation": "恰好相反：寿命较短的蛋白质（如调控蛋白等）通过泛素-蛋白酶体系统降解；寿命较长的蛋白质及细胞结构（如整个线粒体、过氧化物酶体等细胞器）则通过细胞自噬途径由溶酶体降解。",
        "tags": ["自噬", "泛素-蛋白酶体", "蛋白质降解"]
    },
    {
        "topic": "细胞衰老",
        "type": "truefalse",
        "question": "将活化的端粒酶导入人成纤维细胞并使其持续表达，细胞的端粒不再缩短，复制寿命延长了约5倍；反之使癌细胞中的端粒酶失活可导致癌细胞增殖停滞并引发衰老。",
        "answer": "true",
        "difficulty": 1,
        "explanation": "实验证明持续表达活化端粒酶可使成纤维细胞端粒不再缩短、复制寿命延长5倍；使癌细胞端粒酶失活则致其增殖停滞并引发癌细胞衰老——这是端粒酶维持细胞持续增殖能力的直接实验证据。",
        "tags": ["端粒酶", "成纤维细胞", "复制寿命"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "multi",
        "question": "关于炎症caspase与凋亡caspase，下列说法正确的有？（多选）",
        "options": {
            "A": "炎症caspase包括caspase-1、4、5、11、12，负责产生有活性的白介素1(IL1)",
            "B": "凋亡caspase包括caspase-2、3、6、7、8、9、10，介导细胞凋亡",
            "C": "起始caspase在接头蛋白复合物中通过同源活化被激活",
            "D": "效应caspase被已活化的起始caspase切割激活（异源活化）",
            "E": "caspase家族成员还参与自噬、坏死、分化等生命活动的调控"
        },
        "answer": "ABCDE",
        "difficulty": 2,
        "explanation": "炎症caspase负责产生有活性的IL1等炎症因子；凋亡caspase分起始（同源活化）和效应（异源活化）两类；caspase家族成员还参与了自噬、坏死、分化等生命活动的调控——五个选项均正确。",
        "tags": ["炎症caspase", "凋亡caspase", "同源活化", "异源活化"]
    },
    {
        "topic": "细胞程序性死亡",
        "type": "short",
        "question": "简述细胞程序性坏死（necroptosis）的分子机制及其生物学意义。",
        "answer": "（1）坏死复合物的形成：在TNF或某些病原体的诱导下，蛋白激酶RIPK3及其上游信号分子聚合形成坏死复合物。\n（2）RIPK3的磷酸化与活化：RIPK3在坏死复合物中发生磷酸化而活化。\n（3）MLKL的磷酸化与寡聚化：活化的RIPK3招募并磷酸化下游分子MLKL，导致MLKL发生寡聚化。\n（4）质膜通道的形成：磷酸化的MLKL寡聚体通过与质膜中的磷脂酰肌醇磷酸(PIP)结合，在细胞膜上形成通道，导致细胞膜屏障作用消失，最终引起细胞坏死。\n（5）生物学意义：当细胞感染病原体、需要以\"自杀\"方式清除病原体而凋亡又因某种原因无法正常发生时，程序性坏死可作为凋亡的\"替补\"方式被细胞采用；坏死细胞释放的DAMP、PAMP能强烈促发免疫反应，有利于机体对病原体发动更有效的进攻。",
        "difficulty": 3,
        "tags": ["程序性坏死", "RIPK3", "MLKL", "DAMP"],
        "explanation": "本题目为简答题，答案已包含完整分点解析内容，参见answer字段。"
    },
]

P = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第十五章\questions.json'
qs = json.load(open(P, encoding='utf-8'))
assert max(q['id'] for q in qs) == 58
start = 59
for i, q in enumerate(NEW):
    q['id'] = start + i
    qs.append(q)
json.dump(qs, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('OK ch15 appended, total', len(qs))
