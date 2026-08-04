#!/usr/bin/env python3
"""湖南大学考研题库 - 构建脚本 v3 (图片嵌入版)"""
import json, os, sys, base64

BASE_DIR = r'c:\Users\Lenovo\Desktop\湖南大学'
OUTPUT = os.path.join(BASE_DIR, '生物化学题库', '湖南大学题库系统.html')

# ============================================================
# 数据源
# ============================================================
SUBJECTS = {
    'biochem_1_2': {
        'key': 'biochem_1_2', 'name': '生物化学', 'code': '338',
        'chapterLabel': '1+2 绪论+AA',
        'questionsFile': '生物化学题库/第一章+第二章/questions.json',
        'termsFile': '生物化学题库/第一章+第二章/terms.json',
    },
    'biochem_3': {
        'key': 'biochem_3', 'name': '生物化学', 'code': '338',
        'chapterLabel': '3 pr的结构',
        'questionsFile': '生物化学题库/第三章/questions.json',
        'termsFile': '生物化学题库/第三章/terms.json',
    },
    'biochem_4': {
        'key': 'biochem_4', 'name': '生物化学', 'code': '338',
        'chapterLabel': '4 pr的功能',
        'questionsFile': '生物化学题库/第四章/questions.json',
        'termsFile': '生物化学题库/第四章/terms.json',
    },
    'cellbio_1': {
        'key': 'cellbio_1', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '1 绪论',
        'questionsFile': '细胞生物学题库/第一章绪论/questions.json',
        'termsFile': '细胞生物学题库/第一章绪论/terms.json',
    },
    'cellbio_2': {
        'key': 'cellbio_2', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '2 研究方法',
        'questionsFile': '细胞生物学题库/第二章/questions.json',
        'termsFile': '细胞生物学题库/第二章/terms.json',
    },
    'biochem_5': {
        'key': 'biochem_5', 'name': '生物化学', 'code': '338',
        'chapterLabel': '5 蛋白质分离纯化',
        'questionsFile': '生物化学题库/第五章/questions.json',
        'termsFile': '生物化学题库/第五章/terms.json',
    },
    'biochem_6': {
        'key': 'biochem_6', 'name': '生物化学', 'code': '338',
        'chapterLabel': '6 酶的催化作用',
        'questionsFile': '生物化学题库/第六章/questions.json',
        'termsFile': '生物化学题库/第六章/terms.json',
    },
    'biochem_7': {
        'key': 'biochem_7', 'name': '生物化学', 'code': '338',
        'chapterLabel': '7 酶动力学',
        'questionsFile': '生物化学题库/第七章/questions.json',
        'termsFile': '生物化学题库/第七章/terms.json',
    },
    'biochem_8': {
        'key': 'biochem_8', 'name': '生物化学', 'code': '338',
        'chapterLabel': '8 酶的作用机制',
        'questionsFile': '生物化学题库/第八章/questions.json',
        'termsFile': '生物化学题库/第八章/terms.json',
    },
    'biochem_9': {
        'key': 'biochem_9', 'name': '生物化学', 'code': '338',
        'chapterLabel': '9 糖类和糖生物学',
        'questionsFile': '生物化学题库/第九章/questions.json',
        'termsFile': '生物化学题库/第九章/terms.json',
    },
    'biochem_10': {
        'key': 'biochem_10', 'name': '生物化学', 'code': '338',
        'chapterLabel': '10 脂质和生物膜',
        'questionsFile': '生物化学题库/第十章/questions.json',
        'termsFile': '生物化学题库/第十章/terms.json',
    },
    'biochem_11': {
        'key': 'biochem_11', 'name': '生物化学', 'code': '338',
        'chapterLabel': '11 核酸的结构',
        'questionsFile': '生物化学题库/第十一章/questions.json',
        'termsFile': '生物化学题库/第十一章/terms.json',
    },
    'biochem_12': {
        'key': 'biochem_12', 'name': '生物化学', 'code': '338',
        'chapterLabel': '12 核酸的物化性质',
        'questionsFile': '生物化学题库/第十二章/questions.json',
        'termsFile': '生物化学题库/第十二章/terms.json',
    },
    'biochem_13': {
        'key': 'biochem_13', 'name': '生物化学', 'code': '338',
        'chapterLabel': '13 维生素和辅酶',
        'questionsFile': '生物化学题库/第十三章/questions.json',
        'termsFile': '生物化学题库/第十三章/terms.json',
    },
    'biochem_14': {
        'key': 'biochem_14', 'name': '生物化学', 'code': '338',
        'chapterLabel': '14 激素和信号转导',
        'questionsFile': '生物化学题库/第十四章/questions.json',
        'termsFile': '生物化学题库/第十四章/terms.json',
    },
    'cellbio_3': {
        'key': 'cellbio_3', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '3 细胞质膜',
        'questionsFile': '细胞生物学题库/第三章/questions.json',
        'termsFile': '细胞生物学题库/第三章/terms.json',
    },
    'cellbio_4': {
        'key': 'cellbio_4', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '4 物质的跨膜运输',
        'questionsFile': '细胞生物学题库/第四章/questions.json',
        'termsFile': '细胞生物学题库/第四章/terms.json',
    },
    'cellbio_5': {
        'key': 'cellbio_5', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '5 内膜系统',
        'questionsFile': '细胞生物学题库/第五章/questions.json',
        'termsFile': '细胞生物学题库/第五章/terms.json',
    },
    'cellbio_6': {
        'key': 'cellbio_6', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '6 蛋白质分选',
        'questionsFile': '细胞生物学题库/第六章/questions.json',
        'termsFile': '细胞生物学题库/第六章/terms.json',
    },
    'cellbio_7': {
        'key': 'cellbio_7', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '7 线粒体和叶绿体',
        'questionsFile': '细胞生物学题库/第七章/questions.json',
        'termsFile': '细胞生物学题库/第七章/terms.json',
    },
    'cellbio_8': {
        'key': 'cellbio_8', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '8 细胞骨架',
        'questionsFile': '细胞生物学题库/第八章/questions.json',
        'termsFile': '细胞生物学题库/第八章/terms.json',
    },
    'cellbio_9': {
        'key': 'cellbio_9', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '9 细胞核与染色质',
        'questionsFile': '细胞生物学题库/第九章/questions.json',
        'termsFile': '细胞生物学题库/第九章/terms.json',
    },
    'cellbio_10': {
        'key': 'cellbio_10', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '10 核糖体',
        'questionsFile': '细胞生物学题库/第十章/questions.json',
        'termsFile': '细胞生物学题库/第十章/terms.json',
    },
    'cellbio_11': {
        'key': 'cellbio_11', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '11 细胞信号转导',
        'questionsFile': '细胞生物学题库/第十一章/questions.json',
        'termsFile': '细胞生物学题库/第十一章/terms.json',
    },
    'cellbio_12': {
        'key': 'cellbio_12', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '12 细胞周期与分裂',
        'questionsFile': '细胞生物学题库/第十二章/questions.json',
        'termsFile': '细胞生物学题库/第十二章/terms.json',
    },
    'cellbio_13': {
        'key': 'cellbio_13', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '13 增殖调控与癌细胞',
        'questionsFile': '细胞生物学题库/第十三章/questions.json',
        'termsFile': '细胞生物学题库/第十三章/terms.json',
    },
    'cellbio_14': {
        'key': 'cellbio_14', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '14 细胞分化与干细胞',
        'questionsFile': '细胞生物学题库/第十四章/questions.json',
        'termsFile': '细胞生物学题库/第十四章/terms.json',
    },
    'cellbio_15': {
        'key': 'cellbio_15', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '15 细胞衰老与死亡',
        'questionsFile': '细胞生物学题库/第十五章/questions.json',
        'termsFile': '细胞生物学题库/第十五章/terms.json',
    },
    'cellbio_16': {
        'key': 'cellbio_16', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '16 细胞的社会联系',
        'questionsFile': '细胞生物学题库/第十六章/questions.json',
        'termsFile': '细胞生物学题库/第十六章/terms.json',
    },
}

