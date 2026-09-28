# -*- coding: utf-8 -*-
"""
Script to generate three distinct formal Word (.docx) documents:
1. Russian (.docx): ПРЕДПИСАНИЕ_ЗАВОДУ_ПО_РЕМОНТУ_И_ОТГРУЗКЕ_RU.docx
2. English (.docx): OFFICIAL_NOTICE_ON_REPAIR_AND_SHIPMENT_EN.docx
3. Chinese (.docx): 关于活塞杆修复方案的技术决议与发货前要求函_CN.docx

Addresses:
- Rejection of brush plating (刷镀) on rods #3 and #15
- Rejection of regrinding rod #1 (core hardness failure)
- STOP-ORDER on grinding to 179.6 mm (seal extrusion risk)
- Requirement for groove bottom inner diameter
- Conditions for rods #7 & #8 (OD within f7 tolerance)
- Status of radius R0.5 (on hold)
- Pre-shipment roadmap
"""

import os
import sys
import shutil
import docx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

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

# ==========================================
# 1. RUSSIAN DOCUMENT
# ==========================================
def build_russian_docx(output_path):
    doc = docx.Document()
    apply_base_styles(doc, 'Arial')
    
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("ОФИЦИАЛЬНОЕ ТЕХНИЧЕСКОЕ ПРЕДПИСАНИЕ\n")
    r_t.bold = True
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
    
    r_sub = p_title.add_run("Резолюция по предложениям завода из файла «DATASHEET ROD-try to repare»,\n"
                            "категорический отказ от щеточной гальваники, стопор переточки и требования к отгрузке")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    
    # Meta table
    meta = doc.add_table(rows=4, cols=2)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Кому:", "Дэвиду (DEZHOU ALEXDA), Руководству завода, Инспектору ОТК Ван Сююй (汪秀玉)"),
        ("От кого:", "Российская инженерно-проектная группа (Договор поставки оборудования № 62230426)"),
        ("Дата:", "28 сентября 2026 г."),
        ("Тема:", "Оценка предложений цеха по ремонту штоков: запрет щеточной гальваники, стоп-ордер на Ø179.6 и замеры дна канавок")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(5.2)
        set_cell_background(c0, "F2F2F2")
        set_cell_background(c1, "FAFAFA")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 1: Stop-Order on 179.6
    b1 = doc.add_table(rows=1, cols=1)
    b1.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b1 = b1.rows[0].cells[0]
    c_b1.width = Inches(7.0)
    set_cell_background(c_b1, "FDE8E8")
    p_b1 = c_b1.paragraphs[0]
    p_b1.paragraph_format.space_before = Pt(4)
    p_b1.paragraph_format.space_after = Pt(4)
    r_b1_title = p_b1.add_run("🚨 1. СТОП-ОРДЕР: ЗАПРЕТ НА СОШЛИФОВКУ СТУПЕНИ ДО Ø179.6 ММ!\n")
    r_b1_title.bold = True
    r_b1_title.font.size = Pt(11)
    r_b1_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b1.add_run("Предложение завода сошлифовать ступень Ø179.9 до 179.60–179.65 мм ЗАМОРОЖЕНО. "
                 "При рабочем давлении гидроцилиндра (250–350 бар) радиальный зазор 0.3 мм приведет к выдавливанию (экструзии) уплотнений и мгновенному отказу цилиндра. "
                 "Станочные работы на шейках ЗАПРЕЩЕНЫ до получения замеров дна канавок и расчета манжет спец-профиля.")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 2: Rejection of Brush Plating
    b2 = doc.add_table(rows=1, cols=1)
    b2.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b2 = b2.rows[0].cells[0]
    c_b2.width = Inches(7.0)
    set_cell_background(c_b2, "FFF0F0")
    p_b2 = c_b2.paragraphs[0]
    p_b2.paragraph_format.space_before = Pt(4)
    p_b2.paragraph_format.space_after = Pt(4)
    r_b2_title = p_b2.add_run("❌ 2. КАТЕГОРИЧЕСКИЙ ОТКАЗ ОТ ЩЕТОЧНОЙ ГАЛЬВАНИКИ (刷镀) ДЛЯ ШТОКОВ № 3 И № 15!\n")
    r_b2_title.bold = True
    r_b2_title.font.size = Pt(11)
    r_b2_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b2.add_run("Завод предложил нарастить просаженную шейку Ø171.45 на штоках № 3 и № 15, а также поясок 179.55 на штоке № 15 с помощью щеточного (тампонного) покрытия (刷镀).\n"
                 "ИНЖЕНЕРНОЕ РЕШЕНИЕ РФ: КАТЕГОРИЧЕСКИ ОТКЛОНЕНО!\n"
                 "• Низкая адгезия: Щеточное осаждение не имеет достаточной прочности сцепления по сравнению с ванной. Под рабочим давлением до 35 МПа слой отслоится (delamination).\n"
                 "• Задир цилиндра: Сколотые твердые частицы хрома попадут в циркуляцию масла и мгновенно задерут зеркало хонингованной трубы (Ra 0.2) и срежут полиуретан.\n"
                 "• Неустранимый брак по твердости: Шток № 15 имеет твердость 45.7 HRC, шток № 3 — 46.5 HRC (норма ≥ 50 HRC). На штоке № 3 наплыв хрома 850 мкм.\n"
                 "Штоки № 1, № 3, № 15 являются ОКОНЧАТЕЛЬНЫМ БРАКОМ (报废) и подлежат списанию / замене.")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Detailed section: Detailed feedback on each factory proposal
    h_sec = doc.add_heading("3. Официальный ответ по всем 6 предложениям завода из таблицы «try to repare»", level=2)
    h_sec.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_prop = doc.add_table(rows=7, cols=3)
    t_prop.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_headers = ["Пункт / Параметр", "Предложение завода (Col U)", "Официальный вердикт и требование РФ"]
    for i, h in enumerate(p_headers):
        c = t_prop.rows[0].cells[i]
        set_cell_background(c, "E0E0E0")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)

    prop_rows = [
        ("Пункт 1: Ø180 f7\n(Штоки № 7 и № 8)",
         "«Можно ли №7 и №8 довести шлифовкой до 179,88–179,86»",
         "⚠️ УСЛОВНО ДОПУСКАЕТСЯ СОШЛИФОВКА ХРОМА:\n"
         "Разрешено сошлифовать избыток хрома (-50 мкм на №7, -30 мкм на №8) строго на круглошлифовальном станке. "
         "НО наружный диаметр ОБЯЗАН остаться в поле допуска f7 (179.917–179.957 мм)! Занижать тело штока до 179.86 мм ЗАПРЕЩЕНО."),
        
        ("Пункт 3: Ступень Ø179.9\n(Все штоки)",
         "«Φ179.6 ~ Φ179.65»",
         "🚨 СТОПОР (HOLD):\n"
         "Зазор 0.3 мм приведет к выдавливанию манжет при 250–350 бар. "
         "Любые работы ЗАМОРОЖЕНЫ до замера дна канавок и расчета уплотнений."),
        
        ("Пункт 4: Шейка Ø171.6\n(Штоки № 15 и № 3)",
         "«Можно ли №15 и паз №3 довести гальваническим покрытием (刷镀) до 171,55»",
         "❌ КАТЕГОРИЧЕСКИ ОТКЛОНЕНО:\n"
         "Щеточная гальваника запрещена для узлов высокого давления. Риск расслоения и задира гильзы. №3 и №15 — окончательный брак (списание)."),
        
        ("Пункт 5: Поясок 179.55\n(Шток № 15)",
         "«Можно ли №15 (179,55) довести гальваническим покрытием (刷镀) до 179,65»",
         "❌ КАТЕГОРИЧЕСКИ ОТКЛОНЕНО:\n"
         "Щеточное наращивание 100 мкм на опорном пояске недопустимо. Шток № 15 — окончательный брак."),
        
        ("Пункт 6: Длина 2574\n(Шток № 1)",
         "«№1 довести шлифовкой до 179,65; биение — ок. 0,05»",
         "❌ КАТЕГОРИЧЕСКИ ОТКЛОНЕНО:\n"
         "Шлифовка не восстанавливает глубину закалки ТВЧ. Твердость 45.8 HRC (< 50 HRC). Шток согнется под циклической нагрузкой. №1 — окончательный брак."),
        
        ("Пункт 15: Радиус R0.3\n(Переходный угол)",
         "«R0.5»",
         "⚠️ НА ПАУЗЕ (HOLD):\n"
         "Запрос на увеличение радиуса до R0.5 мм передан поставщику уплотнений. До согласования не перетачивать.")
    ]

    for r_idx, data in enumerate(prop_rows, start=1):
        for c_idx, val in enumerate(data):
            cell = t_prop.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "F9F9F9" if r_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
            elif c_idx == 2:
                if "ОТКЛОНЕНО" in val:
                    r.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
                elif "СТОПОР" in val:
                    r.font.color.rgb = RGBColor(0xB2, 0x59, 0x00)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 4: What is needed for urgent shipment
    h_act = doc.add_heading("4. Пошаговый регламент обязательных действий завода перед отгрузкой", level=2)
    h_act.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_act = doc.add_table(rows=6, cols=3)
    t_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    act_hdrs = ["№", "Обязательное действие", "Детали и критерий приемки"]
    for i, h in enumerate(act_hdrs):
        c = t_act.rows[0].cells[i]
        set_cell_background(c, "D9E1F2")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    act_data = [
        ("1", "Срочный замер дна канавок", "Внутренним штангенциркулем замерить внутренний диаметр дна канавок на штоках № 2, 4, 5, 6, 9, 10, 11, 14, 16. Передать цифры в РФ."),
        ("2", "Видеопроверка резьб калибром НЕ", "Резьбовым кольцом M170x4-6g проверить резьбы под видео. Останов строго ≤ 1.5–2 витка (особенно № 6 и № 9!)."),
        ("3", "Станочная сошлифовка хрома № 7 и 8", "Сошлифовать избыток хрома на круглошлифовальном станке. Диаметр строго в поле 179.917–179.957 мм. Ручная шлифовка ЗАПРЕЩЕНА!"),
        ("4", "Биение штоков № 2, 12, 13", "Замерить в центрах индикатором по 5 точкам, внести замеры в таблицу."),
        ("5", "Перемер концов штока № 10", "Замерить участки 300 мм от краев микрометром. Если диаметр < 179.917 мм — шток бракуется.")
    ]
    for r_idx, data in enumerate(act_data, start=1):
        for c_idx, val in enumerate(data):
            cell = t_act.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 0 else "F9FBFD")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Footnote
    p_foot = doc.add_paragraph()
    r_f = p_foot.add_run("Вам переданы обновленные файлы с полной фиксацией инженерных решений:\n"
                        "• DATASHEET ROD-try to repare_EN.xlsx (объединенная матрица с предложениями цеха и вердиктами РФ)\n"
                        "• Таблица_проверки_штоков_16шт.xlsx / Таблица_проверки_штоков_16шт_EN.xlsx\n\n"
                        "С уважением,\nРоссийская проектная группа (Договор поставки оборудования № 62230426)")
    r_f.font.size = Pt(9.5)
    r_f.font.italic = True

    doc.save(output_path)
    print(f"Saved Russian Word: {output_path}")

