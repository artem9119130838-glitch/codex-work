# -*- coding: utf-8 -*-
import pandas as pd
import os

gwt_file = 'export_gwt_keywords.csv'
if not os.path.exists(gwt_file):
    print("File not found")
    exit(1)

df = pd.read_csv(gwt_file, sep=';', encoding='cp1251')
df['Clicks'] = pd.to_numeric(df['Clicks'], errors='coerce').fillna(0)
df['Impressions'] = pd.to_numeric(df['Impressions'], errors='coerce').fillna(0)
df['Avg Position'] = pd.to_numeric(df['Avg Position'], errors='coerce').fillna(100)

print(f"Total keyword entries: {len(df)}")
print(f"Unique queries: {df['Query'].nunique()}")
print(f"Unique URLs: {df['URL'].nunique()}")

# Find queries associated with more than 1 URL
query_url_count = df.groupby('Query')['URL'].nunique()
cannibal_queries = query_url_count[query_url_count > 1]
print(f"Direct cannibalization queries (>1 URL): {len(cannibal_queries)}")

# Let's inspect the top cannibal queries by Impressions
cannibal_df = df[df['Query'].isin(cannibal_queries.index)].copy()
top_cannibal = cannibal_df.groupby('Query')['Impressions'].sum().sort_values(ascending=False)

print("\n--- Top 15 Cannibalization Queries by Impressions ---")
report_rows = []
for q in top_cannibal.head(20).index:
    sub = cannibal_df[cannibal_df['Query'] == q].sort_values(by='Impressions', ascending=False)
    urls = sub['URL'].tolist()
    # Check if mix of blog and commercial hub
    has_blog = any('/useful-articles/' in u for u in urls)
    has_hub = any('/supplies-services-china/' in u for u in urls)
    has_root = any(u == 'https://longwang.ru/' or u == 'https://longwang.ru' for u in urls)
    
    print(f"\nЗапрос: '{q}' (Всего показов: {sub['Impressions'].sum():.0f}, кликов: {sub['Clicks'].sum():.0f})")
    for _, r in sub.iterrows():
        print(f"  -> {r['URL']} (Показы: {r['Impressions']:.0f}, Клики: {r['Clicks']:.0f}, Позиция: {r['Avg Position']:.1f})")
        report_rows.append({
            'Query': q,
            'Total_Impressions': sub['Impressions'].sum(),
            'URL': r['URL'],
            'Impressions': r['Impressions'],
            'Clicks': r['Clicks'],
            'Avg_Position': r['Avg Position'],
            'Type': 'Blog' if '/useful-articles/' in r['URL'] else ('Hub' if '/supplies-services-china/' in r['URL'] else 'Other')
        })

rep_df = pd.DataFrame(report_rows)
rep_df.to_csv('linking_report_output/cannibalization_report.csv', index=False, encoding='utf-8-sig')
print("\nSaved report to linking_report_output/cannibalization_report.csv")
