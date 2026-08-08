# -*- coding: utf-8 -*-
"""第二十章 补充题(985真题参照:蚕豆病/G6PD缺乏症与红细胞溶血)"""
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

Q = []

Q.append({
    "id": 1,
    "topic": "NADPH的生物学作用",
    "type": "choice",
    "question": "蚕豆病(6-磷酸葡萄糖脱氢酶缺乏症)患者食用蚕豆后易发生溶血性贫血,其根本原因是?",
    "options": {
        "A": "红细胞内NADPH生成不足,还原型谷胱甘肽(GSH)再生受阻,含-SH基的蛋白质和脂膜易被过氧化物氧化损伤",
        "B": "红细胞内ATP合成受阻,能量供应不足",
        "C": "红细胞内5-磷酸核糖缺乏,不能合成核酸",
        "D": "红细胞内葡萄糖不能进入细胞,糖酵解完全停止"
    },
    "answer": "A",
    "explanation": "红细胞没有线粒体,主要依靠磷酸戊糖途径提供NADPH,后者作为谷胱甘肽还原酶的辅酶维持GSH的还原状态,保护膜蛋白-SH基与脂膜免受氧化;6-磷酸葡萄糖脱氢酶缺乏时NADPH生成不足,GSH再生受阻,红细胞膜被氧化损伤而发生溶血,这是蚕豆病的发病基础。",
    "difficulty": 2,
    "tags": ["6-磷酸葡萄糖脱氢酶", "NADPH", "GSH", "红细胞", "溶血", "蚕豆病", "真题参照", "考纲44"]
})

Q.append({
    "id": 2,
    "topic": "NADPH的生物学作用",
    "type": "truefalse",
    "question": "6-磷酸葡萄糖脱氢酶缺乏时,红细胞内NADPH生成减少,还原型谷胱甘肽(GSH)再生受阻,红细胞易受氧化损伤而发生溶血。",
    "answer": "true",
    "explanation": "红细胞依赖磷酸戊糖途径产生NADPH,NADPH作为谷胱甘肽还原酶的辅酶使GSSG还原为GSH,保护红细胞膜及蛋白质-SH基;G6PDH缺乏→NADPH不足→GSH再生受阻→膜被过氧化损伤→溶血,即蚕豆病的发病机制。",
    "difficulty": 2,
    "tags": ["6-磷酸葡萄糖脱氢酶", "NADPH", "GSH", "溶血", "蚕豆病", "真题参照", "考纲44"]
})

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_part_g.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(Q, f, ensure_ascii=False, indent=1)
print(f'part_g: {len(Q)} 题已落盘 -> {path}')
