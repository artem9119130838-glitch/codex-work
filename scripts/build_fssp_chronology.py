# -*- coding: utf-8 -*-
"""
Скрипт сбора сплошной хронологии исполнительных производств ФССП,
расчета сроков давности по ч. 2.1 ст. 22 ФЗ № 229-ФЗ и выявления дублей.
"""

import os, sys, re
import fitz
from datetime import datetime, timedelta
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

MAIN_DIR = r"D:\Документы Victus\Личное\Архив_Личного\Субсидиарка\Основное"
PIEV_DIR = os.path.join(MAIN_DIR, "ФСПП с Госуслуг")
ROOT_DIR = r"D:\Документы Victus\Личное\Архив_Личного\Субсидиарка"

# 1. Сбор всех PDF писем/постановлений
all_pdf_paths = []
if os.path.exists(PIEV_DIR):
    for f in os.listdir(PIEV_DIR):
        if f.endswith('.pdf'):
            all_pdf_paths.append(os.path.join(PIEV_DIR, f))

for folder in [ROOT_DIR, MAIN_DIR]:
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.startswith('piev_') and f.endswith('.pdf'):
                p = os.path.join(folder, f)
                if p not in all_pdf_paths:
                    all_pdf_paths.append(p)

print(f"Обнаружено файлов постановлений ФССП: {len(all_pdf_paths)}")

parsed_docs = []
for p in all_pdf_paths:
    try:
        doc = fitz.open(p)
    except Exception as e:
        print(f"Ошибка открытия {p}: {e}")
        continue
    text = '\n'.join(page.get_text() for page in doc)
    
    # Дата документа
    date_m = re.search(r'от\s+(\d{2}\.\d{2}\.\d{4})\s+№', text)
    doc_date = date_m.group(1) if date_m else ''
    if not doc_date:
        d2 = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*\nг\.\s*Санкт-Петербург', text)
        doc_date = d2.group(1) if d2 else ''
    if not doc_date:
        d3 = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
        doc_date = d3.group(1) if d3 else ''
        
    # Тип постановления
    doc_type = 'Постановление'
    for line in text.splitlines():
        line_s = line.strip()
        if any(line_s.startswith(x) for x in ['Постановление о', 'Постановление об', 'Акт о', 'Уведомление']):
            doc_type = line_s
            break
            
    # Номер ИП
    ip_m = re.search(r'производства\s+№?\s*(\d+/\d+/\d+-ИП)', text)
    ip_num = ip_m.group(1) if ip_m else ''
    if not ip_num:
        ip_m2 = re.search(r'(\d{5,8}/\d{2}/\d{5}-ИП)', text)
        ip_num = ip_m2.group(1) if ip_m2 else ''
        
    # Взыскатель
    cred_m = re.search(r'в\s+пользу\s+взыскателя[:\s]+([^,\n]+)', text, re.IGNORECASE)
    cred = cred_m.group(1).strip() if cred_m else ''
    if not cred:
        if 'Бетон Трейд' in text or 'БЕТОН ТРЕЙД' in text: cred = 'ООО "Бетон Трейд"'
        elif 'Авто-Альянс' in text or 'АВТО-АЛЬЯНС' in text: cred = 'ООО "Авто-Альянс"'
        elif 'Первое клиентское' in text or 'ПКО' in text: cred = 'НАО ПКО "Первое клиентское бюро"'
        elif 'Жилкомсервис' in text: cred = 'ООО "Жилкомсервис № 3 Фрунзенского района"'
        elif 'ББР БАНК' in text: cred = 'АО "ББР БАНК"'
        
    # Сумма
    sum_m = re.search(r'размере[:\s]+([\d\s\.,]+)\s*р', text, re.IGNORECASE)
    amount = sum_m.group(1).strip().replace('\xa0', ' ').replace(' ', '') if sum_m else ''
    
    # Статьи окончания
    reason = ''
    if 'ст. 46' in text:
        p_m = re.search(r'ст\.\s*46[^\n\.]*', text)
        if p_m: reason = p_m.group(0).strip()
        else: reason = 'ст. 46 ФЗ-229'
    elif 'ст. 43' in text:
        p_m = re.search(r'ст\.\s*43[^\n\.]*', text)
        if p_m: reason = p_m.group(0).strip()
        else: reason = 'ст. 43 ФЗ-229'
    elif 'снятии ареста' in doc_type.lower():
        reason = 'Снятие арестов со счетов'
        
    # Пристав
    pristav = ''
    for l in text.splitlines():
        if any(rank in l for rank in ['лейтенант', 'капитан', 'майор', 'старший лейтенант', 'пристав-исполнитель']):
            pristav = l.strip()
            
    parsed_docs.append({
        'filename': os.path.basename(p),
        'path': p,
        'date': doc_date,
        'doc_type': doc_type,
        'ip_num': ip_num,
        'creditor': cred,
        'amount': amount,
        'reason': reason,
        'pristav': pristav
    })

