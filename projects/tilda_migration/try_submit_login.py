import requests
from bs4 import BeautifulSoup
import re

def try_submit_login():
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
    
    # 1. GET login page
    login_url = "https://tilda.cc/login/"
    print(f"GET {login_url}")
    r = session.get(login_url)
    print(f"Status: {r.status_code}")
    
    # 2. Get captcha status to retrieve csrf
    captcha_status_url = "https://tilda.cc/login/getcaptchastatus/"
    print(f"POST {captcha_status_url}")
    r_captcha = session.post(captcha_status_url, data={'email': email})
    print(f"Captcha status response: {r_captcha.text}")
    
    csrf = None
    try:
        data_json = r_captcha.json()
        csrf = data_json.get('csrf')
        print(f"CSRF from captcha JSON: {csrf}")
    except Exception as e:
        print("Failed to parse captcha JSON:", e)
        
    # 3. Submit credentials to /login/submit/
    submit_url = "https://tilda.cc/login/submit/"
    payload = {
        'email': email,
        'password': password,
        'tz_offset': -180
    }
    if csrf:
        payload['csrf'] = csrf
        
    print(f"POST {submit_url}")
    r_submit = session.post(submit_url, data=payload)
    print(f"Submit Status: {r_submit.status_code}")
    
    # Try to find redirect URL in response
    redirect_url = None
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta_refresh:
        content_attr = meta_refresh.get('content', '')
        # content looks like: "0;URL=https://tilda.ru/login/auth/?token=..."
        match = re.search(r'URL=(https?://[^\s\'"]+)', content_attr, re.IGNORECASE)
        if match:
            redirect_url = match.group(1)
            print(f"Found redirect URL in meta refresh: {redirect_url}")
            
    if redirect_url:
        # Go to the auth URL to establish session on tilda.ru
        print(f"GET auth redirect: {redirect_url}")
        # Make sure session headers referer is updated
        session.headers.update({'Referer': 'https://tilda.cc/'})
        r_auth = session.get(redirect_url)
        print(f"Auth URL final response URL: {r_auth.url}")
        print(f"Auth status: {r_auth.status_code}")
        
        # Now try to load the target page on tilda.ru
        page_url = "https://tilda.ru/page/?pageid=41294814"
        print(f"GET {page_url}")
        session.headers.update({'Referer': 'https://tilda.ru/projects/'})
        r_page = session.get(page_url)
        print(f"Page Status: {r_page.status_code}")
        print(f"Page content length: {len(r_page.text)}")
        
        # Save page HTML
        with open("C:/Codex_Personal/projects/tilda_migration/page_admin.html", "w", encoding="utf-8") as f:
            f.write(r_page.text)
        print("Saved admin page HTML to C:/Codex_Personal/projects/tilda_migration/page_admin.html")
        
        # Print a snippet of the page to verify
        soup_page = BeautifulSoup(r_page.text, 'html.parser')
        title_tag = soup_page.find('title')
        print("Page Title in Tilda Admin:", title_tag.text.strip() if title_tag else "Not found")
        
        # Look for project ID, page ID or public link on the page
        project_link = soup_page.find('a', href=re.compile(r'/projects/\?projectid=\d+'))
        if project_link:
            print("Project Link:", project_link.get('href'))
    else:
        print("Could not find redirect URL. Response was:")
        print(r_submit.text)

if __name__ == "__main__":
    try_submit_login()
