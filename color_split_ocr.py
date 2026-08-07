# color_split_ocr.py
# -*- coding: utf-8 -*-
"""扫描版 PDF/图片 → 红字/黑字分色 OCR(智谱 GLM-4V-Flash)
用法: python color_split_ocr.py <输入> [输出.txt] [--start N] [--end N] [--dpi 300]
"""
import sys, os, json, time, base64, argparse, io
sys.stdout.reconfigure(encoding='utf-8')
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
                rp[x, y] = (r, g, b)  # 红色像素 → 红字图保留红色
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
