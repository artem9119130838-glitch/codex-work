"""
Скрипт автономной двухсторонней синхронизации контактов между Битрикс24 и телефонией Новофон.

Правила маппинга полей в Новофон:
- Фамилия (last_name)    -> Название компании (если компании нет -> Фамилия контакта)
- Имя (first_name)        -> Имя Фамилия контактного лица (для общих номеров компании -> 'Общий номер')
- Отчество (patronymic)   -> Добавочный номер в формате 'доб. XXX' (если есть)
- Телефоны (phone_numbers)-> Список номеров в формате E.164 (+7XXXXXXXXXX)

Правила обогащения и дедупликации:
1. Добавочный ищется:
   а) В карточке контакта (SECOND_NAME / Отчество);
   б) В строке номера телефона (напр. '+78772578135 доб. 040');
   в) В подписи писем CRM (сделки и контакт в crm.activity.list, TYPE_ID: 4), исключая служебные подписи LongWang.
2. Если добавочный найден в переписке или телефоне, но в Битрикс24 отсутствует:
   - Обновляется SECOND_NAME контакта в Битрикс24 значением 'доб. XXX'.
3. Перезапись в Новофон:
   - Если контакт с таким номером уже есть в Новофон -> вызывается update.contacts (перезапись актуальными данными).
   - Если нет -> create.contacts.
4. Обратное обогащение (Двухсторонняя синхронизация):
   - Если в Новофон есть контакт, чье название компании/фамилия точно совпадает с Битрикс,
     но в Битрикс нет телефона или добавочного -> обновляется Битрикс24.

Использование:
    py scripts/sync_b24_to_novofon.py --dry-run
    py scripts/sync_b24_to_novofon.py --test-batch --dry-run
    py scripts/sync_b24_to_novofon.py --test-batch
    py scripts/sync_b24_to_novofon.py
"""

import sys
import os
import re
import json
import argparse
import requests
from typing import Dict, List, Any, Optional, Tuple, Set

sys.stdout.reconfigure(encoding='utf-8')

def load_dotenv():
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in search_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass

load_dotenv()

B24_WEBHOOK = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"
NOVOFON_URL = os.getenv("NOVOFON_API_URL", "https://dataapi-jsonrpc.novofon.ru/v2.0")
DEFAULT_NOVOFON_TOKEN = os.getenv("NOVOFON_API_TOKEN", "")

# Регулярное выражение для поиска добавочных номеров (исключает "добрый день" и служебные фразы)
EXT_REGEX = re.compile(
    r'(?<![а-яА-ЯёЁ])(?:доб(?![а-яА-ЯёЁ])\.?|вн(?![а-яА-ЯёЁ])\.?|ext\.?|добавочн(?:ый|ого)?\.?)\s*[:#№]?\s*(\d{2,6}(?:-\d{2,6})?)\b',
    re.IGNORECASE
)

# Служебные добавочные LongWang, которые нельзя присваивать клиентам
INTERNAL_EXTENSIONS = {'100', '101', '102', '103'}

def normalize_phone(raw: str) -> Optional[str]:
    """Приводит номер телефона к формату 7XXXXXXXXXX (стандарт Новофон для РФ)."""
    if not raw:
        return None
    cleaned = re.sub(r'[^\d+]', '', raw.split('доб')[0].split('ext')[0].split('вн')[0])
    digits = re.sub(r'\D', '', cleaned)
    if len(digits) == 11 and digits.startswith('8'):
        return f"7{digits[1:]}"
    elif len(digits) == 11 and digits.startswith('7'):
        return digits
    elif len(digits) == 10:
        return f"7{digits}"
    elif len(digits) >= 11:
        return digits
    return None

def extract_extension(raw_text: str) -> Optional[str]:
    """Извлекает добавочный номер из произвольной строки, исключая служебные номера."""
    if not raw_text:
        return None
    matches = EXT_REGEX.findall(raw_text)
    for m in matches:
        clean_ext = m.strip()
        if clean_ext not in INTERNAL_EXTENSIONS:
            return f"доб. {clean_ext}"
    return None

