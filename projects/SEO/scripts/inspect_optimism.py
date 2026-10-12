import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

fp = r"C:\Users\Артем\.gemini\antigravity\brain\0511a1a5-829a-4139-88fe-d1bdf489944a\.system_generated\steps\141\content.md"
print(f"File size: {os.path.getsize(fp)} bytes")

with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
# Print headings
headings = [l.strip() for l in lines if l.startswith('#') or 'Оценка' in l or 'Ссылоч' in l or 'Траст' in l or 'ИКС' in l]
print("Key points / headings:")
for h in headings[:30]:
    print(" ", h[:80])
