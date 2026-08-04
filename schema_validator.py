#!/usr/bin/env python3
"""题库数据 Schema 校验器 —— 零外部依赖，纯 Python3"""
import json
import sys

# ============================================================
# questions.json schema 约束
# ============================================================
VALID_TYPES = {'choice', 'truefalse', 'multi', 'short'}
VALID_DIFFICULTIES = {1, 2, 3}


def validate_questions(filepath):
    """校验单个 questions.json，返回违规信息列表。空列表 = 通过。"""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            questions = json.load(f)
        except json.JSONDecodeError as e:
            return ['JSON解析失败: %s' % e]

    if not isinstance(questions, list):
        return ['根元素必须是数组，当前类型: %s' % type(questions).__name__]

    ids_seen = set()

    for i, q in enumerate(questions):
        idx = q.get('id', '索引%d' % i)

        # 必填字段
        for field in ['id', 'type', 'question', 'answer', 'explanation', 'difficulty', 'tags']:
            if field not in q:
                errors.append('[#%s] 缺少必填字段: %s' % (idx, field))

        # 字段类型
        if 'id' in q and not isinstance(q['id'], int):
            errors.append('[#%s] id必须是整数，当前类型: %s' % (idx, type(q['id']).__name__))
        if 'type' in q and q['type'] not in VALID_TYPES:
            errors.append('[#%s] 无效题型: %s，合法值: %s' % (idx, q['type'], ', '.join(sorted(VALID_TYPES))))
        if 'question' in q and (not isinstance(q['question'], str) or not q['question'].strip()):
            errors.append('[#%s] question不能为空' % idx)
        if 'explanation' in q and (not isinstance(q['explanation'], str) or not q['explanation'].strip()):
            errors.append('[#%s] explanation不能为空' % idx)
        if 'difficulty' in q and q['difficulty'] not in VALID_DIFFICULTIES:
            errors.append('[#%s] difficulty必须为1-3，当前值: %s' % (idx, q['difficulty']))
        if 'tags' in q and not isinstance(q['tags'], list):
            errors.append('[#%s] tags必须是数组' % idx)

        # type 特定校验
        qtype = q.get('type', '')
        if qtype in ('choice', 'multi'):
            opts = q.get('options', {})
            if not isinstance(opts, dict) or len(opts) == 0:
                errors.append('[#%s] %s题型必须提供非空options字典' % (idx, qtype))
            else:
                for key in opts:
                    if not isinstance(key, str) or len(key) != 1 or key < 'A' or key > 'Z':
                        errors.append('[#%s] options键必须为单字母A-Z，当前: %s' % (idx, key))
                    if not isinstance(opts[key], str) or not opts[key].strip():
                        errors.append('[#%s] options[%s]值不能为空' % (idx, key))

        if qtype == 'choice':
            ans = str(q.get('answer', ''))
            opts = q.get('options', {})
            if ans and ans not in opts:
                errors.append('[#%s] choice答案"%s"不在options中(有效键: %s)' % (idx, ans, ', '.join(sorted(opts.keys()))))

        if qtype == 'truefalse':
            ans = str(q.get('answer', '')).strip().lower()
            if ans not in ('true', 'false'):
                errors.append('[#%s] TF答案必须为true/false(全小写)，当前: %s' % (idx, q.get('answer')))

        if qtype == 'multi':
            ans = str(q.get('answer', ''))
            opts = q.get('options', {})
            if not ans:
                errors.append('[#%s] multi答案不能为空' % idx)
            elif opts:
                for ch in ans:
                    if ch not in opts:
                        errors.append('[#%s] multi答案中"%s"不在options中' % (idx, ch))
            # 检查是否有重复字符
            if len(ans) != len(set(ans)):
                errors.append('[#%s] multi答案中有重复字符: %s' % (idx, ans))

        if qtype == 'short':
            ans = str(q.get('answer', ''))
            if not ans or len(ans.strip()) < 5:
                errors.append('[#%s] short答案为空或过短(<5字符)' % idx)

        # ID 唯一性
        if q.get('id') in ids_seen:
            errors.append('[#%s] 重复ID: %s' % (idx, q['id']))
        ids_seen.add(q.get('id'))

    return errors