class NovofonClient:
    def __init__(self, token: str, dry_run: bool = False):
        self.token = token
        self.dry_run = dry_run
        self.req_id = 0

    def _call(self, method: str, params: Dict[str, Any]) -> Tuple[bool, Any]:
        self.req_id += 1
        p = {"access_token": self.token}
        p.update(params)
        payload = {
            "jsonrpc": "2.0",
            "id": self.req_id,
            "method": method,
            "params": p
        }
        try:
            r = requests.post(NOVOFON_URL, json=payload, timeout=10)
            data = r.json()
            if "error" in data:
                return False, data["error"]
            return True, data.get("result", {})
        except Exception as e:
            return False, {"message": str(e)}

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """Выгружает все контакты из адресной книги Новофон."""
        contacts = []
        offset = 0
        limit = 1000
        while True:
            ok, res = self._call("get.contacts", {"offset": offset, "limit": limit})
            if not ok:
                print(f"[!] Внимание при запросе к Новофон: {res}")
                break
            batch = res.get("data", [])
            contacts.extend(batch)
            if len(batch) < limit:
                break
            offset += limit
        return contacts

    def create_contact(self, last_name: str, first_name: str, patronymic: str, phone_numbers: List[str], emails: List[str] = None) -> Tuple[bool, Any]:
        params = {
            "last_name": last_name,
            "first_name": first_name or "",
            "patronymic": patronymic or "",
            "phone_numbers": phone_numbers
        }
        if emails:
            params["emails"] = emails
        if self.dry_run:
            print(f"    [DRY-RUN] Novofon create.contacts: {params}")
            return True, {"id": "dry_run_id"}
        return self._call("create.contacts", params)

    def update_contact(self, contact_id: int, last_name: str, first_name: str, patronymic: str, phone_numbers: List[str], emails: List[str] = None) -> Tuple[bool, Any]:
        params = {
            "id": contact_id,
            "last_name": last_name,
            "first_name": first_name or "",
            "patronymic": patronymic or "",
            "phone_numbers": phone_numbers
        }
        if emails:
            params["emails"] = emails
        if self.dry_run:
            print(f"    [DRY-RUN] Novofon update.contacts (ID {contact_id}): {params}")
            return True, {}
        return self._call("update.contacts", params)

