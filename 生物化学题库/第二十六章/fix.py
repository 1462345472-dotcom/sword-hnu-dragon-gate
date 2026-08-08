# -*- coding: utf-8 -*-
"""补丁:补充4道truefalse覆盖缺失考点 + 修正terms"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

qs = json.load(open('生物化学题库/第二十六章/questions.json', encoding='utf-8'))
existing_topics = {q['topic'] for q in qs}

add = [
dict(type="truefalse",
 question="固氮酶对氧极为敏感,固氮过程必须在厌氧或低氧条件下进行,根瘤中豆血红蛋白结合O2可为固氮酶创造低氧环境。",
 options=None,
 answer="true",
 explanation="固氮酶(铁蛋白和钼铁蛋白)对氧极敏感,遇氧即不可逆失活;根瘤菌共生固氮时由豆血红蛋白结合并缓冲氧,既为呼吸供氧又保护固氮酶,维持低氧环境。",
 difficulty=2, tags=["固氮酶","氧敏感","豆血红蛋白"], topic="固氮的厌氧条件与氧敏感"),
dict(type="truefalse",
 question="固氮产物NH4+对固氮酶的活性有抑制作用,铵含量高时固氮作用会减弱。",
 answer="true",
 explanation="铵(NH4+)是固氮的产物,对固氮酶活性及nif固氮基因的表达均有抑制作用,因此铵充足时固氮菌停止固氮,这是固氮调控的重要机制。",
 difficulty=2, tags=["固氮调控","铵抑制","nif基因"], topic="固氮的调控"),
dict(type="truefalse",
 question="生物固氮是自然界氮循环的关键环节,农业生产中利用豆科作物轮作可减少氮肥施用。",
 answer="true",
 explanation="生物固氮将大气N2固定为NH3,是自然界氮素补充的主要途径,豆科植物与根瘤菌共生固氮可增加土壤氮素,农业上常利用豆科轮作、绿肥减少氮肥。",
 difficulty=1, tags=["固氮","氮循环","农业"], topic="固氮的生态学意义"),
dict(type="truefalse",
 question="谷氨酸是氨基转移反应中氨基的中心库,可将氨基转移给各种α-酮酸生成相应的氨基酸。",
 answer="true",
 explanation="谷氨酸通过转氨酶将氨基转移给丙酮酸、草酰乙酸等α-酮酸,生成丙氨酸、天冬氨酸等,是氨基的中心库,丙氨酸、天冬氨酸、谷氨酸与对应酮酸可逆互变维持平衡。",
 difficulty=1, tags=["谷氨酸","氨基中心库","转氨基"], topic="氨同化与谷氨酸代谢的中心地位"),
]

for q in add:
    if q['topic'] not in existing_topics:
        qs.append(q)
        existing_topics.add(q['topic'])
        print('新增:', q['topic'])

# 重排 id
for idx, q in enumerate(qs, 1):
    q['id'] = idx

with open('生物化学题库/第二十六章/questions.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=1)
print('总题量:', len(qs))

# ---- terms 修正 ----
terms = json.load(open('生物化学题库/第二十六章/terms.json', encoding='utf-8'))
for t in terms:
    if t['id'] == 16:
        t['term'] = 'S-腺苷甲硫氨酸(SAM)'
        t['name'] = 'S-腺苷甲硫氨酸(SAM)'
    if t['id'] == 6:
        t['definition'] = '动物体内不能合成或合成量不足、必须随膳食供给的氨基酸,人体共9种:苯丙氨酸、蛋氨酸、赖氨酸、苏氨酸、色氨酸、组氨酸、亮氨酸、异亮氨酸、缬氨酸。'
with open('生物化学题库/第二十六章/terms.json', 'w', encoding='utf-8') as f:
    json.dump(terms, f, ensure_ascii=False, indent=1)

# 校验 terms 字数与一致性
bad = [(t['id'], len(t['definition'])) for t in terms if not (30 <= len(t['definition']) <= 80)]
print('terms 字数违规:', bad if bad else '无')
print('term==name 全部一致:', all(t['term'] == t['name'] for t in terms))
