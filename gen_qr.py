#!/usr/bin/env python3
"""社区关怀码 · 二维码生成脚本

用法:
    python3 gen_qr.py <目标URL> [输出文件名]

示例:
    python3 gen_qr.py https://你的页面地址.com/xxx care-qr.png

生成的二维码中心带"护"字徽章，白底高分辨率，可直接打印成胸牌/贴纸。
依赖: pip install qrcode pillow
"""
import sys
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageDraw, ImageFont

def make_qr(url: str, out: str, size: int = 1200):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#231f1c", back_color="#ffffff").convert("RGB")

    # ---- 中心"护"字徽章 ----
    qr_w, qr_h = img.size
    badge_r = int(qr_w * 0.13)          # 徽章半径约为码宽的 13%
    badge = Image.new("RGBA", (badge_r * 2, badge_r * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    d.ellipse((0, 0, badge_r * 2, badge_r * 2), fill=(232, 83, 47, 255))
    d.ellipse((badge_r * 0.16, badge_r * 0.16, badge_r * 1.84, badge_r * 1.84),
              outline=(255, 255, 255, 255), width=max(4, badge_r // 8))
    # 找可用中文字体
    font = None
    for fp in ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
               "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
               "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(fp, int(badge_r * 1.15))
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    txt = "护"
    bbox = d.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((badge_r * 2 - tw) / 2 - bbox[0], (badge_r * 2 - th) / 2 - bbox[1]),
           txt, font=font, fill=(255, 255, 255, 255))

    img.paste(badge, ((qr_w - badge_r * 2) // 2, (qr_h - badge_r * 2) // 2), badge)

    # ---- 放大到打印分辨率并加留白 ----
    scale = size / max(qr_w, qr_h)
    img = img.resize((int(qr_w * scale), int(qr_h * scale)), Image.LANCZOS)
    pad = int(size * 0.06)
    canvas = Image.new("RGB", (img.width + pad * 2, img.height + pad * 2), "#ffffff")
    canvas.paste(img, (pad, pad))
    canvas.save(out, "PNG")
    print(f"OK -> {out}  (URL: {url})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    make_qr(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "care-qr.png")
