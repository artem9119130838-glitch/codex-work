# -*- coding: utf-8 -*-
"""
b24_daily_audit_guard.py
Суточный аудит модификаций Битрикс24 (Anti-Tamper & Mass Change Watchdog).
Запускается 2-3 раза в день и в конце рабочего дня.
Анализирует все изменения за текущие сутки (с 00:00 MSK):
- Сделки (crm.deal.list)
- Лиды (crm.lead.list)
- Компании / Контрагенты (crm.company.list)
- Контакты (crm.contact.list)

Если с одного аккаунта/ключа изменено более N сущностей (по умолчанию: 50),
формирует отчет о масштабе изменений и отправляет:
1. В личный чат Битрикс24 Артему (User 1)
2. На рабочую почту salman@longwang.ru
3. На личную почту artem9119130838@gmail.com
"""

import os
import sys
import json
import ssl
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import requests

def load_env():
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), "projects", "1c_odata", ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in env_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
            break

def b24_call(method, payload=None):
    webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
    if not webhook or "http" not in webhook:
        raise ValueError("BITRIX24_WEBHOOK_URL is not configured in .env")
    url = webhook + method
    res = requests.post(url, json=payload or {}, timeout=30)
    res.raise_for_status()
    return res.json()

def get_users_map():
    users_map = {}
    try:
        r = b24_call("user.get", {"ACTIVE": True})
        for u in r.get("result", []):
            uid = str(u.get("ID"))
            name = f"{u.get('NAME', '')} {u.get('LAST_NAME', '')}".strip()
            users_map[uid] = name or f"User {uid}"
    except Exception as e:
        print(f"[WARN] Failed to fetch users map: {e}")
    users_map["0"] = "Система / Робот"
    users_map["1"] = "Артем (Admin / Webhook ID 1)"
    return users_map

def fetch_all_entities_since(entity_type, cutoff_str, select_fields):
    """Выгрузка всех измененных сущностей заданного типа с пагинацией"""
    method = f"crm.{entity_type}.list"
    all_items = []
    start = 0
    while True:
        payload = {
            "filter": {">=DATE_MODIFY": cutoff_str},
            "select": select_fields,
            "order": {"DATE_MODIFY": "DESC"},
            "start": start
        }
        res = b24_call(method, payload)
        items = res.get("result", [])
        all_items.extend(items)
        total = res.get("total", 0)
        start += len(items)
        if start >= total or not items:
            break
    return all_items

def send_email_report(recipients, subject, text_content, html_content=None):
    smtp_server = os.getenv("SMTP_SERVER", "mail.hostland.ru")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    smtp_user = os.getenv("IMAP_USER", "sales@longwang.ru")
    smtp_pass = os.getenv("IMAP_PASSWORD", "")

    if not smtp_pass:
        print("[FAIL] SMTP password not found in .env")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"CRM Sentinel Guard <{smtp_user}>"
    msg["To"] = ", ".join(recipients)

    part1 = MIMEText(text_content, "plain", "utf-8")
    msg.attach(part1)

    if html_content:
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part2)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context, timeout=20) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipients, msg.as_string())
        print(f"[OK] Email успешно отправлен на адреса: {', '.join(recipients)}")
        return True
    except Exception as e:
        print(f"[FAIL] Ошибка отправки Email: {e}")
        return False

def send_b24_chat(user_id, message_bb):
    try:
        b24_call("im.message.add", {
            "DIALOG_ID": str(user_id),
            "MESSAGE": message_bb
        })
        print(f"[OK] Сообщение отправлено в чат Битрикс24 (User ID: {user_id})")
        return True
    except Exception as e:
        print(f"[FAIL] Ошибка отправки в чат Битрикс24: {e}")
        return False

