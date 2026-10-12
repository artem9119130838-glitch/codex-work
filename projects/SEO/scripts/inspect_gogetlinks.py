import csv
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

fp = r"c:\Codex\projects\SEO\paid.csv"

with open(fp, 'r', encoding='cp1251', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    rows = list(reader)

print(f"Total rows: {len(rows)}")
if rows:
    print("Header:", [c.strip() for c in rows[0]])
    print(f"\nAll columns in row 1:")
    for col_name, val in zip(rows[0], rows[1]):
        print(f"  {col_name.strip()} : {val.strip()}")

    print("\n--- Summary of Donors (first 15 links) ---")
    for r in rows[1:16]:
        # usually columns: Кампания, URL обзора, Трафик, ИКС, Тип обзора, Анкор, Цена, Дата, Статус, Целевой URL...
        print(f"  [{r[7] if len(r)>7 else ''}] ИКС:{r[3] if len(r)>3 else ''} | {r[1] if len(r)>1 else ''}")
