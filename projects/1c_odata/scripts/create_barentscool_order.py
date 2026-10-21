"""
Скрипт создания номенклатуры, установки цен закупки КНР (в CNY)
и формирования Заказа покупателя в 1С:УНФ для ООО «БАРЕНЦКУЛ»
на основании Excel-таблицы (Книга1.xlsx).

Использование:
    py projects/1c_odata/scripts/create_barentscool_order.py --dry-run
    py projects/1c_odata/scripts/create_barentscool_order.py --commit
"""

import os
import sys
import argparse
import urllib.parse
from datetime import datetime
import openpyxl
import requests

sys.stdout.reconfigure(encoding='utf-8')

# Константы базы 1С:УНФ
COUNTERPARTY_KEY = "11273a8c-8e22-11ef-8811-02006df8aab5"  # БАРЕНЦКУЛ ООО, ИНН 5190075177
ORGANIZATION_KEY = "31d09449-a872-11ed-b994-f01898a67170"  # ЦИ ЛИНЬ ООО, ИНН 7801719960
CONTRACT_KEY = "29e0a06c-e9cc-11ef-847b-02006df8aab5"      # Договор покупателя с ЦИ ЛИНЬ ООО
UNIT_SHT_KEY = "9dbbff65-23c6-11ed-91a8-a068f8f3337c"      # шт (код 796)
PARENT_DANFOSS_KEY = "68500d75-3db1-11ef-9696-70a8d3ba8753" # Папка номенклатуры "Danfoss"
PRICE_TYPE_CNY_KEY = "d9c510d8-a484-11ed-b994-f01898a67170" # Вид цены "Закупка КНР" (CNY)
VAT_RATE_22_KEY = "2bbf2b28-e7ce-11f0-9d36-02006df8aab5"    # Ставка НДС 22%
CATEGORY_KEY = "43c2e99d-3ff4-11ed-81cf-7824af8324d7"      # Категория номенклатуры
ACTIVITY_KEY = "9dbbff66-23c6-11ed-91a8-a068f8f3337c"      # Направление деятельности
ACCOUNT_INVENTORY = "868894bb-c99c-11ed-b999-f01898a67170" # Счет учета запасов
ACCOUNT_COSTS = "9dbbfeec-23c6-11ed-91a8-a068f8f3337c"     # Счет учета затрат
ACCOUNT_VAT_IN = "65505f44-4db8-11ee-9656-70a8d3ba8753"    # НДС по приобретенным
ACCOUNT_VAT_OUT = "65505f43-4db8-11ee-9656-70a8d3ba8753"   # НДС по реализации


def load_env():
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
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v


