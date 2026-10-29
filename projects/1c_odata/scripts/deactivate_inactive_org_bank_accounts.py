# -*- coding: utf-8 -*-
"""
Канонический скрипт аудита и деактивации неактивных банковских счетов организаций в 1С:УНФ
(Deactivate Inactive Organization Bank Accounts Pipeline)

Бизнес-логика:
1. Загружает список собственных организаций (Catalog_Организации) и их основные банковские счета.
2. Находит все банковские счета (Catalog_БанковскиеСчета), принадлежащие этим организациям.
3. Проверяет активность по каждому счету за последние N дней (по умолчанию 365):
   - Document_ПоступлениеНаСчет (Posted eq true)
   - Document_РасходСоСчета (Posted eq true)
   - Document_ПеремещениеДС (если присутствует в конфигурации)
4. Вычисляет точную дату последней финансовой операции по каждому счету.
5. Инвариант безопасности:
   - Основной банковский счет организации защищен от деактивации (Safety Guard).
   - Если счет уже помечен как "Недействителен", повторная обработка исключается.
6. Формирует детализированный CSV-отчет в режиме Dry-Run (utf-8-sig для Excel).
7. Модификация (PATCH) в 1С выполняется ТОЛЬКО при явном указании флага --apply
   после согласования dry-run отчета с пользователем.

Использование:
    py projects/1c_odata/scripts/deactivate_inactive_org_bank_accounts.py --dry-run
    py projects/1c_odata/scripts/deactivate_inactive_org_bank_accounts.py --days 365 --export-csv "projects/1c_odata/reports/inactive_bank_accounts_dry_run.csv"
    py projects/1c_odata/scripts/deactivate_inactive_org_bank_accounts.py --apply
"""

import os
import sys
import csv
import json
import argparse
from datetime import datetime, timedelta
import urllib.parse
import requests
from requests.auth import HTTPBasicAuth

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def load_env():
    """Загрузка переменных окружения из .env файлов проекта."""
    search_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        r"C:\Codex\projects\1c_odata\.env",
    ]
    for p in search_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v


load_env()

ODATA_BASE = os.getenv("ONEC_ODATA_URL", "http://artem.medianasoft.spb.ru/unf/odata/standard.odata").rstrip("/")
ODATA_USER = os.getenv("ONEC_ODATA_USER", "odata.writer")
ODATA_PASS = os.getenv("ONEC_ODATA_PASSWORD", "")


