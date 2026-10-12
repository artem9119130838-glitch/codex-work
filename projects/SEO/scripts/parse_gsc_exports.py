import os
import sys
import zipfile
import csv
import json

sys.stdout.reconfigure(encoding='utf-8')

SEO_DIR = r"c:\Codex\projects\SEO"
EXTRACT_DIR = os.path.join(SEO_DIR, "gsc_extracted")

def extract_and_parse():
    os.makedirs(EXTRACT_DIR, exist_ok=True)
    zip_files = [f for f in os.listdir(SEO_DIR) if f.endswith(".zip") and "longwang.ru" in f]
    print(f"Found {len(zip_files)} GSC zip archives in {SEO_DIR}:")
    
    for zf in zip_files:
        zpath = os.path.join(SEO_DIR, zf)
        sub_folder = os.path.join(EXTRACT_DIR, os.path.splitext(zf)[0])
        os.makedirs(sub_folder, exist_ok=True)
        try:
            with zipfile.ZipFile(zpath, 'r') as z:
                z.extractall(sub_folder)
                print(f" Extracted: {zf} -> {len(z.namelist())} files: {z.namelist()}")
        except Exception as e:
            print(f" Error extracting {zf}: {e}")

    # Now let's analyze the extracted CSVs
    print("\n================ GSC ANALYSIS ================")
    summary = {}

    for root, dirs, files in os.walk(EXTRACT_DIR):
        for file in files:
            if not file.endswith('.csv'):
                continue
            fp = os.path.join(root, file)
            rel = os.path.relpath(fp, EXTRACT_DIR)
            print(f"\n--- CSV: {rel} ({os.path.getsize(fp)} bytes) ---")
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    rows = list(reader)
                    print(f"Header: {header}")
                    print(f"Rows count: {len(rows)}")
                    print("Top 5 sample rows:")
                    for r in rows[:5]:
                        print(" ", r)
            except Exception as e:
                print(f"Error reading CSV {fp}: {e}")

if __name__ == '__main__':
    extract_and_parse()