class BitrixClient:
    def __init__(self, webhook: str, dry_run: bool = False):
        self.webhook = webhook.rstrip('/') + '/'
        self.dry_run = dry_run

    def get_companies(self) -> Dict[str, Dict[str, Any]]:
        """Выгружает все компании из Битрикс24."""
        print("[*] Выгрузка компаний из Битрикс24...")
        companies = {}
        start = 0
        while True:
            r = requests.get(self.webhook + 'crm.company.list', params={
                'SELECT[]': ['ID', 'TITLE', 'PHONE', 'EMAIL'],
                'order[ID]': 'ASC',
                'start': start
            }).json()
            batch = r.get('result', [])
            for c in batch:
                companies[str(c['ID'])] = c
            if 'next' in r:
                start = r['next']
            else:
                break
        print(f"[*] Загружено компаний: {len(companies)}")
        return companies

    def get_contacts(self, limit: Optional[int] = None, order_desc: bool = True) -> List[Dict[str, Any]]:
        """Выгружает контакты из Битрикс24."""
        order_str = 'DESC' if order_desc else 'ASC'
        print(f"[*] Выгрузка контактов из Битрикс24 (порядок {order_str})...")
        contacts = []
        start = 0
        while True:
            r = requests.get(self.webhook + 'crm.contact.list', params={
                'SELECT[]': ['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME', 'COMPANY_ID', 'PHONE', 'EMAIL', 'POST', 'COMMENTS'],
                f'order[ID]': order_str,
                'start': start
            }).json()
            batch = r.get('result', [])
            contacts.extend(batch)
            if limit and len(contacts) >= limit:
                contacts = contacts[:limit]
                break
            if 'next' in r:
                start = r['next']
            else:
                break
        print(f"[*] Загружено контактов: {len(contacts)}")
        return contacts

    def find_extension_in_emails(self, contact_id: str) -> Optional[str]:
        """Ищет добавочный номер в переписке контакта и связанных сделок."""
        # 1. Проверяем сделки контакта
        deal_res = requests.get(self.webhook + 'crm.deal.list', params={
            'filter[CONTACT_ID]': contact_id,
            'select[]': ['ID']
        }).json().get('result', [])
        
        owner_filters = [{'OWNER_ID': contact_id, 'OWNER_TYPE_ID': 3}]
        for d in deal_res[:3]:
            owner_filters.append({'OWNER_ID': d['ID'], 'OWNER_TYPE_ID': 2})

        for flt in owner_filters:
            r = requests.get(self.webhook + 'crm.activity.list', params={
                'filter[OWNER_ID]': flt['OWNER_ID'],
                'filter[OWNER_TYPE_ID]': flt['OWNER_TYPE_ID'],
                'filter[TYPE_ID]': 4,
                'order[ID]': 'DESC',
                'select[]': ['ID', 'DESCRIPTION'],
                'limit': 5
            }).json()
            for act in r.get('result', []):
                desc = act.get('DESCRIPTION', '')
                # Исключаем служебную часть подписи LongWang
                clean_body = re.sub(r'LongWang.*', '', desc, flags=re.IGNORECASE | re.DOTALL)
                ext = extract_extension(clean_body)
                if ext:
                    return ext
        return None

    def update_contact_second_name(self, contact_id: str, new_second_name: str) -> bool:
        """Обновляет отчество (добавочный) в Битрикс24."""
        if self.dry_run:
            print(f"    [DRY-RUN] Bitrix crm.contact.update (ID {contact_id}) -> SECOND_NAME='{new_second_name}'")
            return True
        r = requests.post(self.webhook + 'crm.contact.update', json={
            'id': contact_id,
            'fields': {'SECOND_NAME': new_second_name}
        })
        return r.status_code == 200

    def add_phone_to_company(self, company_id: str, phone: str) -> bool:
        """Добавляет недостающий номер телефона в карточку компании."""
        if self.dry_run:
            print(f"    [DRY-RUN] Bitrix crm.company.update (ID {company_id}) -> Добавить телефон {phone}")
            return True
        r = requests.post(self.webhook + 'crm.company.update', json={
            'id': company_id,
            'fields': {'PHONE': [{'VALUE_TYPE': 'WORK', 'VALUE': phone}]}
        })
        return r.status_code == 200

    def add_phone_to_contact(self, contact_id: str, phone: str) -> bool:
        """Добавляет недостающий номер телефона в карточку контакта."""
        if self.dry_run:
            print(f"    [DRY-RUN] Bitrix crm.contact.update (ID {contact_id}) -> Добавить телефон {phone}")
            return True
        r = requests.post(self.webhook + 'crm.contact.update', json={
            'id': contact_id,
            'fields': {'PHONE': [{'VALUE_TYPE': 'WORK', 'VALUE': phone}]}
        })
        return r.status_code == 200

