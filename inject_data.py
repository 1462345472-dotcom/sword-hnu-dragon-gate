"""
数据注入脚本：将30章JSON题目注入到一战成硕.html
只替换 QUESTION_BANKS 的 questions/terms/stats，不动任何UI代码
"""
import json, os, re

BASE = r'c:\Users\Lenovo\Desktop\湖南大学'
HTML_IN = os.path.join(BASE, '生物化学题库', '一战成硕.html')
HTML_OUT = os.path.join(BASE, '生物化学题库', '一战成硕.html')  # 直接写入原文件

# Step 1: Read original HTML
print('[1/4] 读取原始HTML...')
with open(HTML_IN, 'r', encoding='utf-8') as f:
    html = f.read()
html_original = html  # keep for verification

# Step 2: Find QUESTION_BANKS boundaries
print('[2/4] 定位 QUESTION_BANKS 数据块...')
start_marker = 'var QUESTION_BANKS = {\n'
end_marker = '\n};\nvar COURSES'

start_pos = html.find(start_marker)
end_pos = html.find(end_marker)

if start_pos == -1 or end_pos == -1:
    # Try alternative markers
    start_marker = 'var QUESTION_BANKS = {'
    end_marker = '};\nvar COURSES'
    start_pos = html.find(start_marker)
    end_pos = html.find(end_marker)

if start_pos == -1 or end_pos == -1:
    raise Exception(f"找不到QUESTION_BANKS边界! start={start_pos}, end={end_pos}")

# Extract the JSON part (the content between the outer braces)
inner_start = html.find('\n', start_pos) + 1  # first char after opening brace + newline
inner_content = html[inner_start:end_pos]  # the bank entries, ending before };

print(f'  数据块位置: {start_pos} - {end_pos} (共 {end_pos-start_pos} 字符)')

# Step 3: Load all JSON data and build new QUESTION_BANKS content
print('[3/4] 加载所有章节JSON并构建新数据...')

SUBJECTS = {}
# Biochemistry chapters
bio_chapters = [
    ('biochem_1_2', '1+2 绪论+AA', '第一章+第二章'),
    ('biochem_3', '3 pr的结构', '第三章'),
    ('biochem_4', '4 pr的功能', '第四章'),
    ('biochem_5', '5 pr分离纯化', '第五章'),
    ('biochem_6', '6 酶的催化', '第六章'),
    ('biochem_7', '7 酶动力学', '第七章'),
    ('biochem_8', '8 酶作用机制', '第八章'),
    ('biochem_9', '9 糖类', '第九章'),
    ('biochem_10', '10 脂质和生物膜', '第十章'),
    ('biochem_11', '11 核酸结构', '第十一章'),
    ('biochem_12', '12 核酸物化', '第十二章'),
    ('biochem_13', '13 维生素和辅酶', '第十三章'),
    ('biochem_14', '14 激素和信号转导', '第十四章'),
]
cell_chapters = [
    ('cellbio_1', '1 绪论', '第一章绪论'),
    ('cellbio_2', '2 研究方法', '第二章'),
    ('cellbio_3', '3 细胞质膜', '第三章'),
    ('cellbio_4', '4 跨膜运输', '第四章'),
    ('cellbio_5', '5 内膜系统', '第五章'),
    ('cellbio_6', '6 蛋白质分选', '第六章'),
    ('cellbio_7', '7 线粒体叶绿体', '第七章'),
    ('cellbio_8', '8 细胞骨架', '第八章'),
    ('cellbio_9', '9 细胞核染色质', '第九章'),
    ('cellbio_10', '10 核糖体', '第十章'),
    ('cellbio_11', '11 信号转导', '第十一章'),
    ('cellbio_12', '12 细胞周期', '第十二章'),
    ('cellbio_13', '13 增殖与癌细胞', '第十三章'),
    ('cellbio_14', '14 分化与干细胞', '第十四章'),
    ('cellbio_15', '15 衰老与死亡', '第十五章'),
    ('cellbio_16', '16 社会联系', '第十六章'),
]

total_q = 0
total_t = 0
bank_lines = []

