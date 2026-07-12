from bs4 import BeautifulSoup

PUBLISHED_HTML = "C:/Codex_Personal/projects/tilda_migration/published_site.html"

with open(PUBLISHED_HTML, "r", encoding="utf-8") as f:
    html = f.read()
    
soup = BeautifulSoup(html, 'html.parser')
# Find all images in the document and print the last few
imgs = soup.find_all('img')
print(f"Total images in live site: {len(imgs)}")
for i, img in enumerate(imgs[-5:]):
    print(f"Image {len(imgs)-5+i}: src={img.get('src')}, data-original={img.get('data-original')}, class={img.get('class')}")
