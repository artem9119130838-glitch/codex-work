"""
Обновленный генератор таблиц проверки штоков (RU и EN):
- Учет всей переписки, согласований клиента и предложений завода (Report of the.docx)
- СТОПОР шлифовки пояска 179.9 до 179.6 мм до получения замеров дна канавок
- Требование замера внутреннего диаметра дна канавок для производителя уплотнений
- Запрос завода по радиусу r=0.5 вместо r=0.3
- Создание двух зеркальных версий:
    * Таблица_проверки_штоков_16шт.xlsx (Русская версия)
    * Таблица_проверки_штоков_16шт_EN.xlsx (English version)
- Внесение замеров биения от 23 сентября (1#, 4#, 5#, 6#, 9#, 10#, 11#, 14#, 16#)
"""

import os
import shutil
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def generate_workbook(lang="RU", output_path=""):
    wb = openpyxl.Workbook()

    # Fonts & Palette
    font_title = Font(name="Calibri", size=12, bold=True, color="1F497D")
    font_legend = Font(name="Calibri", size=9, bold=True)
    font_grp = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    font_header = Font(name="Calibri", size=9, bold=True, color="000000")
    font_sub = Font(name="Calibri", size=8, italic=True, color="333333")
    font_data = Font(name="Calibri", size=9)
    font_data_bold = Font(name="Calibri", size=9, bold=True)

    fill_green = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
    font_green = Font(name="Calibri", size=9, color="006100", bold=True)

    fill_yellow = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    font_yellow = Font(name="Calibri", size=9, color="7F6000")

    fill_white = PatternFill(fill_type=None)
    font_white = Font(name="Calibri", size=9, italic=True, color="595959")

    fill_red = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    font_red = Font(name="Calibri", size=9, color="9C0006", bold=True)

    fill_rework = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    font_rework = Font(name="Calibri", size=9, color="C65911", bold=True)

    fill_grp_id = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    fill_grp_runout = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
    fill_grp_dim = PatternFill(start_color="31859B", end_color="31859B", fill_type="solid")
    fill_grp_groove = PatternFill(start_color="E36C09", end_color="E36C09", fill_type="solid")
    fill_grp_th_l = PatternFill(start_color="595959", end_color="595959", fill_type="solid")
    fill_grp_th_r = PatternFill(start_color="7F7F7F", end_color="7F7F7F", fill_type="solid")
    fill_grp_chrome = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    fill_grp_ndt = PatternFill(start_color="4682B4", end_color="4682B4", fill_type="solid")
    fill_grp_media = PatternFill(start_color="274E13", end_color="274E13", fill_type="solid")
    fill_grp_verdict = PatternFill(start_color="0D343A", end_color="0D343A", fill_type="solid")

    fill_header_base = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
    fill_sub_base = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

    thin_border = Side(border_style="thin", color="D9D9D9")
    thick_border = Side(border_style="medium", color="595959")
    border_cell = Border(left=thin_border, right=thin_border, top=thin_border, bottom=thin_border)
    border_header = Border(left=thin_border, right=thin_border, top=thick_border, bottom=thick_border)

    ws = wb.active
    ws.views.sheetView[0].showGridLines = True

    # -------------------------------------------------------------
    # TEXT DEFINITIONS PER LANGUAGE (53 COLUMNS)
    # -------------------------------------------------------------
    if lang == "RU":
        ws.title = "Матрица_16_штоков"
        title_text = "СВОДНАЯ ВЕДОМОСТЬ ФАКТИЧЕСКИХ ЗАМЕРОВ И ДЕФЕКТОВКИ 16 ШТОКОВ Ø180x2574 мм (AISI 431)"
        legend_text = "ЛЕГЕНДА ЯЧЕЕК:  🟢 ЗЕЛЕНЫЙ = Проверено клиентом  |  🟡 ЖЕЛТЫЙ = Замер завода (не подтвержден)  |  ⚪ БЕЛЫЙ ('Замерить') = Требуется замер  |  🔴 КРАСНЫЙ = Брак / СТОПОР"
        to_measure = "Замерить"
        
        columns = [
            ("ИДЕНТИФИКАЦИЯ", fill_grp_id, "№ штока", "1 .. 16", 11),
            ("ИДЕНТИФИКАЦИЯ", fill_grp_id, "Маркировка", "Клеймо / фото", 14),
            ("ИДЕНТИФИКАЦИЯ", fill_grp_id, "Приоритет клиента", "1: Срочно / 2: Очередь / 3: Утиль", 22),
            ("ИДЕНТИФИКАЦИЯ", fill_grp_id, "Текущий диагноз", "Фактический статус на 28.09.2026", 42),

            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "Торец левый", "Индикатор (мм)", 13),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "1/4 слева (Ring 1)", "Индикатор (мм)", 15),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "Середина (Body)", "Контроль провиса (мм)", 16),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "1/4 справа (Ring 2)", "Индикатор (мм)", 15),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "Торец правый", "Индикатор (мм)", 13),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "Макс. биение", "Лимит ≤ 0,150 мм", 13),
            ("БИЕНИЕ В ЦЕНТРАХ (ЛИМИТ ≤ 0,15 мм)", fill_grp_runout, "Статус по биению", "ГОДЕН / БРАК", 16),

            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Общая длина L", "2574 ± 0,7 мм", 14),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Основной Ø180 f7", "179,917 .. 179,957 мм", 18),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Дефект: Ø на концах?", "Занижение на длине 300 мм", 24),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Поясок Ø179,9", "179,804 .. 179,850 мм", 15),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Шейка Ø171,6 (-0,1)", "171,500 .. 171,600 мм", 15),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Проточка Ø164,3", "Справочно (мм)", 14),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Длина резьбы слева", "245 мм (чертеж)", 15),
            ("РАЗМЕРЫ И ДЛИНА (МЕНЬШЕ = БРАК!)", fill_grp_dim, "Длина правого конца", "189 мм (чертеж)", 15),

            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Канавка 1 ширина", "8,6 +0,15 (факт завода)", 16),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Канавка 2 ширина", "8,6 +0,15 (факт завода)", 16),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Уширение канавок", "Согласование клиента", 18),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Глубина канавок", "4,0 мм (чертеж)", 14),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Внутренний Ø дна", "СРОЧНО ЗАМЕРИТЬ!", 18),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Проточка до 179.6", "СТОПОР: ждем уплотнения", 22),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Радиус кромки R0.3", "Запрос завода r=0.5", 18),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Притирка кромок", "Алмазный надфиль/паста", 20),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Шероховатость дна", "Rmax 1,5 мкм", 16),
            ("КАНАВКИ УПЛОТНЕНИЙ (ВИД А 2:1)", fill_grp_groove, "Шероховатость шейки", "Ra ≤ 0,32 мкм", 16),

            ("РЕЗЬБА ЛЕВАЯ M170x4-6g", fill_grp_th_l, "Калибр ПР (GO) лев.", "Полный проход от руки", 16),
            ("РЕЗЬБА ЛЕВАЯ M170x4-6g", fill_grp_th_l, "Калибр НЕ (NO-GO) лев.", "Останов ≤ 1,5..2 витка!", 18),
            ("РЕЗЬБА ЛЕВАЯ M170x4-6g", fill_grp_th_l, "Витки и фаска лев.", "Без забоин и заусенцев", 16),
            ("РЕЗЬБА ЛЕВАЯ M170x4-6g", fill_grp_th_l, "Контроль резьбы лев.", "Сплошной перемер калибром", 18),

            ("РЕЗЬБА ПРАВАЯ M170x4-6g", fill_grp_th_r, "Калибр ПР (GO) прав.", "Полный проход от руки", 16),
            ("РЕЗЬБА ПРАВАЯ M170x4-6g", fill_grp_th_r, "Калибр НЕ (NO-GO) прав.", "Останов ≤ 1,5..2 витка!", 18),
            ("РЕЗЬБА ПРАВАЯ M170x4-6g", fill_grp_th_r, "Витки и фаска прав.", "Переход 20°±15'", 16),
            ("РЕЗЬБА ПРАВАЯ M170x4-6g", fill_grp_th_r, "Контроль резьбы прав.", "Сплошной перемер калибром", 18),

            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Толщина хрома (мкм)", "Норма 80-100 мкм", 16),
            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Сошлифовка избытка", "Станочная шлифовка", 18),
            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Сколы хрома / торец", "Сошлифовка в фаску", 16),
            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Твердость HRC", "Чертеж: 50-55 HRC", 15),
            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Шероховатость Ra", "Норма Ra ≤ 0,30 мкм", 16),
            ("ХРОМ И ТВЕРДОСТЬ", fill_grp_chrome, "Марка стали", "AISI 431 (спектрометр)", 16),

            ("ДЕФЕКТОСКОПИЯ (NDT)", fill_grp_ndt, "Дефектоскопия NDT", "Без внутренних трещин", 16),
            ("ДЕФЕКТОСКОПИЯ (NDT)", fill_grp_ndt, "Внешний вид хрома", "Без пор, вздутий и царапин", 18),
            ("ДЕФЕКТОСКОПИЯ (NDT)", fill_grp_ndt, "Фаски торцов 3х45°", "Обе стороны по чертежу", 16),

            ("ФОТО / ВИДЕО ФИКСАЦИЯ", fill_grp_media, "Видеозапись замеров", "Непрерывная с клейма", 16),
            ("ФОТО / ВИДЕО ФИКСАЦИЯ", fill_grp_media, "Макро-фото дефектов", "Канавки, резьбы, фаски", 16),
            ("ФОТО / ВИДЕО ФИКСАЦИЯ", fill_grp_media, "ОТК / Замерщик", "Ответственное лицо", 15),

            ("ИТОГОВОЕ РЕШЕНИЕ", fill_grp_verdict, "Решение клиента", "Годен / Доработка / Утиль", 22),
            ("ИТОГОВОЕ РЕШЕНИЕ", fill_grp_verdict, "Условие приемки", "Требование заказчика", 30),
            ("ИТОГОВОЕ РЕШЕНИЕ", fill_grp_verdict, "План завода", "Конкретное действие цеха", 28),
            ("ИТОГОВОЕ РЕШЕНИЕ", fill_grp_verdict, "Риски и комментарии", "Анализ спасения штока", 35),
        ]
    else: # EN
        ws.title = "Rod_Matrix_16pcs"
        title_text = "MASTER INSPECTION & ACCEPTANCE MATRIX FOR 16 PISTON RODS Ø180x2574 mm (AISI 431)"
        legend_text = "CELL LEGEND:  🟢 GREEN = Verified & Accepted by Client  |  🟡 YELLOW = Factory Measurement (Unconfirmed)  |  ⚪ WHITE ('To measure') = Pending  |  🔴 RED = Defect / HOLD"
        to_measure = "To measure"

        columns = [
            ("IDENTIFICATION", fill_grp_id, "Rod No.", "1 .. 16", 11),
            ("IDENTIFICATION", fill_grp_id, "Marking / Stamp", "Stamp ID on end face", 14),
            ("IDENTIFICATION", fill_grp_id, "Client Priority", "1: Urgent / 2: Queue / 3: Scrap", 22),
            ("IDENTIFICATION", fill_grp_id, "Current Diagnosis", "Status as of 28.09.2026", 42),

            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "Left End", "Dial Indicator (mm)", 13),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "1/4 Left (Ring 1)", "Dial Indicator (mm)", 15),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "Middle (Body)", "Deflection Check (mm)", 16),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "1/4 Right (Ring 2)", "Dial Indicator (mm)", 15),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "Right End", "Dial Indicator (mm)", 13),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "Max Runout", "Limit ≤ 0.150 mm", 13),
            ("RUNOUT IN CENTERS (LIMIT ≤ 0.150 mm)", fill_grp_runout, "Runout Status", "PASS / SCRAP", 16),

            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Total Length L", "2574 ± 0.7 mm", 14),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Main OD Ø180 f7", "179.917 .. 179.957 mm", 18),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Defect: OD at ends?", "Undersize on 300mm ends", 24),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Step OD Ø179.9", "179.804 .. 179.850 mm", 15),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Seal Neck Ø171.6", "171.500 .. 171.600 mm", 15),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Undercut Ø164.3", "Reference dimension", 14),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Left Thread Length", "245 mm (Drawing)", 15),
            ("DIMENSIONS & LENGTH (LESS = SCRAP!)", fill_grp_dim, "Right End Length", "189 mm (Drawing)", 15),

            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Groove 1 Width", "8.6 +0.15 (Factory fact)", 16),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Groove 2 Width", "8.6 +0.15 (Factory fact)", 16),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Expansion Acceptance", "Client concession (+0.05)", 18),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Groove Depth", "4.0 mm (Drawing)", 14),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Groove Bottom ID", "URGENT TO MEASURE!", 18),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Grind to 179.6 mm", "HOLD: Awaiting seal check", 22),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Corner Radius R0.3", "Factory request r=0.5", 18),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Edge Deburring", "Diamond file / paste lap", 20),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Bottom Roughness", "Rmax 1.5 µm", 16),
            ("SEALING GROOVES (VIEW A 2:1)", fill_grp_groove, "Neck Roughness", "Ra ≤ 0.32 µm", 16),

            ("LEFT THREAD M170x4-6g", fill_grp_th_l, "GO Gauge (Left)", "Smooth full engagement", 16),
            ("LEFT THREAD M170x4-6g", fill_grp_th_l, "NO-GO Gauge (Left)", "Stop ≤ 1.5..2 turns!", 18),
            ("LEFT THREAD M170x4-6g", fill_grp_th_l, "Thread Turns (Left)", "No burrs or dents", 16),
            ("LEFT THREAD M170x4-6g", fill_grp_th_l, "Thread Verification", "100% video check", 18),

            ("RIGHT THREAD M170x4-6g", fill_grp_th_r, "GO Gauge (Right)", "Smooth full engagement", 16),
            ("RIGHT THREAD M170x4-6g", fill_grp_th_r, "NO-GO Gauge (Right)", "Stop ≤ 1.5..2 turns!", 18),
            ("RIGHT THREAD M170x4-6g", fill_grp_th_r, "Thread Turns (Right)", "Transition 20°±15'", 16),
            ("RIGHT THREAD M170x4-6g", fill_grp_th_r, "Thread Verification", "100% video check", 18),

            ("CHROME & HARDNESS", fill_grp_chrome, "Chrome Thickness (µm)", "Spec: 80-100 µm", 16),
            ("CHROME & HARDNESS", fill_grp_chrome, "Excess Grinding", "Cylindrical grinder only", 18),
            ("CHROME & HARDNESS", fill_grp_chrome, "End Face Chipping", "Blend into 3x45° chamfer", 16),
            ("CHROME & HARDNESS", fill_grp_chrome, "Hardness (HRC)", "Drawing: 50-55 HRC", 15),
            ("CHROME & HARDNESS", fill_grp_chrome, "Roughness Ra", "Spec: Ra ≤ 0.30 µm", 16),
            ("CHROME & HARDNESS", fill_grp_chrome, "Steel Grade", "AISI 431 (Spectrometer)", 16),

            ("NON-DESTRUCTIVE TESTING", fill_grp_ndt, "NDT Inspection", "No subsurface cracks", 16),
            ("NON-DESTRUCTIVE TESTING", fill_grp_ndt, "Visual Chrome Quality", "No pores, blisters or marks", 18),
            ("NON-DESTRUCTIVE TESTING", fill_grp_ndt, "End Chamfers 3x45°", "Both ends per drawing", 16),

            ("PHOTO & VIDEO EVIDENCE", fill_grp_media, "Video of Runout", "Continuous from stamp ID", 16),
            ("PHOTO & VIDEO EVIDENCE", fill_grp_media, "Macro Photos", "Grooves, threads, chamfers", 16),
            ("PHOTO & VIDEO EVIDENCE", fill_grp_media, "QC Inspector", "Responsible person", 15),

            ("FINAL VERDICT & ACTION", fill_grp_verdict, "Client Decision", "Pass / Rework / Strict Scrap", 22),
            ("FINAL VERDICT & ACTION", fill_grp_verdict, "Acceptance Condition", "Client requirement", 30),
            ("FINAL VERDICT & ACTION", fill_grp_verdict, "Factory Action Plan", "Concrete shop floor action", 28),
            ("FINAL VERDICT & ACTION", fill_grp_verdict, "Risk & Technical Notes", "Analysis of rod salvage", 35),
        ]

    # Row 1 & 2
    ws.merge_cells(f"A1:{get_column_letter(len(columns))}1")
    ws.cell(1, 1, title_text).font = font_title
    ws.cell(1, 1).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells(f"A2:{get_column_letter(len(columns))}2")
    c2 = ws.cell(2, 1, legend_text)
    c2.font = font_legend
    c2.alignment = Alignment(horizontal="center", vertical="center")
    c2.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    ws.row_dimensions[2].height = 20

    # Headers
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 24
    ws.row_dimensions[5].height = 18

    for idx, col in enumerate(columns, start=1):
        col_letter = get_column_letter(idx)
        ws.column_dimensions[col_letter].width = col[4]

        c4 = ws.cell(row=4, column=idx, value=col[2])
        c4.fill = fill_header_base
        c4.font = font_header
        c4.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c4.border = border_header

        c5 = ws.cell(row=5, column=idx, value=col[3])
        c5.fill = fill_sub_base
        c5.font = font_sub
        c5.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c5.border = border_cell

    # Merge Row 3 Groups
    curr_grp = None
    start_c = 1
    for idx, col in enumerate(columns, start=1):
        grp_name = col[0]
        grp_fill = col[1]
        if grp_name != curr_grp:
            if curr_grp is not None:
                ws.merge_cells(start_row=3, start_column=start_c, end_row=3, end_column=idx-1)
                for c_i in range(start_c, idx):
                    ws.cell(row=3, column=c_i).fill = prev_fill
                    ws.cell(row=3, column=c_i).border = border_header
                top_c = ws.cell(row=3, column=start_c, value=curr_grp)
                top_c.font = font_grp
                top_c.alignment = Alignment(horizontal="center", vertical="center")
            curr_grp = grp_name
            prev_fill = grp_fill
            start_c = idx
    ws.merge_cells(start_row=3, start_column=start_c, end_row=3, end_column=len(columns))
    for c_i in range(start_c, len(columns) + 1):
        ws.cell(row=3, column=c_i).fill = prev_fill
        ws.cell(row=3, column=c_i).border = border_header
    top_c = ws.cell(row=3, column=start_c, value=curr_grp)
    top_c.font = font_grp
    top_c.alignment = Alignment(horizontal="center", vertical="center")

    # Factory Data Dictionaries
    cn_d180 = {
        1: 179.93, 2: 179.91, 3: 179.92, 4: 179.94, 5: 179.93, 6: 179.95,
        7: 179.925, 8: 179.92, 9: 179.92, 10: "179.92 (300mm: 179.89)" if lang=="EN" else "179.92 (концы 179.89)",
        11: 179.94, 12: 179.94, 13: 179.92, 14: 179.92, 15: 179.94, 16: 179.92
    }
    cn_d179_9 = {
        1: 179.82, 2: 179.825, 3: 179.84, 4: 179.805, 5: 179.81, 6: 179.82,
        7: 179.82, 8: 179.82, 9: 179.83, 10: 179.84, 11: 179.83, 12: 179.80,
        13: 179.86, 14: 179.86, 15: 179.55, 16: 179.85
    }
    cn_d171_6 = {
        1: 171.56, 2: 171.55, 3: 171.45, 4: 171.55, 5: 171.55, 6: 171.58,
        7: 171.52, 8: 171.52, 9: 171.57, 10: 171.53, 11: 171.54, 12: 171.53,
        13: 171.50, 14: 171.53, 15: 171.40, 16: 171.50
    }
    cn_d164_3 = {
        1: 164.28, 2: 164.30, 3: 164.30, 4: 164.35, 5: 164.34, 6: 164.34,
        7: 164.37, 8: 164.40, 9: 164.48, 10: 164.20, 11: 164.32, 12: 164.30,
        13: 164.35, 14: 164.40, 15: 164.30, 16: 164.40
    }
    cn_g1 = {
        1: 8.86, 2: 8.85, 3: 8.90, 4: 8.87, 5: 8.86, 6: 8.89,
        7: 8.84, 8: 8.87, 9: 9.05, 10: 8.85, 11: 8.87, 12: 8.87,
        13: 8.87, 14: 8.87, 15: 8.77, 16: 8.62
    }
    cn_g2 = {
        1: 8.86, 2: 8.87, 3: 8.88, 4: 8.87, 5: 8.87, 6: 8.86,
        7: 8.87, 8: 8.87, 9: 9.10, 10: 8.90, 11: 8.85, 12: 8.86,
        13: 8.86, 14: 8.84, 15: 8.87, 16: 8.62
    }
    cn_chrome = {
        1: 100, 2: 100, 3: 850, 4: 100, 5: 100, 6: 100,
        7: 150, 8: 130, 9: 100, 10: 100, 11: 100, 12: 100,
        13: 100, 14: 100, 15: 100, 16: 100
    }
    cn_ra = {
        1: 0.093, 2: 0.096, 3: 0.183, 4: 0.110, 5: 0.212, 6: 0.135,
        7: 0.146, 8: 0.140, 9: 0.103, 10: 0.168, 11: 0.098, 12: 0.092,
        13: 0.079, 14: 0.280, 15: 0.110, 16: 0.124
    }
    cn_hrc = {
        1: 45.8, 2: 49.6, 3: 46.5, 4: 51.3, 5: 47.0, 6: 51.3,
        7: 50.6, 8: 50.3, 9: 48.3, 10: 49.8, 11: 49.1, 12: 48.8,
        13: 52.1, 14: 49.8, 15: 45.7, 16: 48.0
    }

    if lang == "RU":
        status_info = {
            1: ("3: Утиль (Брак)", "Биение 0.170 мм (>0.15), HRC=45.8. Ra=0.093 мкм.", 0.150, 0.180, 0.180, 0.170, "БРАК (>0.150 мм)", "❌ СТРОГИЙ БРАК", "Биение 0.170 мм превышает согласованный лимит 0.15 мм! HRC 45.8 ниже 50.", "Возврат денег заводом / переделка. Попытка перешлифовки цеха до 179.65 отклонена (ТВЧ 45.8 HRC < 50).", "Брак по биению и твердости подтвержден."),
            2: ("1: Срочно к сдаче", "Годен к приемке. Проверить резьбы калибром НЕ. Проверить Ø180 (факт 179.91 мм).", None, None, None, None, "Замерить", "🟢 ГОДЕН К ПРИЕМКЕ", "Примет: перепроверить резьбы калибром НЕ, подтвердить Ø180 микрометром", "Сплошной перемер калибром НЕ на видео", "Первая очередь приемки."),
            3: ("3: Строгий Брак", "Шейка Ø171.45 (-0.05 мм меньше допуска!), хром 850 мкм, HRC=46.5.", None, None, None, None, "Замерить", "❌ СТРОГИЙ БРАК", "Клиент однозначно не примет: размеры меньше чертежа, хром с наплывом 850 мкм!", "Возврат денег заводом / изготовление заново. Предложение цеха по щеточной гальванике (刷镀) отклонено: риск расслоения под 35 МПа.", "Просадка металла шейки и хром 850 мкм не восстанавливаются."),
            4: ("1: Срочно (ГОДЕН)", "Биение 0.040 мм (≤0.15). HRC=51.3. Притерты кромки канавок.", 0.030, 0.050, 0.040, 0.040, "ГОДЕН (≤0,15 мм)", "🟢 ГОДЕН К ПРИЕМКЕ", "Примет: подтвердить резьбу калибром НЕ (останов ≤1.5 витка)", "Притирка кромок канавок надфилем, отправка", "Один из лучших штоков партии! Биение с огромным запасом."),
            5: ("1: ГОДЕН ПО БИЕНИЮ!", "Биение 0.073 мм (ГОДЕН ≤0.15 мм!). HRC=47.0.", 0.070, 0.070, 0.080, 0.073, "ГОДЕН (≤0,15 мм)", "🟢 ГОДЕН ПО БИЕНИЮ", "Примет: биение 0.073 ≤ 0.15! Подтвердить резьбу калибром НЕ", "Притирка канавок, проверка калибров", "Спасен согласованием лимита биения 0.15 мм!"),
            6: ("1: Срочно (Резьба?)", "Биение 0.140 мм (ГОДЕН ≤0.15). HRC=51.3. Подозрение на просадку резьбы!", 0.150, 0.150, 0.120, 0.140, "ГОДЕН ПО БИЕНИЮ (≤0.15)", "⚠️ КРИТИЧЕСКАЯ РЕЗЬБА", "Клиент однозначно не примет, если калибр НЕ прокрутится глубже 2 витков!", "Срочная видеозапись с калибром НЕ M170x4-6g", "По биению прошел. Судьба штока зависит от калибра НЕ."),
            7: ("2: Спасение (хром)", "Хром 150 мкм (избыток 50 мкм). Снять 50 мкм на круглошлифовальном станке.", None, None, None, None, "Замерить", "🔄 ПРИЕМКА ПОСЛЕ ШЛИФОВКИ", "Примет ТОЛЬКО после снятия 50 мкм хрома на точном круглошлифовальном станке!", "Станочная сошлифовка 50 мкм хрома до слоя 100 мкм. Итоговый Ø180 строго в поле f7 (179.917–179.957 мм). Занижение до 179.86 запрещено!", "Ручная шлифовка строго запрещена во избежание гранности!"),
            8: ("2: Спасение (хром)", "Хром 130 мкм (избыток 30 мкм). Снять 30 мкм на круглошлифовальном станке.", None, None, None, None, "Замерить", "🔄 ПРИЕМКА ПОСЛЕ ШЛИФОВКИ", "Примет ТОЛЬКО после снятия 30 мкм хрома на точном станке!", "Станочная сошлифовка 30 мкм хрома до слоя 100 мкм. Итоговый Ø180 строго в поле f7 (179.917–179.957 мм). Занижение до 179.86 запрещено!", "После перешлифовки шток полностью годен к отгрузке."),
            9: ("1: Срочно (Резьба?)", "Биение 0.140 мм (ГОДЕН ≤0.15). Рекордная ширина канавки 9.10 мм!", 0.150, 0.150, 0.120, 0.140, "ГОДЕН ПО БИЕНИЮ (≤0.15)", "⚠️ КРИТИЧЕСКАЯ РЕЗЬБА / КАНАВКА", "Калибр НЕ на резьбе должен встать ≤ 2 витка. Согласовать канавку 9.10 мм.", "Видеопроверка калибра НЕ и подтверждение уширения у клиента", "По биению уложился (0.140 ≤ 0.15). Проверить резьбу."),
            10: ("2: Вторая очер. (Ø)", "Биение 0.117 мм (≤0.15). ЗАВОД ПРИЗНАЛ: на концах 300 мм Ø180 провален до 179.89 мм!", 0.150, 0.120, 0.080, 0.117, "ГОДЕН ПО БИЕНИЮ (≤0.15)", "⚠️ ЗАНИЖЕНИЕ ДИАМЕТРА НА КОНЦАХ", "Клиент не примет размер меньше чертежа (179.89 < 179.917). Требуется повторный перемер!", "Независимый замер Ø180 по всей длине с шагом 100 мм", "Если 179.89 подтвердится — утиль по условию №4 клиента."),
            11: ("1: ГОДЕН ПО БИЕНИЮ!", "Биение 0.120 мм (ГОДЕН ≤0.15 мм!). Хром 100 мкм, HRC=49.1.", 0.120, 0.120, 0.120, 0.120, "ГОДЕН (≤0,15 мм)", "🟢 ГОДЕН ПО БИЕНИЮ", "Примет: биение 0.120 ≤ 0.15! Подтвердить резьбу калибром НЕ", "Проверка калибров, притирка кромок канавок", "Спасен согласованием допуска 0.15 мм."),
            12: ("2: Вторая очередь", "Ожидает замера биения в центрах. Поясок Ø179.80 (на 4 мкм ниже допуска).", None, None, None, None, "Замерить", "⚪ ТРЕБУЮТСЯ ЗАМЕРЫ", "Замерить биение в 5 точках, подтвердить резьбу калибром НЕ", "Провести замер биения индикатором часового типа", "Вторая очередь проверки."),
            13: ("2: Вторая очер. (Резьба)", "HRC=52.1 (отлично). Подозрение на забоины резьбы по видеозаписи.", None, None, None, None, "Замерить", "⚠️ ПЕРЕПРОВЕРКА РЕЗЬБЫ", "Проверить резьбу калибрами ПР и НЕ, подтвердить отсутствие забоин", "Видеозапись навинчивания калибров M170x4-6g", "Металл и твердость в норме, решить вопрос по резьбе."),
            14: ("1: ГОДЕН ПО БИЕНИЮ!", "Биение 0.110 мм (ГОДЕН ≤0.15 мм!). HRC=49.8.", 0.120, 0.110, 0.100, 0.110, "ГОДЕН (≤0,15 мм)", "🟢 ГОДЕН ПО БИЕНИЮ", "Примет: биение 0.110 ≤ 0.15! Подтвердить резьбу калибром НЕ", "Притирка канавок, проверка резьбы", "Спасен согласованием допуска 0.15 мм."),
            15: ("3: Строгий Брак", "Поясок Ø179.55 (-0.25 мм меньше чертежа!), шейка Ø171.40, HRC=45.7.", None, None, None, None, "Замерить", "❌ СТРОГИЙ БРАК", "Клиент однозначно не примет: грубое занижение посадочных диаметров!", "Возврат денег заводом / переделка партии. Предложение по щеточной гальванике (刷镀) отклонено: поясок -0.25 мм и HRC 45.7 не восстанавливаются.", "Не подлежит ремонту. Чистый брак мехобработки цеха."),
            16: ("1: Срочно (ЭТАЛОН)", "Биение 0.033 мм (идеальное!). Хром 100 мкм, канавки 8.62 мм.", 0.030, 0.020, 0.050, 0.033, "ГОДЕН (≤0,15 мм)", "🟢 ГОДЕН (ЭТАЛОН)", "Примет в первую очередь! Подтвердить резьбу калибром НЕ", "Притирка канавок, подготовка к немедленной отгрузке", "Лучший шток партии, идеальная геометрия.")
        }
    else: # EN
        status_info = {
            1: ("3: Scrap", "Runout 0.170 mm (>0.15), HRC=45.8. Ra=0.093 µm.", 0.150, 0.180, 0.180, 0.170, "SCRAP (>0.150 mm)", "❌ STRICT SCRAP", "Runout 0.170 mm exceeds agreed 0.15 mm limit! Hardness 45.8 < 50 HRC.", "Factory refund / remake batch. Regrinding to 179.65 rejected (Core induction 45.8 < 50 HRC).", "Scrap confirmed by runout and low core hardness."),
            2: ("1: Urgent Delivery", "Ready for acceptance. Check threads with NO-GO gauge. Check Ø180 (fact 179.91 mm).", None, None, None, None, "To measure", "🟢 READY FOR ACCEPTANCE", "Acceptable: verify thread with NO-GO gauge, confirm Ø180 with micrometer", "100% video check with NO-GO ring gauge", "1st priority batch for delivery."),
            3: ("3: Strict Scrap", "Neck Ø171.45 (-0.05 mm under tolerance!), chrome 850 µm, HRC=46.5.", None, None, None, None, "To measure", "❌ STRICT SCRAP", "Client strictly rejects: dimension under drawing, chrome surge 850 µm!", "Factory refund / remake from scratch. Brush plating (刷镀) proposal rejected: dynamic delamination risk at 35 MPa.", "Undersized neck and 850 µm chrome surge cannot be repaired."),
            4: ("1: Urgent (PASS)", "Runout 0.040 mm (≤0.15). HRC=51.3. Groove edges polished.", 0.030, 0.050, 0.040, 0.040, "PASS (≤0.15 mm)", "🟢 READY FOR ACCEPTANCE", "Acceptable: confirm thread with NO-GO gauge (stop ≤1.5 turns)", "Hand lap groove edges, ship to client", "One of best rods! Runout with huge safety margin."),
            5: ("1: PASS BY RUNOUT!", "Runout 0.073 mm (PASS ≤0.15 mm!). HRC=47.0.", 0.070, 0.070, 0.080, 0.073, "PASS (≤0.15 mm)", "🟢 PASS BY RUNOUT", "Acceptable: runout 0.073 ≤ 0.15! Confirm thread with NO-GO gauge", "Lap groove edges, gauge check", "Saved by client concession to 0.15 mm runout!"),
            6: ("1: Urgent (Thread?)", "Runout 0.140 mm (PASS ≤0.15). HRC=51.3. Suspicion of thread undersize!", 0.150, 0.150, 0.120, 0.140, "PASS RUNOUT (≤0.15)", "⚠️ CRITICAL THREAD", "Client strictly rejects if NO-GO gauge engages >2 turns!", "Urgent video test with M170x4-6g NO-GO gauge", "Passed runout. Destiny depends 100% on NO-GO thread gauge."),
            7: ("2: Rework (Chrome)", "Chrome 150 µm (+50 µm excess). Grind 50 µm on cylindrical grinder.", None, None, None, None, "To measure", "🔄 ACCEPT AFTER GRINDING", "Accept ONLY after precision machine grinding 50 µm down to 100 µm!", "Machine grinding of 50 µm chrome to 100 µm spec. Finished OD must stay in f7 (179.917–179.957 mm). Grinding to 179.86 is forbidden!", "Manual grinding is STRICTLY PROHIBITED to avoid waviness!"),
            8: ("2: Rework (Chrome)", "Chrome 130 µm (+30 µm excess). Grind 30 µm on cylindrical grinder.", None, None, None, None, "To measure", "🔄 ACCEPT AFTER GRINDING", "Accept ONLY after precision machine grinding 30 µm down to 100 µm!", "Machine grinding of 30 µm chrome to 100 µm spec. Finished OD must stay in f7 (179.917–179.957 mm). Grinding to 179.86 is forbidden!", "Fully acceptable after precision machine re-grinding."),
            9: ("1: Urgent (Thread?)", "Runout 0.140 mm (PASS ≤0.15). Critical groove width 9.10 mm!", 0.150, 0.150, 0.120, 0.140, "PASS RUNOUT (≤0.15)", "⚠️ CRITICAL THREAD / GROOVE", "NO-GO gauge must stop ≤2 turns. Confirm 9.10 mm groove acceptance.", "Video test of NO-GO gauge and client groove concession", "Passed runout (0.140 ≤ 0.15). Check thread."),
            10: ("2: Queue (OD ends)", "Runout 0.117 mm (≤0.15). FACTORY ADMITTED: ends 300mm have Ø180 undersized to 179.89 mm!", 0.150, 0.120, 0.080, 0.117, "PASS RUNOUT (≤0.15)", "⚠️ OD UNDERSIZE AT ENDS", "Client rejects dimensions under drawing (179.89 < 179.917). Re-measurement required!", "Independent OD micrometer measurement every 100 mm", "If 179.89 mm confirmed — scrap under Condition #4."),
            11: ("1: PASS BY RUNOUT!", "Runout 0.120 mm (PASS ≤0.15 mm!). Chrome 100 µm, HRC=49.1.", 0.120, 0.120, 0.120, 0.120, "PASS (≤0.15 mm)", "🟢 PASS BY RUNOUT", "Acceptable: runout 0.120 ≤ 0.15! Confirm thread with NO-GO gauge", "Gauge check, groove edge de-burring", "Saved by 0.15 mm runout concession."),
            12: ("2: Queue", "Pending runout measurement in centers. Step Ø179.80 (4 µm under tolerance).", None, None, None, None, "To measure", "⚪ PENDING MEASUREMENTS", "Measure runout in 5 points, confirm thread with NO-GO gauge", "Perform dial indicator runout check", "2nd priority queue."),
            13: ("2: Queue (Thread)", "HRC=52.1 (excellent). Video shows suspected dents on thread.", None, None, None, None, "To measure", "⚠️ RE-CHECK THREAD", "Check thread with GO and NO-GO gauges, confirm no dents", "Video record of thread engagement M170x4-6g", "Metal and hardness good, resolve thread issue."),
            14: ("1: PASS BY RUNOUT!", "Runout 0.110 mm (PASS ≤0.15 mm!). HRC=49.8.", 0.120, 0.110, 0.100, 0.110, "PASS (≤0.15 mm)", "🟢 PASS BY RUNOUT", "Acceptable: runout 0.110 ≤ 0.15! Confirm thread with NO-GO gauge", "Lap groove edges, thread verification", "Saved by 0.15 mm runout concession."),
            15: ("3: Strict Scrap", "Step Ø179.55 (-0.25 mm under drawing!), neck Ø171.40, HRC=45.7.", None, None, None, None, "To measure", "❌ STRICT SCRAP", "Client strictly rejects: severe undersize on seating diameters!", "Factory refund / remake batch. Brush plating (刷镀) proposal rejected: -0.25 mm step and 45.7 HRC cannot be repaired.", "Cannot be repaired. Shop floor machining scrap."),
            16: ("1: Urgent (BENCHMARK)", "Runout 0.033 mm (benchmark!). Chrome 100 µm, grooves 8.62 mm.", 0.030, 0.020, 0.050, 0.033, "PASS (≤0.15 mm)", "🟢 PASS (BENCHMARK)", "Highest delivery priority! Confirm thread with NO-GO gauge", "Lap groove edges, prepare for immediate dispatch", "Best rod of entire batch, perfect geometry.")
        }

    # Fill 16 rows
    start_row = 6
    for rod_id in range(1, 17):
        r_num = start_row + rod_id - 1
        ws.row_dimensions[r_num].height = 24
        s = status_info[rod_id]

        prio_txt = s[0]
        diag_txt = s[1]
        b_val = s[2]
        r1_val = s[3]
        r2_val = s[4]
        max_run = s[5]
        run_eval = s[6]
        verdict = s[7]
        cond_txt = s[8]
        act_txt = s[9]
        notes_txt = s[10]

        for col_idx, col in enumerate(columns, start=1):
            title = col[2]
            cell = ws.cell(row=r_num, column=col_idx)
            cell.border = border_cell
            cell.font = font_data
            cell.alignment = Alignment(horizontal="center", vertical="center")

            # Col 1: ID
            if col_idx == 1:
                cell.value = f"Rod #{rod_id}" if lang=="EN" else f"Шток №{rod_id}"
                cell.font = font_data_bold
                cell.fill = fill_sub_base
            elif col_idx == 2:
                cell.value = "Stamp ID on end" if lang=="EN" else "Клеймо на торце"
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 3:
                cell.value = prio_txt
                if "1:" in prio_txt:
                    cell.fill = fill_green
                    cell.font = font_green
                elif "2:" in prio_txt:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_red
                    cell.font = font_red
            elif col_idx == 4:
                cell.value = diag_txt
                cell.alignment = Alignment(horizontal="left", vertical="center")
                if "Scrap" in prio_txt or "Брак" in prio_txt:
                    cell.fill = fill_red
                    cell.font = font_red
                elif "Rework" in prio_txt or "Спасение" in prio_txt:
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif "1:" in prio_txt:
                    cell.fill = fill_green
                    cell.font = font_green

            # Runout 5-9
            elif col_idx in [5, 9]:
                cell.value = to_measure
                cell.fill = fill_white
                cell.font = font_white
            elif col_idx == 6: # Ring 1
                if r1_val is not None:
                    cell.value = r1_val
                    cell.number_format = "0.000"
                    cell.fill = fill_green if max_run <= 0.150 else fill_red
                    cell.font = font_green if max_run <= 0.150 else font_red
                else:
                    cell.value = to_measure
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 7: # Body
                if b_val is not None:
                    cell.value = b_val
                    cell.number_format = "0.000"
                    if rod_id == 10:
                        cell.fill = fill_yellow
                        cell.font = font_yellow
                    else:
                        cell.fill = fill_green if max_run <= 0.150 else fill_red
                        cell.font = font_green if max_run <= 0.150 else font_red
                else:
                    cell.value = to_measure
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 8: # Ring 2
                if r2_val is not None:
                    cell.value = r2_val
                    cell.number_format = "0.000"
                    cell.fill = fill_green if max_run <= 0.150 else fill_red
                    cell.font = font_green if max_run <= 0.150 else font_red
                else:
                    cell.value = to_measure
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 10: # Max runout
                if max_run is not None:
                    cell.value = max_run
                    cell.number_format = "0.000"
                    if max_run <= 0.150:
                        cell.fill = fill_green
                        cell.font = font_green
                    else:
                        cell.fill = fill_red
                        cell.font = font_red
                else:
                    cell.value = to_measure
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 11: # Status
                cell.value = run_eval
                if "PASS" in run_eval or "ГОДЕН" in run_eval:
                    cell.fill = fill_green
                    cell.font = font_green
                elif "measure" in run_eval or "Замерить" in run_eval:
                    cell.fill = fill_white
                    cell.font = font_white
                else:
                    cell.fill = fill_red
                    cell.font = font_red

            # 12. Length L
            elif col_idx == 12:
                cell.value = 2574
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 13. Main OD Ø180
            elif col_idx == 13:
                v = cn_d180.get(rod_id)
                cell.value = v
                if rod_id == 10:
                    cell.fill = fill_red
                    cell.font = font_red
                elif rod_id == 2:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_yellow
                    cell.font = font_yellow

            # 14. OD at ends defect
            elif col_idx == 14:
                if rod_id == 10:
                    cell.value = "YES: 179.89 mm on 300mm ends!" if lang=="EN" else "ДА: 179.89 мм на концах 300 мм!"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "In tolerance per factory report" if lang=="EN" else "В норме (по отчету завода)"
                    cell.fill = fill_yellow
                    cell.font = font_yellow

            # 15. Step OD Ø179.9
            elif col_idx == 15:
                v = cn_d179_9.get(rod_id)
                cell.value = v
                if rod_id in [12, 15]:
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.fill = fill_yellow
                    cell.font = font_yellow

            # 16. Neck Ø171.6
            elif col_idx == 16:
                v = cn_d171_6.get(rod_id)
                cell.value = v
                if rod_id in [3, 15]:
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.fill = fill_yellow
                    cell.font = font_yellow

            # 17. Undercut Ø164.3
            elif col_idx == 17:
                cell.value = cn_d164_3.get(rod_id)
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 18-19. Lengths
            elif col_idx == 18:
                cell.value = 245
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 19:
                cell.value = 189
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 20. Groove 1 width
            elif col_idx == 20:
                v = cn_g1.get(rod_id)
                cell.value = v
                if v > 8.75:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_green
                    cell.font = font_green

            # 21. Groove 2 width
            elif col_idx == 21:
                v = cn_g2.get(rod_id)
                cell.value = v
                if v > 8.95:
                    cell.fill = fill_red
                    cell.font = font_red
                elif v > 8.75:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_green
                    cell.font = font_green

            # 22. Groove expansion
            elif col_idx == 22:
                if rod_id in [1, 3, 15]:
                    cell.value = "Rejected (rod scrapped)" if lang=="EN" else "Отказ (брак штока)"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "Accepted by client (+0.05)" if lang=="EN" else "Согласовано клиентом (+0,05)"
                    cell.fill = fill_green
                    cell.font = font_green

            # 23. Groove depth
            elif col_idx == 23:
                cell.value = 4.0
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 24. NEW: Groove Bottom ID
            elif col_idx == 24:
                if rod_id in [1, 3, 15]:
                    cell.value = "Scrapped" if lang=="EN" else "Не требуется (утиль)"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "URGENT TO MEASURE" if lang=="EN" else "СРОЧНО ЗАМЕРИТЬ ДНУ"
                    cell.fill = fill_yellow
                    cell.font = font_yellow

            # 25. NEW: Grind to 179.6 mm (HOLD)
            elif col_idx == 25:
                if rod_id in [1, 3, 15]:
                    cell.value = "Scrapped" if lang=="EN" else "В утиль"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "HOLD: Check seals first!" if lang=="EN" else "СТОПОР: Ждем расчет манжет!"
                    cell.fill = fill_rework
                    cell.font = font_rework

            # 26. Corner Radius R0.3 / r=0.5
            elif col_idx == 26:
                cell.value = "Factory asked r=0.5 (Under review)" if lang=="EN" else "Запрос завода r=0.5 (на согласовании)"
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 27. Deburring
            elif col_idx == 27:
                if rod_id in [1, 3, 15]:
                    cell.value = "Scrap" if lang=="EN" else "В утиль"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "Mandatory diamond hand lapping" if lang=="EN" else "Обязательна притирка надфилем"
                    cell.fill = fill_rework
                    cell.font = font_rework

            # 28. Bottom roughness
            elif col_idx == 28:
                cell.value = "Rmax 1.5 (In spec)" if lang=="EN" else "Rmax 1.5 (в норме)"
                cell.fill = fill_green
                cell.font = font_green

            # 29. Neck roughness
            elif col_idx == 29:
                cell.value = "Ra ≤ 0.32 (In spec)" if lang=="EN" else "Ra ≤ 0.32 (в норме)"
                cell.fill = fill_green
                cell.font = font_green

            # 30-33. Thread Left
            elif col_idx == 30:
                cell.value = "Factory: Pass (合格)" if lang=="EN" else "Завод: 合格 (Pass)"
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 31:
                if rod_id in [6, 9]:
                    cell.value = "Suspected undersize >2 turns" if lang=="EN" else "Подозрение: прокрутка >2 витков"
                    cell.fill = fill_red
                    cell.font = font_red
                elif rod_id == 13:
                    cell.value = "Suspected dents" if lang=="EN" else "Подозрение на забоины"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "To measure (≤1.5..2 turns)" if lang=="EN" else "Замерить (≤1.5..2 витка)"
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 32:
                cell.value = "Visually clear" if lang=="EN" else "Визуально без забоин"
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 33:
                cell.value = "100% check required" if lang=="EN" else "Обязательный сплошной перемер"
                cell.fill = fill_rework
                cell.font = font_rework

            # 34-37. Thread Right
            elif col_idx == 34:
                cell.value = "Factory: Pass (合格)" if lang=="EN" else "Завод: 合格 (Pass)"
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 35:
                if rod_id in [6, 9]:
                    cell.value = "Suspected undersize >2 turns" if lang=="EN" else "Подозрение: прокрутка >2 витков"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "To measure (≤1.5..2 turns)" if lang=="EN" else "Замерить (≤1.5..2 витка)"
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 36:
                cell.value = "Transition 20°±15'"
                cell.fill = fill_yellow
                cell.font = font_yellow
            elif col_idx == 37:
                cell.value = "100% check required" if lang=="EN" else "Обязательный сплошной перемер"
                cell.fill = fill_rework
                cell.font = font_rework

            # 38. Chrome thickness
            elif col_idx == 38:
                v = cn_chrome.get(rod_id)
                cell.value = v
                if rod_id in [7, 8]:
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif rod_id == 3:
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.fill = fill_green
                    cell.font = font_green

            # 39. Chrome grinding
            elif col_idx == 39:
                if rod_id == 7:
                    cell.value = "Machine grind 50 µm" if lang=="EN" else "Снять 50 мкм на круглошлиф. станке"
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif rod_id == 8:
                    cell.value = "Machine grind 30 µm" if lang=="EN" else "Снять 30 мкм на круглошлиф. станке"
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif rod_id == 3:
                    cell.value = "850 µm surge (Scrap)" if lang=="EN" else "850 мкм — наплыв (утиль)"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "Not required (100 µm spec)" if lang=="EN" else "Не требуется (слой 100 мкм)"
                    cell.fill = fill_green
                    cell.font = font_green

            # 40. Chipping
            elif col_idx == 40:
                cell.value = "Blend into smooth chamfer" if lang=="EN" else "Сошлифовать сколы резца в фаску"
                cell.fill = fill_rework
                cell.font = font_rework

            # 41. HRC
            elif col_idx == 41:
                v = cn_hrc.get(rod_id)
                cell.value = v
                if v < 48.0:
                    cell.fill = fill_red
                    cell.font = font_red
                elif v < 50.0:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_green
                    cell.font = font_green

            # 42. Ra
            elif col_idx == 42:
                v = cn_ra.get(rod_id)
                cell.value = v
                if rod_id == 1:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_green
                    cell.font = font_green

            # 43. Steel Grade
            elif col_idx == 43:
                cell.value = "AISI 431 (Confirmed)" if lang=="EN" else "AISI 431 (Подтверждено)"
                cell.fill = fill_green
                cell.font = font_green

            # 44. NDT
            elif col_idx == 44:
                cell.value = "PASSED (No defects)" if lang=="EN" else "В порядке (без дефектов)"
                cell.fill = fill_green
                cell.font = font_green

            # 45. Chrome visual
            elif col_idx == 45:
                if rod_id in [7, 8]:
                    cell.value = "Excess thickness (to grind)" if lang=="EN" else "Избыток толщины (сошлифовать)"
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif rod_id == 3:
                    cell.value = "850 µm surge" if lang=="EN" else "Наплыв хрома 850 мкм"
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.value = "No blisters or pores" if lang=="EN" else "Без вздутий и пор"
                    cell.fill = fill_green
                    cell.font = font_green

            # 46. Chamfers
            elif col_idx == 46:
                cell.value = "Deburr edges" if lang=="EN" else "Притупить кромки"
                cell.fill = fill_rework
                cell.font = font_rework

            # 47. Video
            elif col_idx == 47:
                if b_val is not None:
                    cell.value = "Video available" if lang=="EN" else "Видеозапись имеется"
                    cell.fill = fill_green
                    cell.font = font_green
                else:
                    cell.value = "Record on video" if lang=="EN" else "Замерить на видео"
                    cell.fill = fill_white
                    cell.font = font_white

            # 48. Macro photo
            elif col_idx == 48:
                cell.value = "Macro photo required" if lang=="EN" else "Требуются макро-фото"
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 49. Inspector
            elif col_idx == 49:
                cell.value = "Factory: 汪秀玉 (Wang Xiuyu)"
                cell.fill = fill_yellow
                cell.font = font_yellow

            # 50-53. Verdicts
            elif col_idx == 50:
                cell.value = verdict
                if "PASS" in verdict or "ГОДЕН" in verdict:
                    cell.fill = fill_green
                    cell.font = font_green
                elif "REWORK" in verdict or "ПРИЕМКА ПОСЛЕ" in verdict:
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif "SCRAP" in verdict or "БРАК" in verdict:
                    cell.fill = fill_red
                    cell.font = font_red
                elif "CRITICAL" in verdict or "КРИТИЧЕСКАЯ" in verdict or "UNDERSIZE" in verdict:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
                else:
                    cell.fill = fill_white
                    cell.font = font_white
            elif col_idx == 51:
                cell.value = cond_txt
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif col_idx == 52:
                cell.value = act_txt
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif col_idx == 53:
                cell.value = notes_txt
                cell.alignment = Alignment(horizontal="left", vertical="center")

    # -------------------------------------------------------------
    # SHEET 2: CONDITIONS GUIDE
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="Client_5_Conditions_Guide" if lang=="EN" else "Справочник_5_условий_клиента")
    ws2.views.sheetView[0].showGridLines = True
    ws2.column_dimensions["A"].width = 14
    ws2.column_dimensions["B"].width = 30
    ws2.column_dimensions["C"].width = 35
    ws2.column_dimensions["D"].width = 50

    t2 = "GUIDE TO CLIENT 5 ACCEPTANCE & SALVAGE CONDITIONS" if lang=="EN" else "СПРАВОЧНИК КРИТЕРИЕВ И ПРАВИЛ ПРИЕМКИ КЛИЕНТА (С ДЕФЕКТОВКОЙ)"
    ws2.cell(1, 1, t2).font = font_title
    ws2.row_dimensions[1].height = 24

    h2 = ["Condition #", "Technical Criterion", "Strictness / Concession", "Acceptance & Salvage Regulation"] if lang=="EN" else ["№ Условия", "Критерий ТЗ", "Жесткость требования", "Регламент приемки / спасения"]
    for c_idx, h in enumerate(h2, start=1):
        c = ws2.cell(2, c_idx, h)
        c.font = font_header
        c.fill = fill_header_base
        c.border = border_header
        c.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[2].height = 22

    if lang == "EN":
        rules = [
            ("Condition 1", "Runout / Eccentricity", "CONCESSION AGREED UP TO 0.150 mm", "All rods with runout ≤ 0.150 mm are ACCEPTED. Salvaged: #4 (0.040), #5 (0.073), #6 (0.140), #9 (0.140), #10 (0.117), #11 (0.120), #14 (0.110), #16 (0.033). Rod #1 (0.170 mm) is SCRAPPED."),
            ("Condition 2", "Threads M170x4-6g", "STRICT SCRAP IF DAMAGED", "Inspection with GO and NO-GO thread ring gauges. NO-GO gauge MUST stop within 1.5–2 turns. Formal factory 'Pass' without NO-GO gauge is rejected!"),
            ("Condition 3", "Chrome Layer Thickness", "REWORK BY PRECISION GRINDING (>100 µm)", "Rods #7 (150 µm) and #8 (130 µm) accepted ONLY after precision machine grinding (strip 50 µm and 30 µm down to 100 µm). Manual grinding strictly forbidden! Rod #3 with 850 µm surge is scrap."),
            ("Condition 4", "Dimensions & Length", "STRICT SCRAP IF UNDERSIZED", "Dimensions smaller than drawing lower limit = strict scrap. Rods #3 (Ø171.45 < 171.50) and #15 (Ø179.55 < 179.804) scrapped. Rod #10 with 179.89 mm on ends requires re-checking!"),
            ("Condition 5", "Sealing Grooves & Grinding", "PAUSE ON 179.6 mm GRINDING!", "STOP GRINDING step to 179.6 mm until factory measures groove bottom internal diameter! Sealing manufacturer needs exact dimensions to calculate custom seals. Hand deburr groove edges with diamond file.")
        ]
    else:
        rules = [
            ("Условие 1", "Биение / эксцентриситет", "СОГЛАСОВАН ДОПУСК ДО 0,15 мм", "Все штоки с биением ≤ 0,150 мм переводятся в категорию ГОДНЫХ. Спасены №4 (0.040), №5 (0.073), №6 (0.140), №9 (0.140), №10 (0.117), №11 (0.120), №14 (0.110), №16 (0.033). Шток №1 (0.170 мм) — утиль."),
            ("Условие 2", "Резьба M170x4-6g", "БЕЗУСЛОВНЫЙ БРАК ПРИ ПОРЧЕ", "Проверка калибрами ПР и НЕ. Калибр НЕ не должен прокручиваться глубже 1.5–2 витков. Формальное '合格' завода без проверки НЕ отвергается!"),
            ("Условие 3", "Толщина хрома", "БРАК ЕСЛИ НЕ ИСПРАВЯТ (>100 мкм)", "Штоки №7 (150 мкм) и №8 (130 мкм) принимаются ТОЛЬКО при сошлифовке на круглошлифовальном станке (снять 50 и 30 мкм). Ручная шлифовка запрещена! Шток №3 с хромом 850 мкм — утиль."),
            ("Условие 4", "Геометрические размеры", "СТРОГИЙ БРАК ПРИ ЗАНИЖЕНИИ", "Размеры меньше допуска — немедленный брак. Шток №3 (Ø171.45 вместо 171.50) и №15 (Ø179.55 вместо 179.804) — утиль. Шток №10 с занижением до 179.89 мм на концах требует перепроверки!"),
            ("Условие 5", "Канавки и проточка до 179.6", "СТОПОР ШЛИФОВКИ ДО 179.6 мм!", "Запрещено шлифовать поясок до 179.6 мм до замера дна канавок заводом! Производителю уплотнений нужны точные данные дна канавок, иначе выдавит манжеты. Обязательна притирка кромок алмазным надфилем.")
        ]

    for r_idx, r in enumerate(rules, start=3):
        ws2.row_dimensions[r_idx].height = 26
        for c_idx, val in enumerate(r, start=1):
            cell = ws2.cell(r_idx, c_idx, val)
            cell.border = border_cell
            cell.font = font_data
            if c_idx == 1:
                cell.font = font_data_bold
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 3:
                cell.font = font_data_bold
                if "SCRAP" in val or "БРАК" in val or "СТОПОР" in val or "PAUSE" in val:
                    cell.fill = fill_red
                    cell.font = font_red
                elif "CONCESSION" in val or "СОГЛАСОВАН" in val:
                    cell.fill = fill_green
                    cell.font = font_green
                else:
                    cell.fill = fill_rework
                    cell.font = font_rework

    # -------------------------------------------------------------
    # SHEET 3: FINAL SORTING & DISPATCH
    # -------------------------------------------------------------
    ws3 = wb.create_sheet(title="Final_Sorting_and_Dispatch" if lang=="EN" else "Итоговая_сортировка_штоков")
    ws3.views.sheetView[0].showGridLines = True
    ws3.column_dimensions["A"].width = 25
    ws3.column_dimensions["B"].width = 18
    ws3.column_dimensions["C"].width = 20
    ws3.column_dimensions["D"].width = 50

    t3 = "FINAL STATUS OF 16 PISTON RODS (BATCH OF 28.09.2026)" if lang=="EN" else "ИТОГОВЫЙ СТАТУС ПАРТИИ 16 ШТОКОВ НА 28.09.2026"
    ws3.cell(1, 1, t3).font = font_title
    ws3.row_dimensions[1].height = 24

    h3 = ["Readiness Category", "Quantity", "Rod Numbers", "Mandatory Action Before Shipment"] if lang=="EN" else ["Категория готовности", "Кол-во (шт)", "Номера штоков", "Требуемые действия до отгрузки"]
    for c_idx, h in enumerate(h3, start=1):
        cell = ws3.cell(2, c_idx, h)
        cell.font = font_header
        cell.fill = fill_header_base
        cell.border = border_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws3.row_dimensions[2].height = 22

    if lang == "EN":
        sort_data = [
            ("🟢 READY FOR SHIPMENT (Urgent)", "5 pcs", "# 4, 5, 11, 14, 16", "Confirm thread with NO-GO gauge (stop ≤1.5..2 turns), measure groove bottom ID, deburr edges with diamond file, ship."),
            ("🟢 READY PENDING THREAD/OD", "1 pc", "# 2", "Check runout in centers and verify thread with NO-GO gauge. Confirm Ø180 with micrometer."),
            ("⚠️ CRITICAL THREAD RE-CHECK", "2 pcs", "# 6, # 9", "Runout is PASS (0.140 ≤ 0.15). Crucial factor is NO-GO gauge M170x4-6g. On #9 confirm groove width 9.10 mm."),
            ("🔄 REWORK: CHROME GRINDING", "2 pcs", "# 7, # 8", "Precision machine grinding: strip 50 µm (#7) and 30 µm (#8) to 100 µm spec. Manual grinding STRICTLY FORBIDDEN."),
            ("⚠️ SUSPECTED UNDERSIZED OD", "1 pc", "# 10", "Runout 0.117 is PASS. Factory admitted 179.89 mm on 300mm ends. Re-measure with micrometer!"),
            ("⚪ PENDING RUNOUT CHECK", "2 pcs", "# 12, # 13", "Measure runout in centers at 5 points, test thread with NO-GO gauge, measure groove bottom ID."),
            ("❌ CONFIRMED SCRAP", "3 pcs", "# 1, # 3, # 15", "#1: Runout 0.170 > 0.15 & HRC 45.8. #3: Ø171.45 under tolerance & chrome 850 µm surge. #15: Step Ø179.55 (-0.25 mm). Refund / remake.")
        ]
    else:
        sort_data = [
            ("🟢 ГОДНЫ К СДАЧЕ (Срочно)", "5 шт", "№ 4, 5, 11, 14, 16", "Перепроверить резьбы калибром НЕ (останов ≤1.5..2 витка), замерить дно канавок, притереть кромки надфилем, отгружать."),
            ("🟢 ГОДЕН ПРИ ПРОВЕРКЕ РЕЗЬБЫ", "1 шт", "№ 2", "Замерить биение в центрах, проверить резьбу калибром НЕ. Подтвердить Ø180 микрометром."),
            ("⚠️ КРИТИЧЕСКАЯ РЕЗЬБА", "2 шт", "№ 6, № 9", "Биение в норме (0.140 ≤ 0.15). Решающий фактор — калибр НЕ M170x4-6g. На №9 согласовать ширину канавки 9.10 мм."),
            ("🔄 ДОРАБОТКА (ХРОМ)", "2 шт", "№ 7, № 8", "Сошлифовать 50 мкм (№7) и 30 мкм (№8) на круглошлифовальном станке до слоя 100 мкм. Ручная шлифовка ЗАПРЕЩЕНА."),
            ("⚠️ ПОД СОМНЕНИЕМ (Ø НА КОНЦАХ)", "1 шт", "№ 10", "Биение 0.117 в норме. Завод признал занижение до 179.89 мм на концах 300 мм — перемерить микрометром!"),
            ("⚪ ОЖИДАЮТ ЗАМЕРА", "2 шт", "№ 12, № 13", "Замерить биение в центрах по 5 точкам, проверить резьбу калибром НЕ, замерить дно канавок."),
            ("❌ ОКОНЧАТЕЛЬНЫЙ БРАК", "3 шт", "№ 1, № 3, № 15", "№1: биение 0.170 > 0.15 и HRC 45.8. №3: Ø171.45 (-0.05 мм меньше нормы) и наплыв 850 мкм. №15: поясок Ø179.55 (-0.25 мм). Возврат денег / переделка.")
        ]

    for r_idx, r in enumerate(sort_data, start=3):
        ws3.row_dimensions[r_idx].height = 30
        for c_idx, val in enumerate(r, start=1):
            cell = ws3.cell(r_idx, c_idx, val)
            cell.border = border_cell
            cell.font = font_data
            if c_idx == 1:
                cell.font = font_data_bold
                if "READY" in val or "ГОДН" in val:
                    cell.fill = fill_green
                    cell.font = font_green
                elif "REWORK" in val or "ДОРАБОТКА" in val:
                    cell.fill = fill_rework
                    cell.font = font_rework
                elif "SCRAP" in val or "БРАК" in val:
                    cell.fill = fill_red
                    cell.font = font_red
                else:
                    cell.fill = fill_yellow
                    cell.font = font_yellow
            elif c_idx in [2, 3]:
                cell.font = font_data_bold
                cell.alignment = Alignment(horizontal="center", vertical="center")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        wb.save(output_path)
        print(f"Successfully saved: {output_path}")
    except PermissionError:
        alt = output_path.replace(".xlsx", "_v2_актуальная.xlsx")
        wb.save(alt)
        print(f"Locked file saved to alt: {alt}")

