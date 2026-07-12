from bs4 import BeautifulSoup

PUBLISHED_HTML = "C:/Codex_Personal/projects/tilda_migration/published_site.html"

with open(PUBLISHED_HTML, "r", encoding="utf-8") as f:
    html = f.read()
    
soup = BeautifulSoup(html, 'html.parser')
footer_block = soup.find(id='rec673087820')
if footer_block:
    img = footer_block.find('img')
    if img:
        print("Image src in live footer:", img.get('src'))
        print("Image data-original in live footer:", img.get('data-original'))
    else:
        print("No image found in live footer block.")
else:
    # Try to find any footer block or class t463__logo
    logo = soup.find(class_='t463__logo')
    if logo:
        print("Logo found by class in live site:", logo.get('src'))
    else:
        print("Footer block not found in live site.")
