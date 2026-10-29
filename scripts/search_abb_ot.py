import requests
import json
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
base = 'https://xn----7sbajahheyaepn1ca0aveqcb0fxl.xn--p1acf'

# Let's search for "ABB Oy" or "OT800" or "OT" with manufacturer ABB
r = requests.get(base, params={'search': 'ABB рубильник'}, headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')
links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('/document/')]

print(f"ABB рубильник found: {len(links)}")
for l in links[:5]:
    print(l)

# Let's also check search for OT
r2 = requests.get(base, params={'search': 'ABB OT'}, headers=headers, timeout=10)
s2 = BeautifulSoup(r2.text, 'html.parser')
links2 = [a['href'] for a in s2.find_all('a', href=True) if a['href'].startswith('/document/')]
print(f"ABB OT found: {len(links2)}")
for l in links2:
    r_doc = requests.get(base + l, headers=headers, timeout=10)
    s_doc = BeautifulSoup(r_doc.text, 'html.parser')
    h1 = s_doc.find('h1')
    h1_t = h1.text.strip() if h1 else l
    txt = s_doc.get_text('\n')
    lines = [line.strip() for line in txt.split('\n') if line.strip()]
    prod = ''
    for i, line in enumerate(lines):
        if 'о продукции' in line.lower() and i+1 < len(lines):
            prod = lines[i+1]
    print(f"  {h1_t} -> {prod[:100]}")
