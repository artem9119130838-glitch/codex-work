import sys
from pathlib import Path
import docx
import shutil

sys.stdout.reconfigure(encoding="utf-8")

file_path = Path(r"D:\Документы Victus\Рабочее\Сотрудники\Дэвид\Equipment from China\For David abiut ckasters and competitors.docx")
backup_path = file_path.with_name("For David abiut ckasters and competitors.bak.docx")

if not backup_path.exists():
    shutil.copy2(file_path, backup_path)
    print(f"Created backup: {backup_path}")

doc = docx.Document(str(file_path))

# 1. Clean para 0
for idx, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if "Вот структурированный" in txt:
        p.text = ""
    elif txt == "David，您好！":
        p.text = "中国工业设备供俄集群化战略方案（Equipment Clusters Export Strategy）"
    elif "如果这个方向并不符合您的判断" in txt:
        p.text = "我们这边已经成功跑通了“热工设备（热处理设备）”这个方向，并通过俄罗斯本土SEO矩阵验证了这一模式的有效性，目前正源源不断地获得俄罗斯企业真实的采购询盘。"
    elif "例如道路标线、钢管等" in txt:
        p.text = "这种方式可以帮助我们以最低成本、最高效率快速验证俄罗斯市场的真实工业采购需求（Value Probe）。"
    elif "但我们最缺的核心优势是：价格竞争力" in txt:
        p.text = "我们与您深度合作的核心关键在于：深入挖掘中国一手实力制造工厂，拿到最具竞争力的出厂底价（比公开市场低10–15%）。"
    elif "可以拿到有优势价格（甚至接近独家价格）的产品" in txt:
        p.text = "👉 因此，我们重点选择：能够直连源头工厂、具备绝对价格优势的产品品类，而不是那些已经被多层转包商炒热的同质化产品。"

# Remove empty paragraphs at the very beginning
clean_doc = docx.Document()
first_non_empty = False
for p in doc.paragraphs:
    if not first_non_empty and not p.text.strip():
        continue
    first_non_empty = True
    new_p = clean_doc.add_paragraph(p.text)
    new_p.style = p.style

clean_doc.save(str(file_path))
print(f"Updated and saved clean docx: {file_path}")