COURSES = {
    'biochemistry': {'name': '生物化学', 'code': '338',
                     'chapters': ['biochem_1_2', 'biochem_3', 'biochem_4',
                                  'biochem_5', 'biochem_6', 'biochem_7', 'biochem_8',
                                  'biochem_9', 'biochem_10', 'biochem_11', 'biochem_12',
                                  'biochem_13', 'biochem_14']},
    'cellbiology': {'name': '细胞生物学', 'code': '851',
                     'chapters': ['cellbio_1', 'cellbio_2', 'cellbio_3', 'cellbio_4',
                                  'cellbio_5', 'cellbio_6', 'cellbio_7', 'cellbio_8',
                                  'cellbio_9', 'cellbio_10', 'cellbio_11', 'cellbio_12',
                                  'cellbio_13', 'cellbio_14', 'cellbio_15', 'cellbio_16']},
}

CHAPTER_NAMES = {
    'biochem_1_2': '1+2 绪论+AA', 'biochem_3': '3 pr的结构',
    'biochem_4': '4 pr的功能', 'biochem_5': '5 pr分离纯化',
    'biochem_6': '6 酶的催化', 'biochem_7': '7 酶动力学',
    'biochem_8': '8 酶作用机制', 'biochem_9': '9 糖类',
    'biochem_10': '10 脂质和生物膜', 'biochem_11': '11 核酸结构',
    'biochem_12': '12 核酸物化', 'biochem_13': '13 维生素和辅酶',
    'biochem_14': '14 激素和信号转导',
    'cellbio_1': '1 绪论', 'cellbio_2': '2 研究方法',
    'cellbio_3': '3 细胞质膜', 'cellbio_4': '4 跨膜运输',
    'cellbio_5': '5 内膜系统', 'cellbio_6': '6 蛋白质分选',
    'cellbio_7': '7 线粒体叶绿体', 'cellbio_8': '8 细胞骨架',
    'cellbio_9': '9 细胞核染色质', 'cellbio_10': '10 核糖体',
    'cellbio_11': '11 信号转导', 'cellbio_12': '12 细胞周期',
    'cellbio_13': '13 增殖与癌细胞', 'cellbio_14': '14 分化与干细胞',
    'cellbio_15': '15 衰老与死亡', 'cellbio_16': '16 社会联系',
}

