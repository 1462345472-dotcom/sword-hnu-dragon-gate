# -*- coding: utf-8 -*-
"""
扫描版 PDF / 图片 → 文字识别管线(智谱 GLM-4V-Flash 中介)

用法:
    python ocr_scan_pdf.py <输入文件.pdf|图片> [输出.txt] [--start N] [--end N] [--dpi 300]

示例:
    python ocr_scan_pdf.py "生物化学题库/338 生物化学考纲.pdf" 考纲文字.txt
    python ocr_scan_pdf.py "生物化学题库/338 生物化学考纲.pdf" --start 1 --end 3

API Key 从环境变量 ZHIPU_API_KEY 读取(或在同目录 ocr_config.json 中配置),
不要在命令行明文传入。
"""

import sys
import os
import json
import time
import base64
import argparse

import fitz  # PyMuPDF
import requests

# ---------- 配置 ----------

ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
OCR_MODEL = "glm-4v-flash"  # 免费视觉模型


def load_api_key():
    key = os.environ.get("ZHIPU_API_KEY", "")
    if not key:
        cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                key = json.load(f).get("zhipu_api_key", "")
    if not key:
        sys.exit("错误: 未找到智谱 API Key。\n"
                 "请设置环境变量 ZHIPU_API_KEY,或在 ocr_config.json 中写入 {\"zhipu_api_key\": \"你的key\"}")
    return key


# ---------- PDF 渲染 ----------

def render_page(page, dpi=300):
    """把 PDF 页渲染成 PNG base64 字符串"""
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    png_bytes = pix.tobytes("png")
    return base64.b64encode(png_bytes).decode("ascii")


# ---------- 智谱 OCR ----------

def ocr_image(api_key, b64_png, prompt="请完整识别这张图片中的全部文字内容,保持原有排版顺序,逐行输出。不要添加任何解释。"):
    """调用 GLM-4V-Flash 识别单张图片,返回识别文本"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OCR_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_png}"}},
                ],
            }
        ],
        "temperature": 0.1,
    }
    for attempt in range(4):
        try:
            resp = requests.post(ZHIPU_BASE_URL, headers=headers, json=payload, timeout=120)
            if resp.status_code == 429:
                # 限流:退避重试
                time.sleep(10 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"    [重试 {attempt + 1}/4] 请求失败: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    return "[识别失败]"


# ---------- 主流程 ----------

def main():
    parser = argparse.ArgumentParser(description="扫描版 PDF → 文字识别(智谱 GLM-4V-Flash)")
    parser.add_argument("input", help="输入 PDF 或图片路径")
    parser.add_argument("output", nargs="?", default=None, help="输出 txt 路径(默认:输入文件名_ocr.txt)")
    parser.add_argument("--start", type=int, default=1, help="起始页(从 1 开始,默认 1)")
    parser.add_argument("--end", type=int, default=None, help="结束页(默认最后一页)")
    parser.add_argument("--dpi", type=int, default=300, help="渲染分辨率(默认 300)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"错误: 文件不存在: {args.input}")

    api_key = load_api_key()
    out_path = args.output or (os.path.splitext(args.input)[0] + "_ocr.txt")

    doc = fitz.open(args.input)
    total = doc.page_count
    start = max(1, args.start)
    end = min(total, args.end or total)
    print(f"共 {total} 页,识别第 {start}~{end} 页 → {out_path}")

    results = []
    for i in range(start - 1, end):
        page_num = i + 1
        print(f"[{page_num}/{end}] 渲染第 {page_num} 页 ...", flush=True)
        b64 = render_page(doc[i], dpi=args.dpi)
        print(f"[{page_num}/{end}] 调用智谱 GLM-4V-Flash 识别 ...", flush=True)
        text = ocr_image(api_key, b64)
        results.append(f"===== 第 {page_num} 页 =====\n{text}\n")
        print(f"[{page_num}/{end}] 完成({len(text)} 字)", flush=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print(f"\n全部完成,结果已保存到: {out_path}")


if __name__ == "__main__":
    main()
