import sys, shutil
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

desktop = Path(r"C:\Users\Артем\Desktop")
ddp_src = Path(r"D:\Документы Victus\Рабочее\Сотрудники\Дэвид\Проект DDP Ru-CN\DDP Russia for Chinese Partners.docx")
clusters_src = Path(r"D:\Документы Victus\Рабочее\Сотрудники\Дэвид\Equipment from China\For David abiut ckasters and competitors.docx")

ddp_dest = desktop / "1_DDP Russia for Chinese Partners.docx"
clusters_dest = desktop / "2_China Equipment Clusters Strategy.docx"

if ddp_src.exists():
    shutil.copy2(ddp_src, ddp_dest)
    print(f"Copied DDP docx to Desktop: {ddp_dest}")

if clusters_src.exists():
    shutil.copy2(clusters_src, clusters_dest)
    print(f"Copied Clusters docx to Desktop: {clusters_dest}")
