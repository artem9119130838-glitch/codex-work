# -*- coding: utf-8 -*-
"""
Генерация официального документа для клиента:
Программа и сметный расчет независимой предотгрузочной инспекции и лабораторных испытаний SGS
(Штоки гидроцилиндров и хонингованные трубы)
С наценкой +30%, без прямых контактов китайского офиса SGS и китайских контрагентов.
"""

import os
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_border(cell, **kwargs):
    """Настройка границ ячейки таблицы."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key, val in edge_data.items():
                element.set(qn(f'w:{key}'), str(val))

def set_cell_background(cell, hex_color):
    """Заливка ячейки фоновым цветом."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Установка внутренних отступов ячейки."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_para(p, font_name='Calibri', size=11, bold=False, italic=False, color=RGBColor(0x22, 0x22, 0x22), align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.15):
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    for r in p.runs:
        r.font.name = font_name
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color

def add_styled_para(doc, text, font_name='Calibri', size=11, bold=False, italic=False, color=RGBColor(0x22, 0x22, 0x22), align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=4, line_spacing=1.15):
    p = doc.add_paragraph()
    p.add_run(text)
    set_para(p, font_name, size, bold, italic, color, align, space_before, space_after, line_spacing)
    return p

def main():
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    out_path = os.path.join(desktop, 'Программа_и_смета_инспекции_SGS_Штоки_и_Трубы.docx')

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    # ------------------ ШАПКА ДОКУМЕНТА ------------------
    add_styled_para(doc, "ПРОГРАММА И СМЕТНЫЙ РАСЧЕТ", size=15, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc, "НЕЗАВИСИМОЙ ПРЕДОТГРУЗОЧНОЙ ИНСПЕКЦИИ И ЛАБОРАТОРНЫХ ИСПЫТАНИЙ (SGS INDUSTRIAL SERVICES)", size=12, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_styled_para(doc, "по договору поставки элементов гидроцилиндров (партия штоков поршня и хонингованных труб)", size=10.5, italic=True, color=RGBColor(0x55, 0x55, 0x55), align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

    # Метаданные документа
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    
    meta_info = [
        ("Инспекционный орган / Лаборатория:", "SGS (Société Générale de Surveillance, Industrial Services)"),
        ("Основание для инспекции:", "Программа входного/выходного контроля партии металлоизделий перед отгрузкой из КНР"),
        ("Форма и статус итогового документа:", "Официальный сертификационный инспекционный отчет SGS (Inspection Report) на английском языке с верификацией QR-кодом"),
        ("Дата актуализации программы:", "Ноябрь 2026 г.")
    ]
    for idx, (k, v) in enumerate(meta_info):
        c0 = meta_table.cell(idx, 0)
        c1 = meta_table.cell(idx, 1)
        c0.width = Inches(2.5)
        c1.width = Inches(4.5)
        c0.paragraphs[0].text = k
        set_para(c0.paragraphs[0], size=9.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D))
        c1.paragraphs[0].text = v
        set_para(c1.paragraphs[0], size=9.5, bold=False)
        set_cell_background(c0, "F4F6F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 60, 60, 100, 100)
        set_cell_margins(c1, 60, 60, 100, 100)
        set_cell_border(c0, top=dict(val='single', sz=4, color='D0D7DE'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
        set_cell_border(c1, top=dict(val='single', sz=4, color='D0D7DE'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ РАЗДЕЛ 1. ОБЪЕКТЫ КОНТРОЛЯ ------------------
    add_styled_para(doc, "1. ОБЪЕКТЫ КОНТРОЛЯ И ПРОИЗВОДСТВЕННЫЕ ПЛОЩАДКИ", size=11.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), space_after=4)
    add_styled_para(doc, "Инспекционный аудит проводится с выездом сертифицированных инженеров-инспекторов и специалистов неразрушающего контроля (NDT Level II) на две специализированные производственные площадки в Китайской Народной Республике:", space_after=6)

    obj_table = doc.add_table(rows=4, cols=5)
    obj_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    obj_table.autofit = False

    obj_headers = ["Лот", "Наименование изделия", "Технические характеристики / Габариты", "Кол-во", "Локация инспекции"]
    col_widths = [Inches(0.6), Inches(2.0), Inches(2.4), Inches(0.7), Inches(1.3)]

    for i, h in enumerate(obj_headers):
        cell = obj_table.cell(0, i)
        cell.width = col_widths[i]
        cell.paragraphs[0].text = h
        set_para(cell.paragraphs[0], size=9, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 80, 80, 80, 80)
        set_cell_border(cell, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=6, color='1B365D'), left=dict(val='none'), right=dict(val='none'))

    obj_data = [
        ("Лот 1", "Штоки гидроцилиндров с хромовым покрытием", "Ø180 f7 × 2574 мм, сталь AISI 431, посадочные шейки и канавки под уплотнения", "16 шт.", "г. Чанчжоу (провинция Цзянсу)"),
        ("Лот 2.1", "Гильзы гидроцилиндров хонингованные (тип 1)", "Ø500 × Ø420 × 2174 мм (допуск 2174–2177 мм, гладкий торец), сталь Q345B", "16 шт.", "г. Лиочэн (провинция Шаньдун)"),
        ("Лот 2.2", "Трубы цилиндровые (тип 2, наружный кожух)", "Ø500 × Ø420 × 1707 мм (8 шт. без фаски + 8 шт. с разделкой кромок 36×45°)", "16 шт.", "г. Лиочэн (провинция Шаньдун)")
    ]

    for r_idx, row in enumerate(obj_data, start=1):
        bg = "FFFFFF" if r_idx % 2 != 0 else "F9FAFC"
        for c_idx, val in enumerate(row):
            cell = obj_table.cell(r_idx, c_idx)
            cell.width = col_widths[c_idx]
            cell.paragraphs[0].text = val
            al = WD_ALIGN_PARAGRAPH.CENTER if c_idx in (0, 3, 4) else WD_ALIGN_PARAGRAPH.LEFT
            set_para(cell.paragraphs[0], size=8.5, bold=(c_idx == 0), align=al)
            set_cell_background(cell, bg)
            set_cell_margins(cell, 60, 60, 80, 80)
            set_cell_border(cell, top=dict(val='single', sz=4, color='E1E4E8'), bottom=dict(val='single', sz=4, color='E1E4E8'), left=dict(val='none'), right=dict(val='none'))

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ РАЗДЕЛ 2. ПЕРЕЧЕНЬ ПРОВОДИМЫХ РАБОТ ------------------
    add_styled_para(doc, "2. ДЕТАЛИЗИРОВАННЫЙ ОБЪЕМ ИСПЫТАНИЙ И ПРОВЕРОК", size=11.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), space_after=4)
    add_styled_para(doc, "Программа инспекции SGS включает в себя комплекс неразрушающего контроля (NDT), инструментальных высокоточных замеров и независимых разрушающих лабораторных испытаний:", space_after=6)

    scope_points = [
        ("1. Сплошной 100% визуальный и поверхностный контроль (Visual & Surface Inspection):",
         "Проверка 100% изделий на отсутствие задиров, рисок, коррозии, трещин, пор, механических повреждений и дефектов хромирования. Проверка качества защитной заводской консервации и деревянной упаковки перед погрузкой."),
        
        ("2. Инструментальный геометрический контроль (Dimensional Inspection):",
         "• Для штоков: замер наружного диаметра Ø180 f7 микрометром в нескольких сечениях; измерение диаметров посадочных поясков Ø179.9 мм, шеек под уплотнения Ø171.6 мм, ширины канавок (8.60+0.15 мм) и общей длины 2574 мм.\n"
         "• Для труб: контроль наружного диаметра Ø500 мм (+1.0/-0.5 мм), внутреннего рабочего диаметра Ø420 мм (квалитет H9) с оценкой овальности и конусности, общей длины и геометрии фасок 36×45° под сварку."),
        
        ("3. Ультразвуковая толщинометрия и контроль разностенности (Wall Thickness Check):",
         "100% инструментальный замер толщины стенки труб (номинал 40 мм) в 8 контрольных сечениях по длине для подтверждения допустимого эксцентриситета (разностенность не более 7–8%)."),

        ("4. Инструментальный контроль биения / прямолинейности штоков (Runout Verification):",
         "Установка каждого штока в центрах (люнетах) с замером радиального биения часовыми индикаторами в 5 сечениях по длине изделия под контролем инспектора."),

        ("5. Замер толщины защитного хромового покрытия (Coating Thickness Measurement):",
         "Инструментальный замер толщины хрома электромагнитным/вихретоковым толщиномером SGS (требование: 100–120 мкм) по всей рабочей длине штока."),

        ("6. Инструментальный экспресс-анализ сплава (PMI — Positive Material Identification):",
         "100% инструментальная спектрометрия сертифицированным переносным XRF-спектрометром SGS для гарантированного подтверждения соответствия марки стали химическому паспорту."),

        ("7. Независимый ультразвуковой контроль сплошности металла (UT Inspection):",
         "Проведение УЗК силами сертифицированного дефектоскописта SGS по международному стандарту EN 10228-3 (неразрушающий контроль стальных поковок и бесшовных труб) с целью выявления внутренних несплошностей, расслоений, неметаллических включений и микротрещин тела металла (объем: 20% для штоков, 10% для труб)."),

        ("8. Лабораторные разрушающие испытания образцов в лаборатории SGS (Lab Testing):",
         "• Спектральный количественный химический анализ (C, Si, Mn, P, S, Cr, Ni) в аккредитованной лаборатории SGS.\n"
         "• Механические испытания на растяжение: определение фактического предела текучести (σт) и временного сопротивления (предел прочности σв).\n"
         "• Выпуск официального заключения SGS о соответствии материала требуемому марочному составу и механическим свойствам.")
    ]

    for title, desc in scope_points:
        p = doc.add_paragraph()
        r1 = p.add_run(title + " ")
        r1.font.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        r2 = p.add_run(desc)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9.5)
        set_para(p, size=9.5, space_before=1, space_after=3)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ------------------ РАЗДЕЛ 3. СМЕТНЫЙ РАСЧЕТ СТОИМОСТИ ------------------
    add_styled_para(doc, "3. СМЕТНЫЙ РАСЧЕТ СТОИМОСТИ ИНСПЕКЦИИ И ЛАБОРАТОРНЫХ РАБОТ", size=11.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), space_after=4)
    add_styled_para(doc, "Стоимость сформирована на основании официальных инспекционных тарифов SGS Industrial Services с учетом выезда профильных инженеров, аренды поверенных диагностических комплексов, проведения лабораторных испытаний и оформления отчетов с международной верификацией:", space_after=6)

    # Данные таблицы (+30%)
    price_rows = [
        # Раздел 1: Штоки
        ("РАЗДЕЛ I. ИНСПЕКЦИЯ ШТОКОВ ГИДРОЦИЛИНДРОВ (г. Чанчжоу)", "", "", "", "HEADER"),
        ("1.1", "Выездная инспекция эксперта QA/QC (геометрия, визуальный контроль, биение, хром, упаковка)", "чел.-день", "2,0", "9 100,00"),
        ("1.2", "Использование переносного спектрометра PMI (экспресс-анализ марки стали)", "комплект", "1,0", "3 900,00"),
        ("1.3", "Ультразвуковой контроль металла по стандарту EN 10228-3 (сертифицированный инженер УЗК)", "комплекс", "1,0", "5 850,00"),
        ("1.4", "Лабораторный химический анализ сплава в аккредитованной лаборатории SGS", "протокол", "1,0", "910,00"),
        ("1.5", "Лабораторные механические испытания на растяжение (предел текучести/прочности)", "протокол", "1,0", "429,00"),
        ("1.6", "Экспертное заключение SGS о марочном соответствии стали", "заключение", "1,0", "260,00"),
        ("ИТОГО ПО РАЗДЕЛУ I (Штоки поршня):", "", "", "", "20 449,00"),
        
        # Раздел 2: Трубы
        ("РАЗДЕЛ II. ИНСПЕКЦИЯ ТРУБ И ГИЛЬЗ ГИДРОЦИЛИНДРОВ (г. Лиочэн)", "", "", "", "HEADER"),
        ("2.1", "Выездная инспекция эксперта QA/QC (геометрия Ø420/Ø500, толщинометрия, фаски, чистота зеркала)", "чел.-день", "3,0", "13 650,00"),
        ("2.2", "Использование переносного спектрометра PMI (экспресс-анализ марки стали)", "комплект", "1,0", "3 900,00"),
        ("2.3", "Ультразвуковой контроль металла по стандарту EN 10228-3 (сертифицированный инженер УЗК)", "комплекс", "1,0", "5 850,00"),
        ("2.4", "Лабораторный химический анализ образца стали в аккредитованной лаборатории SGS", "протокол", "1,0", "910,00"),
        ("2.5", "Лабораторные механические испытания на растяжение (предел текучести/прочности)", "протокол", "1,0", "429,00"),
        ("2.6", "Экспертное заключение SGS о соответствии стали марке Q345B", "заключение", "1,0", "260,00"),
        ("ИТОГО ПО РАЗДЕЛУ II (Хонингованные трубы и гильзы):", "", "", "", "24 999,00"),

        # Итоговая сводка
        ("ИТОГО СТОИМОСТЬ УСЛУГ (БЕЗ НДС):", "", "", "", "45 448,00"),
        ("ИТОГО К ОПЛАТЕ С УЧЕТОМ НДС (6%):", "", "", "", "48 174,88")
    ]

    price_table = doc.add_table(rows=len(price_rows) + 1, cols=5)
    price_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    price_table.autofit = False

    p_headers = ["№", "Наименование услуги / Вид контроля", "Ед. изм.", "Кол-во", "Стоимость (CNY)"]
    p_widths = [Inches(0.5), Inches(3.7), Inches(0.9), Inches(0.7), Inches(1.2)]

    for i, h in enumerate(p_headers):
        cell = price_table.cell(0, i)
        cell.width = p_widths[i]
        cell.paragraphs[0].text = h
        set_para(cell.paragraphs[0], size=9, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, 70, 70, 80, 80)
        set_cell_border(cell, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=6, color='1B365D'), left=dict(val='none'), right=dict(val='none'))

    for r_idx, row in enumerate(price_rows, start=1):
        cell_type = row[4]
        c0 = price_table.cell(r_idx, 0)
        c1 = price_table.cell(r_idx, 1)
        c2 = price_table.cell(r_idx, 2)
        c3 = price_table.cell(r_idx, 3)
        c4 = price_table.cell(r_idx, 4)

        for ci, w in enumerate(p_widths):
            price_table.cell(r_idx, ci).width = w

        if cell_type == "HEADER":
            c0.merge(c4)
            c0.paragraphs[0].text = row[0]
            set_para(c0.paragraphs[0], size=9, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_background(c0, "EAEEF3")
            set_cell_margins(c0, 60, 60, 80, 80)
            set_cell_border(c0, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
        elif "ИТОГО ПО РАЗДЕЛУ" in row[0]:
            c0.merge(c3)
            c0.paragraphs[0].text = row[0]
            set_para(c0.paragraphs[0], size=9, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.RIGHT)
            c4.paragraphs[0].text = row[4]
            set_para(c4.paragraphs[0], size=9, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.RIGHT)
            set_cell_background(c0, "F4F6F9")
            set_cell_background(c4, "F4F6F9")
            set_cell_margins(c0, 60, 60, 80, 80)
            set_cell_margins(c4, 60, 60, 80, 80)
            set_cell_border(c0, top=dict(val='single', sz=4, color='D0D7DE'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
            set_cell_border(c4, top=dict(val='single', sz=4, color='D0D7DE'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
        elif "ИТОГО СТОИМОСТЬ УСЛУГ (БЕЗ НДС)" in row[0]:
            c0.merge(c3)
            c0.paragraphs[0].text = row[0]
            set_para(c0.paragraphs[0], size=9.5, bold=True, color=RGBColor(0x22, 0x22, 0x22), align=WD_ALIGN_PARAGRAPH.RIGHT)
            c4.paragraphs[0].text = row[4]
            set_para(c4.paragraphs[0], size=9.5, bold=True, color=RGBColor(0x22, 0x22, 0x22), align=WD_ALIGN_PARAGRAPH.RIGHT)
            set_cell_background(c0, "E9EDF2")
            set_cell_background(c4, "E9EDF2")
            set_cell_margins(c0, 60, 60, 80, 80)
            set_cell_margins(c4, 60, 60, 80, 80)
            set_cell_border(c0, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
            set_cell_border(c4, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=4, color='D0D7DE'), left=dict(val='none'), right=dict(val='none'))
        elif "ИТОГО К ОПЛАТЕ" in row[0]:
            c0.merge(c3)
            c0.paragraphs[0].text = row[0]
            set_para(c0.paragraphs[0], size=10, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.RIGHT)
            c4.paragraphs[0].text = row[4]
            set_para(c4.paragraphs[0], size=10, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), align=WD_ALIGN_PARAGRAPH.RIGHT)
            set_cell_background(c0, "D5DFEC")
            set_cell_background(c4, "D5DFEC")
            set_cell_margins(c0, 80, 80, 80, 80)
            set_cell_margins(c4, 80, 80, 80, 80)
            set_cell_border(c0, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=8, color='1B365D'), left=dict(val='none'), right=dict(val='none'))
            set_cell_border(c4, top=dict(val='single', sz=6, color='1B365D'), bottom=dict(val='single', sz=8, color='1B365D'), left=dict(val='none'), right=dict(val='none'))
        else:
            c0.paragraphs[0].text = row[0]
            c1.paragraphs[0].text = row[1]
            c2.paragraphs[0].text = row[2]
            c3.paragraphs[0].text = row[3]
            c4.paragraphs[0].text = row[4]
            set_para(c0.paragraphs[0], size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
            set_para(c1.paragraphs[0], size=8.5, align=WD_ALIGN_PARAGRAPH.LEFT)
            set_para(c2.paragraphs[0], size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
            set_para(c3.paragraphs[0], size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER)
            set_para(c4.paragraphs[0], size=8.5, align=WD_ALIGN_PARAGRAPH.RIGHT)
            bg = "FFFFFF" if r_idx % 2 != 0 else "F9FAFC"
            for cell_item in (c0, c1, c2, c3, c4):
                set_cell_background(cell_item, bg)
                set_cell_margins(cell_item, 50, 50, 70, 70)
                set_cell_border(cell_item, top=dict(val='single', sz=4, color='E1E4E8'), bottom=dict(val='single', sz=4, color='E1E4E8'), left=dict(val='none'), right=dict(val='none'))

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Примечание о рублевом эквиваленте
    p_eq = doc.add_paragraph()
    r_eq = p_eq.add_run("Справочно: Расчет в рублях производится по курсу ЦБ РФ + 2% на день выставления счета (ориентировочно 650 000 – 675 000 руб. с учетом НДС за полный аудит двух заводов и лабораторные комплексы).")
    r_eq.font.italic = True
    r_eq.font.size = Pt(8.5)
    r_eq.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    set_para(p_eq, size=8.5, italic=True, space_after=10)

    # ------------------ РАЗДЕЛ 4. СРОКИ И ПОРЯДОК ОРГАНИЗАЦИИ ------------------
    add_styled_para(doc, "4. СРОКИ, УСЛОВИЯ ПРОВЕДЕНИЯ И ВЫПУСКА РЕЗУЛЬТАТОВ", size=11.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D), space_after=4)
    
    terms_list = [
        ("Период проведения выездной инспекции:", "Ноябрь 2026 г. Точные даты выезда согласовываются за 3–5 рабочих дней после получения официального видео-отчета завода о 100% готовности изделий к предъявлению."),
        ("Продолжительность выездных работ:", "• Штоки (г. Чанчжоу): 2 рабочих дня (16 человеко-часов работы инспекторов).\n• Трубы (г. Лиочэн): 3 рабочих дня (24 человеко-часа работы инспекторов)."),
        ("Сроки лабораторных разрушающих испытаний:", "Отбор образцов осуществляется инспектором на заводе в день инспекции. Срок проведения химического анализа и испытаний на растяжение в аккредитованной лаборатории SGS составляет 3–5 рабочих дней с момента доставки образцов в испытательный центр."),
        ("Срок предоставления официального отчета SGS:", "Предварительный акт визуально-измерительного контроля передается в электронном виде в течение 24 часов после завершения выезда. Итоговый сертификационный отчет SGS Inspection Report с протоколами УЗК и лабораторными заключениями выпускается в течение 5–7 рабочих дней."),
        ("Особые технические требования к заводам:", "Заводы обязаны обеспечить свободный круговой доступ к каждому изделию, крановые операции для кантования, токарный станок/люнеты для замера биения штоков, а также калибровочные блоки и специализированный глубокий нутромер для контроля внутреннего зеркала труб.")
    ]

    for label, val in terms_list:
        p = doc.add_paragraph()
        r1 = p.add_run(label + " ")
        r1.font.bold = True
        r1.font.name = 'Calibri'
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
        r2 = p.add_run(val)
        r2.font.name = 'Calibri'
        r2.font.size = Pt(9.5)
        set_para(p, size=9.5, space_before=1, space_after=3)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Блок согласования
    sign_table = doc.add_table(rows=2, cols=2)
    sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sign_table.autofit = False

    s_lh = sign_table.cell(0, 0)
    s_rh = sign_table.cell(0, 1)
    s_lh.width = Inches(3.5)
    s_rh.width = Inches(3.5)
    s_lh.paragraphs[0].text = "СОГЛАСОВАНО ОТ ЗАКАЗЧИКА:"
    set_para(s_lh.paragraphs[0], size=9.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D))
    s_rh.paragraphs[0].text = "ИСПОЛНИТЕЛЬ / КООРДИНАТОР ИНСПЕКЦИИ:"
    set_para(s_rh.paragraphs[0], size=9.5, bold=True, color=RGBColor(0x1B, 0x36, 0x5D))

    s_lb = sign_table.cell(1, 0)
    s_rb = sign_table.cell(1, 1)
    s_lb.width = Inches(3.5)
    s_rb.width = Inches(3.5)
    s_lb.paragraphs[0].text = "\n\n_____________________ / __________________ /\n«___» ______________ 2026 г.\nМ.П."
    set_para(s_lb.paragraphs[0], size=9.5)
    s_rb.paragraphs[0].text = "\n\n_____________________ / __________________ /\n«___» ______________ 2026 г.\nМ.П."
    set_para(s_rb.paragraphs[0], size=9.5)

    doc.save(out_path)
    print(f"SUCCESS: Document successfully created at: {out_path}")

if __name__ == '__main__':
    main()
