import json, os

path = r'细胞生物学题库\第十章\questions.json'
qs = json.load(open(path, encoding='utf-8'))

# Delete redundant Q12, Q20, Q21
qs = [q for q in qs if q['id'] not in [12, 20, 21]]
print(f"After deletion: {len(qs)} questions")

# New questions
new_qs = [
    # ===== 抗生素靶点 (8题) =====
    {
        "id": 38, "topic": "抗生素与核糖体", "type": "choice",
        "question": "四环素（Tetracycline）抑制原核生物蛋白质合成的机制是？",
        "options": {"A": "与50S大亚基结合，抑制肽酰转移酶活性", "B": "与30S小亚基结合，阻止氨酰-tRNA进入A位点", "C": "与50S大亚基结合，阻止转位", "D": "引起30S小亚基读码错误"},
        "answer": "B", "difficulty": 2,
        "explanation": "四环素与30S小亚基结合，阻止氨酰-tRNA进入A位点。A描述氯霉素，C描述红霉素，D描述链霉素。抗生素靶点差异是考研高频考点。",
        "tags": ["抗生素", "四环素", "30S亚基"]
    },
    {
        "id": 39, "topic": "抗生素与核糖体", "type": "choice",
        "question": "氯霉素（Chloramphenicol）抑制细菌蛋白质合成的分子靶点是？",
        "options": {"A": "与30S小亚基16S rRNA结合，阻止起始", "B": "与50S大亚基23S rRNA结合，抑制肽酰转移酶活性", "C": "与EF-G竞争结合核糖体", "D": "促使肽酰-tRNA提前脱落"},
        "answer": "B", "difficulty": 2,
        "explanation": "氯霉素与50S大亚基23S rRNA结合，抑制肽酰转移酶活性，阻断肽键形成。是50S亚基抑制剂的典型代表。",
        "tags": ["抗生素", "氯霉素", "50S亚基", "肽酰转移酶"]
    },
    {
        "id": 40, "topic": "抗生素与核糖体", "type": "choice",
        "question": "链霉素（Streptomycin）与核糖体30S小亚基结合后导致的主要后果是？",
        "options": {"A": "阻止氨酰-tRNA进入A位点", "B": "抑制肽键形成", "C": "引起mRNA读码错误，合成异常蛋白质", "D": "阻止大小亚基解离"},
        "answer": "C", "difficulty": 2,
        "explanation": "链霉素与30S小亚基结合后引起读码错误（misreading），导致合成异常蛋白质。这是链霉素杀菌的关键机制。四环素阻止A位点进入（A），但链霉素的特异性在于诱导密码子-反密码子错配。",
        "tags": ["抗生素", "链霉素", "读码错误"]
    },
    {
        "id": 41, "topic": "抗生素与核糖体", "type": "choice",
        "question": "红霉素（Erythromycin）通过结合50S大亚基来抑制细菌蛋白质合成，其具体作用环节是？",
        "options": {"A": "抑制氨酰-tRNA进入A位点", "B": "抑制肽键形成", "C": "阻止肽酰-tRNA从A位点向P位点的转位", "D": "阻止起始复合物形成"},
        "answer": "C", "difficulty": 3,
        "explanation": "红霉素与50S大亚基结合，在肽链延伸的出口通道处形成空间位阻，阻止肽酰-tRNA的转位和新生肽链的延伸。与氯霉素（抑制肽键形成）和四环素（阻止进A位）作用环节均不同。",
        "tags": ["抗生素", "红霉素", "转位"]
    },
    {
        "id": 42, "topic": "抗生素与核糖体", "type": "choice",
        "question": "嘌呤霉素（Puromycin）抑制蛋白质合成的机制具有特殊的研究价值，这是因为？",
        "options": {"A": "它不可逆地结合50S大亚基", "B": "其结构与氨酰-tRNA的3'端（氨基酸-AMP）类似，使肽链提前终止", "C": "它特异性降解mRNA", "D": "它抑制氨酰-tRNA合成酶"},
        "answer": "B", "difficulty": 2,
        "explanation": "嘌呤霉素的结构与氨酰-tRNA 3'端（即酪氨酰-AMP）类似，可进入A位点接受肽酰转移酶催化，使肽链转移到嘌呤霉素上而提前释放。因其模拟tRNA末端而被广泛用于核糖体功能研究。",
        "tags": ["抗生素", "嘌呤霉素", "结构类似物"]
    },
    {
        "id": 43, "topic": "抗生素与核糖体", "type": "truefalse",
        "question": "多种抗生素（如四环素、氯霉素、链霉素）能选择性抑制细菌蛋白质合成而不显著影响人细胞，其分子基础在于原核与真核核糖体的结构差异。",
        "answer": True, "difficulty": 1,
        "explanation": "原核70S与真核80S核糖体在rRNA和蛋白质组成上存在显著差异，这使抗生素能选择性靶向原核核糖体。这也是抗生素作为抗菌药物的核心原理。",
        "tags": ["抗生素", "选择性", "原核/真核差异"]
    },
    {
        "id": 44, "topic": "抗生素与核糖体", "type": "multi",
        "question": "以下抗生素中，其作用靶点位于原核核糖体50S大亚基的有？",
        "options": {"A": "氯霉素（抑制肽酰转移酶活性）", "B": "红霉素（阻止转位）", "C": "四环素（阻止氨酰-tRNA进入A位点）", "D": "链霉素（引起读码错误）", "E": "嘌呤霉素（使肽链提前终止）"},
        "answer": "AB", "difficulty": 2,
        "explanation": "A和B作用于50S大亚基。C和D作用于30S小亚基。E嘌呤霉素不直接作用于特定亚基，而是作为氨酰-tRNA类似物进入A位点使肽链提前终止。此题考察抗生素靶点归类，是高频多选题。",
        "tags": ["抗生素", "50S亚基", "归类"]
    },
    {
        "id": 45, "topic": "抗生素与核糖体", "type": "short",
        "question": "以四环素和氯霉素为代表，分别说明作用于核糖体30S小亚基和50S大亚基的抗生素的抑制机制，并阐述这些抗生素选择性抑制细菌蛋白质合成的分子基础。",
        "answer": "一、30S小亚基抑制剂（以四环素为代表）：\n① 四环素与30S小亚基结合，空间位阻阻止氨酰-tRNA进入A位点，阻断延伸循环起始步骤。\n② 链霉素也与30S结合，但机制不同——引起mRNA读码错误，合成无功能异常蛋白质。\n\n二、50S大亚基抑制剂（以氯霉素为代表）：\n① 氯霉素与50S大亚基23S rRNA结合，抑制肽酰转移酶活性，阻断肽键形成。\n② 红霉素与50S大亚基结合，在新生肽链出口通道形成位阻，阻止转位和肽链延伸。\n\n三、选择性抑制的分子基础：\n① 原核生物核糖体为70S（50S+30S），真核生物胞质核糖体为80S（60S+40S），两者在rRNA种类、蛋白质组成、亚基大小上均有显著差异。\n② 抗生素利用这些结构差异选择性结合原核核糖体特定位点，对真核80S核糖体亲和力低或不结合。\n③ 这使抗生素成为理想的抗菌药物——抑制细菌生长而不（显著）影响人体细胞。\n④ 线粒体核糖体近似70S，因此高剂量某些抗生素也可能对线粒体蛋白质合成产生一定影响（副作用机制之一）。",
        "difficulty": 2,
        "tags": ["抗生素", "30S", "50S", "选择性抑制"],
        "explanation": "本题目为简答题，答案已包含完整分点解析内容，参见answer字段。"
    },

    # ===== 原核/真核翻译系统差异 (6题) =====
    {
        "id": 46, "topic": "翻译系统差异", "type": "choice",
        "question": "原核生物mRNA通常为多顺反子（polycistronic），这意味着？",
        "options": {"A": "一条mRNA只编码一种蛋白质", "B": "一条mRNA可编码多种蛋白质", "C": "一条mRNA需经剪接后才具翻译活性", "D": "一条mRNA只能被一个核糖体翻译"},
        "answer": "B", "difficulty": 1,
        "explanation": "多顺反子mRNA含多个开放阅读框，可编码多种功能相关的蛋白质（如lac操纵子编码3种酶）。真核mRNA为单顺反子。",
        "tags": ["多顺反子", "原核mRNA"]
    },
    {
        "id": 47, "topic": "翻译系统差异", "type": "choice",
        "question": "原核细胞中转录与翻译可以同时同地进行，其结构基础是？",
        "options": {"A": "原核细胞拥有内质网结构", "B": "原核细胞无核膜，mRNA边转录边与核糖体结合启动翻译", "C": "原核mRNA稳定性极高", "D": "原核核糖体翻译速度远快于RNA聚合酶转录速度"},
        "answer": "B", "difficulty": 1,
        "explanation": "原核细胞无细胞核，转录和翻译发生在同一区室，mRNA在转录未完成前即可被核糖体结合并启动翻译。真核细胞因核膜分隔，转录和翻译有时空分离。",
        "tags": ["转录翻译耦联", "原核"]
    },
    {
        "id": 48, "topic": "翻译系统差异", "type": "truefalse",
        "question": "真核细胞中，转录发生在细胞核内，翻译发生在细胞质中，两个过程因核膜分隔而存在明确的时间先后顺序。",
        "answer": True, "difficulty": 1,
        "explanation": "真核mRNA先在核内转录并加工（加帽、剪接、加尾），然后通过核孔复合体转运至细胞质，在细胞质中完成翻译。这是原核与真核基因表达的重要差异之一。",
        "tags": ["转录翻译分离", "真核", "核膜"]
    },
    {
        "id": 49, "topic": "翻译系统差异", "type": "truefalse",
        "question": "原核细胞mRNA不需要5'加帽、3'加polyA尾和剪接等转录后加工过程，可直接作为翻译模板。",
        "answer": True, "difficulty": 2,
        "explanation": "原核mRNA不经历真核mRNA的加帽、加尾、剪接等加工过程。但需注意原核rRNA和tRNA前体仍需加工成熟。这是原核/真核mRNA的核心区别之一。",
        "tags": ["原核mRNA", "无加工"]
    },
    {
        "id": 50, "topic": "翻译系统差异", "type": "multi",
        "question": "与原核细胞相比，真核细胞蛋白质合成系统的特征包括？",
        "options": {"A": "mRNA为多顺反子结构", "B": "mRNA需经5'加帽、剪接、3'加polyA尾等加工", "C": "翻译起始依赖5'帽子识别和扫描机制", "D": "转录和翻译因核膜分隔而时空分离", "E": "起始氨酰-tRNA为甲酰甲硫氨酰-tRNA"},
        "answer": "BCD", "difficulty": 2,
        "explanation": "A错误——真核为单顺反子，原核为多顺反子。E错误——真核起始tRNA携带甲硫氨酸（不被甲酰化），原核才是fMet-tRNA。BCD均为真核特征。",
        "tags": ["真核", "翻译", "特征"]
    },
    {
        "id": 51, "topic": "翻译系统差异", "type": "short",
        "question": "从核糖体类型、mRNA结构、起始识别机制和翻译后加工四个方面，比较原核细胞与真核细胞蛋白质合成系统的主要差异。",
        "answer": "① 核糖体类型：原核为70S（50S+30S），真核胞质为80S（60S+40S）；真核线粒体和叶绿体含自身70S样核糖体。\n\n② mRNA结构：原核为多顺反子mRNA，不需加工修饰即可翻译，且可转录-翻译同时进行；真核为单顺反子mRNA，需在核内完成5'加帽、剪接内含子、3'加polyA尾等加工，成熟后经核孔转运至胞质翻译，转录与翻译有时空分离。\n\n③ 起始识别机制：原核依赖16S rRNA 3'端与mRNA上SD序列互补配对定位起始密码子；真核mRNA无SD序列，小亚基依赖翻译起始因子识别5'帽子结构，然后沿mRNA 5'→3'扫描寻找起始AUG（扫描机制）。\n\n④ 翻译后加工与定位：原核无内质网和高尔基体，蛋白质加工简单（磷酸化、甲基化等）；真核拥有完善内膜系统，附着内质网上合成的蛋白质进入内质网腔完成信号肽切除、糖基化等加工，经高尔基体分选后精准定位到目的地。",
        "difficulty": 2,
        "tags": ["原核/真核", "蛋白质合成", "比较"],
        "explanation": "本题目为简答题，答案已包含完整分点解析内容，参见answer字段。"
    },

    # ===== IF1/IF2 详细分工 (4题) =====
    {
        "id": 52, "topic": "起始因子", "type": "choice",
        "question": "原核翻译起始因子IF1的主要功能是？",
        "options": {"A": "携带GTP协助起始tRNA进入P位点", "B": "与30S亚基A位点结合，防止氨酰-tRNA错误进入A位点", "C": "防止50S大亚基提前与30S小亚基结合", "D": "识别终止密码子并终止翻译"},
        "answer": "B", "difficulty": 2,
        "explanation": "IF1结合于30S亚基A位点：①防止氨酰-tRNA在起始完成前进入A位点；②协助IF2和IF3的功能。A描述IF2，C描述IF3。三者分工明确，是原核翻译起始的选择题高频考点。",
        "tags": ["IF1", "起始因子", "翻译起始"]
    },
    {
        "id": 53, "topic": "起始因子", "type": "choice",
        "question": "原核起始因子IF2是一种GTP结合蛋白，其核心功能是？",
        "options": {"A": "识别SD序列", "B": "协助第一个氨酰-tRNA（fMet-tRNA）进入核糖体P位点", "C": "催化肽键形成", "D": "促使核糖体大小亚基解离"},
        "answer": "B", "difficulty": 2,
        "explanation": "IF2-GTP与fMet-tRNA形成复合物，协助起始tRNA特异性进入30S亚基P位点。IF2的GTP酶活性在50S亚基结合后被激活，水解GTP后IF2释放。",
        "tags": ["IF2", "GTP结合蛋白", "fMet-tRNA"]
    },
    {
        "id": 54, "topic": "起始因子", "type": "truefalse",
        "question": "IF1通过占据核糖体A位点，防止起始阶段氨酰-tRNA错误进入A位点，同时协助IF2和IF3完成翻译起始。",
        "answer": True, "difficulty": 1,
        "explanation": "IF1是多功能起始因子：占据A位点阻止氨酰-tRNA错误入位，增强IF2活性，协同IF3防止亚基提前结合。",
        "tags": ["IF1", "翻译起始"]
    },
    {
        "id": 55, "topic": "起始因子", "type": "multi",
        "question": "关于原核翻译起始因子的功能配对，正确的有？",
        "options": {"A": "IF1——结合30S A位点，防止氨酰-tRNA在起始完成前错误入位", "B": "IF2——GTP结合蛋白，协助fMet-tRNA进入P位点", "C": "IF3——防止50S大亚基提前与30S小亚基结合，协助第一个氨酰-tRNA入位", "D": "IF3——催化50S大亚基与30S小亚基的最终组装", "E": "三种起始因子均在70S起始复合物形成后保留在核糖体上"},
        "answer": "ABC", "difficulty": 2,
        "explanation": "D错误——IF3防止50S提前结合而非促进组装。E错误——三种IF在70S起始复合物形成后均释放。ABC为IF1/IF2/IF3正确功能。",
        "tags": ["IF1", "IF2", "IF3", "功能配对"]
    },

    # ===== 真核起始扫描机制 (4题) =====
    {
        "id": 56, "topic": "真核起始机制", "type": "choice",
        "question": "真核细胞核糖体小亚基识别mRNA并定位起始密码子的机制是？",
        "options": {"A": "通过16S rRNA 3'端与SD序列互补配对", "B": "依赖翻译起始因子识别5'帽子，然后沿mRNA 5'→3'方向扫描寻找AUG", "C": "核糖体随机结合mRNA任意位置", "D": "直接与polyA尾结合后扫描"},
        "answer": "B", "difficulty": 2,
        "explanation": "真核40S小亚基通过eIF4F复合物识别mRNA 5'帽子→沿5'→3'方向扫描→识别第一个合适的AUG（通常位于Kozak序列中）作为起始密码子。A描述的是原核SD序列机制。",
        "tags": ["扫描机制", "帽子识别", "真核起始"]
    },
    {
        "id": 57, "topic": "真核起始机制", "type": "choice",
        "question": "真核mRNA翻译起始的扫描过程中，40S小亚基移动的方向和寻找的目标是？",
        "options": {"A": "3'→5'方向扫描，寻找polyA尾", "B": "5'→3'方向扫描，寻找第一个合适的AUG起始密码子", "C": "5'→3'方向扫描，寻找SD序列", "D": "随机方向扫描，寻找任意AUG"},
        "answer": "B", "difficulty": 1,
        "explanation": "40S小亚基从5'帽子处开始，沿5'→3'方向扫描，通常识别第一个处于合适上下文（Kozak序列）中的AUG作为起始密码子。这是真核翻译起始的经典扫描模型。",
        "tags": ["扫描机制", "AUG", "Kozak序列"]
    },
    {
        "id": 58, "topic": "真核起始机制", "type": "truefalse",
        "question": "真核细胞mRNA不存在类似原核SD序列的保守核糖体结合序列，小亚基依赖起始因子识别5'帽子结构进行翻译起始。",
        "answer": True, "difficulty": 1,
        "explanation": "真核无SD序列，翻译起始主要通过eIF4E识别5'帽子→eIF4G桥接→40S亚基被招募→沿5'→3'扫描至起始AUG。这是原核与真核翻译起始最本质的区别之一。",
        "tags": ["SD序列", "帽子结构", "真核"]
    },
    {
        "id": 59, "topic": "真核起始机制", "type": "multi",
        "question": "关于原核与真核mRNA翻译起始识别机制的比较，正确的有？",
        "options": {"A": "原核依赖SD序列与16S rRNA 3'端互补配对", "B": "真核依赖eIF4F复合物识别5'帽子，40S亚基沿mRNA 5'→3'扫描", "C": "原核起始tRNA为fMet-tRNA，真核为Met-tRNA（无甲酰化）", "D": "原核需要十多种起始因子，真核仅需3种", "E": "真核mRNA中存在Kozak序列有助于AUG的识别效率"},
        "answer": "ABCE", "difficulty": 2,
        "explanation": "D错误——恰好相反：原核仅需3种起始因子（IF1-3），真核需要十多种eIFs参与。其余选项正确。",
        "tags": ["原核/真核", "起始识别", "比较"]
    },

    # ===== 延伸因子循环 (4题) =====
    {
        "id": 60, "topic": "延伸因子", "type": "choice",
        "question": "原核延伸因子EF-Tu的核心功能是？",
        "options": {"A": "催化肽键形成", "B": "与GTP和氨酰-tRNA形成复合物，将氨酰-tRNA运送到核糖体A位点", "C": "催化核糖体沿mRNA转位", "D": "识别终止密码子"},
        "answer": "B", "difficulty": 2,
        "explanation": "EF-Tu·GTP·氨酰-tRNA三元复合物将正确的氨酰-tRNA运送到A位点。密码子-反密码子配对正确后，EF-Tu水解GTP并释放。EF-Tu不参与肽键形成（由23S rRNA催化）和转位（由EF-G催化）。",
        "tags": ["EF-Tu", "延伸因子", "氨酰-tRNA"]
    },
    {
        "id": 61, "topic": "延伸因子", "type": "choice",
        "question": "原核延伸因子EF-G在肽链延伸循环中的作用是？",
        "options": {"A": "携带氨酰-tRNA进入A位点", "B": "催化肽键形成", "C": "催化核糖体沿mRNA 5'→3'方向转位一个密码子", "D": "促使空载tRNA从E位点释放"},
        "answer": "C", "difficulty": 2,
        "explanation": "EF-G（转位酶）利用GTP水解能量催化转位：肽酰-tRNA从A→P位点，空载tRNA从P→E位点，mRNA相对于核糖体移动3个核苷酸（一个密码子）。A由EF-Tu完成，B由23S rRNA完成。",
        "tags": ["EF-G", "转位", "延伸因子"]
    },
    {
        "id": 62, "topic": "延伸因子", "type": "truefalse",
        "question": "EF-Ts是EF-Tu的GTP交换因子，负责将EF-Tu·GDP再生为EF-Tu·GTP，使EF-Tu能参与下一轮氨酰-tRNA的运输。",
        "answer": True, "difficulty": 3,
        "explanation": "EF-Tu·GDP需经EF-Ts催化GDP释放和GTP重新结合，再生为活性形式EF-Tu·GTP。这是EF-Tu循环的关键步骤：EF-Tu·GTP+氨酰-tRNA→进入A位点→GTP水解→EF-Tu·GDP释放→EF-Ts催化GDP/GTP交换→EF-Tu·GTP再生。",
        "tags": ["EF-Ts", "GTP交换因子", "EF-Tu循环"]
    },
    {
        "id": 63, "topic": "延伸因子", "type": "multi",
        "question": "关于原核肽链延伸过程中各因子的功能，正确的配对有？",
        "options": {"A": "EF-Tu——与GTP和氨酰-tRNA结合，将氨酰-tRNA运至A位点", "B": "EF-Ts——催化EF-Tu上GDP与GTP的交换", "C": "EF-G——催化核糖体沿mRNA 5'→3'的转位", "D": "23S rRNA肽酰转移酶——催化肽键形成", "E": "EF-Tu直接催化肽键形成"},
        "answer": "ABCD", "difficulty": 2,
        "explanation": "E错误——肽键形成由23S rRNA肽酰转移酶催化，EF-Tu仅负责氨酰-tRNA的运输。ABCD均为正确功能配对。",
        "tags": ["延伸因子", "EF-Tu", "EF-Ts", "EF-G"]
    },

    # ===== rRNA修饰与蛋白种类 (3题) =====
    {
        "id": 64, "topic": "核糖体蛋白", "type": "choice",
        "question": "原核生物（如E.coli）核糖体30S小亚基含有多少种不同的核糖体蛋白（S蛋白）？",
        "options": {"A": "约21种", "B": "约34种", "C": "约49种", "D": "约55种"},
        "answer": "A", "difficulty": 2,
        "explanation": "原核30S小亚基约含21种S蛋白（S1-S21），50S大亚基约含34种L蛋白（L1-L34）。真核40S小亚基约含33种蛋白，60S大亚基约含49种蛋白。这些数量差异也是原核/真核核糖体的结构特征之一。",
        "tags": ["核糖体蛋白", "S蛋白", "原核"]
    },
    {
        "id": 65, "topic": "核糖体蛋白", "type": "choice",
        "question": "真核细胞胞质核糖体60S大亚基约含有多少种核糖体蛋白？",
        "options": {"A": "约21种", "B": "约34种", "C": "约49种", "D": "约80种"},
        "answer": "C", "difficulty": 2,
        "explanation": "真核60S大亚基约含49种蛋白（部分教材记为46-47种），多于原核50S大亚基的约34种L蛋白，反映真核核糖体结构的复杂性更高。",
        "tags": ["核糖体蛋白", "60S大亚基", "真核"]
    },
    {
        "id": 66, "topic": "rRNA修饰", "type": "truefalse",
        "question": "真核细胞rRNA的核苷酸化学修饰（如2'-O-甲基化和假尿嘧啶化）的种类和数量均显著高于原核细胞rRNA。",
        "answer": True, "difficulty": 2,
        "explanation": "以酿酒酵母为例，约55个核苷酸发生2'-O-Me修饰、约45个发生假尿嘧啶化修饰；而E.coli 16S rRNA仅10个甲基化+1个假尿嘧啶化、23S rRNA约25个修饰核苷酸。真核rRNA修饰更丰富。",
        "tags": ["rRNA修饰", "2'-O-甲基化", "假尿嘧啶化"]
    }
]

