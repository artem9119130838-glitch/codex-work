import os

img_dir = "C:/Codex/projects/tilda_migration/qilin-theme/assets/img"
files = os.listdir(img_dir)
print("Images in assets/img:")
for f in files:
    print(f)

