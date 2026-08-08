import json, re

qpath = r'细胞生物学题库\第九章\questions.json'
tpath = r'细胞生物学题库\第九章\terms.json'
qs = json.load(open(qpath, encoding='utf-8'))
ts = json.load(open(tpath, encoding='utf-8'))

# Auto-assign topic from tags
topic_map = {
    '核被膜': '核被膜', '核膜': '核被膜', '核孔': '核孔复合体', 'NPC': '核孔复合体',
    '核纤层': '核纤层', 'lamin': '核纤层', 'NLS': '核转运', '核定位': '核转运',
    '核输出': '核转运', 'importin': '核转运', 'Ran': '核转运',
    '核小体': '核小体', 'nucleosome': '核小体', '组蛋白': '组蛋白',
    'H1': '组蛋白', 'H2A': '组蛋白', 'H2B': '组蛋白', 'H3': '组蛋白', 'H4': '组蛋白',
    '常染色质': '染色质类型', '异染色质': '染色质类型', 'HP1': '染色质类型',
    '染色质重塑': '染色质重塑', 'SWI/SNF': '染色质重塑',
    '组蛋白修饰': '表观遗传', '乙酰化': '表观遗传', '甲基化': '表观遗传',
    '染色体': '染色体', '着丝粒': '染色体', '端粒': '染色体', '动粒': '染色体',
    '核仁': '核仁', 'rRNA': '核仁', 'NOR': '核仁',
    '核基质': '核基质', '核骨架': '核基质',
    '30nm': '染色质高级结构', 'X染色体': 'X染色体失活', '失活': 'X染色体失活',
    '巴氏小体': 'X染色体失活', 'Xist': 'X染色体失活',
}

for q in qs:
    if q.get('topic'): continue
    tags = q.get('tags', [])
    assigned = None
    for tag in tags:
        for pattern, topic in topic_map.items():
            if pattern in tag:
                assigned = topic
                break
        if assigned: break
    q['topic'] = assigned if assigned else '综合'

from collections import Counter
tc = Counter(q.get('topic','?') for q in qs)
print(f"Topics: {dict(tc)}")

# New terms
new_terms = [
    {"id":9,"term":"核输出信号(NES)","definition":"富含亮氨酸等疏水氨基酸的短肽序列，被核输出受体exportin/CRM1识别，介导蛋白质和RNA从核内经核孔复合体主动转运至细胞质。NES介导的核输出可被Leptomycin B抑制。","chapter":"第九章"},
    {"id":10,"term":"Ran GTPase","definition":"核质转运的关键调控小G蛋白，在核内以RanGTP形式存在(由RCC1催化)，在胞质以RanGDP形式存在(由RanGAP催化)。RanGTP梯度为importin释放货物和exportin结合货物提供方向性。","chapter":"第九章"},
    {"id":11,"term":"组蛋白八聚体","definition":"由H2A、H2B、H3、H4各二分子组成的八聚体蛋白质核心，约146bp DNA在其上缠绕约1.75圈形成核小体核心颗粒。H3-H4四聚体首先与DNA结合，两个H2A-H2B二聚体随后加入完成组装。","chapter":"第九章"},
    {"id":12,"term":"30nm染色质纤维","definition":"核小体串珠链在组蛋白H1参与下进一步折叠形成的螺线管结构，每圈约6个核小体，是间期染色质的主要存在形式，压缩比约40-50倍。依赖H1和核心组蛋白N端尾巴的相互作用。","chapter":"第九章"},
    {"id":13,"term":"组蛋白密码","definition":"组蛋白N端尾巴特定氨基酸残基上可逆的共价修饰(乙酰化、甲基化、磷酸化、泛素化等)组合构成密码，被特定阅读器蛋白识别后调控染色质结构和基因表达，是表观遗传调控的核心机制。","chapter":"第九章"},
    {"id":14,"term":"着丝粒(Centromere)","definition":"染色体主缢痕处的特化染色质区域，由alpha卫星DNA和CENP-A(H3变体)核小体构成，是动粒组装和纺锤体微管附着的位点。着丝粒位置决定染色体的形态分类。","chapter":"第九章"},
    {"id":15,"term":"端粒(Telomere)","definition":"真核染色体末端的重复DNA序列(人类为TTAGGG)，与Shelterin蛋白复合物结合形成T-loop结构，保护染色体末端不被识别为DNA双链断裂，防止末端融合和降解。端粒随细胞分裂逐渐缩短。","chapter":"第九章"},
    {"id":16,"term":"染色质免疫沉淀(ChIP)","definition":"利用甲醛交联固定细胞内蛋白质-DNA相互作用，用特异性抗体富集靶蛋白结合的DNA片段，通过qPCR或测序鉴定靶蛋白在基因组上的结合位点。是研究组蛋白修饰和转录因子结合的核心技术。","chapter":"第九章"},
    {"id":17,"term":"多线染色体","definition":"果蝇等昆虫唾液腺细胞中由多次DNA复制而不分裂形成的巨大染色体，含上千条平行染色单体。光镜下可见特征性带纹，疏松区(puff)是活跃转录位点，是研究基因表达的经典模型。","chapter":"第九章"},
    {"id":18,"term":"灯刷染色体","definition":"两栖类卵母细胞减数分裂双线期出现的特殊巨大染色体，由主轴和侧环组成。侧环是活跃转录的DNA区域，新生RNA链与蛋白质结合使侧环呈毛刷状，是研究转录的经典模型。","chapter":"第九章"},
    {"id":19,"term":"端粒酶(Telomerase)","definition":"由端粒酶RNA(TERC)和端粒酶反转录酶(TERT)组成的核糖核蛋白复合物，以自身RNA为模板在染色体3'端合成端粒重复序列，补偿DNA复制造成的末端缩短。在生殖干细胞和肿瘤细胞中高表达。","chapter":"第九章"},
    {"id":20,"term":"核纤层蛋白病","definition":"由LMNA基因突变导致核纤层蛋白A/C结构异常引起的一组遗传病，如Hutchinson-Gilford早老症。突变的prelamin A(progerin)永久锚定在核内膜，导致核形态异常和染色质组织紊乱。","chapter":"第九章"},
]
ts.extend(new_terms)
with open(tpath, 'w', encoding='utf-8') as f:
    json.dump(ts, f, ensure_ascii=False, indent=2)
