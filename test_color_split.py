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
