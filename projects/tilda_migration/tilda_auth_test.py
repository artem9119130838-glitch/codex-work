import requests
from bs4 import BeautifulSoup
import json

def test_tilda_auth():
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    })
    
    # 1. Get login page to retrieve any cookies/tokens
    login_url = "https://tilda.cc/login/"
    print(f"GET {login_url}")
    r = session.get(login_url)
    print(f"Status: {r.status_code}")
    
    # 2. Try to log in
    # Often Tilda uses tilda.cc/login/ with POST parameters
    payload = {
        'email': email,
        'password': password
    }
    
    print("Posting credentials...")
    r_post = session.post(login_url, data=payload, allow_redirects=True)
    print(f"POST Status: {r_post.status_code}")
    print(f"Final URL: {r_post.url}")
    
    if "projects" in r_post.url or "page" in r_post.url or "projects" in r_post.text:
        print("Success! Logged in.")
        # Let's save cookies
        cookies = session.cookies.get_dict()
        print("Cookies saved:", cookies)
        
        # Let's try to load the page provided by the user
        page_url = "https://tilda.ru/page/?pageid=41294814"
        print(f"GET {page_url}")
        r_page = session.get(page_url)
        print(f"Page Status: {r_page.status_code}")
        
        # Check if we can find the project ID or preview link
        soup = BeautifulSoup(r_page.text, 'html.parser')
        
        # Save page html for analysis
        with open("C:/Codex_Personal/projects/tilda_migration/page_admin.html", "w", encoding="utf-8") as f:
            f.write(r_page.text)
        print("Saved admin page HTML to C:/Codex_Personal/projects/tilda_migration/page_admin.html")
        
        # Try to find page title and preview URL
        title_tag = soup.find('title')
        print("Page Title:", title_tag.text if title_tag else "Not found")
        
    else:
        print("Failed to log in.")
        # Let's save the response to see if there is a captcha or error message
        with open("C:/Codex_Personal/projects/tilda_migration/login_response.html", "w", encoding="utf-8") as f:
            f.write(r_post.text)
        print("Saved login response HTML to C:/Codex_Personal/projects/tilda_migration/login_response.html")

if __name__ == "__main__":
    test_tilda_auth()
