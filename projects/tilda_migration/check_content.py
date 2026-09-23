import requests
from bs4 import BeautifulSoup

try:
    r = requests.get("https://цилинь.рф", timeout=10, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Print page title
    title = soup.find('title')
    print("Title of published site:", title.text.strip() if title else "Not found")
    
    # Save to file to see if it's the real site or tilda expired warning
    with open("C:/Codex_Personal/projects/tilda_migration/published_site.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    print("Saved public site HTML.")
    
    # Check if there is Tilda expired mark
    if "ограничен" in r.text or "expired" in r.text.lower() or "платеж" in r.text.lower():
        print("Seems like it is expired or has limits warning.")
    else:
        print("It seems to be the active live site!")
        
except Exception as e:
    print("Error:", e)
