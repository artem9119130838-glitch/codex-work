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
        "id": "ai_chats",
        "title": "1. Выгрузка, парсинг и фильтрация чатов ИИ (Gemini / ChatGPT / Claude)",
        "keywords": ["ai_chats", "conversations", "chat_operator", "parse_unresolved", "merge_small", "chats export"]
    },
    {
        "id": "supply_china",
        "title": "2. Снабжение и ВЭД в Китае (Дечжоу / Циндао, фонд 5000 RMB, возврат НДС)",
        "keywords": ["china", "supply", "wechat", "китайский снабженец", "gmv", "дечжоу", "циндао"]
    },
    {
        "id": "price_creating",
        "title": "3. Создание прайс-листов и коммерческих предложений из каталогов",
        "keywords": ["price", "прайс", "спецификаци", "дополнительное соглашение", "wgl"]
    },
    {
        "id": "hr_resume",
        "title": "4. Анализ резюме, RAG-база кандидатов и генерация ответов соискателям",
        "keywords": ["resume", "candidate", "соискател", "резюме", "clean_digits", "inbox_reply"]
    },
    {
        "id": "pc_migration",
        "title": "5. Перенос данных с ПК на ПК (HP Victus ⮂ MateBook ⮂ Mirror_E_Home)",
        "keywords": ["fix_paths", "victus", "matebook", "freefilesync", "ffs", "punto", "user.dic"]
    },
    {
        "id": "sprint_mikhail",
        "title": "6. Спринты Михаила, RAG ГОЗ и Архитектура сети VPS",
        "keywords": ["mikhail", "михаил", "bore", "wireguard", "architecture_map", "tender-rag-api", "deploy-tender", "tender_webhook", "deploy_tender"]
    },
    {
        "id": "windows_diagnostics",
        "title": "7. Windows Diagnostics, графика Victus 16, Safe Mode и дисплеи",
        "keywords": ["acrobat", "safe_mode", "f8", "bcd", "check_and_clean_pc", "сброс_кэша", "mpo", "weekly_run"]
    },
    {
        "id": "session_compression",
        "title": "8. Анализ истории чата, сжатие сессий и /learn",
        "keywords": ["session_compress", "full_gravity_audit", "summary", "build_index"]
    },
    {
        "id": "onec_bitrix_sync",
        "title": "9. Связка 1С:УНФ и Битрикс24 (OData, Контрагенты, Заказы, СКД)",
        "keywords": ["sync_to_bitrix", "check_contractor", "search_1c", "odata", "kpiменеджеров", "onec"]
    },
    {
        "id": "lead_inbound",
        "title": "10. Обработка новых лидов и Inbound-снабжение (Email AI Pipeline)",
        "keywords": ["run_imap", "text_cleaner", "unassociated", "junk_filter", "check_drive_access"]
    },
    {
        "id": "followup_sales",
        "title": "11. Follow-up продаж в сделках и реактивация клиентов",
        "keywords": ["reactivation", "golden_phrases", "follow_up", "followup", "deal_followup", "подогрев"]
    },
    {
        "id": "idempotent_crm_1c",
        "title": "12. Синхронизация лидов и компаний в 1С и Битрикс24 (Idempotent CRM)",
        "keywords": ["run_onec_sync", "reconcile_1c", "patch_n8n", "idempotent"]
    },
    {
        "id": "tenders_goz",
        "title": "13. Тендеры, АСТ ГОЗ и RAG-пайплайн спецификаций",
        "keywords": ["tender_lot", "chunker", "goz", "act", "nmck", "eval_min_context"]
    },
    {
        "id": "infra_vps",
        "title": "14. Инфраструктура, VPS-сервер, Docker и Бэкапы",
        "keywords": ["vps", "backup", "inventory", "mass_replace", "verify", "preflight", "budget", "vacuum", "sqlite-auto-vacuum"]
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
    if "chats export" in full_str or "gemini" in full_str:
        return "ai_chats", level
    if "price" in full_str or "прайс" in full_str:
        return "price_creating", level
    if "victus" in full_str or "matebook" in full_str:
        return "pc_migration", level
    if "1c" in full_str or "bitrix" in full_str or "b24" in full_str:
        return "onec_bitrix_sync", level
    if "tender" in full_str or "goz" in full_str:
        return "tenders_goz", level
    if "email" in full_str or "n8n" in full_str or "imap" in full_str:
        return "lead_inbound", level
    if "hr" in full_str or "resume" in full_str:
        return "hr_resume", level
    if "victus" in full_str or "safe_mode" in full_str or "display" in full_str:
        return "windows_diagnostics", level
    return "infra_vps", level

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
