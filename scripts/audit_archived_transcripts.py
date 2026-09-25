#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_archived_transcripts.py
======================================
Аудит логов архивных чатов Antigravity (brain/*/transcript.jsonl) за последние 30-45 дней:
1. Сканирует все transcript.jsonl в директории brain.
2. Извлекает пользовательские запросы (USER_INPUT, USER_EXPLICIT).
3. Выделяет директивы, бизнес-правила, ограничения, замечания и уроки.
4. Классифицирует по темам (B2B, CRM, 1C, Victus, Китай, Git, Session Discipline).
5. Сохраняет структурированный отчет в scratch/transcript_audit_report.json и выводит сводку.
"""

import os
import sys
import glob
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BRAIN_DIR = Path(r"C:\Users\Артем\.gemini\antigravity\brain")
REPORT_PATH = Path(r"C:\Codex_Personal\scratch\transcript_audit_report.json")
REPORT_MD_PATH = Path(r"C:\Codex_Personal\scratch\transcript_audit_report.md")

# Ключевые паттерны директив, ограничений и замечаний пользователя
DIRECTIVE_KEYWORDS = [
    r"запрещ[её]н", r"нельзя", r"никогда", r"всегда", r"правил", r"не смей",
    r"строго", r"обязательно", r"запомни", r"не делай", r"ошибка", r"не так",
    r"исправь", r"регламент", r"политика", r"стандарт", r"внимание", r"важно",
    r"ловушк", r"недисциплин", r"сбой", r"проигнорир", r"почему ты", r"забыл",
    r"конец чата", r"сжать сесси", r"заверши", r"урок", r"не трогай", r"только чтени"
]
DIRECTIVE_REGEX = re.compile("|".join(DIRECTIVE_KEYWORDS), re.IGNORECASE)

CATEGORIES = {
    "session_discipline": ["конец чата", "сжать", "сесси", "ловушк", "вежливост", "проигнорир", "дисциплин", "запомни", "summary"],
    "b2b_sales_email": ["реанимаци", "follow up", "followup", "писем", "письмо", "черновик", "roundcube", "аккуратно уточнить", "тональност", "21 день", "кп"],
    "china_hr_supply": ["китай", "дечжоу", "циндао", "снабжен", "nancy", "анна", "ванг", "откат", "гмв", "gmv", "退税", "оклад", "5000", "5 000"],
    "windows_victus": ["victus", "видеокарт", "код 43", "intel", "nvidia", "mpo", "safe mode", "f8", "диспле", "экран", "acrobat", "монитор"],
    "crm_1c_bitrix": ["битрикс", "bitrix", "odata", "1с", "унф", "лид", "контрагент", "инн", "дело", "звонок", "crm_todo"],
    "git_vps_security": ["git", "vps", "109.248.170.181", "ключ", "ssh", "только чтение", "read-only", "бэкап", "docker", "metabase"]
}

def parse_iso(ts_str):
    try:
        # e.g. 2026-09-25T16:09:53Z or 2026-09-25T16:09:53+03:00
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None

def run_audit(days_back=35):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_back)
    
    files = glob.glob(str(BRAIN_DIR / "*" / ".system_generated" / "logs" / "transcript.jsonl"))
    print(f"Найдено transcript.jsonl файлов: {len(files)}")
    print(f"Период аудита: с {cutoff.strftime('%Y-%m-%d')} по {now.strftime('%Y-%m-%d')} ({days_back} дней)")
    
    extracted_items = []
    sessions_analyzed = 0
    total_messages_scanned = 0
    
    for fpath in files:
        conv_id = Path(fpath).parent.parent.parent.name
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            continue
            
        sessions_analyzed += 1
        conv_has_recent = False
        
        for idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
                
            total_messages_scanned += 1
            src = data.get("source")
            stype = data.get("type")
            ts_str = data.get("created_at")
            
            if src != "USER_EXPLICIT" or stype != "USER_INPUT":
                continue
                
            dt = parse_iso(ts_str) if ts_str else None
            if dt and dt < cutoff:
                continue
                
            content = data.get("content", "").strip()
            if not content:
                continue
                
            # Проверяем наличие ключевых слов директив или правил
            match = DIRECTIVE_REGEX.search(content)
            if not match:
                continue
                
            # Определяем категорию
            assigned_cat = "other"
            for cat_id, keywords in CATEGORIES.items():
                if any(kw in content.lower() for kw in keywords):
                    assigned_cat = cat_id
                    break
                    
            extracted_items.append({
                "conv_id": conv_id,
                "step_index": data.get("step_index", idx),
                "created_at": ts_str,
                "category": assigned_cat,
                "matched_keyword": match.group(0),
                "content": content
            })
            conv_has_recent = True
            
    print(f"Проанализировано сессий: {sessions_analyzed}")
    print(f"Всего шагов проверено: {total_messages_scanned}")
    print(f"Найдено релевантных директив/требований пользователя: {len(extracted_items)}")
    
    # Сортируем по времени (свежие в конце или по порядку)
    extracted_items.sort(key=lambda x: x.get("created_at") or "")
    
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(extracted_items, f, ensure_ascii=False, indent=2)
    print(f"Отчет сохранен в JSON: {REPORT_PATH}")
    
    # Группировка по категориям для генерации Markdown-отчета
    by_cat = defaultdict(list)
    for it in extracted_items:
        by_cat[it["category"]].append(it)
        
    md_lines = [
        f"# Сводный аудит директив и бизнес-требований пользователя за {days_back} дней",
        f"**Дата аудита:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Проверено сессий:** {sessions_analyzed}, **Найдено замечаний/директив:** {len(extracted_items)}\n",
        "---"
    ]
    
    cat_titles = {
        "session_discipline": "1. Дисциплина закрытия сессий, сжатие и ловушка вежливости",
        "b2b_sales_email": "2. B2B продажи, Follow-up, реанимация и правила коммуникаций",
        "china_hr_supply": "3. Снабжение и найм в Китае (Дечжоу, Циндао, фонд, оклады)",
        "windows_victus": "4. Windows Diagnostics, железо HP Victus, экраны, BCD, Acrobat",
        "crm_1c_bitrix": "5. Интеграция 1С:УНФ, Битрикс24, OData, Лиды и Сделки",
        "git_vps_security": "6. Git, VPS-сервер, Docker, Metabase и безопасность",
        "other": "7. Прочие важные директивы"
    }
    
    for cat_id, title in cat_titles.items():
        items = by_cat.get(cat_id, [])
        md_lines.append(f"\n## {title} (Записей: {len(items)})")
        if not items:
            md_lines.append("_Нет зафиксированных директив в этом периоде._")
            continue
            
        for it in items:
            date_short = it['created_at'][:10] if it.get('created_at') else "н/д"
            # Первые 300 символов или полный текст если короткий
            txt = it['content'].replace("\n", " ")
            if len(txt) > 350:
                txt = txt[:347] + "..."
            md_lines.append(f"- **[{date_short}] [ID: {it['conv_id'][:8]}]** `{it['matched_keyword']}`: {txt}")
            
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Отчет сохранен в Markdown: {REPORT_MD_PATH}")
    
    return len(extracted_items)

if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 35
    run_audit(days)
