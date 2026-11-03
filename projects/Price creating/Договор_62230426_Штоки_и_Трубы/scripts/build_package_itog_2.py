import os
import shutil
import docx
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key, val in edge_data.items():
                element.set(qn('w:{}'.format(key)), str(val))

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_para(p, font_name='Times New Roman', size=11, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4, line_spacing=1.15):
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    for r in p.runs:
        r.font.name = font_name
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic

def add_styled_para(doc, text, font_name='Times New Roman', size=11, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=4, line_spacing=1.15):
    p = doc.add_paragraph()
    p.add_run(text)
    set_para(p, font_name, size, bold, italic, align, space_after, line_spacing)
    return p

def main():
    desktop = os.path.expanduser('~') + r'\Desktop'
    target_dir = os.path.join(desktop, 'Итог номер два')
    os.makedirs(target_dir, exist_ok=True)
    print("Building package in:", target_dir)

    # Копируем скан паспорта
    src_pipes_dir = os.path.join(desktop, 'ДС_№6_Инспекция_КНР_Документы')
    f_pass_src = os.path.join(src_pipes_dir, 'загран инсректора Гидрамакс Богданов.jpg')
    if os.path.exists(f_pass_src):
        shutil.copy2(f_pass_src, os.path.join(target_dir, 'загран инспектора Богданов.jpg'))

    # =========================================================================
    # ДОКУМЕНТ 1: ДС № 6 (ТРУБЫ) - ТОЧНЫЕ ЦЕНЫ 1С (678 000 CNY) И АВАНС 191 835.30 CNY
    # =========================================================================
    doc1 = docx.Document()
    for s in doc1.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc1, "Дополнительное соглашение № 6", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc1, "к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г.", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc1, "(Поставка и порядок инструментальной приемки партии трубной продукции)", size=11, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    p_hd1 = doc1.add_paragraph()
    p_hd1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_hd1.paragraph_format.space_after = Pt(10)
    r1 = p_hd1.add_run("г. Санкт-Петербург")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.font.bold = True
    r2 = p_hd1.add_run("\t\t\t\t\t\t\t        «___» ноября 2026 г.")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    r2.font.bold = True

    add_styled_para(doc1, "Общество с ограниченной ответственностью «ЦИ ЛИНЬ» (ООО «ЦИ ЛИНЬ»), именуемое в дальнейшем «Поставщик», в лице Генерального директора Штефана Виталия Сергеевича, действующего на основании Устава, с одной стороны, и", space_after=4)
    add_styled_para(doc1, "Общество с ограниченной ответственностью «ЛОГИСТИКТРАНС» (ООО «ЛОГИСТИКТРАНС»), именуемое в дальнейшем «Покупатель», в лице Генерального директора Майсурадзе Георгия Вахтанговича, действующего на основании Устава, с другой стороны,", space_after=4)
    add_styled_para(doc1, "совместно именуемые «Стороны», а по отдельности — «Сторона», руководствуясь статьями 421, 450, 452, 453, 469, 474 и 475 Гражданского кодекса Российской Федерации, заключили настоящее Дополнительное соглашение № 6 (далее — «Соглашение») к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г. (далее — «Договор») о нижеследующем:", space_after=8)

    add_styled_para(doc1, "1. Предмет соглашения и сепарация этапа поставки труб", bold=True, space_after=4)
    add_styled_para(doc1, "1.1. В целях оптимизации исполнения договорных обязательств и обеспечения независимости логистических потоков Стороны пришли к соглашению выделить обязательства по поставке партии трубной продукции (Позиция № 1 и Позиция № 2 Приложения № 2 от 01.06.2026 г. к Договору в общем количестве 32 единицы чистовой длины 2174 мм и 1707 мм, далее — «Трубная продукция») в отдельный самостоятельный этап со специальным техническим заданием, дифференцированной поштучной стоимостью и порядком сдачи-приемки, определенными настоящим Соглашением.", space_after=8)

    add_styled_para(doc1, "2. Аннулирование условий Дополнительного соглашения № 5 в части труб", bold=True, space_after=4)
    add_styled_para(doc1, "2.1. В связи с исключением операций по нарезке 36 фланцевых резьбовых отверстий М22 на длинных трубах и подтверждением фактического объема внесенного Покупателем аванса, условия Дополнительного соглашения № 5 от 20.07.2026 г. в части трубной продукции аннулируются и признаются утратившими силу. Согласованное ранее увеличение стоимости механической обработки труб на сумму 17 000,00 CNY отменяется.", space_after=4)
    add_styled_para(doc1, "2.2. Обязательства по поставке Штоков поршня (Позиция № 3 Приложения № 2 от 01.06.2026 г.) выделяются в самостоятельное Дополнительное соглашение № 7 с пропорциональным распределением ранее уплаченного аванса.", space_after=8)

    add_styled_para(doc1, "3. Номенклатура, дифференцированная стоимость и пропорциональный аванс", bold=True, space_after=4)
    add_styled_para(doc1, "3.1. Твердая общая стоимость всей партии Трубной продукции (32 единицы) устанавливается строго в соответствии со спецификацией заказа и устанавливается с учетом вычета стоимости доработки (17 000,00 CNY) и составляет 669 011,00 CNY (Шестьсот шестьдесят девять тысяч одиннадцать китайских юаней 00 фэней), в том числе НДС 22% в размере 120 641,44 CNY (в рублевом эквиваленте по курсу ЦБ РФ на день оплаты плюс 2%). Базовая транспортировка 1-го контейнера включена в цену.", space_after=4)
    add_styled_para(doc1, "3.2. Поштучная стоимость единиц трубной продукции дифференцируется в зависимости от длины, веса и наличия разделки кромок под сварку:", space_after=3)
    add_styled_para(doc1, "а) Позиция № 1: Хонингованная труба (рабочий цилиндр, без фасок) Ø500 × Ø420 × 2174 мм, в количестве 16 штук. Твердая цена за 1 штуку составляет 23 725,00 CNY (в т.ч. НДС 22% — 4 278,28 CNY). Общая стоимость подгруппы (16 шт.) — 379 600,00 CNY;", space_after=2)
    add_styled_para(doc1, "б) Позиция № 2: Труба цилиндровая тип 2 (наружный кожух, без фасок) Ø500 × Ø420 × 1707 мм, в количестве 8 штук. Твердая цена за 1 штуку составляет 17 338,125 CNY (в т.ч. НДС 22% — 3 126,56 CNY). Общая стоимость подгруппы (8 шт.) — 138 705,00 CNY;", space_after=2)
    add_styled_para(doc1, "в) Позиция № 3: Труба цилиндровая тип 2 (с разделкой кромок под сварку 36×45° и 2×45°) Ø500 × Ø420 × 1707 мм, в количестве 8 штук. Твердая цена за 1 штуку составляет 18 838,25 CNY (в т.ч. НДС 22% — 3 397,06 CNY). Общая стоимость подгруппы (8 шт.) — 150 706,00 CNY.", space_after=4)
    add_styled_para(doc1, "3.3. Пропорциональный зачет ранее внесенного аванса:", bold=True, space_after=3)
    add_styled_para(doc1, "3.3.1. Стороны подтверждают, что фактически уплаченный Покупателем аванс в сумме 343 407,30 CNY распределяется пропорционально стоимости товаров: за партию Трубной продукции засчитывается аванс в размере 190 707,30 CNY (Сто девяносто тысяч семьсот семь китайских юаней 30 фэней), в том числе НДС 22% — 34 389,84 CNY (55,5338% от общего аванса). Оставшаяся сумма аванса в размере 152 700,00 CNY закрепляется за партией Штоков поршня по Дополнительному соглашению № 7.", space_after=2)
    add_styled_para(doc1, "3.3.2. Зачтенный аванс распределяется на каждую единицу трубы пропорционально:", space_after=2)
    add_styled_para(doc1, "• за 1 длинную трубу (2174 мм) — аванс 6 762,26 CNY (остаток доплаты 16 962,74 CNY);", space_after=2)
    add_styled_para(doc1, "• за 1 короткую трубу без фасок (1707 мм) — аванс 4 941,88 CNY (остаток доплаты 12 396,24 CNY);", space_after=2)
    add_styled_para(doc1, "• за 1 короткую трубу с фасками (1707 мм) — аванс 5 398,50 CNY (остаток доплаты 13 681,50 CNY).", space_after=4)
    add_styled_para(doc1, "3.4. Зачет аванса за забракованные единицы в счет доплаты: В случае выявления дефектов и обоснованной отбраковки отдельных единиц труб при инспекции, сумма ранее внесенного аванса за забракованные трубы не подлежит возврату «живыми деньгами», а автоматически засчитывается Сторонами в счет окончательного расчета за фактически принятые годные трубы и штоки, соразмерно уменьшая доплату Покупателя перед погрузкой.", space_after=8)

    add_styled_para(doc1, "4. График доплаты за фактически принятые трубы", bold=True, space_after=4)
    add_styled_para(doc1, "4.1. Оставшаяся сумма доплаты за принятые годные трубы (за вычетом зачтенного аванса за забракованные единицы) оплачивается Покупателем двумя платежами:", space_after=3)
    add_styled_para(doc1, "4.1.1. Второй платеж (50% от расчетной стоимости принятых труб) оплачивается в течение 5 (пяти) банковских дней с даты подписания Листа инспекции труб в КНР и выставления счета Поставщика (до погрузки в контейнер);", space_after=2)
    add_styled_para(doc1, "4.1.2. Окончательный платеж (оставшиеся 20% расчетной стоимости принятых труб) оплачивается в течение 5 (пяти) банковских дней с даты письменного уведомления о прибытии контейнера на склад временного хранения (СВХ) в г. Санкт-Петербурге до вывоза товара на склад Покупателя.", space_after=8)

    add_styled_para(doc1, "5. Инструментальная инспекция в КНР, защитные сроки и СВХ", bold=True, space_after=4)
    add_styled_para(doc1, "5.1. Приемка партии труб осуществляется на заводе в г. Ляочэн (Шаньдун) экспертом лаборатории SGS China и инспектором Покупателя Богдановым Дмитрием Андреевичем (загранпаспорт 67 № 4806815) в течение не более 2 (двух) рабочих дней. Результаты вносятся в Лист инспекции трубной продукции (Приложение № 1 к настоящему Соглашению).", space_after=4)
    add_styled_para(doc1, "5.2. При неявке представителя Покупателя либо уклонении от подписания актов без предоставления инструментальной карты дефектов поверенным прибором, Поставщик имеет безусловное право подписать акт в одностороннем порядке по заводскому листу контроля (Inspection Sheet), что обязывает Покупателя произвести оплату.", space_after=4)
    add_styled_para(doc1, "5.3. При просрочке оплаты свыше 10 рабочих дней Поставщик вправе в одностороннем внесудебном порядке отказаться от исполнения Договора в части труб, удержать всю сумму аванса (190 707,30 CNY) в качестве штрафа и реализовать трубы третьим лицам.", space_after=4)
    add_styled_para(doc1, "5.4. Ставка вынужденного хранения на СВХ в Санкт-Петербурге при задержке оплаты/вывоза устанавливается в размере 2 000 (две тысячи) рублей за 1 кубический метр в сутки.", space_after=8)

    add_styled_para(doc1, "6. Заключительные положения", bold=True, space_after=4)
    add_styled_para(doc1, "6.1. Настоящее Соглашение составлено в двух экземплярах, имеющих равную юридическую силу, по одному для каждой из Сторон.", space_after=12)

    # Таблица реквизитов
    t1 = doc1.add_table(rows=2, cols=2)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    t1.cell(0, 0).width = Inches(3.4)
    t1.cell(0, 1).width = Inches(3.4)
    t1.cell(1, 0).width = Inches(3.4)
    t1.cell(1, 1).width = Inches(3.4)
    t1.cell(0, 0).paragraphs[0].text = "Поставщик:\nООО «ЦИ ЛИНЬ»"
    set_para(t1.cell(0, 0).paragraphs[0], bold=True, space_after=2)
    t1.cell(0, 1).paragraphs[0].text = "Покупатель:\nООО «ЛОГИСТИКТРАНС»"
    set_para(t1.cell(0, 1).paragraphs[0], bold=True, space_after=2)

    t1.cell(1, 0).paragraphs[0].text = "Генеральный директор\n\n____________________ / Штефан В.С. /\nМ.П."
    set_para(t1.cell(1, 0).paragraphs[0], size=9.5)
    t1.cell(1, 1).paragraphs[0].text = "Генеральный директор\n\n____________________ / Майсурадзе Г.В. /\nМ.П."
    set_para(t1.cell(1, 1).paragraphs[0], size=9.5)

    p1_path = os.path.join(target_dir, '1_ДС_№6_к_Договору_62230426_(Трубы).docx')
    doc1.save(p1_path)
    print("Saved:", p1_path)

    # =========================================================================
    # ДОКУМЕНТ 2: ПРИЛОЖЕНИЕ № 1 К ДС № 6 (ТЗ + ЧИСТЫЙ ЛИСТ НА 32 ТРУБЫ)
    # =========================================================================
    doc2 = docx.Document()
    for s in doc2.sections:
        s.top_margin = Inches(0.5)
        s.bottom_margin = Inches(0.5)
        s.left_margin = Inches(0.5)
        s.right_margin = Inches(0.5)
        s.orientation = docx.enum.section.WD_ORIENT.LANDSCAPE
        s.page_width = Inches(11.69)
        s.page_height = Inches(8.27)

    add_styled_para(doc2, "Приложение № 1 к Дополнительному соглашению № 6 от «___» ноября 2026 г.", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
    add_styled_para(doc2, "к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г.", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=4)
    add_styled_para(doc2, "ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ И ФОРМА ЛИСТА ИНСТРУМЕНТАЛЬНОЙ ИНСПЕКЦИИ ТРУБ (32 ШТ.)", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc2, "(Сталь Q345B, внутренний хонингованный Ø420 H9, наружный Ø500 h14, партия 32 единицы)", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

    add_styled_para(doc2, "Раздел 1. Нормативные параметры и согласованные допуски партии трубной продукции", size=9.5, bold=True, space_after=2)

    t_pipe_tz = doc2.add_table(rows=4, cols=6)
    t_pipe_tz.alignment = WD_TABLE_ALIGNMENT.CENTER
    tz_headers = ["№", "Наименование позиции", "Кол-во", "Геометрические размеры и допуски", "Обработка торцев / фаски", "Твердая цена за ед."]
    for i, h in enumerate(tz_headers):
        c = t_pipe_tz.cell(0, i)
        c.paragraphs[0].text = h
        set_para(c.paragraphs[0], size=8, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, 50, 50, 60, 60)
        set_cell_border(c, top=dict(val='single', sz=4, color='888888'), bottom=dict(val='single', sz=8, color='000000'), left=dict(val='single', sz=4, color='888888'), right=dict(val='single', sz=4, color='888888'))

    tz_rows = [
        ("Поз. 1", "Хонингованная труба (рабочий цилиндр, без фасок)", "16 шт.", "Ø500 h14 × Ø420 H9 × 2174 мм (допуск длины строго: 2174 +0,5 мм)", "Без фасок под сварку, перпендикулярность торцев ≤ 0,5 мм", "24 045,00 CNY"),
        ("Поз. 2", "Труба цилиндровая тип 2 (наружный кожух, без фасок)", "8 шт.", "Ø500 h14 × Ø420 H9 × 1707 мм (допуск длины: 1707 ±1,85 мм)", "Без фасок под сварку, перпендикулярность торцев ≤ 0,5 мм", "17 580,00 CNY"),
        ("Поз. 3", "Труба цилиндровая тип 2 (с разделкой кромок под сварку)", "8 шт.", "Ø500 h14 × Ø420 H9 × 1707 мм (допуск длины: 1707 ±1,85 мм)", "Разделка кромок под сварку: фаски 36×45° и 2×45°, перпендикулярность ≤0,5 мм", "19 080,00 CNY")
    ]
    for r_idx, r_data in enumerate(tz_rows, start=1):
        for c_idx, val in enumerate(r_data):
            c = t_pipe_tz.cell(r_idx, c_idx)
            c.paragraphs[0].text = val
            set_para(c.paragraphs[0], size=7.5, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2, 5] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_margins(c, 40, 40, 50, 50)
            set_cell_border(c, top=dict(val='single', sz=4, color='CCCCCC'), bottom=dict(val='single', sz=4, color='CCCCCC'), left=dict(val='single', sz=4, color='CCCCCC'), right=dict(val='single', sz=4, color='CCCCCC'))

    add_styled_para(doc2, "Раздел 2. Формуляр Листа инструментальной инспекции 32 труб (Inspection Sheet)", size=9.5, bold=True, space_after=2)
    add_styled_para(doc2, "Формуляр заполняется экспертом SGS China и инспектором Богдановым Д.А. непосредственно на заводе в г. Ляочэн по результатам инструментальных измерений каждого изделия.", size=8, italic=True, space_after=3)

    t_pipe_sheet = doc2.add_table(rows=34, cols=12)
    t_pipe_sheet.alignment = WD_TABLE_ALIGNMENT.CENTER
    ps_headers = [
        "№", "Поз.", "Клеймо / №", "Øвн 420 (H9)", "Øнар 500 (h14)", "Длина L (мм)",
        "Стенка S (40)", "Перпенд. (≤0.5)", "Фаска (36×45°)", "Шерох. Ra (≤0.4)", "Прямолин. (≤1.0)", "Вердикт"
    ]
    for i, h in enumerate(ps_headers):
        c = t_pipe_sheet.cell(0, i)
        c.paragraphs[0].text = h
        set_para(c.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(c, "D9E1F2")
        set_cell_margins(c, 40, 40, 40, 40)
        set_cell_border(c, top=dict(val='single', sz=4, color='888888'), bottom=dict(val='single', sz=8, color='000000'), left=dict(val='single', sz=4, color='888888'), right=dict(val='single', sz=4, color='888888'))

    for r_idx in range(1, 33):
        if r_idx <= 16:
            pos_label = "Поз. 1 (2174)"
        elif r_idx <= 24:
            pos_label = "Поз. 2 (1707)"
        else:
            pos_label = "Поз. 3 (фаска)"

        for c_idx in range(12):
            c = t_pipe_sheet.cell(r_idx, c_idx)
            if c_idx == 0:
                c.paragraphs[0].text = str(r_idx)
                set_para(c.paragraphs[0], size=6.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
            elif c_idx == 1:
                c.paragraphs[0].text = pos_label
                set_para(c.paragraphs[0], size=6, align=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                c.paragraphs[0].text = ""  # ЧИСТАЯ ЯЧЕЙКА
                set_para(c.paragraphs[0], size=6.5)
            set_cell_margins(c, 25, 25, 30, 30)
            set_cell_border(c, top=dict(val='single', sz=4, color='E0E0E0'), bottom=dict(val='single', sz=4, color='E0E0E0'), left=dict(val='single', sz=4, color='E0E0E0'), right=dict(val='single', sz=4, color='E0E0E0'))

    c_tot = t_pipe_sheet.cell(33, 0)
    c_tot.paragraphs[0].text = "ИТОГО:"
    set_para(c_tot.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_background(c_tot, "D9E1F2")
    for ci in range(1, 12):
        cell_t = t_pipe_sheet.cell(33, ci)
        if ci == 11:
            cell_t.paragraphs[0].text = "Годных: ___ шт. | Брак: ___ шт."
            set_para(cell_t.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            cell_t.paragraphs[0].text = ""
        set_cell_background(cell_t, "D9E1F2")

    add_styled_para(doc2, "Подписи лиц, участвовавших в инструментальной инспекции труб:", size=9, bold=True, space_after=2)

    t_pipe_signs = doc2.add_table(rows=2, cols=3)
    t_pipe_signs.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["От независимой лаборатории SGS China:", "От Покупателя (ООО «ЛОГИСТИКТРАНС»):", "От Поставщика (ООО «ЦИ ЛИНЬ»):"]
    for i, sh in enumerate(s_headers):
        c = t_pipe_signs.cell(0, i)
        c.paragraphs[0].text = sh
        set_para(c.paragraphs[0], size=8, bold=True)

    s_bodies = [
        "Эксперт SGS China:\n\n__________________ / __________________ /\nДата: «___» __________ 2026 г.\nПечать / Штамп",
        "Представитель по Доверенности:\n\n__________________ / Богданов Д.А. /\nДата: «___» __________ 2026 г.",
        "Представитель Поставщика в КНР:\n\n__________________ / __________________ /\nДата: «___» __________ 2026 г."
    ]
    for i, sb in enumerate(s_bodies):
        c = t_pipe_signs.cell(1, i)
        c.paragraphs[0].text = sb
        set_para(c.paragraphs[0], size=7.5)

    p2_path = os.path.join(target_dir, '2_Приложение_№1_к_ДС_№6_(ТЗ_Трубы_чертежи_и_Лист_инспекции_32шт).docx')
    doc2.save(p2_path)
    print("Saved:", p2_path)

    # =========================================================================
    # ДОКУМЕНТ 3: ДС № 7 (ШТОКИ) - ЦЕНА 1С (33 480 CNY, ИТОГО 535 680) И АВАНС 151 572 CNY
    # =========================================================================
    doc3 = docx.Document()
    for s in doc3.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc3, "Дополнительное соглашение № 7", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc3, "к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г.", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc3, "(Поставка и порядок инструментальной приемки партии штоков поршня)", size=11, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    p_hd3 = doc3.add_paragraph()
    p_hd3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_hd3.paragraph_format.space_after = Pt(10)
    r1 = p_hd3.add_run("г. Санкт-Петербург")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.font.bold = True
    r2 = p_hd3.add_run("\t\t\t\t\t\t\t        «___» ноября 2026 г.")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    r2.font.bold = True

    add_styled_para(doc3, "Общество с ограниченной ответственностью «ЦИ ЛИНЬ» (ООО «ЦИ ЛИНЬ»), именуемое в дальнейшем «Поставщик», в лице Генерального директора Штефана Виталия Сергеевича, действующего на основании Устава, с одной стороны, и", space_after=4)
    add_styled_para(doc3, "Общество с ограниченной ответственностью «ЛОГИСТИКТРАНС» (ООО «ЛОГИСТИКТРАНС»), именуемое в дальнейшем «Покупатель», в лице Генерального директора Майсурадзе Георгия Вахтанговича, действующего на основании Устава, с другой стороны,", space_after=4)
    add_styled_para(doc3, "совместно именуемые «Стороны», а по отдельности — «Сторона», руководствуясь статьями 421, 450, 452, 453, 469, 474 и 475 Гражданского кодекса Российской Федерации, заключили настоящее Дополнительное соглашение № 7 (далее — «Соглашение») к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г. (далее — «Договор») о нижеследующем:", space_after=8)

    add_styled_para(doc3, "1. Предмет соглашения и выделение этапа поставки штоков", bold=True, space_after=4)
    add_styled_para(doc3, "1.1. В развитие положений Дополнительного соглашения № 6 к Договору, Стороны договорились урегулировать условия поставки, технические критерии годности, процедуру выездной инструментальной инспекции и порядок расчетов в отношении партии Штоков поршня (Позиция № 3 Приложения № 2 от 01.06.2026 г. к Договору, чертеж 20.11.32.67.068, сталь AISI 431, в общем количестве до 16 единиц, далее — «Штоки») в отдельный этап исполнения Договора.", space_after=4)
    add_styled_para(doc3, "1.2. Сдача-приемка Штоков осуществляется непосредственно на производственной площадке завода в КНР по результатам инструментальных измерений независимой аккредитованной лаборатории SGS China и уполномоченного представителя Покупателя.", space_after=8)

    add_styled_para(doc3, "2. Отмена условий предыдущих соглашений и согласованные критерии годности", bold=True, space_after=4)
    add_styled_para(doc3, "2.1. Условия Приложения № 2 от 01.06.2026 г. и Дополнительного соглашения № 5 от 20.07.2026 г. строго в части штоков признаются утратившими силу и заменяются положениями настоящего Соглашения и Приложения № 1 к нему.", space_after=4)
    add_styled_para(doc3, "2.2. Критерии безусловной годности (включая проверку резьб калибрами):", bold=True, space_after=3)
    add_styled_para(doc3, "Шток признается годным к приемке Покупателем при подтверждении независимой лабораторией и представителем Покупателя следующих фактических инструментальных параметров:", space_after=2)
    add_styled_para(doc3, "а) Радиальное биение: фактическое биение по индикатору часового типа при установке штока в центрах составляет не более 0,150 мм (≤ 0,15 мм) во всех контрольных сечениях по длине изделия (оба конца, четверти длины, середина);", space_after=2)
    add_styled_para(doc3, "б) Наружный диаметр штока: номинал Ø180 мм в пределах поля допуска f7 (179,917 – 179,957 мм). Занижение наружного диаметра на концевых участках штока (на длине 300 мм от торцев) не допускается;", space_after=2)
    add_styled_para(doc3, "в) Посадочный поясок: фактический диаметр ступени Ø179,9 мм находится в диапазоне 179,80 – 179,86 мм;", space_after=2)
    add_styled_para(doc3, "г) Шейка под уплотнения: фактический диаметр шейки Ø171,6 мм находится в диапазоне 171,50 – 171,58 мм;", space_after=2)
    add_styled_para(doc3, "д) Канавки под уплотнения: фактическая ширина канавок в пределах 8,84 – 8,89 мм при условии снятия острых кромок/заусенцев и притирки кромок надфилем;", space_after=2)
    add_styled_para(doc3, "е) Хромовое покрытие: толщина рабочего слоя хрома составляет 100 мкм (допустимо до 120 мкм; изделия с исходным слоем 130–150 мкм признаются годными после станочной круглой перешлифовки до 100 мкм). Наплывы свыше 150 мкм, отслоения и микротрещины не допускаются;", space_after=2)
    add_styled_para(doc3, "ж) Твердость закаленного слоя (ТВЧ): показатель поверхностной твердости составляет не менее 48,0 HRC (диапазон 48–52 HRC);", space_after=2)
    add_styled_para(doc3, "з) Резьбовая часть M170x4-6g: проходной калибр-кольцо ПР навинчивается свободно от руки по всей длине резьбы; непроходной калибр-кольцо НЕ останавливается с заходом не более 1,5 – 2,0 витков;", space_after=2)
    add_styled_para(doc3, "и) Торцевая фаска: выполнена равномерная фаска 3×45° со шлифовкой зоны перехода покрытия.", space_after=4)
    add_styled_para(doc3, "2.3. Изделия, замеры которых соответствуют критериям п. 2.2, подлежат обязательной приемке Покупателем. Немотивированный отказ от приемки изделий, соответствующих данным параметрам, не допускается.", space_after=8)

    add_styled_para(doc3, "3. Стоимость штоков, распределение аванса и зачет брака в доплату", bold=True, space_after=4)
    add_styled_para(doc3, "3.1. Твердая стоимость одного годного Штока поршня устанавливается строго по спецификации заказа из 1С и составляет 33 480,00 CNY (Тридцать три тысячи четыреста восемьдесят китайских юаней 00 фэней) за 1 штуку, в том числе НДС 22% в размере 6 037,38 CNY. Общая стоимость максимальной партии (16 шт.) составляет 535 680,00 CNY с НДС 22%.", space_after=4)
    add_styled_para(doc3, "3.2. Пропорциональный зачет аванса: Из фактически внесенного Покупателем аванса (343 407,30 CNY) за партию Штоков поршня засчитывается сумма 152 700,00 CNY (Сто пятьдесят две тысячи семьсот китайских юаней 00 фэней), в том числе НДС 22% — 27 536,07 CNY (44,4662% от общего аванса). Сумма аванса распределяется ровно по 9 543,75 CNY на каждый шток (из 16 единиц).", space_after=4)
    add_styled_para(doc3, "3.3. Зачет аванса за забракованные штоки в счет доплаты: В случае выявления дефектов и обоснованной поштучной отбраковки штоков при инспекции, сумма ранее внесенного аванса за забракованные штоки (из расчета 9 543,75 CNY за каждую непринятую единицу) не подлежит возврату «живыми деньгами», а автоматически засчитывается Сторонами в счет окончательного расчета за фактически принятые годные трубы и штоки (уменьшая сумму доплаты Покупателя перед погрузкой).", space_after=4)
    add_styled_para(doc3, "3.4. График окончательных расчетов за фактически принятые штоки:", bold=True, space_after=3)
    add_styled_para(doc3, "Оставшаяся сумма доплаты за каждый принятый шток (23 936,25 CNY за единицу за вычетом зачтенного аванса за брак) оплачивается Покупателем в следующем порядке:", space_after=2)
    add_styled_para(doc3, "а) Второй платеж — в течение 5 банковских дней после подписания Листа инспекции штоков в КНР и выставления счета Поставщика (до погрузки во 2-й контейнер);", space_after=2)
    add_styled_para(doc3, "б) Окончательный платеж — в течение 5 банковских дней с даты уведомления о прибытии 2-го контейнера на СВХ в Санкт-Петербурге.", space_after=4)
    add_styled_para(doc3, "3.5. Условия доставки 2-го контейнера: Доставка партии Штоков поршня осуществляется во 2-м контейнере и не включена в базовую стоимость настоящего Соглашения. Доставка 2-го контейнера оплачивается Покупателем дополнительно по фактическим счетам перевозчика. Ориентировочная стоимость транспортировки 2-го контейнера составляет 70 000,00 CNY (Семьдесят тысяч китайских юаней 00 фэней) без НДС и подлежит уточнению по тарифам экспедитора на момент отгрузки.", space_after=8)

    add_styled_para(doc3, "4. Порядок инспекции в КНР, 24-часовой акцепт и поштучная отбраковка", bold=True, space_after=4)
    add_styled_para(doc3, "4.1. Инспекция проводится экспертом SGS China и представителем Покупателя Богдановым Д.А. по Доверенности, с оформлением Листа инспекции (Приложение № 1 к настоящему Соглашению).", space_after=4)
    add_styled_para(doc3, "4.2. Регламент 24-часового рассмотрения и молчаливый акцепт (Deemed Acceptance): Скан подписанного Листа инспекции штоков направляется по email (info@logistiktrans.pro). Покупатель обязан в течение 24 часов заявить мотивированный поштучный отказ по конкретным дефектным номерам. При неполучении мотивированного отказа в течение 24 часов партия признается безусловно принятой Покупателем в полном объеме.", space_after=4)
    add_styled_para(doc3, "4.3. Не принятые штоки исключаются из Договора, не отгружаются в РФ и остаются в КНР. Исключение дефектных штоков не считается нарушением договора и не влечет штрафов или неустоек к Поставщику.", space_after=8)

    add_styled_para(doc3, "5. Заключительные положения", bold=True, space_after=4)
    add_styled_para(doc3, "5.1. Настоящее Соглашение составлено в двух экземплярах, имеющих равную силу, и вступает в силу с даты подписания обеими Сторонами.", space_after=12)

    # Реквизиты
    t3 = doc3.add_table(rows=2, cols=2)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3.cell(0, 0).width = Inches(3.4)
    t3.cell(0, 1).width = Inches(3.4)
    t3.cell(1, 0).width = Inches(3.4)
    t3.cell(1, 1).width = Inches(3.4)
    t3.cell(0, 0).paragraphs[0].text = "Поставщик:\nООО «ЦИ ЛИНЬ»"
    set_para(t3.cell(0, 0).paragraphs[0], bold=True, space_after=2)
    t3.cell(0, 1).paragraphs[0].text = "Покупатель:\nООО «ЛОГИСТИКТРАНС»"
    set_para(t3.cell(0, 1).paragraphs[0], bold=True, space_after=2)

    t3.cell(1, 0).paragraphs[0].text = "Генеральный директор\n\n____________________ / Штефан В.С. /\nМ.П."
    set_para(t3.cell(1, 0).paragraphs[0], size=9.5)
    t3.cell(1, 1).paragraphs[0].text = "Генеральный директор\n\n____________________ / Майсурадзе Г.В. /\nМ.П."
    set_para(t3.cell(1, 1).paragraphs[0], size=9.5)

    p3_path = os.path.join(target_dir, '3_ДС_№7_к_Договору_62230426_(Штоки).docx')
    doc3.save(p3_path)
    print("Saved:", p3_path)

    # =========================================================================
    # ДОКУМЕНТ 4: ПРИЛОЖЕНИЕ № 1 К ДС № 7 (КРИТЕРИИ + ЧИСТЫЙ ЛИСТ С КАЛИБРАМИ)
    # =========================================================================
    doc4 = docx.Document()
    for s in doc4.sections:
        s.top_margin = Inches(0.5)
        s.bottom_margin = Inches(0.5)
        s.left_margin = Inches(0.5)
        s.right_margin = Inches(0.5)
        s.orientation = docx.enum.section.WD_ORIENT.LANDSCAPE
        s.page_width = Inches(11.69)
        s.page_height = Inches(8.27)

    add_styled_para(doc4, "Приложение № 1 к Дополнительному соглашению № 7 от «___» ноября 2026 г.", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=1)
    add_styled_para(doc4, "к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г.", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=4)
    add_styled_para(doc4, "КРИТЕРИИ ГОДНОСТИ И ФОРМА ЛИСТА ИНСТРУМЕНТАЛЬНОЙ ИНСПЕКЦИИ ШТОКОВ (16 ШТ.)", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc4, "(Чертеж 20.11.32.67.068, сталь AISI 431, габарит Ø180 f7 × 2574 мм, резьба M170x4-6g)", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

    add_styled_para(doc4, "Раздел 1. Нормативные технические параметры и согласованные допуски", size=9.5, bold=True, space_after=2)

    t_rod_crit = doc4.add_table(rows=9, cols=4)
    t_rod_crit.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_hd = ["Контролируемый параметр", "Чертежное требование", "Согласованный допустимый критерий (норма приемки)", "Методика и средства измерения"]
    for i, h in enumerate(r_hd):
        c = t_rod_crit.cell(0, i)
        c.paragraphs[0].text = h
        set_para(c.paragraphs[0], size=8, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, 50, 50, 60, 60)
        set_cell_border(c, top=dict(val='single', sz=4, color='888888'), bottom=dict(val='single', sz=8, color='000000'), left=dict(val='single', sz=4, color='888888'), right=dict(val='single', sz=4, color='888888'))

    rc_data = [
        ("Радиальное биение (эксцентриситет)", "≤ 0,030 мм / ≤ 0,050 мм", "≤ 0,150 мм (согласованное расширение допуска)", "Установка в центрах, замер индикатором часового типа в 5 сечениях с видеофиксацией"),
        ("Наружный диаметр штока", "Ø180 f7 (179,917 – 179,957 мм)", "179,917 – 179,957 мм. Занижение на концевых участках 300 мм не допускается", "Микрометр гладкий 175–200 мм с калибровкой"),
        ("Посадочный поясок", "Ø179,9 (-0,05 / -0,096 мм)", "179,800 – 179,860 мм", "Микрометр гладкий 175–200 мм"),
        ("Шейка под уплотнения", "Ø171,6 (-0,05 / -0,10 мм)", "171,500 – 171,580 мм (просадка ниже 171,48 мм не допускается)", "Микрометр гладкий 150–175 мм"),
        ("Канавки под уплотнения (ширина)", "8,60 +0,15 мм (max 8,75 мм)", "8,84 – 8,89 мм (согласовано при условии доводки кромок надфилем)", "Штангенциркуль ШЦЦ с глубиномером"),
        ("Толщина слоя хрома", "100 мкм (0,10 мм)", "100 – 120 мкм (избыток 130–150 мкм допускается после станочной шлифовки)", "Поверенный толщиномер покрытий (SGS China)"),
        ("Твердость поверхности (ТВЧ)", "≥ 50 HRC", "≥ 48,0 HRC (диапазон 48,0 – 52,0 HRC, закалка ТВЧ)", "Твердомер по Роквеллу (HRC)"),
        ("Резьбовая часть M170x4-6g", "Резьба метрическая M170x4-6g", "Калибр ПР навинчивается от руки; калибр НЕ заходит не более 1,5–2 витков", "Поверенные резьбовые калибры-кольца M170x4-6g (ПР и НЕ)")
    ]
    for row_idx, rdata in enumerate(rc_data, start=1):
        for col_idx, text in enumerate(rdata):
            c = t_rod_crit.cell(row_idx, col_idx)
            c.paragraphs[0].text = text
            set_para(c.paragraphs[0], size=7.5, space_after=1)
            set_cell_margins(c, 40, 40, 50, 50)
            set_cell_border(c, top=dict(val='single', sz=4, color='CCCCCC'), bottom=dict(val='single', sz=4, color='CCCCCC'), left=dict(val='single', sz=4, color='CCCCCC'), right=dict(val='single', sz=4, color='CCCCCC'))

    add_styled_para(doc4, "Раздел 2. Формуляр Листа инструментальной инспекции 16 штоков (Inspection Sheet)", size=9.5, bold=True, space_after=2)
    add_styled_para(doc4, "Формуляр заполняется экспертом независимой лаборатории (SGS China) и уполномоченным инспектором Покупателя Богдановым Д.А. непосредственно на заводе в КНР.", size=8, italic=True, space_after=3)

    t_rod_sheet = doc4.add_table(rows=18, cols=13)
    t_rod_sheet.alignment = WD_TABLE_ALIGNMENT.CENTER
    rs_headers = [
        "№", "Биение (≤0.15)", "Ø180 f7", "Поясок Ø179.9", "Шейка Ø171.6",
        "Канавки (мм)", "Ø дна канавок", "Хром (мкм)", "HRC (≥48)",
        "Калибр ПР (рука)", "Калибр НЕ (≤2в.)", "Длина L", "Вердикт"
    ]
    for i, h in enumerate(rs_headers):
        c = t_rod_sheet.cell(0, i)
        c.paragraphs[0].text = h
        set_para(c.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, 40, 40, 30, 30)
        set_cell_border(c, top=dict(val='single', sz=4, color='888888'), bottom=dict(val='single', sz=8, color='000000'), left=dict(val='single', sz=4, color='888888'), right=dict(val='single', sz=4, color='888888'))

    for r_idx in range(1, 17):
        for c_idx in range(13):
            c = t_rod_sheet.cell(r_idx, c_idx)
            if c_idx == 0:
                c.paragraphs[0].text = f"Шток №{r_idx}"
                set_para(c.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
                set_cell_background(c, "F9F9F9")
            else:
                c.paragraphs[0].text = ""  # ПУСТАЯ ЯЧЕЙКА
                set_para(c.paragraphs[0], size=7)
            set_cell_margins(c, 30, 30, 30, 30)
            set_cell_border(c, top=dict(val='single', sz=4, color='D3D3D3'), bottom=dict(val='single', sz=4, color='D3D3D3'), left=dict(val='single', sz=4, color='D3D3D3'), right=dict(val='single', sz=4, color='D3D3D3'))

    c_tot_r = t_rod_sheet.cell(17, 0)
    c_tot_r.paragraphs[0].text = "ИТОГО:"
    set_para(c_tot_r.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_cell_background(c_tot_r, "EAEAEA")
    for ci in range(1, 13):
        cell_t = t_rod_sheet.cell(17, ci)
        if ci == 12:
            cell_t.paragraphs[0].text = "Годных: ___ шт. | Брак: ___ шт."
            set_para(cell_t.paragraphs[0], size=7, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        else:
            cell_t.paragraphs[0].text = ""
        set_cell_background(cell_t, "EAEAEA")

    add_styled_para(doc4, "Подписи лиц, участвовавших в инструментальной инспекции штоков:", size=9, bold=True, space_after=2)

    t_rod_signs = doc4.add_table(rows=2, cols=3)
    t_rod_signs.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers_r = ["От независимой лаборатории SGS China:", "От Покупателя (ООО «ЛОГИСТИКТРАНС»):", "От Поставщика (ООО «ЦИ ЛИНЬ»):"]
    for i, sh in enumerate(s_headers_r):
        c = t_rod_signs.cell(0, i)
        c.paragraphs[0].text = sh
        set_para(c.paragraphs[0], size=8, bold=True)

    s_bodies_r = [
        "Эксперт SGS China:\n\n__________________ / __________________ /\nДата: «___» __________ 2026 г.\nПечать / Штамп",
        "Представитель по Доверенности:\n\n__________________ / Богданов Д.А. /\nДата: «___» __________ 2026 г.",
        "Представитель Поставщика в КНР:\n\n__________________ / __________________ /\nДата: «___» __________ 2026 г."
    ]
    for i, sb in enumerate(s_bodies_r):
        c = t_rod_signs.cell(1, i)
        c.paragraphs[0].text = sb
        set_para(c.paragraphs[0], size=7.5)

    p4_path = os.path.join(target_dir, '4_Приложение_№1_к_ДС_№7_(Критерии_годности_и_Лист_инспекции_штоков).docx')
    doc4.save(p4_path)
    print("Saved:", p4_path)

    # =========================================================================
    # ДОКУМЕНТ 5: ОБЩЕЕ СОГЛАШЕНИЕ ОБ ИНСПЕКЦИИ И ТРЕВЕЛ-РАСХОДАХ
    # =========================================================================
    doc5 = docx.Document()
    for s in doc5.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc5, "Соглашение", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc5, "об организации выездной инспекции качества продукции в КНР,", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc5, "порядке распределения расходов и регламенте сдачи-приемки товаров", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc5, "(к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г., ДС № 6 и ДС № 7)", size=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    p_hd5 = doc5.add_paragraph()
    p_hd5.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_hd5.paragraph_format.space_after = Pt(10)
    r1 = p_hd5.add_run("г. Санкт-Петербург")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.font.bold = True
    r2 = p_hd5.add_run("\t\t\t\t\t\t\t        «___» ноября 2026 г.")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    r2.font.bold = True

    add_styled_para(doc5, "Общество с ограниченной ответственностью «ЦИ ЛИНЬ» (ООО «ЦИ ЛИНЬ»), именуемое в дальнейшем «Поставщик», в лице Генерального директора Штефана Виталия Сергеевича, действующего на основании Устава, с одной стороны, и", space_after=4)
    add_styled_para(doc5, "Общество с ограниченной ответственностью «ЛОГИСТИКТРАНС» (ООО «ЛОГИСТИКТРАНС»), именуемое в дальнейшем «Покупатель», в лице Генерального директора Майсурадзе Георгия Вахтанговича, действующего на основании Устава, с другой стороны,", space_after=4)
    add_styled_para(doc5, "совместно именуемые «Стороны», в целях организации процедуры инструментального контроля качества Трубной продукции (32 шт., ДС № 6) и Штоков поршня (до 16 шт., ДС № 7) непосредственно на производственных площадках в Китайской Народной Республике (КНР), согласования графика перемещения экспертов и распределения связанных расходов, заключили настоящее Соглашение о нижеследующем:", space_after=8)

    add_styled_para(doc5, "1. Уполномоченный представитель Покупателя и график контрольных мероприятий", bold=True, space_after=4)
    add_styled_para(doc5, "1.1. Покупатель подтверждает, что его надлежащим образом уполномоченным представителем для проведения совместных инструментальных замеров и входного контроля обеих партий продукции в КНР является гражданин РФ Богданов Дмитрий Андреевич (заграничный паспорт серии 67 № 4806815, выдан 19.12.2025 органом МВД 0608), действующий на основании официальной Доверенности Покупателя.", space_after=4)
    add_styled_para(doc5, "1.2. Программа и маршрут инспекции в КНР состоят из двух последовательных этапов (логистическая эстафета):", space_after=3)
    add_styled_para(doc5, "1.2.1. Этап 1 (Завод штоков): Прибытие инспектора Покупателя Богданова Д.А. и представителя Поставщика на площадку завода-изготовителя штоков. Проведение инструментальных измерений параметров каждого штока с участием эксперта независимой аккредитованной лаборатории SGS China (通标标准技术服务). Срок проведения измерений — не более 1 (одного) рабочего дня. Оформление и подписание на месте трехстороннего Листа инспекции штоков (Inspection Sheet).", space_after=3)
    add_styled_para(doc5, "1.2.2. Трансфер: Непосредственно по завершении измерений штоков инспектор Покупателя и представитель Поставщика выезжают автотранспортом на трубный завод в г. Ляочэн (провинция Шаньдун). Скан-копия подписанного Листа инспекции штоков в этот же день направляется генеральному директору ООО «ЛОГИСТИКТРАНС» по электронной почте (info@logistiktrans.pro).", space_after=3)
    add_styled_para(doc5, "1.2.3. Этап 2 (Трубный завод в г. Ляочэн): Проведение визуального и инструментального контроля партии трубной продукции (32 шт.) поверенным инструментом. Срок контроля на заводе труб составляет не более 2 (двух) рабочих дней. По итогам измерений подписывается Лист инспекции трубной продукции.", space_after=3)
    add_styled_para(doc5, "1.2.4. Параллельное согласование штоков и консолидация: В период проведения замеров труб Покупатель обязан в течение 24 часов направить официальное подтверждение приемки годных штоков либо мотивированный поштучный отказ (п. 4.2 ДС № 7). Принятые штоки упаковываются на заводе штоков и транспортируются в г. Ляочэн для совместной погрузки с трубами в общий 40-футовый контейнер.", space_after=8)

    add_styled_para(doc5, "2. Оплата командировочных расходов и защитные гарантии (Anti-Default Travel Clause)", bold=True, space_after=4)
    add_styled_para(doc5, "2.1. Поставщик (ООО «ЦИ ЛИНЬ») берет на себя добровольные обязательства организовать, забронировать и оплатить за свой счет авиабилеты эконом-класса (по маршруту Россия — Китай — Россия) и гостиничный номер в КНР для инспектора Покупателя Богданова Д.А. на период проведения инспекционной программы.", space_after=4)
    add_styled_para(doc5, "2.2. Обязательство возмещения затрат при срыве поездки: В случае, если инспектор Покупателя не явится на рейс, отменит поездку, отзовет доверенность, откажется от прибытия на заводы или уклонится от проведения измерений и подписания протоколов/актов, Покупатель обязан в течение 3 (трех) банковских дней с момента получения требования Поставщика возместить Поставщику 100% расходов на приобретенные авиабилеты и бронирование отелей. Поставщик также вправе в бесспорном порядке удержать указанную сумму из любых платежей, поступивших от Покупателя по Договору.", space_after=8)

    add_styled_para(doc5, "3. Обязанности сторон и право одностороннего актирования", bold=True, space_after=4)
    add_styled_para(doc5, "3.1. Поставщик обеспечивает доступ к продукции, грузоподъемные механизмы, освещение и поверенные средства измерений заводских лабораторий с действующими калибровочными протоколами.", space_after=4)
    add_styled_para(doc5, "3.2. Покупатель обязуется обеспечить, чтобы его инспектор проводил замеры строго в согласованные сроки, использовал исключительно поверенный измерительный инструмент и подписывал промежуточные акты и таблицы замеров непосредственно на месте проведения контроля.", space_after=4)
    add_styled_para(doc5, "3.3. В случае неприбытия инспектора Покупателя в согласованные даты либо его немотивированного отказа от подписания актов/таблиц замеров без предоставления инструментальной карты дефектов поверенным прибором, Поставщик имеет безусловное право составить и подписать промежуточные акты приемки в одностороннем порядке (на основании заводского листа контроля и протоколов SGS).", space_after=8)

    add_styled_para(doc5, "4. Заключительные положения", bold=True, space_after=4)
    add_styled_para(doc5, "4.1. Настоящее Соглашение вступает в силу с момента его подписания и действует до полного исполнения Сторонами обязательств по ДС № 6 и ДС № 7.", space_after=12)

    # Реквизиты
    t5 = doc5.add_table(rows=2, cols=2)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    t5.cell(0, 0).width = Inches(3.4)
    t5.cell(0, 1).width = Inches(3.4)
    t5.cell(1, 0).width = Inches(3.4)
    t5.cell(1, 1).width = Inches(3.4)
    t5.cell(0, 0).paragraphs[0].text = "Поставщик:\nООО «ЦИ ЛИНЬ»"
    set_para(t5.cell(0, 0).paragraphs[0], bold=True, space_after=2)
    t5.cell(0, 1).paragraphs[0].text = "Покупатель:\nООО «ЛОГИСТИКТРАНС»"
    set_para(t5.cell(0, 1).paragraphs[0], bold=True, space_after=2)

    t5.cell(1, 0).paragraphs[0].text = "Генеральный директор\n\n____________________ / Штефан В.С. /\nМ.П."
    set_para(t5.cell(1, 0).paragraphs[0], size=9.5)
    t5.cell(1, 1).paragraphs[0].text = "Генеральный директор\n\n____________________ / Майсурадзе Г.В. /\nМ.П."
    set_para(t5.cell(1, 1).paragraphs[0], size=9.5)

    p5_path = os.path.join(target_dir, '5_Общее_соглашение_об_организации_выездной_инспекции_и_тревел_расходах_(Трубы_и_Штоки).docx')
    doc5.save(p5_path)
    print("Saved:", p5_path)

    # =========================================================================
    # ДОКУМЕНТ 6: ЕДИНАЯ ДОВЕРЕННОСТЬ (ТРУБЫ И ШТОКИ)
    # =========================================================================
    doc6 = docx.Document()
    for s in doc6.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc6, "Проект доверенности (форма для Покупателя)", size=10, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
    add_styled_para(doc6, "(Оформляется на фирменном бланке ООО «ЛОГИСТИКТРАНС» с круглой печатью)", size=9.5, italic=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=8)

    add_styled_para(doc6, "Доверенность № ____", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc6, "на представление интересов Покупателя при инструментальной приемке продукции в КНР", size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    p_hd6 = doc6.add_paragraph()
    p_hd6.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_hd6.paragraph_format.space_after = Pt(8)
    r1 = p_hd6.add_run("г. Санкт-Петербург")
    r1.font.name = 'Times New Roman'
    r1.font.size = Pt(11)
    r1.font.bold = True
    r2 = p_hd6.add_run("\t\t\t\t\t\t\t        «___» __________ 2026 г.")
    r2.font.name = 'Times New Roman'
    r2.font.size = Pt(11)
    r2.font.bold = True

    add_styled_para(doc6, "Общество с ограниченной ответственностью «ЛОГИСТИКТРАНС» (ИНН 7805828985, КПП 780501001, ОГРН 1267800018420, адрес: 198095, г. Санкт-Петербург, ул. Севастопольская, д. 26, лит. О, пом. 1-Н, оф. 22) в лице Генерального директора Майсурадзе Георгия Вахтанговича, действующего на основании Устава, настоящей доверенностью уполномочивает:", space_after=6)

    add_styled_para(doc6, "гражданина Российской Федерации Богданова Дмитрия Андреевича,", bold=True, space_after=2)
    add_styled_para(doc6, "паспорт гражданина РФ: серия ________ № ____________, выдан ____________________________________________________, код подразделения __________, дата выдачи «___» ____________ ______ г., зарегистрированного по адресу: ______________________________________________________________________,", space_after=2)
    add_styled_para(doc6, "заграничный паспорт гражданина РФ: 67 № 4806815, выдан 19.12.2025 органом МВД 0608,", space_after=6)

    add_styled_para(doc6, "совершать от имени ООО «ЛОГИСТИКТРАНС» следующие юридические и фактические действия в рамках исполнения Договора поставки оборудования № 62/23/04/26 от 23.04.2026 г., Дополнительного соглашения № 6 от «___» ноября 2026 г. (Трубная продукция) и Дополнительного соглашения № 7 от «___» ноября 2026 г. (Штоки поршня):", space_after=4)

    powers = [
        "1. Представлять интересы ООО «ЛОГИСТИКТРАНС» на производственных площадках, складах и лабораториях в Китайской Народной Республике (включая заводы в провинции Шаньдун и иных локациях КНР);",
        "2. Принимать личное участие в проведении инструментального контроля, геометрических измерений, дефектоскопии и визуального осмотра партии Трубной продукции (32 шт.) и партии Штоков поршня (до 16 шт., чертеж 20.11.32.67.068);",
        "3. Производить замеры с использованием поверенных средств измерений Поставщика, независимой лаборатории (SGS China) либо собственных поверенных средств измерений Покупателя (включая резьбовые калибры-кольца M170x4-6g, микрометры, индикаторы);",
        "4. Подписывать от имени ООО «ЛОГИСТИКТРАНС» двусторонние протоколы измерений, Листы инспекции штоков и Листы инспекции трубной продукции, промежуточные акты приемки продукции, а также инструментальные ведомости дефектов, оформленные строго на основании показаний поверенных приборов;",
        "5. Осуществлять фото- и видеофиксацию контрольных операций и состояния маркировки изделий."
    ]
    for pw in powers:
        add_styled_para(doc6, pw, space_after=3)

    add_styled_para(doc6, "Особые условия: Полномочия на подписание документов об отказе от Договора в целом, изменение цены Договора или перечисление денежных средств настоящей доверенностью не предоставляются.", bold=True, space_after=6)
    add_styled_para(doc6, "Настоящая доверенность выдана сроком по «31» декабря 2026 года без права передоверия третьим лицам.", space_after=8)

    add_styled_para(doc6, "Образец подписи представителя Богданова Д.А. ____________________ удостоверяю.", space_after=12)

    add_styled_para(doc6, "Генеральный директор ООО «ЛОГИСТИКТРАНС»\n\n______________________________ / Майсурадзе Г.В. /\nМ.П.", bold=True, space_after=4)

    p6_path = os.path.join(target_dir, '6_Проект_единой_Доверенности_на_инспектора_Богданова_Д.А._(Трубы_и_Штоки).docx')
    doc6.save(p6_path)
    print("Saved:", p6_path)

    # =========================================================================
    # ДОКУМЕНТ 7: ОФИЦИАЛЬНОЕ ПИСЬМО-ВЫЗОВ (ТРУБЫ И ШТОКИ)
    # =========================================================================
    doc7 = docx.Document()
    for s in doc7.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc7, "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ «ЦИ ЛИНЬ»", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1)
    add_styled_para(doc7, "ОГРН 1237800001340 | ИНН 7801719960 | КПП 780101001", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1)
    add_styled_para(doc7, "199058, г. Санкт-Петербург, ул. Кораблестроителей, дом 30, лит. А, пом. 196-Н, оф. 1-7 Б", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1)
    add_styled_para(doc7, "Тел.: +7 (812) 928-83-88 | E-mail: sales@longwang.ru", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    p_meta = doc7.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_meta.paragraph_format.space_after = Pt(8)
    r_num = p_meta.add_run("Исх. № 03/11-ЦЛ от «03» ноября 2026 г.\nНа № б/н от 29.10.2026 г.")
    r_num.font.name = 'Times New Roman'
    r_num.font.size = Pt(10)

    p_to = doc7.add_paragraph()
    p_to.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_to.paragraph_format.space_after = Pt(10)
    r_to = p_to.add_run("Генеральному директору\nООО «ЛОГИСТИКТРАНС»\nМайсурадзе Г.В.\n198095, г. Санкт-Петербург,\nул. Севастопольская, д. 26, лит. О,\nпом. 1-Н, оф. 22\nE-mail: info@logistiktrans.pro")
    r_to.font.name = 'Times New Roman'
    r_to.font.size = Pt(10)

    add_styled_para(doc7, "УВЕДОМЛЕНИЕ", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1)
    add_styled_para(doc7, "о готовности партий трубной продукции и штоков поршня к совместной инспекции в КНР", size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

    add_styled_para(doc7, "Уважаемый Георгий Вахтангович!", size=11, bold=True, space_after=4)
    add_styled_para(doc7, "Настоящим уведомляем Вас о том, что партии Трубной продукции (32 шт., ДС № 6) и Штоков поршня (до 16 шт., ДС № 7) по Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г. подготовлены к проведению входного инструментального контроля качества на производственных площадках в Китайской Народной Республике.", space_after=4)
    add_styled_para(doc7, "ООО «ЦИ ЛИНЬ» подтверждает согласование выезда Вашего представителя Богданова Дмитрия Андреевича (заграничный паспорт 67 № 4806815) и в рамках партнерского содействия берет на себя расходы по бронированию авиабилетов и гостиницы в КНР.", space_after=4)
    add_styled_para(doc7, "Для завершения оформления тревел-пакета и допуска на заводы просим Вас направить с официальной почты info@logistiktrans.pro:", space_after=3)
    add_styled_para(doc7, "1. Официальное письмо с подтверждением дат командировки и полномочий инспектора Богданова Д.А.;", space_after=2)
    add_styled_para(doc7, "2. Скан-копию Доверенности с печатью ООО «ЛОГИСТИКТРАНС» на проведение инструментального контроля и подписание актов по трубам и штокам;", space_after=2)
    add_styled_para(doc7, "3. Подтверждение действующей китайской визы инспектора.", space_after=4)
    add_styled_para(doc7, "Программа инспекции включает: 1 день работы на заводе штоков с независимой лабораторией SGS China, трансфер в г. Ляочэн и 2 рабочих дня измерений трубной продукции с последующей консолидацией принятых товаров в один контейнер.", space_after=8)

    add_styled_para(doc7, "С уважением,\nГенеральный директор ООО «ЦИ ЛИНЬ»\n\n___________________ / Штефан В.С. /\nМ.П.", bold=True, space_after=4)

    p7_path = os.path.join(target_dir, '7_Официальное_письмо_вызов_на_инспекцию_в_КНР_(Трубы_и_Штоки).docx')
    doc7.save(p7_path)
    print("Saved:", p7_path)

    # =========================================================================
    # ДОКУМЕНТ 8: ПОЯСНИТЕЛЬНАЯ ЗАПИСКА И СВОДНАЯ МОДЕЛЬ ДЛЯ ЮРИСТА
    # =========================================================================
    doc8 = docx.Document()
    for s in doc8.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc8, "ПОЯСНИТЕЛЬНАЯ ЗАПИСКА И СВОДНАЯ МОДЕЛЬ ДЛЯ ЮРИСТА", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc8, "Юридическое и финансовое обоснование пакета документов по приемке труб и штоков в КНР", size=11, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc8, "(Договор поставки оборудования № 62/23/04/26 от 23.04.2026 г., ДС № 6 и ДС № 7)", size=10, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    add_styled_para(doc8, "Уважаемый коллега!", size=11, bold=True, space_after=4)
    add_styled_para(doc8, "Данная записка составлена простым юридическим языком для быстрого понимания коммерческо-договорной архитектуры сделки, движения денежных средств и заложенных защитных механизмов перед правовой экспертизой пакета документов.", space_after=8)

    add_styled_para(doc8, "1. Сводная финансовая модель по реальным данным 1С и распределение аванса", size=11, bold=True, space_after=4)
    add_styled_para(doc8, "Покупателем (ООО «ЛОГИСТИКТРАНС») был ранее оплачен аванс в размере 343 407,30 CNY по первоначальной спецификации заказа. Доплата аванса по ДС № 5 покупателем произведена не была.", space_after=3)
    add_styled_para(doc8, "В обновленной редакции документов все цены строго приведены в соответствие с номенклатурным заказом из 1С, а уплаченный аванс (343 407,30 CNY) распределен пропорционально стоимости товаров:", space_after=4)

    # Таблица для юриста
    t_fin = doc8.add_table(rows=8, cols=6)
    t_fin.alignment = WD_TABLE_ALIGNMENT.CENTER
    f_hd = ["Номенклатура (по 1С)", "Кол-во", "Цена за ед. (CNY)", "Общая стоимость", "Зачтенный аванс (CNY)", "Остаток доплаты (CNY)"]
    for i, h in enumerate(f_hd):
        c = t_fin.cell(0, i)
        c.paragraphs[0].text = h
        set_para(c.paragraphs[0], size=8, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_background(c, "EAEAEA")
        set_cell_margins(c, 50, 50, 50, 50)
        set_cell_border(c, top=dict(val='single', sz=4, color='888888'), bottom=dict(val='single', sz=8, color='000000'), left=dict(val='single', sz=4, color='888888'), right=dict(val='single', sz=4, color='888888'))

    fin_rows = [
        ("Трубы: Поз. 1 (2174 мм, без фасок)", "16 шт.", "23 725,00", "379 600,00", "108 196,16 (6 762,26/шт.)", "271 403,84 (16 962,74/шт.)"),
        ("Трубы: Поз. 2 (1707 мм, без фасок)", "8 шт.", "17 338,125", "138 705,00", "39 535,07 (4 941,88/шт.)", "99 169,93 (12 396,24/шт.)"),
        ("Трубы: Поз. 3 (1707 мм, с фаской 36×45°)", "8 шт.", "18 838,25", "150 706,00", "42 976,07 (5 372,01/шт.)", "107 729,93 (13 466,24/шт.)"),
        ("ИТОГО ТРУБЫ (ДС № 6):", "32 шт.", "—", "669 011,00 CNY", "190 707,30 CNY", "478 303,70 CNY"),
        ("ШТОКИ ПОРШНЯ (ДС № 7):", "16 шт.", "33 480,00", "535 680,00 CNY", "152 700,00 CNY (9 543,75/шт.)", "382 980,00 CNY (23 936,25/шт.)"),
        ("ОБЩИЙ ИТОГ ТОВАРЫ (без 2-го конт.):", "48 шт.", "—", "1 204 691,00 CNY", "343 407,30 CNY", "861 283,70 CNY"),
        ("Доставка 2-го контейнера (Штоки):", "1 конт.", "—", "70 000,00 CNY без НДС", "оплата по факту отгрузки", "по счетам перевозчика")
    ]
    for r_idx, r_data in enumerate(fin_rows, start=1):
        for c_idx, val in enumerate(r_data):
            c = t_fin.cell(r_idx, c_idx)
            c.paragraphs[0].text = val
            is_bold = r_idx in [4, 5, 6]
            set_para(c.paragraphs[0], size=7.5, bold=is_bold, space_after=1, align=WD_ALIGN_PARAGRAPH.CENTER if c_idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT)
            set_cell_margins(c, 40, 40, 40, 40)
            if r_idx in [4, 6]:
                set_cell_background(c, "F2F2F2")
            set_cell_border(c, top=dict(val='single', sz=4, color='CCCCCC'), bottom=dict(val='single', sz=4, color='CCCCCC'), left=dict(val='single', sz=4, color='CCCCCC'), right=dict(val='single', sz=4, color='CCCCCC'))

    add_styled_para(doc8, "2. Механизм зачета аванса за забракованные единицы в счет доплаты", size=11, bold=True, space_after=4)
    add_styled_para(doc8, "В обоих Дополнительных соглашениях (п. 3.4 ДС № 6 и п. 3.3 ДС № 7) закреплен фундаментальный защитный механизм:", space_after=3)
    add_styled_para(doc8, "Если при инспекции покупатель обоснованно бракует часть изделий (например, 2 штока или 3 трубы), мы НЕ возвращаем аванс живыми деньгами на счет покупателя. Сумма аванса за забракованные единицы (6 762,26 CNY за длинную трубу, 4 941,88 CNY за короткую, 9 543,75 CNY за шток) автоматически засчитывается Сторонами в счет оплаты принятых годных единиц, уменьшая сумму доплаты покупателя перед погрузкой.", space_after=8)

    add_styled_para(doc8, "3. Двухэтапный график доплаты за принятые изделия", size=11, bold=True, space_after=4)
    add_styled_para(doc8, "Оставшаяся доплата за принятые изделия осуществляется в два этапа:", space_after=3)
    add_styled_para(doc8, "1) 50% от расчетной стоимости принятых изделий — оплачивается в течение 5 банковских дней после подписания Листов инспекции в КНР (строго до отгрузки со склада и погрузки в контейнер);", space_after=2)
    add_styled_para(doc8, "2) 20% (окончательный расчет) — оплачивается в течение 5 банковских дней после прибытия контейнера на СВХ в Санкт-Петербурге до вывоза товара со склада.", space_after=8)

    add_styled_para(doc8, "4. Логистическая эстафета и 24-часовой Deemed Acceptance", size=11, bold=True, space_after=4)
    add_styled_para(doc8, "Инспекция организована в 2 этапа: сначала 1 день на заводе штоков с независимой лабораторией SGS China (подписание Листа инспекции штоков) ➔ переезд инспектора в г. Ляочэн (2 дня на замер труб). В этот период директор покупателя обязан в течение 24 часов согласовать Лист инспекции штоков по email. При отсутствии возражений включается правило молчаливого акцепта (Deemed Acceptance). Принятые штоки доставляются к трубам и грузятся в один 40-футовый контейнер.", space_after=8)

    add_styled_para(doc8, "5. Карта рисков и юридические предохранители", size=11, bold=True, space_after=4)
    risks = [
        ("Риск 1: Срыв поездки инспектора после покупки билетов за наш счет.",
         "Защита: В Соглашении об инспекции (п. 2.2) зафиксирован Anti-Default Travel Clause — 100% возмещение расходов покупателем в 3 банковских дня либо бесспорное удержание из оплат."),
        ("Риск 2: Уклонение инспектора от подписания актов на заводе.",
         "Защита: Право одностороннего актирования (п. 5.2 ДС № 6) на основании заводского Inspection Sheet и протоколов SGS."),
        ("Риск 3: Спор по резьбе штоков.",
         "Защита: В критерии возвращены калибры M170x4-6g: ПР (навинчивание от руки) и НЕ (останов ≤1.5-2 витка). Если шток не проходит калибр НЕ — он поштучно бракуется, аванс зачитывается в годные трубы/штоки, штрафы исключены."),
        ("Риск 4: Претензии по качеству после доставки в РФ.",
         "Защита: Инструментальная приемка по геометрии и покрытиям в КНР признана окончательной. В РФ товар принимается исключительно по количеству мест и целостности тары.")
    ]
    for r_title, r_body in risks:
        p_r = doc8.add_paragraph()
        r1 = p_r.add_run(r_title + "\n")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10)
        r1.font.bold = True
        r2 = p_r.add_run(r_body)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(9.5)
        set_para(p_r, space_after=3)

    p8_path = os.path.join(target_dir, '8_Пояснительная_записка_и_сводная_финансовая_модель_для_юриста.docx')
    doc8.save(p8_path)
    print("Saved:", p8_path)

if __name__ == '__main__':
    main()
