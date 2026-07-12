import requests
import re

url = "https://app.tildacdn.one/tfront/dashboard/t-sign-in.min.js?ver=v25122301"
r = requests.get(url)
content = r.text

# Let's search for URLs or api endpoints
urls = re.findall(r'(https?://[^\s"\']+|/[^\s"\']+)', content)
print("Found URLs or paths:")
for u in set(urls):
    if "api" in u or "login" in u or "signin" in u or "auth" in u:
        print(u)
