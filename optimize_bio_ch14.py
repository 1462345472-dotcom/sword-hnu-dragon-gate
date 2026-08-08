import json

qpath = r'生物化学题库\第十四章\questions.json'
qs = json.load(open(qpath, encoding='utf-8'))

new_qs = [
    # 植物激素 (5 - 考纲明确要求)
    {"id":51,"topic":"植物激素","type":"choice","question":"生长素(IAA)促进细胞伸长的酸性生长学说认为，IAA激活质膜H+-ATP酶导致？","options":{"A":"细胞壁碱化，纤维素合成增加","B":"细胞壁酸化，扩展蛋白活化，微纤维间氢键断裂，细胞壁松弛","C":"细胞质pH升高，微管解聚","D":"细胞壁木质化"},"answer":"B","difficulty":2,"explanation":"酸性生长学说：IAA激活质膜H+-ATP酶→H+外排→细胞壁pH降低(pH约5.0)→激活扩展蛋白(expansin)→断裂纤维素微纤维与半纤维素间氢键→细胞壁松弛→膨压驱动细胞伸长。细胞壁酸化是生长素快速效应的核心。","tags":["生长素","IAA","酸性生长学说"]},
    {"id":52,"topic":"植物激素","type":"choice","question":"以下植物激素中，唯一以气体形式存在的是？","options":{"A":"生长素(IAA)","B":"赤霉素(GA)","C":"乙烯(C2H4)","D":"脱落酸(ABA)"},"answer":"C","difficulty":1,"explanation":"乙烯是唯一的气态植物激素，由甲硫氨酸合成，促进果实成熟(催熟)、器官脱落和衰老。生产中利用乙烯利释放乙烯催熟香蕉。","tags":["乙烯","植物激素","气体"]},
    {"id":53,"topic":"植物激素","type":"choice","question":"脱落酸(ABA)的核心生理功能是？","options":{"A":"促进细胞分裂","B":"促进种子萌发","C":"诱导种子休眠和响应干旱胁迫(关闭气孔)","D":"促进茎的伸长"},"answer":"C","difficulty":1,"explanation":"ABA是胁迫激素：干旱→ABA合成→保卫细胞K+外流→气孔关闭→减少蒸腾。ABA也诱导种子贮藏蛋白合成，建立和维持种子休眠，拮抗GA的促萌发作用。","tags":["脱落酸","ABA","休眠","气孔"]},
    {"id":54,"topic":"植物激素","type":"choice","question":"细胞分裂素(CTK)主要在植物哪个部位合成？","options":{"A":"茎尖分生组织","B":"根尖","C":"成熟叶片","D":"花器官"},"answer":"B","difficulty":2,"explanation":"细胞分裂素在根尖合成，经木质部导管向上运输至地上部，促进细胞分裂、延缓叶片衰老、促进侧芽生长。CTK与IAA的比例决定愈伤组织分化方向：CTK/IAA高→芽分化，低→根分化。","tags":["细胞分裂素","CTK","根尖"]},
    {"id":55,"topic":"植物激素","type":"multi","question":"关于五大经典植物激素的生理功能配对，正确的有？","options":{"A":"生长素(IAA)——促进细胞伸长、向光性、顶端优势","B":"赤霉素(GA)——促进茎伸长、种子萌发(激活alpha-淀粉酶)","C":"细胞分裂素(CTK)——促进细胞分裂、延缓叶片衰老","D":"脱落酸(ABA)——诱导种子休眠、响应干旱关闭气孔","E":"乙烯——促进果实成熟、器官脱落和衰老"},"answer":"ABCDE","difficulty":1,"explanation":"五大植物激素功能：（1）IAA：细胞伸长、向性、顶端优势、生根（2）GA：茎伸长、种子萌发时诱导糊粉层合成淀粉酶（3）CTK：细胞分裂、延缓衰老、侧芽生长（4）ABA：胁迫激素、种子休眠、气孔关闭（5）乙烯：催熟、三重反应、脱落。","tags":["植物激素","五大激素","功能"]},

    # Ca2+第二信使 (2)
    {"id":56,"topic":"信号转导","type":"choice","question":"钙调蛋白(Calmodulin, CaM)作为Ca2+的感受器蛋白，其激活机制是？","options":{"A":"CaM被PKA磷酸化后激活","B":"CaM结合4个Ca2+后构象改变，暴露疏水区与靶蛋白结合并调节其活性","C":"CaM直接进入细胞核调节基因表达","D":"CaM与G蛋白结合后激活"},"answer":"B","difficulty":2,"explanation":"CaM含4个EF-hand Ca2+结合域→结合4个Ca2+后构象显著改变→暴露疏水裂隙→与CaM依赖性蛋白激酶(CaMK)、MLCK等靶蛋白结合→激活/抑制靶蛋白。CaM本身无酶活性，是Ca2+信号的转导桥梁。","tags":["钙调蛋白","CaM","Ca2+","第二信使"]},
    {"id":57,"topic":"信号转导","type":"truefalse","question":"细胞内Ca2+浓度在静息状态下极低(~100nM)，受信号刺激后通过质膜钙通道或内质网IP3受体/RyR受体释放可迅速升高至约1uM，触发多种Ca2+依赖性反应。","answer":True,"difficulty":1,"explanation":"胞质[Ca2+]在静息时被Ca2+-ATP酶和Na+/Ca2+交换体维持在极低水平(~100nM)，信号刺激后通过电压门控钙通道、IP3受体(ER)或RyR受体(ER/SR)释放Ca2+→[Ca2+]升高至~1uM→激活CaM、PKC、钙蛋白酶等多种效应蛋白。","tags":["Ca2+","第二信使","IP3受体"]},

    # JAK-STAT通路 (2)
    {"id":58,"topic":"信号转导","type":"choice","question":"JAK-STAT信号通路与其他信号转导通路相比，最独特的特点是？","options":{"A":"通过第二信使cAMP传递信号","B":"受体本身具有酪氨酸激酶活性","C":"受体无激酶活性但结合JAK激酶，STAT被磷酸化后直接进入细胞核调节基因转录","D":"信号传递完全在细胞质中进行"},"answer":"C","difficulty":3,"explanation":"JAK-STAT是最短路径的信号通路：细胞因子(如EPO、GH)结合受体→受体二聚化→结合在受体胞内段的JAK相互磷酸化→JAK磷酸化受体Tyr残基→STAT的SH2识别并结合→JAK磷酸化STAT→STAT二聚化→直接入核结合DNA→调控转录。从受体激活到基因表达仅需少数几步。","tags":["JAK-STAT","信号转导","直接入核"]},
    {"id":59,"topic":"信号转导","type":"truefalse","question":"JAK-STAT通路中，STAT蛋白兼具SH2结构域（识别磷酸化受体）和DNA结合域，被磷酸化后直接作为转录因子入核激活靶基因表达。","answer":True,"difficulty":2,"explanation":"STAT(Signal Transducer and Activator of Transcription)蛋白C端含SH2识别磷酸酪氨酸，N端含DNA结合域。磷酸化后形成同/异二聚体→暴露NLS→importin介导入核→结合GAS元件(TTCNNNGAA)→激活靶基因转录。这一\"信号转导+转录因子\"二合一的设计使JAK-STAT成为最精简的信号通路。","tags":["STAT","SH2","转录因子"]},

    # Ras-MAPK (1)
    {"id":60,"topic":"信号转导","type":"choice","question":"Ras蛋白在RTK信号通路中充当分子开关，其活性形式是？","options":{"A":"Ras-GDP","B":"Ras-GTP","C":"Ras被磷酸化","D":"Ras去磷酸化"},"answer":"B","difficulty":1,"explanation":"Ras是小G蛋白：Ras-GTP为活性态（ON），Ras-GDP为非活性态（OFF）。RTK激活→Grb2-SOS复合物被招募→SOS是Ras的GEF→催化Ras释放GDP结合GTP→Ras-GTP→激活Raf→MEK→ERK(MAPK)级联。Ras自身GTP酶活性弱，需GAP加速水解。Ras突变(G12V等)锁定GTP结合态→持续增殖信号→约30%人类肿瘤含Ras突变。","tags":["Ras","GTP","分子开关"]},

    # 下丘脑-垂体轴 (1)
    {"id":61,"topic":"激素通论","type":"choice","question":"下丘脑-垂体-靶腺轴（三级激素调控）中，下丘脑分泌的激素属于？","options":{"A":"促激素(tropic hormone)","B":"释放/抑制激素(releasing/inhibiting hormone)","C":"靶腺激素","D":"反馈抑制因子"},"answer":"B","difficulty":1,"explanation":"三级调控轴：下丘脑分泌释放/抑制激素→垂体前叶分泌促激素→外周靶腺分泌靶腺激素→靶腺激素反馈抑制下丘脑和垂体（负反馈）。如TRH(下丘脑)→TSH(垂体)→T3/T4(甲状腺)→T3/T4反馈抑制TRH和TSH。","tags":["下丘脑","垂体","三级调控","负反馈"]},

    # 肾上腺素受体亚型 (1)
    {"id":62,"topic":"信号转导","type":"choice","question":"肾上腺素在肝脏和骨骼肌中分别通过不同受体发挥糖原分解作用，这两种受体及其下游通路分别是？","options":{"A":"肝：alpha1受体→PLC→IP3/DAG；肌：beta2受体→AC→cAMP","B":"肝：beta2受体→AC→cAMP→PKA；肌：beta2受体→AC→cAMP→PKA","C":"肝：beta2受体→AC→cAMP；肌：alpha1受体→PLC→IP3/DAG","D":"两者均通过alpha1受体"},"answer":"A","difficulty":3,"explanation":"肾上腺素在肝中主要通过alpha1受体→PLC→IP3→Ca2+→糖原磷酸化酶激活→糖原分解；在骨骼肌中通过beta2受体→AC→cAMP→PKA→磷酸化酶激酶→糖原分解。同一激素在不同组织通过不同受体和通路产生相同终效应，体现信号转导的组织特异性。","tags":["肾上腺素","alpha1受体","beta2受体","组织特异性"]},

    # 信号通路交叉对话 (1)
    {"id":63,"topic":"信号转导","type":"short","question":"简述信号转导中交叉对话(cross-talk)的概念，并以胰岛素和肾上腺素对糖原代谢的拮抗调控为例说明。","answer":"交叉对话：不同信号通路之间通过共享信号分子、相互磷酸化或第二信使的交互影响，实现信号的整合与协调。\n\n胰岛素vs肾上腺素对糖原代谢的拮抗：\n\n(1)肾上腺素通过beta受体→Gs→AC→cAMP↑→PKA活化→磷酸化糖原磷酸化酶激酶和糖原合酶。糖原磷酸化酶被激活(糖原分解↑)，糖原合酶被磷酸化失活(糖原合成↓)。净效应：糖原分解，血糖升高。\n\n(2)胰岛素通过RTK→PI3K→AKT→激活PDE（磷酸二酯酶）→cAMP↓→PKA活性降低。同时AKT激活蛋白磷酸酶1(PP1)→去磷酸化糖原磷酸化酶(失活)和糖原合酶(活化)。净效应：糖原合成↑，糖原分解↓。\n\n交叉对话：胰岛素通路通过降低cAMP水平来拮抗肾上腺素信号→两条通路在cAMP环节交叉。这体现了机体通过多重信号整合实现对糖原代谢的精确调控。","difficulty":3,"tags":["交叉对话","胰岛素","肾上腺素","cAMP"],"explanation":"本题目为简答题。"}
]

qs.extend(new_qs)
with open(qpath, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)
print(f"{len(qs)}Q done")
