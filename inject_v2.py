"""
安全注入脚本 v2：先构建JS → Node验证 → 通过才写入
"""
import json, os, subprocess, sys

BASE = r'c:\Users\Lenovo\Desktop\湖南大学'
HTML_PATH = os.path.join(BASE, '生物化学题库', '这次一定不要搞坏了.html')

# ========== STEP 1: Build the new QUESTION_BANKS data ==========
print('[1/4] 构建新数据...')

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

banks = {}
total_q = 0

for key, label, dirname in bio_chapters + cell_chapters:
    # Determine subject
    if key.startswith('biochem'):
        subject_dir = '生物化学题库'
        subject_name = '生物化学'
        subject_code = '338'
    else:
        subject_dir = '细胞生物学题库'
        subject_name = '细胞生物学'
        subject_code = '851'

    qf = os.path.join(BASE, subject_dir, dirname, 'questions.json')
    tf = os.path.join(BASE, subject_dir, dirname, 'terms.json')

    questions = json.load(open(qf, encoding='utf-8'))
    terms = json.load(open(tf, encoding='utf-8'))

    # Normalize questions
    for q in questions:
        if 'tags' not in q: q['tags'] = []
        if 'difficulty' not in q: q['difficulty'] = 1

    # Normalize terms
    normalized_terms = []
    for t in terms:
        if isinstance(t, list):
            normalized_terms.append({
                'id': t[0],
                'name': t[1] if len(t) > 1 else '',
                'definition': t[2] if len(t) > 2 else '',
                'chapter': key
            })
        elif isinstance(t, dict):
            if 'term' in t and 'name' not in t:
                t['name'] = t['term']
            if 'definition' not in t:
                t['definition'] = ''
            t['chapter'] = key
            normalized_terms.append(t)

    choice_n = sum(1 for q in questions if q['type'] == 'choice')
    tf_n = sum(1 for q in questions if q['type'] == 'truefalse')

    banks[key] = {
        'key': key,
        'name': subject_name,
        'code': subject_code,
        'chapterLabel': label,
        'questions': questions,
        'terms': normalized_terms,
        'stats': {
            'total': len(questions),
            'choice': choice_n,
            'truefalse': tf_n,
            'terms': len(normalized_terms)
        }
    }
    total_q += len(questions)

# Serialize to JSON
banks_json = json.dumps(banks, ensure_ascii=False, separators=(',', ':'))

# ========== STEP 2: Build JS and validate with Node ==========
print(f'[2/4] 构建JS并Node验证... ({total_q} 题)')

# Match the ORIGINAL format: var QUESTION_BANKS = {<data>};
js_code = f'var QUESTION_BANKS = {banks_json};'

with open('_validate.js', 'w', encoding='utf-8') as f:
    f.write(js_code)

# Test with Node.js
result = subprocess.run(
    ['node', '-e',
     "const fs=require('fs');const js=fs.readFileSync('_validate.js','utf-8');"
     "new Function(js);"
     "const QB=new Function(js+';return QUESTION_BANKS;')();"
     "const keys=Object.keys(QB);"
     "let totalQ=0,totalT=0;"
     "for(const k of keys){totalQ+=QB[k].stats.total;totalT+=QB[k].stats.terms;}"
     "console.log('VALID:'+keys.length+' chapters,'+totalQ+' questions,'+totalT+' terms');"],
    capture_output=True, text=True, timeout=30
)

if result.returncode != 0:
    print(f'\n!!! NODE VALIDATION FAILED !!!')
    print(f'STDERR: {result.stderr}')
    print(f'STDOUT: {result.stdout}')
    print('NOT writing to HTML. Original file is SAFE.')
    sys.exit(1)

print(f'  Node: {result.stdout.strip()}')

# ========== STEP 3: Inject into HTML ==========
print('[3/4] Node验证通过，注入HTML...')

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# Find the exact boundaries
qb_start = html.find('var QUESTION_BANKS = {')
courses_start = html.find('var COURSES')

# Find content boundaries
content_start = qb_start + len('var QUESTION_BANKS = ') + 1  # skip past '{'
content_end = html.rfind('}};', 0, courses_start)  # position of }}; before COURSES

if content_start < 0 or content_end < 0:
    print('ERROR: Cannot find boundaries!')
    sys.exit(1)

# Reconstruct: keep the var QUESTION_BANKS = { prefix, insert new data, keep suffix
# The suffix is: }};\nvar COURSES... (everything from content_end)
html_new = html[:content_start] + banks_json + html[content_end:]

# Verify critical markers still exist
assert 'var COURSES' in html_new, "COURSES lost!"
assert 'var CHAPTER_NAMES' in html_new, "CHAPTER_NAMES lost!"
assert html_new.count('var COURSES') == 1, "COURSES count changed!"
assert 'var S =' in html_new, "Global state lost!"

# ========== STEP 4: Write and verify ==========
with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html_new)

print(f'[4/4] 写入完成，验证...')
size_mb = os.path.getsize(HTML_PATH) / 1024 / 1024

# Final verification: can still parse the data back
data_start = html_new.find('var QUESTION_BANKS = {') + len('var QUESTION_BANKS = ')
data_end_verify = html_new.find('}};\nvar COURSES')
verify_json = '{' + html_new[data_start:data_end_verify] + '}}'
try:
    verify_data = json.loads(verify_json)
    v_total = sum(b['stats']['total'] for b in verify_data.values())
    assert v_total == total_q
    print(f'  文件: {size_mb:.1f} MB')
    print(f'  题目: {total_q} 题')
    print(f'  章节: {len(verify_data)} 章')
    print(f'  COURSES: OK, CHAPTER_NAMES: OK, S: OK')
    print(f'\n===== 注入成功 =====')
except Exception as e:
    print(f'  FINAL VERIFY FAILED: {e}')
    sys.exit(1)
