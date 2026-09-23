import requests
import json
import os
import time
from bs4 import BeautifulSoup
import re

COOKIE_FILE = "C:/Codex_Personal/projects/tilda_migration/session_cookies.json"

def login(email, password):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://tilda.cc/login/',
        'Origin': 'https://tilda.cc',
    })
    
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    captcha_data = r_captcha.json()
    csrf = captcha_data.get('csrf')
    needcaptcha = captcha_data.get('needcaptcha')
    
    if needcaptcha:
        raise Exception("Captcha is required by Tilda. Cannot log in programmatically right now.")
        
    payload = {'email': email, 'password': password, 'tz_offset': -180}
    if csrf:
        payload['csrf'] = csrf
        
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    if r_submit.status_code != 200:
        raise Exception(f"Submit failed with status {r_submit.status_code}")
        
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if not meta_refresh:
        raise Exception("Login failed: no meta refresh tag in submit response.")
        
    content_attr = meta_refresh.get('content', '')
    match = re.search(r'URL=(https?://[^\s\'"]+)', content_attr, re.IGNORECASE)
    if not match:
        raise Exception("Login failed: no redirect URL in meta refresh.")
        
    redirect_url = match.group(1)
    session.headers.update({'Referer': 'https://tilda.cc/'})
    session.get(redirect_url)
    
    # Save cookies to file
    cookies = session.cookies.get_dict()
    with open(COOKIE_FILE, "w") as f:
        json.dump(cookies, f)
    print("New session created and cookies saved.")
    return session

def get_session(email="selfaqua@yandex.ru", password="70341607Lw-"):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            session.cookies.update(cookies)
            # Verify if session is still valid
            session.headers.update({'Referer': 'https://tilda.ru/'})
            r = session.get("https://tilda.ru/projects/", allow_redirects=False)
            if r.status_code == 200 and "identity" not in r.url and "login" not in r.url:
                print("Using existing valid session from cookies.")
                return session
            else:
                print("Session cookies expired or invalid. Logging in again...")
        except Exception as e:
            print("Failed to load cookies:", e)
            
    # If not loaded or invalid, do login
    return login(email, password)

if __name__ == "__main__":
    s = get_session()
    print("Session ready. Cookies:", s.cookies.get_dict())
