import re

INDEX_PHP = "C:/Codex_Personal/projects/tilda_migration/qilin-theme/index.php"

with open(INDEX_PHP, "r", encoding="utf-8") as f:
    content = f.read()

# Search for "БИОХИМ" or "biohim"
matches_ru = re.findall(r'(.{0,100}БИОХИМ.{0,100})', content)
print("Matches for 'БИОХИМ':")
for m in matches_ru:
    print(m.strip())
    
# Let's search for the preview back panel styles or images
# The preview panel is often inside a div with a specific id
# Let's search for "t-page-preview" or "preview" in the content
print("\nMatches for 'preview' or similar:")
matches_prev = re.findall(r'(.{0,100}preview.{0,100})', content)
for m in matches_prev[:10]:
    print(m.strip())
