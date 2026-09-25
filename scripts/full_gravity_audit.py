#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Gravity Audit and Catalog Generator
=========================================
Автоматическая ревизия всех контуров (Personal, Shared, tender-rag-api, бэкапы):
1. Отсекает сторонние библиотеки вендоров (venv, site-packages, node_modules).
2. Находит дубликаты и устаревшие архивные копии.
3. Группирует скрипты по функциональным семействам (Tool Families).
4. Автоматически пересобирает codex_kb/SCRIPTS_CATALOG.md.
"""

import os
import sys
import hashlib
import time
from pathlib import Path
from collections import defaultdict

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

VENDOR_DIRS = {
    'venv', '.venv', 'site-packages', 'node_modules', '.vendor', 
    '__pycache__', 'dist-packages', '.git', '.idea', '.vscode'
}

DOMAINS = [
    {
        "id": "b24",
        "title": "1. CRM Битрикс24 (Чаты, Сделки, Лиды, Задачи, Вебхуки)",
        "keywords": ["bitrix", "b24", "crm", "deal", "lead"]
    },
    {
        "id": "1c",
        "title": "2. 1С:УНФ и OData API (Контрагенты, Заказы, Номенклатура)",
        "keywords": ["odata", "onec", "1c", "contractor", "saby", "dadata"]
    },
    {
        "id": "email",
        "title": "3. Почта (IMAP / SMTP / Обработка писем и вложений)",
        "keywords": ["imap", "smtp", "mail", "email", "inbox", "junk", "pdf_text"]
    },
    {
        "id": "hr",
        "title": "4. HR, Резюме и Кандидаты (Китай / ВЭД)",
        "keywords": ["candidate", "resume", "hr", "wechat", "china", "salary"]
    },
    {
        "id": "tender",
        "title": "5. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций",
        "keywords": ["tender", "lot", "chunker", "goz", "act", "nmck", "eval"]
    },
    {
        "id": "infra",
        "title": "6. Инфраструктура, VPS-сервер, Docker и Бэкапы",
        "keywords": ["vps", "backup", "inventory", "mass_replace", "verify", "preflight", "budget", "docker", "ssh"]
    },
    {
        "id": "windows",
        "title": "7. Windows, HP Victus 16, Дисплеи и Safe Mode",
        "keywords": ["victus", "safe_mode", "f8", "bcd", "acrobat", "display", "mpo", "snapshot"]
    },
    {
        "id": "session",
        "title": "8. Управление сессиями и сжатие ИИ-контекста",
        "keywords": ["session", "compress", "summary", "build_index", "audit"]
    }
]

def is_vendor(path):
    return any(v in path.parts for v in VENDOR_DIRS)

def file_hash(path):
    try:
        h = hashlib.md5()
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def extract_description(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [f.readline().strip() for _ in range(15)]
        
        # Look for docstring or comments
        desc_lines = []
        for line in lines:
            if line.startswith(('"""', "'''")):
                clean = line.replace('"""', '').replace("'''", '').strip()
                if clean:
                    desc_lines.append(clean)
            elif line.startswith(('#', '::', 'REM')):
                clean = line.lstrip('#:REM rem').strip()
                if clean and not clean.startswith('!/bin') and not clean.startswith('-*-') and not clean.startswith('@echo'):
                    desc_lines.append(clean)
            elif desc_lines and not line:
                break
        
        if desc_lines:
            return " ".join(desc_lines[:2])
    except Exception:
        pass
    return "Автоматизация рабочего процесса."

def classify_script(path, desc):
    full_str = f"{path.as_posix().lower()} {desc.lower()}"
    
    # Determine level
    level = "Базовый"
    if any(w in full_str for w in ["check", "sync", "patch", "filter", "excel", "eval", "golden", "v7", "advanced"]):
        level = "Расширенный"
    if any(w in full_str for w in ["reconcile", "build_rag", "workflow", "matrix", "demon", "mass"]):
        level = "Интеграционный"
    if any(w in full_str for w in ["verify", "test", "status", "diag", "preflight"]):
        level = "Диагностический"
        
    for dom in DOMAINS:
        if any(kw in full_str for kw in dom["keywords"]):
            return dom["id"], level
            
    # Default category based on path
    if "1c" in full_str:
        return "1c", level
    if "tender" in full_str:
        return "tender", level
    if "email" in full_str or "n8n" in full_str:
        return "email", level
    if "hr" in full_str:
        return "hr", level
    if "inventory" in full_str or "vps" in full_str:
        return "infra", level
    return "infra", level

