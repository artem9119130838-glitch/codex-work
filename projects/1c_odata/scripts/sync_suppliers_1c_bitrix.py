#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/sync_suppliers_1c_bitrix.py
=====================================================
Канонический боевой конвейер сквозной синхронизации поставщиков 1С:УНФ и Битрикс24 CRM.

Команда пользователя:
  «синхронизируй поставщиков 1С в битрикс»
  (алиасы: «перенос китайских поставщиков», «синхронизация фабрик КНР»)

Архитектурный устав:
  1. Синхронизирует активных поставщиков (Catalog_Контрагенты, Поставщик eq true) из 1С:УНФ в Битрикс24 CRM.
  2. Специализированный каскадный матчинг для китайских фабрик без ИНН:
     - 1С GUID (ORIGIN_ID);
     - ИНН (при наличии для РФ контрагентов);
     - Домен веб-сайта (из контактов или комментариев);
     - Международные телефоны (+86...) и Email (crm.duplicate.findbycomm);
     - Нормализованное ядро наименования (Brand Core, отсев суффиксов Co., Ltd., провинций).
  3. Safe Merge & Anti-Garbage Guard:
     - Никогда не создаются дубли уже заведенных менеджерами компаний.
     - Сохраняется текущий ответственный менеджер (ASSIGNED_BY_ID) в Б24.
     - Контакты (телефоны/email) дополняются без удаления существующих.
     - Банковские счета (SWIFT, CNY/USD) сохраняются в crm.requisite и crm.requisite.bankdetail.
  4. Структура папок 1С: транслируется в иерархические теги CRM (#Хэштеги) и фиксируется в карточке/таймлайне.
  5. Dry-Run First: по умолчанию скрипт работает в безопасном режиме отчета. Запись строго по флагу --execute.
"""

import os
import sys
import re
import time
import json
import argparse
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth

# Форсирование UTF-8 для вывода в консоль Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _load_env():
    """Загрузка конфигурации из projects/1c_odata/.env."""
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v


_load_env()

# Настройки OData 1С:УНФ
ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata").rstrip("/")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.writer")
ODATA_PWD = os.getenv("ONEC_ODATA_PASSWORD", "")
ONEC_AUTH = HTTPBasicAuth(ODATA_USER, ODATA_PWD)
ONEC_HEADERS = {"Accept": "application/json"}

# Настройки Битрикс24 REST API
B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
DEFAULT_ASSIGNED_ID = 20  # Азат (снабжение КНР)


# ----------------------------------------------------------------------
# Битрикс24 API Клиент с защитой от Rate Limit
# ----------------------------------------------------------------------
_LAST_B24_CALL_TS = 0.0


def call_b24(method: str, params: dict = None, retries: int = 3) -> dict:
    """Вызов метода REST API Битрикс24 с ограничением частоты запросов и retry."""
    global _LAST_B24_CALL_TS
    if not B24_WEBHOOK or B24_WEBHOOK == "/":
        raise ValueError("BITRIX24_WEBHOOK_URL не настроен в .env")

    # Rate limiting: не чаще 2-3 запросов в секунду
    elapsed = time.time() - _LAST_B24_CALL_TS
    if elapsed < 0.35:
        time.sleep(0.35 - elapsed)

    url = f"{B24_WEBHOOK}{method}"
    payload = params or {}

    for attempt in range(1, retries + 1):
        try:
            _LAST_B24_CALL_TS = time.time()
            resp = requests.post(url, json=payload, timeout=20)
            data = resp.json()
            if "error" in data:
                err_code = data.get("error")
                err_msg = data.get("error_description", "")
                if err_code in ["QUERY_LIMIT_EXCEEDED", "SLOW_DOWN"]:
                    time.sleep(1.5 * attempt)
                    continue
                raise RuntimeError(f"Ошибка Б24 [{err_code}]: {err_msg}")
            return data.get("result")
        except requests.RequestException as e:
            if attempt == retries:
                raise RuntimeError(f"Сетевая ошибка Б24 {method}: {e}")
            time.sleep(1.0 * attempt)

    return {}


# ----------------------------------------------------------------------
# Нормализация китайских наименований и извлечение данных
# ----------------------------------------------------------------------
STOP_CORP_SUFFIXES = [
    r'\bco\.,?\s*ltd\.?\b',
    r'\bco\.,?\s*limited\b',
    r'\blimited\b',
    r'\bltd\.?\b',
    r'\binc\.?\b',
    r'\bcorp\.?\b',
    r'\bcorporation\b',
    r'\bgroup\b',
    r'\bllc\b',
    r'\btrading\b',
    r'\bholding\b',
    r'\bindustry\b',
    r'\bindustrial\b',
    r'\bmanufacturing\b',
    r'\bmachinery\b',
    r'\bequipment\b',
    r'\btechnology\b',
    r'\btech\b',
]

STOP_PROVINCES_CITIES = [
    r'\bshanghai\b', r'\bbeijing\b', r'\bshenzhen\b', r'\bguangzhou\b',
    r'\bsuzhou\b', r'\bhangzhou\b', r'\bdezhou\b', r'\bjinan\b',
    r'\bningbo\b', r'\bwuxi\b', r'\bdongguan\b', r'\bfoshan\b',
    r'\bshandong\b', r'\bjiangsu\b', r'\bzhejiang\b', r'\bguangdong\b',
    r'\bhebei\b', r'\bhenan\b', r'\banhui\b', r'\byiwu\b',
    r'\bchina\b', r'\bp\.?r\.?c\.?\b'
]


def normalize_brand_core(title: str) -> str:
    """Извлекает нормализованное ядро бренда/наименования фабрики."""
    if not title:
        return ""
    t = title.lower()
    # Убираем кавычки, скобки и спецсимволы
    t = re.sub(r'[«»"“”\'`\(\)\[\]（）]', ' ', t)
    # Убираем юридические суффиксы
    for pat in STOP_CORP_SUFFIXES:
        t = re.sub(pat, ' ', t, flags=re.IGNORECASE)
    # Убираем названия городов и провинций КНР для выделения чистого бренда
    for pat in STOP_PROVINCES_CITIES:
        t = re.sub(pat, ' ', t, flags=re.IGNORECASE)
    # Очистка от лишних знаков препинания и пробелов
    t = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5а-яА-ЯёЁ\s]', ' ', t)
    tokens = [w for w in t.split() if len(w) > 1]
    return " ".join(tokens).strip()


def extract_domain(url_or_email: str) -> str:
    """Извлекает чистый домен из URL или Email."""
    if not url_or_email:
        return ""
    s = url_or_email.strip().lower()
    if "@" in s:
        s = s.split("@")[-1]
    else:
        if not s.startswith("http://") and not s.startswith("https://"):
            s = "http://" + s
        parsed = urlparse(s)
        s = parsed.netloc or parsed.path
    s = re.sub(r'^www\.', '', s)
    s = s.split(":")[0].strip()
    # Исключаем общие почтовые сервисы
    if any(s.endswith(comm) for comm in ["qq.com", "163.com", "126.com", "gmail.com", "yandex.ru", "mail.ru", "sina.com"]):
        return ""
    return s


def parse_supplier_contacts(s_data: dict) -> dict:
    """Извлекает телефоны, email, адреса, сайты и WeChat из данных 1С."""
    phones = set()
    emails = set()
    websites = set()
    addresses = []

    # 1. Из табличной части КонтактнаяИнформация
    ci_list = s_data.get("КонтактнаяИнформация", []) or []
    for ci in ci_list:
        ci_type = ci.get("Тип", "")
        ci_val = (ci.get("Представление") or "").strip()
        if not ci_val:
            continue
        if ci_type == "Телефон":
            clean_p = re.sub(r'[^\d+]', '', ci_val)
            if len(clean_p) >= 6:
                phones.add(ci_val)
        elif ci_type == "АдресЭлектроннойПочты":
            if "@" in ci_val:
                emails.add(ci_val.lower())
                dm = extract_domain(ci_val)
                if dm:
                    websites.add(dm)
        elif ci_type == "Адрес":
            if ci_val not in addresses:
                addresses.append(ci_val)
        elif ci_type == "ВебСтраница":
            dm = extract_domain(ci_val)
            if dm:
                websites.add(dm)

    # 2. Из полей для быстрого поиска 1С
    if s_data.get("АдресЭПДляПоиска"):
        em = s_data["АдресЭПДляПоиска"].strip().lower()
        if "@" in em:
            emails.add(em)
            dm = extract_domain(em)
            if dm:
                websites.add(dm)

    if s_data.get("НомерТелефонаДляПоиска"):
        ph = s_data["НомерТелефонаДляПоиска"].strip()
        if ph:
            phones.add(ph)

    # 3. Из текстового комментария / Заметки (в 1С там детальная карточка фабрики)
    comment = (s_data.get("Комментарий") or s_data.get("ОсновныеСведения") or "").strip()
    messengers = set()

    if comment:
        # Поиск email в комментарии
        found_emails = re.findall(r'[a-zA-Z0-9_\.\+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9\.-]+', comment)
        for em in found_emails:
            emails.add(em.lower())
            dm = extract_domain(em)
            if dm:
                websites.add(dm)

        # Поиск сайтов
        found_urls = re.findall(r'(?:https?:\/\/|www\.)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:\/[^\s]*)?', comment)
        for u in found_urls:
            dm = extract_domain(u)
            if dm:
                websites.add(dm)

        # Поиск WeChat / Whatsapp
        found_im = re.findall(r'(?:whatsapp|wechat)[\s/:]*([0-9\s\+-]+)', comment, flags=re.IGNORECASE)
        for im in found_im:
            im_clean = im.strip()
            if len(re.sub(r'\D', '', im_clean)) >= 8:
                messengers.add(im_clean)

        # Поиск телефонов (с учетом 0086 и +86)
        c_norm = re.sub(r'\b0086\b', '+86', comment)
        found_phones = re.findall(r'(?:mob|tel|phone|факс|fax)?[\s/:]*(\+?86[\s\-]?(?:1[3-9]\d[\s\-]?\d{4}[\s\-]?\d{4}|(?:0\d{2,3}[\s\-]?)?\d{7,8}))', c_norm, flags=re.IGNORECASE)
        for ph in found_phones:
            if len(re.sub(r'\D', '', ph)) >= 8:
                phones.add(ph.strip())

        # Поиск адресов (строки с Add: или Address:)
        for line in comment.splitlines():
            line_str = line.strip()
            if line_str.lower().startswith("add:") or line_str.lower().startswith("address:"):
                a_clean = re.sub(r'^(?:add|address)\s*:\s*', '', line_str, flags=re.IGNORECASE).strip()
                if a_clean and a_clean not in addresses:
                    addresses.append(a_clean)

    return {
        "phones": list(phones),
        "emails": list(emails),
        "websites": list(websites),
        "messengers": list(messengers),
        "address": " | ".join(addresses) if addresses else "",
        "raw_note": comment
    }


# ----------------------------------------------------------------------
# Кэширование существующих поставщиков Битрикс24
# ----------------------------------------------------------------------
class B24SupplierRegistry:
    """Кэшированный реестр существующих компаний-поставщиков в Битрикс24 для быстрого матчинга."""

    def __init__(self):
        self.companies = {}  # {id: company_dict}
        self.origin_map = {}  # {origin_id: id}
        self.inn_map = {}  # {inn: id}
        self.domain_map = {}  # {domain: id}
        self.email_map = {}  # {email: id}
        self.phone_map = {}  # {clean_phone: id}
        self.brand_core_map = {}  # {core_brand: id}

    def load(self):
        """Пакетная выгрузка всех компаний с типом SUPPLIER из Битрикс24."""
        print("  [B24] Загрузка реестра существующих компаний-поставщиков из Битрикс24...")
        start = 0
        batch_size = 50
        loaded_count = 0

        while True:
            res = call_b24("crm.company.list", {
                "filter": {"COMPANY_TYPE": "SUPPLIER"},
                "select": ["ID", "TITLE", "COMPANY_TYPE", "ORIGIN_ID", "ORIGINATOR_ID", "ASSIGNED_BY_ID",
                           "UF_CRM_699421CD2A684", "WEB", "EMAIL", "PHONE", "COMMENTS"],
                "start": start
            })
            if not res:
                break

            for comp in res:
                cid = int(comp["ID"])
                self.companies[cid] = comp
                loaded_count += 1

                # 1. Индекс ORIGIN_ID
                orig_id = (comp.get("ORIGIN_ID") or "").strip()
                if orig_id:
                    self.origin_map[orig_id.lower()] = cid

                # 2. Индекс ИНН
                inn = str(comp.get("UF_CRM_699421CD2A684") or "").strip()
                if inn:
                    self.inn_map[inn] = cid

                # 3. Индекс сайтов / доменов
                for w_item in comp.get("WEB") or []:
                    dm = extract_domain(w_item.get("VALUE", ""))
                    if dm:
                        self.domain_map[dm] = cid

                # 4. Индекс Email
                for e_item in comp.get("EMAIL") or []:
                    em = (e_item.get("VALUE") or "").strip().lower()
                    if em:
                        self.email_map[em] = cid
                        dm = extract_domain(em)
                        if dm:
                            self.domain_map[dm] = cid

                # 5. Индекс Телефонов
                for p_item in comp.get("PHONE") or []:
                    raw_ph = p_item.get("VALUE") or ""
                    clean_ph = re.sub(r'\D', '', raw_ph)
                    if len(clean_ph) >= 7:
                        self.phone_map[clean_ph] = cid

                # 6. Индекс ядра названия
                title = comp.get("TITLE") or ""
                core = normalize_brand_core(title)
                if len(core) >= 4:
                    self.brand_core_map[core] = cid

            if len(res) < batch_size:
                break
            start += batch_size

        print(f"  [B24] Успешно загружено и проиндексировано {loaded_count} поставщиков из CRM.")

    def match(self, s_data: dict, contacts: dict) -> tuple:
        """
        Каскадный поиск поставщика в Битрикс24.
        Возвращает: (matched_company_dict or None, match_reason_str)
        """
        ref_key = (s_data.get("Ref_Key") or "").strip().lower()
        inn = str(s_data.get("ИНН") or "").strip()
        title = s_data.get("Description") or s_data.get("НаименованиеПолное") or ""

        # Уровень 1: По 1С GUID (ORIGIN_ID)
        if ref_key and ref_key in self.origin_map:
            cid = self.origin_map[ref_key]
            return self.companies[cid], f"ORIGIN_ID ({ref_key})"

        # Уровень 2: По ИНН (если заполнен для РФ поставщиков)
        if inn and inn in self.inn_map:
            cid = self.inn_map[inn]
            return self.companies[cid], f"ИНН ({inn})"

        # Уровень 3: По домену веб-сайта
        for dm in contacts.get("websites", []):
            if dm in self.domain_map:
                cid = self.domain_map[dm]
                return self.companies[cid], f"Домен сайта ({dm})"

        # Уровень 4: По Email
        for em in contacts.get("emails", []):
            if em in self.email_map:
                cid = self.email_map[em]
                return self.companies[cid], f"Email ({em})"

        # Уровень 5: По номерам телефонов
        for ph in contacts.get("phones", []):
            clean_ph = re.sub(r'\D', '', ph)
            if len(clean_ph) >= 7 and clean_ph in self.phone_map:
                cid = self.phone_map[clean_ph]
                return self.companies[cid], f"Телефон ({ph})"

        # Уровень 6: По нормализованному ядру бренда
        core = normalize_brand_core(title)
        if len(core) >= 5 and core in self.brand_core_map:
            cid = self.brand_core_map[core]
            return self.companies[cid], f"Ядро бренда ('{core}')"

        return None, "НОВАЯ КОМПАНИЯ"


# ----------------------------------------------------------------------
# Клиент 1С:УНФ (OData)
# ----------------------------------------------------------------------
class OneCClient:
    """Клиент выгрузки данных контрагентов и папок из 1С:УНФ по OData."""

    def __init__(self):
        self.folder_map = {}  # {guid: {"name": str, "parent": guid}}
        self.bank_accounts = {}  # {owner_guid: [acc_dict]}

    def load_folders(self):
        """Загрузка полного дерева групп/папок справочника Контрагенты."""
        print("  [1C] Загрузка дерева папок контрагентов...")
        url = f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$filter=IsFolder eq true and DeletionMark eq false&$select=Ref_Key,Description,Parent_Key"
        try:
            resp = requests.get(url, auth=ONEC_AUTH, headers=ONEC_HEADERS, timeout=20)
            items = resp.json().get("value", [])
            for item in items:
                self.folder_map[item["Ref_Key"]] = {
                    "name": (item.get("Description") or "").strip(),
                    "parent": item.get("Parent_Key")
                }
            print(f"  [1C] Загружено {len(self.folder_map)} папок/групп.")
        except Exception as e:
            print(f"  [WARN] Ошибка загрузки папок 1С: {e}")

    def get_folder_path(self, parent_key: str) -> list:
        """Построение цепочки имен папок от корня до текущей."""
        path = []
        cur = parent_key
        visited = set()
        while cur and cur in self.folder_map and cur not in visited:
            visited.add(cur)
            f_data = self.folder_map[cur]
            name = f_data["name"]
            if name:
                path.insert(0, name)
            cur = f_data["parent"]
        return path

    def load_bank_accounts(self):
        """Загрузка банковских счетов контрагентов."""
        print("  [1C] Загрузка банковских счетов...")
        url = f"{ODATA_BASE}/Catalog_БанковскиеСчета?$format=json&$select=Ref_Key,Owner,НомерСчета,Банк_Key,Description"
        try:
            resp = requests.get(url, auth=ONEC_AUTH, headers=ONEC_HEADERS, timeout=25)
            items = resp.json().get("value", [])
            for item in items:
                owner = item.get("Owner")
                if owner:
                    if owner not in self.bank_accounts:
                        self.bank_accounts[owner] = []
                    self.bank_accounts[owner].append(item)
            print(f"  [1C] Загружено {len(items)} банковских счетов.")
        except Exception as e:
            print(f"  [WARN] Ошибка загрузки счетов 1С: {e}")

    def fetch_suppliers(self, limit: int = None, folder_name: str = None, code: str = None, codes: list = None, inn: str = None, since: str = None) -> list:
        """Выборка активных поставщиков с фильтрацией и пагинацией."""
        print("  [1C] Выборка поставщиков из 1С:УНФ...")
        filter_parts = ["Поставщик eq true", "IsFolder eq false", "DeletionMark eq false"]

        target_codes = []
        if codes:
            target_codes.extend([c.strip() for c in codes if c.strip()])
        if code and code.strip() not in target_codes:
            target_codes.append(code.strip())

        if target_codes:
            if len(target_codes) == 1:
                filter_parts.append(f"Code eq '{target_codes[0]}'")
            else:
                c_sub = " or ".join([f"Code eq '{c}'" for c in target_codes])
                filter_parts.append(f"({c_sub})")

        if inn:
            filter_parts.append(f"ИНН eq '{inn}'")

        # Предварительный поиск целевых папок (по подстроке или GUID)
        target_folder_guids = set()
        if folder_name:
            fn_clean = folder_name.strip().lower()
            for f_guid, f_info in self.folder_map.items():
                if fn_clean in f_guid.lower() or fn_clean in f_info["name"].lower():
                    target_folder_guids.add(f_guid)

        odata_filter = " and ".join(filter_parts)
        top = 100
        skip = 0
        all_suppliers = []

        while True:
            url = f"{ODATA_BASE}/Catalog_Контрагенты?$format=json&$filter={odata_filter}&$top={top}&$skip={skip}&$orderby=Ref_Key"
            try:
                resp = requests.get(url, auth=ONEC_AUTH, headers=ONEC_HEADERS, timeout=30)
                items = resp.json().get("value", [])
                if not items:
                    break

                for item in items:
                    # Фильтр по названию папки (если задан)
                    if folder_name:
                        p_key = item.get("Parent_Key")
                        # Проверяем прямое совпадение с целевой папкой или ее предками
                        p_path = self.get_folder_path(p_key)
                        matches_folder = (p_key in target_folder_guids) or any(folder_name.lower() in p.lower() for p in p_path)
                        if not matches_folder:
                            continue

                    all_suppliers.append(item)
                    if limit and len(all_suppliers) >= limit:
                        print(f"  [1C] Достигнут лимит выборки ({limit} записей).")
                        return all_suppliers

                if len(items) < top:
                    break
                skip += top
            except Exception as e:
                print(f"  [ERROR] Сбой выборки поставщиков 1С: {e}")
                break

        print(f"  [1C] Отобрано {len(all_suppliers)} поставщиков для синхронизации.")
        return all_suppliers


# ----------------------------------------------------------------------
# Safe Merge & Синхронизация сущностей Битрикс24
# ----------------------------------------------------------------------
def sync_supplier_to_b24(s_data: dict, onec: OneCClient, registry: B24SupplierRegistry, execute: bool = False, verbose: bool = False) -> dict:
    """Синхронизирует одну запись поставщика в Битрикс24 с защитой данных."""
    ref_key = s_data.get("Ref_Key")
    code_1c = s_data.get("Code", "")
    title = (s_data.get("Description") or s_data.get("НаименованиеПолное") or "").strip()
    full_name = (s_data.get("НаименованиеПолное") or title).strip()
    inn = str(s_data.get("ИНН") or "").strip()
    kpp = str(s_data.get("КПП") or "").strip()
    parent_key = s_data.get("Parent_Key")
    comment_1c = (s_data.get("Комментарий") or "").strip()

    # 1. Извлечение контактов
    contacts = parse_supplier_contacts(s_data)

    # 2. Определение структуры папок и формирование тегов CRM
    folder_path = onec.get_folder_path(parent_key)
    tags = ["1С", "Поставщик"]
    for f in folder_path:
        clean_tag = re.sub(r'[^a-zA-Zа-яА-ЯёЁ0-9\s_-]', '', f).strip()
        if clean_tag and clean_tag not in tags:
            tags.append(clean_tag)

    # 3. Матчинг в Битрикс24
    matched_company, match_reason = registry.match(s_data, contacts)

    action = "UPDATE" if matched_company else "CREATE"
    b24_id = matched_company["ID"] if matched_company else None

    # Формирование комментария для таймлайна
    folder_display = " -> ".join(folder_path) if folder_path else "Без группы"
    tags_hashtags = " ".join([f"#{t.replace(' ', '_')}" for t in tags])

    timeline_comment = (
        f"🏭 [b]Синхронизация из 1С:УНФ (Поставщик)[/b]\n"
        f"Код 1С: [b]{code_1c}[/b] | GUID: {ref_key}\n"
        f"📁 Папка 1С: [b]{folder_display}[/b]\n"
        f"🏷 Теги: {tags_hashtags}\n"
    )
    if comment_1c:
        timeline_comment += f"\n📝 [b]Комментарий / Карточка из 1С:[/b]\n{comment_1c}\n"
    if contacts["websites"]:
        timeline_comment += f"\n🌐 Сайты: {', '.join(contacts['websites'])}\n"

    # DRY-RUN режим (без записи)
    if not execute:
        return {
            "action": action,
            "code_1c": code_1c,
            "title": title,
            "inn": inn,
            "folder": folder_display,
            "b24_id": b24_id,
            "match_reason": match_reason,
            "phones": len(contacts["phones"]),
            "emails": len(contacts["emails"]),
            "tags": tags
        }

    # БОЕВОЙ РЕЖИМ (--execute)
    try:
        # Подготовка полей телефонов, email, web, мессенджеров для Битрикс24
        phone_fields = [{"VALUE_TYPE": "WORK", "VALUE": p} for p in contacts["phones"]]
        email_fields = [{"VALUE_TYPE": "WORK", "VALUE": e} for e in contacts["emails"]]
        web_fields = [{"VALUE_TYPE": "WORK", "VALUE": w} for w in contacts["websites"]]
        im_fields = [{"VALUE_TYPE": "OTHER", "VALUE": m} for m in contacts.get("messengers", [])]

        raw_note = contacts.get("raw_note") or ""
        formatted_comment = (
            f"📁 Папка 1С: {folder_display}\n"
            f"🏷 Категория: {tags_hashtags}\n"
            f"🔢 Код 1С: {code_1c}\n"
        )
        if raw_note:
            formatted_comment += f"\n📝 Заметки из 1С:\n{raw_note}\n"

        if action == "CREATE":
            create_payload = {
                "TITLE": title,
                "COMPANY_TYPE": "SUPPLIER",
                "INDUSTRY": "OTHER",
                "ORIGIN_ID": ref_key,
                "ORIGINATOR_ID": "1C_UNF",
                "ASSIGNED_BY_ID": DEFAULT_ASSIGNED_ID,
                "OPENED": "Y",
                "UF_CRM_1C_FOLDER": folder_display,
                "COMMENTS": formatted_comment
            }
            if inn:
                create_payload["UF_CRM_699421CD2A684"] = inn
            if contacts["address"]:
                create_payload["ADDRESS"] = contacts["address"]
            if phone_fields:
                create_payload["PHONE"] = phone_fields
            if email_fields:
                create_payload["EMAIL"] = email_fields
            if web_fields:
                create_payload["WEB"] = web_fields
            if im_fields:
                create_payload["IM"] = im_fields

            b24_id = call_b24("crm.company.add", {"fields": create_payload})
            b24_id = int(b24_id)

        else:  # UPDATE (Safe Merge)
            update_payload = {
                "COMPANY_TYPE": "SUPPLIER",
                "UF_CRM_1C_FOLDER": folder_display,
                "COMMENTS": formatted_comment
            }
            if not matched_company.get("ORIGIN_ID"):
                update_payload["ORIGIN_ID"] = ref_key
                update_payload["ORIGINATOR_ID"] = "1C_UNF"
            if inn and not matched_company.get("UF_CRM_699421CD2A684"):
                update_payload["UF_CRM_699421CD2A684"] = inn
            if contacts["address"] and not matched_company.get("ADDRESS"):
                update_payload["ADDRESS"] = contacts["address"]

            # Безопасное дополнение контактов без затирания имеющихся
            if phone_fields and not matched_company.get("PHONE"):
                update_payload["PHONE"] = phone_fields
            if email_fields and not matched_company.get("EMAIL"):
                update_payload["EMAIL"] = email_fields
            if web_fields and not matched_company.get("WEB"):
                update_payload["WEB"] = web_fields
            if im_fields and not matched_company.get("IM"):
                update_payload["IM"] = im_fields

            call_b24("crm.company.update", {"id": b24_id, "fields": update_payload})

        # Синхронизация реквизитов crm.requisite
        try:
            req_list = call_b24("crm.requisite.list", {"filter": {"ENTITY_TYPE_ID": 4, "ENTITY_ID": b24_id}}) or []
            req_fields = {
                "ENTITY_TYPE_ID": 4,
                "ENTITY_ID": b24_id,
                "PRESET_ID": 1,
                "NAME": title,
                "RQ_COMPANY_NAME": title,
                "RQ_COMPANY_FULL_NAME": full_name,
                "RQ_INN": inn,
                "RQ_KPP": kpp,
                "ADDRESS_ONLY": "N"
            }
            if contacts["address"]:
                req_fields["RQ_ADDR"] = {"1": {"ADDRESS_1": contacts["address"]}}

            if not req_list:
                req_id = call_b24("crm.requisite.add", {"fields": req_fields})
            else:
                req_id = req_list[0]["ID"]
                call_b24("crm.requisite.update", {"id": req_id, "fields": req_fields})

            # Синхронизация банковских счетов
            accounts_1c = onec.bank_accounts.get(ref_key, [])
            for acc in accounts_1c:
                acc_num = acc.get("НомерСчета")
                if acc_num:
                    bdetails = call_b24("crm.requisite.bankdetail.list", {"filter": {"ENTITY_ID": req_id}}) or []
                    exists_acc = any(b.get("RQ_ACC_NUM") == acc_num for b in bdetails)
                    if not exists_acc:
                        call_b24("crm.requisite.bankdetail.add", {
                            "fields": {
                                "ENTITY_ID": req_id,
                                "NAME": acc.get("ТекстКорреспондента") or "Основной счет",
                                "RQ_ACC_NUM": acc_num,
                                "RQ_SWIFT": acc.get("SWIFT_Key") or ""
                            }
                        })
        except Exception as e:
            if verbose:
                print(f"    [WARN] Ошибка синхронизации реквизитов для компании {b24_id}: {e}")

        # Добавление и закрепление комментария в таймлайне
        try:
            comm_res = call_b24("crm.timeline.comment.add", {
                "fields": {
                    "ENTITY_ID": b24_id,
                    "ENTITY_TYPE": "company",
                    "COMMENT": timeline_comment
                }
            })
            if comm_res:
                call_b24("crm.timeline.item.pin", {
                    "ownerTypeId": 4,
                    "ownerId": b24_id,
                    "id": comm_res
                })
        except Exception as e:
            if verbose:
                print(f"    [WARN] Ошибка добавления таймлайна для компании {b24_id}: {e}")

        return {
            "action": action,
            "code_1c": code_1c,
            "title": title,
            "inn": inn,
            "folder": folder_display,
            "b24_id": b24_id,
            "match_reason": match_reason,
            "status": "SUCCESS"
        }

    except Exception as e:
        return {
            "action": action,
            "code_1c": code_1c,
            "title": title,
            "inn": inn,
            "folder": folder_display,
            "b24_id": b24_id,
            "match_reason": match_reason,
            "status": f"ERROR: {e}"
        }


# ----------------------------------------------------------------------
# CLI Runner и Итоговый Отчет
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Канонический конвейер синхронизации поставщиков 1С:УНФ и Битрикс24 CRM."
    )
    parser.add_argument("--execute", action="store_true", help="Боевой запуск с записью в Битрикс24 (по умолчанию включен --dry-run)")
    parser.add_argument("--dry-run", action="store_true", help="Принудительный безопасный запуск без записи")
    parser.add_argument("--limit", type=int, default=None, help="Ограничение количества поставщиков (например --limit 10)")
    parser.add_argument("--folder", type=str, default=None, help="Фильтр по имени папки в 1С (например --folder 'Гидравлика')")
    parser.add_argument("--code", type=str, default=None, help="Синхронизация конкретного контрагента по коду 1С (например --code НФ-001148)")
    parser.add_argument("--codes", nargs="+", default=None, help="Синхронизация списка контрагентов по кодам 1С (например --codes НФ-000853 НФ-001208 НФ-000554)")
    parser.add_argument("--inn", type=str, default=None, help="Синхронизация по конкретному ИНН")
    parser.add_argument("--verbose", action="store_true", help="Подробный вывод технической информации")

    args = parser.parse_args()

    is_execute = args.execute and not args.dry_run

    print("\n" + "=" * 80)
    print("🚀 КОНВЕЙЕР СИНХРОНИЗАЦИИ ПОСТАВЩИКОВ 1С:УНФ <-> БИТРИКС24 CRM")
    print(f"   Режим работы: {'🔴 БОЕВАЯ ЗАПИСЬ (--execute)' if is_execute else '🟢 БЕЗОПАСНЫЙ АУДИТ (--dry-run)'}")
    if args.limit:
        print(f"   Ограничение выборки: {args.limit} записей")
    if args.folder:
        print(f"   Фильтр по папке 1С: '{args.folder}'")
    if args.code:
        print(f"   Фильтр по коду 1С: '{args.code}'")
    if args.codes:
        print(f"   Фильтр по списку кодов 1С: {', '.join(args.codes)}")
    print("=" * 80 + "\n")

    # 1. Инициализация клиентов
    onec = OneCClient()
    onec.load_folders()
    onec.load_bank_accounts()

    registry = B24SupplierRegistry()
    registry.load()

    # 2. Выборка поставщиков из 1С
    suppliers = onec.fetch_suppliers(
        limit=args.limit,
        folder_name=args.folder,
        code=args.code,
        codes=args.codes,
        inn=args.inn
    )

    if not suppliers:
        print("\nПоставщики по заданным критериям не найдены.")
        return

    # 3. Итерация и обработка
    print(f"\nОбработка выборки ({len(suppliers)} поставщиков)...")
    print("-" * 80)
    print(f"{'1С Код':<10} | {'Наименование 1С':<32} | {'Папка 1С':<18} | {'Действие':<8} | {'Б24 ID':<8} | {'Причина матчинга'}")
    print("-" * 80)

    stats = {
        "total": len(suppliers),
        "created": 0,
        "updated": 0,
        "errors": 0
    }

    results = []

    for s in suppliers:
        res = sync_supplier_to_b24(s, onec, registry, execute=is_execute, verbose=args.verbose)
        results.append(res)

        act = res["action"]
        if act == "CREATE":
            stats["created"] += 1
        else:
            stats["updated"] += 1

        b_id = str(res.get("b24_id") or "НОВЫЙ")
        s_title = (res.get("title") or "")[:30]
        s_folder = (res.get("folder") or "")[:16]
        reason = res.get("match_reason") or ""

        print(f"{res.get('code_1c', ''):<10} | {s_title:<32} | {s_folder:<18} | {act:<8} | {b_id:<8} | {reason}")

    # 4. Итоговая сводка
    print("\n" + "=" * 80)
    print("📊 ИТОГОВАЯ СВОДКА СИНХРОНИЗАЦИИ")
    print("=" * 80)
    print(f"Всего поставщиков в выборке 1С:     {stats['total']}")
    print(f"Существующие в CRM (Safe Merge):    {stats['updated']} (без создания дублей!)")
    print(f"Будет создано новых компаний в CRM: {stats['created']}")
    print(f"Ошибок:                             {stats['errors']}")
    print("=" * 80)

    if not is_execute:
        print("\n💡 Для применения изменений и боевой записи в Битрикс24 запустите команду с флагом --execute:")
        cmd_args = []
        if args.limit:
            cmd_args.append(f"--limit {args.limit}")
        if args.folder:
            cmd_args.append(f"--folder \"{args.folder}\"")
        if args.code:
            cmd_args.append(f"--code \"{args.code}\"")
        cmd_str = " ".join(cmd_args)
        print(f"   py projects/1c_odata/scripts/sync_suppliers_1c_bitrix.py --execute {cmd_str}\n")


if __name__ == "__main__":
    main()
