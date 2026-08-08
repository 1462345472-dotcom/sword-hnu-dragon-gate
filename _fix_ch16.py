# -*- coding: utf-8 -*-
"""第16章轻量核对:8处处理(7重出/1改判断题)"""
import json

PATH = '生物化学题库/第十六章/questions.json'
with open(PATH, encoding='utf-8') as f:
    qs = json.load(f)

def find(qid):
    for q in qs:
        if q['id'] == qid:
            return q
    raise KeyError(qid)

# ---------- Q44 重出: ATP→AMP+PPi 供能方式 ----------
q = find(44)
q.clear()
q.update({
    "topic": "ATP供能方式",
    "type": "choice",
    "question": "在脂肪酸活化、氨酰-tRNA合成等生物合成反应中,ATP常被水解为AMP和焦磷酸(PPi),随后PPi被焦磷酸酶水解为两分子无机磷酸。该供能方式的特点是?",
    "options": {
        "A": "使合成反应不可逆地向产物方向进行,释放的能量高于ATP仅水解为ADP",
        "B": "减少能量的释放,使反应更容易进行",
        "C": "释放的能量与ATP水解为ADP完全相同",
        "D": "抑制底物进入代谢途径"
    },
    "answer": "A",
    "explanation": "ATP→AMP+PPi断裂α-β磷酐键,释放约-45.6 kJ/mol的能量,高于ATP水解为ADP(-30.5 kJ/mol);PPi随后被无机焦磷酸酶水解为两分子Pi(约-19 kJ/mol),共同推动脂肪酸活化(生成脂酰-AMP)、氨酰-tRNA合成等反应不可逆地向产物方向进行,这是ATP以基团转移方式参与生物合成的典型供能形式。",
    "difficulty": 2,
    "tags": ["ATP", "AMP", "焦磷酸", "供能方式", "基团转移", "考纲37"],
    "id": 44
})

# ---------- Q68 重出: 铁硫蛋白功能 ----------
q = find(68)
q.clear()
q.update({
    "topic": "呼吸链复合体",
    "type": "choice",
    "question": "铁硫蛋白(Fe-S蛋白)在呼吸链中的主要作用是?",
    "options": {
        "A": "以铁原子Fe2+/Fe3+互变传递电子(单电子载体)",
        "B": "跨膜转运质子,建立质子梯度",
        "C": "结合并还原氧分子生成水",
        "D": "催化ADP磷酸化生成ATP"
    },
    "answer": "A",
    "explanation": "铁硫蛋白通过铁原子Fe2+/Fe3+的氧化还原互变传递电子,是呼吸链中的单电子载体,存在于复合体I、II、III中,与FMN、FAD、细胞色素等协同完成电子传递;它不是递氢体,不传递质子,也不直接参与氧的结合与ATP合成。",
    "difficulty": 2,
    "tags": ["铁硫蛋白", "Fe-S", "呼吸链组分", "递电子体", "考纲39"],
    "id": 68
})

# ---------- Q73 重出: E0' 电位数值排序 ----------
q = find(73)
q.clear()
q.update({
    "topic": "呼吸链排列顺序的实验依据",
    "type": "choice",
    "question": "呼吸链各组分的标准氧化还原电位(E0')由低到高排列,下列顺序正确的是?",
    "options": {
        "A": "NADH/NAD+(-0.32V)→CoQ(+0.045V)→Cyt c(+0.235V)→O2/H2O(+0.82V)",
        "B": "O2/H2O(+0.82V)→Cyt c(+0.235V)→CoQ(+0.045V)→NADH/NAD+(-0.32V)",
        "C": "Cyt c(+0.235V)→NADH/NAD+(-0.32V)→CoQ(+0.045V)→O2/H2O(+0.82V)",
        "D": "CoQ(+0.045V)→NADH/NAD+(-0.32V)→O2/H2O(+0.82V)→Cyt c(+0.235V)"
    },
    "answer": "A",
    "explanation": "呼吸链组分按E0'由低到高排列:NADH/NAD+约-0.32V、CoQ/CoQH2约+0.045V、Cyt c约+0.235V、O2/H2O约+0.82V;电子沿电位升高的方向传递,相邻组分间的电位差释放自由能,为质子泵与ATP合成提供能量。",
    "difficulty": 3,
    "tags": ["氧化还原电位", "E0'", "排列顺序", "数值", "考纲39"],
    "id": 73
})

