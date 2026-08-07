# 生化 15-36 章出题导入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把生物化学第 15~36 章(22 章)扫描版课件,通过"分色 OCR → 考纲对照 → 按 12 条标准出题 → 校验去重 → 导入臻至版 HTML"的流水线逐步入库,试点从第十五章开始。

**Architecture:** 复用现有智谱 GLM-4V-Flash OCR 管线(ocr_scan_pdf.py),新增像素级红/黑分色功能;出题采用"识别文本 + 考纲考点清单 → 逐考点出题"的 AI 生成流程(人工抽审关卡);导入直接向臻至版 HTML 的章节对象字典插入新对象(不动任何其他内容),并全程以 CSS 指纹与结构核对做安全网。

**Tech Stack:** Python 3.12(PyMuPDF 1.28、PIL、requests)、智谱 GLM-4V-Flash API、臻至版单文件 HTML(JS 对象字面量数据)、schema_validator.py(已有)。

## Global Constraints

- 只改臻至版 HTML 的数据对象,禁止改动 CSS、HTML 结构、已有章节对象(UI 零容忍)
- 新题与 HTML 已有 2549 题去重,重复题剔除或改写
- 考纲考点全覆盖是宗旨;优先级:考纲 > 红色重点 > 黑色正文
- 名词解释 definition 长度 30-80 字;简答答案 ①②③ 分点;不出时间/年代类选择题
- 题目字段:choice/truefalse/multi/short 四种 type;多选题选项跨 ≥2 知识点
- 不自动备份(用户自备);CSS 指纹检测仅做对比,不复制文件
- 每章完成后需用户抽审(每种题型 1-2 道)才可导入
- **基本代谢章节(第十五~二十八章)是全部章节中最重要部分(用户强调"最最最重要")**:题量按篇幅线性计算后再 ×1.3~1.5 上浮;难度 2-3 的题占比更高;考纲代谢考点逐条深度覆盖(一个代谢考点不许浅尝辄止);红字重点考点全出;出题角度扩充(定义/特点/机制/过程/酶与调控/生理意义/比较/计算/联系综合);抽审更严格(用户对代谢章节抽审每种题型 2-3 道)

---

### Task 1: 分色 OCR 工具 `color_split_ocr.py`

**Files:**
- Create: `color_split_ocr.py`
- Create: `test_color_split.py`

**Interfaces:**
- Consumes: 智谱 API Key(读 `ocr_config.json` 或环境变量 `ZHIPU_API_KEY`,复用 ocr_scan_pdf.py 的 `load_api_key` 逻辑)
- Produces: `split_pixels(b64_png) -> (red_b64, black_b64)`(红字图/黑字图 base64)、`ocr_image(api_key, b64_png) -> str`(复用 ocr_scan_pdf.py 同名函数逻辑)、CLI:`python color_split_ocr.py <pdf|png> <输出.txt> [--start N] [--end N] [--dpi 300]`

- [ ] **Step 1: 写失败测试(合成红黑文字图,验证分色)**

```python
# test_color_split.py
# -*- coding: utf-8 -*-
import sys, base64, io
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw
from color_split_ocr import split_pixels

def make_test_png():
    img = Image.new('RGB', (600, 200), (255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((20, 30), 'RED TEXT', fill=(200, 30, 30))
    d.text((20, 120), 'BLACK TEXT', fill=(20, 20, 20))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('ascii')

def test_split():
    red_b64, black_b64 = split_pixels(make_test_png())
    assert red_b64 and black_b64
    # 红图不应含黑色像素,黑图不应含红色像素
    for b64, expect_red in ((red_b64, True), (black_b64, False)):
        img = Image.open(io.BytesIO(base64.b64decode(b64))).convert('RGB')
        pixels = list(img.getdata())
        red_count = sum(1 for r, g, b in pixels if r > 150 and g < 90 and b < 90)
        black_count = sum(1 for r, g, b in pixels if r < 60 and g < 60 and b < 60)
        if expect_red:
            assert red_count > 0 and black_count == 0, '红图含黑色像素或缺失红色'
        else:
            assert black_count > 0 and red_count == 0, '黑图含红色像素或缺失黑色'
    print('test_split PASS')

if __name__ == '__main__':
    test_split()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python test_color_split.py`
Expected: FAIL(ImportError: color_split_ocr 不存在)

- [ ] **Step 3: 实现分色函数与 CLI 主流程**

