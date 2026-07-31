#!/usr/bin/env python3
"""湖南大学考研题库 构建脚本"""
import json, os, base64

BASE_DIR = r'c:\Users\Lenovo\Desktop\湖南大学'
OUTPUT = os.path.join(BASE_DIR, '生物化学题库', '题库系统.html')

SUBJECTS = {
    'biochemistry': {
        'key': 'biochemistry', 'name': '生物化学', 'code': '338',
        'chapterLabel': '1+2 绪论+AA简介',
        'questionsFile': os.path.join(BASE_DIR, '生物化学题库/第一章+第二章/questions.json'),
        'termsFile': os.path.join(BASE_DIR, '生物化学题库/第一章+第二章/terms.json'),
    },
    'cellbiology': {
        'key': 'cellbiology', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '1 绪论',
        'questionsFile': os.path.join(BASE_DIR, '细胞生物学题库/绪论/questions.json'),
        'termsFile': os.path.join(BASE_DIR, '细胞生物学题库/绪论/terms.json'),
    },
    'biochem_ch3': {
        'key': 'biochem_ch3', 'name': '生物化学', 'code': '338',
        'chapterLabel': '3 pr的结构',
        'questionsFile': os.path.join(BASE_DIR, '生物化学题库/第三章/questions.json'),
        'termsFile': os.path.join(BASE_DIR, '生物化学题库/第三章/terms.json'),
    },
    'biochem_ch4': {
        'key': 'biochem_ch4', 'name': '生物化学', 'code': '338',
        'chapterLabel': '4 pr的功能',
        'questionsFile': os.path.join(BASE_DIR, '生物化学题库/第四章/questions.json'),
        'termsFile': os.path.join(BASE_DIR, '生物化学题库/第四章/terms.json'),
    },
    'cellbio_ch2': {
        'key': 'cellbio_ch2', 'name': '细胞生物学', 'code': '851',
        'chapterLabel': '2 研究方法',
        'questionsFile': os.path.join(BASE_DIR, '细胞生物学题库/第一章/questions.json'),
        'termsFile': os.path.join(BASE_DIR, '细胞生物学题库/第一章/terms.json'),
    },
}

def load_data():
    banks = {}
    for key, cfg in SUBJECTS.items():
        with open(cfg['questionsFile'], 'r', encoding='utf-8') as f:
            questions = json.load(f)
        with open(cfg['termsFile'], 'r', encoding='utf-8') as f:
            terms = json.load(f)
        choice_n = sum(1 for q in questions if q['type']=='choice')
        tf_n = sum(1 for q in questions if q['type']=='truefalse')
        banks[key] = {
            'key': key, 'name': cfg['name'], 'code': cfg['code'],
            'chapterLabel': cfg['chapterLabel'],
            'questions': questions, 'terms': terms,
            'stats': {'total':len(questions),'choice':choice_n,'truefalse':tf_n,
                      'easy':0,'mid':0,'hard':0,'terms':len(terms)}
        }
    return banks

def load_brand_image():
    brand_path = os.path.join(BASE_DIR, '生物化学题库', '新校徽.jpg')
    if os.path.exists(brand_path):
        with open(brand_path, 'rb') as f:
            return f'data:image/jpeg;base64,{base64.b64encode(f.read()).decode("ascii")}'
    return ''

def load_bg_image():
    bg_path = os.path.join(BASE_DIR, '生物化学题库', '背景图.jpg')
    if os.path.exists(bg_path):
        with open(bg_path, 'rb') as f:
            return f'data:image/jpeg;base64,{base64.b64encode(f.read()).decode("ascii")}'
    return ''

