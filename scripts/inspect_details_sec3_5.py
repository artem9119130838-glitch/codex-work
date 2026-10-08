import os
import sys

DOWNLOADS = r"C:\Users\Артем\Downloads"
REPO = r"C:\Users\Артем\tender-rag-api"
SCRATCH = r"C:\Codex_Personal\scratch"

r6_path = os.path.join(DOWNLOADS, "report (6).md")
with open(r6_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

out_lines = []
sec3 = text.split("## 3. Сводная таблица результатов обработки")[1].split("## 4. Детальные карточки")[0]
sec5 = text.split("## 5. Внедренные инженерные доработки по результатам тестирования")[1]

out_lines.append("=== СЕКЦИЯ 3 (Сводная таблица результатов обработки) ===")
out_lines.append(sec3.strip())

out_lines.append("\n=== СЕКЦИЯ 5 (Внедренные инженерные доработки) ===")
out_lines.append(sec5.strip())

resp_path = os.path.join(REPO, "docs", "roadmaps", "mikhail_response_to_artem_roadmap.md")
if os.path.exists(resp_path):
    with open(resp_path, "r", encoding="utf-8", errors="ignore") as f:
        out_lines.append("\n=== MIKHAIL RESPONSE TO ARTEM ROADMAP ===")
        out_lines.append(f.read().strip())

with open(os.path.join(SCRATCH, "sec3_5_summary.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Saved sec3_5_summary.txt")
