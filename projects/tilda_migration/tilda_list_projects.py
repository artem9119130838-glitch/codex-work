import requests
from bs4 import BeautifulSoup
import re

def list_projects():
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
        
    content_attr = meta_refresh.get('content', '')
    match = re.search(r'URL=(https?://[^\s\'"]+)', content_attr, re.IGNORECASE)
    if not match:
        print("Login failed, no redirect")
        return
        
    redirect_url = match.group(1)
    session.headers.update({'Referer': 'https://tilda.cc/'})
    session.get(redirect_url)
    
    # Get projects page
    print("Getting projects list...")
    session.headers.update({'Referer': 'https://tilda.ru/'})
    r_projects = session.get("https://tilda.ru/projects/")
    
    # Save projects HTML for debugging
    with open("C:/Codex_Personal/projects/tilda_migration/projects.html", "w", encoding="utf-8") as f:
        f.write(r_projects.text)
        
    soup_p = BeautifulSoup(r_projects.text, 'html.parser')
    
    # Find all project links
    # Often Tilda projects pages have links like /projects/?projectid=XXXXXX
    links = soup_p.find_all('a', href=re.compile(r'/projects/\?projectid=\d+'))
    print(f"Found {len(links)} links to projects:")
    
    project_ids = []
    for link in links:
        href = link.get('href')
        proj_id = re.search(r'projectid=(\d+)', href).group(1)
        project_ids.append(proj_id)
        # Find project title
        title = link.text.strip()
        # Sometimes title is empty or contains child elements, let's find the nearest text
        print(f"Project ID: {proj_id}, Title: {title or '[Empty]'}, Link: {href}")
        
    # Get unique project IDs
    project_ids = list(set(project_ids))
    
    # For each project, let's load the project page to see its pages!
    for proj_id in project_ids:
        project_url = f"https://tilda.ru/projects/?projectid={proj_id}"
        print(f"\nLoading pages for Project {proj_id} ({project_url})...")
        r_proj = session.get(project_url)
        
        # Save project page HTML
        with open(f"C:/Codex_Personal/projects/tilda_migration/project_{proj_id}.html", "w", encoding="utf-8") as f:
            f.write(r_proj.text)
            
        soup_proj = BeautifulSoup(r_proj.text, 'html.parser')
        
        # Look for page links like /page/?pageid=XXXXXX
        page_links = soup_proj.find_all('a', href=re.compile(r'/page/\?pageid=\d+'))
        print(f"Found {len(page_links)} links to pages in project {proj_id}:")
        
        seen_pages = set()
        for p_link in page_links:
            p_href = p_link.get('href')
            p_id = re.search(r'pageid=(\d+)', p_href).group(1)
            if p_id in seen_pages:
                continue
            seen_pages.add(p_id)
            
            # Find page name (usually in a div next to or inside the link)
            p_title = p_link.text.strip()
            print(f"  Page ID: {p_id}, Text: {p_title or '[Empty]'}, Link: {p_href}")

if __name__ == "__main__":
    list_projects()
