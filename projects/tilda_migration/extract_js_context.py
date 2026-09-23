import requests

url = "https://app.tildacdn.one/tfront/dashboard/t-sign-in.min.js?ver=v25122301"
r = requests.get(url)
content = r.text

idx = content.find("/login/submit/")
if idx != -1:
    print("Found '/login/submit/' at index:", idx)
    # print 1000 characters before and after
    start = max(0, idx - 500)
    end = min(len(content), idx + 1500)
    print(content[start:end])
else:
    print("Not found")
