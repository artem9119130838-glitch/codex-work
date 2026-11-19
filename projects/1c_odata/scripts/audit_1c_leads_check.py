import os
import sys
import requests

sys.path.insert(0, os.path.abspath(r"C:\Codex\projects\1c_odata\scripts"))
from process_b24_inbound_leads import ONEC_BASE, ONEC_AUTH_READ

targets = [
    {'label': 'Лид 19236: ООО «АРТ КОМПЛЕКТ»', 'name': 'АРТ КОМПЛЕКТ', 'inn': '', 'email': 'artcomplect2017@gmail.com', 'phone': '9253003205'},
    {'label': 'Лид 19222: ООО «СТРОЙКОМПЛЕКС 78»', 'name': 'СТРОЙКОМПЛЕКС 78', 'inn': '7805821570', 'email': 'snab@stroykompleks78.ru', 'phone': '9810482505'},
    {'label': 'Лид 19216: Валерий Талипов (ООО «Логика»)', 'name': 'Логика', 'inn': '', 'email': 'tvs@logika.online', 'phone': '9920099462'},
    {'label': 'Лид 19214: ООО «Единая Служба Снабжения»', 'name': 'Единая Служба Снабжения', 'inn': '6670441379', 'email': 'manager8@ess-ural.ru', 'phone': '3432885165'},
    {'label': 'Лид 19130: АО «ПЗ «Машиностроитель»', 'name': 'Машиностроитель', 'inn': '5906075029', 'email': 'nyu-maksimova@pzmash.perm.ru', 'phone': '3422626899'}
]

print("=== ДЕТАЛЬНАЯ СВЕРКА С 1С:УНФ ===")
for t in targets:
    print(f"\n---> {t['label']}")
    # 1. Поиск в Catalog_Контрагенты
    cp_found = []
    if t['inn']:
        try:
            r = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter=ИНН eq '{t['inn']}'&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                cp_found = r.json().get('value', [])
        except Exception as e:
            print(f"  Ошибка 1С Контрагенты: {e}")

    # 2. Поиск в Catalog_Лиды
    ld_found = []
    if t['inn']:
        try:
            r = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter=ИНН eq '{t['inn']}'&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r.status_code == 200:
                ld_found = r.json().get('value', [])
        except Exception as e:
            print(f"  Ошибка 1С Лиды: {e}")

    # 3. Поиск по наименованию (если ИНН нет)
    if not cp_found and not ld_found and t['name']:
        try:
            r_n = requests.get(f"{ONEC_BASE}/Catalog_Контрагенты?$filter=substringof('{t['name']}', Description) eq true&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r_n.status_code == 200:
                cp_found = r_n.json().get('value', [])
            r_nl = requests.get(f"{ONEC_BASE}/Catalog_Лиды?$filter=substringof('{t['name']}', Description) eq true&$format=json", auth=ONEC_AUTH_READ, timeout=10)
            if r_nl.status_code == 200:
                ld_found = r_nl.json().get('value', [])
        except Exception as e:
            pass

    if cp_found:
        for c in cp_found:
            ci = c.get('КонтактнаяИнформация', [])
            phones = [x.get('Представление') for x in ci if 'телефон' in x.get('Тип', '').lower() or 'phone' in str(x).lower()]
            emails = [x.get('Представление') or x.get('АдресЭП') for x in ci if 'электрон' in x.get('Тип', '').lower() or 'email' in str(x).lower()]
            addrs = [x.get('Представление') for x in ci if 'адрес' in x.get('Тип', '').lower()]
            print(f"  [1С Контрагент] '{c.get('Description')}' (Код: {c.get('Code')}, ИНН: {c.get('ИНН')})")
            print(f"    - Адреса: {addrs}")
            print(f"    - Телефоны: {phones}")
            print(f"    - Email: {emails}")
    else:
        print("  [1С Контрагент] НЕ НАЙДЕН")

    if ld_found:
        for l in ld_found:
            ci = l.get('КонтактнаяИнформация', [])
            phones = [x.get('Представление') for x in ci if 'телефон' in x.get('Тип', '').lower() or 'phone' in str(x).lower()]
            emails = [x.get('Представление') or x.get('АдресЭП') for x in ci if 'электрон' in x.get('Тип', '').lower() or 'email' in str(x).lower()]
            addrs = [x.get('Представление') for x in ci if 'адрес' in x.get('Тип', '').lower()]
            print(f"  [1С Лид] '{l.get('Description')}' (Код: {l.get('Code')}, ИНН: {l.get('ИНН')})")
            print(f"    - Адреса: {addrs}")
            print(f"    - Телефоны: {phones}")
            print(f"    - Email: {emails}")
    else:
        print("  [1С Лид] НЕ НАЙДЕН")