# ==========================================
# 2. ENGLISH DOCUMENT
# ==========================================
def build_english_docx(output_path):
    doc = docx.Document()
    apply_base_styles(doc, 'Arial')
    
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("OFFICIAL TECHNICAL NOTICE & RESOLUTION\n")
    r_t.bold = True
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
    
    r_sub = p_title.add_run("Formal Technical Resolution on Factory Repair Proposals in 'DATASHEET ROD-try to repare':\n"
                            "Strict Rejection of Brush Plating, Stop-Order on Grinding to Ø179.6, and Pre-Shipment Criteria")
    r_sub.font.size = Pt(10)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    
    # Meta table
    meta = doc.add_table(rows=4, cols=2)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("To:", "David (DEZHOU ALEXDA), Factory Management, QC Inspector Wang Xiuyu (汪秀玉)"),
        ("From:", "Russian Project Engineering Group (Equipment Supply Contract No. 62230426)"),
        ("Date:", "28 September 2026"),
        ("Subject:", "Evaluation of Factory Repair Proposals: Rejection of Brush Plating, Hold on Ø179.6 Grinding & Groove Bottom ID")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(5.2)
        set_cell_background(c0, "F2F2F2")
        set_cell_background(c1, "FAFAFA")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 1: Stop-Order on 179.6
    b1 = doc.add_table(rows=1, cols=1)
    b1.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b1 = b1.rows[0].cells[0]
    c_b1.width = Inches(7.0)
    set_cell_background(c_b1, "FDE8E8")
    p_b1 = c_b1.paragraphs[0]
    p_b1.paragraph_format.space_before = Pt(4)
    p_b1.paragraph_format.space_after = Pt(4)
    r_b1_title = p_b1.add_run("🚨 1. URGENT STOP-ORDER: STRICT PROHIBITION ON GRINDING STEP TO Ø179.60 MM!\n")
    r_b1_title.bold = True
    r_b1_title.font.size = Pt(11)
    r_b1_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b1.add_run("The factory's proposal to grind the step from Ø179.9 down to 179.60–179.65 mm is STRICTLY FROZEN. "
                 "Under cylinder operating pressure (250–350 bar), a 0.30 mm radial clearance gap will cause SEAL EXTRUSION and immediate hydraulic failure. "
                 "All machining on the steps is FROZEN until the factory provides the Groove Bottom ID and custom seal calculations are verified.")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 2: Rejection of Brush Plating
    b2 = doc.add_table(rows=1, cols=1)
    b2.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b2 = b2.rows[0].cells[0]
    c_b2.width = Inches(7.0)
    set_cell_background(c_b2, "FFF0F0")
    p_b2 = c_b2.paragraphs[0]
    p_b2.paragraph_format.space_before = Pt(4)
    p_b2.paragraph_format.space_after = Pt(4)
    r_b2_title = p_b2.add_run("❌ 2. CATEGORICAL REJECTION OF BRUSH PLATING (刷镀) FOR RODS #3 AND #15!\n")
    r_b2_title.bold = True
    r_b2_title.font.size = Pt(11)
    r_b2_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b2.add_run("The factory proposed applying selective brush electroplating (刷镀) to build up neck Ø171.45 on Rods #3 and #15 to 171.55 mm, and step 179.55 on Rod #15 to 179.65 mm.\n"
                 "ENGINEERING RESOLUTION: CATEGORICALLY REJECTED!\n"
                 "• Weak Adhesion & Delamination: Brush electroplating has significantly lower adhesion than conventional tank plating. Under 35 MPa cyclic pressure, the brush layer will peel off (delaminate).\n"
                 "• Severe Cylinder Scoring: Spalled hard chromium particles circulating in hydraulic oil will score the precision-honed tube surface (Ra 0.2) and shred seals.\n"
                 "• Unfixed Low Hardness: Rod #15 core hardness is 45.7 HRC, Rod #3 is 46.5 HRC (spec: ≥ 50 HRC). Rod #3 additionally has an 850 µm chrome surge.\n"
                 "Rods #1, #3, and #15 are CONFIRMED PERMANENT SCRAP and must be remade or refunded.")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 3: Proposals table
    h_sec = doc.add_heading("3. Formal Engineering Decisions on All 6 Factory Proposals in 'try to repare'", level=2)
    h_sec.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_prop = doc.add_table(rows=7, cols=3)
    t_prop.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_headers = ["Item / Parameter", "Factory Proposal (Col U)", "Russian Engineering Verdict & Requirements"]
    for i, h in enumerate(p_headers):
        c = t_prop.rows[0].cells[i]
        set_cell_background(c, "E0E0E0")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)

    prop_rows_en = [
        ("Item 1: OD Ø180 f7\n(Rods #7 and #8)",
         "Can Rods #7 & #8 be ground to OD 179.88 ~ 179.86 mm?",
         "⚠️ CONDITIONAL APPROVAL:\n"
         "Machine grinding excess chrome on #7 (-50 µm) and #8 (-30 µm) is permitted on a cylindrical grinding machine. "
         "HOWEVER, finished OD MUST stay within f7 tolerance (179.917–179.957 mm). Grinding rod body down to 179.86 mm is FORBIDDEN."),
        
        ("Item 3: Step Ø179.9\n(All Rods)",
         "Grind step down to Ø179.60 ~ Ø179.65 mm",
         "🚨 STRICT STOP-ORDER (HOLD):\n"
         "0.30 mm clearance causes seal extrusion at 250–350 bar. "
         "FROZEN until groove bottom ID is provided and seal engineering calculations are complete."),
        
        ("Item 4: Neck Ø171.6\n(Rods #15 and #3)",
         "Can Rods #15 & #3 neck be built up by brush plating to 171.55 mm?",
         "❌ CATEGORICALLY REJECTED:\n"
         "Brush plating is prohibited for high-pressure sliding dynamic seals. Severe risk of flaking and tube scoring. Rods #3 and #15 are permanent scrap."),
        
        ("Item 5: Step 179.55\n(Rod #15)",
         "Can Rod #15 step (179.55) be built up by brush plating to 179.65 mm?",
         "❌ CATEGORICALLY REJECTED:\n"
         "100 µm brush plating on bearing step cannot withstand shear loads. Hardness is only 45.7 HRC. Permanent scrap."),
        
        ("Item 6: Length 2574\n(Rod #1)",
         "Grind Rod #1 to 179.65 mm, factory guarantees runout ~0.05 mm",
         "❌ CATEGORICALLY REJECTED:\n"
         "Grinding does not restore core induction hardness (measured 45.8 HRC vs min 50 HRC spec). Soft rod will bend under load. Permanent scrap."),
        
        ("Item 15: Radius R0.3\n(Transition Corner)",
         "Increase transition radius to R0.5 mm",
         "⚠️ ON HOLD:\n"
         "Factory omitted R≤0.3 before chroming, causing flaking. Request to increase to R0.5 is on hold pending seal manufacturer verification.")
    ]

    for r_idx, data in enumerate(prop_rows_en, start=1):
        for c_idx, val in enumerate(data):
            cell = t_prop.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "F9F9F9" if r_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
            elif c_idx == 2:
                if "REJECTED" in val:
                    r.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
                elif "STOP-ORDER" in val:
                    r.font.color.rgb = RGBColor(0xB2, 0x59, 0x00)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 4: Actions table
    h_act = doc.add_heading("4. Mandatory Factory Action Roadmap Prior to Shipment", level=2)
    h_act.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_act = doc.add_table(rows=6, cols=3)
    t_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    act_hdrs = ["No.", "Mandatory Action", "Details & Acceptance Criteria"]
    for i, h in enumerate(act_hdrs):
        c = t_act.rows[0].cells[i]
        set_cell_background(c, "D9E1F2")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    act_data_en = [
        ("1", "Measure Groove Bottom ID", "Use internal groove calipers to measure exact inner diameter of groove bottoms on rods #2, 4, 5, 6, 9, 10, 11, 14, 16. Report data to Russia immediately."),
        ("2", "Video NO-GO Thread Gauge Test", "Use M170x4-6g ring gauge on video. Ring gauge must stop within ≤ 1.5–2 turns (especially on rods #6 and #9!)."),
        ("3", "Machine Grind Chrome on #7 & #8", "Strip excess chrome on cylindrical grinder. Final OD must be 179.917–179.957 mm. Manual grinding is STRICTLY FORBIDDEN!"),
        ("4", "Runout Inspection for #2, 12, 13", "Set in lathe centers, measure radial runout at 5 points with dial indicator, record in matrix."),
        ("5", "Re-measure Ends of Rod #10", "Use micrometer on 300 mm end zones. If OD < 179.917 mm, rod is scrap.")
    ]
    for r_idx, data in enumerate(act_data_en, start=1):
        for c_idx, val in enumerate(data):
            cell = t_act.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 0 else "F9FBFD")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Footnote
    p_foot = doc.add_paragraph()
    r_f = p_foot.add_run("You have been provided with the updated master inspection files:\n"
                        "• DATASHEET ROD-try to repare_EN.xlsx (Combined inspection matrix with proposals & verdicts)\n"
                        "• Таблица_проверки_штоков_16шт_EN.xlsx (Client inspection matrix)\n\n"
                        "Sincerely,\nRussian Project Engineering Group (Contract No. 62230426)")
    r_f.font.size = Pt(9.5)
    r_f.font.italic = True

    doc.save(output_path)
    print(f"Saved English Word: {output_path}")

