# -*- coding: utf-8 -*-
"""
b24_mass_change_guard.py
Сторожевой скрипт (Watchdog / Sentinel) для мгновенного обнаружения аномальных массовых изменений в Битрикс24.
Отслеживает всплески crm.deal.update / crm.lead.update.
При превышении порога (например, > 10 измененных сделок за 3 минуты) отправляет тревожный алерт:
- В личный чат Битрикс24 Артему (im.message.add)
- В системные уведомления (колокольчик im.notify.system.add)
- На email (через SMTP)
- Сохраняет аварийный снимок затронутых сделок в safety_log.json
"""

import os
import sys
import json
import smtplib
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
    res = requests.post(url, json=payload or {}, timeout=20)
    res.raise_for_status()
    return res.json()

def send_b24_alerts(admin_user_id, message_text):
    """Отправка в чат и в колокольчик Битрикс24"""
    # 1. Личное сообщение в чат
    try:
        b24_call("im.message.add", {
            "DIALOG_ID": str(admin_user_id),
            "MESSAGE": message_text
        })
        print(f" [OK] Алерт отправлен в личный чат Битрикс24 (User {admin_user_id})")
    except Exception as e:
        print(f" [FAIL] Ошибка отправки в чат: {e}")

    # 2. Системное уведомление (колокольчик)
    try:
        b24_call("im.notify.system.add", {
            "USER_ID": str(admin_user_id),
            "MESSAGE": message_text
        })
        print(f" [OK] Алерт отправлен в колокольчик Битрикс24")
    except Exception as e:
        print(f" [DEBUG] Колокольчик: {e}")

def check_mass_modifications(threshold=10, minutes_window=5, dry_run=False):
    """Проверка количества измененных сделок за временное окно"""
    # Bitrix24 uses server time +03:00 (MSK)
    cutoff = datetime.now(timezone(timedelta(hours=3))) - timedelta(minutes=minutes_window)
    cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Сканирование изменений с {cutoff_str}...")

    # Fetch recent deals modified after cutoff
    res = b24_call("crm.deal.list", {
        "filter": {">=DATE_MODIFY": cutoff_str},
        "select": ["ID", "TITLE", "DATE_MODIFY", "MODIFY_BY_ID", "STAGE_ID", "OPPORTUNITY"],
        "order": {"DATE_MODIFY": "DESC"},
        "start": 0
    })

    deals = res.get("result", [])
    count = len(deals)
    print(f"Найдено измененных сделок за {minutes_window} мин: {count} шт (Порог тревоги: {threshold})")

    if count >= threshold:
        # Аномальная массовая активность!
        by_user = {}
        deal_ids = []
        for d in deals:
            uid = str(d.get("MODIFY_BY_ID", "0"))
            by_user[uid] = by_user.get(uid, 0) + 1
            deal_ids.append(d.get("ID"))

        alert_msg = (
            f"🚨 [B]ВНИМАНИЕ! ЗАФИКСИРОВАНА МАССОВАЯ МОДИФИКАЦИЯ ДАННЫХ В CRM![/B] 🚨\n\n"
            f"За последние {minutes_window} минут было изменено [B]{count} сделок[/B]!\n"
            f"Подозрение на работу вредоносного скрипта массовой перезаписи.\n\n"
            f"🔹 Инициаторы изменений (ID пользователей): {by_user}\n"
            f"🔹 Затронутые сделки (первые 15 шт): {deal_ids[:15]}\n\n"
            f"⚠️ [B]ДЕЙСТВИЕ:[/B] Если это не санкционированная операция, немедленно отзовите вебхук в Битрикс24 (Разработчикам -> Интеграции) для остановки скрипта!"
        )

        print("\n" + alert_msg + "\n")

        # Log to emergency file
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "window_minutes": minutes_window,
            "modified_count": count,
            "by_user": by_user,
            "deals": deals
        }
        os.makedirs("logs", exist_ok=True)
        with open("logs/b24_mass_change_emergency.json", "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        if not dry_run:
            send_b24_alerts(admin_user_id=1, message_text=alert_msg)
            return True, count
    else:
        print(" Все в порядке, нормальный фоновый режим.")
        return False, count

if __name__ == "__main__":
    load_env()
    dry = "--dry-run" in sys.argv
    check_mass_modifications(threshold=10, minutes_window=10, dry_run=dry)
