import requests
from bs4 import BeautifulSoup
import re
import json
import time

def fetch_pages():
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    project_id = "5807910"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://tilda.cc/login/',
        'Origin': 'https://tilda.cc',
    })
    
    # 1. Login
    time.sleep(2)  # pause to avoid spam detection
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    print("Captcha status:", r_captcha.text)
    csrf = r_captcha.json().get('csrf')
    
    payload = {'email': email, 'password': password, 'tz_offset': -180}
    if csrf:
        payload['csrf'] = csrf
        
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    print("Submit status code:", r_submit.status_code)
    
    soup = BeautifulSoup(r_submit.text, 'html.parser')
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if not meta_refresh:
        print("Login failed! Response:")
        print(r_submit.text[:1000])
        return
        
    redirect_url = meta_refresh.get('content', '').split('URL=')[1].strip('"\'')
    session.headers.update({'Referer': 'https://tilda.cc/'})
    session.get(redirect_url)
    
    # 2. Update headers for AJAX
    session.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://tilda.ru/projects/?projectid={project_id}',
    })
    
    # Try requesting getpagesettings
    print(f"Requesting getpagesettings for project {project_id}...")
    r_pages = session.post("https://tilda.ru/projects/get/getpagesettings/", data={'projectid': project_id})
    print("Status:", r_pages.status_code)
    try:
        data = r_pages.json()
        print("Response parsed as JSON successfully.")
        with open(f"C:/Codex_Personal/projects/tilda_migration/project_{project_id}_pages.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved to project_pages.json")
    except Exception as e:
        print("Response is not JSON. Text snippet:", r_pages.text[:500])

if __name__ == "__main__":
    fetch_pages()