for key, label, dirname in bio_chapters:
    qf = os.path.join(BASE, '生物化学题库', dirname, 'questions.json')
    tf = os.path.join(BASE, '生物化学题库', dirname, 'terms.json')
    questions = json.load(open(qf, encoding='utf-8'))
    terms = json.load(open(tf, encoding='utf-8'))

    # Normalize
    for q in questions:
        if 'tags' not in q: q['tags'] = []
        if 'difficulty' not in q: q['difficulty'] = 1
    normalized_terms = []
    for t in terms:
        if isinstance(t, list):
            normalized_terms.append({
                'id': t[0], 'name': t[1] if len(t)>1 else '',
                'definition': t[2] if len(t)>2 else '', 'chapter': key
            })
        elif isinstance(t, dict):
            if 'term' in t and 'name' not in t: t['name'] = t['term']
            if 'definition' not in t: t['definition'] = ''
            t['chapter'] = key
            normalized_terms.append(t)

    choice_n = sum(1 for q in questions if q['type'] == 'choice')
    tf_n = sum(1 for q in questions if q['type'] == 'truefalse')

    bank = {
        'key': key, 'name': '生物化学', 'code': '338',
        'chapterLabel': label,
        'questions': questions,
        'terms': normalized_terms,
        'stats': {'total': len(questions), 'choice': choice_n,
                  'truefalse': tf_n, 'terms': len(normalized_terms)}
    }
    total_q += len(questions)
    total_t += len(normalized_terms)
    bank_lines.append(f'"{key}":{json.dumps(bank, ensure_ascii=False, separators=(",", ":"))}')

for key, label, dirname in cell_chapters:
    qf = os.path.join(BASE, '细胞生物学题库', dirname, 'questions.json')
    tf = os.path.join(BASE, '细胞生物学题库', dirname, 'terms.json')
    questions = json.load(open(qf, encoding='utf-8'))
    terms = json.load(open(tf, encoding='utf-8'))

    for q in questions:
        if 'tags' not in q: q['tags'] = []
        if 'difficulty' not in q: q['difficulty'] = 1
    normalized_terms = []
    for t in terms:
        if isinstance(t, list):
            normalized_terms.append({
                'id': t[0], 'name': t[1] if len(t)>1 else '',
                'definition': t[2] if len(t)>2 else '', 'chapter': key
            })
        elif isinstance(t, dict):
            if 'term' in t and 'name' not in t: t['name'] = t['term']
            if 'definition' not in t: t['definition'] = ''
            t['chapter'] = key
            normalized_terms.append(t)

    choice_n = sum(1 for q in questions if q['type'] == 'choice')
    tf_n = sum(1 for q in questions if q['type'] == 'truefalse')

    bank = {
        'key': key, 'name': '细胞生物学', 'code': '851',
        'chapterLabel': label,
        'questions': questions,
        'terms': normalized_terms,
        'stats': {'total': len(questions), 'choice': choice_n,
                  'truefalse': tf_n, 'terms': len(normalized_terms)}
    }
    total_q += len(questions)
    total_t += len(normalized_terms)
    bank_lines.append(f'"{key}":{json.dumps(bank, ensure_ascii=False, separators=(",", ":"))}')

new_banks_content = ','.join(bank_lines)

# Step 4: Inject and save
print(f'[4/4] 注入数据... ({total_q} 题, {total_t} 术语)')
html_new = html[:inner_start] + new_banks_content + html[end_pos:]

# Verify the markers around injection point
# Check that COURSES and CHAPTER_NAMES are intact
assert 'var COURSES' in html_new, "FATAL: COURSES lost!"
assert 'var CHAPTER_NAMES' in html_new, "FATAL: CHAPTER_NAMES lost!"

# Check that the injection point looks right
check_idx = html_new.find('};\nvar COURSES')
assert check_idx > 0, "FATAL: data boundary corrupted!"

with open(HTML_OUT, 'w', encoding='utf-8') as f:
    f.write(html_new)

size_mb = os.path.getsize(HTML_OUT) / 1024 / 1024
print(f'\n===== 注入完成 =====')
print(f'输出: {HTML_OUT}')
print(f'大小: {size_mb:.1f} MB')
print(f'题目: {total_q} 题')
print(f'术语: {total_t} 条')
print(f'章节: {len(bio_chapters)} 生化 + {len(cell_chapters)} 细胞 = {len(bio_chapters)+len(cell_chapters)}')
print(f'原始备份: {HTML_IN} (未修改)')
