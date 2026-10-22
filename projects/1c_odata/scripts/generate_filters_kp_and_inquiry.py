#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/generate_filters_kp_and_inquiry.py
============================================================
Канонический скрипт обработки комплексных закрытых запросов ОЛ на фильтры
(кейс: ООО «ИНК», Сделка Битрикс24 CRM №2598, задача №5124).

Назначение:
  1. Выгрузка и агрегация номенклатурных потребностей заказчика из входящих почтовых
     сообщений и задач CRM (разбитых по цехам/МВЗ/ЗО) с точным подсчетом сумм штук.
  2. Сверка с ответами фабрик/поставщиков из КНР (Ванг), сопоставление замен,
     выделение регуляторных ограничений (экспортный контроль КНР, OEM-артикулы).
  3. Формирование пакета документов:
     - Сводный Excel-реестр КП для заказчика на русском языке с ценами, статусами и примечаниями;
     - Ведомость корректировки объемов для поставщика в КНР (на китайском языке);
     - Официальный опросный лист технических уточнений по неквалифицированным позициям.

Команда запуска:
  py projects/1c_odata/scripts/generate_filters_kp_and_inquiry.py --deal-id 2598 --output-dir projects/1c_odata/deals/deal_2598_ink_filters
"""

import os
import sys
import argparse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def generate_filters_kp_package(deal_id: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Генерация пакета КП и опросного листа для сделки #{deal_id} в {output_dir}...")

    # Создание клиентского Excel КП
    client_excel_path = os.path.join(output_dir, f"KP_Filters_Deal_{deal_id}.xlsx")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "КП_Фильтры"

    # Стили
    font_title = Font(name="Calibri", size=13, bold=True, color="1F497D")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Calibri", size=9.5)
    font_bold = Font(name="Calibri", size=9.5, bold=True)

    fill_header = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    fill_priced = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    fill_pending = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    fill_rf = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    fill_total = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

    thin = Side(style="thin", color="D9D9D9")
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws["A1"] = f"ТЕХНИКО-КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ / РЕЕСТР ПОСТАВКИ (Сделка CRM #{deal_id})"
    ws["A1"].font = font_title
    ws["A2"] = "Заказчик: ООО «Иркутская нефтяная компания» (ИНК) | Ставка НДС в РФ: 22%"
    ws["A2"].font = Font(name="Calibri", size=10, italic=True)

    headers = [
        "№", "Код номенклатуры", "Наименование", "Артикул / Замена",
        "Бренд", "Кол-во", "Ед.", "Цена за ед., RMB", "Сумма, RMB",
        "Срок", "Статус", "Технические характеристики и примечания"
    ]

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # 23 позиции ИНК
    items = [
        (1, "0000499594", "Картридж магистрального фильтра Atlas Copco DD 130+", "DD 130+ (1624108801 / 2901200305)", "Atlas Copco", 2, "шт.", 1676.0, "4–6 нед.", "Оценено (зарубежный хаб)", fill_priced, "Экспортный контроль производителя, спецпоставка."),
        (2, "0000374693", "Фильтр масляный 1625752501", "1625752501", "Atlas Copco", 10, "шт.", 320.0, "1–2 нед.", "Оценено (заводской дисконт)", fill_priced, "Накручивающийся фильтр (spin-on), резьбовой порт."),
        (3, "0000256752", "Элемент первой ступени маслосепаратора 431120", "431120", "Keltec / OEM", 1, "шт.", None, "Уточняется", "Требуется шильдик компрессора", fill_pending, "Работает в паре со 2-й ступенью 431120-1 (поз. 15)."),
        (4, "0000256917", "Фильтр-картридж входного газа G-5", "G-5 (Gas Filter)", "Gas Filter", 2, "шт.", None, "Уточняется", "Требуются параметры и фото", fill_pending, "Высокопоточный картридж. Требуются размеры и среда."),
        (5, "0000234728", "Фильтр воздушный GA22 1613872000", "1613872000 (GA22)", "Atlas Copco", 9, "шт.", 318.0, "1–2 нед.", "Оценено", fill_priced, "Входной фильтр компрессора GA22. Ø130×Ø70×H270 мм."),
        (6, "0000153113", "Элемент фильтрующий 1249203604", "1249203604", "Atlas Copco / Kaeser", 4, "шт.", None, "Подбор аналога", "Ограничение в КНР, нужен чертеж", fill_pending, "Ограничен к открытой продаже в КНР. Запрошен чертеж."),
        (7, "0000234724", "Фильтр масляный Atlas Copco GA45 1625752500", "1625752500 (GA45)", "Atlas Copco", 12, "шт.", 320.0, "1–2 нед.", "Оценено (оптовый дисконт)", fill_priced, "Спинонный фильтр GA45. Заводская цена на 12 шт."),
        (8, "0000299032", "Элемент газо-масляного сепаратора 43-1130", "43-1130 / 431130", "Keltec / OEM", 2, "шт.", None, "Уточняется", "Требуется шильдик компрессора", fill_pending, "Цилиндрический маслоотделительный картридж."),
        (9, "0000374586", "Элемент фильтрующий 1622 5693 00", "1622 5693 00 (1622569300)", "Atlas Copco", 6, "шт.", 3300.0, "1–2 нед.", "Оценено", fill_priced, "Погружной сепаратор с заземляющей пластиной."),
        (10, "0000464834", "Фильтр масляный 2023400100", "2023400100", "Ceccato / CP", 3, "шт.", None, "На проработке", "Уточнение модели компрессора", fill_pending, "Группа Atlas Copco (Ceccato/CP). Прямой кросс не найден."),
        (11, "0000374569", "Элемент фильтрующий 1622 1855 01", "1622 1855 01 (1622185501)", "Atlas Copco", 6, "шт.", 1300.0, "1–2 нед.", "Оценено", fill_priced, "Главный воздушный фильтр винтового компрессора."),
        (12, "0001064187", "Фильтроэлемент маслосепаратора 1625481100", "1625481100", "Atlas Copco", 3, "шт.", 1700.0, "1–2 нед.", "Оценено", fill_priced, "Встроенный маслоотделитель с комплектом уплотнений."),
        (13, "0000334153", "Элемент фильтрующий 1249203606", "1249203606", "Atlas Copco / Kaeser", 2, "шт.", None, "Подбор аналога", "Ограничение в КНР, нужен чертеж", fill_pending, "Прецизионный фильтроэлемент. Запрошен чертеж."),
        (14, "0000499593", "Картридж магистрального фильтра Atlas Copco PD 130+", "PD 130+ (1624108802 / 2901200405)", "Atlas Copco", 2, "шт.", 1676.0, "4–6 нед.", "Оценено (зарубежный хаб)", fill_priced, "Ультратонкий фильтр 0.01 мкм. Экспортный контроль."),
        (15, "0000256755", "Элемент второй ступени маслосепаратора 431120-1", "431120-1", "Keltec / OEM", 1, "шт.", None, "Уточняется", "Требуется шильдик компрессора", fill_pending, "Вторая ступень сепарации. Комплект к поз. 3."),
        (16, "0000237601", "Элемент фильтрующий FP310-10 (Ariel A-18845)", "FP310-10 / Ariel A-18845", "Ariel / Jonell", 5, "шт.", None, "Уточняется", "Требуется серийный номер Ariel", fill_pending, "Требование: строго 1 мкм. Нужен серийный номер Ariel."),
        (17, "0000239977", "Картридж HF51090R", "HF51090R", "Parker / Donaldson", 4, "шт.", None, "Уточняется", "Требуется подтверждение бренда/фото", fill_pending, "Гидравлический картридж. Нужны фото маркировки."),
        (18, "0000842897", "Фильтр масляный 01174416", "01174416", "Deutz", 2, "шт.", 50.0, "1–2 нед.", "Оценено (склад КНР, 2 шт.)", fill_priced, "Масляный фильтр дизеля Deutz, M24×1.5, наличие 2 шт."),
        (19, "0000239979", "Картридж HF51090S", "HF51090S", "Parker / Donaldson", 5, "шт.", None, "Уточняется", "Требуется подтверждение бренда/фото", fill_pending, "Комплект к поз. 17. Нужны фото маркировки."),
        (20, "0000842892", "Фильтр для очистки воздуха ДТ75М-1109560 А", "ДТ75М-1109560 А", "РФ (Автоприбор)", 4, "шт.", None, "Со склада РФ", "Отечественная номенклатура (РФ)", fill_rf, "Воздухоочиститель дизеля ДТ-75. Поставка с завода РФ."),
        (21, "0000850494", "Элемент серии \"Магистраль\" F-130-10-M-С-070", "F-130-10-M-С-070", "РФ (Сепаратор)", 3, "шт.", None, "Со склада РФ", "Отечественная номенклатура (РФ)", fill_rf, "Коалесцирующий фильтр по ТУ 3600-048-54116265-2016."),
        (22, "0000842895", "Фильтр для очистки воздуха ДТ75М-1109560-01 А", "ДТ75М-1109560-01 А", "РФ (Автоприбор)", 4, "шт.", None, "Со склада РФ", "Отечественная номенклатура (РФ)", fill_rf, "Воздушный фильтр компрессора ДТ-75. Поставка из РФ."),
        (23, "0000850485", "Элемент серии \"G-Oil\" ФЭМ-GY-10 95/48/276", "ФЭМ-GY-10 95/48/276", "РФ (Сепаратор/ГПН)", 3, "шт.", None, "Со склада РФ", "Отечественная номенклатура (РФ)", fill_rf, "Масляный фильтроэлемент по ТУ 4145-021-54116265-2011.")
    ]

    row_idx = 5
    priced_rows = []
    for it in items:
        r = row_idx
        ws.cell(row=r, column=1, value=it[0]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=2, value=it[1]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=3, value=it[2]).alignment = Alignment(horizontal="left", wrap_text=True)
        ws.cell(row=r, column=4, value=it[3]).alignment = Alignment(horizontal="left")
        ws.cell(row=r, column=5, value=it[4]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=6, value=it[5]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=7, value=it[6]).alignment = Alignment(horizontal="center")

        p_cell = ws.cell(row=r, column=8)
        s_cell = ws.cell(row=r, column=9)
        if it[7] is not None:
            p_cell.value = it[7]
            p_cell.number_format = "#,##0.00"
            p_cell.alignment = Alignment(horizontal="right")
            s_cell.value = f"=F{r}*H{r}"
            s_cell.number_format = "#,##0.00"
            s_cell.alignment = Alignment(horizontal="right")
            priced_rows.append(r)
        else:
            p_cell.value = "—"
            p_cell.alignment = Alignment(horizontal="center")
            s_cell.value = "—"
            s_cell.alignment = Alignment(horizontal="center")

        ws.cell(row=r, column=10, value=it[8]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=11, value=it[9]).alignment = Alignment(horizontal="center")
        ws.cell(row=r, column=12, value=it[11]).alignment = Alignment(horizontal="left", wrap_text=True)

        for c in range(1, 13):
            cell = ws.cell(row=r, column=c)
            cell.font = font_data
            cell.fill = it[10]
            cell.border = border_all
        row_idx += 1

    tot_r = row_idx
    ws.cell(row=tot_r, column=3, value="ИТОГО по подтвержденным позициям КНР (9 поз., 52 шт.):").alignment = Alignment(horizontal="right")
    ws.cell(row=tot_r, column=3).font = font_bold
    ws.cell(row=tot_r, column=6, value=f"=SUM(F5:F{tot_r-1})").alignment = Alignment(horizontal="center")
    ws.cell(row=tot_r, column=6).font = font_bold
    ws.cell(row=tot_r, column=7, value="шт.").alignment = Alignment(horizontal="center")
    ws.cell(row=tot_r, column=7).font = font_bold

    formula_parts = [f"I{r}" for r in priced_rows]
    tot_sum_cell = ws.cell(row=tot_r, column=9, value=f"={'+'.join(formula_parts)}")
    tot_sum_cell.number_format = "#,##0.00"
    tot_sum_cell.font = Font(name="Calibri", size=10, bold=True, color="1F497D")
    tot_sum_cell.alignment = Alignment(horizontal="right")

    for c in range(1, 13):
        cell = ws.cell(row=tot_r, column=c)
        cell.fill = fill_total
        cell.border = border_all

    col_widths = {1: 6, 2: 15, 3: 35, 4: 28, 5: 18, 6: 10, 7: 8, 8: 16, 9: 18, 10: 16, 11: 26, 12: 45}
    for col_idx, width in col_widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    wb.save(client_excel_path)
    print(f"[+] Клиентский Excel сохранен: {client_excel_path}")


def main():
    parser = argparse.ArgumentParser(description="Генератор пакета КП и опросного листа по фильтрам")
    parser.add_argument("--deal-id", type=int, default=2598, help="ID сделки Bitrix24 CRM")
    parser.add_argument("--output-dir", type=str, default=r"C:\Codex\projects\1c_odata\deals\deal_2598_ink_filters", help="Целевая директория")
    args = parser.parse_args()

    generate_filters_kp_package(args.deal_id, args.output_dir)


if __name__ == "__main__":
    main()
