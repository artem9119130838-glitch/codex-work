import requests
from bs4 import BeautifulSoup
import re
from tilda_session import get_session

def check_preview(page_id="41294814"):
    session = get_session()
    
    preview_url = f"https://tilda.ru/page/preview/?pageid={page_id}"
    print(f"GET {preview_url}...")
    session.headers.update({
        'Referer': f'https://tilda.ru/page/?pageid={page_id}',
    })
    
    r = session.get(preview_url, allow_redirects=True)
    print("Status:", r.status_code)
    print("Final URL:", r.url)
    
    # Save preview HTML
    with open("C:/Codex_Personal/projects/tilda_migration/preview_response.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved response to preview_response.html")
    
    # Check if we can find page content or iframe
    soup = BeautifulSoup(r.text, 'html.parser')
    iframe = soup.find('iframe')
    if iframe:
        print("Found iframe src:", iframe.get('src'))
    else:
        # Check if there is some other redirect or link
        print("Snippet:", r.text[:500])

if __name__ == "__main__":
    check_preview()