```python
# color_split_ocr.py
# -*- coding: utf-8 -*-
"""扫描版 PDF/图片 → 红字/黑字分色 OCR(智谱 GLM-4V-Flash)
用法: python color_split_ocr.py <输入> [输出.txt] [--start N] [--end N] [--dpi 300]
"""
import sys, os, json, time, base64, argparse, io
import fitz
import requests
from PIL import Image, ImageDraw

ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
OCR_MODEL = "glm-4v-flash"

def load_api_key():
    key = os.environ.get("ZHIPU_API_KEY", "")
    if not key:
        cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_config.json")
        if os.path.exists(cfg):
            key = json.load(open(cfg, encoding="utf-8")).get("zhipu_api_key", "")
    if not key:
        sys.exit("错误: 未找到智谱 API Key(ocr_config.json 或 ZHIPU_API_KEY)")
    return key

def split_pixels(b64_png):
    """按像素把图片拆成 红字图 和 黑字图 两份 base64。"""
    img = Image.open(io.BytesIO(base64.b64decode(b64_png))).convert('RGB')
    w, h = img.size
    px = img.load()
    red_img = Image.new('RGB', (w, h), (255, 255, 255))
    black_img = Image.new('RGB', (w, h), (255, 255, 255))
    rp, bp = red_img.load(), black_img.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if r > 150 and g < 90 and b < 90:
                rp[x, y] = (0, 0, 0)  # 红色像素 → 黑字图黑字(便于 OCR)
            elif r < 90 and g < 90 and b < 90:
                bp[x, y] = (0, 0, 0)  # 黑色像素 → 黑字图黑字
    def to_b64(img):
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return base64.b64encode(buf.getvalue()).decode('ascii')
    return to_b64(red_img), to_b64(black_img)

def ocr_image(api_key, b64_png, prompt=None):
    prompt = prompt or "请完整识别这张图片中的全部文字内容,保持原有排版顺序,逐行输出。不要添加任何解释。"
    payload = {
        "model": OCR_MODEL,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_png}"}},
        ]}],
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(4):
        try:
            resp = requests.post(ZHIPU_BASE_URL, headers=headers, json=payload, timeout=120)
            if resp.status_code == 429:
                time.sleep(10 * (attempt + 1)); continue
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"    [重试 {attempt+1}/4] {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return "[识别失败]"

def render_page_b64(page, dpi=300):
    mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return base64.b64encode(pix.tobytes("png")).decode("ascii")

def main():
    ap = argparse.ArgumentParser(description="扫描版 → 红/黑分色 OCR")
    ap.add_argument("input"); ap.add_argument("output", nargs="?", default=None)
    ap.add_argument("--start", type=int, default=1); ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--dpi", type=int, default=300)
    args = ap.parse_args()
    if not os.path.exists(args.input): sys.exit(f"文件不存在: {args.input}")
    api_key = load_api_key()
    doc = fitz.open(args.input)
    total = doc.page_count
    end = min(total, args.end or total)
    out = args.output or (os.path.splitext(args.input)[0] + "_分色.txt")
    results = []
    for i in range(args.start - 1, end):
        print(f"[{i+1}/{end}] 渲染+分色 ...", flush=True)
        b64 = render_page_b64(doc[i], args.dpi)
        red_b64, black_b64 = split_pixels(b64)
        print(f"[{i+1}/{end}] OCR 红色重点 ...", flush=True)
        red_text = ocr_image(api_key, red_b64, "识别图片中的全部文字,逐行输出,不要解释。")
        print(f"[{i+1}/{end}] OCR 黑色正文 ...", flush=True)
        black_text = ocr_image(api_key, black_b64, "识别图片中的全部文字,逐行输出,不要解释。")
        results.append(f"===== 第 {i+1} 页 =====\n【红色·重点】\n{red_text}\n【黑色·正文】\n{black_text}\n")
        print(f"[{i+1}/{end}] 完成(红{len(red_text)}字/黑{len(black_text)}字)", flush=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"完成 → {out}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python test_color_split.py`
Expected: PASS(test_split PASS)

- [ ] **Step 5: 提交**

```bash
git add color_split_ocr.py test_color_split.py
git commit -m "feat: 分色OCR工具 — 扫描页红字/黑字像素分离后分别识别"
```

---

### Task 2: 考纲考点提取器 `extract_syllabus.py`

**Files:**
- Create: `extract_syllabus.py`
- Create: `test_extract_syllabus.py`

