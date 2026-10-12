import csv
import sys
import os
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

fp = r"c:\Codex\projects\SEO\paid.csv"

rows = []
with open(fp, 'r', encoding='cp1251', errors='ignore') as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader, None)
    for r in reader:
        if r and len(r) > 1:
            rows.append(r)

print(f"Total reviews: {len(rows)}")

# Columns:
# 0: Кампания
# 1: Страница с обзором
# 2: Трафик
# 3: ИКС
# 4: Тематика
# 5: Тип обзора
# 6: Цена, руб.
# 7: Дата
# 8: Анкор
# 9: URL кампании
# 10: Участие в биржах автоссылок

campaigns = Counter([r[0].strip() for r in rows])
topics = Counter([r[4].strip() for r in rows])
targets = Counter([r[9].strip() for r in rows])
types = Counter([r[5].strip() for r in rows])

prices = []
for r in rows:
    p = r[6].replace(' ', '').replace(',', '.')
    try:
        prices.append(float(p))
    except:
        pass

iks_values = []
zero_iks = 0
high_iks = []
low_iks = []
for r in rows:
    iks_str = r[3].replace(' ', '').strip()
    try:
        val = int(iks_str)
        iks_values.append(val)
        if val >= 500:
            high_iks.append((val, r[1]))
        elif val < 50:
            low_iks.append((val, r[1]))
    except:
        zero_iks += 1

print("\n--- CAMPAIGNS ---")
for k, v in campaigns.most_common():
    print(f"  {k}: {v}")

print("\n--- TOPICS ---")
for k, v in topics.most_common():
    print(f"  {k}: {v}")

print(f"\n--- FINANCIALS ---")
print(f"Total spent: {sum(prices)} руб.")
print(f"Avg link price: {round(sum(prices)/len(prices), 1)} руб.")

print(f"\n--- IKS METRICS ---")
print(f"Links with IKS: {len(iks_values)}, Zero/No IKS: {zero_iks}")
if iks_values:
    print(f"Avg IKS: {round(sum(iks_values)/len(iks_values), 1)}")
    print(f"High IKS (>=500): {len(high_iks)} links")
    print(f"Low IKS (<50): {len(low_iks)} links")

print("\n--- TARGET URLS (Where links point) ---")
for k, v in targets.most_common(12):
    print(f"  [{v} ссылок] -> {k}")

print("\n--- ANCHORS SAMPLE (first 20) ---")
for r in rows[:20]:
    print(f"  '{r[8]}' -> {r[9]}")
