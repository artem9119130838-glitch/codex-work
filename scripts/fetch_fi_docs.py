import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
base = 'https://xn----7sbajahheyaepn1ca0aveqcb0fxl.xn--p1acf'

for path in ['/document/eaes-n-ru-d-fira07v1724926/', '/document/eaes-n-ru-d-fira08v6818426/']:
    r = requests.get(base + path, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    with open(f"c:\\Codex\\{path.strip('/').split('/')[-1]}.txt", 'w', encoding='utf-8') as f:
        f.write(soup.get_text('\n'))
    print(f"Saved {path}")