def run_sync(dry_run: bool = True, test_batch: bool = False, limit: Optional[int] = None, novofon_token: str = DEFAULT_NOVOFON_TOKEN, report_file: Optional[str] = None, verbose: bool = False):
    from datetime import datetime
    print("=" * 70)
    print(f"[*] СТАРТ СИНХРОНИЗАЦИИ БИТРИКС24 <-> НОВОФОН (Режим DRY-RUN: {dry_run})")
    print("=" * 70)

    novofon = NovofonClient(token=novofon_token, dry_run=dry_run)
    bitrix = BitrixClient(webhook=B24_WEBHOOK, dry_run=dry_run)

    # 1. Загрузка существующей адресной книги Новофон
    print("[*] Чтение текущих контактов Новофон...")
    novo_contacts = novofon.get_all_contacts()
    novo_by_phone: Dict[str, Dict[str, Any]] = {}
    novo_by_name: Dict[str, List[Dict[str, Any]]] = {}

    for c in novo_contacts:
        c_id = c.get('id')
        l_name = (c.get('last_name') or '').strip().lower()
        if l_name:
            novo_by_name.setdefault(l_name, []).append(c)
        for ph in (c.get('phone_numbers') or []):
            norm = normalize_phone(ph)
            if norm:
                novo_by_phone[norm] = c
    print(f"[*] Загружено из Новофон: {len(novo_contacts)} контактов, {len(novo_by_phone)} уникальных номеров.")

    report_items = []

    if test_batch:
        print("[*] Режим TEST-BATCH: запуск по 6 эталонным кейсам...")
        target_contact_ids = ['16512', '16424', '16436', '14520', '16044']
        raw_contacts = []
        companies = {}
        for cid in target_contact_ids:
            c = requests.get(B24_WEBHOOK + 'crm.contact.get', params={'id': cid}).json().get('result', {})
            if c:
                raw_contacts.append(c)
                comp_id = str(c.get('COMPANY_ID') or '')
                if comp_id and comp_id not in companies:
                    comp_data = requests.get(B24_WEBHOOK + 'crm.company.get', params={'id': comp_id}).json().get('result', {})
                    if comp_data:
                        companies[comp_id] = comp_data
        target_company_ids = ['12068']
        for comp_id in target_company_ids:
            if comp_id not in companies:
                comp_data = requests.get(B24_WEBHOOK + 'crm.company.get', params={'id': comp_id}).json().get('result', {})
                if comp_data:
                    companies[comp_id] = comp_data
        comp_by_clean_title = {c.get('TITLE', '').strip().lower(): c for c in companies.values() if c.get('TITLE')}
    else:
        companies = bitrix.get_companies()
        comp_by_clean_title = {c.get('TITLE', '').strip().lower(): c for c in companies.values() if c.get('TITLE')}
        raw_contacts = []

        start = 0
        order_str = 'DESC'
        print(f"[*] Выгрузка контактов из Битрикс24 (порядок {order_str})...")
        while True:
            r = requests.get(B24_WEBHOOK + 'crm.contact.list', params={
                'SELECT[]': ['ID', 'NAME', 'LAST_NAME', 'SECOND_NAME', 'COMPANY_ID', 'PHONE', 'EMAIL', 'POST', 'COMMENTS', 'HAS_EMAIL'],
                'filter[HAS_PHONE]': 'Y',
                f'order[ID]': order_str,
                'start': start
            }).json()
            batch = r.get('result', [])
            for c in batch:
                if c.get('PHONE'):
                    raw_contacts.append(c)
                if limit and len(raw_contacts) >= limit:
                    break
            if (limit and len(raw_contacts) >= limit) or 'next' not in r or not batch:
                break
            start = r['next']
        print(f"[*] Отобрано контактов с телефонами: {len(raw_contacts)}")
        target_company_ids = [] if limit else list(companies.keys())

    # Статистика выполнения
    stats = {
        'contacts_processed': 0,
        'companies_processed': 0,
        'b24_enriched': 0,
        'b24_reverse_enriched': 0,
        'novofon_created': 0,
        'novofon_updated': 0,
        'skipped_no_phone': 0
    }

    # 3. Обработка контактов Битрикс24
    print("\n--- Обработка контактов ---")
    processed_phones: Set[str] = set()

    for c in raw_contacts:
        cid = str(c['ID'])
        stats['contacts_processed'] += 1
        name = (c.get('NAME') or '').strip()
        last_name = (c.get('LAST_NAME') or '').strip()
        second_name = (c.get('SECOND_NAME') or '').strip()
        company_id = str(c.get('COMPANY_ID') or '')
        
        # Определение названия компании / Фамилии в Новофон
        company_title = ""
        if company_id and company_id in companies:
            company_title = (companies[company_id].get('TITLE') or '').strip()
        
        # Правило поля Фамилия: Компания, если есть. Иначе Фамилия/Имя контакта
        novo_last_name = company_title if company_title else (last_name or name or "Частное лицо")
        # Правило поля Имя: Имя Фамилия контактного лица
        novo_first_name = f"{name} {last_name}".strip()

        # Поиск и валидация телефонов
        raw_phones = c.get('PHONE') or []
        phones = []
        phone_embedded_ext = None

        for p_item in raw_phones:
            val = p_item.get('VALUE', '')
            ext_found = extract_extension(val)
            if ext_found and not phone_embedded_ext:
                phone_embedded_ext = ext_found
            norm = normalize_phone(val)
            if norm and norm not in phones:
                phones.append(norm)

        # Обратное обогащение (Правило 3): если у контакта в Битрикс нет телефона, но в Новофон есть
        if not phones and novo_last_name.lower() in novo_by_name:
            candidates = novo_by_name[novo_last_name.lower()]
            for cand in candidates:
                for c_ph in cand.get('phone_numbers', []):
                    norm_c = normalize_phone(c_ph)
                    if norm_c:
                        print(f"  [<--] Обратное обогащение: найден телефон {norm_c} в Новофон для контакта {cid} ({novo_first_name})")
                        bitrix.add_phone_to_contact(cid, norm_c)
                        phones.append(norm_c)
                        stats['b24_reverse_enriched'] += 1
                        break
                if phones:
                    break

        if not phones:
            stats['skipped_no_phone'] += 1
            continue

        # Определение добавочного номера
        extension = None
        # Приоритет 1: в SECOND_NAME
        if second_name and ('доб' in second_name.lower() or any(ch.isdigit() for ch in second_name)):
            ext_match = extract_extension(second_name)
            extension = ext_match if ext_match else (second_name if 'доб' in second_name.lower() else f"доб. {second_name}")
        # Приоритет 2: в строке телефона
        elif phone_embedded_ext:
            extension = phone_embedded_ext
            if verbose:
                print(f"  [+] Обнаружен добавочный в номере контакта {cid}: {extension}")
            bitrix.update_contact_second_name(cid, extension)
            stats['b24_enriched'] += 1
        # Приоритет 3: поиск в подписи писем (только если у контакта есть email)
        elif c.get('HAS_EMAIL') == 'Y':
            email_ext = bitrix.find_extension_in_emails(cid)
            if email_ext:
                extension = email_ext
                if verbose:
                    print(f"  [+] Обнаружен добавочный в Email-переписке контакта {cid} ({novo_first_name}): {extension}")
                bitrix.update_contact_second_name(cid, extension)
                stats['b24_enriched'] += 1

        # Обратное обогащение (Правило 3): если добавочного в Битрикс нет, но в Новофон он записан
        if not extension and novo_last_name.lower() in novo_by_name:
            candidates = novo_by_name[novo_last_name.lower()]
            for cand in candidates:
                novo_pat = cand.get('patronymic', '')
                ext_from_novo = extract_extension(novo_pat)
                if ext_from_novo:
                    extension = ext_from_novo
                    if verbose:
                        print(f"  [<--] Обратное обогащение: перенос добавочного {extension} из Новофон в Битрикс контакт {cid}")
                    bitrix.update_contact_second_name(cid, extension)
                    stats['b24_reverse_enriched'] += 1
                    break

        novo_patronymic = extension or ""

        # Проверка наличия контакта в Новофон (по номерам телефона)
        existing_novo_id = None
        for ph in phones:
            if ph in novo_by_phone:
                existing_novo_id = novo_by_phone[ph].get('id')
                break

        if verbose:
            print(f"\n[Контакт B24 #{cid}] {novo_first_name} | {novo_last_name} | {novo_patronymic} | {phones}")
        recorded_id = existing_novo_id
        if existing_novo_id:
            if verbose:
                print(f"  -> Уже существует в Новофон (ID {existing_novo_id}) -> ОБНОВЛЕНИЕ/ПЕРЕЗАПИСЬ")
            ok, res = novofon.update_contact(
                contact_id=existing_novo_id,
                last_name=novo_last_name,
                first_name=novo_first_name,
                patronymic=novo_patronymic,
                phone_numbers=phones
            )
            if ok:
                if verbose:
                    print(f"    [OK] Успешно обновлено в Новофон (ID: {existing_novo_id})")
                stats['novofon_updated'] += 1
            else:
                print(f"    [!] Ошибка обновления контакта {cid} в Новофон: {res}")
        else:
            if verbose:
                print(f"  -> Новый контакт для Новофон -> СОЗДАНИЕ")
            ok, res = novofon.create_contact(
                last_name=novo_last_name,
                first_name=novo_first_name,
                patronymic=novo_patronymic,
                phone_numbers=phones
            )
            if ok:
                new_id = res.get('data', {}).get('id') if isinstance(res, dict) else res
                recorded_id = new_id
                if verbose:
                    print(f"    [OK] Успешно создан в Новофон (ID: {new_id})")
                stats['novofon_created'] += 1
            else:
                print(f"    [!] Ошибка создания контакта {cid} в Новофон: {res}")

        if stats['contacts_processed'] % 50 == 0:
            print(f"  [*] Прогресс: обработано {stats['contacts_processed']} контактов (создано: {stats['novofon_created']}, обновлено: {stats['novofon_updated']})...")

        report_items.append({
            'type': 'Контакт',
            'cid': cid,
            'full_name': novo_first_name,
            'company': novo_last_name,
            'patronymic': novo_patronymic,
            'phones': ', '.join(phones),
            'action': 'Обновлен' if existing_novo_id else 'Создан',
            'novo_id': recorded_id or '-'
        })

        for ph in phones:
            processed_phones.add(ph)

    # 4. Обработка общих номеров компаний (где нет физлиц)
    if target_company_ids:
        print("\n--- Обработка компаний без привязанных контактов ---")
    for comp_id in target_company_ids:
        comp = companies.get(comp_id)
        if not comp:
            continue
        raw_ph = comp.get('PHONE') or []
        comp_phones = []
        for p in raw_ph:
            norm = normalize_phone(p.get('VALUE', ''))
            if norm and norm not in processed_phones:
                comp_phones.append(norm)

        comp_title = (comp.get('TITLE') or '').strip()

        # Обратное обогащение (Правило 3): если у компании нет телефона в Битрикс, но есть в Новофон
        if not comp_phones and comp_title.lower() in novo_by_name:
            candidates = novo_by_name[comp_title.lower()]
            for cand in candidates:
                for c_ph in cand.get('phone_numbers', []):
                    norm_c = normalize_phone(c_ph)
                    if norm_c and norm_c not in processed_phones:
                        if verbose:
                            print(f"  [<--] Обратное обогащение: найден телефон {norm_c} в Новофон для компании {comp_id} ({comp_title})")
                        bitrix.add_phone_to_company(comp_id, norm_c)
                        comp_phones.append(norm_c)
                        stats['b24_reverse_enriched'] += 1
                        break
                if comp_phones:
                    break

        if not comp_phones:
            continue

        stats['companies_processed'] += 1
        if verbose:
            print(f"\n[Компания #{comp_id}] {comp_title} (Общий номер) | Телефоны: {comp_phones}")
        
        # Проверяем в Новофон
        existing_novo_id = None
        for ph in comp_phones:
            if ph in novo_by_phone:
                existing_novo_id = novo_by_phone[ph].get('id')
                break

        recorded_id = existing_novo_id
        if existing_novo_id:
            if verbose:
                print(f"  -> Компания уже в Новофон (ID {existing_novo_id}) -> ОБНОВЛЕНИЕ/ПЕРЕЗАПИСЬ")
            ok, res = novofon.update_contact(
                contact_id=existing_novo_id,
                last_name=comp_title,
                first_name="Общий номер",
                patronymic="",
                phone_numbers=comp_phones
            )
            if ok:
                if verbose:
                    print(f"    [OK] Успешно обновлено в Новофон (ID: {existing_novo_id})")
                stats['novofon_updated'] += 1
            else:
                print(f"    [!] Ошибка обновления компании {comp_id} в Новофон: {res}")
        else:
            if verbose:
                print(f"  -> Компания новая для Новофон -> СОЗДАНИЕ")
            ok, res = novofon.create_contact(
                last_name=comp_title,
                first_name="Общий номер",
                patronymic="",
                phone_numbers=comp_phones
            )
            if ok:
                new_id = res.get('data', {}).get('id') if isinstance(res, dict) else res
                recorded_id = new_id
                if verbose:
                    print(f"    [OK] Успешно создано в Новофон (ID: {new_id})")
                stats['novofon_created'] += 1
            else:
                print(f"    [!] Ошибка создания компании {comp_id} в Новофон: {res}")

        if stats['companies_processed'] % 50 == 0:
            print(f"  [*] Прогресс: обработано {stats['companies_processed']} компаний...")

        report_items.append({
            'type': 'Компания',
            'cid': comp_id,
            'full_name': 'Общий номер',
            'company': comp_title,
            'patronymic': '',
            'phones': ', '.join(comp_phones),
            'action': 'Обновлен' if existing_novo_id else 'Создан',
            'novo_id': recorded_id or '-'
        })

        for ph in comp_phones:
            processed_phones.add(ph)

    # 5. Сохранение файла отчета
    if report_file:
        os.makedirs(os.path.dirname(os.path.abspath(report_file)), exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Отчет синхронизации Битрикс24 <-> Новофон\n\n")
            f.write(f"- **Дата и время:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **Режим:** {'DRY-RUN (предпросмотр)' if dry_run else 'БОЕВОЙ'}\n")
            f.write(f"- **Контактов обработано:** {stats['contacts_processed']}\n")
            f.write(f"- **Компаний обработано:** {stats['companies_processed']}\n")
            f.write(f"- **Обогащено в Битрикс24 (добавлен добавочный):** {stats['b24_enriched']}\n")
            f.write(f"- **Обратно обогащено в Битрикс24 из Новофон:** {stats['b24_reverse_enriched']}\n")
            f.write(f"- **Создано в Новофон:** {stats['novofon_created']}\n")
            f.write(f"- **Обновлено в Новофон:** {stats['novofon_updated']}\n")
            f.write(f"- **Пропущено без телефонов:** {stats['skipped_no_phone']}\n\n")
            f.write("## Детализация по обработанным контактам и компаниям\n\n")
            f.write("| № | Тип | ID B24 | Фамилия (last_name) | Имя (first_name) | Отчество (patronymic) | Телефоны | Действие | ID Новофон |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
            for idx, item in enumerate(report_items, start=1):
                f.write(f"| {idx} | {item['type']} | {item['cid']} | {item['company']} | {item['full_name']} | {item['patronymic']} | `{item['phones']}` | {item['action']} | {item['novo_id']} |\n")
        print(f"\n[+] Полный отчет ({len(report_items)} записей) сохранен в файл: {report_file}")

    print("\n" + "=" * 70)
    print(f"[*] СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА:")
    print(f"    - Контактов обработано: {stats['contacts_processed']}")
    print(f"    - Компаний обработано: {stats['companies_processed']}")
    print(f"    - Обогащено в Битрикс24 (добавлен доб.): {stats['b24_enriched']}")
    print(f"    - Обратно обогащено в Битрикс24 из Новофон: {stats['b24_reverse_enriched']}")
    print(f"    - Создано в Новофон: {stats['novofon_created']}")
    print(f"    - Обновлено в Новофон: {stats['novofon_updated']}")
    print(f"    - Пропущено без телефонов: {stats['skipped_no_phone']}")
    print("=" * 70)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Синхронизация контактов Битрикс24 <-> Новофон")
    parser.add_argument('--dry-run', action='store_true', help="Предпросмотр без внесения изменений")
    parser.add_argument('--test-batch', action='store_true', help="Прогон по 6 эталонным кейсам")
    parser.add_argument('--limit', type=int, default=None, help="Ограничение количества контактов")
    parser.add_argument('--token', type=str, default=DEFAULT_NOVOFON_TOKEN, help="Токен API Новофон")
    parser.add_argument('--report-file', type=str, default=None, help="Файл для сохранения детального отчета")
    parser.add_argument('--verbose', action='store_true', help="Подробный вывод каждого контакта")
    args = parser.parse_args()

    run_sync(
        dry_run=args.dry_run,
        test_batch=args.test_batch,
        limit=args.limit,
        novofon_token=args.token,
        report_file=args.report_file,
        verbose=args.verbose
    )
