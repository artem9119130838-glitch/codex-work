import requests
from bs4 import BeautifulSoup
import re
import json

def guess_endpoints():
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    pageid = "41294814"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://tilda.cc/login/',
        'Origin': 'https://tilda.cc',
    })
    
    # 1. Login
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    csrf = r_captcha.json().get('csrf')
    
    payload = {'email': email, 'password': password, 'tz_offset': -180}
    if csrf:
        payload['csrf'] = csrf
        
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    
    # Extract redirect
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if not meta_refresh:
        print("Login failed, no refresh meta.")
        return
        
    content_attr = meta_refresh.get('content', '')
    match = re.search(r'URL=(https?://[^\s\'"]+)', content_attr, re.IGNORECASE)
    if not match:
        print("Login failed, no redirect URL.")
        return
        
    redirect_url = match.group(1)
    session.headers.update({'Referer': 'https://tilda.cc/'})
    session.get(redirect_url)
    
    print("Logged in successfully. Testing endpoints...")
    
    # Now we test various URLs
    urls_to_test = [
        # Page info / block data endpoints
        f"https://tilda.ru/page/get/?pageid={pageid}",
        f"https://tilda.ru/page/gethtml/?pageid={pageid}",
        f"https://tilda.ru/page/getblocks/?pageid={pageid}",
        f"https://tilda.ru/page/json/?pageid={pageid}",
        f"https://tilda.ru/page/export/?pageid={pageid}",
        f"https://tilda.ru/page/preview/?pageid={pageid}",
        f"https://tilda.ru/page/getpage/?pageid={pageid}",
        f"https://tilda.ru/page/edit/?pageid={pageid}",
        f"https://tilda.ru/page/settings/?pageid={pageid}",
        
        # POST versions (some might require POST)
        ("POST", "https://tilda.ru/page/get/", {'pageid': pageid}),
        ("POST", "https://tilda.ru/page/gethtml/", {'pageid': pageid}),
        ("POST", "https://tilda.ru/page/getblocks/", {'pageid': pageid}),
        ("POST", "https://tilda.ru/page/json/", {'pageid': pageid}),
        
        # General project info
        "https://tilda.ru/projects/",
        f"https://tilda.ru/projects/settings/?projectid={pageid}", # probably needs projectid, not pageid
    ]
    
    for item in urls_to_test:
        method = "GET"
        data = None
        if isinstance(item, tuple):
            method, url, data = item
        else:
            url = item
            
        try:
            if method == "GET":
                r_test = session.get(url, timeout=5)
            else:
                r_test = session.post(url, data=data, timeout=5)
                
            print(f"[{method}] {url} -> Status: {r_test.status_code}, Length: {len(r_test.text)}")
            # print first 100 characters of response
            clean_text = " ".join(r_test.text[:150].split())
            print(f"   Snippet: {clean_text}...")
        except Exception as e:
            print(f"[{method}] {url} -> Error: {e}")

if __name__ == "__main__":
    guess_endpoints()