def write_html(banks):
    with open('src_css.txt', 'r', encoding='utf-8') as f:
        CSS = f.read()
    bg_src = load_bg_image()
    CSS = CSS.replace('{__BG_IMAGE__}', bg_src)
    brand_src = load_brand_image()
    with open('src_js.txt', 'r', encoding='utf-8') as f:
        JS_TEMPLATE = f.read()

    banks_js = json.dumps(banks, ensure_ascii=False, separators=(',', ':'))
    default_course = 'biochemistry'
    default_subject = 'biochemistry'
    default_bank = banks[default_subject]

    COURSES = {
        'biochemistry': {'name': '生物化学', 'code': '338', 'chapters': ['biochemistry', 'biochem_ch3', 'biochem_ch4']},
        'cellbiology': {'name': '细胞生物学', 'code': '851', 'chapters': ['cellbiology', 'cellbio_ch2']},
    }
    CHAPTER_NAMES = {
        'biochemistry': '1+2 绪论+AA简介', 'cellbiology': '1 绪论',
        'biochem_ch3': '3 pr的结构', 'biochem_ch4': '4 pr的功能', 'cellbio_ch2': '2 研究方法',
    }
    courses_js = json.dumps(COURSES, ensure_ascii=False)
    ch_names_js = json.dumps(CHAPTER_NAMES, ensure_ascii=False)

    JS = JS_TEMPLATE.replace('{__BANKS__}', banks_js)
    JS = JS.replace('{__COURSES__}', courses_js)
    JS = JS.replace('{__CH_NAMES__}', ch_names_js)
    JS = JS.replace('__COURSE__', default_course)
    KEYS = json.dumps(list(SUBJECTS.keys()), ensure_ascii=False)
    JS = JS.replace('__KEYS__', KEYS)
    JS = JS.replace('__SUBJECT__', default_subject)

    # Build HTML using string concatenation (NOT f-string - no escaping issues)
    code = str(default_bank['code'])
    name = default_bank['name']
    ch_label = default_bank['chapterLabel']

    html = '<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n'
    html += '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
    html += '<meta name="theme-color" content="#8B1A2B">\n'
    html += '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    html += '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
    html += '<title>湖南大学考研题库</title>\n<style>' + CSS + '</style>\n</head>\n<body>\n'
    html += '<div class="container">\n'
    html += '  <div class="brand">\n'
    html += '    <img class="brand-img" src="' + brand_src + '" alt="湖南大学">\n'
    html += '    <div class="brand-code" id="brandCode"><em>' + code + '</em> ' + name + '</div>\n'
    html += '    <div class="tab-bar">\n'
    html += '      <div class="tab-row" id="subjectSwitcher"></div>\n'
    html += '      <div class="tab-row" id="chapterSwitcher"></div>\n'
    html += '    </div>\n  </div>\n'
    html += '  <div class="progress-wrap" id="progWrap" style="display:none">\n'
    html += '    <div class="progress-outer"><div class="progress-inner" id="progBar" style="width:0%"></div></div>\n'
    html += '    <span class="progress-text" id="progText">0 / 0</span>\n'
    html += '    <span class="progress-tag" id="progDiff" style="display:none"></span>\n'
    html += '    <span class="progress-tag" id="progModeTag" style="display:none"></span>\n  </div>\n'
    html += '  <div id="quiz"></div>\n'
    html += '  <div class="nav-row" id="navRow" style="display:none">\n'
    html += '    <button class="btn btn-ghost btn-sm" id="btnHome">&#x1F3E0;</button>\n'
    html += '    <button class="btn btn-ghost" id="btnPrev">&#x25C0;</button>\n'
    html += '    <span class="nav-hint" id="navHint"></span>\n'
    html += '    <button class="btn btn-go" id="btnNext" disabled>&#x25B6;</button>\n  </div>\n</div>\n'
    html += '<script>\n' + JS + '\n</script>\n</body>\n</html>'

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    total_qs = sum(b['stats']['total'] for b in banks.values())
    total_terms = sum(b['stats']['terms'] for b in banks.values())
    print(f'[OK] {os.path.getsize(OUTPUT)/1024:.1f} KB | {total_qs}题 | {total_terms}名词')

if __name__ == '__main__':
    banks = load_data()
    write_html(banks)
