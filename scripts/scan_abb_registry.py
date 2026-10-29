import requests
import json
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
base = 'https://xn----7sbajahheyaepn1ca0aveqcb0fxl.xn--p1acf'

def find_docs_for_query(query):
    try:
        r = requests.get(base, params={'search': query}, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        docs = []
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('/document/'):
                docs.append(a['href'])
        return list(set(docs))
    except Exception as e:
        print(f"Error for query {query}: {e}")
        return []

queries = ['OT800', 'Tmax T6', 'T6N', 'ABB OT', 'SACE Tmax', 'выключатель ABB']
all_docs = {}
for q in queries:
    all_docs[q] = find_docs_for_query(q)
    print(f'Query "{q}": found {len(all_docs[q])} docs')

abb_matching = []
checked = set()
for q, dlist in all_docs.items():
    for durl in dlist:
        if durl in checked:
            continue
        checked.add(durl)
        try:
            r = requests.get(base + durl, headers=headers, timeout=10)
            s = BeautifulSoup(r.text, 'html.parser')
            txt = s.get_text('\n')
            if 'ABB' in txt or 'abb' in txt or 'Asea Brown Boveri' in txt:
                h1 = s.find('h1')
                num = h1.text.strip() if h1 else durl
                status = 'Действует' if 'Действует' in txt else 'Архивный/Прекращен'
                
                # Extract applicant and product snippet
                lines = [line.strip() for line in txt.split('\n') if line.strip()]
                applicant = ''
                product = ''
                for i, l in enumerate(lines):
                    if 'заявитель' in l.lower() and i+1 < len(lines):
                        applicant = lines[i+1]
                    if 'о продукции' in l.lower() and i+1 < len(lines):
                        product = lines[i+1]
                
                abb_matching.append({
                    'url': base + durl,
                    'number': num,
                    'status': status,
                    'applicant': applicant,
                    'product_snippet': product[:300],
                    'full_text': txt
                })
        except Exception as e:
            print(f"Error reading doc {durl}: {e}")

print(f'Total ABB matching docs: {len(abb_matching)}')
with open(r'c:\Codex\abb_matching_docs.json', 'w', encoding='utf-8') as f:
    json.dump(abb_matching, f, ensure_ascii=False, indent=2)
print("Saved to c:\\Codex\\abb_matching_docs.json")
