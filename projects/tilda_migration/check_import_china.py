import requests

try:
    r = requests.get("http://импорт-китай.рф", timeout=5, verify=False)
    print("Status code:", r.status_code)
    print("Final URL:", r.url)
    print("Snippet:", r.text[:200])
except Exception as e:
    print("Error:", e)
