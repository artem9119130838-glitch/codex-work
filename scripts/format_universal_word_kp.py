#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/format_universal_word_kp.py
===================================
Канонический универсальный генератор и форматировщик коммерческих предложений
в формате Microsoft Word (DOCX) и PDF (Universal Word Commercial Proposal Engine).

Ключевые инварианты:
  1. Universal Header Table Invariant:
     - Шапка оформляется строго через таблицу шириной 100% (w:tblW type="pct" w:w="5000")
       без границ внутри верхнего колонтитула (w:headerReference).
     - Левая ячейка: Inline-логотип компании (wp:inline, без жестких абсолютных координат).
     - Правая ячейка: Контакты, юрлицо и ИНН/КПП с выравниванием по правому краю.
     - Адаптивность: при переключении Landscape (29.7 см) ⮂ Portrait (21.0 см) шапка
       автоматически плавно масштабируется без искажений и смещений.
  2. Multi-Page Header Guard (Защита от наезда шапки на таблицу):
     - Отступ колонтитула от края листа: 0.6 см.
     - Верхнее поле начала текста: 3.1 см (гарантирует чистый 0.8 см интервал над таблицей).
     - На первой строке таблицы включен w:tblHeader (автоповтор шапки колонок на стр. 2+).
     - На всех строках таблицы включен w:cantSplit (запрет разрыва строк поперек листа).
  3. Single-Section Clean Layout:
     - Запрещены скрытые паразитные разрывы разделов (w:sectPr continuous/nextPage).
     - Весь документ удерживается в едином разделе.
  4. Block-Level Terms & Signature Table:
     - Условия поставки (слева) и подпись с синей печатью (справа) объединены в двухколоночный
       невидимый блок, исключающий наложение печати на текст.
