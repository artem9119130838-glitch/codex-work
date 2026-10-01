import sys
from pathlib import Path
import docx

sys.stdout.reconfigure(encoding="utf-8")

ddp_dir = Path(r"D:\Документы Victus\Рабочее\Сотрудники\Дэвид\Проект DDP Ru-CN")

for f in ddp_dir.glob("*.docx"):
    print(f"\n==========================================")
    print(f"FILE: {f.name} ({f.stat().st_size} bytes)")
    doc = docx.Document(str(f))
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    print(f"Total non-empty paragraphs: {len(paras)}")
    for i, p in enumerate(paras[:10]):
        print(f"  [{i}]: {p[:100]}")
