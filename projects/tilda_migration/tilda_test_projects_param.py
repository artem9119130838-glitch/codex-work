import requests
from bs4 import BeautifulSoup
import re
import json

def test_param():
    email = "selfaqua@yandex.ru"
    password = "70341607Lw-"
    project_id = "5807910"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://tilda.ru/projects/?projectid={project_id}',
        'Origin': 'https://tilda.ru',
    })
    
    # Login
    r_captcha = session.post("https://tilda.cc/login/getcaptchastatus/", data={'email': email})
    csrf = r_captcha.json().get('csrf')
    payload = {'email': email, 'password': password, 'tz_offset': -180, 'csrf': csrf}
    r_submit = session.post("https://tilda.cc/login/submit/", data=payload)
    redirect_url = BeautifulSoup(r_submit.text, 'html.parser').find('meta', attrs={'http-equiv': 'refresh'}).get('content').split('URL=')[1].strip('"\'')
    session.get(redirect_url)
    
    # Request getprojects with projectid
    print("Requesting getprojects with projectid...")
    r = session.post("https://tilda.ru/projects/get/getprojects/", data={'projectid': project_id})
    print("Status:", r.status_code)
    try:
        data = r.json()
        print("Success! JSON keys:", data.keys())
        with open("C:/Codex_Personal/projects/tilda_migration/project_details.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Saved to project_details.json")
    except Exception as e:
        print("Not JSON. Response:", r.text[:200])

if __name__ == "__main__":
    test_param()