**Interfaces:**
- Consumes: `338生物化学考纲_识别全文.txt`(已识别,5 页)
- Produces: `extract_syllabus_points(text, chapter_hint) -> list[dict]`,每项 `{"point": str, "source": "考纲", "chapter_hint": str}`;CLI 输出 `docs/superpowers/specs/考纲考点清单.json`

- [ ] **Step 1: 写失败测试**

```python
# test_extract_syllabus.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from extract_syllabus import extract_syllabus_points

def test_extract():
    text = "二、考试内容及范围\n9.糖的分解代谢和合成代谢\n(1) 糖的代谢途径\n(2) 糖的无氧分解"
    pts = extract_syllabus_points(text, "糖代谢")
    assert any("代谢途径" in p["point"] for p in pts), "未提取出考点"
    assert all(p["source"] == "考纲" for p in pts)
    print('test_extract PASS')

if __name__ == '__main__':
    test_extract()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python test_extract_syllabus.py`
Expected: FAIL(ImportError)

- [ ] **Step 3: 实现考点提取**

```python
# extract_syllabus.py
# -*- coding: utf-8 -*-
"""从考纲识别文本中提取结构化考点清单(按章节条目拆分,保留层级)。"""
import re, json, sys

def extract_syllabus_points(text, chapter_hint=""):
    """把考纲文本按 数字编号条目 拆成考点列表。
    每项: {"point": 原文条目, "source": "考纲", "chapter_hint": chapter_hint}"""
    points = []
    for line in text.splitlines():
        line = line.strip()
        # 匹配形如 "9.糖的分解代谢和合成代谢" 或 "(1) 糖的代谢途径" 的条目
        m = re.match(r'^\(?(\d{1,2})\)?[.、]\s*(.+)$', line)
        if m and len(m.group(2)) >= 2:
            points.append({"point": m.group(2).strip(), "source": "考纲", "chapter_hint": chapter_hint})
    return points

def main():
    src = "338生物化学考纲_识别全文.txt"
    text = open(src, encoding="utf-8").read()
    pts = extract_syllabus_points(text)
    with open("docs/superpowers/specs/考纲考点清单.json", "w", encoding="utf-8") as f:
        json.dump(pts, f, ensure_ascii=False, indent=2)
    print(f"提取 {len(pts)} 条考点 → docs/superpowers/specs/考纲考点清单.json")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python test_extract_syllabus.py`
Expected: PASS

- [ ] **Step 5: 运行并人工核对考点数量**

Run: `python extract_syllabus.py`
Expected: 输出考点数(考纲 5 页约 30-60 条),人工抽查关键考点(如"新陈代谢""糖代谢"条目)在清单中

- [ ] **Step 6: 提交**

```bash
git add extract_syllabus.py test_extract_syllabus.py docs/superpowers/specs/考纲考点清单.json
git commit -m "feat: 考纲考点提取器 + 考点清单(考纲全覆盖对照基线)"
```

---

### Task 3: 第十五章分色 OCR

**Files:**
- Run: `color_split_ocr.py` 处理 `生物化学题库/第十五章/第十五章 新陈代谢总论.pdf`
- Create: `生物化学题库/第十五章/第十五章_分色.txt`

**Interfaces:**
- Consumes: Task 1 的 `color_split_ocr.py`
- Produces: `生物化学题库/第十五章/第十五章_分色.txt`(每页含【红色·重点】【黑色·正文】两段)

- [ ] **Step 1: 确认 PDF 存在并统计页数**

Run: `python -c "import fitz; d=fitz.open('生物化学题库/第十五章/第十五章 新陈代谢总论.pdf'); print('页数:', d.page_count)"`
Expected: 输出页数(预计 10-30 页)

- [ ] **Step 2: 运行分色 OCR(全部页)**

Run: `python color_split_ocr.py "生物化学题库/第十五章/第十五章 新陈代谢总论.pdf" "生物化学题库/第十五章/第十五章_分色.txt" --dpi 300`
Expected: 每页输出"红X字/黑X字",全部完成

- [ ] **Step 3: 读取结果,检查识别质量**

Run: 读 `生物化学题库/第十五章/第十五章_分色.txt` 前 2 页
Expected: 红/黑两段文字可读,专业术语基本正确;若红字为空,检查 PDF 是否真含红字(用 PIL 统计该页红色像素占比)

- [ ] **Step 4: 提交识别文本**

```bash
git add 生物化学题库/第十五章/第十五章_分色.txt
git commit -m "data: 第十五章分色OCR完成(红字重点+黑字正文)"
```

---

### Task 4: 第十五章出题(生成 questions.json + terms.json)