class ODataClient:
    def __init__(self, base_url: str, user: str, password: str):
        self.base_url = base_url
        self.auth = HTTPBasicAuth(user, password) if user else None
        self.headers = {"Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}
        self.session = requests.Session()
        if self.auth:
            self.session.auth = self.auth
        self.session.headers.update(self.headers)

    def get(self, endpoint: str, params: dict = None, timeout: int = 30):
        url = f"{self.base_url}/{endpoint}"
        resp = self.session.get(url, params=params, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"OData GET error [{resp.status_code}] on {url}: {resp.text[:300]}")
        return resp.json()

    def patch(self, endpoint: str, data: dict, timeout: int = 30):
        url = f"{self.base_url}/{endpoint}"
        resp = self.session.patch(url, json=data, timeout=timeout)
        if resp.status_code not in (200, 204):
            raise RuntimeError(f"OData PATCH error [{resp.status_code}] on {url}: {resp.text[:300]}")
        return resp.status_code


def parse_odata_date(date_str: str):
    """Парсинг даты из формата OData 1C (ISO формат YYYY-MM-DDTHH:MM:SS)."""
    if not date_str:
        return None
    cleaned = date_str.split(".")[0].rstrip("Z")
    try:
        return datetime.fromisoformat(cleaned)
    except Exception:
        try:
            return datetime.strptime(cleaned[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return None


def fetch_organizations(client: ODataClient):
    """Получение всех организаций и их основных банковских счетов."""
    data = client.get("Catalog_Организации?$format=json&$filter=DeletionMark eq false")
    orgs = {}
    items = data.get("value", [])
    for item in items:
        ref_key = item.get("Ref_Key")
        name = item.get("Description", "").strip()
        inn = item.get("ИНН", "").strip()
        default_account_key = item.get("БанковскийСчетПоУмолчанию_Key") or item.get("ОсновнойБанковскийСчет_Key")
        orgs[ref_key] = {
            "ref_key": ref_key,
            "name": name,
            "inn": inn,
            "default_account_key": default_account_key,
        }
    return orgs


def fetch_bank_accounts_for_orgs(client: ODataClient, org_keys: set):
    """Получение банковских счетов организаций."""
    data = client.get("Catalog_БанковскиеСчета?$format=json&$filter=DeletionMark eq false&$top=10")
    sample_items = data.get("value", [])
    if sample_items:
        first = sample_items[0]
        # Выведем доступные ключи первого элемента для диагностики схемы
        owner_fields = [k for k in first.keys() if "owner" in k.lower() or "владелец" in k.lower()]
        print(f"[*] Диагностика полей владельца в Catalog_БанковскиеСчета: {owner_fields}")
    
    # Теперь запросим все счета
    data = client.get("Catalog_БанковскиеСчета?$format=json&$filter=DeletionMark eq false")
    all_accounts = data.get("value", [])
    print(f"[*] Всего счетов в базе (не удаленных): {len(all_accounts)}")
    
    org_accounts = []
    for acc in all_accounts:
        # Проверяем все возможные варианты поля владельца
        owner_key = acc.get("Owner_Key") or acc.get("Владелец_Key") or acc.get("Owner")
        # В 1С составной тип владельца может быть строкой вида "StandardODATA.Catalog_Организации/guid'...' " или объектом
        if isinstance(owner_key, dict):
            owner_key = owner_key.get("Ref_Key") or owner_key.get("Key")
        elif isinstance(owner_key, str) and "guid'" in owner_key:
            import re
            m = re.search(r"guid'([0-9a-fA-F-]+)'", owner_key)
            if m:
                owner_key = m.group(1)
                
        if owner_key in org_keys:
            acc["_resolved_owner_key"] = owner_key
            org_accounts.append(acc)
            
    return org_accounts


# Белый список исключений по прямому указанию пользователя (спецсчета, тендерные счета, резервные CNY)
USER_PROTECTED_GUIDS = {
    "812210e8-7436-11ee-9662-70a8d3ba8753": "Ци Линь: юаневый счет ДелоБанк (Синара)",
    "eb0230b0-1934-11f1-905b-02006df8aab5": "Ци Линь: спецсчет Банк ПСБ (119046)",
    "9198f029-3ad2-11ee-964c-70a8d3ba8753": "Лун-Ван / Ци Линь: тендерный спецсчет Альфа-Банк",
    "9329437b-ca52-11ed-b999-f01898a67170": "Лун-Ван / Ци Линь: спецсчет Альфа-Банк",
}


def get_latest_movement_date(client: ODataClient, account_key: str):
    """Поиск даты последней операции по счету (поступление или расход)."""
    latest_dates = []

    # 1. Поступления на счет
    try:
        url_receipt = f"Document_ПоступлениеНаСчет?$format=json&$filter=БанковскийСчет_Key eq guid'{account_key}' and Posted eq true&$orderby=Date desc&$top=1&$select=Date,Number"
        res_r = client.get(url_receipt)
        items_r = res_r.get("value", [])
        if items_r:
            d = parse_odata_date(items_r[0].get("Date"))
            if d:
                latest_dates.append(d)
    except Exception:
        pass

    # 2. Расход со счета
    try:
        url_expense = f"Document_РасходСоСчета?$format=json&$filter=БанковскийСчет_Key eq guid'{account_key}' and Posted eq true&$orderby=Date desc&$top=1&$select=Date,Number"
        res_e = client.get(url_expense)
        items_e = res_e.get("value", [])
        if items_e:
            d = parse_odata_date(items_e[0].get("Date"))
            if d:
                latest_dates.append(d)
    except Exception:
        pass

    # 3. Перемещение ДС (безналичное перемещение, если поддерживается)
    try:
        url_transfer = f"Document_ПеремещениеДС?$format=json&$filter=(БанковскийСчет_Key eq guid'{account_key}' or БанковскийСчетПолучатель_Key eq guid'{account_key}') and Posted eq true&$orderby=Date desc&$top=1&$select=Date,Number"
        res_t = client.get(url_transfer)
        items_t = res_t.get("value", [])
        if items_t:
            d = parse_odata_date(items_t[0].get("Date"))
            if d:
                latest_dates.append(d)
    except Exception:
        pass

    if latest_dates:
        return max(latest_dates)
    return None


def search_special_accounts(csv_path: str):
    """Поиск спецсчетов и счетов по ключевым словам среди всех наших организаций."""
    if not os.path.exists(csv_path):
        return

    keywords = ["спец", "альфа", "псб", "дело", "синара", "петербург", "cny", "юан", "тендер"]
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        print("\n[*] Поиск счетов по ключевым словам (спец/альфа/псб/дело/петербург/cny/тендер):")
        print("=" * 110)
        for r in reader:
            desc = r.get("Наименование счета", "").lower()
            num = r.get("Номер счета", "").lower()
            if any(k in desc or k in num for k in keywords):
                print(f"[{r['Организация']}] {r['Номер счета']} | {r['Наименование счета']}")
                print(f"    GUID: {r['GUID счета']} | Статус: {r['Текущий статус (Недействителен)']} | Посл. движение: {r['Дата последнего движения']} | Решение: {r['Решение']}")
        print("=" * 110)


def inspect_org_accounts(csv_path: str, org_substr: str):
    """Вывод всех счетов организации для анализа исключений."""
    if not os.path.exists(csv_path):
        print(f"[!] Файл не найден: {csv_path}")
        return

    matched = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            if org_substr.lower() in row.get("Организация", "").lower():
                matched.append(row)

    print(f"\n[*] Все счета организации '{org_substr}' (всего: {len(matched)}):")
    print("=" * 110)
    for idx, r in enumerate(matched, 1):
        status = "НЕДЕЙСТВИТЕЛЕН" if r.get("Текущий статус (Недействителен)") == "ДА" else "ДЕЙСТВУЕТ"
        print(f"{idx:2d}. Счет: {r['Номер счета']}")
        print(f"    Наименование: {r['Наименование счета']}")
        print(f"    GUID: {r['GUID счета']}")
        print(f"    Статус в 1С: [{status}] | Посл. движение: {r['Дата последнего движения']} ({r['Дней без движений']} дн.)")
        print(f"    Текущее решение скрипта: {r['Решение']} -> {r['Действие']}")
        print("-" * 110)


def print_remaining_active_accounts(csv_path: str, days: int = 365):
    """Вывод красивого списка счетов, которые останутся действующими."""
    if not os.path.exists(csv_path):
        print(f"[!] Файл не найден: {csv_path}")
        return

    remaining = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            # Счет остается действующим, если он не деактивируется и не был уже недействительным
            if row.get("Решение") != "DEACTIVATE" and row.get("Текущий статус (Недействителен)") != "ДА":
                remaining.append(row)

    print(f"\n[+] Счета, которые ОСТАНУТСЯ ДЕЙСТВУЮЩИМИ (всего: {len(remaining)}):")
    print("-" * 100)
    for idx, r in enumerate(remaining, 1):
        action_text = r.get("Действие", "")
        print(f"{idx:2d}. [{r['Организация']}]")
        print(f"    Счет: {r['Номер счета']} | {r['Наименование счета']}")
        print(f"    Посл. операция: {r['Дата последнего движения']} ({r['Дней без движений']} дн. назад) | {action_text}")
    print("-" * 100)
    return remaining


def run_pipeline(days: int = 365, apply_changes: bool = False, export_csv: str = None):
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    
    print(f"[*] Инициализация подключения к 1С:УНФ OData: {ODATA_BASE}")
    print(f"[*] Пользователь: {ODATA_USER}")
    print(f"[*] Режим: {'БОЕВАЯ МОДИФИКАЦИЯ (--apply)' if apply_changes else 'DRY RUN (Безопасный аудит)'}")
    print(f"[*] Порог неактивности: {days} дней (до {cutoff_date.strftime('%Y-%m-%d %H:%M')})")
    
    client = ODataClient(ODATA_BASE, ODATA_USER, ODATA_PASS)

    # 1. Загрузка организаций
    print("[*] Загрузка справочника организаций (Catalog_Организации)...")
    orgs = fetch_organizations(client)
    print(f"[+] Найдено активных организаций: {len(orgs)}")
    for o_key, o_info in orgs.items():
        print(f"    - {o_info['name']} (ИНН: {o_info['inn'] or 'нет'}) | Основной счет GUID: {o_info['default_account_key']}")

    org_keys = set(orgs.keys())
    if not org_keys:
        print("[!] Внимание: организации не найдены.")
        return

    # 2. Загрузка банковских счетов
    print("[*] Загрузка банковских счетов организаций (Catalog_БанковскиеСчета)...")
    accounts = fetch_bank_accounts_for_orgs(client, org_keys)
    print(f"[+] Найдено банковских счетов организаций: {len(accounts)}")

    report_rows = []
    to_deactivate = []
    already_inactive = 0
    protected_primary = 0
    active_recent = 0

    print("[*] Проверка истории движений денежных средств по счетам...")
    for idx, acc in enumerate(accounts, 1):
        ref_key = acc.get("Ref_Key")
        owner_key = acc.get("_resolved_owner_key") or acc.get("Owner_Key") or acc.get("Владелец_Key")
        acc_num = acc.get("НомерСчета", "").strip() or acc.get("Description", "").strip()
        acc_desc = acc.get("Description", "").strip()
        is_inactive_current = bool(acc.get("Недействителен", False))
        
        org_info = orgs.get(owner_key, {"name": "Неизвестная организация", "inn": "", "default_account_key": None})
        org_name = org_info["name"]
        org_inn = org_info["inn"]
        is_primary = (ref_key == org_info.get("default_account_key"))

        # Получаем последнее движение
        latest_date = get_latest_movement_date(client, ref_key)
        
        if latest_date:
            days_since = (now - latest_date).days
            latest_str = latest_date.strftime("%Y-%m-%d")
            has_recent_movement = (latest_date >= cutoff_date)
        else:
            days_since = 99999
            latest_str = "Нет движений"
            has_recent_movement = False

        # Определение действия
        is_spec_or_tender = (
            acc_num.startswith("47405") 
            or "спец" in acc_desc.lower() 
            or "тендер" in acc_desc.lower()
        )

        if is_primary:
            action = "ЗАЩИТА: Основной счет организации (нельзя отключать)"
            decision = "SKIP_PRIMARY"
            protected_primary += 1
        elif is_inactive_current:
            action = "ПРОПУСК: Уже помечен как недействительный"
            decision = "ALREADY_INACTIVE"
            already_inactive += 1
        elif ref_key in USER_PROTECTED_GUIDS:
            reason_wl = USER_PROTECTED_GUIDS[ref_key]
            action = f"ЗАЩИТА (Whitelist): {reason_wl}"
            decision = "SKIP_WHITELIST"
            active_recent += 1
        elif is_spec_or_tender:
            action = f"ЗАЩИТА (Спецсчет/Тендер 47405): {acc_desc}"
            decision = "SKIP_SPEC_ACCOUNT"
            active_recent += 1
        elif has_recent_movement:
            action = f"ПРОПУСК: Активен (движение {latest_str}, {days_since} дн. назад)"
            decision = "ACTIVE"
            active_recent += 1
        else:
            action = f"К ДЕАКТИВАЦИИ: Неактивен > {days} дн. (последнее: {latest_str})"
            decision = "DEACTIVATE"
            to_deactivate.append({
                "ref_key": ref_key,
                "org_name": org_name,
                "acc_num": acc_num,
                "acc_desc": acc_desc,
                "latest_str": latest_str,
                "days_since": days_since,
            })

        report_rows.append({
            "Организация": org_name,
            "ИНН": org_inn,
            "Наименование счета": acc_desc,
            "Номер счета": acc_num,
            "GUID счета": ref_key,
            "Основной счет организации": "ДА" if is_primary else "НЕТ",
            "Текущий статус (Недействителен)": "ДА" if is_inactive_current else "НЕТ",
            "Дата последнего движения": latest_str,
            "Дней без движений": str(days_since) if days_since != 99999 else "—",
            "Решение": decision,
            "Действие": action,
        })

    # Экспорт отчета CSV
    if not export_csv:
        rep_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        os.makedirs(rep_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_csv = os.path.join(rep_dir, f"inactive_org_bank_accounts_dry_run_{timestamp}.csv")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(export_csv)), exist_ok=True)

    with open(export_csv, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = [
            "Организация", "ИНН", "Наименование счета", "Номер счета",
            "GUID счета", "Основной счет организации", "Текущий статус (Недействителен)",
            "Дата последнего движения", "Дней без движений", "Решение", "Действие"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(report_rows)

    print("\n" + "=" * 60)
    print("ИТОГИ АУДИТА БАНКОВСКИХ СЧЕТОВ НАШИХ ОРГАНИЗАЦИЙ")
    print("=" * 60)
    print(f"Всего счетов проверено:                     {len(accounts)}")
    print(f"Счетов с недавними движениями (< {days} дн.):   {active_recent}")
    print(f"Защищено (основные счета организаций):       {protected_primary}")
    print(f"Уже были помечены недействительными:         {already_inactive}")
    print(f"КАНДИДАТОВ НА ДЕАКТИВАЦИЮ (Недействителен):   {len(to_deactivate)}")
    print("=" * 60)
    print(f"[+] Детализированный отчет Dry-Run сохранен: {os.path.abspath(export_csv)}")

    # Вывод кандидатов
    if to_deactivate:
        print("\nСписок счетов к деактивации:")
        for item in to_deactivate:
            print(f"  • [{item['org_name']}] Счет: {item['acc_num']} ({item['acc_desc']}) | Движение: {item['latest_str']} ({item['days_since']} дн.)")
    else:
        print("\n[+] Счетов, требующих деактивации, не обнаружено.")

    # Если включен режим --apply
    if apply_changes:
        if not to_deactivate:
            print("\n[*] Нет счетов для изменения.")
            return

        print(f"\n[!] ВНИМАНИЕ: Запуск боевого обновления {len(to_deactivate)} счетов через OData PATCH...")
        updated_count = 0
        error_count = 0
        for item in to_deactivate:
            ref_key = item["ref_key"]
            endpoint = f"Catalog_БанковскиеСчета(guid'{ref_key}')"
            patch_body = {"Недействителен": True}
            try:
                client.patch(endpoint, patch_body)
                print(f"  [OK] Обновлен счет {item['acc_num']} ({item['org_name']})")
                updated_count += 1
            except Exception as e:
                print(f"  [ERROR] Сбой обновления счета {item['acc_num']}: {e}")
                error_count += 1
        print(f"\n[+] Итог применения: успешно обновлено {updated_count}, ошибок {error_count}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Аудит и деактивация неактивных счетов организаций в 1С:УНФ.")
    parser.add_argument("--days", type=int, default=365, help="Порог неактивности в днях (по умолчанию 365).")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Режим сухой проверки без записи в базу (по умолчанию).")
    parser.add_argument("--apply", action="store_true", default=False, help="Применить изменения в базе 1С:УНФ (PATCH Недействителен=True).")
    parser.add_argument("--export-csv", type=str, default=None, help="Путь к экспортируемому CSV-файлу.")
    parser.add_argument("--show-active", type=str, default=None, help="Показать остающиеся действующие счета из указанного CSV отчета.")
    parser.add_argument("--search-special", action="store_true", help="Поиск спецсчетов и счетов по ключевым банкам.")
    parser.add_argument("--inspect-org", type=str, default=None, help="Вывести все счета организации (например, 'ЦИ ЛИНЬ') из указанного отчета.")
    args = parser.parse_args()

    if args.search_special:
        csv_file = args.export_csv or "projects/1c_odata/reports/inactive_org_bank_accounts_dry_run_20261028_132840.csv"
        search_special_accounts(csv_file)
        sys.exit(0)

    if args.inspect_org:
        csv_file = args.export_csv or "projects/1c_odata/reports/inactive_org_bank_accounts_dry_run_20261028_132840.csv"
        inspect_org_accounts(csv_file, args.inspect_org)
        sys.exit(0)

    if args.show_active:
        print_remaining_active_accounts(args.show_active, days=args.days)
        sys.exit(0)

    # Если передан флаг --apply, отключаем dry-run
    apply_mode = args.apply
    run_pipeline(days=args.days, apply_changes=apply_mode, export_csv=args.export_csv)
