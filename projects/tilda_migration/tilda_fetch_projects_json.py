import requests
from bs4 import BeautifulSoup
import re
import json

def fetch_projects():
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://tilda.cc/login/',
        'Origin': 'https://tilda.cc',
    })
    
    # 1. Check captcha status
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    print("Captcha status response:", r_captcha.text)
    captcha_data = r_captcha.json()
    csrf = captcha_data.get('csrf')
    needcaptcha = captcha_data.get('needcaptcha')
    
    if needcaptcha:
        print("WARNING: Captcha is required! Cannot login programmatically without captcha solver.")
        return
        
    payload = {'email': email, 'password': password, 'tz_offset': -180}
    if csrf:
        payload['csrf'] = csrf
        
    # 2. Submit credentials
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    print("Submit Status Code:", r_submit.status_code)
    print("Submit Response snippet:", r_submit.text[:300])
    
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if not meta_refresh:
        print("Login failed - no meta refresh tag.")
        return
        
    content_attr = meta_refresh.get('content', '')
    match = re.search(r'URL=(https?://[^\s\'"]+)', content_attr, re.IGNORECASE)
    if not match:
        print("Login failed - no redirect URL in meta refresh.")
        return
        
    redirect_url = match.group(1)
    print("Auth redirect URL:", redirect_url)
    session.headers.update({'Referer': 'https://tilda.cc/'})
    r_redirect = session.get(redirect_url)
    print("Redirect response final URL:", r_redirect.url)
    
    # Update headers for AJAX requests on tilda.ru
    session.headers.update({
        'Referer': 'https://tilda.ru/projects/',
    })
    
    # Request to getprojects
    print("Requesting /projects/get/getprojects/ via POST...")
    r_projects_post = session.post("https://tilda.ru/projects/get/getprojects/")
    print("POST Status:", r_projects_post.status_code)
    try:
        data_post = r_projects_post.json()
        print("POST Response parsed as JSON successfully.")
        with open("C:/Codex_Personal/projects/tilda_migration/projects_list.json", "w", encoding="utf-8") as f:
            json.dump(data_post, f, indent=2, ensure_ascii=False)
        print("Saved to projects_list.json")
    except Exception as e:
        print("POST Response is not JSON. Text snippet:", r_projects_post.text[:200])

if __name__ == "__main__":
    fetch_projects()
