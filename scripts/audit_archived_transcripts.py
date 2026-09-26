#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/audit_archived_transcripts.py
======================================
Глубокий аудит архивных чатов Antigravity и ликвидация «слепой зоны VPS»:
1. Сканирует все transcript.jsonl в директории brain за любой период (включая свыше 35 дней или всю историю).
2. Извлекает пользовательские запросы (USER_INPUT, USER_EXPLICIT), директивы, правила, ограничения.
3. Парсит SSH/SCP/bash команды создания и модификации скриптов на VPS (/Storage/, /root/scripts/, crontab).
4. Поддерживает вызов модуля зеркалирования боевых скриптов с хоста VPS (1 сессия SSH) в scripts/vps/.
5. Формирует отчеты в scratch/transcript_audit_report.json и scratch/transcript_audit_report.md.
"""

import os
import sys
import glob
import json
import re
import argparse
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

DIRECTIVE_KEYWORDS = [
    r"запрещ[её]н", r"нельзя", r"никогда", r"всегда", r"правил", r"не смей",
    r"строго", r"обязательно", r"запомни", r"не делай", r"ошибка", r"не так",
    r"исправь", r"регламент", r"политика", r"стандарт", r"внимание", r"важно",
    r"ловушк", r"недисциплин", r"сбой", r"проигнорир", r"почему ты", r"забыл",
    r"конец чата", r"сжать сесси", r"заверши", r"урок", r"не трогай", r"только чтени"
]
DIRECTIVE_REGEX = re.compile("|".join(DIRECTIVE_KEYWORDS), re.IGNORECASE)

VPS_KEYWORDS = [
    r"/Storage/", r"/root/scripts", r"monitor_disk", r"run_server_backup",
    r"backup-sql", r"crontab", r"cron\.weekly", r"n8n-sqlite-auto-vacuum",
    r"auto_deploy\.sh", r"deploy-tender\.sh", r"b24_daily_analytics_sync",
    r"clear_tmp\.sh", r"/usr/local/bin/"
]
VPS_REGEX = re.compile("|".join(VPS_KEYWORDS), re.IGNORECASE)

CATEGORIES = {
    "session_discipline": ["конец чата", "сжать", "сесси", "ловушк", "вежливост", "проигнорир", "дисциплин", "запомни", "summary"],
    "b2b_sales_email": ["реанимаци", "follow up", "followup", "писем", "письмо", "черновик", "roundcube", "аккуратно уточнить", "тональност", "21 день", "кп"],
    "china_hr_supply": ["китай", "дечжоу", "циндао", "снабжен", "nancy", "анна", "ванг", "откат", "гмв", "gmv", "退税", "оклад", "5000", "5 000"],
    "windows_victus": ["victus", "видеокарт", "код 43", "intel", "nvidia", "mpo", "safe mode", "f8", "диспле", "экран", "acrobat", "монитор"],
    "crm_1c_bitrix": ["битрикс", "bitrix", "odata", "1с", "унф", "лид", "контрагент", "инн", "дело", "звонок", "crm_todo"],
    "git_vps_security": ["git", "vps", "109.248.170.181", "ключ", "ssh", "только чтение", "read-only", "бэкап", "docker", "metabase"],
    "tenders_ast_goz": ["тендер", "гоз", "аст", "извещени", "номер процедуры", "26", "спецификац"]
}

def parse_iso(ts_str):
    try:
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except Exception:
        return None

def run_audit(mode="older_than_35", days_val=35, mirror_vps=False):
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days_val)
    
    files = glob.glob(str(BRAIN_DIR / "*" / ".system_generated" / "logs" / "transcript.jsonl"))
    print(f"Найдено transcript.jsonl файлов: {len(files)}")
    print(f"Режим фильтрации аудита: {mode} (отсечка: {cutoff.strftime('%Y-%m-%d')})")
    
    extracted_directives = []
    vps_script_ops = []
    sessions_analyzed = 0
    total_messages_scanned = 0
    
    for fpath in files:
        conv_id = Path(fpath).parent.parent.parent.name
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            continue
            
        sessions_analyzed += 1
        
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
            content = data.get("content", "").strip()
            if not content:
                continue
                
            dt = parse_iso(ts_str) if ts_str else None
            
            # Применение временного фильтра
            if mode == "recent":
                if dt and dt < cutoff:
                    continue
            elif mode == "older_than_35":
                if dt and dt >= cutoff:
                    continue
            # mode == "all" не пропускает по дате
            
            # 1. Поиск директив пользователя
            if src == "USER_EXPLICIT" and stype == "USER_INPUT":
                match = DIRECTIVE_REGEX.search(content)
                if match:
                    assigned_cat = "other"
                    for cat_id, keywords in CATEGORIES.items():
                        if any(kw in content.lower() for kw in keywords):
                            assigned_cat = cat_id
                            break
                            
                    extracted_directives.append({
                        "conv_id": conv_id,
                        "step_index": data.get("step_index", idx),
                        "created_at": ts_str,
                        "category": assigned_cat,
                        "matched_keyword": match.group(0),
                        "content": content
                    })
                    
            # 2. Поиск операций создания скриптов на VPS
            vps_match = VPS_REGEX.search(content)
            if vps_match:
                if any(act in content for act in ["cat <<", "echo ", "touch ", "chmod ", "crontab", "scp ", "rsync ", "nano ", "vim "]):
                    vps_script_ops.append({
                        "conv_id": conv_id,
                        "created_at": ts_str,
                        "source": src,
                        "matched": vps_match.group(0),
                        "sample": content[:250].replace("\n", " ")
                    })

    print(f"Сессий проанализировано: {sessions_analyzed}")
    print(f"Всего шагов проверено: {total_messages_scanned}")
    print(f"Найдено директив пользователя: {len(extracted_directives)}")
    print(f"Найдено операций с VPS-скриптами: {len(vps_script_ops)}")
    
    # Зеркалирование VPS если запрошено
    if mirror_vps:
        print("\n--- Запуск односессионного зеркалирования VPS ---")
        try:
            from scripts.mirror_vps_scripts import mirror_scripts
            mirror_scripts()
        except Exception as e:
            print(f"Ошибка вызова mirror_scripts: {e}")

    # Сохраняем отчет JSON
    full_report = {
        "audit_meta": {
            "mode": mode,
            "days_val": days_val,
            "created_at": now.isoformat(),
            "sessions_analyzed": sessions_analyzed,
            "total_messages_scanned": total_messages_scanned,
            "directives_count": len(extracted_directives),
            "vps_ops_count": len(vps_script_ops)
        },
        "directives": extracted_directives,
        "vps_operations": vps_script_ops
    }
    
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(full_report, f, ensure_ascii=False, indent=2)
    print(f"Отчет сохранен в JSON: {REPORT_PATH}")
    
    # Генерация Markdown
    by_cat = defaultdict(list)
    for it in extracted_directives:
        by_cat[it["category"]].append(it)
        
    md_lines = [
        f"# Сводный аудит архивных чатов Antigravity ({mode})",
        f"**Дата проведения:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"**Проверено сессий:** {sessions_analyzed}, **Всего сообщений:** {total_messages_scanned}",
        f"**Извлечено директив:** {len(extracted_directives)}, **Операций с VPS:** {len(vps_script_ops)}\n",
        "---"
    ]
    
    cat_titles = {
        "session_discipline": "1. Дисциплина закрытия сессий, сжатие и ловушка вежливости",
        "b2b_sales_email": "2. B2B продажи, Follow-up, реанимация и коммуникации",
        "china_hr_supply": "3. Снабжение и найм в Китае (Дечжоу, Циндао, фонд, оклады)",
        "windows_victus": "4. Windows Diagnostics, железо HP Victus, экраны, BCD, Acrobat",
        "crm_1c_bitrix": "5. Интеграция 1С:УНФ, Битрикс24, OData, Лиды и Сделки",
        "git_vps_security": "6. Git, VPS-сервер, Docker, Metabase и бэкапы",
        "tenders_ast_goz": "7. Тендеры, АСТ ГОЗ и спецификации",
        "other": "8. Прочие бизнес-директивы"
    }
    
    for cat_id, title in cat_titles.items():
        items = by_cat.get(cat_id, [])
        md_lines.append(f"\n## {title} (Записей: {len(items)})")
        if not items:
            md_lines.append("_Нет зафиксированных директив в этом фильтре._")
            continue
        for it in items[:25]:
            date_short = it['created_at'][:10] if it.get('created_at') else "н/д"
            txt = it['content'].replace("\n", " ")
            if len(txt) > 300:
                txt = txt[:297] + "..."
            md_lines.append(f"- **[{date_short}] [ID: {it['conv_id'][:8]}]** `{it['matched_keyword']}`: {txt}")
            
    md_lines.extend([
        "\n---",
        f"\n## 9. Хронология операций создания/модификации боевых скриптов на VPS (Записей: {len(vps_script_ops)})"
    ])
    for op in vps_script_ops[:30]:
        date_short = op.get('created_at', '')[:10] if op.get('created_at') else "н/д"
        md_lines.append(f"- **[{date_short}] [{op['source']}]** `{op['matched']}`: {op['sample']}")
        
    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Отчет сохранен в Markdown: {REPORT_MD_PATH}")
    return len(extracted_directives)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Аудит архивных логов brain и слепой зоны VPS")
    parser.add_argument("--mode", choices=["all", "older_than_35", "recent"], default="older_than_35", help="Режим фильтрации")
    parser.add_argument("--days", type=int, default=35, help="Количество дней для отсечки")
    parser.add_argument("--mirror-vps", action="store_true", help="Запустить односессионный опрос и зеркалирование VPS")
    args = parser.parse_args()
    
    run_audit(mode=args.mode, days_val=args.days, mirror_vps=args.mirror_vps)
