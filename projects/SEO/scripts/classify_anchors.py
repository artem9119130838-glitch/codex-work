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

# Classify anchors
exact_commercial = []
url_brand_anchors = []
generic_anchors = []

generic_words = ['здесь', 'тут', 'подробнее', 'читать', 'источник', 'сайте', 'ссылке']

for r in rows:
    anc = r[8].strip()
    anc_lower = anc.lower()
    if anc.startswith('http') or 'longwang' in anc_lower:
        url_brand_anchors.append(r)
    elif any(g in anc_lower for g in generic_words):
        generic_anchors.append(r)
    else:
        exact_commercial.append(r)

print(f"Total links: {len(rows)}")
print(f"Exact commercial anchors: {len(exact_commercial)} ({round(len(exact_commercial)/len(rows)*100, 1)}%)")
print(f"URL / Brand anchors: {len(url_brand_anchors)} ({round(len(url_brand_anchors)/len(rows)*100, 1)}%)")
print(f"Generic anchors (здесь, подробнее): {len(generic_anchors)} ({round(len(generic_anchors)/len(rows)*100, 1)}%)")

# Find potentially weak / irrelevant donors
irrelevant_topics = ['Семья', 'Квартира и дача', 'Развлекательные журналы']
weak_donors = []
for r in rows:
    iks_str = r[3].replace(' ', '').strip()
    topic = r[4].strip()
    url_donor = r[1]
    iks = int(iks_str) if iks_str.isdigit() else 0
    if iks < 30 or topic in irrelevant_topics or any(w in url_donor for w in ['immynolog', 'francii', 'recept', 'kulinari']):
        weak_donors.append((iks, topic, r[8], url_donor))

print(f"\nPotentially weak / off-topic links: {len(weak_donors)}")
for w in weak_donors[:10]:
    print(f"  ИКС:{w[0]} | Тема:{w[1]} | Анкор:'{w[2]}' | URL:{w[3][:70]}...")
