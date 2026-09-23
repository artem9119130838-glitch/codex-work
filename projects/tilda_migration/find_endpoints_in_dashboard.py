import requests
import re

url = "https://app.tildacdn.com/tfront/dashboard/td-p-all.min.js?v=v26062601"
r = requests.get(url)
content = r.text

matches = re.findall(r'url\s*:\s*["\']([^"\']+)["\']', content)
paths = re.findall(r'["\'](/projects/[a-zA-Z0-9_/]+|/page/[a-zA-Z0-9_/]+)["\']', content)

with open("C:/Codex_Personal/projects/tilda_migration/endpoints.txt", "w", encoding="utf-8") as f:
    f.write("Ajax URLs:\n")
    for m in set(matches):
        f.write(f"{m}\n")
    f.write("\nPaths:\n")
    for p in set(paths):
        f.write(f"{p}\n")
        
print("Saved endpoints to endpoints.txt successfully.")