print(f"Terms: {len(ts)}")

# New questions
new_qs = [
    {"id":80,"topic":"核纤层","type":"choice","question":"Hutchinson-Gilford早老症(HGPS)的分子机制是？","options":{"A":"端粒酶基因突变","B":"LMNA基因突变导致截短的核纤层蛋白A(progerin)积累，核纤层结构异常","C":"核孔复合体蛋白Nup98突变","D":"组蛋白H3K9甲基转移酶缺陷"},"answer":"B","difficulty":2,"explanation":"HGPS由LMNA基因点突变导致产生缺失Zmpste24切割位点的prelamin A(progerin)，progerin永久法尼基化锚定在核内膜，导致核纤层结构异常、核形态改变、异染色质丢失，加速衰老。体现核纤层的核心功能。","tags":["早老症","核纤层蛋白","lamin A","progerin"]},
    {"id":81,"topic":"核转运","type":"choice","question":"核质转运中，RanGTP在核内和胞质中不对称分布由哪两个关键酶维持？","options":{"A":"核内RCC1(GEF)催化RanGDP->RanGTP，胞质RanGAP催化RanGTP->RanGDP","B":"核内RanGAP催化，胞质RCC1催化","C":"核内和胞质均有等量RanGTP和RanGDP","D":"仅由Ran本身的GTP酶活性决定"},"answer":"A","difficulty":3,"explanation":"RCC1(RanGEF)通过染色质结合定位于核内，胞质RanGAP催化RanGTP水解。RanGTP梯度为importin释放货物(核内)和exportin结合货物(核内)提供方向性驱动力。","tags":["Ran","RCC1","RanGAP","核转运"]},
    {"id":82,"topic":"核转运","type":"multi","question":"关于核质转运中Ran GTPase系统的描述，正确的有？","options":{"A":"RCC1定位于细胞核内，催化RanGDP转化为RanGTP","B":"RanGAP定位于细胞质，催化RanGTP水解为RanGDP","C":"importin在核内遇到RanGTP后释放货物蛋白质","D":"exportin需要RanGTP结合才能与NES货物形成复合物","E":"RanGTP梯度为核质定向转运提供能量来源"},"answer":"ABCDE","difficulty":3,"explanation":"五项全正确。RanGTP梯度是核质转运方向性的分子基础。","tags":["Ran","importin","exportin","核转运"]},
    {"id":83,"topic":"组蛋白变体","type":"choice","question":"着丝粒特异性组蛋白H3变体CENP-A的功能是？","options":{"A":"促进着丝粒区转录","B":"替代常规H3形成着丝粒特化核小体，作为动粒组装平台","C":"催化DNA复制起始","D":"参与端粒维持"},"answer":"B","difficulty":2,"explanation":"CENP-A(CenH3)替代H3掺入着丝粒核小体，形成特化染色质结构作为动粒组装位点。CENP-A是着丝粒的表观遗传标记，不依赖DNA序列即可指定着丝粒位置。","tags":["CENP-A","着丝粒","组蛋白变体"]},
    {"id":84,"topic":"组蛋白变体","type":"choice","question":"DNA双链断裂后，H2AX快速磷酸化(gamma-H2AX)的生物学意义是？","options":{"A":"促进细胞凋亡","B":"作为DNA损伤的早期标志，在断裂位点形成焦点招募DNA修复蛋白","C":"激活细胞周期检查点激酶","D":"促进染色质解凝以利转录"},"answer":"B","difficulty":2,"explanation":"DNA损伤后ATM/ATR磷酸化H2AX Ser139形成gamma-H2AX，在断裂位点两侧延伸形成修饰域，荧光显微镜下呈焦点(foci)，招募MDC1、53BP1等修复因子启动DNA修复。是最广泛应用的DNA损伤标志物。","tags":["gamma-H2AX","DNA损伤","组蛋白变体"]},
    {"id":85,"topic":"染色质重塑","type":"choice","question":"SWI/SNF染色质重塑复合物利用ATP水解能量的主要作用是？","options":{"A":"催化组蛋白乙酰化","B":"沿DNA滑动或移除核小体，改变染色质可及性","C":"甲基化DNA启动子区域","D":"降解连接组蛋白H1"},"answer":"B","difficulty":2,"explanation":"SWI/SNF利用ATP水解能量改变核小体位置和构象，暴露或遮蔽特定DNA序列，调控转录因子结合。约20%人类肿瘤含SWI/SNF亚基突变，体现其在基因调控和肿瘤抑制中的关键作用。","tags":["SWI/SNF","染色质重塑","ATP依赖"]},
    {"id":86,"topic":"染色质重塑","type":"truefalse","question":"染色质重塑复合物利用ATP水解能量可滑动、移除或置换核小体，从而调节染色质对转录因子和RNA聚合酶的可及性。","answer":True,"difficulty":1,"explanation":"ATP依赖的染色质重塑复合物(SWI/SNF、ISWI、CHD、INO80四大家族)是染色质动态调控的核心机器。","tags":["染色质重塑","核小体","ATP"]},
    {"id":87,"topic":"表观遗传","type":"choice","question":"组蛋白密码假说的核心思想是？","options":{"A":"组蛋白序列本身编码遗传信息","B":"组蛋白N端尾巴特定氨基酸的组合修饰模式被阅读器蛋白识别，调控不同的染色质功能状态","C":"组蛋白通过其三维结构决定基因表达","D":"组蛋白与DNA间的氢键模式决定基因活性"},"answer":"B","difficulty":1,"explanation":"组蛋白密码假说：组蛋白尾部多种共价修饰(乙酰化/甲基化/磷酸化等)的类型、位点和组合构成密码，被含特定结构域(溴结构域识别乙酰化、chromodomain识别甲基化)的阅读器解读，调控转录、复制、修复等。","tags":["组蛋白密码","表观遗传","组蛋白修饰"]},
    {"id":88,"topic":"表观遗传","type":"short","question":"简述染色质免疫沉淀技术(ChIP)的基本原理及其在研究基因表达调控中的应用。","answer":"基本原理：(1)甲醛交联：活细胞经甲醛处理使组蛋白/转录因子与DNA共价交联固定体内结合状态。(2)超声/酶切打断：将染色质随机打断为200-500bp片段。(3)免疫沉淀：用靶蛋白特异性抗体富集含目标蛋白质的DNA片段。(4)解交联与纯化：高温/蛋白酶K逆转交联后纯化DNA。(5)检测：qPCR检测特定位点(ChIP-qPCR)或高通量测序(ChIP-seq)获得全基因组结合谱。\n\n应用：(1)鉴定特定转录因子在全基因组的结合位点。(2)绘制组蛋白修饰(H3K4me3启动子、H3K27ac增强子、H3K27me3沉默区等)的全基因组分布。(3)研究不同条件下染色质修饰的动态变化。(4)联合RNA-seq建立染色质状态-基因表达的调控网络。","difficulty":3,"tags":["ChIP","表观遗传","组蛋白修饰"],"explanation":"本题目为简答题，答案已包含完整分点解析。"},
    {"id":89,"topic":"核仁","type":"choice","question":"核仁在有丝分裂过程中经历怎样的动态变化？","options":{"A":"核仁在整个有丝分裂期间保持不变","B":"核仁在有丝分裂前期解体，末期在NOR处重新组装","C":"核仁仅在S期存在","D":"核仁在中期迁移至纺锤体两极"},"answer":"B","difficulty":1,"explanation":"有丝分裂前期rRNA转录停止，核仁解体，核仁蛋白部分散布于胞质。末期rRNA转录恢复，核仁蛋白重新被招募至NOR，核仁重新组装。核仁的周期性变化与rRNA转录活性精密耦合。","tags":["核仁","有丝分裂","NOR"]},
    {"id":90,"topic":"X染色体失活","type":"choice","question":"雌性哺乳动物X染色体失活的关键调控RNA是？","options":{"A":"Xist(X-inactive specific transcript)","B":"Tsix","C":"HOTAIR","D":"MALAT1"},"answer":"A","difficulty":2,"explanation":"Xist是长约17kb的lncRNA，从失活X染色体(Xi)上的XIC转录，顺式扩散包裹Xi并招募PRC2复合物催化H3K27me3修饰，导致Xi异染色质化形成巴氏小体。Tsix是Xist的反义转录物，仅在活性X上表达阻止Xist积累。","tags":["Xist","X染色体失活","巴氏小体"]},
    {"id":91,"topic":"X染色体失活","type":"truefalse","question":"雌性哺乳动物体细胞中一条X染色体上的Xist基因转录产生长链非编码RNA，顺式包裹该X染色体并招募染色质修饰因子使其异染色质化，形成巴氏小体。","answer":True,"difficulty":1,"explanation":"Xist顺式扩散覆盖Xi，招募PRC2催化H3K27me3修饰，HP1结合后染色质凝集，转录沉默。这是lncRNA介导表观遗传调控的经典范例。","tags":["Xist","X染色体失活","lncRNA"]},
    {"id":92,"topic":"端粒","type":"choice","question":"端粒末端形成的T-loop结构的主要功能是？","options":{"A":"促进端粒酶结合","B":"保护染色体末端不被识别为DNA双链断裂，防止DNA损伤应答和末端融合","C":"作为DNA复制起点","D":"招募转录因子促进端粒附近基因表达"},"answer":"B","difficulty":2,"explanation":"端粒3'单链末端侵入双链端粒区形成T-loop，结合Shelterin蛋白复合物(TRF1、TRF2、POT1等)，阻止ATM/ATR激酶识别端粒为DSB，抑制NHEJ和HR修复途径，保护染色体末端。TRF2缺失导致末端融合。","tags":["T-loop","端粒","Shelterin"]},
    {"id":93,"topic":"染色质类型","type":"multi","question":"关于常染色质与异染色质的比较，正确的有？","options":{"A":"常染色质染色浅、结构松散、转录活跃","B":"异染色质染色深、高度凝缩、转录不活跃","C":"组成性异染色质(如着丝粒区)在所有细胞类型中始终凝缩","D":"兼性异染色质(如失活X染色体)在特定细胞类型或发育阶段可发生常染色质-异染色质转换","E":"HP1蛋白通过识别H3K9me3修饰参与异染色质的形成和扩展"},"answer":"ABCDE","difficulty":2,"explanation":"五项全正确。HP1的chromodomain识别H3K9me3后，通过自身二聚化和招募SUV39H1甲基转移酶，使异染色质标记沿染色质纤维扩展。","tags":["常染色质","异染色质","HP1"]},
    {"id":94,"topic":"染色质高级结构","type":"short","question":"简述从DNA双螺旋到中期染色体的染色质逐级压缩过程及各层次的关键分子。","answer":"染色质多级压缩模型：\n\n(1)DNA双螺旋(2nm)：遗传信息的分子基础。\n\n(2)核小体串珠链(11nm)：约146bp DNA缠绕组蛋白八聚体(H2A、H2B、H3、H4各二分子)形成核小体核心，H1结合在连接DNA处。压缩比约7倍。\n\n(3)30nm染色质纤维：核小体链在H1协助下盘绕成螺线管或之字形排列，每圈约6个核小体。压缩比约40-50倍。\n\n(4)环状结构域(300nm)：30nm纤维锚定在染色体支架(由Topo IIalpha、Condensin等组成)上形成30-100kb环状结构域。压缩比约1000倍。\n\n(5)中期染色体(700-1400nm)：环状结构域经Condensin II介导进一步轴向压缩形成可见染色单体。总压缩比约10000-20000倍。\n\n关键分子：组蛋白(核小体)、H1(30nm纤维)、Cohesin(环状结构域)、Condensin(中期染色体凝集)。","difficulty":3,"tags":["染色质压缩","核小体","30nm纤维"],"explanation":"本题目为简答题，答案已包含完整分点解析。"}
]

qs.extend(new_qs)
with open(qpath, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

from collections import Counter
types = Counter(q['type'] for q in qs)
print(f"Done: {len(qs)}Q, types={dict(types)}, Terms: {len(ts)}")
no_t = sum(1 for q in qs if not q.get('topic'))
print(f"Still no topic: {no_t}")