def run_daily_audit(threshold=50, is_test=False, dry_run=False):
    load_env()
    users_map = get_users_map()

    # Начало текущих суток по времени MSK (+03:00)
    now_msk = datetime.now(timezone(timedelta(hours=3)))
    start_of_day = now_msk.replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_str = start_of_day.strftime("%Y-%m-%d %H:%M:%S")

    print("=" * 70)
    print(f"СУТОЧНЫЙ АУДИТ ИЗМЕНЕНИЙ CRM: {start_of_day.strftime('%d.%m.%Y')} (с 00:00 MSK)")
    print(f"Время проверки: {now_msk.strftime('%Y-%m-%d %H:%M:%S MSK')} | Порог тревоги: {threshold} сущностей")
    print("=" * 70)

    # Сканирование 4 ключевых типов сущностей
    print("1. Сканирование сделок (crm.deal)...")
    deals = fetch_all_entities_since("deal", cutoff_str, ["ID", "TITLE", "DATE_MODIFY", "MODIFY_BY_ID", "STAGE_ID", "OPPORTUNITY"])
    print(f"   Изменено сделок: {len(deals)}")

    print("2. Сканирование лидов (crm.lead)...")
    leads = fetch_all_entities_since("lead", cutoff_str, ["ID", "TITLE", "DATE_MODIFY", "MODIFY_BY_ID", "STATUS_ID"])
    print(f"   Изменено лидов: {len(leads)}")

    print("3. Сканирование компаний / контрагентов (crm.company)...")
    companies = fetch_all_entities_since("company", cutoff_str, ["ID", "TITLE", "DATE_MODIFY", "MODIFY_BY_ID"])
    print(f"   Изменено компаний: {len(companies)}")

    print("4. Сканирование контактов (crm.contact)...")
    contacts = fetch_all_entities_since("contact", cutoff_str, ["ID", "NAME", "LAST_NAME", "DATE_MODIFY", "MODIFY_BY_ID"])
    print(f"   Изменено контактов: {len(contacts)}")

    total_changes = len(deals) + len(leads) + len(companies) + len(contacts)

    # Агрегация по пользователям
    user_stats = {}
    def track(items, entity_name):
        for item in items:
            uid = str(item.get("MODIFY_BY_ID") or "0")
            if uid not in user_stats:
                user_stats[uid] = {"name": users_map.get(uid, f"User {uid}"), "deals": 0, "leads": 0, "companies": 0, "contacts": 0, "total": 0}
            user_stats[uid][entity_name] += 1
            user_stats[uid]["total"] += 1

    track(deals, "deals")
    track(leads, "leads")
    track(companies, "companies")
    track(contacts, "contacts")

    # Проверка порога тревоги
    alarms = []
    for uid, stats in user_stats.items():
        if stats["total"] >= threshold:
            alarms.append((uid, stats))

    is_alert = len(alarms) > 0 or is_test

    # Формирование отчета
    status_header = "🚨 ТРЕВОГА: МАССОВАЯ МОДИФИКАЦИЯ ДАННЫХ В CRM!" if len(alarms) > 0 else ("🔍 ТЕСТОВЫЙ КОНТРОЛЬНЫЙ ОТЧЕТ СТОРОЖЕВОГО КОНТУРА" if is_test else "✅ СУТОЧНЫЙ АУДИТ CRM: ВСЕ ШТАТНО")

    # BB-Code для Битрикс24
    bb_lines = [
        f"[B]{status_header}[/B]",
        f"📅 [B]Дата отчета:[/B] {now_msk.strftime('%d.%m.%Y %H:%M:%S MSK')} (за сутки с 00:00)",
        f"📊 [B]Всего изменений за день:[/B] {total_changes} шт (Сделок: {len(deals)}, Лидов: {len(leads)}, Компаний: {len(companies)}, Контактов: {len(contacts)})",
        f"🎯 [B]Порог алертов:[/B] {threshold} сущностей на одного сотрудника\n"
    ]

    if alarms:
        bb_lines.append("[B]⚠️ ВЫЯВЛЕНА АНОМАЛЬНАЯ АКТИВНОСТЬ (ПРЕВЫШЕН ПОРОГ):[/B]")
        for uid, st in alarms:
            bb_lines.append(f"🔴 [B]{st['name']} (ID {uid}):[/B] [B]{st['total']} сущностей[/B] (Сделок: {st['deals']}, Лидов: {st['leads']}, Компаний: {st['companies']}, Контактов: {st['contacts']})")
        bb_lines.append("\n👉 [B]РЕКОМЕНДАЦИЯ:[/B] Если это не ваша ручная работа — запросите суточный откат у техподдержки Битрикс24 или восстановите из локального дампа!")
    else:
        bb_lines.append("🔹 [B]Сводка активности сотрудников за день:[/B]")
        if not user_stats:
            bb_lines.append("   Изменений данных сегодня не зафиксировано.")
        for uid, st in sorted(user_stats.items(), key=lambda x: x[1]["total"], reverse=True):
            bb_lines.append(f"   • {st['name']} (ID {uid}): {st['total']} шт (Сделок: {st['deals']}, Лидов: {st['leads']}, Компаний: {st['companies']}, Контактов: {st['contacts']})")

    # Примеры затронутых сделок
    if deals:
        sample_deals = [f"#{d.get('ID')} ({d.get('TITLE', '')[:30]}...)" for d in deals[:5]]
        bb_lines.append(f"\nПримеры измененных сделок: {', '.join(sample_deals)}")

    bb_message = "\n".join(bb_lines)

    # Текстовый вариант для Email
    text_message = bb_message.replace("[B]", "").replace("[/B]", "").replace("[I]", "").replace("[/I]", "")
    subject = f"[{'ТРЕВОГА' if len(alarms)>0 else 'ТЕСТ' if is_test else 'ОТЧЕТ'}] Суточный аудит CRM ({now_msk.strftime('%d.%m.%Y')}) — изменений: {total_changes}"

    # HTML вариант для красивого письма
    html_lines = [
        f"<h2>{status_header}</h2>",
        f"<p><b>Дата отчета:</b> {now_msk.strftime('%d.%m.%Y %H:%M:%S MSK')} (за сутки с 00:00)</p>",
        f"<p><b>Всего изменений за день:</b> {total_changes} шт (Сделок: {len(deals)}, Лидов: {len(leads)}, Компаний: {len(companies)}, Контактов: {len(contacts)})</p>",
        f"<p><b>Порог тревоги:</b> {threshold} сущностей на сотрудника</p>",
        "<hr/>"
    ]
    if alarms:
        html_lines.append("<h3 style='color: red;'>⚠️ ВЫЯВЛЕНА АНОМАЛЬНАЯ АКТИВНОСТЬ (ПРЕВЫШЕН ПОРОГ):</h3><ul>")
        for uid, st in alarms:
            html_lines.append(f"<li><b>{st['name']} (ID {uid}):</b> {st['total']} сущностей (Сделок: {st['deals']}, Лидов: {st['leads']}, Компаний: {st['companies']}, Контактов: {st['contacts']})</li>")
        html_lines.append("</ul><p><b>👉 РЕКОМЕНДАЦИЯ:</b> Запросите суточный откат у техподдержки Битрикс24 или восстановите из локального дампа.</p>")
    else:
        html_lines.append("<h3>Сводка активности сотрудников за день:</h3><ul>")
        for uid, st in sorted(user_stats.items(), key=lambda x: x[1]["total"], reverse=True):
            html_lines.append(f"<li><b>{st['name']} (ID {uid}):</b> {st['total']} шт (Сделок: {st['deals']}, Лидов: {st['leads']}, Компаний: {st['companies']}, Контактов: {st['contacts']})</li>")
        html_lines.append("</ul>")

    html_message = "".join(html_lines)

    print("\n--- ТЕКСТ СВОДКИ ДЛЯ ОТПРАВКИ ---")
    print(text_message)
    print("---------------------------------\n")

    recipients = ["salman@longwang.ru", "artem9119130838@gmail.com"]

    if dry_run:
        print("[DRY-RUN] Отправка пропущена (режим сухого прогона)")
        return

    # 1. Отправка в личный чат Битрикс24
    send_b24_chat(user_id=1, message_bb=bb_message)

    # 2. Отправка на 2 почтовых ящика
    send_email_report(recipients, subject, text_message, html_message)

    # 3. Сохранение снимка на диск
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/b24_daily_audit_{now_msk.strftime('%Y%m%d')}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": now_msk.isoformat(),
            "total_changes": total_changes,
            "threshold": threshold,
            "alarms": alarms,
            "user_stats": user_stats
        }, f, ensure_ascii=False, indent=2)
    print(f"[OK] Снимок аудита сохранен в {log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Суточный аудит модификаций Битрикс24")
    parser.add_argument("--threshold", type=int, default=50, help="Порог тревоги (по умолчанию: 50)")
    parser.add_argument("--test", action="store_true", help="Тестовый контрольный запуск со статусом ТЕСТ")
    parser.add_argument("--dry-run", action="store_true", help="Сухой прогон без отправки сообщений")
    args = parser.parse_args()

    run_daily_audit(threshold=args.threshold, is_test=args.test, dry_run=args.dry_run)
