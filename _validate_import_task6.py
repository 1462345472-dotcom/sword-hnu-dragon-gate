# _validate_import_task6.py — 临时验证脚本(不提交),Task 6 导入后结构验证
# -*- coding: utf-8 -*-
import json, re, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')

PATH = "生物化学题库/湖南大学题库系统-剑指湖大一战成硕.html"
# 修复轮基线 = Task 6 提交后(已含 biochem_15 对象 + CHAPTER_NAMES)的版本
BAK = ".superpowers/sdd/2026-08-07-biochem-15-36-import/html_after_task6.html.bak"
PRE_FP = "96e3aad4f8cf0d80"

ok = lambda c: "PASS" if c else "FAIL"
results = []

def check(name, cond, detail=""):
    results.append((name, cond, detail))
    print(f"[{ok(cond)}] {name}" + (f"  {detail}" if detail else ""))

# ---- 1. strict 读取(确认文件无损可解码) ----
html = open(PATH, encoding="utf-8").read()  # strict
check("strict UTF-8 解码无损", True, f"文本长度 {len(html)}")

# ---- 2. BOM 与换行 ----
data = open(PATH, "rb").read()
check("BOM 保留", data[:3] == b"\xef\xbb\xbf", repr(data[:3]))
crlf, lf = data.count(b"\r\n"), data.count(b"\n")
check("换行仍为全 CRLF(无裸 LF)", crlf == lf, f"CRLF={crlf} LF={lf}")
check("无裸 CR", data.count(b"\r") == crlf, f"bareCR={data.count(chr(13).encode()) - crlf}")

# ---- 3. 解析 QUESTION_BANKS 顶层字典 ----
m = re.search(r"var QUESTION_BANKS\s*=\s*\{", html)
bra = m.start() + m.group(0).rfind("{")
obj, endpos = json.JSONDecoder().raw_decode(html, bra)
check("顶层字典整体可解析", True, f"end={bra+endpos} filelen={len(html)}")
keys = list(obj.keys())
check("章节对象数 == 30", len(keys) == 30, f"实际 {len(keys)}")

# ---- 4. 顺序:biochem_15 紧跟在 biochem_14 之后 ----
i14 = keys.index("biochem_14"); i15 = keys.index("biochem_15")
check("biochem_15 在 biochem_14 之后", i15 == i14 + 1,
      f"biochem_14@{i14} biochem_15@{i15} 顺序={keys[i14:i15+2]}")

# ---- 5. 总数与 stats 互证(全部 30 对象) ----
total_q = sum(len(v["questions"]) for v in obj.values())
total_t = sum(len(v["terms"]) for v in obj.values())
check("总题数 == 2549+77 == 2626", total_q == 2626, f"实际 {total_q}")
check("总术语数 == 516+18 == 534", total_t == 534, f"实际 {total_t}")
bad = 0
for k, v in obj.items():
    qs, ts, st = v["questions"], v["terms"], v.get("stats", {})
    if st.get("total") != len(qs) or st.get("terms") != len(ts):
        bad += 1
        print("  MISMATCH", k, st.get("total"), len(qs), st.get("terms"), len(ts))
check("30 对象 stats 全部互证", bad == 0, f"违规 {bad}")

# ---- 6. biochem_15 内部细节 ----
b15 = obj["biochem_15"]
from collections import Counter
q15, t15 = b15["questions"], b15["terms"]
types = Counter(x.get("type", "") for x in q15)
check("biochem_15 题数 == 77", len(q15) == 77, f"实际 {len(q15)}")
check("biochem_15 术语数 == 18", len(t15) == 18, f"实际 {len(t15)}")
check("biochem_15 题型分布 41/16/12/8",
      types["choice"] == 41 and types["truefalse"] == 16 and types["multi"] == 12 and types["short"] == 8,
      f"实际 {dict(types)}")
st15 = b15["stats"]
check("biochem_15 stats.total == 77", st15["total"] == 77)
check("biochem_15 stats.terms == 18", st15["terms"] == 18)
check("biochem_15 key/chapterLabel/code",
      b15["key"] == "biochem_15" and b15["chapterLabel"] == "15 新陈代谢总论" and b15["code"] == "338")
check("biochem_15 terms 均带 chapter=biochem_15",
      all(t.get("chapter") == "biochem_15" for t in t15))