# ==========================================
# 3. CHINESE DOCUMENT
# ==========================================
def build_chinese_docx(output_path):
    doc = docx.Document()
    apply_base_styles(doc, 'Microsoft YaHei')
    
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("官方技术决议与发货前要求函\n")
    r_t.bold = True
    r_t.font.size = Pt(15)
    r_t.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
    
    r_sub = p_title.add_run("关于对工厂《DATASHEET ROD-try to repare》活塞杆修复方案的技术评估决议：\n"
                            "严禁刷镀修复、紧急暂停179.6mm磨削、密封槽底径实测及最终发货前要求")
    r_sub.font.size = Pt(10)
    r_sub.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
    
    # Meta table
    meta = doc.add_table(rows=4, cols=2)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("收件人 (To):", "David (德州亚历斯达 / DEZHOU ALEXDA)、工厂领导层、质检主管 汪秀玉"),
        ("发件人 (From):", "俄罗斯项目工程技术专家组（设备采购合同号：62230426）"),
        ("日期 (Date):", "2026年9月28日"),
        ("主题 (Subject):", "工厂修复方案技术评估决议：严禁刷镀、暂停179.6磨削、强制密封槽底径复测及报废品认定")
    ]
    for idx, (k, v) in enumerate(meta_data):
        row = meta.rows[idx]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(1.8)
        c1.width = Inches(5.2)
        set_cell_background(c0, "F2F2F2")
        set_cell_background(c1, "FAFAFA")
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(2)
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 1: Stop-Order on 179.6
    b1 = doc.add_table(rows=1, cols=1)
    b1.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b1 = b1.rows[0].cells[0]
    c_b1.width = Inches(7.0)
    set_cell_background(c_b1, "FDE8E8")
    p_b1 = c_b1.paragraphs[0]
    p_b1.paragraph_format.space_before = Pt(4)
    p_b1.paragraph_format.space_after = Pt(4)
    r_b1_title = p_b1.add_run("🚨 1. 紧急暂停指令：严禁擅自将外圆台阶磨削至 179.60 mm！\n")
    r_b1_title.bold = True
    r_b1_title.font.size = Pt(11)
    r_b1_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b1.add_run("工厂在表格第3项提议将Φ179.9外圆台阶磨削至 179.60~179.65 mm。俄方专家正式下达【紧急暂停令】！"
                 "油缸额定工作压力高达 250~350 bar（25~35 MPa），外圆做小导致配合间隙增大 0.30 mm，将导致高压密封圈在受压时发生【间隙挤出破损（Seal Extrusion）】，造成油缸严重内漏拉伤！"
                 "在工厂提供密封槽底径实测数据并经俄罗斯密封件厂家重新计算确认前，严禁任何磨削！")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # BANNER 2: Rejection of Brush Plating
    b2 = doc.add_table(rows=1, cols=1)
    b2.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_b2 = b2.rows[0].cells[0]
    c_b2.width = Inches(7.0)
    set_cell_background(c_b2, "FFF0F0")
    p_b2 = c_b2.paragraphs[0]
    p_b2.paragraph_format.space_before = Pt(4)
    p_b2.paragraph_format.space_after = Pt(4)
    r_b2_title = p_b2.add_run("❌ 2. 坚决拒绝使用刷镀（电刷镀）工艺修复 3# 和 15# 活塞杆！\n")
    r_b2_title.bold = True
    r_b2_title.font.size = Pt(11)
    r_b2_title.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    p_b2.add_run("工厂在第4、5项提议：对 3# 和 15# 轴颈（实测171.45/171.40mm）及 15# 外圆（实测179.55mm）采用【刷镀工艺】补镀至合格尺寸。\n"
                 "俄方工程专家组正式决议：坚决否决刷镀方案！\n"
                 "• 结合力致命缺陷：刷镀层结合强度远低于传统槽镀高温热处理镀层。重载液压油缸在高频往复运动及35MPa高压剪切下，刷镀层极易发生大面积剥落（Delamination）！\n"
                 "• 恶性连锁事故：剥落的超硬铬渣混入液压油，将瞬间拉伤高精度绗磨缸筒内壁（Ra 0.2），割裂密封圈，导致整套重型液压系统瘫痪！\n"
                 "• 硬度与尺寸无法逆转：15#实测硬度仅45.7 HRC，3#仅46.5 HRC（图纸要求≥50 HRC）。且3#镀铬层存在0.85mm（850μm）的严重堆铬缺陷！\n"
                 "结论：1#、3#、15# 活塞杆属于绝对不可逆的最终报废品（报废），工厂必须退款或重新加工补发！")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 3: Proposals table
    h_sec = doc.add_heading("3. 对工厂《try to repare》表内全部6项提议的官方逐项技术决议", level=2)
    h_sec.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_prop = doc.add_table(rows=7, cols=3)
    t_prop.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_headers = ["序号 / 检验项目", "工厂提议内容 (U列)", "俄方技术专家决议与强制要求"]
    for i, h in enumerate(p_headers):
        c = t_prop.rows[0].cells[i]
        set_cell_background(c, "E0E0E0")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)

    prop_rows_cn = [
        ("第1项: 外圆 Φ180 f7\n(7#、8# 活塞杆)",
         "7号8号能不能磨到179.88~179.86",
         "⚠️ 有条件同意磨去多余铬层：\n"
         "同意在外圆磨床上磨去超差铬层（7#磨去50μm，8#磨去30μm）。"
         "但是最终外圆尺寸必须严格落在 f7 公差带内（179.917~179.957 mm）！严禁磨小至179.86mm（超差下溢出）！"),
        
        ("第3项: 台阶 Φ179.9\n(全部活塞杆)",
         "Φ179.6~  Φ179.65",
         "🚨 紧急暂停指令 (HOLD)：\n"
         "改到179.6间隙放大0.3mm，250~350bar高压下密封圈必遭挤出损坏！"
         "在完成槽底内径实测及俄方核算前，严禁任何机加！"),
        
        ("第4项: 轴颈 Φ171.6\n(15#、3# 活塞杆)",
         "15号3号槽能不能刷镀171.55",
         "❌ 坚决否决 (最终报废)：\n"
         "高压动态密封滑动部位严禁使用刷镀！高压下镀层必剥落并拉伤缸筒。3#和15#确认报废。"),
        
        ("第5项: 槽深/台阶\n(15# 活塞杆)",
         "15号179.55能不能刷镀179.65",
         "❌ 坚决否决 (最终报废)：\n"
         "台阶做小0.25mm，且硬度仅45.7HRC不合格。刷镀无法承受导向支撑载荷。15#确认报废。"),
        
        ("第6项: 长度 2574\n(1# 活塞杆)",
         "1号磨到179.65，跳动保证0.05左右",
         "❌ 坚决否决 (最终报废)：\n"
         "外圆重磨无法挽救高频淬火硬度（实测仅45.8 HRC，严重低于50 HRC标准）。重载下活塞杆必疲劳弯曲。1#确认报废。"),
        
        ("第15项: 圆角 R\n(倒角过渡圆角)",
         "R0.5",
         "⚠️ 暂缓确认 (HOLD)：\n"
         "工厂崩铬主因是镀铬前未做R0.3锐角所致。圆角做大到R0.5可能影响密封圈根部贴合。目前暂缓，严禁擅自倒圆！")
    ]

    for r_idx, data in enumerate(prop_rows_cn, start=1):
        for c_idx, val in enumerate(data):
            cell = t_prop.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "F9F9F9" if r_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
            elif c_idx == 2:
                if "坚决否决" in val:
                    r.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
                elif "紧急暂停" in val:
                    r.font.color.rgb = RGBColor(0xB2, 0x59, 0x00)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 4: Actions table
    h_act = doc.add_heading("4. 国庆节假前工厂必须完成的紧急行动路线图", level=2)
    h_act.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    t_act = doc.add_table(rows=6, cols=3)
    t_act.alignment = WD_TABLE_ALIGNMENT.CENTER
    act_hdrs = ["序号", "工厂必须执行的动作", "具体实施要求与验收判定标准"]
    for i, h in enumerate(act_hdrs):
        c = t_act.rows[0].cells[i]
        set_cell_background(c, "D9E1F2")
        p = c.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x00, 0x20, 0x60)

    act_data_cn = [
        ("1", "测量密封槽槽底内径 (Groove Bottom ID)", "立即使用内径卡尺/内径千分尺测量 2#、4#、5#、6#、9#、10#、11#、14#、16# 的两道密封槽槽底内径，并报送俄方。"),
        ("2", "螺纹止规 (NO-GO) 视频复检", "用 M170x4-6g 螺纹止规进行视频连续复查。止规旋入必须严格在 ≤ 1.5~2 牙内卡死停住（重点检测 6# 和 9#！）。"),
        ("3", "7# 和 8# 精密外圆磨床消铬", "必须在外圆磨床上精密磨去多余铬层，磨后尺寸严格保持在 179.917~179.957 mm，严禁手工打磨！"),
        ("4", "2#、12#、13# 顶尖跳动复检", "上车床顶尖，用百分表测量5个截面跳动量，将数据填入验收矩阵。"),
        ("5", "10# 两端 300mm 区域千分尺复测", "用千分尺复核两端外径，若实测低于 179.917 mm，则该杆直接判定为报废。")
    ]
    for r_idx, data in enumerate(act_data_cn, start=1):
        for c_idx, val in enumerate(data):
            cell = t_act.rows[r_idx].cells[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 0 else "F9FBFD")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Footnote
    p_foot = doc.add_paragraph()
    r_f = p_foot.add_run("随函已交付完整的技术数据矩阵表格：\n"
                        "• DATASHEET ROD-try to repare_EN.xlsx（包含工厂提议与俄方专家决议的综合对比英文表）\n"
                        "• Таблица_проверки_штоков_16шт_EN.xlsx（俄方活塞杆全项检验矩阵英文版）\n\n"
                        "顺祝商祺！\n俄罗斯项目工程技术专家组（合同号：62230426）")
    r_f.font.size = Pt(9.5)

    doc.save(output_path)
    print(f"Saved Chinese Word: {output_path}")