"""

import os
import sys
import argparse
import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def format_universal_kp(
    input_docx: str,
    output_docx: str,
    output_pdf: str = None,
    orientation: str = "landscape",
    logo_path: str = None,
    stamp_path: str = None
):
    print(f"[*] Сборка универсального КП ({orientation}) из {input_docx} -> {output_docx}...")
    
    src_doc = docx.Document(input_docx)
    
    # Извлечение данных из исходного документа
    table_data = []
    # Ищем таблицу товаров (самая большая по числу строк)
    target_table = None
    for tbl in src_doc.tables:
        if len(tbl.rows) > 3:
            target_table = tbl
            break
            
    if target_table:
        for r in target_table.rows:
            table_data.append([c.text.strip() for c in r.cells])
            
    # Заголовок и заказчик
    title_text = "Коммерческое предложение № 117/26 от 22.10.2026"
    client_text = "Баренцкул (сборный) фильтры и датчики 21-10"
    for p in src_doc.paragraphs:
        if "коммерческое предложение" in p.text.lower():
            title_text = p.text.strip()
        elif "заказчик:" in p.text.lower():
            client_text = p.text.replace("Заказчик:", "").replace("заказчик:", "").strip()

    # Новый чистый документ
    doc = docx.Document()
    sec = doc.sections[0]
    
    if orientation.lower() == "landscape":
        sec.orientation = docx.enum.section.WD_ORIENT.LANDSCAPE
        sec.page_width = Cm(29.7)
        sec.page_height = Cm(21.0)
        content_width_cm = 28.1
        sec.left_margin = Cm(0.8)
        sec.right_margin = Cm(0.8)
        sec.top_margin = Cm(3.1)
        sec.bottom_margin = Cm(0.7)
        sec.header_distance = Cm(0.6)
        sec.footer_distance = Cm(0.4)
        col_widths_dxa = [500, 3500, 2100, 1450, 900, 1400, 1500, 4580]
    else:
        sec.orientation = docx.enum.section.WD_ORIENT.PORTRAIT
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        content_width_cm = 19.4
        sec.left_margin = Cm(0.8)
        sec.right_margin = Cm(0.8)
        sec.top_margin = Cm(3.1)
        sec.bottom_margin = Cm(0.8)
        sec.header_distance = Cm(0.6)
        sec.footer_distance = Cm(0.4)
        col_widths_dxa = [450, 2500, 1450, 1050, 650, 1050, 1150, 2700]

    # 1. КОЛОНТИТУЛ: Таблица 100% ширины без рамок
    hdr = sec.header
    hdr.paragraphs[0].text = ""
    hdr_tbl = hdr.add_table(rows=1, cols=2, width=Inches(content_width_cm / 2.54))
    hdr_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    tblPr = hdr_tbl._element.xpath('w:tblPr')
    if tblPr:
        tblW = OxmlElement('w:tblW')
        tblW.set(qn('w:w'), '5000')
        tblW.set(qn('w:type'), 'pct')
        tblPr[0].append(tblW)
        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
            f'<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(tblBorders)

    # Левая ячейка: Логотип
    cell_l = hdr_tbl.cell(0, 0)
    cell_l.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_l = cell_l.paragraphs[0]
    p_l.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_l.paragraph_format.space_before = Pt(0)
    p_l.paragraph_format.space_after = Pt(0)
    if logo_path and os.path.exists(logo_path):
        p_l.add_run().add_picture(logo_path, width=Cm(1.8), height=Cm(1.8))

    # Правая ячейка: Контакты и ИНН
    cell_r = hdr_tbl.cell(0, 1)
    cell_r.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_r = cell_r.paragraphs[0]
    p_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_r.paragraph_format.space_before = Pt(0)
    p_r.paragraph_format.space_after = Pt(0)
    p_r.paragraph_format.line_spacing = Pt(11.0)

    r1 = p_r.add_run("Long Wang LLC\n")
    r1.font.name = "Calibri"
    r1.font.size = Pt(10.5)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(31, 73, 125)

    r2 = p_r.add_run("E-mail: sales@longwang.ru | longwang.ru\n")
    r2.font.name = "Calibri"
    r2.font.size = Pt(8.5)
    r2.font.color.rgb = RGBColor(0, 112, 192)

    r3 = p_r.add_run("Исполнитель: ООО \"ЦИ ЛИНЬ\" | ")
    r3.font.name = "Calibri"
    r3.font.size = Pt(8.5)
    r3.font.bold = True

    r4 = p_r.add_run("ИНН 7801719960, КПП 780101001")
    r4.font.name = "Calibri"
    r4.font.size = Pt(8.5)
    r4.font.color.rgb = RGBColor(89, 89, 89)

    # 2. ТЕЛО: Заголовок и Заказчик
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(1)
    rt = p_t.add_run(title_text)
    rt.font.name = "Calibri"
    rt.font.size = Pt(11.5)
    rt.font.bold = True

    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_c.paragraph_format.space_before = Pt(0)
    p_c.paragraph_format.space_after = Pt(3)
    rc1 = p_c.add_run("Заказчик: ")
    rc1.font.name = "Calibri"
    rc1.font.size = Pt(9.5)
    rc1.font.bold = True
    rc2 = p_c.add_run(client_text)
    rc2.font.name = "Calibri"
    rc2.font.size = Pt(9.5)

    # 3. ТАБЛИЦА ТОВАРОВ
    if table_data:
        tbl = doc.add_table(rows=len(table_data), cols=len(table_data[0]))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        tpr = tbl._element.xpath('w:tblPr')
        if tpr:
            tw = OxmlElement('w:tblW')
            tw.set(qn('w:w'), '5000')
            tw.set(qn('w:type'), 'pct')
            tpr[0].append(tw)
            
            tmar = parse_xml(
                f'<w:tblCellMar {nsdecls("w")}>'
                f'<w:top w:w="18" w:type="dxa"/><w:bottom w:w="18" w:type="dxa"/>'
                f'<w:left w:w="40" w:type="dxa"/><w:right w:w="40" w:type="dxa"/>'
                f'</w:tblCellMar>'
            )
            tpr[0].append(tmar)
            
            tb = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                f'<w:top w:val="single" w:sz="4" w:space="0" w:color="A6ACAF"/>'
                f'<w:left w:val="single" w:sz="4" w:space="0" w:color="A6ACAF"/>'
                f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="A6ACAF"/>'
                f'<w:right w:val="single" w:sz="4" w:space="0" w:color="A6ACAF"/>'
                f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="D5D8DC"/>'
                f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="D5D8DC"/>'
                f'</w:tblBorders>'
            )
            tpr[0].append(tb)

        for r_idx, r_vals in enumerate(table_data):
            row = tbl.rows[r_idx]
            trPr = row._element.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            if r_idx == 0:
                trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

            is_hdr = (r_idx == 0)
            is_tot = (r_idx == len(table_data) - 1)

            for c_idx, val in enumerate(r_vals):
                cell = row.cells[c_idx]
                tcPr = cell._element.get_or_add_tcPr()

                if c_idx < len(col_widths_dxa):
                    tcW = OxmlElement('w:tcW')
                    tcW.set(qn('w:w'), str(col_widths_dxa[c_idx]))
                    tcW.set(qn('w:type'), 'dxa')
                    tcPr.append(tcW)

                cell.text = val
                cp = cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(0)
                cp.paragraph_format.space_after = Pt(0)
                cp.paragraph_format.line_spacing = Pt(8.5)

                if is_hdr:
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="E5E8E8"/>'))
                    for run in cp.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(8)
                        run.font.bold = True
                elif is_tot:
                    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="EAEDED"/>'))
                    if c_idx in [5, 6]:
                        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    for run in cp.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(8.5)
                        run.font.bold = True
                else:
                    for run in cp.runs:
                        run.font.name = "Calibri"
                        run.font.size = Pt(7.2)
                    if c_idx in [0, 4]:
                        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    elif c_idx in [5, 6]:
                        cp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    else:
                        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # 4. УСЛОВИЯ И ПОДПИСЬ
    p_th = doc.add_paragraph()
    p_th.paragraph_format.space_before = Pt(4)
    p_th.paragraph_format.space_after = Pt(1)
    rth = p_th.add_run("Условия поставки:")
    rth.font.name = "Calibri"
    rth.font.size = Pt(8.5)
    rth.font.bold = True
    rth.underline = True

    terms_tbl = doc.add_table(rows=1, cols=2)
    terms_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    ttpr = terms_tbl._element.xpath('w:tblPr')
    if ttpr:
        ttw = OxmlElement('w:tblW')
        ttw.set(qn('w:w'), '5000')
        ttw.set(qn('w:type'), 'pct')
        ttpr[0].append(ttw)
        ttb = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/>'
            f'<w:right w:val="none"/><w:insideH w:val="none"/><w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        ttpr[0].append(ttb)

    c_terms = terms_tbl.cell(0, 0)
    c_terms.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    delivery_terms = [
        "Предоплата 50%, 50% перед отгрузкой",
        "Срок поставки 60-110 дней с момента оплаты",
        "Расчет сделан по курсу руб/юань на 22.10.2026",
        "Цена включает в себя доставку до склада в РФ",
        "Цена с учетом НДС 22%"
    ]
    for idx, term in enumerate(delivery_terms):
        pt = c_terms.paragraphs[0] if idx == 0 else c_terms.add_paragraph()
        pt.paragraph_format.space_before = Pt(0)
        pt.paragraph_format.space_after = Pt(0.5)
        pt.paragraph_format.line_spacing = Pt(9.5)
        rb = pt.add_run("•  ")
        rb.font.name = "Calibri"
        rb.font.size = Pt(7.5)
        rb.font.bold = True
        rtx = pt.add_run(term)
        rtx.font.name = "Calibri"
        rtx.font.size = Pt(7.5)

    c_sig = terms_tbl.cell(0, 1)
    c_sig.vertical_alignment = WD_ALIGN_VERTICAL.BOTTOM
    ps = c_sig.paragraphs[0]
    ps.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    ps.paragraph_format.space_before = Pt(0)
    ps.paragraph_format.space_after = Pt(0)
    if stamp_path and os.path.exists(stamp_path):
        ps.add_run().add_picture(stamp_path, width=Cm(3.5), height=Cm(2.7))

    pl = c_sig.add_paragraph()
    pl.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pl.paragraph_format.space_before = Pt(1)
    pl.paragraph_format.space_after = Pt(0)
    rsg = pl.add_run("С уважением, Генеральный Директор  /Штефан В. С./")
    rsg.font.name = "Calibri"
    rsg.font.size = Pt(8)
    rsg.font.bold = True

    doc.save(output_docx)
    print(f"[+] DOCX сохранен: {output_docx}")

    # Валидация Word COM и экспорт в PDF
    if output_pdf:
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            wdoc = word.Documents.Open(os.path.abspath(output_docx))
            pages = wdoc.ComputeStatistics(2)
            print(f"[+] Word COM валидация: страниц = {pages}")
            wdoc.SaveAs(os.path.abspath(output_pdf), FileFormat=17)
            wdoc.Close(False)
            word.Quit()
            print(f"[+] PDF сохранен: {output_pdf}")
        except Exception as e:
            print(f"[!] Word COM экспорт пропущен или вызвал исключение: {e}")


def main():
    parser = argparse.ArgumentParser(description="Универсальный генератор КП Word/PDF")
    parser.add_argument("--input", required=True, help="Путь к исходному docx")
    parser.add_argument("--output", required=True, help="Целевой docx")
    parser.add_argument("--pdf", default=None, help="Целевой pdf")
    parser.add_argument("--orientation", default="landscape", choices=["landscape", "portrait"])
    parser.add_argument("--logo", default=None, help="Путь к логотипу PNG")
    parser.add_argument("--stamp", default=None, help="Путь к печати PNG")
    args = parser.parse_args()

    format_universal_kp(
        args.input,
        args.output,
        output_pdf=args.pdf,
        orientation=args.orientation,
        logo_path=args.logo,
        stamp_path=args.stamp
    )


if __name__ == "__main__":
    main()
