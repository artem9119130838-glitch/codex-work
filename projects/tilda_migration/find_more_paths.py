import requests
import re

url = "https://app.tildacdn.com/tfront/dashboard/td-p-all.min.js?v=v26062601"
r = requests.get(url)
content = r.text

paths = re.findall(r'["\'](/[a-zA-Z0-9_/]+)["\']', content)

with open("C:/Codex_Personal/projects/tilda_migration/all_js_paths.txt", "w", encoding="utf-8") as f:
    for p in set(paths):
        if len(p) > 5:
            f.write(f"{p}\n")
            
print("Saved JS paths to all_js_paths.txt")
