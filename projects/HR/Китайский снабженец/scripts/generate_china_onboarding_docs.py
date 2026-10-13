# -*- coding: utf-8 -*-
"""
Канонический скрипт генерации вводных документов и регламентов офиса в КНР
========================================================================
Бизнес-процесс: Онбординг, должностные регламенты и инструкции для китайского офиса.
Генерирует 4 комплекта документов в форматах Word (.docx) и Markdown (.md):
1. ИНСТРУКЦИЯ_ПО_РАБОТЕ_В_БИТРИКС24_ДЛЯ_КИТАЙСКОГО_ОФИСА
2. Вводный_инструктаж_и_спринт_Цянь_Ин_Логистика
3. Вводный_инструктаж_и_спринт_Ли_Юйнань_Снабжение
4. Вводный_инструктаж_и_спринт_Лиень_Поддержка_и_Логистика

Файлы сохраняются синхронно:
- На Рабочий стол: C:\\Users\\Артем\\Desktop
- В репозиторий: projects/HR/Китайский снабженец/

Использование CLI:
  py generate_china_onboarding_docs.py --all              (генерация всех документов и валидация)
  py generate_china_onboarding_docs.py --doc b24          (только инструкция по Битрикс24)
  py generate_china_onboarding_docs.py --doc qian         (только бриф Цянь Ин)
  py generate_china_onboarding_docs.py --doc yunan        (только бриф Ли Юйнань)
  py generate_china_onboarding_docs.py --doc lien         (только бриф Лиень)
  py generate_china_onboarding_docs.py --dry-run          (проверка путей и валидация без записи)
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PROJECT_DIR = Path(__file__).resolve().parent.parent
DESKTOP_DIR = Path.home() / "Desktop"

# =====================================================================
# 1. СТИЛИ И ХЕЛПЕРЫ ДЛЯ DOCX
# =====================================================================
def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def apply_base_styles(doc, font_name='Arial'):
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
    normal = doc.styles['Normal']
    normal.font.name = font_name
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

def add_header_banner(doc, title_text, subtitle_text, color_rgb=(0x00, 0x33, 0x66)):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(title_text + "\n")
    run_t.bold = True
    run_t.font.size = Pt(15)
    run_t.font.color.rgb = RGBColor(*color_rgb)
    if subtitle_text:
        run_s = p.add_run(subtitle_text)
        run_s.font.size = Pt(10)
        run_s.font.italic = True
        run_s.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        p.paragraph_format.space_after = Pt(12)

def add_h1(doc, text, color_rgb=(0x00, 0x33, 0x66)):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(12.5)
    r.font.color.rgb = RGBColor(*color_rgb)
    return p

def add_h2(doc, text, color_rgb=(0x11, 0x44, 0x77)):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(*color_rgb)
    return p

def add_p(doc, text, bold_prefix="", space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.size = Pt(10)
    r = p.add_run(text)
    r.font.size = Pt(10)
    return p

def add_bullet(doc, text, bold_prefix=""):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.size = Pt(10)
    r = p.add_run(text)
    r.font.size = Pt(10)
    return p

def add_note_box(doc, text, title="ВАЖНОЕ ПРАВИЛО:", bg_color="F2F5F9"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if title:
        rt = p.add_run(title + " ")
        rt.bold = True
        rt.font.size = Pt(10)
        rt.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    r = p.add_run(text)
    r.font.size = Pt(9.5)
    r.font.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_screenshot_placeholder(doc, desc):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F9FAFB")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run("📷 [МЕСТО ДЛЯ СКРИНШОТА ИЗ БИТРИКС24]\n")
    r1.bold = True
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)
    r2 = p.add_run(desc)
    r2.font.size = Pt(9)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_table_data(doc, headers, rows_data):
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = tbl.cell(0, j)
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, top=100, bottom=100, left=120, right=120)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for i, row in enumerate(rows_data):
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row):
            c = tbl.cell(i + 1, j)
            set_cell_background(c, bg)
            set_cell_margins(c, top=80, bottom=80, left=120, right=120)
            p = c.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            clean_val = val.replace("<br>", "\n").strip()
            r = p.add_run(clean_val)
            r.font.size = Pt(9)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

# =====================================================================
# 2. РЕНДЕРЕР MARKDOWN В DOCX
# =====================================================================
def markdown_to_docx(md_path, docx_path):
    doc = docx.Document()
    apply_base_styles(doc, 'Arial')

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title_text = ""
    subtitle_text = ""
    in_header = True
    idx = 0
    total = len(lines)

    # Заголовочный баннер
    if lines and lines[0].startswith("# "):
        title_text = lines[0].replace("# ", "").strip()
        idx = 1
        sub_parts = []
        while idx < total and not lines[idx].startswith("|") and not lines[idx].startswith("---"):
            line = lines[idx].strip()
            if line.startswith("### "):
                sub_parts.append(line.replace("### ", "").strip())
            elif line.startswith("**") and line.endswith("**"):
                sub_parts.append(line.strip("*").strip())
            idx += 1
        subtitle_text = "\n".join(sub_parts)
        add_header_banner(doc, title_text, subtitle_text)

    # Парсинг тела документа
    in_table = False
    table_headers = []
    table_rows = []

    def flush_table():
        nonlocal in_table, table_headers, table_rows
        if in_table and table_headers and table_rows:
            add_table_data(doc, table_headers, table_rows)
        in_table = False
        table_headers = []
        table_rows = []

    while idx < total:
        raw_line = lines[idx]
        line = raw_line.strip()

        # Разделитель таблиц
        if line.startswith("|") and line.endswith("|"):
            parts = [p.strip() for p in line[1:-1].split("|")]
            # Пропуск разделительной строки таблицы (e.g. | :--- | :--- |)
            if all(re.match(r"^:?-+:?$", p) for p in parts if p):
                idx += 1
                continue
            if not in_table:
                in_table = True
                table_headers = parts
            else:
                table_rows.append(parts)
            idx += 1
            continue
        else:
            flush_table()

        if not line or line == "---":
            idx += 1
            continue

        # Заголовки H1
        if line.startswith("## "):
            h_text = line.replace("## ", "").strip()
            add_h1(doc, h_text)
            idx += 1
            continue

        # Заголовки H2
        if line.startswith("### "):
            h_text = line.replace("### ", "").strip()
            add_h2(doc, h_text)
            idx += 1
            continue

        # Плейсхолдер скриншота
        if "📷 [МЕСТО ДЛЯ СКРИНШОТА" in line or "[МЕСТО ДЛЯ СКРИНШОТА" in line:
            desc = re.sub(r"^.*\[МЕСТО ДЛЯ СКРИНШОТА[^:]*:\s*", "", line).rstrip("]").strip()
            add_screenshot_placeholder(doc, desc)
            idx += 1
            continue

        # Заметка цитаты (Note box)
        if line.startswith("> 📌") or line.startswith("> ⚠️"):
            note_lines = []
            prefix = "ПРИМЕЧАНИЕ:"
            if "ПРИНЦИП" in line:
                prefix = "ПРИНЦИП:"
            elif "ПРАВИЛО" in line:
                prefix = "ВАЖНОЕ ПРАВИЛО:"
            elif "ПРИВЕТСТВИЕ" in line:
                prefix = "ПРИВЕТСТВИЕ И СТРАТЕГИЧЕСКИЙ ОРИЕНТИР:"
            elif "СВЯЗЬ" in line:
                prefix = "СВЯЗЬ ЗАДАЧ И СДЕЛОК:"

            # Сбор многострочной цитаты
            while idx < total and lines[idx].strip().startswith(">"):
                clean_nl = lines[idx].strip()[1:].strip()
                clean_nl = re.sub(r"^[📌⚠️]\s*\*\*[^*]+\*\*:\s*", "", clean_nl)
                if clean_nl:
                    note_lines.append(clean_nl)
                idx += 1
            add_note_box(doc, " ".join(note_lines), title=prefix)
            continue

        # Маркированные списки
        if line.startswith("- ") or line.startswith("* ") or re.match(r"^\d+\.\s+", line):
            content = re.sub(r"^[-*]\s+", "", line)
            content = re.sub(r"^\d+\.\s+", "", content)
            bold_prefix = ""
            m_bold = re.match(r"^\*\*([^*]+)\*\*:\s*(.*)", content)
            if m_bold:
                bold_prefix = m_bold.group(1) + ": "
                content = m_bold.group(2)
            add_bullet(doc, content, bold_prefix=bold_prefix)
            idx += 1
            continue

        # Обычный абзац
        bold_prefix = ""
        m_pbold = re.match(r"^\*\*([^*]+)\*\*:\s*(.*)", line)
        if m_pbold:
            bold_prefix = m_pbold.group(1) + ": "
            line = m_pbold.group(2)
        add_p(doc, line, bold_prefix=bold_prefix)
        idx += 1

    flush_table()
    doc.save(str(docx_path))

# =====================================================================
# 3. ОСНОВНОЙ КОНТРОЛЛЕР СИНХРОНИЗАЦИИ И ВАЛИДАЦИИ
# =====================================================================
DOCS_MAP = {
    "b24": "ИНСТРУКЦИЯ_ПО_РАБОТЕ_В_БИТРИКС24_ДЛЯ_КИТАЙСКОГО_ОФИСА",
    "qian": "Вводный_инструктаж_и_спринт_Цянь_Ин_Логистика",
    "yunan": "Вводный_инструктаж_и_спринт_Ли_Юйнань_Снабжение",
    "lien": "Вводный_инструктаж_и_спринт_Лиень_Поддержка_и_Логистика",
}

def sync_doc(key, dry_run=False):
    base_name = DOCS_MAP[key]
    md_file = PROJECT_DIR / f"{base_name}.md"
    docx_file = PROJECT_DIR / f"{base_name}.docx"
    desk_md = DESKTOP_DIR / f"{base_name}.md"
    desk_docx = DESKTOP_DIR / f"{base_name}.docx"

    print(f"Обработка [{key}]: {base_name}...")
    if not md_file.exists():
        raise FileNotFoundError(f"Исходный файл Markdown не найден: {md_file}")

    if dry_run:
        print(f"  [DRY-RUN] MD source найден: {md_file.name} ({md_file.stat().st_size:,} байт)")
        return

    # Компиляция MD -> DOCX
    markdown_to_docx(md_file, docx_file)
    # Синхронизация на Рабочий стол
    shutil.copy2(str(docx_file), str(desk_docx))
    shutil.copy2(str(md_file), str(desk_md))
    print(f"  [OK] Скомпилирован и синхронизирован: {base_name} (.docx и .md)")

def validate_all():
    print("\n--- Аппаратная валидация чистоты и целостности файлов ---")
    forbidden = ["Лина", "Сауле", "пацански"]
    for key, base in DOCS_MAP.items():
        for ext in [".docx", ".md"]:
            fname = base + ext
            f_proj = PROJECT_DIR / fname
            f_desk = DESKTOP_DIR / fname
            assert f_proj.exists(), f"Файл не найден в проекте: {f_proj}"
            assert f_desk.exists(), f"Файл не найден на Рабочем столе: {f_desk}"
            sz = f_proj.stat().st_size
            if ext == ".md":
                text = open(f_proj, encoding='utf-8').read()
                for bad in forbidden:
                    if bad in text:
                        raise ValueError(f"ОШИБКА: Запрещенный термин '{bad}' найден в {fname}!")
            print(f"  [VALID] {fname} ({sz:,} байт) — проверен и чист.")
    print("Все 8 файлов (.docx и .md) на Рабочем столе и в проекте подтверждены.\n")

def main():
    parser = argparse.ArgumentParser(description="Канонический генератор вводных документов офиса в КНР")
    parser.add_argument("--all", action="store_true", help="Сгенерировать все 4 комплекта документов")
    parser.add_argument("--doc", choices=["b24", "qian", "yunan", "lien"], help="Сгенерировать конкретный документ")
    parser.add_argument("--dry-run", action="store_true", help="Проверить параметры без записи")
    args = parser.parse_args()

    if not args.all and not args.doc and not args.dry_run:
        args.all = True

    if args.doc:
        sync_doc(args.doc, args.dry_run)
    elif args.all:
        for k in DOCS_MAP:
            sync_doc(k, args.dry_run)

    if not args.dry_run:
        validate_all()

if __name__ == "__main__":
    main()
