import requests

url = "http://xn--80aaagi1aieb9a7amg.xn--p1ai/"
try:
    # Disable redirect following to see if there is a redirect
    r = requests.get(url, timeout=10, allow_redirects=True)
    print("Status code:", r.status_code)
    print("Final URL:", r.url)
    print("Content length:", len(r.text))
    # print first 500 characters of response HTML
    print("HTML Snippet:\n", r.text[:1000])
except Exception as e:
    print("Error:", e)
