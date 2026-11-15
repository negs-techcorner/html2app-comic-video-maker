import os
from PIL import Image, ImageDraw

BG_HEX = "#FFFFFF"
SRC_ICON = "assets/icon.png"
RES_DIR = "android/app/src/main/res"

DENSITIES = {
    "mipmap-mdpi": (48, 108),
    "mipmap-hdpi": (72, 162),
    "mipmap-xhdpi": (96, 216),
    "mipmap-xxhdpi": (144, 324),
    "mipmap-xxxhdpi": (192, 432),
}

def hex_to_rgba(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join([c*2 for c in h])
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

bg_rgba = hex_to_rgba(BG_HEX)
src = Image.open(SRC_ICON).convert("RGBA")

for folder, (legacy_sz, fg_sz) in DENSITIES.items():
    out_dir = os.path.join(RES_DIR, folder)
    os.makedirs(out_dir, exist_ok=True)

    # 1. Legacy Square Launcher Icon (ic_launcher.png)
    sq_bg = Image.new("RGBA", (legacy_sz, legacy_sz), bg_rgba)
    sq_icon = src.resize((legacy_sz, legacy_sz), Image.Resampling.LANCZOS)
    sq_bg.alpha_composite(sq_icon)
    sq_bg.save(os.path.join(out_dir, "ic_launcher.png"), "PNG")

    # 2. Legacy Round Launcher Icon (ic_launcher_round.png)
    mask = Image.new("L", (legacy_sz, legacy_sz), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, legacy_sz - 1, legacy_sz - 1), fill=255)
    round_img = Image.new("RGBA", (legacy_sz, legacy_sz), (0, 0, 0, 0))
    round_img.paste(sq_bg, (0, 0), mask=mask)
    round_img.save(os.path.join(out_dir, "ic_launcher_round.png"), "PNG")

    # 3. Android 8.0+ Adaptive Foreground (centered at ~62% inside 108dp safe zone)
    fg_canvas = Image.new("RGBA", (fg_sz, fg_sz), (0, 0, 0, 0))
    safe_dim = int(fg_sz * 0.62)
    fg_icon = src.resize((safe_dim, safe_dim), Image.Resampling.LANCZOS)
    offset = (fg_sz - safe_dim) // 2
    fg_canvas.alpha_composite(fg_icon, (offset, offset))
    fg_canvas.save(os.path.join(out_dir, "ic_launcher_foreground.png"), "PNG")

# 4. Write values/ic_launcher_background.xml
values_dir = os.path.join(RES_DIR, "values")
os.makedirs(values_dir, exist_ok=True)
with open(os.path.join(values_dir, "ic_launcher_background.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <color name="ic_launcher_background">' + BG_HEX + '</color>\n</resources>\n')

# 5. Overwrite mipmap-anydpi-v26/ic_launcher.xml & ic_launcher_round.xml
anydpi_dir = os.path.join(RES_DIR, "mipmap-anydpi-v26")
os.makedirs(anydpi_dir, exist_ok=True)
adaptive_xml = '<?xml version="1.0" encoding="utf-8"?>\n<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n    <background android:drawable="@color/ic_launcher_background"/>\n    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>\n</adaptive-icon>\n'
for xml_name in ("ic_launcher.xml", "ic_launcher_round.xml"):
    with open(os.path.join(anydpi_dir, xml_name), "w") as f:
        f.write(adaptive_xml)

print("Adaptive icons generated successfully with background", BG_HEX)