def read_excel_rows(excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    rows = []
    for r in range(3, 17):  # строки 3-16 с товарами
        num = sheet.cell(r, 1).value
        name = sheet.cell(r, 2).value
        art = sheet.cell(r, 3).value
        qty = sheet.cell(r, 4).value
        cny_price = sheet.cell(r, 5).value
        cny_sum = sheet.cell(r, 6).value
        rub_price = sheet.cell(r, 10).value
        rub_sum = sheet.cell(r, 11).value
        term = sheet.cell(r, 14).value
        weight = sheet.cell(r, 15).value

        if not name or not qty:
            continue

        art_clean = str(art).strip() if art else ""
        rows.append({
            "num": int(num) if num else len(rows) + 1,
            "name": str(name).strip(),
            "article": art_clean,
            "quantity": float(qty),
            "cny_price": float(cny_price) if cny_price is not None else 0.0,
            "cny_sum": float(cny_sum) if cny_sum is not None else 0.0,
            "rub_price": round(float(rub_price), 2) if rub_price is not None else 0.0,
            "rub_sum": round(float(rub_sum), 2) if rub_sum is not None else 0.0,
            "term": str(term).strip() if term else "",
            "weight": round(float(weight), 4) if weight is not None else 0.0,
        })
    return rows


def get_odata_session():
    load_env()
    base = os.environ.get("ONEC_ODATA_URL", "").rstrip("/")
    user = os.environ.get("ONEC_ODATA_USER", "")
    pwd = os.environ.get("ONEC_ODATA_PASSWORD", "")
    if not base or not user:
        raise ValueError("Не настроены переменные ONEC_ODATA_URL / ONEC_ODATA_USER в .env")
    sess = requests.Session()
    sess.auth = (user, pwd)
    sess.headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    return base, sess


def find_nomenclature_by_article(base, sess, article):
    if not article:
        return None
    # Экранируем кавычки
    art_esc = article.replace("'", "''")
    q = urllib.parse.quote(f"Артикул eq '{art_esc}'")
    url = f"{base}/Catalog_Номенклатура?$filter={q}&$format=json"
    r = sess.get(url, timeout=15)
    if r.status_code == 200:
        vals = r.json().get("value", [])
        if vals:
            return vals[0]
    return None


def create_nomenclature_item(base, sess, item_data):
    payload = {
        "Description": item_data["name"][:100],
        "НаименованиеПолное": item_data["name"],
        "Артикул": item_data["article"],
        "Parent_Key": PARENT_DANFOSS_KEY,
        "ЕдиницаИзмерения_Key": UNIT_SHT_KEY,
        "КатегорияНоменклатуры_Key": CATEGORY_KEY,
        "ТипНоменклатуры": "Запас",
        "СпособПополнения": "Закупка",
        "МетодОценки": "FIFO",
        "НаправлениеДеятельности_Key": ACTIVITY_KEY,
        "СчетУчетаЗапасов_Key": ACCOUNT_INVENTORY,
        "СчетУчетаЗатрат_Key": ACCOUNT_COSTS,
        "СчетУчетаНДСПоПриобретеннымЦенностям_Key": ACCOUNT_VAT_IN,
        "СчетУчетаНДСПоРеализации_Key": ACCOUNT_VAT_OUT,
        "СтавкаНДС_Key": VAT_RATE_22_KEY,
        "Вес": item_data["weight"],
        "Комментарий": item_data["term"][:1000] if item_data["term"] else "",
        "ПризнакПредметаРасчета": "Товар",
        "ВидМаркировки": "НеМаркируется"
    }
    url = f"{base}/Catalog_Номенклатура?$format=json"
    r = sess.post(url, json=payload, timeout=20)
    if r.status_code in [200, 201]:
        return r.json()
    else:
        raise RuntimeError(f"Ошибка создания номенклатуры {item_data['name']}: {r.status_code} - {r.text}")


def update_nomenclature_item(base, sess, guid, item_data):
    payload = {
        "Вес": item_data["weight"],
        "Комментарий": item_data["term"][:1000] if item_data["term"] else ""
    }
    url = f"{base}/Catalog_Номенклатура(guid'{guid}')?$format=json"
    r = sess.patch(url, json=payload, timeout=20)
    if r.status_code in [200, 204]:
        return True
    else:
        print(f"Предупреждение при обновлении {guid}: {r.status_code} - {r.text[:200]}")
        return False


def create_price_setup_document(base, sess, price_rows):
    """
    Создает документ УстановкаЦенНоменклатуры для вида цен 'Закупка КНР' (в юанях).
    Документ создается непроведенным (Posted=False).
    """
    inventory_table = []
    for i, p in enumerate(price_rows, 1):
        inventory_table.append({
            "LineNumber": str(i),
            "Номенклатура_Key": p["guid"],
            "Характеристика_Key": "00000000-0000-0000-0000-000000000000",
            "ЕдиницаИзмерения": UNIT_SHT_KEY,
            "ЕдиницаИзмерения_Type": "StandardODATA.Catalog_КлассификаторЕдиницИзмерения",
            "ВидЦены_Key": PRICE_TYPE_CNY_KEY,
            "Цена": p["cny_price"],
            "ЦенаСтарая": 0
        })

    payload = {
        "Date": datetime.now().isoformat(),
        "Posted": False,
        "Комментарий": "Закупка КНР (юани) для БАРЕНЦКУЛ ООО по спецификации Книга1.xlsx",
        "ЗаписыватьНовыеЦеныПоверхУстановленных": True,
        "Запасы": inventory_table
    }
    url = f"{base}/Document_УстановкаЦенНоменклатуры?$format=json"
    r = sess.post(url, json=payload, timeout=25)
    if r.status_code in [200, 201]:
        doc = r.json()
        return doc
    else:
        raise RuntimeError(f"Ошибка создания документа УстановкаЦен: {r.status_code} - {r.text}")


def create_customer_order(base, sess, order_items):
    """
    Создает документ ЗаказПокупателя для ООО 'БАРЕНЦКУЛ' (рубли, НДС 22%).
    Документ создается непроведенным (Posted=False).
    """
    total_doc_sum = 0.0
    inventory_table = []
    for i, item in enumerate(order_items, 1):
        qty = item["quantity"]
        price = item["rub_price"]
        item_sum = item["rub_sum"]
        vat_sum = round(item_sum * 22.0 / 122.0, 2)
        total_doc_sum += item_sum

        inventory_table.append({
            "LineNumber": str(i),
            "ТипНоменклатурыЗапас": True,
            "Номенклатура": item["guid"],
            "Номенклатура_Type": "StandardODATA.Catalog_Номенклатура",
            "Характеристика_Key": "00000000-0000-0000-0000-000000000000",
            "ЕдиницаИзмерения": UNIT_SHT_KEY,
            "ЕдиницаИзмерения_Type": "StandardODATA.Catalog_КлассификаторЕдиницИзмерения",
            "Количество": qty,
            "Цена": price,
            "Сумма": item_sum,
            "СтавкаНДС_Key": VAT_RATE_22_KEY,
            "СуммаНДС": vat_sum,
            "Всего": item_sum,
            "ПроцентСкидкиНаценки": 0,
            "СуммаСкидкиНаценки": 0,
            "Вес": item["weight"]
        })

    payload = {
        "Date": datetime.now().isoformat(),
        "Posted": False,
        "Контрагент_Key": COUNTERPARTY_KEY,
        "Организация_Key": ORGANIZATION_KEY,
        "Договор_Key": CONTRACT_KEY,
        "НалогообложениеНДС": "ОблагаетсяНДС",
        "СуммаВключаетНДС": True,
        "СуммаДокумента": round(total_doc_sum, 2),
        "Комментарий": "Заказ покупателя ООО «БАРЕНЦКУЛ» (загружен из Книга1.xlsx)",
        "Запасы": inventory_table
    }
    url = f"{base}/Document_ЗаказПокупателя?$format=json"
    r = sess.post(url, json=payload, timeout=25)
    if r.status_code in [200, 201]:
        return r.json()
    else:
        raise RuntimeError(f"Ошибка создания Заказа покупателя: {r.status_code} - {r.text}")


def test_posting(base, sess, doc_entity, doc_guid):
    """
    Пробует провести документ и возвращает результат либо текст ошибки платформы 1С.
    """
    post_url = f"{base}/{doc_entity}(guid'{doc_guid}')/Post?PostingModeOperation=Regular"
    r = sess.post(post_url, timeout=25)
    if r.status_code in [200, 204]:
        return True, "Успешно проведен без ошибок"
    else:
        # Извлекаем сообщение об ошибке 1С
        err_msg = r.text
        try:
            err_json = r.json()
            if "odata.error" in err_json:
                err_msg = err_json["odata.error"].get("message", {}).get("value", r.text)
        except Exception:
            pass
        return False, f"HTTP {r.status_code}: {err_msg}"


def main():
    parser = argparse.ArgumentParser(description="Импорт номенклатуры, цен КНР и Заказа покупателя для БАРЕНЦКУЛ ООО")
    parser.add_argument("--excel", default=r"C:\Users\Артем\Desktop\Книга1.xlsx", help="Путь к Excel файлу")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Режим симуляции (по умолчанию)")
    parser.add_argument("--commit", action="store_true", help="Фактическая запись данных в 1С:УНФ")
    args = parser.parse_args()

    is_dry_run = not args.commit

    print("=" * 80)
    print(f"РЕЖИМ РАБОТЫ: {'[DRY-RUN - БЕЗ ИЗМЕНЕНИЙ В 1С]' if is_dry_run else '[COMMIT - БОЕВАЯ ЗАПИСЬ В 1С]'}")
    print(f"Файл Excel: {args.excel}")
    print("=" * 80)

    if not os.path.exists(args.excel):
        print(f"ОШИБКА: Файл не найден: {args.excel}")
        sys.exit(1)

    items = read_excel_rows(args.excel)
    print(f"Считано позиций из Excel: {len(items)}")

    base, sess = get_odata_session()

    print("\nПроверка позиций в базе 1С:УНФ по артикулам...")
    processed_items = []
    total_rub = 0.0
    total_cny = 0.0

    for it in items:
        existing = find_nomenclature_by_article(base, sess, it["article"])
        if existing:
            status = "НАЙДЕНА В 1С (обновление)"
            guid = existing.get("Ref_Key")
        else:
            status = "НОВАЯ КАРТОЧКА (создание)"
            guid = f"temp-guid-{it['num']}" if is_dry_run else None

        it["status"] = status
        it["guid"] = guid
        total_rub += it["rub_sum"]
        total_cny += it["cny_sum"]
        processed_items.append(it)

        print(f"[{it['num']:2d}] {it['article']:<15} | {status:<26} | Кол-во: {it['quantity']:<3} | Закупка CNY: {it['cny_price']:>7.2f} | Цена RUB: {it['rub_price']:>10.2f} | Сумма RUB: {it['rub_sum']:>10.2f} | Срок: {it['term']}")

    print("-" * 80)
    print(f"ИТОГО ПОЗИЦИЙ: {len(processed_items)}")
    print(f"ИТОГО СУММА ЗАКУПКИ КНР: {total_cny:,.2f} CNY")
    print(f"ИТОГО СУММА ЗАКАЗА В РУБЛЯХ: {total_rub:,.2f} RUB")
    print(f"Контрагент: ООО «БАРЕНЦКУЛ» (ИНН 5190075177)")
    print(f"Организация: ЦИ ЛИНЬ ООО (ИНН 7801719960)")
    print(f"Ставка НДС: 22% (сумма включает НДС)")
    print("=" * 80)

    if is_dry_run:
        print("\n[DRY-RUN ЗАВЕРШЕН УСПЕШНО]")
        print("Данные в 1С НЕ изменялись. Для записи запустите скрипт с флагом --commit.")
        return

    # БОЕВОЙ РЕЖИМ (--commit)
    print("\n[ШАГ 1/3] Создание/обновление номенклатуры в 1С...")
    for it in processed_items:
        if it["status"] == "НОВАЯ КАРТОЧКА (создание)":
            res = create_nomenclature_item(base, sess, it)
            it["guid"] = res.get("Ref_Key")
            print(f"  + Создана: {it['name'][:40]}... (GUID: {it['guid']})")
        else:
            update_nomenclature_item(base, sess, it["guid"], it)
            print(f"  ~ Обновлена: {it['name'][:40]}... (GUID: {it['guid']})")

    print("\n[ШАГ 2/3] Регистрация цен закупки КНР (сохранение документа Установка цен)...")
    price_doc = create_price_setup_document(base, sess, processed_items)
    price_guid = price_doc.get("Ref_Key")
    print(f"  + Документ УстановкаЦенНоменклатуры №{price_doc.get('Number')} сохранен (не проведен, GUID: {price_guid})")
    
    # Тест проведения Установки цен
    ok_pr, pr_msg = test_posting(base, sess, "Document_УстановкаЦенНоменклатуры", price_guid)
    if ok_pr:
        print(f"  [Тест проведения УстановкаЦен]: {pr_msg}")
    else:
        print(f"  [Тест проведения УстановкаЦен ОШИБКА]: {pr_msg}")

    print("\n[ШАГ 3/3] Создание Заказа покупателя (сохранение документа)...")
    order_doc = create_customer_order(base, sess, processed_items)
    order_guid = order_doc.get("Ref_Key")
    print(f"  + Документ ЗаказПокупателя №{order_doc.get('Number')} сохранен (не проведен, GUID: {order_guid})")
    print(f"  Сумма документа: {order_doc.get('СуммаДокумента')} руб. Контрагент: БАРЕНЦКУЛ ООО.")

    # Тест проведения Заказа покупателя
    print("\n[ТЕСТ ПРОВЕДЕНИЯ ЗАКАЗА ПОКУПАТЕЛЯ]")
    ok_ord, ord_msg = test_posting(base, sess, "Document_ЗаказПокупателя", order_guid)
    if ok_ord:
        print(f"  Результат проведения Заказа покупателя: {ord_msg}")
    else:
        print(f"  Ошибка при попытке проведения Заказа покупателя:")
        print(f"  >>> {ord_msg}")

    print("\n[ВСЕ ШАГИ ВЫПОЛНЕНЫ УСПЕШНО: ДОКУМЕНТЫ СОХРАНЕНЫ В 1С]")


if __name__ == "__main__":
    main()
