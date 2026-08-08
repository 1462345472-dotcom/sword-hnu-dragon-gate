# -*- coding: utf-8 -*-
"""第一章绪论补题 批次2: truefalse 20题 (ID 145-164)"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第一章绪论'
qp = BASE + r'\questions.json'

new = [
{"id":145,"type":"truefalse","question":"罗伯特·胡克1665年用显微镜观察软木薄片时看到的是死亡组织残留的细胞壁，而非活细胞。","answer":"true","explanation":"胡克观察到的是软木（栓皮）薄片中死亡细胞残留的细胞壁和空腔，并非活细胞。真正观察到活细胞的是列文虎克。","difficulty":1,"tags":["细胞发现史","胡克"]},
{"id":146,"type":"truefalse","question":"列文虎克是第一个观察到活细胞的科学家。","answer":"true","explanation":"列文虎克1674年观察鱼的红细胞时描述了细胞核结构，并观察了活体动物及细菌，是真正的活细胞发现者。","difficulty":1,"tags":["细胞发现史","列文虎克"]},
{"id":147,"type":"truefalse","question":"施莱登1838年发表《植物发生论》，施旺1839年发表《关于动植物的结构和生长的一致性的显微研究》，共同奠定了细胞学说的基础。","answer":"true","explanation":"施莱登（1838，植物方面）和施旺（1839，动物方面）的著作分别从植物和动物两个角度论证了细胞是生物体的基本结构单位，共同奠定细胞学说基础。","difficulty":2,"tags":["细胞学说","施莱登","施旺","著作"]},
{"id":148,"type":"truefalse","question":"下村脩、查尔菲和钱永健因发现和改造绿色荧光蛋白（GFP）获得2008年诺贝尔化学奖。","answer":"true","explanation":"2008年诺贝尔化学奖授予下村脩（发现GFP）、马丁·查尔菲（将GFP用于标记生物体）和钱永健（改造GFP产生多种荧光变体）。","difficulty":2,"tags":["诺贝尔奖","GFP"]},
{"id":149,"type":"truefalse","question":"大隅良典因发现细胞自噬的分子机制获得2016年诺贝尔生理学或医学奖。","answer":"true","explanation":"大隅良典以酿酒酵母为模型，通过基因筛选阐明了细胞自噬的分子机制（Atg基因等），获2016年诺贝尔生理学或医学奖。","difficulty":2,"tags":["诺贝尔奖","自噬","大隅良典"]},
{"id":150,"type":"truefalse","question":"山中伸弥和格登因发现成熟细胞可以被重编程为多能干细胞（iPSC）获得2012年诺贝尔生理学或医学奖。","answer":"true","explanation":"2012年诺奖授予格登（核移植重编程）与山中伸弥（iPSC诱导），表彰其发现成熟细胞可被重编程为多能性状态，为再生医学奠定基础。","difficulty":2,"tags":["诺贝尔奖","iPSC","重编程"]},
{"id":151,"type":"truefalse","question":"超分辨荧光显微技术（STED、PALM等）因突破光学显微镜衍射极限获得2014年诺贝尔化学奖。","answer":"true","explanation":"2014年诺贝尔化学奖授予赫尔（STED）、贝齐格和莫纳尔（PALM/STORM），表彰他们开发超分辨荧光显微技术，突破约200nm的阿贝衍射极限。","difficulty":2,"tags":["诺贝尔奖","超分辨"]},
{"id":152,"type":"truefalse","question":"哈特韦尔、亨特和纳斯因发现细胞周期调控机制（周期蛋白与CDK）获得2001年诺贝尔生理学或医学奖。","answer":"true","explanation":"三位科学家以酵母为模型发现细胞周期蛋白（cyclin）和周期蛋白依赖性激酶（CDK），揭示细胞周期运转的分子机制，获2001年诺奖。","difficulty":2,"tags":["诺贝尔奖","细胞周期","CDK"]},
{"id":153,"type":"truefalse","question":"RNA干扰现象（RNAi）由法尔和梅洛在线虫中发现，因此获得2006年诺贝尔生理学或医学奖。","answer":"true","explanation":"法尔和梅洛于1998年在线虫中发现双链RNA介导的基因沉默现象（RNAi），这一发现推动了基因功能研究方法的革命，获2006年诺奖。","difficulty":2,"tags":["诺贝尔奖","RNAi"]},
{"id":154,"type":"truefalse","question":"细菌的DNA分布在由核膜包裹的细胞核中。","answer":"false","explanation":"细菌（原核细胞）没有核膜包裹的典型细胞核，其环状DNA集中于细胞质中的核区（拟核），与细胞质之间无膜界限。","difficulty":1,"tags":["原核细胞","核区"]},
{"id":155,"type":"truefalse","question":"细菌以二分裂方式增殖，一个细菌分裂产生两个子细胞。","answer":"true","explanation":"细菌等原核细胞以二分裂方式增殖：DNA复制后细胞中部内陷，一分为二，遗传物质平均分配到两个子细胞。","difficulty":1,"tags":["原核细胞","二分裂"]},
{"id":156,"type":"truefalse","question":"鞭毛是细菌的运动器官，其结构基础与真核细胞的鞭毛完全相同。","answer":"false","explanation":"细菌鞭毛由鞭毛蛋白螺旋装配而成，通过旋转运动推进细菌；真核细胞鞭毛（如精子鞭毛）由微管以9+2排列构成，二者结构基础完全不同。","difficulty":2,"tags":["原核细胞","鞭毛"]},
{"id":157,"type":"truefalse","question":"所有病毒都具有由脂双层构成的包膜。","answer":"false","explanation":"只有部分病毒（包膜病毒，如流感病毒、HIV）具有来源于宿主细胞膜的脂双层包膜；无包膜病毒（如T4噬菌体、腺病毒）只有蛋白质衣壳。","difficulty":1,"tags":["病毒","包膜"]},
{"id":158,"type":"truefalse","question":"噬菌体（如T4噬菌体）是专门感染细菌的病毒。","answer":"true","explanation":"噬菌体是感染细菌等原核生物的病毒。T4噬菌体通过尾部将DNA注入大肠杆菌，利用宿主细胞机制复制增殖，是研究病毒增殖的经典模型。","difficulty":1,"tags":["病毒","噬菌体"]},
{"id":159,"type":"truefalse","question":"反转录病毒（如HIV）以自身RNA为模板反转录合成DNA，再整合进宿主基因组。","answer":"true","explanation":"反转录病毒（retrovirus）携带反转录酶，以RNA为模板反转录出双链DNA，并整合到宿主细胞基因组中长期存在，随宿主DNA复制而传递。","difficulty":2,"tags":["病毒","反转录病毒","HIV"]},
{"id":160,"type":"truefalse","question":"病毒衣壳由蛋白质亚基（壳粒）组装而成，包裹并保护病毒核酸。","answer":"true","explanation":"衣壳是病毒的蛋白质外壳，由多个蛋白亚基（壳粒）按对称规则组装而成，包裹核酸，保护病毒基因组并参与识别宿主细胞。","difficulty":1,"tags":["病毒","衣壳"]},
{"id":161,"type":"truefalse","question":"细胞内含量最多的有机化合物是核酸。","answer":"false","explanation":"蛋白质约占细胞干重的一半以上，是含量最多的有机化合物；核酸（DNA和RNA）总量低于蛋白质。","difficulty":1,"tags":["化学组成","蛋白质"]},
{"id":162,"type":"truefalse","question":"细胞骨架是动态结构，能够不断装配和解聚，参与细胞运动与分裂。","answer":"true","explanation":"细胞骨架（微丝、微管、中间纤维）是高度动态的结构，通过亚基的聚合与解聚发生重构，从而驱动细胞运动、细胞质分裂、物质运输和细胞形态改变。","difficulty":2,"tags":["细胞骨架","动态性"]},
{"id":163,"type":"truefalse","question":"所有真核细胞都具有细胞壁。","answer":"false","explanation":"只有植物细胞（及真菌、某些原生生物）具有细胞壁，动物细胞没有细胞壁，只有细胞质膜。因此细胞壁不是真核细胞的共有特征。","difficulty":1,"tags":["真核细胞","细胞壁"]},
{"id":164,"type":"truefalse","question":"生物大分子（核酸、蛋白质、多糖、脂类）均由相同的基本结构单元构成，体现了细胞化学组成的统一性。","answer":"true","explanation":"核酸由核苷酸、蛋白质由氨基酸、多糖由单糖、脂类由脂肪酸等基本单元构成，所有细胞共用相同的结构单元，这是细胞统一性的化学基础。","difficulty":1,"tags":["化学组成","生物大分子","统一性"]},
]

qs = json.load(open(qp, encoding='utf-8'))
ids = {q['id'] for q in qs}
assert not (ids & {n['id'] for n in new}), 'ID冲突!'
qs.extend(new)
json.dump(qs, open(qp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('批次2完成: 新增', len(new), '题, 当前总数', len(qs))