def main():
    p_ru_proj = r"C:\Codex\projects\Price creating\Договор_62230426_Штоки_и_Трубы\Таблица_проверки_штоков_16шт.xlsx"
    p_ru_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\Таблица_проверки_штоков_16шт.xlsx"
    p_ru_dl_v2 = r"C:\Users\Артем\Downloads\ТЗ для гравити\Таблица_проверки_штоков_16шт_v2_актуальная.xlsx"
    p_ru_proj_v2 = r"C:\Codex\projects\Price creating\Договор_62230426_Штоки_и_Трубы\Таблица_проверки_штоков_16шт_v2_актуальная.xlsx"
    
    p_en_proj = r"C:\Codex\projects\Price creating\Договор_62230426_Штоки_и_Трубы\Таблица_проверки_штоков_16шт_EN.xlsx"
    p_en_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\Таблица_проверки_штоков_16шт_EN.xlsx"

    print("--- GENERATING RUSSIAN MATRIX ---")
    generate_workbook("RU", p_ru_proj)
    generate_workbook("RU", p_ru_dl)
    generate_workbook("RU", p_ru_dl_v2)
    generate_workbook("RU", p_ru_proj_v2)

    print("\n--- GENERATING ENGLISH MATRIX ---")
    generate_workbook("EN", p_en_proj)
    generate_workbook("EN", p_en_dl)

if __name__ == "__main__":
    main()