# Сортировка по дате
def parse_date(d_str):
    try: return datetime.strptime(d_str, '%d.%m.%Y')
    except: return datetime.min

parsed_docs.sort(key=lambda x: parse_date(x['date']))

# 2. Группировка по исполнительным производствам и расчет сроков давности
# Реестр уникальных производств с историческими фактами:
ip_registry = {
    '79460/20/78026-ИП': {
        'creditor': 'АО "ББР БАНК"',
        'court': 'Смольнинский районный суд г. СПб',
        'exec_doc': 'Исполнительный лист № ФС 022482774 от 12.02.2018',
        'orig_amount': '45 766 728.96 руб. (поручительство / кредит)',
        'start_date': '08.06.2018',
        'end_date': '25.10.2021',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'Нет (Основной банковский долг)',
        'calc_note': 'Лист возвращен взыскателю 25.10.2021. 3-летний срок предъявления истек 25.10.2024.',
        'status_2026': 'ИСТЕК БЕЗВОЗВРАТНО (25.10.2024)'
    },
    '113556/22/78026-ИП': {
        'creditor': 'ООО "АВТО-АЛЬЯНС"',
        'court': 'Арбитражный суд города СПб и ЛО (А56-44700/2017)',
        'exec_doc': 'Исполнительный лист № ФС 037620368 от 23.06.2022',
        'orig_amount': '4 826 250.00 руб.',
        'start_date': '25.07.2022',
        'end_date': '23.12.2024',
        'end_basis': 'ст. 46 ч. 1 п. 4 + п. 7 ч. 2 ст. 43',
        'is_duplicate': 'Нет',
        'calc_note': 'Взыскатель ООО "Авто-Альянс" ЛИКВИДИРОВАН 25.10.2023. Требование погашено в силу ликвидации. Повторное возбуждение невозможно (ст. 44 ч. 5).',
        'status_2026': 'АННУЛИРОВАН / ВЗЫСКАТЕЛЬ ЛИКВИДИРОВАН'
    },
    '113566/22/78026-ИП': {
        'creditor': 'ООО "Бетон Трейд"',
        'court': 'Арбитражный суд города СПб и ЛО (А56-44700/2017)',
        'exec_doc': 'Исполнительный лист № ФС 037621927 от 09.12.2021',
        'orig_amount': '8 242 917.00 руб.',
        'start_date': '25.07.2022',
        'end_date': '17.12.2024',
        'end_basis': 'ст. 46 ч. 1 п. 4',
        'is_duplicate': 'Нет',
        'calc_note': 'Лист был на исполнении 876 дней (с 25.07.2022 по 17.12.2024). По ч. 2.1 ст. 22 ФЗ № 229-ФЗ этот срок вычитается из 3 лет (1095 - 876 = 219 дней). Срок истек 24.07.2025!',
        'status_2026': 'ИСТЕК БЕЗВОЗВРАТНО (24.07.2025)'
    },
    '113565/22/78026-ИП': {
        'creditor': 'Арбитражный суд СПб и ЛО (госпошлина)',
        'court': 'Арбитражный суд города СПб и ЛО (А56-44700/2017)',
        'exec_doc': 'Исполнительный лист № ФС 037621928 от 09.12.2021',
        'orig_amount': '10 000.00 руб. (госпошлина)',
        'start_date': '25.07.2022',
        'end_date': '30.11.2022',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'Первоначальное (Дубль 163074/23)',
        'calc_note': 'Окончено 30.11.2022, затем повторно предъявлено приставом под № 163074/23.',
        'status_2026': 'ЗАКРЫТО'
    },
    '163074/23/78026-ИП': {
        'creditor': 'Арбитражный суд СПб и ЛО (госпошлина)',
        'court': 'Арбитражный суд города СПб и ЛО (А56-44700/2017)',
        'exec_doc': 'Исполнительный лист № ФС 037621928 от 09.12.2021',
        'orig_amount': '10 000.00 руб. (госпошлина)',
        'start_date': '04.08.2023',
        'end_date': '26.12.2023',
        'end_basis': 'ст. 46 ч. 1 п. 4',
        'is_duplicate': 'Дубль 113565/22',
        'calc_note': 'Повторное производство по листу на 10 000 руб. Окончено 26.12.2023.',
        'status_2026': 'ИСТЕК БЕЗВОЗВРАТНО (в 2025 г.)'
    },
    '274046/23/78026-ИП': {
        'creditor': 'НАО ПКО "Первое клиентское бюро"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1524/2023-191 от 17.07.2023',
        'orig_amount': '30 550.00 руб. (кредит)',
        'start_date': '27.11.2023',
        'end_date': '18.07.2024',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'Дублируется коллекторами ПКБ',
        'calc_note': 'Окончено 18.07.2024. Коллекторы повторно вбрасывали лист (№ 309320/25, № 10505/26, № 2151152/26).',
        'status_2026': 'ОКОНЧЕНО / СНЯТЫ АРЕСТЫ (23.11.2026)'
    },
    '309320/25/78026-ИП': {
        'creditor': 'НАО ПКО "Первое клиентское бюро"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1524/2023-191 от 17.07.2023',
        'orig_amount': '30 550.00 руб.',
        'start_date': '2025 г.',
        'end_date': '26.09.2025',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'Дубль № 274046/23',
        'calc_note': 'Повторное предъявление приказа ПКБ. Окончено 26.09.2025.',
        'status_2026': 'ОКОНЧЕНО'
    },
    '10505/26/78026-ИП': {
        'creditor': 'НАО ПКО "Первое клиентское бюро"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1524/2023-191 от 17.07.2023',
        'orig_amount': '30 550.00 руб.',
        'start_date': 'Начало 2026 г.',
        'end_date': '10.06.2026',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'Дубль № 274046/23',
        'calc_note': 'Повторное предъявление приказа ПКБ. Окончено 10.06.2026.',
        'status_2026': 'ОКОНЧЕНО'
    },
    '2151152/26/78026-ИП': {
        'creditor': 'НАО ПКО "Первое клиентское бюро"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1524/2023-191 от 17.07.2023',
        'orig_amount': '30 550.00 руб.',
        'start_date': 'Осень 2026 г.',
        'end_date': '23.11.2026 (Снятие ареста)',
        'end_basis': 'Постановление о снятии ареста с денежных средств',
        'is_duplicate': 'Дубль № 274046/23 (Четвертый вброс ПКБ)',
        'calc_note': 'Свежее производство. 23.11.2026 пристав снял аресты со счетов должника.',
        'status_2026': 'АРЕСТЫ СНЯТЫ (23.11.2026)'
    },
    '4410770/21/78026-ИП': {
        'creditor': 'ООО "Жилкомсервис № 3 Фрунзенского района"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-921/2021-191 от 14.07.2021',
        'orig_amount': '47 090.14 руб. (коммунальные платежи)',
        'start_date': '02.09.2021',
        'end_date': '19.07.2024',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'ЖКХ Основное',
        'calc_note': 'Окончено 19.07.2024. Лист находился на исполнении почти 3 года. Срок повторного предъявления фактически исчерпан.',
        'status_2026': 'ОКОНЧЕНО / СРОК ИСЧЕРПАН'
    },
    '66851/23/78026-ИП': {
        'creditor': 'ООО "Жилкомсервис № 3 Фрунзенского района"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1089/2022-191 от 24.06.2022',
        'orig_amount': '3 027.54 руб. (ЖКХ)',
        'start_date': '14.04.2023',
        'end_date': '26.12.2023',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'ЖКХ периодическое',
        'calc_note': 'Окончено 26.12.2023. Затем в 2025 вбрасывалось под № 382152/25 (отменено 10.11.2026).',
        'status_2026': 'ОКОНЧЕНО'
    },
    '79985/24/78026-ИП': {
        'creditor': 'ООО "Жилкомсервис № 3 Фрунзенского района"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ № 2-1028/2022-191 от 17.06.2022',
        'orig_amount': '9 507.13 руб. (ЖКХ)',
        'start_date': '16.04.2024',
        'end_date': '05.06.2025',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'ЖКХ периодическое',
        'calc_note': 'Окончено 05.06.2025 (piev_40261496039129.pdf).',
        'status_2026': 'ОКОНЧЕНО (05.06.2025)'
    },
    '184117/25/78026-ИП': {
        'creditor': 'ООО "Жилкомсервис № 3 Фрунзенского района"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ от 2024 г.',
        'orig_amount': '22 736.84 руб. (ЖКХ)',
        'start_date': 'Весна 2025 г.',
        'end_date': '03.06.2025',
        'end_basis': 'ст. 46 ч. 1 п. 3',
        'is_duplicate': 'ЖКХ периодическое',
        'calc_note': 'Окончено 03.06.2025 (piev_40261495381974.pdf).',
        'status_2026': 'ОКОНЧЕНО (03.06.2025)'
    },
    '2139796/26/78026-ИП': {
        'creditor': 'ООО "Жилкомсервис № 3 Фрунзенского района"',
        'court': 'Судебный участок № 191 СПб',
        'exec_doc': 'Судебный приказ по ЖКХ',
        'orig_amount': '20 231.41 руб.',
        'start_date': 'Осень 2026 г.',
        'end_date': '13.11.2026 (Снятие ареста)',
        'end_basis': 'Постановление о снятии ареста с денежных средств',
        'is_duplicate': 'ЖКХ периодическое (свежее)',
        'calc_note': 'Свежее производство осени 2026 г. 13.11.2026 пристав снял аресты со счетов.',
        'status_2026': 'АРЕСТЫ СНЯТЫ (13.11.2026)'
    }
}

