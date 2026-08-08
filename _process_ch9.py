# -*- coding: utf-8 -*-
"""第九章处理: 删重题/修正/统一topic/补17题/重排id"""
import json

BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第九章'
QP = BASE + r'\questions.json'

with open(QP, encoding='utf-8') as f:
    qs = json.load(f)

by_id = {q['id']: q for q in qs}
assert len(by_id) == len(qs), 'id 不唯一'

# ---------- 1. 修正 Q8: C选项文字 ----------
q8 = by_id[8]
q8['options']['C'] = 'NLS是核蛋白被转运入核的必要条件而非充分条件'
q8['explanation'] = ('NLS富含碱性氨基酸（Lys、Arg），是亲核蛋白入核的必要条件而非充分条件——'
                     '入核还需要importin等蛋白因子协助并受其他因素影响。NLS入核后不被切除'
                     '（区别于信号肽），可位于蛋白质不同部位。')

# ---------- 2. 修正 Q94: 压缩比按课件多级螺旋模型(8400倍) ----------
q94 = by_id[94]
q94['answer'] = ('染色质多级压缩模型：\n'
                 '(1) DNA双螺旋（2nm）：遗传信息的分子基础。\n'
                 '(2) 核小体串珠链（约10nm）：约146bp DNA缠绕组蛋白八聚体（H2A、H2B、H3、H4各二分子）约1.75圈'
                 '形成核小体核心颗粒，组蛋白H1结合在连接DNA与核心颗粒交界处稳定结构，串珠状纤维为一级结构，'
                 '压缩约7倍。\n'
                 '(3) 螺线管（30nm）：核小体链在H1参与下每圈约6个核小体盘绕成中空螺线管（二级结构），'
                 '累计压缩约42倍。\n'
                 '(4) 超螺线管（约0.4μm）：螺线管进一步螺旋化形成圆筒状超螺线管（三级结构），累计压缩约1680倍。\n'
                 '(5) 染色单体（2~10μm）：超螺线管经进一步螺旋化与折叠形成中期染色单体（四级结构），'
                 '累计压缩约8400倍。\n'
                 '关键分子：组蛋白八聚体（核小体）、H1（稳定核小体并维持30nm螺线管）。')
q94['tags'] = ['染色质压缩', '核小体', '多级螺旋模型']
q94['explanation'] = '本题目为简答题，答案已包含完整分点解析。'

# ---------- 3. 统一 topic 为 851 考纲条目简称 ----------
# 核被膜(含核孔复合体/核纤层/核转运/核膜组装)
TOPIC_NE = '核被膜'
TOPIC_CHR = '染色质'
TOPIC_EXP = '染色质复制与表达'
TOPIC_NO = '核仁与核体'

map_topic = {}
for i in [1,2,3,4,5,6,7,8,9,10,38,41,42,43,47,52,54,55,56,59,63,64,69,70,74,76,80,81,82]:
    map_topic[i] = TOPIC_NE
for i in [11,12,13,14,15,16,17,18,19,20,22,23,24,25,26,27,28,29,37,39,40,44,45,46,48,51,53,
          57,58,60,66,71,72,77,78,83,84,92,93,94]:
    map_topic[i] = TOPIC_CHR
for i in [21,50,65,67,73,85,86,87,88,90,91]:
    map_topic[i] = TOPIC_EXP
for i in [30,31,32,33,34,35,36,49,61,62,68,75]:
    map_topic[i] = TOPIC_NO
assert set(map_topic) == set(by_id) - {79, 89}, 'topic映射与题目集合不一致'

# ---------- 4. 删除重复题 Q79(ChIP简答,与Q88重复) Q89(核仁周期,与Q34/Q49重复) ----------
for q in qs:
    if q['id'] in map_topic:
        q['topic'] = map_topic[q['id']]
qs = [q for q in qs if q['id'] in map_topic]

