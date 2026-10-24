# -*- coding: utf-8 -*-
import os
import sys
import json
import base64
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def load_env():
    p = os.path.join(os.getcwd(), "projects", "1c_odata", ".env")
    if os.path.exists(p):
        for line in open(p, "r", encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

load_env()
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"

def b24(method, payload=None):
    r = requests.post(webhook + method, json=payload or {}, timeout=30)
    r.raise_for_status()
    return r.json()

# 1. Verify file on disk
docx_path = os.path.join(os.getcwd(), "projects", "HR", "azat_supply_and_erp_faq.docx")
fname = os.path.basename(docx_path)
with open(docx_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

print(f"Uploading {fname} to Common Storage (#3)...")
r_up = b24("disk.storage.uploadfile", {
    "id": 3,
    "data": {"NAME": fname},
    "fileContent": [fname, b64],
    "generateUniqueName": True
})
file_id = r_up.get("result", {}).get("ID")
print(f"File uploaded, ID: {file_id}")

# 2. Task Description
task_desc = """Азат, добрый день.

Прошу Вас ознакомиться с подготовленным стартовым файлом базы знаний отдела снабжения и ВЭД (файл azat_supply_and_erp_faq.docx прикреплен к задаче).

Мы провели аудит истории переписок и собрали пул реальных вопросов и решений, возникавших в работе:
1. Расположение ключевых ресурсов: папка ВЭД на Диске, файл Дэвида Ideal Basic (инвойсы и упаковочные), шаблоны КП и запросов карго.
2. Регламент 1С:УНФ: сроки начисления зарплаты (10-го числа), проверка оплат покупателей, момент заведения «Заказа поставщику», ведение папки контрагентов «Китай» без дублей.
3. Взаимодействие с китайскими фабриками: чеклист параметров (габариты, вес брутто/нетто), запрет закрытия сделок без габаритов (поиск ориентировочных данных в каталогах), обязательное сохранение российских артикулов и ГОСТов в спецификациях.
4. Доступы и пароли: единый доступ к аналитической системе Tender-RAG (manager@tender-rag.local / manager12345), регламенты VPN и менеджеров паролей.

Что необходимо сделать со сроком исполнения до 31 октября 2026 г.:
1. Посмотреть сырой батч вопросов и решений в прикрепленном файле.
2. Вспомнить и выписать, что Вы и Ваши сотрудники еще спрашивали в ходе работы и с какими трудностями сталкивались.
3. По аналогии с вопросником Александры оформить рабочий двуязычный (русско-китайский) вопросник для своего отдела (в виде Google Документа или структурированного файла на Диске), чтобы новые сотрудники могли сразу находить готовые ответы.
4. Ссылку на созданный вопросник прикрепить в комментариях к этой задаче.
"""

task_fields = {
    "TITLE": "Создать двуязычный (RU/CN) вопросник-FAQ отдела снабжения и ВЭД",
    "DESCRIPTION": task_desc,
    "RESPONSIBLE_ID": 20,
    "CREATED_BY": 1,
    "DEADLINE": "2026-10-31T18:00:00+03:00",
    "UF_TASK_WEBDAV_FILES": [f"n{file_id}"]
}

print("Creating Bitrix24 task for Azat (ID: 20)...")
r_task = b24("tasks.task.add", {"fields": task_fields})
new_task_id = r_task.get("result", {}).get("task", {}).get("id")
print(f"Task successfully created! Task ID: #{new_task_id}")
task_url = f"https://b24-g4wfjq.bitrix24.ru/company/personal/user/1/tasks/task/view/{new_task_id}/"
print(f"Task URL: {task_url}")

# 3. Send message to Azat in direct chat
chat_msg = f"""Азат, добрый день. 
Поставил Вам задачу по созданию базы знаний отдела: {task_url}
К задаче прикрепил файл в формате Word (azat_supply_and_erp_faq.docx). Прошу Вас посмотреть этот сырой батч вопросов, вспомнить, что Вы еще сами спрашивали в процессе работы, и по аналогии с Александрой сделать двуязычный (русско-китайский) опросник для своего отдела со сроком до конца октября."""

print("Sending message to Azat in direct chat...")
r_msg = b24("im.message.add", {
    "DIALOG_ID": "20",
    "MESSAGE": chat_msg
})
msg_id = r_msg.get("result")
print(f"Direct message sent, ID: {msg_id}")
