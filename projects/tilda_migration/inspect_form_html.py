from bs4 import BeautifulSoup

def inspect():
    with open("C:/Codex_Personal/projects/tilda_migration/preview_response.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    block = soup.find(id='rec669618054')
    if block:
        # print first 3000 chars of block HTML
        print(block.prettify()[:3000])
    else:
        print("Block rec669618054 not found.")

if __name__ == "__main__":
    inspect()
