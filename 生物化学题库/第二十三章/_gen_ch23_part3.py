# -*- coding: utf-8 -*-
"""第二十三章 光合作用 出题批3 (题63-93): 考点5收尾 + 考点6 C4途径 + 考点7 光呼吸 + 考点8 调控与意义"""
import json, os

NEW = [
# ========== 考点5 卡尔文循环(续) ==========
{"id":63,"topic":"卡尔文循环","type":"multi",
 "question":"关于卡尔文循环中3-磷酸甘油酸(PGA)还原阶段的叙述,正确的有?",
 "options":{"A":"PGA先被ATP磷酸化生成1,3-二磷酸甘油酸","B":"1,3-二磷酸甘油酸再被NADPH还原","C":"还原阶段产物为3-磷酸甘油醛","D":"还原阶段不消耗能量"},
 "answer":"ABC",
 "explanation":"PGA还原分两步:磷酸化(消耗ATP,磷酸甘油酸激酶催化)和还原(消耗NADPH,3-磷酸甘油醛脱氢酶催化),产物为3-磷酸甘油醛,两步均消耗能量(同化力)。",
 "difficulty":2,"tags":["PGA还原","磷酸化","还原"]},

{"id":64,"topic":"卡尔文循环","type":"short",
 "question":"简述卡尔文循环三个阶段的主要反应。",
 "answer":"①CO2固定:Rubisco催化RuBP与CO2结合,生成2分子3-磷酸甘油酸(PGA);②还原:PGA先磷酸化(消耗ATP)生成1,3-二磷酸甘油酸,再被NADPH还原生成3-磷酸甘油醛;③RuBP再生:3-磷酸甘油醛经磷酸二羟丙酮及一系列转变,重新形成CO2受体RuBP。",
 "explanation":"卡尔文循环是碳同化的基本途径(C3途径),每循环一次固定1分子CO2,消耗3分子ATP和2分子NADPH。",
 "difficulty":2,"tags":["卡尔文循环","三阶段","简答"]},

{"id":65,"topic":"卡尔文循环","type":"choice",
 "question":"卡尔文循环运转3次(固定3分子CO2)后,净产生的磷酸丙糖是?",
 "options":{"A":"3分子葡萄糖","B":"1分子三碳糖(磷酸丙糖)","C":"3分子RuBP","D":"6分子3-磷酸甘油醛全部净得"},
 "answer":"B",
 "explanation":"固定3分子CO2产生6分子3-磷酸甘油醛,其中5分子用于再生RuBP,净产出1分子磷酸丙糖;故循环3次净得1分子三碳糖【教材补全】。",
 "difficulty":3,"tags":["净产物","磷酸丙糖","化学计量"]},

# ========== 考点6 C4途径 ==========
{"id":66,"topic":"C4途径","type":"choice",
 "question":"C4植物中,CO2最初的固定发生在?",
 "options":{"A":"维管束鞘细胞","B":"叶肉细胞","C":"类囊体腔","D":"线粒体"},
 "answer":"B",
 "explanation":"C4植物中CO2最初在外部叶肉细胞中与磷酸烯醇式丙酮酸(PEP)反应被固定,生成的4碳分子再转运到维管束鞘细胞释放CO2。",
 "difficulty":1,"tags":["C4途径","叶肉细胞","CO2固定"]},

{"id":67,"topic":"C4途径","type":"choice",
 "question":"C4途径中CO2的最初受体是?",
 "options":{"A":"RuBP","B":"磷酸烯醇式丙酮酸(PEP)","C":"3-磷酸甘油酸","D":"苹果酸"},
 "answer":"B",
 "explanation":"C4植物叶肉细胞中,PEP羧化酶催化CO2与PEP结合生成草酰乙酸;RuBP是卡尔文循环(C3)的CO2受体。",
 "difficulty":1,"tags":["C4途径","PEP","CO2受体"]},

{"id":68,"topic":"C4途径","type":"choice",
 "question":"C4途径中,草酰乙酸被还原生成的物质是?",
 "options":{"A":"苹果酸或天冬氨酸","B":"丙酮酸","C":"乙醇酸","D":"磷酸甘油醛"},
 "answer":"A",
 "explanation":"叶肉细胞中草酰乙酸被还原为苹果酸(或经转氨生成天冬氨酸),苹果酸作为四碳CO2载体转运到维管束鞘细胞。",
 "difficulty":2,"tags":["草酰乙酸","苹果酸","天冬氨酸"]},

{"id":69,"topic":"C4途径","type":"choice",
 "question":"C4植物中,四碳载体脱羧释放CO2的部位是?",
 "options":{"A":"叶肉细胞","B":"维管束鞘细胞","C":"细胞壁","D":"气孔"},
 "answer":"B",
 "explanation":"四碳CO2载体(苹果酸)通过胞间连丝运进邻近的维管束鞘细胞,脱羧形成三碳产物丙酮酸并释放CO2,CO2进入卡尔文循环被固定。",
 "difficulty":2,"tags":["C4途径","维管束鞘细胞","脱羧"]},

{"id":70,"topic":"C4途径","type":"choice",
 "question":"C4途径中苹果酸氧化脱羧的反应是?",
 "options":{"A":"苹果酸+NADP+→CO2+丙酮酸+NADPH+H+","B":"苹果酸+ATP→CO2+丙酮酸+ADP","C":"苹果酸+O2→草酰乙酸","D":"苹果酸→乙醇酸+CO2"},
 "answer":"A",
 "explanation":"维管束鞘细胞中苹果酸在苹果酸酶催化下氧化脱羧:苹果酸+NADP+→CO2+丙酮酸+NADPH+H+,同时产生NADPH。",
 "difficulty":2,"tags":["苹果酸","脱羧","反应式"]},

{"id":71,"topic":"C4途径","type":"truefalse",
 "question":"C4途径中,丙酮酸转变为PEP需要消耗ATP。",
 "answer":"true",
 "explanation":"丙酮酸运回叶肉细胞后经丙酮酸磷酸双激酶催化重新转变为PEP:丙酮酸+ATP+Pi→PEP+AMP+PPi,消耗1分子ATP(生成AMP)。",
 "difficulty":2,"tags":["丙酮酸","PEP","ATP"]},

{"id":72,"topic":"C4途径","type":"choice",
 "question":"与Rubisco相比,PEP羧化酶的特点是?",
 "options":{"A":"对CO2亲和力高,且不受O2竞争抑制","B":"对CO2亲和力低","C":"同时具有加氧酶活性","D":"只在维管束鞘细胞中起作用"},
 "answer":"A",
 "explanation":"PEP羧化酶对CO2亲和力远高于Rubisco,且无加氧酶活性、不受O2竞争抑制,使C4植物能在低CO2浓度下高效固定CO2【教材补全】。",
 "difficulty":2,"tags":["PEP羧化酶","CO2亲和力"]},

{"id":73,"topic":"C4途径","type":"choice",
 "question":"C4途径被称为\"CO2泵\",其生理意义是?",
 "options":{"A":"在维管束鞘细胞富集CO2,提高Rubisco羧化效率并抑制光呼吸","B":"直接合成葡萄糖","C":"降低光合速率","D":"使光合作用不需要光"},
 "answer":"A",
 "explanation":"C4途径在叶肉细胞固定CO2,再在维管束鞘细胞释放CO2,使维管束鞘细胞中CO2浓度升高,既提高Rubisco羧化效率,又抑制其加氧反应(光呼吸),适应高温干旱强光环境【教材补全】。",
 "difficulty":3,"tags":["C4途径","CO2泵","光呼吸"]},

{"id":74,"topic":"C4途径","type":"multi",
 "question":"关于C3与C4植物CO2固定的比较,正确的有?",
 "options":{"A":"C3植物在叶肉细胞经Rubisco固定CO2","B":"C4植物在叶肉细胞经PEP羧化酶固定CO2","C":"C4植物的卡尔文循环在维管束鞘细胞中进行","D":"C4植物能富集CO2,光呼吸相对较弱"},
 "answer":"ABCD",
 "explanation":"C3植物:叶肉细胞Rubisco固定CO2,卡尔文循环在叶肉细胞进行;C4植物:叶肉细胞PEP羧化酶固定,苹果酸转运到维管束鞘细胞脱羧供卡尔文循环,富集CO2抑制光呼吸【教材补全】。",
 "difficulty":3,"tags":["C3植物","C4植物","比较"]},

{"id":75,"topic":"C4途径","type":"short",
 "question":"简述C4植物固定CO2的四个步骤。",
 "answer":"①叶肉细胞吸收CO2,羧化PEP形成草酰乙酸(CO2+PEP→草酰乙酸+Pi);②草酰乙酸被还原为苹果酸(或天冬氨酸);③苹果酸经胞间连丝运进维管束鞘细胞,脱羧形成丙酮酸并释放CO2(苹果酸+NADP+→CO2+丙酮酸+NADPH+H+);④CO2进入卡尔文循环被固定,丙酮酸运回叶肉细胞重新转变为PEP(消耗ATP)。",
 "explanation":"C4途径通过\"空间分离\"实现CO2富集:叶肉细胞固定、维管束鞘细胞释放并进入卡尔文循环。",
 "difficulty":2,"tags":["C4途径","四步","简答"]},

{"id":76,"topic":"C4途径","type":"short",
 "question":"为什么C4植物的光呼吸比C3植物弱?",
 "answer":"①C4途径在叶肉细胞用PEP羧化酶固定CO2,并在维管束鞘细胞脱羧释放CO2,相当于\"CO2泵\",使维管束鞘细胞中CO2浓度远高于C3植物;②高CO2浓度使Rubisco羧化反应占优势,加氧反应(光呼吸)被竞争抑制;③故C4植物在高温、干旱、强光下仍能高效光合,光呼吸较弱【教材补全】。",
 "explanation":"C4途径的本质是CO2浓缩机制:通过提高Rubisco周围CO2浓度抑制其加氧活性,从而降低光呼吸。",
 "difficulty":3,"tags":["C4途径","光呼吸","CO2泵"]},

# ========== 考点7 光呼吸 ==========
{"id":77,"topic":"光呼吸","type":"choice",
 "question":"光呼吸中,Rubisco的加氧酶活性使RuBP与O2结合,生成的二碳产物是?",
 "options":{"A":"磷酸乙醇酸","B":"磷酸二羟丙酮","C":"磷酸甘油酸","D":"乙醛酸"},
 "answer":"A",
 "explanation":"Rubisco加氧反应:RuBP+O2→1分子3-磷酸甘油酸+1分子磷酸乙醇酸(2碳化合物);磷酸乙醇酸是乙醇酸途径的起始底物,故光呼吸又称C2循环【教材补全】。",
 "difficulty":2,"tags":["光呼吸","磷酸乙醇酸","加氧"]},

{"id":78,"topic":"光呼吸","type":"choice",
 "question":"Rubisco的双功能是指?",
 "options":{"A":"既能羧化RuBP又能使其加氧","B":"既能合成ATP又能合成NADPH","C":"既能固定CO2又能光解水","D":"既能催化又能调节pH"},
 "answer":"A",
 "explanation":"Rubisco是双功能酶:催化RuBP与CO2结合(羧化,光合固碳),也能催化RuBP与O2结合(加氧,启动光呼吸),两者竞争取决于CO2与O2浓度比【教材补全】。",
 "difficulty":2,"tags":["Rubisco","双功能酶","羧化与加氧"]},

{"id":79,"topic":"光呼吸","type":"choice",
 "question":"乙醇酸途径(光呼吸)涉及的细胞器是?",
 "options":{"A":"叶绿体、过氧化物酶体、线粒体","B":"叶绿体、内质网、高尔基体","C":"线粒体、溶酶体、核糖体","D":"过氧化物酶体、核仁、液泡"},
 "answer":"A",
 "explanation":"光呼吸(乙醇酸途径/C2循环)需要叶绿体、过氧化物酶体和线粒体三种细胞器协同:叶绿体生成乙醇酸,过氧化物酶体中氧化,线粒体中释放CO2【教材补全】。",
 "difficulty":2,"tags":["光呼吸","细胞器","乙醇酸途径"]},

{"id":80,"topic":"光呼吸","type":"choice",
 "question":"提高CO2浓度可以抑制光呼吸,其原因是?",
 "options":{"A":"CO2与O2竞争Rubisco的活性位点","B":"CO2直接抑制加氧酶合成","C":"CO2使Rubisco变性","D":"CO2使O2浓度降低"},
 "answer":"A",
 "explanation":"CO2与O2竞争Rubisco同一活性位点:CO2浓度高时羧化反应占优,加氧反应(光呼吸)被竞争抑制,故提高CO2浓度可促进光合、抑制光呼吸【教材补全】。",
 "difficulty":2,"tags":["光呼吸","CO2浓度","竞争抑制"]},

{"id":81,"topic":"光呼吸","type":"choice",
 "question":"光呼吸过程中CO2的释放主要发生在?",
 "options":{"A":"叶绿体","B":"过氧化物酶体","C":"线粒体","D":"类囊体腔"},
 "answer":"C",
 "explanation":"光呼吸CO2的释放主要在线粒体中进行:乙醇酸在叶绿体生成,过氧化物酶体中被氧化为甘氨酸,甘氨酸在线粒体中脱羧释放CO2【教材补全】。",
 "difficulty":3,"tags":["光呼吸","CO2释放","线粒体"]},

{"id":82,"topic":"光呼吸","type":"multi",
 "question":"下列关于光呼吸的叙述,正确的有?",
 "options":{"A":"只在光下进行","B":"消耗O2并释放CO2,不产生ATP","C":"底物是乙醇酸(磷酸乙醇酸),又称C2循环","D":"高O2低CO2条件促进光呼吸"},
 "answer":"ABCD",
 "explanation":"光呼吸:光下Rubisco加氧启动,消耗O2释放CO2、不产能,是磷酸乙醇酸的代谢途径即C2循环;高O2/低CO2利于加氧反应促进光呼吸,高CO2抑制【教材补全】。",
 "difficulty":3,"tags":["光呼吸","特点","C2循环"]},

{"id":83,"topic":"光呼吸","type":"truefalse",
 "question":"光呼吸与光合作用同时发生,在黑暗中也照样进行。",
 "answer":"false",
 "explanation":"光呼吸只在光下发生,其启动依赖Rubisco加氧与光反应提供的底物条件;无光即无光呼吸,故题述错误。",
 "difficulty":1,"tags":["光呼吸","光照条件"]},

{"id":84,"topic":"光呼吸","type":"short",
 "question":"简述光呼吸的生化过程要点及其意义。",
 "answer":"①过程:Rubisco加氧使RuBP与O2结合,生成1分子3-磷酸甘油酸和1分子磷酸乙醇酸(2碳);磷酸乙醇酸经乙醇酸途径(叶绿体→过氧化物酶体→线粒体)最终释放CO2,故称C2循环;②特点:光下进行,消耗O2、释放CO2、不产生ATP且净耗能;③意义:回收加氧产物中的部分碳,消耗过剩的ATP与还原力,避免强光下电子传递链过度还原【教材补全】。",
 "explanation":"光呼吸是Rubisco加氧活性引发的乙醇酸代谢途径,高CO2低O2抑制、高O2低CO2促进。",
 "difficulty":3,"tags":["光呼吸","乙醇酸途径","意义"]},

# ========== 考点8 光合作用调控与生理意义 ==========
{"id":85,"topic":"光合作用调控与生理意义","type":"choice",
 "question":"CAM途径(景天酸代谢)的特点是?",
 "options":{"A":"夜间气孔开放固定CO2为苹果酸,白天脱羧释放CO2供卡尔文循环","B":"白天固定CO2夜间释放","C":"与C4途径完全相同","D":"不固定CO2"},
 "answer":"A",
 "explanation":"CAM植物(景天、仙人掌等)夜间气孔开放,由PEP羧化酶固定CO2生成苹果酸贮于液泡;白天关闭气孔减少蒸腾,苹果酸脱羧释放CO2供卡尔文循环,实现时间分离以抗旱【教材补全】。",
 "difficulty":2,"tags":["CAM途径","景天酸代谢","昼夜节律"]},

{"id":86,"topic":"光合作用调控与生理意义","type":"truefalse",
 "question":"CAM植物在白天气孔开放,夜间气孔关闭。",
 "answer":"false",
 "explanation":"CAM植物恰恰相反:夜间气孔开放吸收CO2(固定为苹果酸贮于液泡),白天关闭气孔减少蒸腾失水,苹果酸脱羧供卡尔文循环【教材补全】。",
 "difficulty":2,"tags":["CAM途径","气孔","节律"]},

{"id":87,"topic":"光合作用调控与生理意义","type":"multi",
 "question":"下列关于光合产物合成与输出的叙述,正确的有?",
 "options":{"A":"淀粉在叶绿体内合成","B":"蔗糖在细胞质中合成","C":"磷酸丙糖是叶绿体输出的主要糖类","D":"磷酸丙糖经磷酸转运体与无机磷交换运出叶绿体"},
 "answer":"ABCD",
 "explanation":"磷酸丙糖是叶绿体输出的主要光合产物:一部分在叶绿体内合成淀粉,大部分经磷酸转运体(磷酸丙糖/无机磷交换)运出,在细胞质中合成蔗糖【教材补全】。",
 "difficulty":2,"tags":["光合产物","淀粉","蔗糖","磷酸丙糖"]},

{"id":88,"topic":"光合作用调控与生理意义","type":"choice",
 "question":"用14CO2饲喂植物并结合纸层析与放射自显影,可用于证明?",
 "options":{"A":"卡尔文循环的反应历程与CO2固定的最初产物","B":"光合磷酸化的机理","C":"叶绿素的结构","D":"光呼吸的量子需要量"},
 "answer":"A",
 "explanation":"卡尔文用14CO2示踪,经纸层析分离和放射自显影检测,发现最早被标记的化合物是3-磷酸甘油酸,从而阐明了卡尔文循环历程【教材补全】。",
 "difficulty":2,"tags":["14CO2示踪","卡尔文循环","研究方法"]},

{"id":89,"topic":"光合作用调控与生理意义","type":"choice",
 "question":"希尔反应证明?",
 "options":{"A":"光合作用释放的O2来自水","B":"光合作用释放的O2来自CO2","C":"NADPH在暗反应中合成","D":"光呼吸消耗O2"},
 "answer":"A",
 "explanation":"离体叶绿体在光照下加入人工氧化剂时释放O2而不固定CO2(希尔反应),证明光合放氧的O2全部来自水的光解而非CO2【教材补全】。",
 "difficulty":2,"tags":["希尔反应","O2来源","水的光解"]},

{"id":90,"topic":"光合作用调控与生理意义","type":"multi",
 "question":"光对卡尔文循环酶的激活机制包括?",
 "options":{"A":"光反应使叶绿体基质pH升高","B":"光反应使基质Mg2+浓度升高","C":"硫氧还蛋白介导的氧化还原调节","D":"Rubisco活化酶激活Rubisco"},
 "answer":"ABCD",
 "explanation":"光调节卡尔文循环:①光反应消耗H+使基质pH升高(约7→8);②H+泵入腔侧伴随Mg2+从腔内流入基质使Mg2+浓度升高;③硫氧还蛋白-铁氧还蛋白体系还原性激活多种酶;④Rubisco活化酶在光照下激活Rubisco【教材补全】。",
 "difficulty":3,"tags":["光调节","卡尔文循环","pH","Mg2+","硫氧还蛋白"]},

{"id":91,"topic":"光合作用调控与生理意义","type":"short",
 "question":"简述光合作用的三方面意义。",
 "answer":"①将无机物转变为有机物:绿色植物制造的光合产物是地球上有机物的最主要来源;②将光能转变为化学能:为人类及其他异养生物的活动提供能量;③保护环境和维持生态平衡:吸收CO2释放O2,维持大气中CO2与O2的平衡。",
 "explanation":"光合作用的意义可概括为物质来源、能量来源和生态平衡三方面。",
 "difficulty":1,"tags":["光合作用","意义","简答"]},

{"id":92,"topic":"光合作用调控与生理意义","type":"short",
 "question":"简述光反应与暗反应的关系。",
 "answer":"①定位不同:光反应发生在叶绿体类囊体膜,暗反应发生在叶绿体基质;②光反应通过光合磷酸化产生NADPH和ATP(同化力)并释放O2;③暗反应利用同化力将CO2还原为糖;④暗反应虽不直接需光,但依赖光反应产物,故整体在光下进行。",
 "explanation":"光反应与暗反应相互依存:光反应为暗反应提供ATP和NADPH,暗反应消耗同化力完成CO2还原,二者偶联构成完整的光合作用。",
 "difficulty":2,"tags":["光反应","暗反应","关系"]},

{"id":93,"topic":"光合作用调控与生理意义","type":"short",
 "question":"比较C3、C4与CAM植物固定CO2方式的主要区别。",
 "answer":"①C3植物:只在叶肉细胞由Rubisco固定CO2,直接进入卡尔文循环,无CO2浓缩机制,光呼吸较强;②C4植物:叶肉细胞PEP羧化酶固定CO2(空间分离),苹果酸转运到维管束鞘细胞脱羧供卡尔文循环,富集CO2抑制光呼吸,适应高温强光;③CAM植物:夜间气孔开放固定CO2为苹果酸贮液泡(时间分离),白天脱羧供卡尔文循环,适应干旱环境【教材补全】。",
 "explanation":"三者均为CO2固定方式:C3为单细胞直接固定,C4为空间分离,CAM为时间分离;后两者通过PEP羧化酶浓缩CO2抑制光呼吸。",
 "difficulty":3,"tags":["C3","C4","CAM","比较"]},
]

BASE = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(BASE, 'questions.json')
with open(out, 'r', encoding='utf-8') as f:
    QS = json.load(f)
assert QS[-1]['id'] == 62, '批2末题id应为62,实际%d' % QS[-1]['id']
QS.extend(NEW)
with open(out, 'w', encoding='utf-8') as f:
    json.dump(QS, f, ensure_ascii=False, indent=1)
print('批3完成: 追加 %d 题 (id 63-%d), 当前共 %d 题' % (len(NEW), NEW[-1]['id'], len(QS)))
