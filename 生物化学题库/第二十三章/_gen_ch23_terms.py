# -*- coding: utf-8 -*-
"""第二十三章 光合作用 名词解释 terms.json (17个, 30-80字)"""
import json, os

TERMS = [
{"id":1,"term":"光合作用","name":"光合作用","definition":"含光合色素(主要是叶绿素)的植物细胞和细菌吸收太阳光能,将CO2和H2O合成有机物质并释放氧气或其他物质的过程,是地球上有机物与能量的最主要来源。","chapter":"biochem_23"},
{"id":2,"term":"光反应","name":"光反应","definition":"光合作用中发生在叶绿体类囊体膜(原核为质膜结合颗粒)上的反应,通过光合磷酸化产生NADPH和ATP,并伴随水的光解释放O2,为暗反应提供同化力。","chapter":"biochem_23"},
{"id":3,"term":"暗反应","name":"暗反应","definition":"光合作用中发生在叶绿体基质(原核为细胞质)的反应,利用光反应产生的ATP和NADPH将CO2还原为糖,即卡尔文循环;虽不直接需光但依赖光反应产物。","chapter":"biochem_23"},
{"id":4,"term":"光合色素","name":"光合色素","definition":"植物细胞和光合细菌中能吸收并转化光能的色素,主要是叶绿素(叶绿素a、b),还包括类胡萝卜素等辅助色素,后者可扩大光吸收范围并保护叶绿素。","chapter":"biochem_23"},
{"id":5,"term":"光反应中心","name":"光反应中心","definition":"光合系统中含1对特殊叶绿素a的部位,受光能激发后发生电荷分离,产生强电子供体和强电子受体;植物有两类串联的光反应中心P700和P680。","chapter":"biochem_23"},
{"id":6,"term":"光合系统(光系统)","name":"光合系统(光系统)","definition":"类囊体膜上执行光能吸收与转化的功能单位,由天线系统(数百个叶绿素和辅助色素)、含1对特殊叶绿素a的光反应中心和相关电子传递体系组成。","chapter":"biochem_23"},
{"id":7,"term":"光合磷酸化","name":"光合磷酸化","definition":"被生物的光系统捕获的光能中有一部分能量转化为ATP的磷酸键能,这种光驱动的ATP合成过程称为光合磷酸化,其机理遵循化学渗透假说。","chapter":"biochem_23"},
{"id":8,"term":"非环式光合磷酸化","name":"非环式光合磷酸化","definition":"光合电子经PSII和PSI线性传递的磷酸化过程:电子从水的光解出发,经P680、质体醌、细胞色素b6f、质体蓝素到P700,最终还原NADP+生成NADPH,同时合成ATP并释放O2。","chapter":"biochem_23"},
{"id":9,"term":"循环光合磷酸化","name":"循环光合磷酸化","definition":"P700失去的电子借助细胞色素b6f复合物重新回到P700的磷酸化过程,只合成ATP而不生成NADPH,不涉及水的光解和放氧。","chapter":"biochem_23"},
{"id":10,"term":"假循环光合磷酸化","name":"假循环光合磷酸化","definition":"电子经光系统传递后最终以O2为受体的磷酸化过程,不生成NADPH,可产生超氧自由基;见于铁氧还蛋白过量还原等条件,是一种耗散电子与能量的方式。","chapter":"biochem_23"},
{"id":11,"term":"同化力","name":"同化力","definition":"光反应产生的ATP和NADPH的合称,是暗反应(卡尔文循环)将CO2还原为糖类所需的能量和还原力的来源,又称同化能力。","chapter":"biochem_23"},
{"id":12,"term":"卡尔文循环","name":"卡尔文循环","definition":"利用光反应形成的同化力将CO2还原形成糖类的过程,最初产物为3-磷酸甘油酸,故称C3途径;包括CO2固定、3-磷酸甘油酸还原、RuBP再生三个阶段,是碳同化的基本途径。","chapter":"biochem_23"},
{"id":13,"term":"Rubisco","name":"Rubisco","definition":"核酮糖-1,5-二磷酸羧化酶,催化CO2固定阶段RuBP与CO2结合生成2分子3-磷酸甘油酸;为双功能酶,亦可催化RuBP加氧启动光呼吸,是植物体内含量最丰富的蛋白质。","chapter":"biochem_23"},
{"id":14,"term":"C4途径","name":"C4途径","definition":"C4植物中CO2先在叶肉细胞与PEP结合被固定为草酰乙酸,再还原为苹果酸转运到维管束鞘细胞脱羧释放CO2供卡尔文循环的固定方式,具浓缩CO2、抑制光呼吸的作用。","chapter":"biochem_23"},
{"id":15,"term":"PEP羧化酶","name":"PEP羧化酶","definition":"催化CO2与磷酸烯醇式丙酮酸(PEP)结合生成草酰乙酸的酶,存在于C4植物叶肉细胞和CAM植物细胞质中,对CO2亲和力高且不受O2抑制。","chapter":"biochem_23"},
{"id":16,"term":"光呼吸","name":"光呼吸","definition":"光下Rubisco加氧使RuBP与O2结合,生成磷酸乙醇酸并经乙醇酸途径(叶绿体、过氧化物酶体、线粒体协同)释放CO2的过程,又称C2循环,消耗O2、释放CO2且不产生ATP。","chapter":"biochem_23"},
{"id":17,"term":"CAM途径","name":"CAM途径","definition":"景天酸代谢:景天科等植物夜间气孔开放,由PEP羧化酶固定CO2生成苹果酸贮于液泡,白天气孔关闭,苹果酸脱羧释放CO2供卡尔文循环,以适应干旱环境的碳固定方式。","chapter":"biochem_23"},
]

BASE = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(BASE, 'terms.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(TERMS, f, ensure_ascii=False, indent=1)
# 自检名解字数
for t in TERMS:
    n = len(t['definition'])
    flag = 'OK' if 30 <= n <= 80 else '!!!超出范围'
    print('%d %s %d字 %s' % (t['id'], t['term'], n, flag))
print('terms.json 已写入 %d 个' % len(TERMS))
