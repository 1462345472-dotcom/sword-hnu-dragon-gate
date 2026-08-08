# -*- coding: utf-8 -*-
"""第十章 terms: definition 压缩到 30-80 字 + 补 3 条 -> 18 条"""
import json

P = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第十章\terms.json'
with open(P, encoding='utf-8') as f:
    terms = json.load(f)

defs = {
 1: "由rRNA和核糖体蛋白组成的核糖核蛋白，是细胞内蛋白质合成的细胞器，原核70S（50S+30S），真核80S（60S+40S），肽酰转移酶中心由rRNA构成。",
 2: "由多个核糖体串联在同一条mRNA分子上同时进行肽链合成所形成的核糖体-mRNA聚合物，核糖体数量由mRNA长度决定，可提高多肽合成效率并经济有效地利用mRNA。",
 3: "核糖体上与新掺入的氨酰-tRNA结合的位点。延伸过程中，携带与mRNA密码子互补反密码子的氨酰-tRNA进入A位点，为肽键形成提供新的氨基酸。",
 4: "具有催化活性的RNA分子。Cech发现四膜虫26S前体rRNA自剪接，证明RNA具催化功能，核糖体肽酰转移酶由23S rRNA构成，是核酶的代表。",
 5: "原核mRNA起始密码子AUG上游5~10个核苷酸处的保守序列（5'-AGGAGG-3'），与16S rRNA 3'端互补配对，保证小亚基准确识别起始密码子。",
 6: "核糖体中与延伸中的肽酰-tRNA结合的位点。肽键形成时P位点tRNA上的多肽链转移到A位点氨酰-tRNA上，使肽链延长一个氨基酸残基。",
 7: "tRNA离开核糖体前的最后结合位点。转位后空载tRNA从P位点移至E位点，然后释放到细胞质中。",
 8: "催化肽键形成的酶活性中心，位于核糖体大亚基23S rRNA（原核）或28S rRNA（真核）上，由rRNA而非蛋白质构成，是核糖体为核酶的核心证据。",
 9: "20世纪80年代由W.Gilbert等人提出的生命起源假说：最早的生物大分子是RNA，兼具储存遗传信息和催化反应双重功能，DNA与蛋白质是后续演化的产物。",
 10: "协助核糖体小亚基、mRNA和起始tRNA组装形成起始复合物的蛋白质因子。原核有IF1、IF2、IF3三种；真核需十多种eIFs，eIF4F负责识别5'帽子。",
 11: "原核肽链延伸的关键因子，与GTP和氨酰-tRNA形成三元复合物将其运送至核糖体A位点，密码子配对正确后水解GTP并释放，其GDP/GTP交换由EF-Ts催化。",
 12: "结构与氨酰-tRNA 3'端类似的抗生素，可进入A位点接受肽酰转移酶催化，使新生肽链提前终止释放，因模拟tRNA末端而广泛用于核糖体功能研究。",
 13: "真核40S小亚基定位起始密码子的机制：eIF4F识别mRNA 5'帽子后，小亚基沿mRNA 5'→3'扫描，识别合适上下文中的AUG作为翻译起始位点。",
 14: "真核mRNA中位于起始密码子AUG周围的保守序列，可显著提高40S小亚基扫描过程中对AUG的识别效率和翻译起始频率。",
 15: "识别核糖体A位点终止密码子并催化翻译终止的蛋白质因子。原核RF1识别UAA/UAG，RF2识别UAA/UGA；真核eRF1识别全部三种终止密码子。",
}

assert set(defs) == {t['id'] for t in terms}, 'term id 集合不一致'
for t in terms:
    d = defs[t['id']]
    print('term %d 定义长度: %d' % (t['id'], len(d)))
    assert 30 <= len(d) <= 80, '定义长度越界: %s -> %d' % (t['id'], len(d))
    t['definition'] = d

# ---------- 补 3 条 ----------
extra = [
 {"id": 16, "term": "EF-G（延伸因子G）",
  "definition": "原核肽链延伸的转位因子，利用GTP水解能量催化核糖体沿mRNA 5'→3'方向移动一个密码子，使肽酰-tRNA从A位点移至P位点、空载tRNA移至E位点。",
  "chapter": "第十章"},
 {"id": 17, "term": "附着核糖体与游离核糖体",
  "definition": "附着核糖体附着于内质网膜表面或原核质膜内侧，参与糙面内质网上蛋白质的合成；游离核糖体分散于细胞质基质中，进行其他类型蛋白质的合成。",
  "chapter": "第十章"},
 {"id": 18, "term": "多顺反子mRNA（Polycistronic mRNA）",
  "definition": "含多个开放阅读框、可编码多种蛋白质的mRNA，是原核生物转录产物的典型特征；真核生物mRNA为单顺反子，只编码一种蛋白质。",
  "chapter": "第十章"},
]
for e in extra:
    assert 30 <= len(e['definition']) <= 80, '新术语长度越界: %s' % e['id']
    print('term %d 定义长度: %d' % (e['id'], len(e['definition'])))
terms.extend(extra)

with open(P, 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=1)
print('第十章 terms:', len(terms), '条')
