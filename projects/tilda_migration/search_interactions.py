from bs4 import BeautifulSoup
import re

def analyze_interactions():
    with open("C:/Codex_Personal/projects/tilda_migration/preview_response.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Links
    links = soup.find_all('a')
    print(f"Total links: {len(links)}")
    for l in links[:20]:
        href = l.get('href', '')
        text = l.text.strip()
        if href.startswith('tel:') or href.startswith('mailto:') or 'wa.me' in href or 't.me' in href or 'vk.com' in href:
            print(f"  Contact Link: '{text}' -> {href}")
            
    # 2. Find any inputs
    inputs = soup.find_all('input')
    print(f"Total inputs: {len(inputs)}")
    
    # 3. Find buttons
    buttons = soup.find_all('button')
    print(f"Total buttons: {len(buttons)}")
    for b in buttons:
        print(f"  Button: '{b.text.strip()}' | ID: {b.get('id')} | Class: {b.get('class')}")
        
    # 4. Search for common Tilda form elements
    tilda_forms = soup.find_all(class_=re.compile(r't-form'))
    print(f"Tilda form classes: {len(tilda_forms)}")

if __name__ == "__main__":
    analyze_interactions()