**Files:**
- Create: `生物化学题库/第十五章/questions.json`
- Create: `生物化学题库/第十五章/terms.json`
- Create: `生物化学题库/第十五章/出题报告.md`(考点覆盖打勾 + 985 真题参照说明 + 抽审样题)

**Interfaces:**
- Consumes: Task 2 的考点清单、Task 3 的分色文本
- Produces: 与 1-14 章完全同构的 `questions.json`(list of dict)与 `terms.json`(list of dict)

- [ ] **Step 1: 逐段阅读分色文本,提炼本章考点池**

按"考纲条目(宗旨) > 红字重点 > 黑字正文"顺序,整理该章考点清单,标注来源(考纲/红/正文),先呈给用户过目

- [ ] **Step 2: 按 12 条标准逐考点出题**

约束执行细则(每条题必须满足):
- choice/truefalse 属"全部刷题";multi 属"多选专项";short 属"简答模板";名词解释进 terms.json
- 多选题选项跨 ≥2 知识点;简答答案 ①②③ 分点;名解 definition 30-80 字
- 不出时间/年代类选择题;难度取 1-3(难度 3 留给综合/红字考点)
- 题量:按篇幅线性(第十五章篇幅与 1-14 章平均对齐,预计 60-110 题)
- 出题风格参照 985 高校真题(设问角度、选项设计)

- [ ] **Step 3: 组装标准 JSON(字段与 1-14 章一致)**

```json
{"id":1,"type":"choice","question":"…","options":{"A":"…","B":"…","C":"…","D":"…"},"answer":"B","explanation":"…","difficulty":2,"tags":[],"topic":"考点名"}
{"id":1,"term":"…","name":"…","definition":"…","chapter":"biochem_15"}
```

- [ ] **Step 4: 写 `出题报告.md` 并提交**

报告含:考点覆盖打勾表(考纲条目 → 是否有题)、红字考点清单、985 真题参照说明、每种题型抽审样例 2-3 道

- [ ] **Step 5: 用户抽审**

呈上 `出题报告.md`,用户对每种题型抽看 1-2 道,认可后进入 Task 5;不认可则按反馈修改后重审
- [ ] **Step 6: 提交**

```bash
git add 生物化学题库/第十五章/questions.json 生物化学题库/第十五章/terms.json 生物化学题库/第十五章/出题报告.md
git commit -m "data: 第十五章出题完成(待校验导入)"
```

---

### Task 5: 数据校验与去重

**Files:**
- Run: `schema_validator.py`(已有)
- Create: `dedup_check.py`
- Create: `test_dedup_check.py`

**Interfaces:**
- Consumes: Task 4 的 questions.json、臻至版 HTML
- Produces: `dedup_check(questions, existing_texts) -> list[str]`(重复题目列表);CLI 输出校验报告

- [ ] **Step 1: 写失败测试(重复检测)**

```python
# test_dedup_check.py
# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
from dedup_check import dedup_check

def test_dedup():
    new = [{"question": "三羧酸循环的限速酶是？", "id": 1},
           {"question": "糖酵解的最终产物是？", "id": 2}]
    existing = ["三羧酸循环的限速酶是？", "完全无关的题"]
    dups = dedup_check(new, existing)
    assert len(dups) == 1 and dups[0]["id"] == 1, f"重复检测失败: {dups}"
    print('test_dedup PASS')

if __name__ == '__main__':
    test_dedup()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python test_dedup_check.py`
Expected: FAIL(ImportError)

- [ ] **Step 3: 实现去重(题干归一化相似度)**

```python
# dedup_check.py
# -*- coding: utf-8 -*-
"""新题与已有题去重:题干去空白/标点后精确匹配 + 前 12 字前缀匹配。"""
import re

def normalize(q):
    return re.sub(r'[\s，。？！、,.:："“”\'()（）【】]', '', q or '')

def dedup_check(questions, existing_texts):
    norm_existing = set(normalize(t) for t in existing_texts)
    prefixes = set(n[:12] for n in norm_existing if len(n) >= 8)
    dups = []
    for q in questions:
        n = normalize(q.get("question", ""))
        if not n: continue
        if n in norm_existing or n[:12] in prefixes:
            dups.append(q)
    return dups

def main():
    import json, re as _re
    new = json.load(open("生物化学题库/第十五章/questions.json", encoding="utf-8"))
    html = open("生物化学题库/湖南大学题库系统-臻至版.html", encoding="utf-8", errors="ignore").read()
    existing = _re.findall(r'"question":"((?:[^"\\]|\\.)*)"', html)
    dups = dedup_check(new, existing)
    print(f"已有题干 {len(existing)} 条, 新题 {len(new)} 条, 重复 {len(dups)} 条")
    for d in dups: print("重复:", d.get("question", "")[:40])

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python test_dedup_check.py`
Expected: PASS