def validate_terms(filepath):
    """校验单个 terms.json，返回违规信息列表。支持 list 和 dict 两种格式。"""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            terms = json.load(f)
        except json.JSONDecodeError as e:
            return ['JSON解析失败: %s' % e]

    if not isinstance(terms, list):
        return ['根元素必须是数组，当前类型: %s' % type(terms).__name__]

    ids_seen = set()

    for i, t in enumerate(terms):
        if isinstance(t, list):
            # 旧格式: [id, term, definition]
            if len(t) < 3:
                errors.append('[索引%d] list格式terms需至少3个元素[id, term, definition]' % i)
                continue
            tid = t[0]
            if not isinstance(tid, int):
                errors.append('[索引%d] id必须是整数，当前: %s' % (i, tid))
            if not isinstance(t[1], str) or not t[1].strip():
                errors.append('[索引%d] term不能为空' % i)
            if not isinstance(t[2], str) or not t[2].strip():
                errors.append('[索引%d] definition不能为空' % i)
        elif isinstance(t, dict):
            tid = t.get('id', i)
            for field in ['id', 'term', 'definition']:
                if field not in t:
                    errors.append('[#%s] 缺少必填字段: %s' % (tid, field))
            if 'id' in t and not isinstance(t['id'], int):
                errors.append('[#%s] id必须是整数' % tid)
            if 'term' in t and (not isinstance(t['term'], str) or not t['term'].strip()):
                errors.append('[#%s] term不能为空' % tid)
            if 'definition' in t and (not isinstance(t['definition'], str) or not t['definition'].strip()):
                errors.append('[#%s] definition不能为空' % tid)
        else:
            errors.append('[索引%d] terms元素必须是list或dict，当前类型: %s' % (i, type(t).__name__))
            continue

        if tid in ids_seen:
            errors.append('[#%s] 重复ID' % tid)
        ids_seen.add(tid)

    return errors


def validate_all_chapters(subjects):
    """
    对 build_unified.py 的 SUBJECTS 字典逐章校验。
    返回: { chapter_key: { 'questions': [errors], 'terms': [errors] } }
    """
    import os
    BASE_DIR = r'c:\Users\Lenovo\Desktop\湖南大学'
    results = {}
    for key, cfg in subjects.items():
        qf = os.path.join(BASE_DIR, cfg['questionsFile'])
        tf = os.path.join(BASE_DIR, cfg['termsFile'])
        results[key] = {
            'questionsFile': cfg['questionsFile'],
            'termsFile': cfg['termsFile'],
            'q_errors': validate_questions(qf),
            't_errors': validate_terms(tf),
        }
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python schema_validator.py <file.json>         校验单个文件')
        print('      python schema_validator.py --all               校验全部29章')
        sys.exit(0)

    if sys.argv[1] == '--all':
        from build_unified import SUBJECTS
        results = validate_all_chapters(SUBJECTS)
        total_errors = 0
        for key, r in results.items():
            label = '%s (%s)' % (key, r['questionsFile'])
            if r['q_errors'] or r['t_errors']:
                total_errors += len(r['q_errors']) + len(r['t_errors'])
                print('\n[%s]' % label)
                for e in r['q_errors']:
                    print('  Q: ' + e)
                for e in r['t_errors']:
                    print('  T: ' + e)
            else:
                print('[%s] OK (%d题 + %d术语)' % (label,
                    len(r['q_errors']), len(r['t_errors'])))  # counts via separate load
        if total_errors:
            print('\n[FAIL] 共 %d 个违规项' % total_errors)
            sys.exit(1)
        else:
            print('\n[PASS] 全部29章校验通过')
    else:
        filepath = sys.argv[1]
        if 'questions' in filepath.lower():
            errors = validate_questions(filepath)
        else:
            errors = validate_terms(filepath)
        if errors:
            for e in errors:
                print('ERROR: ' + e)
            sys.exit(1)
        else:
            print('OK: ' + filepath)
