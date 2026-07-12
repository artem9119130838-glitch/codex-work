from bs4 import BeautifulSoup

def analyze():
    with open("C:/Codex_Personal/projects/tilda_migration/preview_response.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form')
    print(f"Found {len(forms)} forms:")
    
    for i, form in enumerate(forms):
        print(f"\nForm {i+1}:")
        print("  Action:", form.get('action'))
        print("  Method:", form.get('method'))
        print("  ID:", form.get('id'))
        print("  Class:", form.get('class'))
        
        # Check inputs
        inputs = form.find_all(['input', 'textarea', 'select'])
        print("  Fields:")
        for inp in inputs:
            name = inp.get('name')
            type_attr = inp.get('type')
            placeholder = inp.get('placeholder')
            print(f"    - Name: {name} | Type: {type_attr} | Placeholder: {placeholder}")

if __name__ == "__main__":
    analyze()