- [ ] **Step 5: 运行 schema 校验 + 去重**

Run: `python schema_validator.py 生物化学题库/第十五章/questions.json`(如脚本接受路径参数;否则用其既有调用方式)
Expected: 0 违规
Run: `python dedup_check.py`
Expected: 重复 0 条(若有重复:改写题干后重跑)

- [ ] **Step 6: 提交**

```bash
git add dedup_check.py test_dedup_check.py
git commit -m "feat: 去重检测脚本 + 第十五章数据校验通过"
```

---

### Task 6: 导入臻至版 HTML(插入 biochem_15 对象)

**Files:**
- Modify: `生物化学题库/湖南大学题库系统-臻至版.html`
- Create: `inject_chapter.py`
- Create: `test_inject_chapter.py`

**Interfaces:**
- Consumes: Task 4 的 questions.json/terms.json、Task 5 通过的数据
- Produces: `build_chapter_obj(chapter_key, label, questions, terms) -> str`(生成 JSON 文本)、`inject(html, obj_text, after_key="biochem_14") -> str`(插入并返回新 HTML)

- [ ] **Step 1: 写失败测试(插入逻辑)**

```python
# test_inject_chapter.py
# -*- coding: utf-8 -*-
import sys, json; sys.stdout.reconfigure(encoding='utf-8')
from inject_chapter import build_chapter_obj, inject

def test_inject():
    html = '{"biochem_14":{"key":"biochem_14","questions":[],"terms":[],"stats":{}},"cellbio_1":{}}'
    obj = build_chapter_obj("biochem_15", "15 新陈代谢总论",
                            [{"id":1,"type":"choice","question":"q?"}], [])
    out = inject(html, obj, after_key="biochem_14")
    assert '"biochem_15"' in out, "未插入 biochem_15"
    assert out.index('"biochem_15"') > out.index('"biochem_14"') and out.index('"biochem_15"') < out.index('"cellbio_1"'), "插入位置错误"
    print('test_inject PASS')

if __name__ == '__main__':
    test_inject()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python test_inject_chapter.py`
Expected: FAIL(ImportError)

- [ ] **Step 3: 实现插入脚本**

```python
# inject_chapter.py
# -*- coding: utf-8 -*-
"""把新章节数据对象插入臻至版 HTML 的章节字典(biochem_14 之后)。
关键安全点:只插入一个对象;用 JSONDecoder.raw_decode 精确定位插入点。"""
import json, sys, re

def build_chapter_obj(chapter_key, label, questions, terms):
    qty = {"choice": 0, "truefalse": 0, "multi": 0, "short": 0}
    for q in questions:
        qty[q.get("type", "")] = qty.get(q.get("type", ""), 0) + 1
    stats = {"total": len(questions), **qty, "terms": len(terms)}
    obj = {
        "key": chapter_key, "name": "生物化学", "code": "338",
        "chapterLabel": label, "questions": questions,
        "terms": terms, "stats": stats,
    }
    return json.dumps(obj, ensure_ascii=False, indent=1)

def inject(html, obj_text, after_key):
    """在 after_key 对象结束后插入 ,"key":{...};返回新 html"""
    dec = json.JSONDecoder()
    m = re.search(r'"' + re.escape(after_key) + r'"\s*:\s*\{', html)
    if not m:
        raise ValueError(f"未找到章节 {after_key}")
    _, endpos = dec.raw_decode(html[m.start() + m.group(0).rfind('{'):])
    insert_at = m.start() + m.group(0).rfind('{') + endpos
    return html[:insert_at] + "," + obj_text + html[insert_at:]

def main():
    key = "biochem_15"
    label = "15 新陈代谢总论"
    questions = json.load(open("生物化学题库/第十五章/questions.json", encoding="utf-8"))
    terms = json.load(open("生物化学题库/第十五章/terms.json", encoding="utf-8"))
    for t in terms:
        t["chapter"] = key
    obj_text = build_chapter_obj(key, label, questions, terms)
    path = "生物化学题库/湖南大学题库系统-臻至版.html"
    html = open(path, encoding="utf-8", errors="ignore").read()
    new_html = inject(html, obj_text, after_key="biochem_14")
    # CHAPTER_NAMES 同步
    m = re.search(r'CHAPTER_NAMES\s*=\s*\{', new_html)
    if m:
        new_html = new_html[:m.end()] + '"' + key + '":"第十五章 新陈代谢总论",' + new_html[m.end():]
    open(path, "w", encoding="utf-8").write(new_html)
    print(f"已插入 {key}({len(questions)} 题, {len(terms)} 术语)")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python test_inject_chapter.py`
