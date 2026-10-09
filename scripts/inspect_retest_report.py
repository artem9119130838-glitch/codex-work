import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DOWNLOADS = r"C:\Users\Артем\Downloads"
SCRATCH = r"C:\Codex_Personal\scratch"

path = os.path.join(DOWNLOADS, "retest_report.md")
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

lines = text.splitlines()

headers = [l for l in lines if l.startswith("#")]
print(f"Total lines: {len(lines)}, Total chars: {len(text)}")
print("=== HEADERS ===")
for h in headers[:30]:
    print(h)

# Check first 50 lines
print("\n=== INTRO ===")
for l in lines[:50]:
    print(l)

# Save full text to scratch for slice viewing if needed
with open(os.path.join(SCRATCH, "retest_report_clean.md"), "w", encoding="utf-8") as f:
    f.write(text)

print("\nSaved scratch/retest_report_clean.md")
