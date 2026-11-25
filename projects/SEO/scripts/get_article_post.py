# -*- coding: utf-8 -*-
import os
import sys
import json
import base64
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

env_file = '.env'
env_vars = {}
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

user = os.getenv('WP_USER') or env_vars.get('WP_USER', '')
pwd = os.getenv('WP_APP_PASSWORD') or env_vars.get('WP_APP_PASSWORD', '') or env_vars.get('WP_PASSWORD', '')
auth = f"Basic {base64.b64encode(f'{user}:{pwd}'.encode('utf-8')).decode('utf-8')}" if user and pwd else None

slug = "kak-kupit-oborudovanie-kitay"
url = f"https://longwang.ru/wp-json/wp/v2/posts?slug={slug}&context=edit"
headers = {'User-Agent': 'Mozilla/5.0'}
if auth:
    headers['Authorization'] = auth

print(f"Requesting post: {slug}...")
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx) as r:
        posts = json.loads(r.read().decode('utf-8'))
        if posts:
            p = posts[0]
            post_id = p['id']
            print(f"SUCCESS: Post ID = {post_id}")
            print(f"Title: {p['title']['raw']}")
            raw_content = p['content']['raw']
            print(f"Raw content length: {len(raw_content)}")
            
            # Save backup
            os.makedirs("backup", exist_ok=True)
            backup_file = f"backup/post_{post_id}_{slug}_backup.html"
            with open(backup_file, "w", encoding="utf-8") as bf:
                bf.write(raw_content)
            print(f"Backup saved to: {backup_file}")
            
            # Print first 500 chars and headings
            import re
            h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', raw_content, re.I)
            print(f"Found {len(h2s)} H2 headings:")
            for h in h2s:
                print("   -", h)
        else:
            print("Post not found by slug in posts!")
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"Error: {e}")
