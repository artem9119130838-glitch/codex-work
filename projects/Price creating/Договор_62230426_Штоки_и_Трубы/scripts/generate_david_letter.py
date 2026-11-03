import os
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

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
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
    target_dir = os.path.join(desktop, 'Письмо Дэвиду')
    os.makedirs(target_dir, exist_ok=True)

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.75)

    add_styled_para(doc, "Запрос партнеру Дэвиду (DEZHOU ALEXDA)", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
    add_styled_para(doc, "по согласованию статуса штоков, технических условий приемки и регламента инспекции", size=11, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

    add_styled_para(doc, "Здравствуйте, Дэвид!", size=11, bold=True, space_after=6)
    add_styled_para(doc, "Перед финальным подписанием документов с заводом и российским клиентом нам необходимо оперативно и точно согласовать с Вами и руководством завода три ключевых вопроса по партии штоков гидроцилиндров (16 шт., чертеж 20.11.32.67.068, сталь AISI 431).", space_after=4)
    add_styled_para(doc, "По трубной продукции договоренности с покупателем уже полностью зафиксированы. Сейчас мы готовим дополнительное соглашение по штокам. Наша юридическая цель — жестко связать заказчика техническими рамками: если параметры штока соответствуют согласованным критериям, заказчик обязан безоговорочно принять изделие и не имеет права заявлять немотивированный отказ. Чтобы не допустить срыва на месте, просим Вас подтвердить следующие пункты.", space_after=8)

    # Вопрос 1
    add_styled_para(doc, "Вопрос 1. Актуален ли текущий статус партии из 16 штоков на заводе?", size=11, bold=True, space_after=4)
    add_styled_para(doc, "Просим подтвердить или скорректировать распределение штоков по группам на сегодняшний день:", space_after=3)

    groups = [
        ("Группа А — Годны к сдаче (6–8 шт.):", "Штоки № 4, № 16 (эталон), № 11, № 14, № 5, № 2. На них нарезана резьба, радиальное биение находится в согласованном допуске (не более 0,15 мм), посадочные шейки в норме."),
        ("Группа Б — Критическая резьба под сомнением (2 шт.):", "Штоки № 6 и № 9. Биение у них в норме (0,14 мм), но на заводском видео непроходной калибр-кольцо НЕ зашел глубже допустимого предела (более 1,5–2 витков). Если независимая лаборатория SGS подтвердит просадку резьбы калибром НЕ, заказчик их обоснованно забракует. Успел ли завод перепроверить резьбу на этих номерах?"),
        ("Группа В — Требуется станочная сошлифовка хрома (2 шт.):", "Штоки № 7 и № 8. Исходная толщина хрома завышена (130–150 мкм). Снял ли завод избыток хрома на круглошлифовальном станке до слоя 100 мкм, как требовалось?"),
        ("Группа Г — Окончательный брак / Утиль (3 шт.):", "Штоки № 1, № 3, № 15. У них зафиксированы неустранимые дефекты: твердость ниже 47 HRC (при норме от 48–50 HRC), биение 0,17 мм, просадка посадочных шеек и поясков. Эти 3 штуки завод признает браком, или по ним есть новые данные?")
    ]
    for title, desc in groups:
        p = doc.add_paragraph()
        r1 = p.add_run(title + " ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r2 = p.add_run(desc)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10.5)
        set_para(p, space_after=3)

    # Вопрос 2
    add_styled_para(doc, "Вопрос 2. Согласны ли Вы и завод с критериями безусловной приемки штоков?", size=11, bold=True, space_after=4)
    add_styled_para(doc, "В дополнительное соглашение с покупателем мы включаем пункт о том, что покупатель обязан принять штоки, если при совместных измерениях с лабораторией SGS подтверждены следующие фактические параметры:", space_after=3)

    crit_list = [
        "1. Радиальное биение: не более 0,150 мм (≤ 0,15 мм) в центрах по всей длине штока;",
        "2. Наружный диаметр штока: номинал Ø180 мм в допуске f7 (179,917 – 179,957 мм), без занижения на концах 300 мм;",
        "3. Посадочный поясок Ø179,9 мм: в пределах 179,80 – 179,86 мм;",
        "4. Шейка под уплотнения Ø171,6 мм: в пределах 171,50 – 171,58 мм;",
        "5. Канавки под уплотнения: ширина 8,84 – 8,89 мм после аккуратного снятия заусенцев и притирки кромок надфилем;",
        "6. Толщина хромового покрытия: 100 мкм (допустимо до 120 мкм, без сколов и отслоений);",
        "7. Твердость ТВЧ: не менее 48,0 HRC (диапазон 48–52 HRC);",
        "8. Торцевая фаска: равномерная фаска со шлифовкой зоны перехода покрытия."
    ]
    for c in crit_list:
        add_styled_para(doc, c, size=10.5, space_after=2)

    add_styled_para(doc, "Просим ответить: гарантирует ли завод соответствие годных штоков этим значениям, или какие-то позиции лучше сразу списать и не выставлять инспектору, чтобы не создавать конфликт на месте?", space_after=8)

    # Вопрос 3
    add_styled_para(doc, "Вопрос 3. Согласован ли порядок проведения инспекции и логистической эстафеты в Китае?", size=11, bold=True, space_after=4)
    add_styled_para(doc, "Мы выстраиваем четкий пошаговый график контрольных мероприятий в КНР:", space_after=3)

    steps = [
        ("Шаг 1 (Инспекция штоков, 1 день):", "Инспектор покупателя Богданов Д.А. и представитель нашей компании прибывают на завод штоков. В присутствии аккредитованного эксперта SGS China проводятся замеры параметров каждого штока и заполняется чистая двусторонняя Таблица замеров (Inspection Sheet), которая подписывается всеми тремя сторонами на месте."),
        ("Шаг 2 (Переезд на трубный завод):", "Сразу после подписания таблицы штоков инспектор Богданов Д.А. и наш представитель выезжают автотранспортом на трубный завод в г. Ляочэн для проведения 2-дневной приемки труб."),
        ("Шаг 3 (Параллельное решение покупателя по email за 24 часа):", "Скан подписанной таблицы штоков направляется директору покупателя в Санкт-Петербург. У покупателя есть ровно 24 часа на рассмотрение. Если за 24 часа мотивированный отказ не поступил, партия штоков считается безусловно принятой по качеству. Непринятые штоки с дефектами вычеркиваются из спецификации и остаются на заводе в КНР без каких-либо претензий к заводу со стороны покупателя в РФ."),
        ("Шаг 4 (Упаковка и доставка штоков к трубам):", "Пока в Ляочэне идет приемка труб, принятые штоки упаковываются на заводе штоков в специальную деревянную тару под контролем нашего второго представителя и автотранспортом доставляются на трубный завод в г. Ляочэн для совместной погрузки в единый 40-футовый контейнер.")
    ]
    for s_title, s_desc in steps:
        p = doc.add_paragraph()
        r1 = p.add_run(s_title + " ")
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10.5)
        r1.font.bold = True
        r2 = p.add_run(s_desc)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(10.5)
        set_para(p, space_after=3)

    add_styled_para(doc, "Просим подтвердить, согласован ли такой порядок действий с заводом штоков и готовы ли они обеспечить упаковку и транспортировку принятых штоков к трубам в указанные сроки.", space_after=12)

    add_styled_para(doc, "С уважением,\nРоссийская проектная группа", bold=True, space_after=4)

    out_path = os.path.join(target_dir, 'Письмо_Дэвиду_Штоки_Инспекция.docx')
    doc.save(out_path)
    print("Saved:", out_path)

if __name__ == '__main__':
    main()