def main():
    dl_dir = r"C:\Users\Артем\Downloads\ТЗ для гравити"
    proj_dir = r"C:\Codex_Personal\projects\Price creating\Договор_62230426_Штоки_и_Трубы\reports"
    
    os.makedirs(dl_dir, exist_ok=True)
    os.makedirs(proj_dir, exist_ok=True)
    
    # 1. Russian
    ru_dl = os.path.join(dl_dir, "ПРЕДПИСАНИЕ_ЗАВОДУ_ПО_РЕМОНТУ_И_ОТГРУЗКЕ_RU.docx")
    ru_proj = os.path.join(proj_dir, "ПРЕДПИСАНИЕ_ЗАВОДУ_ПО_РЕМОНТУ_И_ОТГРУЗКЕ_RU.docx")
    build_russian_docx(ru_dl)
    shutil.copy2(ru_dl, ru_proj)
    
    # 2. English
    en_dl = os.path.join(dl_dir, "OFFICIAL_NOTICE_ON_REPAIR_AND_SHIPMENT_EN.docx")
    en_proj = os.path.join(proj_dir, "OFFICIAL_NOTICE_ON_REPAIR_AND_SHIPMENT_EN.docx")
    build_english_docx(en_dl)
    shutil.copy2(en_dl, en_proj)
    
    # 3. Chinese
    cn_dl = os.path.join(dl_dir, "关于活塞杆修复方案的技术决议与发货前要求函_CN.docx")
    cn_proj = os.path.join(proj_dir, "关于活塞杆修复方案的技术决议与发货前要求函_CN.docx")
    build_chinese_docx(cn_dl)
    shutil.copy2(cn_dl, cn_proj)
    
    print("\nAll 3 Word documents successfully generated in Downloads and Project directories!")

if __name__ == "__main__":
    main()
