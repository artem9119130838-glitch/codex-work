import os
import zipfile

BASE_DIR = "C:/Codex_Personal/projects/tilda_migration"
THEME_DIR = os.path.join(BASE_DIR, "qilin-theme")
ZIP_FILE = os.path.join(BASE_DIR, "qilin-theme.zip")

def make_zip():
    print(f"Creating ZIP archive {ZIP_FILE}...")
    with zipfile.ZipFile(ZIP_FILE, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(THEME_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                # Compute relative path in ZIP (should start with qilin-theme/)
                rel_path = os.path.relpath(file_path, os.path.dirname(THEME_DIR))
                zipf.write(file_path, rel_path)
    print("ZIP archive created successfully!")

if __name__ == "__main__":
    make_zip()