Expected: PASS

- [ ] **Step 5: 备份确认 + 记录导入前 CSS 指纹**

Run: `python -c "
import re, hashlib, sys
sys.stdout.reconfigure(encoding='utf-8')
html = open('生物化学题库/湖南大学题库系统-臻至版.html', encoding='utf-8', errors='ignore').read()
styles = ''.join(re.findall(r'<style[^>]*>.*?</style>', html, re.S))
print('导入前 CSS 指纹:', hashlib.sha256(styles.encode('utf-8')).hexdigest()[:16])
"` 并将输出记入 `生物化学题库/第十五章/出题报告.md`
Expected: 输出 16 位指纹

- [ ] **Step 6: 执行导入并验证结构**

Run: `python inject_chapter.py`
Expected: 输出"已插入 biochem_15(N 题, M 术语)"
Run: 重新解析全部章节对象,验证 30 个对象、数字与 stats 互证(复用核对脚本口径)
Expected: 30 个对象,总数 = 2549+N 题, 516+M 术语,biochem_15 数字正确

- [ ] **Step 7: 提交**

```bash
git add 生物化学题库/湖南大学题库系统-臻至版.html inject_chapter.py test_inject_chapter.py
git commit -m "feat: 第十五章数据导入臻至版(30章节对象,数字互证通过)"
```

---

### Task 7: UI 指纹验证与功能抽查

**Files:**
- Run: 指纹对比 + 浏览器打开臻至版 HTML

**Interfaces:**
- Consumes: Task 6 导入后的 HTML、Task 6 Step 5 记录的导入前指纹
- Produces: 验收结论(满足设计文档第 10 节 5 条验收标准)

- [ ] **Step 1: 提取导入后 CSS 指纹并对比**

Run: 同 Task 6 Step 5 命令
Expected: 指纹与导入前完全一致;若不一致 → 立即停止,不提交,用用户备份恢复

- [ ] **Step 2: 打开 HTML 做功能抽查**

Run: 用浏览器打开 `生物化学题库/湖南大学题库系统-臻至版.html`,进入"第十五章 新陈代谢总论"
Expected: 章节可见、可进入;choice/truefalse/multi/short 四种题型都出现;名词解释页含本章术语;无 JS 报错(控制台无红错)

- [ ] **Step 3: 考纲覆盖核对**

对照 `出题报告.md` 的考点打勾表,确认"考纲中与新陈代谢相关条目"全部有题
Expected: 打勾表全绿

- [ ] **Step 4: 验收结论写入出题报告并提交**

```bash
git add 生物化学题库/第十五章/出题报告.md
git commit -m "docs: 第十五章试点验收通过(UI零改动/考纲全覆盖/schema 0违规)"
```

- [ ] **Step 5: 试点完成后,把 7 个任务的流水线固化**

创建 `docs/superpowers/plans/2026-08-07-biochem-15-36-import.md` 附录:每章推进 = 重复 Task 3→Task 7(第十五章出题报告中的考点打勾表 + 指纹基线随章更新),22 章完成后做一次全量核对(29→51 章节对象)

---

## Self-Review

- **Spec coverage:** 规格 10 节全部有任务对应:流水线 7 步 → Task 1-7;12 条标准 → Task 4 细则;数据格式 → Task 6;质量关卡 → Task 4 Step 5 / Task 5 / Task 7;技能链 → 计划内各任务用 code-review/verification-before-completion;推进节奏 → Task 7 Step 5。✅
- **Placeholder scan:** 无 TBD/TODO;Task 4 的题目内容为"AI 生成"性质,已用执行细则+抽审关卡替代占位(题目本身无法预写,这是数据生成任务而非代码任务)。✅
- **Type consistency:** `split_pixels`/`ocr_image`/`extract_syllabus_points`/`dedup_check`/`build_chapter_obj`/`inject` 在各自 Task 定义,后续 Task 引用一致;biochem_15 章节键、chapterLabel 在 Task 4/6/7 中一致。✅
