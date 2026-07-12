import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_project_pages(project_id="5807910"):
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://tilda.cc/login/',
        'Origin': 'https://tilda.cc',
    })
    
    # Login
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    csrf = r_captcha.json().get('csrf')
    
    payload = {'email': email, 'password': password, 'tz_offset': -180}
    if csrf:
        payload['csrf'] = csrf
        
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if not meta_refresh:
        print("Login failed")
        return
        
    redirect_url = meta_refresh.get('content', '').split('URL=')[1].strip('"\'')
    session.headers.update({'Referer': 'https://tilda.cc/'})
    session.get(redirect_url)
    
    # Load project pages HTML
    project_url = f"https://tilda.ru/projects/?projectid={project_id}"
    print(f"Loading pages from: {project_url}...")
    session.headers.update({'Referer': 'https://tilda.ru/projects/'})
    r_proj = session.get(project_url)
    
    # Save project page HTML
    with open(f"C:/Codex_Personal/projects/tilda_migration/project_{project_id}.html", "w", encoding="utf-8") as f:
        f.write(r_proj.text)
        
    soup_proj = BeautifulSoup(r_proj.text, 'html.parser')
    
    # Pages are typically listed inside a table or divs with classes like "td-project-page-row" or links to page edit
    # Let's find all links matching /page/?pageid=XXXXXX
    page_links = soup_proj.find_all('a', href=re.compile(r'/page/\?pageid=\d+'))
    print(f"Total page links found: {len(page_links)}")
    
    pages = {}
    for p_link in page_links:
        href = p_link.get('href')
        page_id = re.search(r'pageid=(\d+)', href).group(1)
        
        # Avoid duplicates
        if page_id in pages:
            continue
            
        # Try to find page title and path
        # Usually, page title is inside td-project-page-title or a child element
        # Let's try to find title text
        title = p_link.text.strip()
        
        # If title is empty, look around
        # In Tilda UI, there's often a div for page title and another for path (e.g. index.html)
        # Let's find parent elements
        parent = p_link.find_parent('div', class_='td-project-grid__item') or p_link.find_parent('td') or p_link.find_parent('tr') or p_link.parent
        
        path = ""
        # Let's search inside the parent for elements containing page path (e.g. "/index")
        if parent:
            text_nodes = parent.find_all(text=True)
            for tn in text_nodes:
                val = tn.strip()
                if val.startswith('/') and (val.endswith('.html') or len(val) > 1):
                    path = val
                    break
        
        pages[page_id] = {
            'id': page_id,
            'title': title,
            'path': path,
            'url': f"https://tilda.ru/page/?pageid={page_id}"
        }
        
    # Print pages
    print(f"\nPages found in project {project_id}:")
    for pid, pdata in pages.items():
        print(f"Page ID: {pid} | Title: {pdata['title']} | Path: {pdata['path']} | URL: {pdata['url']}")
        
    # Save page dictionary to json
    with open(f"C:/Codex_Personal/projects/tilda_migration/project_{project_id}_pages.json", "w", encoding="utf-8") as f:
        json.dump(list(pages.values()), f, indent=2, ensure_ascii=False)
    print(f"Saved pages list to C:/Codex_Personal/projects/tilda_migration/project_{project_id}_pages.json")

if __name__ == "__main__":
    fetch_project_pages()
