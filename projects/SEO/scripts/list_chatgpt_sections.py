import os
import sys
import docx

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\Документы Victus\Рабочее\В работе\SEO GPT Проект\Итоговый отчёт для SEO-аудита CHATGPT.docx"
d = docx.Document(p)

print("=== CHATGPT AUDIT SUMMARY SECTIONS ===")
for i, p in enumerate(d.paragraphs):
    t = p.text.strip()
    if p.style and ('Heading 1' in p.style.name or 'Heading 2' in p.style.name):
        print(f"\n[{p.style.name}] {t}")
    elif any(t.startswith(f"{x}.") for x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]) and len(t) < 70:
        print(f"  -> {t}")