# ---- 7. 字节级对比(修复轮):基线=Task6后版本,仅允许 COURSES 一处插入 ----
orig = open(BAK, "rb").read()
new = open(PATH, "rb").read()
c_anchor = b'"biochem_14"]'
assert orig.count(c_anchor) == 1, f"COURSES 锚点不唯一: {orig.count(c_anchor)}"
z = orig.index(c_anchor)   # 原文件中 "biochem_14" 起始(该 12B 保留,插入发生在其后)
c_keep = b'"biochem_14"'   # 保留的 12B
c_ins = b',"biochem_15"'   # 插入的 13B
seg_ok = True
seg_ok &= new[:z] == orig[:z]                          # 插入点之前零改动
seg_ok &= new[z:z + len(c_keep)] == c_keep             # "biochem_14" 原样保留
seg_ok &= new[z + len(c_keep):z + len(c_keep) + len(c_ins)] == c_ins  # COURSES 插入段逐字节一致
seg_ok &= new[z + len(c_keep) + len(c_ins):] == orig[z + len(c_keep):]  # 其后零改动
check("字节级:仅 COURSES 一处插入、其余全文件零改动", seg_ok,
      f"增量={len(new)-len(orig)} COURSES段={len(c_ins)}")

# ---- 7b. Task 6 两处插入(章节对象+CHAPTER_NAMES)仍完好(对照导入前基线) ----
orig6 = open(".superpowers/sdd/2026-08-07-biochem-15-36-import/html_before_import.html.bak", "rb").read()
anchor6 = b',"cellbio_8":{"key":"cellbio_8"'
assert orig6.count(anchor6) == 1
x6 = orig6.index(anchor6)
questions = json.load(open("生物化学题库/第十五章/questions.json", encoding="utf-8"))
terms = json.load(open("生物化学题库/第十五章/terms.json", encoding="utf-8"))
for t in terms:
    t["chapter"] = "biochem_15"
import inject_chapter as inj
obj_text = inj.build_chapter_obj("biochem_15", "15 新陈代谢总论", questions, terms)
ins6 = (',"biochem_15":' + obj_text).encode("utf-8").replace(b"\n", b"\r\n")
cn_a6 = b"CHAPTER_NAMES = {"
cn6 = orig6.index(cn_a6)
cn_ins6 = '"biochem_15":"第十五章 新陈代谢总论",'.encode("utf-8")
# 文件字节顺序:QUESTION_BANKS → COURSES → CHAPTER_NAMES,故 CHAPTER_NAMES 需加
# 章节段偏移 + COURSES 段偏移(c_ins 已在其前定义)
cn_new = cn6 + len(ins6) + len(c_ins)
seg6 = (new[x6:x6 + len(ins6)] == ins6                          # 章节对象插入段逐字节一致
        and new[cn_new:cn_new + len(cn_a6)] == cn_a6             # CHAPTER_NAMES 声明原样
        and new[cn_new + len(cn_a6):
                cn_new + len(cn_a6) + len(cn_ins6)] == cn_ins6)  # CHAPTER_NAMES 插入段
check("Task 6 两处插入(章节对象+CHAPTER_NAMES)仍完好", seg6)

# ---- 7c. COURSES 结构检查 ----
m_courses = re.search(r"COURSES\s*=\s*\{", html)
cobj, _ = json.JSONDecoder().raw_decode(html, m_courses.start() + m_courses.group(0).rfind("{"))
ch = cobj["biochemistry"]["chapters"]
check("COURSES.biochemistry.chapters 含 biochem_15", "biochem_15" in ch)
check("COURSES.biochemistry.chapters 数量 == 14", len(ch) == 14, f"实际 {len(ch)}")
check("COURSES.chapters 无重复且 biochem_15 紧接 biochem_14",
      len(set(ch)) == len(ch) and ch[ch.index("biochem_15") - 1] == "biochem_14",
      f"biochem_15 前驱 = {ch[ch.index('biochem_15') - 1] if 'biochem_15' in ch else 'N/A'}")
check("COURSES.cellbiology 未受影响", len(cobj["cellbiology"]["chapters"]) == 16)

# ---- 8. CHAPTER_NAMES 同步 ----
cn = re.search(r"CHAPTER_NAMES\s*=\s*\{([^}]*)\}", html).group(1)
check("CHAPTER_NAMES 含 biochem_15 条目",
      '"biochem_15":"第十五章 新陈代谢总论"' in cn)
check("CHAPTER_NAMES 条目数 == 30", len(re.findall(r'"[\w_]+":', cn)) == 30,
      f"实际 {len(re.findall(chr(34)+'[\\w_]+'+chr(34)+':', cn))}")

# ---- 9. CSS 指纹对比 ----
styles = "".join(re.findall(r"<style[^>]*>.*?</style>", html, re.S))
fp = hashlib.sha256(styles.encode("utf-8")).hexdigest()[:16]
check("CSS 指纹与导入前一致", fp == PRE_FP, f"导入后 {fp}")

# ---- 汇总 ----
fails = [r for r in results if not r[1]]
print()
print("=" * 50)
print(f"验证总计: {len(results)} 项, 失败 {len(fails)} 项")
if fails:
    print("FAILED:", [r[0] for r in fails])
    sys.exit(1)
print("ALL PASS")
