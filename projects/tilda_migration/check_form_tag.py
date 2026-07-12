from bs4 import BeautifulSoup

def check_form_tag():
    with open("C:/Codex_Personal/projects/tilda_migration/published_site.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form')
    print(f"Found {len(forms)} form tags in published site:")
    for i, form in enumerate(forms):
        print(f"Form {i+1}: action={form.get('action')}, method={form.get('method')}, class={form.get('class')}")

if __name__ == "__main__":
    check_form_tag()
