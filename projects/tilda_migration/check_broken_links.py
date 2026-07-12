import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "http://xn--80aaagi1aieb9a7amg.xn--p1ai/"
r = requests.get(url, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

print("Checking assets status...")

assets = []

# 1. Stylesheets
for link in soup.find_all('link', rel='stylesheet'):
    href = link.get('href')
    if href:
        assets.append(('CSS', urljoin(url, href)))
        
# 2. Scripts
for script in soup.find_all('script'):
    src = script.get('src')
    if src:
        assets.append(('JS', urljoin(url, src)))
        
# 3. Images
for img in soup.find_all('img'):
    src = img.get('src')
    orig = img.get('data-original')
    for u in [src, orig]:
        if u:
            assets.append(('IMG', urljoin(url, u)))

# Test all assets
broken = []
for type_name, asset_url in set(assets):
    # Skip standard external ones like yandex metrika or google tags
    if "yandex" in asset_url or "google" in asset_url or "googletagmanager" in asset_url or "dropbox" in asset_url:
        continue
    try:
        res = requests.head(asset_url, timeout=5, allow_redirects=True)
        if res.status_code != 200:
            # try GET just in case HEAD is not allowed
            res_get = requests.get(asset_url, timeout=5)
            status = res_get.status_code
        else:
            status = res.status_code
            
        if status != 200:
            print(f"BROKEN [{type_name}]: {asset_url} -> Status: {status}")
            broken.append((type_name, asset_url, status))
        else:
            # print(f"OK [{type_name}]: {asset_url}")
            pass
    except Exception as e:
        print(f"ERROR [{type_name}]: {asset_url} -> {e}")
        broken.append((type_name, asset_url, "Error"))

print(f"\nTotal assets checked: {len(set(assets))}")
print(f"Total broken assets: {len(broken)}")
