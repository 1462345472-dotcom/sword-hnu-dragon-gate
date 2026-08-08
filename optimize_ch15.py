import json

path = r'细胞生物学题库\第十五章\questions.json'
qs = json.load(open(path, encoding='utf-8'))

# No deletions needed - all 38 questions are distinct and valuable

new_qs = [
    # ===== 凋亡的生理学意义 (2题) =====
    {
        "id": 39, "topic": "凋亡生理意义", "type": "choice",
        "question": "哺乳动物指（趾）间膜的消失是通过哪种细胞死亡方式实现的？",
        "options": {"A": "细胞坏死", "B": "细胞凋亡", "C": "细胞焦亡", "D": "细胞自噬"},
        "answer": "B", "difficulty": 1,
        "explanation": "指（趾）间膜消失、腭融合、肠腔管道形成、视网膜发育等胚胎发育过程中的组织塑造均依赖细胞凋亡精确清除多余细胞。这是凋亡生理意义的经典例子。",
        "tags": ["凋亡", "胚胎发育", "生理意义"]
    },
    {
        "id": 40, "topic": "凋亡生理意义", "type": "short",
        "question": "阐述细胞凋亡在机体中的主要生理意义，并各举一例说明。",
        "answer": "① 保证正常胚胎发育，塑造个体及器官形态：哺乳动物指（趾）间膜消失、腭融合、肠腔管道形成、视网膜发育等均依赖凋亡精确清除多余细胞。胸腺中识别自身抗原的T细胞克隆通过凋亡被选择性消除，形成免疫耐受。\n\n② 维持成体组织器官细胞数量的稳态：机体通过调节凋亡与增殖速率维持组织细胞数量恒定。凋亡不足可致疾病（如ALPS患者T淋巴细胞无法正常凋亡导致自身免疫病）；凋亡过度亦可致病（如HIV诱发CD4+ T细胞过度凋亡导致免疫缺陷；阿尔茨海默病、帕金森病等神经退行性疾病与神经细胞过度凋亡相关）。\n\n③ 生理保护与肿瘤监控：凋亡清除DNA损伤等异常细胞而不引发炎症，是机体预防癌症的重要手段。p53等抑癌基因通过诱导凋亡或衰老阻断癌变进程。",
        "difficulty": 2,
        "tags": ["凋亡", "生理意义", "胚胎发育", "稳态", "肿瘤监控"],
        "explanation": "本题目为简答题，答案已包含完整分点解析内容，参见answer字段。"
    },

    # ===== p16/Rb通路 (2题) =====
    {
        "id": 41, "topic": "衰老机制", "type": "choice",
        "question": "除p53/p21通路外，调控细胞复制衰老的另一条重要通路是？",
        "options": {"A": "p16/Rb通路", "B": "Wnt/β-catenin通路", "C": "NF-κB通路", "D": "JAK/STAT通路"},
        "answer": "A", "difficulty": 2,
        "explanation": "p16（CDKN2A基因产物）通过抑制CDK4/6阻止Rb磷酸化，维持Rb与E2F的结合，使细胞停滞于G1期。p53/p21和p16/Rb是细胞衰老的两条主要调控通路。",
        "tags": ["p16", "Rb", "衰老调控"]
    },
    {
        "id": 42, "topic": "衰老机制", "type": "truefalse",
        "question": "p53/p21通路和p16/Rb通路均可介导细胞复制衰老，两者协同作用使衰老细胞不可逆地退出细胞周期。",
        "answer": True, "difficulty": 2,
        "explanation": "两条通路均导致G1期阻滞：p53→p21→抑制CDK活性；p16→抑制CDK4/6→Rb保持低磷酸化→E2F被抑制。两条通路协同确保衰老的不可逆性。",
        "tags": ["p53", "p16", "Rb", "衰老"]
    },

    # ===== 细胞衰老与个体衰老的关系 (1题) =====
    {
        "id": 43, "topic": "衰老与个体", "type": "short",
        "question": "阐述细胞衰老与个体衰老的关系。",
        "answer": "细胞衰老是导致个体衰老的重要因素，具体体现在：\n\n① 组织干细胞的复制衰老：造血干细胞、上皮干细胞、神经干细胞等持续分裂的组织干细胞，其端粒酶活性不足以完全弥补复制过程中端粒的缩短，随年龄增长增殖能力下降→组织再生受阻→器官功能减退→影响全身协调→个体衰老。\n\n② 衰老细胞的积累效应：已分化的组织细胞衰老后功能减退，正常应被免疫细胞清除并由干细胞新生替代。但随着年龄增长，未及时清除的衰老细胞越积越多。\n\n③ SASP的微环境恶化：衰老细胞分泌炎性因子和金属蛋白酶等SASP，影响周围正常细胞功能，破坏组织结构，加速个体衰老表征。\n\n④ 终末分化细胞的功能衰退：神经细胞、心肌细胞等虽不发生复制衰老，但其生命进程中功能活性的逐渐下降也是个体衰老的重要原因。\n\n细胞衰老既是机体抗癌的保护机制，也是驱动个体衰老的细胞学基础——体现了生物体在抗癌与抗衰老之间的演化权衡。",
        "difficulty": 2,
        "tags": ["细胞衰老", "个体衰老", "SASP", "干细胞"],
        "explanation": "本题目为简答题，答案已包含完整分点解析内容，参见answer字段。"
    },

    # ===== caspase同源活化vs异源活化 (1题) =====
    {
        "id": 44, "topic": "caspase活化", "type": "choice",
        "question": "起始caspase（如caspase-8、caspase-9）的激活方式是？",
        "options": {"A": "被效应caspase切割激活（异源活化）", "B": "在接头蛋白复合物中通过自身切割激活（同源活化）", "C": "直接被Ca²⁺激活", "D": "被磷酸化激活"},
        "answer": "B", "difficulty": 2,
        "explanation": "起始caspase通过同源活化：酶原被招募至DISC（caspase-8）或凋亡复合体（caspase-9）中，在复合物内发生构象变化并自身切割产生活性形式。效应caspase（如caspase-3）则是被已活化的起始caspase切割激活——异源活化。",
        "tags": ["caspase", "同源活化", "异源活化"]
    },

    # ===== caspase抑制剂 (3题) =====
    {
        "id": 45, "topic": "caspase调控", "type": "choice",
        "question": "cIAP（细胞凋亡抑制因子）通过哪种机制抑制细胞凋亡？",
        "options": {"A": "降解线粒体释放的细胞色素c", "B": "直接与活性caspase分子结合，阻抑其切割底物", "C": "抑制死亡受体Fas的表达", "D": "促进Bcl-2的降解"},
        "answer": "B", "difficulty": 2,
        "explanation": "cIAP直接结合已活化的caspase并抑制其活性。当凋亡程序启动后，线粒体释放的Smac和Htra2/Omi可与cIAP结合，解除cIAP对caspase的抑制，释放出被封闭的caspase执行凋亡。",
        "tags": ["cIAP", "caspase抑制", "Smac"]
    },
    {
        "id": 46, "topic": "caspase调控", "type": "choice",
        "question": "Smac/DIABLO在细胞凋亡中的核心功能是？",
        "options": {"A": "直接激活caspase-3", "B": "与cIAP结合，解除cIAP对caspase的抑制", "C": "促进Bcl-2表达", "D": "在线粒体膜上形成通道释放细胞色素c"},
        "answer": "B", "difficulty": 2,
        "explanation": "Smac（Second Mitochondria-derived Activator of Caspase）从线粒体释放后，与cIAP结合使其失活，释放出被cIAP封闭的caspase。这是线粒体促进凋亡执行的重要机制。",
        "tags": ["Smac", "cIAP", "线粒体"]
    },
    {
        "id": 47, "topic": "caspase调控", "type": "multi",
        "question": "以下关于caspase活性调控的描述，正确的有？",
        "options": {"A": "cIAP可直接结合活性caspase并抑制其功能", "B": "Smac从线粒体释放后与cIAP结合，解除对caspase的抑制", "C": "丝氨酸蛋白酶Htra2/Omi通过切割cIAP来解除凋亡抑制", "D": "病毒蛋白CrmA和p35是天然的caspase抑制剂", "E": "疱疹病毒的v-FLIP通过抑制死亡受体外源途径来阻止宿主细胞凋亡"},
        "answer": "ABCDE", "difficulty": 3,
        "explanation": "五种机制均参与caspase活性的调控。病毒演化出多种策略抑制宿主细胞凋亡以保证自身复制——这是宿主-病毒协同演化的重要案例。",
        "tags": ["caspase", "cIAP", "Smac", "病毒调控"]
    },

    # ===== 细胞衰老的防癌意义 (2题) =====
    {
        "id": 48, "topic": "衰老与癌症", "type": "choice",
        "question": "细胞衰老被认为是一种重要的抗癌机制，其核心逻辑是？",
        "options": {"A": "衰老细胞分泌的SASP直接杀死癌细胞", "B": "DNA损伤等癌变诱因同时触发衰老→使潜在恶性细胞不可逆地停止增殖→并被免疫清除", "C": "衰老细胞中的端粒酶活性降低直接抑制肿瘤", "D": "衰老细胞通过自噬消灭癌细胞"},
        "answer": "B", "difficulty": 2,
        "explanation": "随着生命进程积累的DNA损伤既是癌变诱因也会触发细胞衰老。机体通过p53/p16介导的衰老机制使受损细胞不可逆退出细胞周期，阻断其癌化进程，并通过SASP招募免疫细胞清除之。这体现了衰老作为抗癌机制的双刃剑效应。",
        "tags": ["衰老", "抗癌", "p53"]
    },
    {
        "id": 49, "topic": "衰老与癌症", "type": "truefalse",
        "question": "细胞衰老既是机体防止细胞癌变的重要保护机制，也是驱动个体衰老的细胞学基础，体现了抗癌与抗衰老之间的演化权衡。",
        "answer": True, "difficulty": 1,
        "explanation": "p53/p16介导的细胞衰老阻断癌变→保护年轻个体远离癌症；但随着衰老细胞积累和SASP分泌→又驱动组织老化和个体衰老。这就是演化中抗癌与抗衰老的权衡。",
        "tags": ["衰老", "抗癌", "演化权衡"]
    },

    # ===== DAMP/PAMP (2题) =====
    {
        "id": 50, "topic": "DAMP/PAMP", "type": "choice",
        "question": "细胞程序性坏死时释放到胞外的HMGB1蛋白属于？",
        "options": {"A": "病原相关分子模式（PAMP）", "B": "损伤相关分子模式（DAMP）", "C": "生长因子", "D": "补体蛋白"},
        "answer": "B", "difficulty": 2,
        "explanation": "HMGB1是核内高速泳动族蛋白，程序性坏死时释放到胞外作为内源性危险信号（DAMP），强烈促发免疫反应。PAMP是病原体来源的外源性危险信号，如细菌核酸和蛋白质成分。",
        "tags": ["DAMP", "HMGB1", "程序性坏死"]
    },
    {
        "id": 51, "topic": "DAMP/PAMP", "type": "truefalse",
        "question": "程序性坏死细胞释放的DAMP（损伤相关分子模式）可作为内源性危险信号，强烈促发机体的免疫反应和炎症应答。",
        "answer": True, "difficulty": 2,
        "explanation": "DAMP（如HMGB1、线粒体DNA等）在程序性坏死时随细胞膜破裂释放，被免疫细胞模式识别受体识别，激活炎症反应。这使程序性坏死成为凋亡受阻时的有效免疫替补机制。",
        "tags": ["DAMP", "炎症", "程序性坏死"]
    },

    # ===== 个体衰老标志 (3题) =====
    {
        "id": 52, "topic": "个体衰老标志", "type": "choice",
        "question": "以下哪项属于个体衰老在基因和蛋白质水平上的标志？",
        "options": {"A": "基因组DNA损伤积累", "B": "端粒长度明显缩短", "C": "蛋白质折叠和降解体系（泛素-蛋白酶体、自噬体-溶酶体）功能障碍", "D": "以上都是"},
        "answer": "D", "difficulty": 1,
        "explanation": "ABC均属于基因和蛋白质水平上的衰老标志。此外还包括表观遗传修饰改变（DNA甲基化、组蛋白修饰）引起的基因表达异常。",
        "tags": ["个体衰老", "分子标志"]
    },
    {
        "id": 53, "topic": "个体衰老标志", "type": "multi",
        "question": "以下属于个体衰老在细胞水平上的标志的有？",
        "options": {"A": "丧失增殖能力和功能减退的衰老细胞累积，不能被免疫系统及时清除", "B": "成体干细胞因复制衰老而减弱甚至丧失组织更新能力", "C": "线粒体功能障碍，损伤的线粒体累积造成能量代谢障碍", "D": "衰老细胞SASP分泌物恶化周围组织微环境", "E": "细胞通信失调，尤其是营养信号传递通路紊乱"},
        "answer": "ABCDE", "difficulty": 2,
        "explanation": "五项均为个体衰老在细胞水平上的标志。这些标志相互关联、级联放大，共同驱动个体衰老进程。",
        "tags": ["个体衰老", "细胞标志"]
    },
    {
        "id": 54, "topic": "个体衰老标志", "type": "truefalse",
        "question": "个体衰老仅由细胞复制衰老引起，终末分化细胞（如神经细胞、心肌细胞）不参与个体衰老进程。",
        "answer": False, "difficulty": 2,
        "explanation": "错误。终末分化细胞虽不发生复制衰老，但其生命进程中功能活性的逐渐下降同样是导致个体衰老的重要原因。个体衰老是多因素综合作用的结果。",
        "tags": ["个体衰老", "终末分化细胞"]
    },

    # ===== p53在凋亡中的转录调控 (1题) =====
    {
        "id": 55, "topic": "p53调控", "type": "choice",
        "question": "p53促进细胞凋亡的机制不包括？",
        "options": {"A": "直接解除Bcl-2对Bax/Bak的抑制作用触发内源途径", "B": "作为转录因子激活凋亡正调节因子表达", "C": "直接激活caspase-3执行凋亡", "D": "抑制凋亡负调节因子的表达"},
        "answer": "C", "difficulty": 2,
        "explanation": "p53通过两种方式促凋亡：①直接在线粒体上解除Bcl-2对Bax/Bak的抑制（非转录途径）；②作为转录因子激活Bax、Puma、Noxa等促凋亡基因，抑制Bcl-2等抗凋亡基因的表达（转录途径）。p53不直接激活caspase-3。",
        "tags": ["p53", "凋亡", "转录调控"]
    },

    # ===== 坏死复合物分子细节 (2题) =====
    {
        "id": 56, "topic": "程序性坏死", "type": "choice",
        "question": "程序性坏死（necroptosis）的关键执行分子MLKL被激活后，如何导致细胞死亡？",
        "options": {"A": "进入细胞核切割DNA", "B": "被RIPK3磷酸化后寡聚化，与质膜PIP结合形成通道，破坏质膜屏障", "C": "激活caspase级联反应", "D": "降解细胞骨架蛋白"},
        "answer": "B", "difficulty": 2,
        "explanation": "RIPK3磷酸化MLKL→MLKL寡聚化→寡聚体与质膜磷脂酰肌醇磷酸（PIP）结合→在质膜上形成通道→膜屏障功能丧失→细胞坏死。这是程序性坏死的核心执行机制。",
        "tags": ["MLKL", "程序性坏死", "RIPK3"]
    },
    {
        "id": 57, "topic": "程序性坏死", "type": "truefalse",
        "question": "程序性坏死与细胞凋亡的关键区别在于：凋亡经caspase级联执行且质膜完整，程序性坏死经RIPK3/MLKL通路执行且质膜破裂，但两者均受基因调控。",
        "answer": True, "difficulty": 2,
        "explanation": "根据最新第五版教材，凋亡和程序性坏死（含焦亡）都是受基因控制的有序程序性死亡。区别在于分子机制（caspase vs RIPK3/MLKL）和形态特征（质膜完整 vs 破裂+炎症）。",
        "tags": ["程序性坏死", "凋亡", "基因调控"]
    },

    # ===== 凋亡细胞清除——磷脂酰丝氨酸外翻 (1题) =====
    {
        "id": 58, "topic": "凋亡检测", "type": "choice",
        "question": "细胞凋亡过程中，位于细胞膜内侧的磷脂酰丝氨酸（PS）翻转到细胞膜外侧的生物学意义是？",
        "options": {"A": "激活caspase级联反应", "B": "作为\"eat-me\"信号，被吞噬细胞表面的PS受体识别，介导凋亡细胞的清除", "C": "促进细胞色素c从线粒体释放", "D": "直接导致DNA断裂"},
        "answer": "B", "difficulty": 2,
        "explanation": "PS外翻是凋亡早期的标志性事件，作为\"吃我\"信号被吞噬细胞识别，确保凋亡细胞在质膜破裂前被安全清除——这是凋亡不引发炎症的关键步骤之一。这一特征也被广泛用于凋亡的流式细胞术检测。",
        "tags": ["磷脂酰丝氨酸", "吞噬", "凋亡清除"]
    }
]

qs.extend(new_qs)
print(f"Total questions: {len(qs)}")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

# Verify
from collections import Counter
types = Counter(q['type'] for q in qs)
ids = [q['id'] for q in qs]
assert len(ids) == len(set(ids)), f"Duplicate IDs!"
print(f"Types: {dict(types)}, IDs: {min(ids)}-{max(ids)}")
print("Saved!")