qs.extend(new_qs)
print(f"After addition: {len(qs)} questions")

with open(path, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)
print("Saved questions.json")

# Also update terms.json
tpath = r'细胞生物学题库\第十章\terms.json'
terms = json.load(open(tpath, encoding='utf-8'))
new_terms = [
    {"id": 6, "term": "P位点（肽酰基位点，Peptidyl-tRNA Site）", "definition": "核糖体中与延伸中的肽酰-tRNA结合的位点，位于大小亚基结合面。肽键形成时P位点tRNA携带的多肽链转移到A位点氨酰-tRNA的氨基上，使肽链延长一个氨基酸残基。", "chapter": "第十章"},
    {"id": 7, "term": "E位点（出口位点，Exit Site）", "definition": "tRNA离开核糖体前的最后一个结合位点，位于大小亚基结合面。转位后空载tRNA从P位点移至E位点，然后从E位点释放到细胞质中。", "chapter": "第十章"},
    {"id": 8, "term": "肽酰转移酶（Peptidyl Transferase）", "definition": "催化肽键形成的酶活性中心，位于核糖体大亚基23S rRNA（原核）或28S rRNA（真核）上，由rRNA而非蛋白质构成，是核糖体为核酶的核心证据。", "chapter": "第十章"},
    {"id": 9, "term": "RNA世界假说（RNA World Hypothesis）", "definition": "20世纪80年代由W.Gilbert等人提出的生命起源假说，认为最早的生物大分子是RNA，兼具遗传信息储存和催化功能。DNA因更高的化学稳定性和修复能力取代RNA成为遗传载体，蛋白质因结构和功能多样性取代RNA成为主要催化剂。", "chapter": "第十章"},
    {"id": 10, "term": "起始因子（Initiation Factor, IF）", "definition": "协助核糖体小亚基、mRNA和起始tRNA正确组装形成翻译起始复合物的蛋白质因子。原核有IF1、IF2、IF3三种；真核需要十多种eIFs，其中eIF4F复合物负责识别mRNA 5'帽子结构。", "chapter": "第十章"},
    {"id": 11, "term": "EF-Tu（延伸因子Tu）", "definition": "原核生物肽链延伸的关键因子，与GTP和氨酰-tRNA形成三元复合物，将氨酰-tRNA运送至核糖体A位点。密码子配对正确后水解GTP并释放。其GDP/GTP交换由EF-Ts催化完成。", "chapter": "第十章"},
    {"id": 12, "term": "嘌呤霉素（Puromycin）", "definition": "一种结构与氨酰-tRNA 3'端（氨基酸-AMP）类似的抗生素，可进入核糖体A位点接受肽酰转移酶催化，使新生肽链提前终止释放。因其模拟tRNA末端被广泛用于核糖体功能研究。", "chapter": "第十章"},
    {"id": 13, "term": "扫描机制（Scanning Mechanism）", "definition": "真核细胞核糖体40S小亚基定位起始密码子的机制：eIF4F复合物识别mRNA 5'帽子结构后，40S亚基沿mRNA 5'→3'方向扫描，通常识别第一个位于合适Kozak序列上下文中的AUG作为翻译起始位点。", "chapter": "第十章"},
    {"id": 14, "term": "Kozak序列", "definition": "真核mRNA中位于起始密码子AUG周围的保守序列（最适序列为GCCGCC(A/G)CCAUGG），其存在可显著提高核糖体40S小亚基扫描过程中对AUG的识别效率和翻译起始频率。", "chapter": "第十章"},
    {"id": 15, "term": "释放因子（Release Factor, RF）", "definition": "识别核糖体A位点终止密码子（UAA、UAG、UGA）并催化蛋白质合成终止的蛋白质因子。原核RF1识别UAA/UAG，RF2识别UAA/UGA；真核eRF1识别全部三种终止密码子。", "chapter": "第十章"},
]
terms.extend(new_terms)
with open(tpath, 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=2)
print(f"Terms: {len(terms)} total")
print("Done!")