# ---------- 5. 补 17 题 ----------
new_questions = [
{
 "topic": TOPIC_NE, "type": "choice",
 "question": "核输出信号（NES）的主要特征是？",
 "options": {
  "A": "富含碱性氨基酸（Lys、Arg）的短序列",
  "B": "富含亮氨酸等疏水氨基酸的短肽序列，被核输出受体识别",
  "C": "位于蛋白质N端且出核后被切除",
  "D": "与NLS序列完全相同"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "NES富含亮氨酸等疏水氨基酸，被exportin/CRM1类核输出受体识别，介导蛋白质和RNA经核孔复合体主动转运出核。RNA出核依赖含NES的蛋白质因子，如HIV的Rev蛋白、TFIIIA等。",
 "tags": ["NES", "核输出", "核转运"]
},
{
 "topic": TOPIC_NE, "type": "multi",
 "question": "关于真核细胞RNA经核孔复合体出核转运的描述，正确的有？",
 "options": {
  "A": "由RNA聚合酶I转录的rRNA在核仁中与核糖体蛋白结合成亚基，以RNP形式出核，需耗能",
  "B": "由RNA聚合酶III转录的5S rRNA与tRNA出核是一种由蛋白质介导的过程",
  "C": "由RNA聚合酶II转录的hnRNA需完成加帽、加polyA尾及剪接等加工后才能出核",
  "D": "未成熟的前体RNA可以自由穿过核孔复合体出核",
  "E": "RNA出核依赖含核输出信号（NES）的蛋白质因子"
 },
 "answer": "ABCE",
 "difficulty": 3,
 "explanation": "RNA一般需加工为成熟分子才能出核（D错）：聚合酶I产物以RNP形式耗能出核，聚合酶III产物由蛋白质介导，聚合酶II产物（mRNA）经加帽、加尾、剪接后以载体介导的主动运输出核，且依赖NES蛋白因子。",
 "tags": ["RNA出核", "核转运", "RNA聚合酶"]
},
{
 "topic": TOPIC_CHR, "type": "choice",
 "question": "主要分布在染色体着丝粒部位的串联重复DNA是？",
 "options": {
  "A": "微卫星DNA",
  "B": "卫星DNA",
  "C": "小卫星DNA",
  "D": "散在重复序列DNA"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "卫星DNA重复单位长5~100bp，主要分布在染色体着丝粒部位，如人类着丝粒区α-卫星DNA家族。小卫星DNA重复单位长12~100bp、拷贝数高度可变，曾用于DNA指纹分析；微卫星DNA重复单位仅1~5bp，具高度多态性，是重要的遗传标记。",
 "tags": ["卫星DNA", "重复序列", "着丝粒"]
},
{
 "topic": TOPIC_CHR, "type": "choice",
 "question": "关于非组蛋白的描述，错误的是？",
 "options": {
  "A": "非组蛋白又称序列特异性DNA结合蛋白",
  "B": "非组蛋白能特异性识别DNA双螺旋大沟中的信息，靠氢键和离子键结合",
  "C": "不同组织细胞中非组蛋白的种类和数量相同且代谢周转慢",
  "D": "非组蛋白参与基因表达调控和染色质高级结构的形成"
 },
 "answer": "C",
 "difficulty": 2,
 "explanation": "非组蛋白具有多样性：不同组织细胞中非组蛋白的种类和数量都不相同，代谢周转快（C错）。它能特异性识别DNA大沟信息，并参与基因表达调控与染色质高级结构形成，可用凝胶延滞实验分离检测。",
 "tags": ["非组蛋白", "DNA结合蛋白", "染色质蛋白"]
},
{
 "topic": TOPIC_CHR, "type": "multi",
 "question": "关于染色质组装过程中核小体形成的描述，正确的有？",
 "options": {
  "A": "H3-H4四聚体首先由CAF1介导与新合成的裸露DNA结合",
  "B": "两个H2A-H2B异二聚体由NAP1和NAP2介导加入形成核心颗粒",
  "C": "新合成组蛋白H4上Lys5和Lys12被乙酰化",
  "D": "组蛋白去乙酰化和ISWI、SWI/SNF家族蛋白参与调节核小体间距",
  "E": "核小体形成不需要任何组装因子的参与"
 },
 "answer": "ABCD",
 "difficulty": 3,
 "explanation": "核小体组装：(1)H3-H4四聚体由CAF1介导与DNA结合；(2)两个H2A-H2B二聚体由NAP1/NAP2介导加入形成核心颗粒，H4上Lys5、Lys12乙酰化；(3)ATP建立规则间距，组蛋白去乙酰化，ISWI、SWI/SNF家族参与调节。E错——组装需要多种染色质组装因子。",
 "tags": ["核小体组装", "CAF1", "染色质复制"]
},
{
 "topic": TOPIC_CHR, "type": "choice",
 "question": "用2mol/L NaCl或硫酸葡聚糖加肝素处理HeLa细胞中期染色体后，可观察到？",
 "options": {
  "A": "核小体串珠结构",
  "B": "非组蛋白构成的染色体骨架和与骨架相连的DNA侧环",
  "C": "30nm螺线管结构",
  "D": "组蛋白八聚体结晶"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "高盐处理除去组蛋白和大部分非组蛋白后，电镜下可见非组蛋白构成的染色体骨架（chromosomal scaffold）和与骨架相连的无数DNA侧环，这是染色质组装放射环结构模型的实验基础。",
 "tags": ["染色体骨架", "放射环模型", "染色质高级结构"]
},
{
 "topic": TOPIC_EXP, "type": "choice",
 "question": "关于GC岛与DNA甲基化的关系，描述正确的是？",
 "options": {
  "A": "GC岛高度甲基化时基因通常具有转录活性",
  "B": "GC岛处于低甲基化或非甲基化状态时基因通常正常表达",
  "C": "GC岛不含CpG二核苷酸序列",
  "D": "DNA甲基化位点随机分布于整个基因组，与GC岛无关"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "GC岛是富含G、C碱基对的DNA区域，通常位于基因转录调控区附近，其CpG位点是DNA甲基化的主要靶点。低甲基化/非甲基化时基因具有转录活性（B对）；高度甲基化使染色质结构紧密，阻止转录复合物结合而抑制基因表达，是一种重要的表观遗传基因沉默机制。",
 "tags": ["GC岛", "DNA甲基化", "基因表达调控"]
},
{
 "topic": TOPIC_EXP, "type": "truefalse",
 "question": "DNA甲基化抑制基因转录的方式包括：干扰转录因子对DNA结合位点的识别，以及将转录激活因子识别的DNA序列转换为转录抑制因子的结合位点。",
 "answer": "true",
 "difficulty": 2,
 "explanation": "DNA甲基化是使基因转入持久遏制状态的重要条件，其抑制转录有两种方式：一是干扰转录因子对DNA结合位点的识别；二是将激活因子识别的序列转换为抑制因子结合位点。但甲基化并非使基因失活的普遍机制，且随演化程度提高而逐步增强。",
 "tags": ["DNA甲基化", "转录抑制", "基因表达调控"]
},
{
 "topic": TOPIC_EXP, "type": "choice",
 "question": "下列不属于转录因子DNA结合基序的是？",
 "options": {
  "A": "锌指结构",
  "B": "螺旋-转角-螺旋（HTH）",
  "C": "亮氨酸拉链",
  "D": "信号肽"
 },
 "answer": "D",
 "difficulty": 1,
 "explanation": "转录因子的DNA结合基序包括锌指、螺旋-转角-螺旋（HTH）、亮氨酸拉链和同源异形结构域等。信号肽是蛋白质跨膜运输的信号序列，不属于DNA结合基序。",
 "tags": ["转录因子", "DNA结合基序", "基因表达调控"]
},
{
 "topic": TOPIC_EXP, "type": "choice",
 "question": "亮氨酸拉链结构域中，亮氨酸残基在α-螺旋一侧有规律排列的间隔是？",
 "options": {
  "A": "每2~3个氨基酸出现一个",
  "B": "每6~7个氨基酸出现一个",
  "C": "每10~12个氨基酸出现一个",
  "D": "无规律随机分布"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "亮氨酸拉链区域由一段富含亮氨酸的α-螺旋构成，亮氨酸残基在螺旋一侧每间隔6~7个氨基酸出现一个。两个含亮氨酸拉链的蛋白质分子通过亮氨酸残基间的疏水相互作用像拉链一样结合，形成同源或异源二聚体。",
 "tags": ["亮氨酸拉链", "转录因子", "结构模体"]
},
{
 "topic": TOPIC_EXP, "type": "multi",
 "question": "关于隔离子（insulator）的描述，正确的有？",
 "options": {
  "A": "位于抑制状态与活化状态的染色质结构域之间",
  "B": "能防止不同状态的染色质结构域的结构特征向两侧扩展",
  "C": "可作为异染色质定向形成的起始位点",
  "D": "可阻止结构域外的增强子成分进入，提供拓扑隔离区",
  "E": "隔离子与基因表达调控无关"
 },
 "answer": "ABCD",
 "difficulty": 3,
 "explanation": "隔离子位于抑制与活化染色质结构域之间，防止结构特征向两侧扩展，作用包括：作为异染色质定向形成的起始位点；作为结构域两端的锚定点提供拓扑隔离区，阻止域外增强子进入；涉及追踪机制，阻止远端增强子复合体超越正常作用范围。E错。",
 "tags": ["隔离子", "染色质结构域", "基因表达调控"]
},
{
 "topic": TOPIC_EXP, "type": "multi",
 "question": "关于非编码RNA调控基因表达的描述，正确的有？",
 "options": {
  "A": "miRNA可抑制靶mRNA的翻译或促进其降解",
  "B": "siRNA介导靶mRNA的降解",
  "C": "piRNA抑制生殖细胞中的转座子",
  "D": "lncRNA可作为\"支架\"招募调控复合物或作为\"海绵\"吸附miRNA",
  "E": "长链非编码RNA不参与X染色体沉默"
 },
 "answer": "ABCD",
 "difficulty": 2,
 "explanation": "小非编码RNA中，miRNA抑制靶mRNA翻译或促降解，siRNA介导靶mRNA降解，piRNA抑制生殖细胞转座子；lncRNA可作支架招募调控复合物、作海绵吸附miRNA、直接结合核酸干扰转录加工，如Xist介导X染色体沉默（E错）。",
 "tags": ["非编码RNA", "miRNA", "lncRNA", "表观遗传"]
},
{
 "topic": TOPIC_CHR, "type": "multi",
 "question": "关于染色体显带技术的描述，正确的有？",
 "options": {
  "A": "Q带是中期染色体经喹吖因荧光染色后在紫外线照射下呈现的荧光亮带和暗带",
  "B": "G带带型一般与Q带相符，但Q带显示的人Y染色体特异荧光在G带带型上不出现",
  "C": "R带显示的带型与G带明暗相间带型正好相反，又称反带",
  "D": "C带主要显示着丝粒结构异染色质及其他染色体区段的异染色质部分",
  "E": "显带技术最重要的应用是区分细胞质中的细胞器"
 },
 "answer": "ABCD",
 "difficulty": 2,
 "explanation": "显带技术最重要的应用是明确鉴别一个核型中的任何一条染色体乃至某个易位片段，也可用于基因定位和染色体重构（E错）。Q带中富含AT区段为亮带、富含GC区段为暗带；G带与Q带基本相符；R带为反带；C带显示着丝粒区异染色质。",
 "tags": ["染色体显带", "Q带", "G带", "核型分析"]
},
{
 "topic": TOPIC_CHR, "type": "choice",
 "question": "关于巨大染色体的描述，正确的是？",
 "options": {
  "A": "多线染色体来源于核内有丝分裂，即核内DNA多次复制而细胞不分裂",
  "B": "多线染色体首先在哺乳动物肝细胞中发现",
  "C": "灯刷染色体出现在卵母细胞减数分裂终变期",
  "D": "灯刷染色体的侧环没有转录活性"
 },
 "answer": "A",
 "difficulty": 2,
 "explanation": "多线染色体来源于核内有丝分裂（DNA多次复制而细胞不分裂），子染色体并行排列，同源染色体配对紧密结合，首先在双翅目摇蚊幼虫唾腺细胞中发现；灯刷染色体是卵母细胞减数分裂第一次分裂双线期停留时形成的，侧环是RNA活跃转录区域。",
 "tags": ["巨大染色体", "多线染色体", "灯刷染色体"]
},
{
 "topic": TOPIC_CHR, "type": "choice",
 "question": "关于次缢痕与随体的描述，正确的是？",
 "options": {
  "A": "所有次缢痕都是核仁组织区",
  "B": "次缢痕的数目、位置和大小可作鉴定染色体的标记",
  "C": "随体是位于染色体中部的球形节段",
  "D": "随体与染色体主体直接相连，不经次缢痕"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "次缢痕是除主缢痕外染色体上其他浅染缢缩部位，其数目、位置和大小是某些染色体特有的形态特征，可作鉴定标记（B对）。NOR位于次缢痕部位，但并非所有次缢痕都是NOR（A错）；随体是位于染色体末端的球形节段，通过次缢痕区与主体相连（C、D错）。",
 "tags": ["次缢痕", "随体", "染色体形态"]
},
{
 "topic": TOPIC_CHR, "type": "truefalse",
 "question": "端粒酶是一种核糖核蛋白复合物，具有反转录酶的性质，以物种特异的内在RNA为模板，把合成的端粒重复序列添加到染色体3'端。",
 "answer": "true",
 "difficulty": 2,
 "explanation": "端粒酶以自身RNA为模板，反转录合成端粒重复序列加到染色体3'端，解决末端复制问题。生殖细胞和部分干细胞中有端粒酶活性，体细胞无端粒酶活性，肿瘤细胞具有表达端粒酶活性的能力。",
 "tags": ["端粒酶", "反转录酶", "染色体末端"]
},
{
 "topic": TOPIC_EXP, "type": "short",
 "question": "简述DNA甲基化抑制基因转录的机制及其生物学意义。",
 "answer": ("① 概念：DNA甲基化是指在DNA分子胞嘧啶碱基上添加甲基基团（通常在CpG二核苷酸的C5位），"
            "形成5-甲基胞嘧啶。\n"
            "② 抑制转录的两种方式：一是干扰转录因子对DNA结合位点的识别；"
            "二是将转录激活因子识别的DNA序列转换为转录抑制因子的结合位点。\n"
            "③ 与GC岛的关系：GC岛富含CpG序列，是DNA甲基化的主要靶点；GC岛高度甲基化时染色质结构紧密，"
            "阻止转录复合物结合，使基因沉默。\n"
            "④ 生物学意义：DNA甲基化是使基因转入持久遏制状态的重要条件，参与基因组印记、"
            "X染色体失活等表观遗传调控；但甲基化并非基因失活的普遍机制，且随演化程度提高而逐步增强。"),
 "difficulty": 2,
 "tags": ["DNA甲基化", "基因表达调控", "表观遗传"],
 "explanation": "本题目为简答题，答案已包含完整分点解析。"
},
]

qs.extend(new_questions)

# ---------- 6. 重排 id ----------
qs = sorted(qs, key=lambda q: q.get('id', 10 ** 9))
for new_id, q in enumerate(qs, start=1):
    q['id'] = new_id

with open(QP, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)

import collections
print('第九章处理后总题数:', len(qs))
print('题型分布:', dict(collections.Counter(q['type'] for q in qs)))
print('topic分布:', dict(collections.Counter(q['topic'] for q in qs)))
print('id连续:', [q['id'] for q in qs] == list(range(1, len(qs) + 1)))