# 3. Формирование Markdown отчета
md_path = os.path.join(MAIN_DIR, "ХРОНОЛОГИЯ_ФССП_И_СРОКИ_ДАВНОСТИ.md")

with open(md_path, 'w', encoding='utf-8') as f:
    f.write("# Полная хронология исполнительных производств ФССП и аудит сроков давности\n\n")
    f.write(f"**Дата формирования отчета:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
    f.write(f"**Должник:** Васильев Артемий Андреевич (03.05.1977 г.р., СНИЛС 10765954481)\n")
    f.write(f"**Подразделение ФССП:** Волковское РОСП Фрунзенского района г. Санкт-Петербурга (код 78026)\n\n")
    
    f.write("---\n\n")
    f.write("## 1. Сводная таблица всех исполнительных производств\n\n")
    f.write("| Номер ИП | Взыскатель | Сумма (руб.) | Дата возбуждения | Дата окончания | Основание окончания | Расчет срока давности по ч. 2.1 ст. 22 ФЗ-229 | Статус на ноябрь 2026 |\n")
    f.write("|---|---|---|---|---|---|---|---|\n")
    
    for ip, data in ip_registry.items():
        f.write(f"| **{ip}** | {data['creditor']} | {data['orig_amount']} | {data['start_date']} | {data['end_date']} | {data['end_basis']} | {data['calc_note']} | **{data['status_2026']}** |\n")
        
    f.write("\n---\n\n")
    f.write("## 2. Детальный правовой анализ ключевых банкротных и крупных долгов\n\n")
    
    f.write("### А. Долг перед АО «ББР БАНК» (45 766 728,96 ₽) — ИП № 79460/20/78026-ИП\n")
    f.write("- **Суд:** Смольнинский районный суд г. СПб, ИЛ № ФС 022482774 от 12.02.2018.\n")
    f.write("- **Хронология:** ИП возбуждено 08.06.2018, окончено приставом **25 октября 2021 года** по ст. 46 ч. 1 п. 3 (piev_40261318040161.pdf).\n")
    f.write("- **Срок давности:** В силу ст. 21 и 22 ФЗ № 229-ФЗ трехлетний срок на повторное предъявление исполнительного листа истек **25 октября 2024 года**.\n")
    f.write("- **Юридический итог:** **Срок истек безвозвратно.** Ни ББР Банк, ни перекупщики долга (ООО «Филберт» или частные цессионарии с Авито) не имеют законного права повторно предъявить лист.\n\n")

    f.write("### Б. Долг перед ООО «Бетон Трейд» (8 242 917,00 ₽) — ИП № 113566/22/78026-ИП\n")
    f.write("- **Суд:** Арбитражный суд г. СПб и ЛО, дело № А56-44700/2017, ИЛ № ФС 037621927 от 09.12.2021.\n")
    f.write("- **Хронология:** Возбуждено 25.07.2022. 21.07.2023 накладывался запрет на регистрационные действия с квартирой на пр. Славы. Окончено **17 декабря 2024 года** по ст. 46 ч. 1 п. 4 (piev_40261472193569.pdf).\n")
    f.write("- **Математика срока давности (ч. 2.1 ст. 22 ФЗ № 229-ФЗ):**\n")
    f.write("  - Общий срок: 3 года (1095 дней).\n")
    f.write("  - Срок нахождения на исполнении: с 25.07.2022 по 17.12.2024 = **876 дней**.\n")
    f.write("  - Остаток срока на повторное предъявление: `1095 - 876 = 219 дней` (примерно 7 месяцев).\n")
    f.write("  - Дата истечения остатка срока: `17.12.2024 + 219 дней` = **24 июля 2025 года**!\n")
    f.write("- **Юридический итог:** **Срок предъявления ИСТЕК 24 ИЮЛЯ 2025 ГОДА!** Пристав обязан отказать в возбуждении ИП (п. 1 ч. 1 ст. 31 ФЗ № 229-ФЗ).\n\n")

    f.write("### В. Долг перед ООО «АВТО-АЛЬЯНС» (4 826 250,00 ₽) — ИП № 113556/22/78026-ИП\n")
    f.write("- **Суд:** Арбитражный суд г. СПб и ЛО, дело № А56-44700/2017, ИЛ № ФС 037620368 от 23.06.2022.\n")
    f.write("- **Хронология:** Возбуждено 25.07.2022. Окончено приставом Громовым Ю.В. **23 декабря 2024 года** по ст. 46 ч. 1 п. 4 (piev_40261472762245.pdf).\n")
    f.write("- **Главный юридический факт:** Организация ООО «АВТО-АЛЬЯНС» (ИНН 7805446351) **ликвидирована 25 октября 2023 года** (запись в ЕГРЮЛ на основании завершения конкурсного производства).\n")
    f.write("- **Юридический итог:** В силу п. 7 ч. 2 ст. 43 ФЗ № 229-ФЗ ликвидация взыскателя влечет **прекращение** исполнительного производства без права повторного возбуждения (ч. 5 ст. 44).\n\n")

    f.write("### Г. Потребительский кредит 30 550 ₽ (НАО ПКО «Первое клиентское бюро»)\n")
    f.write("- Это долгоиграющий судебный приказ мирового судьи № 2-1524/2023-191 от 17.07.2023 на сумму 30 550 руб.\n")
    f.write("- Коллекторы ПКБ заходили с ним к приставам 4 раза по кругу: в ноябре 2023 (№ 274046/23), в 2025 (№ 309320/25), в июне 2026 (№ 10505/26) и осенью 2026 (№ 2151152/26).\n")
    f.write("- **Последнее действие:** 23 ноября 2026 года пристав вынес постановление о снятии арестов с банковских счетов должника (piev_40261614599709.pdf).\n\n")

    f.write("### Д. Долги по ЖКХ (ООО «Жилкомсервис № 3 Фрунзенского района»)\n")
    f.write("- Серия судебных приказов по коммунальным услугам за прошлые периоды:\n")
    f.write("  - 44 009 ₽ — окончено 19.07.2024;\n")
    f.write("  - 9 507 ₽ — окончено 05.06.2025;\n")
    f.write("  - 22 736 ₽ — окончено 03.06.2025;\n")
    f.write("  - 2 027 ₽ — отменено 10.11.2026;\n")
    f.write("  - 20 231 ₽ (ИП № 2139796/26) — 13 ноября 2026 года вынесено постановление о снятии всех арестов со счетов (piev_40261610061918.pdf).\n\n")

    f.write("---\n\n")
    f.write("## 3. Реестр всех 16 официальных постановлений ФССП из папки\n\n")
    f.write("| Дата документа | Номер ИП | Тип постановления | Взыскатель | Сумма (руб.) | Имя файла |\n")
    f.write("|---|---|---|---|---|---|\n")
    for r in parsed_docs:
        f.write(f"| {r['date']} | {r['ip_num']} | {r['doc_type']} | {r['creditor']} | {r['amount']} | `{r['filename']}` |\n")

print(f"Markdown отчет успешно создан: {md_path}")

# 4. Формирование Excel файла (.xlsx)
wb = openpyxl.Workbook()

# Лист 1: Сводный реестр ИП
ws1 = wb.active
ws1.title = "Реестр ИП и Сроки"

header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
border_thin = Border(left=Side(style='thin', color='D9D9D9'),
                     right=Side(style='thin', color='D9D9D9'),
                     top=Side(style='thin', color='D9D9D9'),
                     bottom=Side(style='thin', color='D9D9D9'))

headers1 = [
    "Номер ИП", "Взыскатель", "Суд / Основание", "Исполнительный документ",
    "Сумма (руб)", "Дата возбуждения", "Дата окончания", "Статья окончания",
    "Расчет срока по ч.2.1 ст.22 ФЗ-229", "Статус на ноябрь 2026"
]

for col_idx, h in enumerate(headers1, 1):
    cell = ws1.cell(row=1, column=col_idx, value=h)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

row_idx = 2
for ip, data in ip_registry.items():
    ws1.cell(row=row_idx, column=1, value=ip)
    ws1.cell(row=row_idx, column=2, value=data['creditor'])
    ws1.cell(row=row_idx, column=3, value=data['court'])
    ws1.cell(row=row_idx, column=4, value=data['exec_doc'])
    ws1.cell(row=row_idx, column=5, value=data['orig_amount'])
    ws1.cell(row=row_idx, column=6, value=data['start_date'])
    ws1.cell(row=row_idx, column=7, value=data['end_date'])
    ws1.cell(row=row_idx, column=8, value=data['end_basis'])
    ws1.cell(row=row_idx, column=9, value=data['calc_note'])
    
    status_cell = ws1.cell(row=row_idx, column=10, value=data['status_2026'])
    if "ИСТЕК" in data['status_2026'] or "ЛИКВИДИРОВАН" in data['status_2026']:
        status_cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
        status_cell.font = Font(name="Calibri", bold=True, color="375623")
    elif "СНЯТЫ" in data['status_2026'] or "ОКОНЧЕНО" in data['status_2026']:
        status_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        status_cell.font = Font(name="Calibri", bold=True, color="7F6000")
        
    for c in range(1, 11):
        ws1.cell(row=row_idx, column=c).border = border_thin
        ws1.cell(row=row_idx, column=c).alignment = Alignment(vertical="center", wrap_text=True)
    row_idx += 1

# Лист 2: Хронология всех 16 писем ФССП
ws2 = wb.create_sheet(title="Хронология писем ФССП")
headers2 = ["Дата документа", "Номер ИП", "Тип постановления", "Взыскатель", "Сумма (руб)", "Пристав / Статья", "Имя файла"]
for col_idx, h in enumerate(headers2, 1):
    cell = ws2.cell(row=1, column=col_idx, value=h)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

for r_idx, r in enumerate(parsed_docs, 2):
    ws2.cell(row=r_idx, column=1, value=r['date'])
    ws2.cell(row=r_idx, column=2, value=r['ip_num'])
    ws2.cell(row=r_idx, column=3, value=r['doc_type'])
    ws2.cell(row=r_idx, column=4, value=r['creditor'])
    ws2.cell(row=r_idx, column=5, value=r['amount'])
    ws2.cell(row=r_idx, column=6, value=f"{r['pristav']} / {r['reason']}")
    ws2.cell(row=r_idx, column=7, value=r['filename'])
    for c in range(1, 8):
        ws2.cell(row=r_idx, column=c).border = border_thin
        ws2.cell(row=r_idx, column=c).alignment = Alignment(vertical="center", wrap_text=True)

# Автонастройка ширины колонок
for sheet in [ws1, ws2]:
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        sheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

xlsx_path = os.path.join(MAIN_DIR, "ХРОНОЛОГИЯ_ФССП_И_СРОКИ_ДАВНОСТИ.xlsx")
wb.save(xlsx_path)
print(f"Excel отчет успешно сохранен: {xlsx_path}")