# ---------- Q83 重出: 电位差与自由能释放 ----------
q = find(83)
q.clear()
q.update({
    "topic": "呼吸链排列顺序的实验依据",
    "type": "truefalse",
    "question": "呼吸链中相邻传递体之间的氧化还原电位差越大,电子传递时释放的自由能越多。",
    "answer": "true",
    "explanation": "电子传递释放的自由能由ΔG°'=-nFΔE°'决定,电位差越大,释放的自由能越多;NADH→CoQ、CoQ→Cyt c等电位差较大的环节足以偶联ATP合成,而复合体II(琥珀酸→CoQ)电位差太小,不足以偶联ATP生成。",
    "difficulty": 2,
    "tags": ["氧化还原电位", "电位差", "自由能", "考纲39"],
    "id": 83
})

# ---------- Q86 重出: 萎锈灵抑制复合体II ----------
q = find(86)
q.clear()
q.update({
    "topic": "电子传递抑制剂",
    "type": "choice",
    "question": "萎锈灵是呼吸链中哪一复合体的特异性抑制剂?",
    "options": {
        "A": "复合体II(琥珀酸-泛醌还原酶)",
        "B": "复合体I(NADH-泛醌还原酶)",
        "C": "复合体III(泛醌-细胞色素c还原酶)",
        "D": "复合体IV(细胞色素c氧化酶)"
    },
    "answer": "A",
    "explanation": "萎锈灵特异性抑制复合体II(琥珀酸-泛醌还原酶),阻断琥珀酸脱氢产生的电子向CoQ的传递,此时NADH的氧化不受影响;鱼藤酮、异戊巴比妥、杀粉蝶菌素抑制复合体I,抗霉素A抑制复合体III,CN-、CO、N3-、H2S抑制复合体IV。",
    "difficulty": 2,
    "tags": ["抑制剂", "萎锈灵", "复合体II", "考纲39"],
    "id": 86
})

# ---------- Q94 重出: 氧分子口径的ATP计算 ----------
q = find(94)
q.clear()
q.update({
    "topic": "P/O比值",
    "type": "choice",
    "question": "若以消耗1 mol氧分子(O2)计,NADH氧化呼吸链偶联合成的ATP数约为?",
    "options": {
        "A": "5",
        "B": "2.5",
        "C": "1.5",
        "D": "10"
    },
    "answer": "A",
    "explanation": "P/O比以每消耗1 mol氧原子计:NADH氧化链P/O≈2.5,琥珀酸(FADH2)链P/O≈1.5;1 mol O2含2 mol氧原子,故每消耗1 mol O2,NADH氧化链约合成2×2.5=5 mol ATP(FADH2链约为3)。注意区分\"氧原子\"与\"氧分子\"两种计数口径。",
    "difficulty": 2,
    "tags": ["P/O比", "氧分子", "ATP产量", "考纲38"],
    "id": 94
})

# ---------- Q112 改判断题: F0不催化ATP合成 ----------
q = find(112)
q.clear()
q.update({
    "topic": "F0F1-ATP合酶",
    "type": "truefalse",
    "question": "F0F1-ATP合酶的F0部分催化ADP与Pi生成ATP。",
    "answer": "false",
    "explanation": "F0是埋在线粒体内膜中的疏水部分,构成跨膜质子通道,让质子顺梯度回流;催化ADP+Pi→ATP的是伸向基质侧的亲水部分F1(ATP合酶的催化中心)。F0不具催化ATP合成的功能。",
    "difficulty": 2,
    "tags": ["ATP合酶", "F0", "质子通道", "考纲40"],
    "id": 112
})

# ---------- Q124 重出: 脂质体重组实验 ----------
q = find(124)
q.clear()
q.update({
    "topic": "化学渗透学说的实验证据",
    "type": "choice",
    "question": "将纯化的F0F1-ATP合酶与光驱动质子泵细菌视紫红质重组到脂质体上,光照后脂质体合成了ATP。该实验表明?",
    "options": {
        "A": "质子电化学梯度(质子动力势)足以驱动ATP合酶合成ATP",
        "B": "ATP合酶合成ATP不需要能量",
        "C": "光照本身直接提供合成ATP所需的磷酸基团",
        "D": "脂质体可以替代线粒体内膜进行电子传递"
    },
    "answer": "A",
    "explanation": "重组脂质体实验是支持化学渗透学说的重要证据:细菌视紫红质受光驱动将H+泵出,形成跨膜质子梯度,质子顺梯度经F0F1-ATP合酶回流即驱动ATP合成,证明质子电化学梯度是电子传递与ATP合成之间的偶联桥梁,而非两者的直接接触。",
    "difficulty": 3,
    "tags": ["化学渗透学说", "实验证据", "脂质体", "细菌视紫红质", "考纲40"],
    "id": 124
})

# 写回,保持格式
with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)
    f.write('\n')

print('OK, 8 处处理完成')
