# -*- coding: utf-8 -*-
"""第二十三章 光合作用 出题批2 (题32-62): 考点3收尾 + 考点4光合磷酸化 + 考点5卡尔文循环前半"""
import json, os

NEW = [
# ========== 考点3 光反应与电子传递(续) ==========
{"id":32,"topic":"光反应与电子传递","type":"multi",
 "question":"非环式光合磷酸化的直接产物包括?",
 "options":{"A":"ATP","B":"NADPH","C":"O2","D":"葡萄糖"},
 "answer":"ABC",
 "explanation":"非环式光合磷酸化中,水的光解释放O2,电子传递伴随ATP合成,NADP+被还原为NADPH;葡萄糖是暗反应的产物。",
 "difficulty":2,"tags":["非环式光合磷酸化","产物","放氧"]},

{"id":33,"topic":"光反应与电子传递","type":"multi",
 "question":"下列关于光合电子传递链各组分的叙述,正确的有?",
 "options":{"A":"质体醌是脂溶性醌类,可在膜内移动","B":"质体蓝素是含铜蛋白","C":"铁氧还蛋白是铁硫蛋白","D":"细胞色素b6f复合物类似线粒体bc1复合物"},
 "answer":"ABCD",
 "explanation":"质体醌(脂溶性醌类,递氢递电子,可移动)、质体蓝素(含铜蛋白)、铁氧还蛋白(铁硫蛋白)、细胞色素b6f复合物(类似线粒体bc1)均为光合电子传递链组分【教材补全】。",
 "difficulty":3,"tags":["电子传递链","质体醌","质体蓝素","铁氧还蛋白","细胞色素b6f"]},

{"id":34,"topic":"光反应与电子传递","type":"choice",
 "question":"光合作用电子传递的总方向是?",
 "options":{"A":"水→NADP+","B":"NADP+→水","C":"O2→CO2","D":"CO2→葡萄糖"},
 "answer":"A",
 "explanation":"光合电子流总方向:水(电子供体)→PSII→PSI→NADP+(最终电子受体),与呼吸链(NADH→O2)方向相反。",
 "difficulty":1,"tags":["电子传递","方向","Z方案"]},

{"id":35,"topic":"光反应与电子传递","type":"short",
 "question":"简述非环式光合磷酸化的电子传递途径。",
 "answer":"①水的光解在光系统II一侧提供电子,释放O2;②电子经质体醌(PQ)→细胞色素b6f复合物→质体蓝素(PC)传递到光系统I的P700;③P700受光激发后,电子经铁氧还蛋白(Fd)最终使NADP+还原为NADPH;④整个过程伴随跨膜质子梯度的建立,驱动ATP合成,产物为ATP、NADPH和O2。",
 "explanation":"非环式电子传递是开放的线性通路:水是电子供体,NADP+是最终电子受体,同时产生ATP、NADPH和O2。",
 "difficulty":3,"tags":["非环式光合磷酸化","电子传递","途径"]},

# ========== 考点4 光合磷酸化 ==========
{"id":36,"topic":"光合磷酸化","type":"choice",
 "question":"光合磷酸化是指?",
 "options":{"A":"光系统捕获的光能中有一部分转化为ATP的磷酸键能的光驱动ATP合成过程","B":"光下叶绿体固定CO2的过程","C":"类囊体膜上合成NADPH的过程","D":"线粒体中ATP的合成过程"},
 "answer":"A",
 "explanation":"光合磷酸化:被生物的光系统捕获的光能有一部分能量转化为ATP的磷酸键能,这一光驱动的ATP合成过程称为光合磷酸化。",
 "difficulty":1,"tags":["光合磷酸化","定义"]},

{"id":37,"topic":"光合磷酸化","type":"choice",
 "question":"光合磷酸化的能量偶联机理遵循?",
 "options":{"A":"底物水平磷酸化","B":"化学渗透假说","C":"直接磷酸基转移","D":"基团移位"},
 "answer":"B",
 "explanation":"光合磷酸化的机理遵循化学渗透假说:光驱动电子传递在类囊体膜两侧建立质子梯度,质子经CF0-CF1 ATP合酶回流驱动ATP合成。",
 "difficulty":2,"tags":["光合磷酸化","化学渗透假说"]},

{"id":38,"topic":"光合磷酸化","type":"choice",
 "question":"光下类囊体腔与基质之间的质子浓度关系是?",
 "options":{"A":"腔内H+浓度高于基质","B":"腔内H+浓度低于基质","C":"两侧相等","D":"腔内不含质子"},
 "answer":"A",
 "explanation":"光驱动电子传递将H+泵入类囊体腔,腔内H+浓度高于基质(腔内pH低、基质pH高),形成跨膜质子梯度,驱动ATP合成【教材补全】。",
 "difficulty":2,"tags":["质子梯度","类囊体腔","化学渗透"]},

{"id":39,"topic":"光合磷酸化","type":"choice",
 "question":"叶绿体ATP合酶(CF0-CF1)的结构与功能是?",
 "options":{"A":"CF0催化ATP合成,CF1构成质子通道","B":"CF0构成质子通道,CF1催化ATP合成","C":"CF0与CF1都催化ATP合成","D":"CF0与CF1都是色素蛋白"},
 "answer":"B",
 "explanation":"叶绿体ATP合酶CF0-CF1:CF0为嵌在膜内的质子通道,CF1为朝向基质侧的催化部分,质子经CF0回流驱动CF1合成ATP【教材补全】。",
 "difficulty":2,"tags":["ATP合酶","CF0","CF1"]},

{"id":40,"topic":"光合磷酸化","type":"truefalse",
 "question":"解偶联剂能抑制光合电子传递。",
 "answer":"false",
 "explanation":"解偶联剂(如NH4Cl、DNP)使跨膜质子梯度消解,只抑制ATP合成,电子传递(水的光解与NADP+还原)照常进行【教材补全】。",
 "difficulty":2,"tags":["解偶联剂","光合磷酸化","电子传递"]},

{"id":41,"topic":"光合磷酸化","type":"choice",
 "question":"非环式与循环光合磷酸化的根本区别在于?",
 "options":{"A":"是否产生ATP","B":"最终电子受体不同(NADP+/P700)","C":"是否需要光","D":"是否经过光系统"},
 "answer":"B",
 "explanation":"非环式以NADP+为最终电子受体,生成ATP、NADPH和O2;循环式电子经细胞色素b6f回到P700,只生成ATP不生成NADPH;二者的根本区别是电子回路与最终受体不同。",
 "difficulty":3,"tags":["非环式","循环式","电子受体"]},

{"id":42,"topic":"光合磷酸化","type":"truefalse",
 "question":"光合磷酸化与线粒体氧化磷酸化都遵循化学渗透假说。",
 "answer":"true",
 "explanation":"二者都以跨膜质子梯度驱动ATP合酶合成ATP,区别仅在于建立质子梯度的能量来源:光合磷酸化来自光能驱动的电子传递,氧化磷酸化来自底物氧化【教材补全】。",
 "difficulty":2,"tags":["化学渗透","氧化磷酸化","光合磷酸化"]},

{"id":43,"topic":"光合磷酸化","type":"choice",
 "question":"非环式光合磷酸化中,类囊体腔内质子浓度升高主要依靠?",
 "options":{"A":"质体醌的穿梭递氢和水的光解","B":"质体蓝素的电子传递","C":"铁氧还蛋白还原NADP+","D":"Rubisco的羧化反应"},
 "answer":"A",
 "explanation":"腔内H+主要来自:①质体醌在膜内穿梭递氢,把H+带入腔侧;②水的光解在腔侧释放H+;另有细胞色素b6f的Q循环贡献【教材补全】。",
 "difficulty":3,"tags":["质子梯度","质体醌","水的光解"]},

{"id":44,"topic":"光合磷酸化","type":"choice",
 "question":"非环式电子传递中,每对电子从水到NADP+需要经过几次光激发?",
 "options":{"A":"1次","B":"2次(PSII与PSI各1次)","C":"3次","D":"0次"},
 "answer":"B",
 "explanation":"非环式电子传递必须经过PSII和PSI两次光激发(双光系统串联,Z方案),每对电子需要吸收2个光量子【教材补全】。",
 "difficulty":2,"tags":["光激发","双光系统","Z方案"]},

{"id":45,"topic":"光合磷酸化","type":"multi",
 "question":"化学渗透假说解释光合磷酸化的要点包括?",
 "options":{"A":"光驱动电子传递在类囊体膜两侧建立质子梯度","B":"质子经CF0通道回流到基质","C":"质子回流驱动CF1催化ADP磷酸化生成ATP","D":"ATP的合成发生在类囊体腔中"},
 "answer":"ABC",
 "explanation":"化学渗透:光驱动电子传递与递氢将H+泵入腔侧形成质子梯度,质子经CF0通道回流,驱动CF1在基质侧催化ATP合成;ATP合成不在腔中。",
 "difficulty":2,"tags":["化学渗透假说","质子梯度","ATP合酶"]},

{"id":46,"topic":"光合磷酸化","type":"multi",
 "question":"关于非环式与循环光合磷酸化的比较,正确的有?",
 "options":{"A":"非环式生成NADPH,循环式不生成","B":"非环式放氧,循环式不放氧","C":"循环式电子从P700出发经细胞色素b6f回到P700","D":"两者都生成ATP"},
 "answer":"ABCD",
 "explanation":"非环式:电子从水到NADP+,产物ATP+NADPH+O2;循环式:电子从P700出发经b6f回到P700,只产ATP不产NADPH也不放氧;两者均伴随ATP合成。",
 "difficulty":3,"tags":["非环式","循环式","比较"]},

{"id":47,"topic":"光合磷酸化","type":"short",
 "question":"简述光合磷酸化的类型及各自特点。",
 "answer":"①非环式光合磷酸化:电子经PSII→PSI线性传递,最终还原NADP+,生成ATP、NADPH和O2;②循环光合磷酸化:电子从P700经细胞色素b6f复合物回到P700,只生成ATP,不生成NADPH;③假循环光合磷酸化:电子最终传递给O2,不生成NADPH【教材补全】。",
 "explanation":"光合磷酸化分非环式、循环式(及假循环式)三类,区别在于电子流路线与最终电子受体(NADP+/P700/O2)不同。",
 "difficulty":2,"tags":["光合磷酸化","分类","非环式","循环式"]},

{"id":48,"topic":"光合磷酸化","type":"short",
 "question":"比较光合磷酸化与线粒体氧化磷酸化的异同。",
 "answer":"①相同:都遵循化学渗透假说,靠跨膜质子梯度经ATP合酶合成ATP;②能量来源不同:光合磷酸化由光能驱动的电子传递供能,氧化磷酸化由底物氧化(NADH/FADH2)供能;③质子梯度方向相反:光合的质子进入类囊体腔(腔内pH低),呼吸的质子泵出基质进入膜间隙;④电子流向相反:光合从水到NADP+,呼吸从NADH到O2【教材补全】。",
 "explanation":"两者是“相反方向的化学渗透机”,能量来源、质子梯度方向与电子流向均相反,但偶联机制相同。",
 "difficulty":3,"tags":["光合磷酸化","氧化磷酸化","化学渗透","比较"]},

# ========== 考点5 卡尔文循环 ==========
{"id":49,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环是指?",
 "options":{"A":"利用光反应形成的同化力(ATP和NADPH)将CO2还原形成糖类的过程","B":"光驱动ATP合成的过程","C":"水的光解过程","D":"葡萄糖氧化分解的过程"},
 "answer":"A",
 "explanation":"卡尔文循环利用光反应形成的同化力(ATP和NADPH)将CO2还原形成糖类,最初产物是3-磷酸甘油酸,故又称C3途径,是碳同化的基本途径。",
 "difficulty":1,"tags":["卡尔文循环","定义","同化力"]},

{"id":50,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环又称C3途径,其原因是?",
 "options":{"A":"CO2固定的最初产物是三碳化合物3-磷酸甘油酸","B":"循环包含三个酶","C":"需要三种辅酶参与","D":"循环在30℃下进行"},
 "answer":"A",
 "explanation":"卡尔文循环中CO2被固定后最初产物为3-磷酸甘油酸(三碳化合物),故称C3途径。",
 "difficulty":1,"tags":["卡尔文循环","C3途径"]},

{"id":51,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环中CO2的受体是?",
 "options":{"A":"磷酸烯醇式丙酮酸(PEP)","B":"核酮糖-1,5-二磷酸(RuBP)","C":"3-磷酸甘油酸","D":"草酰乙酸"},
 "answer":"B",
 "explanation":"CO2固定阶段,受体为RuBP(核酮糖-1,5-二磷酸),由Rubisco催化;PEP是C4途径的CO2受体,草酰乙酸是C4固定的产物。",
 "difficulty":1,"tags":["CO2受体","RuBP"]},

{"id":52,"topic":"卡尔文循环","type":"choice",
 "question":"催化CO2与RuBP结合的酶是?",
 "options":{"A":"PEP羧化酶","B":"核酮糖-1,5-二磷酸羧化酶(Rubisco)","C":"磷酸甘油酸激酶","D":"苹果酸脱氢酶"},
 "answer":"B",
 "explanation":"CO2固定由Rubisco(核酮糖-1,5-二磷酸羧化酶)催化,使RuBP羧化生成2分子3-磷酸甘油酸。",
 "difficulty":1,"tags":["Rubisco","CO2固定"]},

{"id":53,"topic":"卡尔文循环","type":"choice",
 "question":"Rubisco催化CO2固定生成的产物是?",
 "options":{"A":"3-磷酸甘油酸(PGA)","B":"3-磷酸甘油醛","C":"1,3-二磷酸甘油酸","D":"草酰乙酸"},
 "answer":"A",
 "explanation":"Rubisco催化RuBP与CO2结合,生成2分子3-磷酸甘油酸(PGA),PGA即CO2固定的最初产物。",
 "difficulty":2,"tags":["Rubisco","PGA","CO2固定"]},

{"id":54,"topic":"卡尔文循环","type":"truefalse",
 "question":"光是Rubisco的最终激活剂。",
 "answer":"true",
 "explanation":"光通过光反应使叶绿体基质pH升高、Mg2+浓度升高,并激活Rubisco活化酶,从而激活Rubisco,故课件强调\"光是Rubisco的最终激活剂\"。",
 "difficulty":2,"tags":["Rubisco","光调节"]},

{"id":55,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环中,3-磷酸甘油酸(PGA)还原生成3-磷酸甘油醛需要消耗?",
 "options":{"A":"仅ATP","B":"ATP和NADPH(同化力)","C":"仅NADPH","D":"GTP和NADH"},
 "answer":"B",
 "explanation":"PGA还原分为磷酸化(消耗ATP)和还原(消耗NADPH)两步,即消耗同化力ATP和NADPH。",
 "difficulty":2,"tags":["PGA还原","同化力","ATP","NADPH"]},

{"id":56,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环中\"3-磷酸甘油酸+ATP→1,3-二磷酸甘油酸+ADP\"的催化酶是?",
 "options":{"A":"磷酸甘油酸激酶","B":"3-磷酸甘油醛脱氢酶","C":"Rubisco","D":"核酮糖磷酸激酶"},
 "answer":"A",
 "explanation":"PGA的磷酸化由磷酸甘油酸激酶催化(消耗1分子ATP);后续还原由3-磷酸甘油醛脱氢酶催化(消耗1分子NADPH)【教材补全】。",
 "difficulty":2,"tags":["磷酸甘油酸激酶","PGA磷酸化"]},

{"id":57,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环中1,3-二磷酸甘油酸被还原的产物是?",
 "options":{"A":"3-磷酸甘油酸","B":"3-磷酸甘油醛","C":"磷酸二羟丙酮","D":"核酮糖-5-磷酸"},
 "answer":"B",
 "explanation":"1,3-二磷酸甘油酸+NADPH→3-磷酸甘油醛+NADP++Pi,3-磷酸甘油醛是光合作用中形成的第一个三碳糖。",
 "difficulty":2,"tags":["还原反应","3-磷酸甘油醛"]},

{"id":58,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环中RuBP再生的路径是?",
 "options":{"A":"3-磷酸甘油醛转变为磷酸二羟丙酮,经一系列转变重新形成RuBP","B":"3-磷酸甘油酸直接变回RuBP","C":"CO2直接与核酮糖-5-磷酸结合","D":"RuBP由葡萄糖分解而来"},
 "answer":"A",
 "explanation":"再生阶段:3-磷酸甘油醛转变成磷酸二羟丙酮,再经一系列转变(转酮醇酶、转醛醇酶、磷酸酶等参与)重新形成CO2受体RuBP,使循环得以运转。",
 "difficulty":2,"tags":["RuBP再生","磷酸二羟丙酮"]},

{"id":59,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环每固定6分子CO2合成1分子葡萄糖,消耗的ATP和NADPH分别是?",
 "options":{"A":"12 ATP和18 NADPH","B":"18 ATP和12 NADPH","C":"6 ATP和6 NADPH","D":"18 ATP和18 NADPH"},
 "answer":"B",
 "explanation":"每固定1分子CO2消耗3分子ATP和2分子NADPH;固定6分子CO2共消耗18分子ATP和12分子NADPH【教材补全】。",
 "difficulty":3,"tags":["ATP消耗","NADPH消耗","化学计量"]},

{"id":60,"topic":"卡尔文循环","type":"choice",
 "question":"Rubisco的亚基组成与基因编码特点是?",
 "options":{"A":"大亚基由叶绿体基因编码,小亚基由核基因编码","B":"大小亚基都由核基因编码","C":"大小亚基都由叶绿体基因编码","D":"由单一亚基组成"},
 "answer":"A",
 "explanation":"Rubisco由大亚基和小亚基组成:大亚基由叶绿体基因组编码,小亚基由核基因编码;它是植物体内含量最丰富的蛋白质【教材补全】。",
 "difficulty":3,"tags":["Rubisco","亚基","基因编码"]},

{"id":61,"topic":"卡尔文循环","type":"multi",
 "question":"卡尔文循环的三个阶段包括?",
 "options":{"A":"CO2固定","B":"3-磷酸甘油酸还原","C":"RuBP再生","D":"水的光解"},
 "answer":"ABC",
 "explanation":"卡尔文循环包括CO2固定、3-磷酸甘油酸还原、RuBP再生三个阶段;水的光解属于光反应。",
 "difficulty":1,"tags":["卡尔文循环","三阶段"]},

{"id":62,"topic":"卡尔文循环","type":"multi",
 "question":"卡尔文循环的运转需要消耗的物质包括?",
 "options":{"A":"CO2","B":"ATP","C":"NADPH","D":"O2"},
 "answer":"ABC",
 "explanation":"卡尔文循环以CO2为底物,消耗光反应提供的同化力ATP和NADPH;O2是光呼吸的底物而非卡尔文循环的消耗物。",
 "difficulty":2,"tags":["卡尔文循环","消耗物","同化力"]},
]

BASE = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(BASE, 'questions.json')
with open(out, 'r', encoding='utf-8') as f:
    QS = json.load(f)
assert QS[-1]['id'] == 31, '批1末题id应为31,实际%d' % QS[-1]['id']
QS.extend(NEW)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(QS, f, ensure_ascii=False, indent=1)
print('批2完成: 追加 %d 题 (id 32-%d), 当前共 %d 题' % (len(NEW), NEW[-1]['id'], len(QS)))