# ============================================================
# 图片嵌入
# ============================================================
def load_image_b64(rel_path):
    """读取图片并转为 base64 data URI"""
    fp = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(fp):
        print(f'  [WARN] 图片未找到: {rel_path}')
        return ''
    with open(fp, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(rel_path)[1].lower()
    mime = 'image/png' if ext == '.png' else 'image/jpeg'
    b64 = base64.b64encode(data).decode('ascii')
    print(f'  [IMG] {rel_path}: {len(data)/1024:.1f} KB -> base64')
    return f'data:{mime};base64,{b64}'

def load_images():
    images = {
        'logo': '生物化学题库/湖南大学-logo-2048px.png',
        'emblem': '生物化学题库/和 校徽融合的图.jpg',
        'bg': '生物化学题库/背景图.jpg',
    }
    result = {}
    for key, path in images.items():
        result[key] = load_image_b64(path)
    return result

# ============================================================
# 数据加载
# ============================================================
def load_data():
    banks = {}
    for key, cfg in SUBJECTS.items():
        qf = os.path.join(BASE_DIR, cfg['questionsFile'])
        tf = os.path.join(BASE_DIR, cfg['termsFile'])

        with open(qf, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        with open(tf, 'r', encoding='utf-8') as f:
            terms = json.load(f)

        # 规范化题目
        for q in questions:
            if 'tags' not in q: q['tags'] = []
            if 'topic' in q and q['topic'] and q['topic'] not in q['tags']:
                q['tags'].insert(0, q['topic'])
            if 'difficulty' not in q: q['difficulty'] = 1

        # 规范化术语
        normalized_terms = []
        for t in terms:
            if isinstance(t, list):
                normalized_terms.append({
                    'id': t[0],
                    'name': t[1] if len(t) > 1 else '',
                    'definition': t[2] if len(t) > 2 else '暂无详细定义',
                    'chapter': key
                })
            elif isinstance(t, dict):
                if 'term' in t and 'name' not in t: t['name'] = t['term']
                if 'definition' not in t: t['definition'] = '暂无详细定义'
                t['chapter'] = key
                normalized_terms.append(t)

        choice_n = sum(1 for q in questions if q['type'] == 'choice')
        tf_n = sum(1 for q in questions if q['type'] == 'truefalse')
        multi_n = sum(1 for q in questions if q['type'] == 'multi')
        short_n = sum(1 for q in questions if q['type'] == 'short')

        banks[key] = {
            'key': key, 'name': cfg['name'], 'code': cfg['code'],
            'chapterLabel': cfg['chapterLabel'],
            'questions': questions, 'terms': normalized_terms,
            'stats': {'total': len(questions), 'choice': choice_n,
                      'truefalse': tf_n, 'multi': multi_n,
                      'short': short_n, 'terms': len(normalized_terms)}
        }

    # ============================================================
    # 验证关卡 — 任一失败立即终止构建
    # ============================================================
    print('\n[验证] 检查数据完整性...')
    validation_errors = []
    for key, bank in banks.items():
        qs = bank['questions']
        ids_seen = set()
        for q in qs:
            qid = q.get('id', '?')
            qtype = q.get('type', '')
            # 必填字段
            for field in ['id', 'type', 'question', 'answer']:
                if field not in q:
                    validation_errors.append('[%s #%s] 缺少字段: %s' % (key, qid, field))
            # choice验证
            if qtype == 'choice':
                opts = q.get('options', {})
                ans = str(q.get('answer', ''))
                if not isinstance(opts, dict) or len(opts) == 0:
                    validation_errors.append('[%s #%s] choice缺少有效options' % (key, qid))
                elif ans and ans not in opts:
                    validation_errors.append('[%s #%s] answer=%s不在options中' % (key, qid, ans))
            # truefalse验证
            if qtype == 'truefalse':
                ans = str(q.get('answer', '')).strip().lower()
                if ans not in ('true', 'false'):
                    validation_errors.append('[%s #%s] TF答案非true/false: %s' % (key, qid, ans))
            # multi验证
            if qtype == 'multi':
                opts = q.get('options', {})
                ans = str(q.get('answer', ''))
                if not isinstance(opts, dict) or len(opts) == 0:
                    validation_errors.append('[%s #%s] multi缺少有效options' % (key, qid))
                else:
                    for ch in ans:
                        if ch not in opts:
                            validation_errors.append('[%s #%s] multi answer中%s不在options中' % (key, qid, ch))
            # short验证
            if qtype == 'short':
                ans = str(q.get('answer', ''))
                if not ans or len(ans.strip()) < 5:
                    validation_errors.append('[%s #%s] short答案为空或过短' % (key, qid))
            # 题型合法性
            if qtype not in ('choice', 'truefalse', 'multi', 'short'):
                validation_errors.append('[%s #%s] 无效题型: %s' % (key, qid, qtype))
            # ID唯一
            if qid != '?' and qid in ids_seen:
                validation_errors.append('[%s] 重复ID: %s' % (key, qid))
            ids_seen.add(qid)

    if validation_errors:
        print('\n[验证失败] 发现 %d 个错误:' % len(validation_errors))
        for err in validation_errors:
            print('  ERROR: ' + err)
        print('\n构建中止 - 请修复以上错误后重试')
        sys.exit(1)
    print('[验证通过] 所有数据完整，开始构建...\n')

    return banks

# ============================================================
# 组装
# ============================================================
def build(banks, images):
    # 读CSS
    with open(os.path.join(BASE_DIR, 'src_css.txt'), 'r', encoding='utf-8') as f:
        CSS = f.read()

    # 读JS模板
    with open(os.path.join(BASE_DIR, 'src_js.txt'), 'r', encoding='utf-8') as f:
        JS = f.read()

    # 序列化数据
    banks_js = json.dumps(banks, ensure_ascii=False, separators=(',', ':'))
    courses_js = json.dumps(COURSES, ensure_ascii=False, separators=(',', ':'))
    ch_names_js = json.dumps(CHAPTER_NAMES, ensure_ascii=False, separators=(',', ':'))
    keys_js = json.dumps(list(SUBJECTS.keys()), ensure_ascii=False)

    default_course = 'biochemistry'
    default_subject = 'biochem_1_2'

    # 替换占位符
    JS = JS.replace('{__BANKS__}', banks_js)
    JS = JS.replace('{__COURSES__}', courses_js)
    JS = JS.replace('{__CH_NAMES__}', ch_names_js)
    JS = JS.replace('__COURSE__', default_course)
    JS = JS.replace('__SUBJECT__', default_subject)
    JS = JS.replace('__KEYS__', keys_js)

    # 替换图片
    for key, b64 in images.items():
        placeholder = f'__{key.upper()}_B64__'
        JS = JS.replace(placeholder, b64)

    # 构建HTML
    html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n'
    html += '<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    html += '<meta name="theme-color" content="#F9F6F0">\n'
    html += '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    html += '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
    html += '<title>湖南大学考研题库</title>\n'
    html += '<style>\n' + CSS + '\n</style>\n'
    html += '</head>\n<body>\n'
    html += '<script>\n' + JS + '\n</script>\n'
    html += '</body>\n</html>'

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(OUTPUT) / 1024
    total_qs = sum(b['stats']['total'] for b in banks.values())
    total_terms = sum(b['stats']['terms'] for b in banks.values())
    print(f'\n[OK] {OUTPUT}')
    print(f'     文件大小: {size_kb:.1f} KB')
    print(f'     题目: {total_qs} 题 | 术语: {total_terms} 条')

if __name__ == '__main__':
    print('加载图片...')
    images = load_images()
    print('\n加载题库数据...')
    banks = load_data()
    print('\n构建HTML...')
    build(banks, images)
