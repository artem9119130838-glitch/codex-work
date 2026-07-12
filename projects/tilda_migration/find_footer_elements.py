from bs4 import BeautifulSoup

INDEX_PHP = "C:/Codex_Personal/projects/tilda_migration/qilin-theme/index.php"

with open(INDEX_PHP, "r", encoding="utf-8") as f:
    content = f.read()

soup = BeautifulSoup(content, 'html.parser')

# Let's look at elements inside the footer or bottom of the page
# We can find all elements with classes containing 'rec' at the end
recs = soup.find_all(class_=lambda x: x and x.startswith('r t-rec'))
print(f"Total blocks: {len(recs)}")

# Print HTML of the last 3 blocks
for i, rec in enumerate(recs[-3:]):
    print(f"\n--- BLOCK {rec.get('id')} ({rec.get('data-record-type')}) ---")
    print(rec.prettify()[:1000])
