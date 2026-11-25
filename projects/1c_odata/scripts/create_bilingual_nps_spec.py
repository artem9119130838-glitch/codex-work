#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_bilingual_nps_spec.py
Генерация профессиональной двуязычной (RU/CN) и чисто китайской (CN) спецификации
для Задачи #6160 (ООО «НПС», 110 комплектов Outdoor шкаф Тип 1).
Загрузка на Диск группы 14, прикрепление к задаче #6160 и отправка в чат снабжения.
"""

import os
import sys
sys.path.insert(0, r"C:\Codex\projects\1c_odata\scripts")
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from process_b24_inbound_leads import (
    call_b24,
    upload_file_to_b24_disk,
    send_b24_task_chat_message,
    FOLDER_CHINA_SUPPLY_DISK,
    USER_AZAT
)

def create_bilingual_spec_excel(output_path: str):
    wb = openpyxl.Workbook()

    # -------------------------------------------------------------
    # 1. Лист 1: 中俄双语 Bilingual (RU / CN)
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "中俄双语 Bilingual"
    ws1.views.sheetView[0].showGridLines = True

    # Стили
    font_title = Font(name="Arial", size=13, bold=True, color="1F4E78")
    font_subtitle = Font(name="Arial", size=10, bold=True, color="262626")
    font_sec = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    font_th = Font(name="Arial", size=9, bold=True, color="FFFFFF")
    font_cell = Font(name="Arial", size=9, color="000000")
    font_cell_bold = Font(name="Arial", size=9, bold=True, color="000000")
    font_cn = Font(name="Arial", size=9, color="1F4E78")
    font_note = Font(name="Arial", size=8, color="404040")

    fill_th = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    fill_sec1 = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    fill_sec2 = PatternFill(start_color="333F48", end_color="333F48", fill_type="solid")
    fill_sec3 = PatternFill(start_color="595959", end_color="595959", fill_type="solid")
    fill_zebra = PatternFill(start_color="F9FAFC", end_color="F9FAFC", fill_type="solid")
    fill_qty = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

    thin = Side(border_style="thin", color="D9D9D9")
    border_all = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Заголовок
    ws1.merge_cells("A1:L1")
    ws1["A1"] = "СПЕЦИФИКАЦИЯ НА ЗАКУПКУ — OUTDOOR ШКАФ ТИП 1 / 采购规格书 — 室外机柜 1型 (110台/套)"
    ws1["A1"].font = font_title
    ws1["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws1.row_dimensions[1].height = 28

    ws1.merge_cells("A2:L2")
    ws1["A2"] = "Клиент: ООО «Нефтепромысловые системы» (НПС) | Партия: 110 шкафов | Срок ответа: Четверг 26.11 до 13:00 МСК (周四前加急)"
    ws1["A2"].font = font_subtitle
    ws1["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws1.row_dimensions[2].height = 20

    ws1.row_dimensions[3].height = 6

    # Шапка таблицы
    headers_ws1 = [
        ("№\n序号", 5),
        ("Поз.\n位号", 8),
        ("Наименование оборудования / 技术规格与产品名称\n(Русский / 中文)", 42),
        ("Артикул / Модель\n规格型号", 18),
        ("Производитель\n品牌/生产厂家", 20),
        ("Кол./ед.\n单台用量", 10),
        ("Ед.\n单位", 8),
        ("Кол. на партию\n采购总数 (110台)", 15),
        ("Цена за ед.\n单价 (USD/RMB)", 14),
        ("Валюта\n币种", 8),
        ("Сумма\n总价", 12),
        ("Примечание и требования\n技术备注与要求 (RU / CN)", 36)
    ]

    for col_idx, (th_text, width) in enumerate(headers_ws1, start=1):
        c = ws1.cell(row=4, column=col_idx, value=th_text)
        c.font = font_th
        c.fill = fill_th
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border_all
        col_letter = get_column_letter(col_idx)
        ws1.column_dimensions[col_letter].width = width
    ws1.row_dimensions[4].height = 34

    # Строки данных
    # Формат: ('sec', title, fill) или ('data', [num, pos, ru_name, cn_name, model, brand, qty_unit, unit, qty_tot, curr, note_ru, note_cn])
    items_ws1 = [
        ("sec", "1. КОРПУС И КЛИМАТ (КИТАЙ) / 1. 机柜柜体与温控系统（中国品牌）", fill_sec1),
        ("data", [
            1, "",
            "Корпус шкафа 2000×800×800 мм, IP55, IK10, теплоизоляция, цоколь 800×800×100 мм (Ш×Г×В), с закрывающимися лючками сзади и с боков, отверстия Ø25 в днище (16 шт.)",
            "室外机柜柜体 2000×800×800 mm, IP55, IK10, 保温隔热, 底座 800×800×100 mm (宽×深×高), 后部及侧面带可关闭检修盖板, 底部带 Ø25 开孔 (16个)",
            "EAC-02B", "EverExceed",
            1, "шт. / 台", 110, "USD",
            "ТкП-4, 18", "符合技术规范 4, 18 条款"
        ]),
        ("data", [
            2, "A2",
            "Кондиционер 1500 Вт, −48 В DC, IP55, RS485 Modbus, на двери",
            "工业机柜空调 1500W, −48V DC, IP55, RS485 Modbus 通信接口, 门装式",
            "DC15HDNC1A", "Shenzhen Envicool\n(深圳市英维克)",
            1, "шт. / 台", 110, "USD",
            "ТкП-23…27", "符合技术规范 23…27 条款"
        ]),
        ("sec", "2. СИСТЕМА ЭЛЕКТРОПИТАНИЯ И МОНИТОРИНГ (КИТАЙ) / 2. 电源系统与监控（中国品牌）", fill_sec2),
        ("data", [
            3, "A1",
            "ЭПУ −48 В 6U, заказное исп.: без AC-ввода и AC-УЗИП, распределение по ТкП-49, 50 в 3U, без общей шины",
            "通信电源系统(ЭПУ) −48V 6U, 定制版：不含交流输入与交流防雷, 3U空间配电符合技术要求49、50, 无总母排",
            "E48400", "Shenzhen Impower\n(深圳英宝电气)",
            1, "компл. / 套", 110, "USD",
            "автоматы CHINT: CB-125CXZ ×7 (АКБ 4×125, BLVD 2×125, LLVD 125), CB-63CXZ ×7 (63×3, 32×3, 16)",
            "配正泰断路器: CB-125CXZ ×7 (电池 4×125A, BLVD 2×125A, LLVD 125A), CB-63CXZ ×7 (63A×3, 32A×3, 16A×1)"
        ]),
        ("data", [
            4, "A1",
            "Выпрямительный модуль 48 В, 4350 Вт",
            "高频开关整流模块 48V, 4350W",
            "HPR48-4000HE3", "Hanertek\n(华奈尔 / 航天远东)",
            4, "шт. / 台", 440, "USD",
            "подтвердить совместимость с E48400",
            "需确认与 Impower E48400 电源机架完全兼容"
        ]),
        ("data", [
            5, "A1.1",
            "Контроллер ЭПУ",
            "电源系统监控单元 (集中控制器)",
            "в составе E48400\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 台", 110, "USD",
            "Modbus к кондиционерам, BMS LiFePO4, SNMP",
            "支持空调Modbus通信、锂电池BMS协议、SNMP网管"
        ]),
        ("data", [
            6, "SQ2",
            "Датчик открытия двери (геркон)",
            "门禁传感器 (干簧管门磁开关)",
            "из комплекта ЭПУ\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 个", 110, "USD",
            "", ""
        ]),
        ("data", [
            7, "BS1",
            "Датчик дыма",
            "烟雾传感器 (光电感烟探测器)",
            "из комплекта ЭПУ\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 个", 110, "USD",
            "", ""
        ]),
        ("data", [
            8, "BL1",
            "Датчик протечки воды",
            "水浸传感器 (漏水探测器)",
            "из комплекта ЭПУ\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 个", 110, "USD",
            "", ""
        ]),
        ("data", [
            9, "BK1",
            "Датчик температуры",
            "温度传感器 (柜内温感探头)",
            "из комплекта ЭПУ\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 个", 110, "USD",
            "", ""
        ]),
        ("data", [
            10, "BH1",
            "Датчик температуры и влажности RS485",
            "RS485 温湿度传感器 (数字型)",
            "из комплекта ЭПУ\n(配套)", "Shenzhen Impower\n(深圳英宝电气)",
            1, "шт. / 个", 110, "USD",
            "", ""
        ]),
        ("data", [
            11, "EL1, EL2",
            "Светильник LED 48 В DC",
            "机柜照明 LED 灯 48V DC",
            "уточнить\n(待确认)", "Shenzhen Impower\n(深圳英宝电气)",
            2, "шт. / 支", 220, "USD",
            "запросить у Impower вместе с ЭПУ",
            "与电源系统一同向深圳英宝询价采购"
        ]),
        ("sec", "3. АККУМУЛЯТОРНЫЕ БАТАРЕИ (КИТАЙ) / 3. 储能锂电池组（中国品牌）", fill_sec3),
        ("data", [
            12, "GB1–GB3",
            "АКБ LiFePO4 48 В 100 А·ч, 19\" 3U, BMS RS485",
            "磷酸铁锂电池组 (LiFePO4) 48V 100Ah, 19英寸标准机架式 3U, 带 RS485 智能BMS",
            "SDA10-48100", "Shoto\n(双登集团)",
            3, "шт. / 组", 330, "USD",
            "место под 4-ю АКБ; UN3480",
            "柜内预留第4组电池安装位；运输与认证符合 UN3480 标准"
        ]),
    ]

    curr_row = 5
    for item in items_ws1:
        itype = item[0]
        if itype == "sec":
            sec_title, sec_fill = item[1], item[2]
            ws1.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=12)
            c = ws1.cell(row=curr_row, column=1, value=sec_title)
            c.font = font_sec
            c.fill = sec_fill
            c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            for col_i in range(1, 13):
                ws1.cell(row=curr_row, column=col_i).border = border_all
            ws1.row_dimensions[curr_row].height = 22
            curr_row += 1
        elif itype == "data":
            d = item[1]
            num, pos, ru_name, cn_name, model, brand, q_unit, unit, q_tot, curr, n_ru, n_cn = d
            
            # Двуязычный текст наименования
            combined_name = f"{ru_name}\n【中文】{cn_name}"
            # Двуязычное примечание
            combined_note = f"{n_ru}\n{n_cn}".strip() if (n_ru or n_cn) else ""

            row_vals = [
                num, pos, combined_name, model, brand, q_unit, unit, q_tot, "", curr, "", combined_note
            ]

            is_even = (num % 2 == 0)
            row_fill = fill_zebra if is_even else None

            for col_idx, val in enumerate(row_vals, start=1):
                c = ws1.cell(row=curr_row, column=col_idx, value=val)
                c.font = font_cell
                c.border = border_all
                if row_fill:
                    c.fill = row_fill

                if col_idx in (1, 2, 6, 7, 10):
                    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                elif col_idx == 8:
                    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    c.font = font_cell_bold
                    c.fill = fill_qty
                elif col_idx in (4, 5):
                    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                    c.font = font_cell_bold
                else:
                    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

            ws1.row_dimensions[curr_row].height = 42
            curr_row += 1

    # Итоговая строка
    ws1.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=7)
    c_tot_lbl = ws1.cell(row=curr_row, column=1, value="ИТОГО ПО СПЕЦИФИКАЦИИ / 采购总计 (12 позиций на 110 комплектов):")
    c_tot_lbl.font = font_subtitle
    c_tot_lbl.alignment = Alignment(horizontal="right", vertical="center")
    c_tot_lbl.border = border_all

    for c_i in range(1, 8):
        ws1.cell(row=curr_row, column=c_i).border = border_all

    c_tot_qty = ws1.cell(row=curr_row, column=8, value=1980)
    c_tot_qty.font = Font(name="Arial", size=10, bold=True, color="1F4E78")
    c_tot_qty.fill = fill_qty
    c_tot_qty.alignment = Alignment(horizontal="center", vertical="center")
    c_tot_qty.border = border_all

    for c_i in range(9, 13):
        ws1.cell(row=curr_row, column=c_i).border = border_all

    ws1.row_dimensions[curr_row].height = 24


    # -------------------------------------------------------------
    # 2. Лист 2: 采购清单 Chinese (For Chinese Suppliers)
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="采购清单 Chinese")
    ws2.views.sheetView[0].showGridLines = True

    # Заголовок
    ws2.merge_cells("A1:K1")
    ws2["A1"] = "室外机柜成套散件采购清单 (Outdoor Cabinet Components RFQ)"
    ws2["A1"].font = font_title
    ws2["A1"].alignment = Alignment(horizontal="left", vertical="center")
    ws2.row_dimensions[1].height = 28

    ws2.merge_cells("A2:K2")
    ws2["A2"] = "项目采购规模：110台/套 | 报价截止时间：周四（11月26日）北京时间 18:00 前 | 报价币种：RMB(含税) 或 USD"
    ws2["A2"].font = font_subtitle
    ws2["A2"].alignment = Alignment(horizontal="left", vertical="center")
    ws2.row_dimensions[2].height = 20

    ws2.row_dimensions[3].height = 6

    headers_ws2 = [
        ("序号\nNo.", 6),
        ("位号\nRef.", 8),
        ("产品名称及详细技术规格\nProduct Name & Technical Specifications", 45),
        ("规格型号\nPart Number / Model", 18),
        ("品牌 / 厂家\nBrand / Manufacturer", 20),
        ("单台用量\nQty/Unit", 10),
        ("单位\nUnit", 8),
        ("采购总数\nTotal Qty", 14),
        ("供货单价\nUnit Price", 14),
        ("币种\nCurrency", 8),
        ("技术要求及采购备注\nTechnical Notes / Requirements", 36)
    ]

    for col_idx, (th_text, width) in enumerate(headers_ws2, start=1):
        c = ws2.cell(row=4, column=col_idx, value=th_text)
        c.font = font_th
        c.fill = fill_th
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border_all
        col_letter = get_column_letter(col_idx)
        ws2.column_dimensions[col_letter].width = width
    ws2.row_dimensions[4].height = 32

    items_ws2 = [
        ("sec", "一、机柜柜体与温控系统 (Cabinet & Thermal Management)", fill_sec1),
        ("data", [
            1, "",
            "室外机柜柜体 2000×800×800 mm, IP55, IK10, 保温隔热材料, 配底座 800×800×100 mm (宽×深×高), 后部及侧面带可关闭检修盖板, 底部带 Ø25 开孔 (16个)",
            "EAC-02B", "EverExceed",
            1, "台", 110, "RMB/USD",
            "符合技术规范 4, 18 条款要求"
        ]),
        ("data", [
            2, "A2",
            "工业机柜空调 1500W, −48V DC, IP55, RS485 Modbus 通信接口, 门装式一体化空调",
            "DC15HDNC1A", "Shenzhen Envicool\n(英维克)",
            1, "台", 110, "RMB/USD",
            "符合技术规范 23…27 条款要求"
        ]),
        ("sec", "二、通信电源系统与动环监控 (Power System & Monitoring)", fill_sec2),
        ("data", [
            3, "A1",
            "通信电源系统(ЭПУ) −48V 6U, 定制版：不含交流输入与交流防雷, 3U空间配电符合技术要求, 无总母排",
            "E48400", "Shenzhen Impower\n(深圳英宝电气)",
            1, "套", 110, "RMB/USD",
            "正泰断路器: CB-125CXZ ×7 (电池 4×125A, BLVD 2×125A, LLVD 125A), CB-63CXZ ×7 (63A×3, 32A×3, 16A×1)"
        ]),
        ("data", [
            4, "A1",
            "高频开关整流模块 48V, 4350W (高效率)",
            "HPR48-4000HE3", "Hanertek\n(华奈尔 / 航天远东)",
            4, "台", 440, "RMB/USD",
            "需确认与深圳英宝 E48400 机架完全兼容插拔"
        ]),
        ("data", [
            5, "A1.1",
            "电源系统监控单元 (集中控制器)",
            "E48400配套控制器", "Shenzhen Impower\n(深圳英宝电气)",
            1, "台", 110, "RMB/USD",
            "需支持空调Modbus通信协议、锂电池BMS及SNMP网管"
        ]),
        ("data", [
            6, "SQ2",
            "门禁传感器 (干簧管门磁开关)",
            "电源系统配套", "Shenzhen Impower\n(深圳英宝电气)",
            1, "个", 110, "RMB/USD",
            "标准动环配套附件"
        ]),
        ("data", [
            7, "BS1",
            "烟雾传感器 (光电感烟探测器)",
            "电源系统配套", "Shenzhen Impower\n(深圳英宝电气)",
            1, "个", 110, "RMB/USD",
            "标准动环配套附件"
        ]),
        ("data", [
            8, "BL1",
            "水浸传感器 (漏水探测器)",
            "电源系统配套", "Shenzhen Impower\n(深圳英宝电气)",
            1, "个", 110, "RMB/USD",
            "标准动环配套附件"
        ]),
        ("data", [
            9, "BK1",
            "温度传感器 (柜内温感探头)",
            "电源系统配套", "Shenzhen Impower\n(深圳英宝电气)",
            1, "个", 110, "RMB/USD",
            "标准动环配套附件"
        ]),
        ("data", [
            10, "BH1",
            "RS485 温湿度传感器 (数字型)",
            "电源系统配套", "Shenzhen Impower\n(深圳英宝电气)",
            1, "个", 110, "RMB/USD",
            "带RS485通讯接口"
        ]),
        ("data", [
            11, "EL1, EL2",
            "机柜照明 LED 灯 48V DC",
            "待英宝确认型号", "Shenzhen Impower\n(深圳英宝电气)",
            2, "支", 220, "RMB/USD",
            "与电源系统一同向英宝电气询价采购"
        ]),
        ("sec", "三、储能锂电池组 (LiFePO4 Energy Storage Batteries)", fill_sec3),
        ("data", [
            12, "GB1–GB3",
            "磷酸铁锂电池组 (LiFePO4) 48V 100Ah, 19英寸标准机架式 3U, 带 RS485 智能BMS",
            "SDA10-48100", "Shoto\n(双登集团)",
            3, "组", 330, "RMB/USD",
            "机柜预留第4组电池安装位；包装与运输满足 UN3480 标准"
        ]),
    ]

    curr_row = 5
    for item in items_ws2:
        itype = item[0]
        if itype == "sec":
            sec_title, sec_fill = item[1], item[2]
            ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=11)
            c = ws2.cell(row=curr_row, column=1, value=sec_title)
            c.font = font_sec
            c.fill = sec_fill
            c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            for col_i in range(1, 12):
                ws2.cell(row=curr_row, column=col_i).border = border_all
            ws2.row_dimensions[curr_row].height = 22
            curr_row += 1
        elif itype == "data":
            d = item[1]
            num, pos, cn_desc, model, brand, q_unit, unit, q_tot, curr, note_cn = d
            row_vals = [
                num, pos, cn_desc, model, brand, q_unit, unit, q_tot, "", curr, note_cn
            ]
            is_even = (num % 2 == 0)
            row_fill = fill_zebra if is_even else None

            for col_idx, val in enumerate(row_vals, start=1):
                c = ws2.cell(row=curr_row, column=col_idx, value=val)
                c.font = font_cell
                c.border = border_all
                if row_fill:
                    c.fill = row_fill

                if col_idx in (1, 2, 6, 7, 10):
                    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                elif col_idx == 8:
                    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    c.font = font_cell_bold
                    c.fill = fill_qty
                elif col_idx in (4, 5):
                    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                    c.font = font_cell_bold
                else:
                    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

            ws2.row_dimensions[curr_row].height = 36
            curr_row += 1

    # Итог лист 2
    ws2.merge_cells(start_row=curr_row, start_column=1, end_row=curr_row, end_column=7)
    c_tot_lbl2 = ws2.cell(row=curr_row, column=1, value="采购总计 Total Qty (12项 / 110套机柜):")
    c_tot_lbl2.font = font_subtitle
    c_tot_lbl2.alignment = Alignment(horizontal="right", vertical="center")
    c_tot_lbl2.border = border_all

    for c_i in range(1, 8):
        ws2.cell(row=curr_row, column=c_i).border = border_all

    c_tot_qty2 = ws2.cell(row=curr_row, column=8, value=1980)
    c_tot_qty2.font = Font(name="Arial", size=10, bold=True, color="1F4E78")
    c_tot_qty2.fill = fill_qty
    c_tot_qty2.alignment = Alignment(horizontal="center", vertical="center")
    c_tot_qty2.border = border_all

    for c_i in range(9, 12):
        ws2.cell(row=curr_row, column=c_i).border = border_all

    ws2.row_dimensions[curr_row].height = 24

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Сформирован файл: {output_path}")
    return output_path

def main():
    target_task_id = 6160
    excel_filename = "26-398 Спецификация на закуп — Outdoor шкаф Тип 1 (Двуязычная RU_CN).xlsx"
    local_path = os.path.join(r"C:\Codex\projects\1c_odata\temp", excel_filename)

    print(f"1. Генерация двуязычного Excel-файла по ТЗ НПС...")
    create_bilingual_spec_excel(local_path)

    print(f"2. Загрузка файла на Диск группы 14...")
    disk_file_id = upload_file_to_b24_disk(local_path, FOLDER_CHINA_SUPPLY_DISK)
    if not disk_file_id:
        print("[ERROR] Не удалось загрузить файл на Диск")
        return
    print(f"   Успешно загружен на Диск: ID={disk_file_id}")

    print(f"3. Прикрепление файла к Задаче #{target_task_id}...")
    task_res = call_b24("tasks.task.get", {"taskId": target_task_id, "select": ["ID", "UF_TASK_WEBDAV_FILES", "DESCRIPTION"]})
    task_obj = task_res.get("task", {}) if task_res else {}
    current_files = task_obj.get("ufTaskWebdavFiles") or []
    if isinstance(current_files, dict):
        current_files = list(current_files.values())
    elif not isinstance(current_files, list):
        current_files = []

    # Добавляем новый файл
    new_files_param = [f"n{fid}" if not str(fid).startswith("n") else str(fid) for fid in current_files]
    new_file_str = f"n{disk_file_id}"
    if new_file_str not in new_files_param:
        new_files_param.append(new_file_str)

    current_desc = task_obj.get("description", "")
    new_file_link_bb = f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{disk_file_id}/]{excel_filename}[/URL] ([B]Двуязычная спецификация RU/CN + Чистовой китайский лист для фабрик КНР[/B])"
    
    if "СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ" in current_desc:
        updated_desc = current_desc.replace(
            "[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]",
            f"[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]\n{new_file_link_bb}"
        )
    else:
        updated_desc = f"{current_desc}\n\n[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]\n{new_file_link_bb}"

    call_b24("tasks.task.update", {
        "taskId": target_task_id,
        "fields": {
            "UF_TASK_WEBDAV_FILES": new_files_param,
            "DESCRIPTION": updated_desc
        }
    })
    print(f"   Файл прикреплен к Задаче #{target_task_id}, описание обновлено.")

    print(f"4. Отправка уведомления в чат Задачи #{target_task_id}...")
    chat_message = (
        f"[USER={USER_AZAT}]阿扎特[/USER] Обновление по срочной заявке Outdoor шкаф Тип 1 (НПС):\n"
        f"К задаче прикреплена полная двуязычная спецификация на китайском и русском языках:\n"
        f"📄 [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{disk_file_id}/]{excel_filename}[/URL]\n\n"
        f"В файле 2 листа:\n"
        f"1. [B]中俄双语 Bilingual[/B] — полное техническое описание и требования по всем 12 позициям (RU + CN);\n"
        f"2. [B]采购清单 Chinese[/B] — чистовой китайский лист для отправки непосредственно заводам и поставщикам в КНР (EverExceed, Envicool, Impower, Hanertek, Shoto).\n\n"
        f"⚠️ Напоминание: Срок предоставления цен — четверг 26.11 до обеда (13:00) по МСК!"
    )
    send_b24_task_chat_message(target_task_id, chat_message)
    print(f"   Уведомление и файл успешно отправлены в чат задачи.")

if __name__ == "__main__":
    main()
