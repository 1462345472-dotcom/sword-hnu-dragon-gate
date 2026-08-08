# -*- coding: utf-8 -*-
"""第十章处理: id重排/统一topic/补3题"""
import json, collections

BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第十章'
QP = BASE + r'\questions.json'

with open(QP, encoding='utf-8') as f:
    qs = json.load(f)

# ---------- 1. 统一 topic 为 851 考纲条目简称 ----------
T_STRUCT = '核糖体结构'          # 考纲: 核糖体的类型与结构
T_SYNTH = '核糖体与蛋白质合成'   # 考纲: 核糖体与蛋白质合成

map_topic = {}
# 结构类: 沉降系数/亚基/组成/位点结构/蛋白数量/rRNA修饰/共同特征/比较
for i in [1,2,3,4,5,7,8,9,10,19,25,27,28,29,32,33,64,65,66]:
    map_topic[i] = T_STRUCT
# 合成类: 翻译各阶段/因子/多核糖体/核酶/RNA世界/抗生素/系统差异
for i in [6,11,13,14,15,16,17,18,22,23,24,26,30,31,34,35,36,37,
          38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63]:
    map_topic[i] = T_SYNTH
assert set(map_topic) == {q['id'] for q in qs}, 'topic映射与题目集合不一致'

for q in qs:
    q['topic'] = map_topic[q['id']]

# ---------- 2. 补 3 题(课件依据: 核糖体蛋白功能/数量变化/EDTA尿素分离) ----------
new_questions = [
{
 "topic": T_STRUCT, "type": "choice",
 "question": "关于核糖体蛋白质功能的描述，正确的是？",
 "options": {
  "A": "核糖体蛋白构成核糖体的核心，决定核糖体形态",
  "B": "核糖体蛋白对rRNA折叠成有功能的三维结构十分重要，并在翻译中对核糖体空间构象进行\"微调\"",
  "C": "核糖体蛋白催化肽键形成",
  "D": "核糖体蛋白缺失或突变对核糖体功能无影响"
 },
 "answer": "B",
 "difficulty": 2,
 "explanation": "rRNA构成核糖体核心、决定形态并催化肽键形成（A、C错）。核糖体蛋白分布于核糖体表面或填充于rRNA缝隙：对rRNA折叠成有功能的三维结构十分重要，并在翻译过程中对核糖体空间构象进行\"微调\"以保证翻译顺利进行，缺失或突变会降低多肽合成活性（D错）。",
 "tags": ["核糖体蛋白", "rRNA折叠", "核糖体功能"]
},
{
 "topic": T_STRUCT, "type": "truefalse",
 "question": "核糖体的数量与细胞蛋白质合成的需求直接相关：快速生长的细菌细胞中每个细胞可能含有数万个核糖体，而饥饿状态下的细胞中核糖体数量显著减少。",
 "answer": "true",
 "difficulty": 1,
 "explanation": "核糖体数量随蛋白质合成需求变化：快速生长的细菌含数万个核糖体，饥饿时显著减少；即使最小的细胞如支原体也含有数百个核糖体。这体现了核糖体作为蛋白质合成机器的适应性调节。",
 "tags": ["核糖体数量", "蛋白质合成需求"]
},
{
 "topic": T_STRUCT, "type": "truefalse",
 "question": "核糖体由rRNA和蛋白质组成，可用EDTA、尿素等试剂将二者分离。",
 "answer": "true",
 "difficulty": 2,
 "explanation": "EDTA和尿素可破坏核糖体蛋白与rRNA之间的相互作用，使两者分离，这是研究核糖体化学组成和结构重建的经典方法。此外，Mg2+浓度也影响亚基聚合状态：低Mg2+促使解离，高Mg2+促使形成二聚体。",
 "tags": ["rRNA分离", "EDTA", "化学组成"]
},
]

qs.extend(new_questions)

# ---------- 3. 重排 id ----------
qs = sorted(qs, key=lambda q: q.get('id', 10 ** 9))
for new_id, q in enumerate(qs, start=1):
    q['id'] = new_id

with open(QP, 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)

print('第十章处理后总题数:', len(qs))
print('题型分布:', dict(collections.Counter(q['type'] for q in qs)))
print('topic分布:', dict(collections.Counter(q['topic'] for q in qs)))
print('id连续:', [q['id'] for q in qs] == list(range(1, len(qs) + 1)))
