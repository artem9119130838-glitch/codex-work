import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCRATCH = r"C:\Codex_Personal\scratch"

path = os.path.join(SCRATCH, "retest_report_clean.md")
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Extract Section 2 (Таблица) and Section 3 (Детали)
sec2 = text.split("## 2. Сводная таблица результатов обработки (Итерация 2: Пакет 1)")[1].split("## 3. Детальные карточки сделок")[0]
sec3 = text.split("## 3. Детальные карточки сделок и доказательная база")[1].split("## 4. Сводка расходов")[0]

print("=== СЕКЦИЯ 2: Сводная таблица ===")
print(sec2.strip())

print("\n=== ВЫЖИМКА ИЗ СЕКЦИИ 3 (Сделки и ТН ВЭД) ===")
# Let's inspect deals and HS codes
deals = sec3.split("### Сделка №")
for d in deals[1:]:
    lines = d.strip().splitlines()
    title = lines[0]
    # find lines about VED / ТН ВЭД / номенклатура
    ved_lines = [l for l in lines if any(k in l.lower() for k in ["вэд", "тн вэд", "номенклатур", "позици", "товар", "статус", "причина", "hs_code", "ошибк"])]
    print(f"\n[Сделка №{title}]")
    for vl in ved_lines[:6]:
        print(" ", vl)
