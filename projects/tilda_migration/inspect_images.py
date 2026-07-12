import os

img_dir = "C:/Codex_Personal/projects/tilda_migration/qilin-theme/assets/img"
files = os.listdir(img_dir)
print("Images in assets/img:")
for f in files:
    print(f)
