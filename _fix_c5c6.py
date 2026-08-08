# -*- coding: utf-8 -*-
"""第五章+第六章 重审修正脚本:
1) 知识/格式修正(questions.json)
2) 补全 topic(两章)与 tags(第六章)
3) terms.json 名解裁剪至 30-80 字
"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库'


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def dump(p, obj):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print('saved:', p)


def infer_topic5(tags, question):
    """按 tags/题干推断第五章 topic。"""
    q = question
    if any(k in tags for k in ['过氧化物酶体']):
        return '过氧化物酶体'
    if any(k in q for k in ['PTS1', 'PTS2']):
        return '过氧化物酶体'
    if any(k in tags for k in ['糖基化', 'O-连接', 'N-连接']):
        return '糖基化'
    if any(k in tags for k in ['细胞质基质']):
        return '细胞质基质'
    if any(k in tags for k in ['泛素', '蛋白酶体', '蛋白质降解']):
        return '泛素化'
    if any(k in tags for k in ['内质网', 'rER', 'sER', '肌质网', '微粒体', 'ERS', '内质网应激', '蛋白折叠', 'PDI', 'BiP', '跨膜蛋白', '蛋白修饰']):
        return '内质网'
    if any(k in tags for k in ['高尔基体', 'TGN', '分泌途径']):
        return '高尔基体'
    if any(k in tags for k in ['溶酶体', '贮积症', '自噬', 'M6P', '信号斑', 'I细胞病', '硅肺', '疾病']):
        return '溶酶体'
    if any(k in tags for k in ['细胞内膜系统']):
        return '细胞内膜系统'
    if any(k in tags for k in ['细胞骨架']):
        return '细胞骨架'
    return '细胞内膜系统'


def infer_topic6(tags, question):
    q = question
    if any(k in tags for k in ['信号肽', 'SRP', '共翻译']):
        return '共翻译转运'
    if any(k in q for k in ['信号肽', 'SRP', '停靠蛋白', '移位子', '信号假说', '信号锚定', '停止转移', '跨膜']):
        return '共翻译转运'
    if any(k in q for k in ['线粒体', '叶绿体', '导肽', 'Tom', 'Tim', 'Oxi', '类囊体', '转运肽']):
        return '翻译后转运'
    if any(k in tags for k in ['翻译后转运']):
        return '翻译后转运'
    if any(k in q for k in ['COPII', 'COPI', '网格蛋白', '发动蛋白', 'ARF', 'Sar1', 'Sec', 'KDEL', 'KKXX', '逃逸', '接头蛋白']):
        return '膜泡运输'
    if any(k in q for k in ['Rab', 'SNARE', 'v-SNARE', 't-SNARE', '融合', '锚定']):
        return '膜泡运输'
    if any(k in q for k in ['膜泡运输', '分选', '转运']):
        return '蛋白质分选'
    return '蛋白质分选'


def fix_ch5():
    p = f'{BASE}\\第五章\\questions.json'
    qs = load(p)
    fixes = 0
    for q in qs:
        i = q['id']
        # Q65 选项笔误 KDE L -> KDEL
        if i == 65:
            for k, v in q['options'].items():
                if 'KDE' in v and 'L' in v.replace('KDE', ''):
                    q['options'][k] = v.replace('KDE L', 'KDEL')
                    fixes += 1
        # 明确修正 topic(个别错误标注)
        if i == 69:
            q['topic'] = '过氧化物酶体'
        if i in (87, 94, 114):
            q['topic'] = '糖基化'
        # 全题补 topic
        if 'topic' not in q or not q['topic']:
            q['topic'] = infer_topic5(q.get('tags', []), q['question'])
    dump(p, qs)
    print('第五章修正项:', fixes, '| 题目总数:', len(qs))


def fix_ch6():
    p = f'{BASE}\\第六章\\questions.json'
    qs = load(p)
    for q in qs:
        i = q['id']
        # Q74 知识错误: 原核细胞同样存在蛋白质定向转运 -> false
        if i == 74:
            q['answer'] = 'false'
            q['explanation'] = ('原核细胞同样存在蛋白质的定向转运（如分泌蛋白经Sec途径跨膜转运），'
                                '该说法错误。蛋白质分选并非真核细胞特有，本章讨论的主要是真核细胞核基因编码蛋白质的分选。')
        # Q79 信号肽酶位置: 位于内质网腔面(非胞质面)
        if i == 79:
            q['explanation'] = ('信号肽酶定位在内质网膜腔面，切除信号肽后立即将其降解；'
                                '信号肽切除发生在内质网腔侧而非胞质侧。')
        # Q17 题干明确为腔面
        if i == 17:
            q['options']['B'] = '内质网腔面'
            q['explanation'] = '内质网腔面的信号肽酶切除信号肽并将其快速降解，信号肽不会进入内质网腔。'
        # Q105 题干修正: Dynamin 不属于"小分子"GTP结合蛋白,但具有 GTP 酶活性
        if i == 105:
            q['question'] = '以下哪些蛋白具有GTP酶活性（属于GTP酶超家族成员）？'
        # 全题补 tags 与 topic
        tags = q.get('tags', [])
        if not tags:
            t = infer_topic6([], q['question'])
            tags = [t, '蛋白质分选'] if t != '蛋白质分选' else ['蛋白质分选', '转运机制']
            q['tags'] = tags
        q['topic'] = infer_topic6(q.get('tags', []), q['question'])
    dump(p, qs)
    print('第六章题目总数:', len(qs))


def trim_terms(ch, term_fixes):
    """term_fixes: {term: 新定义} 裁剪超80字名解。"""
    p = f'{BASE}\\{ch}\\terms.json'
    ts = load(p)
    for t in ts:
        name = t['term']
        if name in term_fixes:
            t['definition'] = term_fixes[name]
    dump(p, ts)
    # 校验长度
    bad = [(t['term'], len(t['definition'])) for t in ts if not (30 <= len(t['definition']) <= 80)]
    print(f'{ch} 裁剪后超界:', bad if bad else '无')


F5 = {
 '分子伴侣': '一类协助其他蛋白质正确折叠、组装和分选的辅助蛋白质，不参与最终功能状态，通过暂时与多肽链结合防止错误折叠或聚集，典型代表为热激蛋白（Hsp70、Hsp60）。',
 '热激蛋白（Hsp）': '常作为分子伴侣协助蛋白质合成、分选、折叠与装配的高度保守蛋白质家族，按分子量分为Hsp100、Hsp90、Hsp70、Hsp60等，胁迫条件下可上调以维持细胞稳态。',
 '内质网应激（ERS）': '内质网功能紊乱、钙稳态失衡及未折叠/错误折叠蛋白过量积累时激活的保护性信号通路，涉及UPR、EOR、固醇调节级联反应和凋亡程序。',
 '细胞自噬': '自噬相关基因（Atg）调控下对细胞内受损或需淘汰的蛋白质和细胞器进行再利用的过程，底物被双层膜包裹形成自噬小泡并与溶酶体融合降解。',
 'M6P（甘露糖-6-磷酸）': '溶酶体酶的分选信号，在高尔基体顺面膜囊和中间膜囊中由磷酸转移酶和磷酸葡糖苷酶先后催化形成于甘露糖残基上，介导溶酶体酶靶向转运至溶酶体。',
 '溶酶体贮积症': '因遗传缺陷导致溶酶体中水解酶缺失或分选信号异常，相应底物无法降解而在溶酶体内累积所引发的一类代谢性疾病，如泰-萨克斯病、I细胞病。',
 '过氧化物酶体': '由单层膜围绕、内含氧化酶和过氧化氢酶的异质性细胞器（又称微体），功能为氧化解毒、分解H2O2保护细胞、分解脂肪酸提供热能。',
}
F6 = {
 '共翻译转运途径': '一种边合成边转运的蛋白质分选方式。在游离核糖体上起始合成后，由信号肽-SRP引导至糙面内质网，新生肽边合成边进入内质网腔或定位在ER膜上。',
 '翻译后转运途径': '一种合成后转运的蛋白质分选方式。在细胞质基质游离核糖体上完成多肽链合成，然后在导肽等信号序列指引下转运至线粒体、叶绿体、过氧化物酶体及细胞核。',
 '信号肽（Signal Peptide）': '位于分泌蛋白和膜蛋白N端的短信号序列，由约16~26个氨基酸残基组成，中部含疏水核心区，被SRP识别并结合，引导核糖体-新生肽复合物靶向内质网膜，后被信号肽酶切除。',
 '信号识别颗粒（SRP）': '胞质核糖核蛋白复合体，由6种蛋白质和1个7S RNA组成。识别并结合新生肽N端信号肽及核糖体，暂停肽链延伸，引导核糖体-新生肽复合物至内质网膜SRP受体。',
 'SRP受体（停靠蛋白，DP）': '内质网膜上的整合蛋白，由α和β亚基组成。与SRP结合后将核糖体-新生肽复合物锚定至内质网膜，是共翻译转运的锚定装置。',
 '信号假说（Signal Hypothesis）': 'Blobel和Sabatini提出的假说，认为分泌蛋白N端携带短信号序列，翻译后与相关因子结合，指导核糖体转移至内质网膜并继续翻译，解释了共翻译转运的分子机制。',
 '导肽（Targeting Sequence/Presequence）': '翻译后转运途径中指导蛋白质靶向特定细胞器的信号序列的统称，包括线粒体N端导肽、叶绿体转运肽、过氧化物酶体C端内在靶向序列（如SKL）等，转运后被切除。',
 '信号斑（Signal Patch）': '由蛋白质三维折叠后形成的空间构象型分选信号，由不同区域多段氨基酸序列在空间上聚集而成，依赖三维折叠构象被识别，如溶酶体酶的分选信号。',
 '分子伴侣（Molecular Chaperone）': '一类协助其他蛋白质正确折叠、组装和转运的蛋白质。Hsp70与前体蛋白结合维持其非折叠状态以便跨膜转运，Hsp60协助已进入细胞器的蛋白质折叠为活性构象。',
 '膜泡运输（Vesicular Transport）': '真核细胞内膜系统细胞器表面出芽形成转运囊泡，沿细胞骨架运输至目的地后与靶膜融合的过程，包括COPII、COPI和网格蛋白包被膜泡三种类型。',
 'COPII包被膜泡': '介导内质网到高尔基体顺向运输的包被膜泡，包被组分包括Sar1、Sec23/Sec24、Sec13/Sec31和Sec16，Sar1-GTP启动装配，Sec13/Sec31形成骨架。',
 'COPI包被膜泡': '介导高尔基体到内质网逆向运输的包被膜泡，含7种蛋白亚基和GTP结合蛋白ARF，通过KDEL和KKXX回收信号回收内质网驻留蛋白，是COPII转运的纠错机制。',
 'KDEL信号序列': '内质网可溶性驻留蛋白C端的回收信号，由赖氨酸-天冬氨酸-谷氨酸-亮氨酸组成，被高尔基体TGN区的KDEL受体识别后经COPI膜泡逆向回收至内质网。',
 '网格蛋白/接头蛋白包被膜泡': '双层结构的包被膜泡：外层为三腿结构网格蛋白，内层为接头蛋白复合物（AP1/AP2/AP3），介导TGN分泌泡和受体介导内吞泡形成，断裂依赖发动蛋白GTP酶。',
 '发动蛋白（Dynamin）': '介导网格蛋白包被膜泡从供体膜断裂的关键蛋白，具有GTP酶活性，围绕膜泡颈部聚合，通过水解GTP驱动构象改变导致膜泡断裂释放。',
 'Rab蛋白': '小分子GTP结合蛋白，属GTP酶超家族。GEF催化Rab-GDP转换为Rab-GTP后，通过类异戊二烯基团插入膜泡膜，与靶膜Rab效应器结合完成膜泡锚定。',
 'SNARE蛋白（v-SNARE/t-SNARE）': '介导转运膜泡与靶膜融合的跨膜蛋白对。v-SNARE位于膜泡上，t-SNARE位于靶膜上，二者特异性配对形成四螺旋束复合体驱动膜融合，融合后需ATP解离。',
 '停靠蛋白（Docking Protein，DP）': '即SRP受体，内质网膜上的整合蛋白，由α和β亚基组成，与SRP结合后将核糖体-新生肽复合物锚定至内质网膜，是共翻译转运的关键桥梁蛋白。',
 '逃逸蛋白（Escaped Protein）': '本应在特定细胞器驻留但被错误包装进入转运膜泡的蛋白质，如内质网驻留蛋白偶被COPII膜泡运至高尔基体，细胞经COPI膜泡回收机制（KDEL/KKXX）将其返回。',
}

if __name__ == '__main__':
    fix_ch5()
    fix_ch6()
    trim_terms('第五章', F5)
    trim_terms('第六章', F6)
    print('done')
