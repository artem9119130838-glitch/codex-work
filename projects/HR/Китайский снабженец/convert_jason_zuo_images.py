import sys
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

in_dir = Path(r"C:\Codex\projects\HR\Китайский снабженец\jason_zuo_pages")

for i in range(1, 5):
    bin_file = in_dir / f"page_{i}.bin"
    if bin_file.exists():
        raw_bytes = bin_file.read_bytes()
        # 1055 x 1491, RGB
        img = Image.frombytes("RGB", (1055, 1491), raw_bytes)
        png_path = in_dir / f"page_{i}.png"
        jpg_path = in_dir / f"page_{i}.jpg"
        img.save(png_path, "PNG")
        img.save(jpg_path, "JPEG", quality=90)
        print(f"Saved page {i}: {png_path} ({png_path.stat().st_size} bytes), {jpg_path} ({jpg_path.stat().st_size} bytes)")
