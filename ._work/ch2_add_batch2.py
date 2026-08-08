# -*- coding: utf-8 -*-
"""第二章补题 批次2: truefalse 24题 (ID 135-158)"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = r'C:\Users\Lenovo\Desktop\湖南大学\细胞生物学题库\第二章'
qp = BASE + r'\questions.json'

new = [
{"id":135,"type":"truefalse","question":"暗视野显微镜适合观察未经染色的活细胞中的微小颗粒。","answer":"true","explanation":"暗视野显微镜在暗背景中通过样品颗粒的散射光成像，无需染色即可观察活细胞中的微小颗粒及其运动（如螺旋体、细胞器），但只显示颗粒轮廓，不能分辨内部结构。","difficulty":2,"tags":["暗视野显微镜","活细胞"]},
{"id":136,"type":"truefalse","question":"偏振光显微镜可用来观察具有双折射特性的结构，如肌动蛋白丝和微管。","answer":"true","explanation":"偏振光显微镜利用偏振光检测样品的各向异性（双折射）特性，细胞骨架纤维（肌动蛋白丝、微管）、胶原纤维、晶体等有序结构均可引起偏振变化而被显示。","difficulty":2,"tags":["偏振光显微镜","双折射","细胞骨架"]},
{"id":137,"type":"truefalse","question":"双光子显微镜使用两个红外光子同时激发荧光，适合活体深层组织成像。","answer":"true","explanation":"双光子激发需要焦点处极高的光子密度，天然具有三维定位能力；红外光波长长、散射小、穿透深，光毒性低，因此双光子显微镜适合观察脑组织等活体深层结构。","difficulty":2,"tags":["双光子显微镜","活体成像"]},
{"id":138,"type":"truefalse","question":"冷冻蚀刻技术可以将生物膜沿脂双分子层疏水内部断裂开来。","answer":"true","explanation":"生物膜断裂面沿疏水相互作用最弱的脂双分子层内部进行，暴露出膜内蛋白颗粒，冷冻蚀刻据此显示膜蛋白在脂双层内的分布。","difficulty":2,"tags":["冷冻蚀刻","生物膜"]},
{"id":139,"type":"truefalse","question":"电镜图像的对比度主要来源于样品不同区域对电子的散射能力差异。","answer":"true","explanation":"电镜是电子散射成像：重金属染色区域散射电子能力强，到达底片电子少，图像暗；反之图像亮。反差由电子散射差异决定，与样品颜色无关。","difficulty":2,"tags":["电镜","对比度","电子散射"]},
{"id":140,"type":"truefalse","question":"X射线晶体学要求样品能够形成晶体，而冷冻电镜不需要。","answer":"true","explanation":"X射线晶体学需将生物大分子结晶后衍射分析，很多蛋白（尤其膜蛋白）难以结晶；冷冻电镜在玻璃态冰中直接成像单颗粒样品，无需结晶，是近年结构生物学的革命性突破。","difficulty":2,"tags":["X射线晶体学","冷冻电镜"]},
{"id":141,"type":"truefalse","question":"凝胶过滤层析中，大分子蛋白质先被洗脱出来。","answer":"true","explanation":"凝胶过滤层析中，大分子不能进入凝胶颗粒内部孔隙，流经路径短、先流出；小分子进入孔隙内路径长、后流出。因此洗脱顺序为从大到小。","difficulty":2,"tags":["凝胶过滤层析","分子筛"]},
{"id":142,"type":"truefalse","question":"亲和层析的纯化倍数通常高于离子交换层析。","answer":"true","explanation":"亲和层析基于特异性亲和结合（抗体-抗原、配体-受体等），目标蛋白一步即可获得极高纯度，纯化倍数常达百倍以上；离子交换层析按电荷差异分离，选择性相对较低，纯化倍数通常不及亲和层析。","difficulty":2,"tags":["亲和层析","离子交换层析","纯化"]},
{"id":143,"type":"truefalse","question":"SDS-PAGE中，蛋白质的迁移率与其天然构象和电荷无关，只取决于分子量。","answer":"true","explanation":"SDS按固定比例（约1.4 g SDS/g蛋白质）结合变性蛋白质并掩盖其固有电荷，β-巯基乙醇还原二硫键使蛋白质呈线性，故迁移率仅取决于分子量，可用于分子量测定。","difficulty":2,"tags":["SDS-PAGE","迁移率","分子量"]},
{"id":144,"type":"truefalse","question":"等电聚焦电泳中，蛋白质停留在其等电点（pI）对应的pH位置。","answer":"true","explanation":"等电聚焦在pH梯度中进行，蛋白质在电场中迁移至净电荷为零的等电点位置时不再移动，聚焦成窄带。该技术分辨率高，常用于二维电泳第一向分离。","difficulty":2,"tags":["等电聚焦","等电点"]},
{"id":145,"type":"truefalse","question":"Western blot可以用来检测特定蛋白质的表达量变化。","answer":"true","explanation":"Western blot经SDS-PAGE分离、转膜、抗体杂交和显色，条带灰度或化学发光强度与蛋白含量成正比，可比较不同样品中特定蛋白的表达差异，也可用内参蛋白（如β-actin）进行半定量。","difficulty":1,"tags":["Western blot","表达量"]},
{"id":146,"type":"truefalse","question":"盐析法能使蛋白质可逆沉淀，一般不破坏蛋白质的天然构象。","answer":"true","explanation":"盐析通过高浓度中性盐破坏蛋白质水化层使蛋白质沉淀，但不改变蛋白质一级结构和天然构象，脱盐后蛋白质可复溶并恢复活性，是温和的初步纯化方法。","difficulty":2,"tags":["盐析","蛋白质","可逆"]},
{"id":147,"type":"truefalse","question":"透析可用于去除蛋白质溶液中的盐等小分子杂质。","answer":"true","explanation":"透析利用半透膜（截留分子量如10~14 kDa）阻挡蛋白质大分子，而盐离子、小分子可自由扩散，通过更换外液可将小分子杂质逐渐除去，实现脱盐或缓冲液置换。","difficulty":1,"tags":["透析","脱盐"]},
{"id":148,"type":"truefalse","question":"酶的比活力等于总酶活力除以总蛋白质含量，是衡量酶纯度的标准。","answer":"true","explanation":"比活力=总活力（U）/总蛋白（mg），单位U/mg。提纯过程中随杂质去除，比活力逐渐升高，比活力越高说明酶越纯；纯化倍数=各步骤比活力/起始比活力。","difficulty":2,"tags":["比活力","酶纯度"]},
{"id":149,"type":"truefalse","question":"测定酶活力时应在底物饱和、最适温度和pH条件下测定反应初速度。","answer":"true","explanation":"酶活力测定需在底物饱和（使反应速度反映酶量而非底物限制）、最适温度和pH条件下测定初速度（产物随时间线性增加的阶段），否则测定结果不能准确反映酶活力。","difficulty":2,"tags":["酶活力","初速度"]},
{"id":150,"type":"truefalse","question":"ELISA技术可以用于定量检测样本中的抗原或抗体。","answer":"true","explanation":"ELISA将抗体（或抗原）包被固相，通过抗原-抗体特异结合和酶标二抗催化显色，显色深浅与待测物浓度成正比，结合标准曲线可定量，广泛用于临床诊断（如激素、病原体抗体检测）。","difficulty":1,"tags":["ELISA","定量检测"]},
{"id":151,"type":"truefalse","question":"免疫沉淀（IP）用于富集单个目标蛋白，免疫共沉淀（Co-IP）用于研究蛋白质间相互作用。","answer":"true","explanation":"IP用特异性抗体将单个目标蛋白从细胞裂解液中沉淀富集；Co-IP在温和条件下裂解保留蛋白复合体，沉淀目标蛋白时共沉淀其相互作用伙伴蛋白，用于蛋白互作研究。","difficulty":1,"tags":["免疫沉淀","Co-IP"]},
{"id":152,"type":"truefalse","question":"哺乳动物细胞培养通常在37℃、5% CO₂培养箱中进行。","answer":"true","explanation":"哺乳动物细胞最适温度约37℃，CO₂培养箱维持5% CO₂以配合培养基中碳酸氢盐缓冲体系稳定pH（约7.2~7.4）。","difficulty":1,"tags":["细胞培养","CO2","37℃"]},
{"id":153,"type":"truefalse","question":"血清在细胞培养基中的主要功能是提供生长因子、激素和贴壁因子等。","answer":"true","explanation":"血清（常用胎牛血清FBS）富含生长因子（EGF、PDGF等）、激素、贴壁因子（纤连蛋白）、转运蛋白、脂类和微量元素，为细胞体外生长提供全面营养支持，是经典培养基添加成分。","difficulty":1,"tags":["血清","生长因子"]},
{"id":154,"type":"truefalse","question":"细胞同步化技术可使培养的细胞群体处于同一细胞周期时相。","answer":"true","explanation":"细胞同步化通过药物阻断（双胸苷、秋水仙素）、血清饥饿、摇落法等方法使群体细胞同步进入特定周期时相，便于研究细胞周期特定事件（如DNA复制、有丝分裂）。","difficulty":1,"tags":["细胞同步化","细胞周期"]},
{"id":155,"type":"truefalse","question":"克隆形成实验通过单个细胞形成克隆的能力来评估细胞的增殖和存活能力。","answer":"true","explanation":"克隆形成实验将细胞稀释至单细胞后培养，计数形成克隆（一般≥50个细胞）的比例，克隆形成率反映细胞的增殖和存活能力，也用于放疗、化疗敏感性评估及干细胞研究。","difficulty":2,"tags":["克隆形成","增殖能力"]},
{"id":156,"type":"truefalse","question":"PCR技术可以在体外指数扩增特定的DNA片段。","answer":"true","explanation":"PCR以DNA为模板，经变性-退火-延伸循环，每轮DNA量翻倍，25~35轮扩增可达数百万倍，可对微量DNA进行扩增分析，是分子生物学最基本的技术之一。","difficulty":1,"tags":["PCR","DNA扩增"]},
{"id":157,"type":"truefalse","question":"光镊利用聚焦激光束产生的梯度力捕获和操控微小粒子。","answer":"true","explanation":"光镊利用高度聚焦激光束的梯度力（辐射压力）非接触捕获微米级粒子，可操控细胞、细胞器、DNA分子等，并可测量分子马达的力学参数（皮牛量级）。","difficulty":2,"tags":["光镊","激光","力学"]},
{"id":158,"type":"truefalse","question":"超分辨显微镜（STED、PALM等）已在2014年获诺贝尔化学奖，其分辨率可达数十纳米。","answer":"true","explanation":"2014年诺贝尔化学奖授予超分辨荧光显微技术开发者，STED、PALM/STORM等技术突破阿贝衍射极限（约200 nm），分辨率可达20~50 nm，实现纳米级活细胞成像。","difficulty":2,"tags":["超分辨","诺贝尔奖","STED"]},
]

qs = json.load(open(qp, encoding='utf-8'))
ids = {q['id'] for q in qs}
assert not (ids & {n['id'] for n in new}), 'ID冲突!'
qs.extend(new)
json.dump(qs, open(qp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('批次2完成: 新增', len(new), '题, 当前总数', len(qs))