def run_audit():
    root_personal = Path(r"C:\Codex_Personal")
    roots = [
        Path(r"C:\Codex_Personal"),
        Path(r"C:\Codex_Shared"),
        Path(r"C:\Users\Артем\tender-rag-api"),
        Path(r"D:\Soft\Codex Backup")
    ]
    
    print("=" * 60)
    print(" [AUDIT] ПОЛНАЯ РЕВИЗИЯ И ФОРМАТИРОВАНИЕ ГРАВИТИ")
    print("=" * 60)
    print(f"Сканирование контуров:\n" + "\n".join(f"  • {r}" for r in roots if r.exists()))
    
    raw_files = []
    vendor_skipped = 0
    
    for r in roots:
        if not r.exists():
            continue
        for ext in ['*.py', '*.ps1', '*.bat', '*.sh']:
            for p in r.glob(f"**/{ext}"):
                if is_vendor(p):
                    vendor_skipped += 1
                else:
                    raw_files.append(p)
                    
    print(f"\n[1/4] Всего файлов обнаружено: {len(raw_files) + vendor_skipped}")
    print(f"[2/4] Отсеяно сторонних библиотек (venv/vendor): {vendor_skipped}")
    print(f"[3/4] Отобрано чистых скриптов контура: {len(raw_files)}")
    
    # Hash check & deduplication
    by_hash = defaultdict(list)
    for p in raw_files:
        h = file_hash(p)
        if h:
            by_hash[h].append(p)
            
    unique_tools = []
    duplicate_count = 0
    
    for h, flist in by_hash.items():
        if len(flist) > 1:
            duplicate_count += (len(flist) - 1)
            # Pick the best representative path (prefer C:\Codex_Personal, then C:\Codex_Shared)
            flist_sorted = sorted(flist, key=lambda p: (
                0 if "Codex_Personal" in str(p) and "ARCHIVE" not in str(p) else
                1 if "Codex_Shared" in str(p) and "backup" not in str(p) else
                2 if "tender-rag-api" in str(p) else 3
            ))
            primary = flist_sorted[0]
            unique_tools.append((primary, flist[1:]))
        else:
            unique_tools.append((flist[0], []))
            
    print(f"[4/4] Исключено дубликатов и архивных копий: {duplicate_count}")
    print(f"      Уникальных боевых скриптов готово к учету: {len(unique_tools)}")
    
    # Categorize unique tools
    categorized = defaultdict(list)
    for primary, dups in unique_tools:
        # Ignore empty dummy __init__.py files
        if primary.name == '__init__.py' and primary.stat().st_size == 0:
            continue
        desc = extract_description(primary)
        dom_id, level = classify_script(primary, desc)
        categorized[dom_id].append({
            "name": primary.name,
            "path": primary.as_posix(),
            "level": level,
            "desc": desc,
            "duplicates": len(dups)
        })
        
    # Generate codex_kb/SCRIPTS_CATALOG.md
    catalog_path = root_personal / "codex_kb" / "SCRIPTS_CATALOG.md"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    
    dt = time.strftime('%Y-%m-%d %H:%M:%S')
    
    lines = [
        "# Единый каталог скриптов и автоматизаций контура (SCRIPTS_CATALOG)\n",
        f"> **Дата последней автоматической ревизии:** `{dt}`  ",
        f"> **Статус контура:** Уникальных проверенных скриптов: `{len(unique_tools)}` | Отсеяно дубликатов: `{duplicate_count}` | Библиотек вендоров: `{vendor_skipped}`.  ",
        "> **Архитектурный стандарт:** «Семейства инструментов» (Tool Families). Любые модификации группируются в одной ячейке от базового вызова к расширенным.\n",
        "---",
        "\n## 🧭 Навигация по доменам\n"
    ]
    
    for dom in DOMAINS:
        lines.append(f"- [{dom['title']}](#{dom['id']})")
        
    lines.append("\n---\n")
    
    for dom in DOMAINS:
        items = categorized.get(dom["id"], [])
        lines.append(f"<a id='{dom['id']}'></a>")
        lines.append(f"## {dom['title']}\n")
        lines.append("| Уровень / Роль | Скрипт | Расположение | Описание и модификации | Дублей в архивах |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        
        # Sort by level: Базовый -> Расширенный -> Интеграционный -> Диагностический
        order = {"Базовый": 0, "Расширенный": 1, "Интеграционный": 2, "Диагностический": 3}
        items_sorted = sorted(items, key=lambda x: (order.get(x["level"], 4), x["name"]))
        
        if not items_sorted:
            lines.append("| - | *Нет зарегистрированных скриптов* | - | - | - |")
        else:
            for it in items_sorted:
                p_display = it['path'].replace('C:/Codex_Personal/', '').replace('C:/Codex_Shared/', 'Shared: ')
                desc_clean = it['desc'].replace('|', '/')
                lines.append(f"| **{it['level']}** | `{it['name']}` | `{p_display}` | {desc_clean} | {it['duplicates']} |")
        lines.append("\n---\n")
        
    with open(catalog_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines).strip() + "\n")
        
    print(f"\n[OK] Каталог успешно пересобран и сохранен: {catalog_path}")
    print("=" * 60)
    print(" [SUCCESS] РЕВИЗИЯ ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 60)

if __name__ == '__main__':
    run_audit()
