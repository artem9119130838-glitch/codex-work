from bs4 import BeautifulSoup
import re

def inspect():
    with open("C:/Codex_Personal/projects/tilda_migration/preview_response.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Let's find all divs with class 't-form'
    form_divs = soup.find_all(class_=re.compile(r't-form'))
    print(f"Found {len(form_divs)} elements with 't-form' in class.")
    
    # Find all input fields (including text, tel, email)
    inputs = soup.find_all(['input', 'textarea', 'select'])
    print(f"Total inputs/fields: {len(inputs)}")
    for i, inp in enumerate(inputs):
        print(f"  Field {i+1}: Tag: {inp.name} | Type: {inp.get('type')} | Name: {inp.get('name')} | Placeholder: {inp.get('placeholder')} | Class: {inp.get('class')}")
        
    # Let's print parent block IDs for fields
    for inp in inputs:
        parent_rec = inp.find_parent(class_='t-rec')
        if parent_rec:
            print(f"    Field '{inp.get('name')}' is inside block {parent_rec.get('id')} (type {parent_rec.get('data-record-type')})")

if __name__ == "__main__":
    inspect()
