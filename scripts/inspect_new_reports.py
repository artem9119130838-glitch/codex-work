import os
import sys

DOWNLOADS = r"C:\Users\Артем\Downloads"
REPO_DOCS = r"C:\Users\Артем\tender-rag-api\docs"
SCRATCH = r"C:\Codex_Personal\scratch"

out_lines = []

# 1. Inspect report (6).md
r6_path = os.path.join(DOWNLOADS, "report (6).md")
with open(r6_path, "r", encoding="utf-8", errors="ignore") as f:
    r6_content = f.read()

out_lines.append(f"=== report (6).md ({len(r6_content)} chars) ===")
lines = r6_content.splitlines()
out_lines.extend(lines[:40])
out_lines.append("\n...\nHeaders in report (6).md:")
for l in lines:
    if l.startswith("#"):
        out_lines.append(f"  {l}")

# 2. Inspect cost_report (1).md
cost_path = os.path.join(DOWNLOADS, "cost_report (1).md")
with open(cost_path, "r", encoding="utf-8", errors="ignore") as f:
    cost_content = f.read()

out_lines.append(f"\n=== cost_report (1).md ({len(cost_content)} chars) ===")
out_lines.extend(cost_content.splitlines())

with open(os.path.join(SCRATCH, "new_reports_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Saved new_reports_summary.txt")
