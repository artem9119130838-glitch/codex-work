import argparse
from pathlib import Path
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _set_no_borders(table):
    tblPr = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for b_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'none')
        borders.append(b)
    tblPr.append(borders)


def _init_doc():
    doc = docx.Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(1.5)
    sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(2.0)
    sec.right_margin = Cm(1.8)
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(10.5)
    style.paragraph_format.space_after = Pt(4)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.line_spacing = 1.12
    return doc


def _add_p(doc, text="", bold=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10.5, space_after=4, space_before=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.12
    if text:
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(size)
        r.bold = bold
    return p


def _add_mixed_p(doc, parts, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=10.5, space_after=4, space_before=0):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = 1.12
    for txt, is_bold in parts:
        r = p.add_run(txt)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(size)
        r.bold = is_bold
    return p


def _add_header_and_preamble(doc, ds_num, ds_date, place, act_date, sheet_ref):
    _add_p(doc, "Акт промежуточной приемки продукции по качеству, количеству и упаковке", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=12.5, space_after=2)
    _add_p(doc, f"к Дополнительному соглашению № {ds_num} от «{ds_date}»", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, size=10.5, space_after=1)
    _add_p(doc, "к Договору поставки оборудования № 62/23/04/26 от 23.04.2026 г.", bold=False, align=WD_ALIGN_PARAGRAPH.CENTER, size=10.5, space_after=8)

    dt_tbl = doc.add_table(rows=1, cols=2)
    dt_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_no_borders(dt_tbl)
    r_loc = dt_tbl.rows[0].cells[0].paragraphs[0].add_run(place)
    r_loc.font.name = 'Times New Roman'; r_loc.font.size = Pt(10.5); r_loc.bold = True

    p_dt = dt_tbl.rows[0].cells[1].paragraphs[0]
    p_dt.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_dt = p_dt.add_run(act_date)
    r_dt.font.name = 'Times New Roman'; r_dt.font.size = Pt(10.5); r_dt.bold = True

    _add_mixed_p(doc, [
        ("Общество с ограниченной ответственностью «ЦИ ЛИНЬ» (ООО «ЦИ ЛИНЬ»)", True),
        (" (ИНН 7801719960, ОГРН 1237800001340), именуемое в дальнейшем «Поставщик», в лице Генерального директора Штефана Виталия Сергеевича, действующего на основании Устава, с одной стороны, и", False)
    ], space_before=6)

    _add_mixed_p(doc, [
        ("Общество с ограниченной ответственностью «ЛОГИСТИКТРАНС» (ООО «ЛОГИСТИКТРАНС»)", True),
        (" (ИНН 7805828985, ОГРН 1267800018420), именуемое в дальнейшем «Покупатель», в лице уполномоченного представителя ", False),
        ("Богданова Дмитрия Андреевича", True),
        (" (паспорт гражданина РФ серии 4026 № 589768, выдан ГУ МВД России по г. Санкт-Петербургу и Ленинградской области 03.09.2026 г., код подразделения 780-030; заграничный паспорт серии 67 № 4806815, выдан 19.12.2025 г. органом МВД 0608), действующего на основании Доверенности б/н от «05» ноября 2026 г., с другой стороны,", False)
    ])

    _add_p(doc, f"совместно именуемые «Стороны», во исполнение Договора поставки оборудования № 62/23/04/26 от 23.04.2026 г. (далее — «Договор»), Дополнительного соглашения № {ds_num} от {ds_date} (далее — «ДС № {ds_num}») и Соглашения об организации выездной инспекции от 05.11.2026 г., на основании подписанного {sheet_ref}, составили настоящий Акт о нижеследующем:")


def _add_signatures(doc):
    sig_tbl = doc.add_table(rows=2, cols=2)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    _set_no_borders(sig_tbl)
    for row in sig_tbl.rows:
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))

    c00 = sig_tbl.rows[0].cells[0].paragraphs[0]
    c00.paragraph_format.space_after = Pt(4)
    r = c00.add_run("От Поставщика (ООО «ЦИ ЛИНЬ»):")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.bold = True

    c01 = sig_tbl.rows[0].cells[1].paragraphs[0]
    c01.paragraph_format.space_after = Pt(4)
    r = c01.add_run("От Покупателя (ООО «ЛОГИСТИКТРАНС»):")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5); r.bold = True

    c10 = sig_tbl.rows[1].cells[0].paragraphs[0]
    c10.paragraph_format.line_spacing = 1.15
    r = c10.add_run("Генеральный директор\nООО «ЦИ ЛИНЬ»\n\n____________________ / Штефан В.С. /\nМ.П.")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5)

    c11 = sig_tbl.rows[1].cells[1].paragraphs[0]
    c11.paragraph_format.line_spacing = 1.15
    r = c11.add_run("Представитель по Доверенности\nб/н от «05» ноября 2026 г.\n\n____________________ / Богданов Д.А. /\nМ.П.")
    r.font.name = 'Times New Roman'; r.font.size = Pt(10.5)


def build_rods_act(out_path: Path):
    doc = _init_doc()
    _add_header_and_preamble(
        doc,
        ds_num="7",
        ds_date="05» ноября 2026 г.",
        place="г. Чанчжоу (провинция Цзянсу, КНР)",
        act_date="«10» ноября 2026 г.",
        sheet_ref="трехстороннего Листа инструментальной инспекции штоков от 10.11.2026 г. (Приложение № 1 к ДС № 7)",
    )
    # Fix double quote in header subtitle
    doc.paragraphs[1].runs[0].text = "к Дополнительному соглашению № 7 от «05» ноября 2026 г."

    _add_p(doc, "1. Результаты выездной инструментальной приемки и согласованное количество", bold=True, space_before=4, space_after=3)
    _add_mixed_p(doc, [
        ("1.1. На производственной площадке завода-изготовителя в г. Чанчжоу (КНР) 10 ноября 2026 г. проведена совместная сплошная инструментальная инспекция партии товара — ", False),
        ("Штоков поршня", True),
        (" (Позиция № 3 Приложения № 2 от 01.06.2026 г. к Договору, чертеж 20.11.32.67.068, сталь AISI 431, габаритные размеры Ø180 f7 × 2574 мм, резьба M170×4-6g) с участием эксперта независимой аккредитованной лаборатории SGS China (Simon Zhang, штамп от 10.11.2026 г.), представителя Покупателя Богданова Д.А. и представителя Поставщика Чжао Наня (赵南).", False)
    ])
    _add_p(doc, "1.2. По результатам замеров поверенными приборами (диаметры, радиальное биение, посадочный поясок, шейка и канавки, толщина хромового покрытия, твердость ТВЧ HRC, шероховатость Ra, проверка резьбовыми калибрами ПР/НЕ M170×4-6g, общая длина, а также свидетельствование PMI и 100% УЗК), зафиксированным в Листе инструментальной инспекции от 10.11.2026 г., Стороны установили и окончательно согласовали следующее:")
    _add_mixed_p(doc, [
        ("• Принято Покупателем как полностью годное: ", True),
        ("14 (четырнадцать) штук", True),
        (" штоков поршня под инспекционными номерами ", False),
        ("№ 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16", True),
        (" (включая изделие № 12 после проведенной доработки на месте и положительного повторного замера);", False)
    ], space_after=2)
    _add_mixed_p(doc, [
        ("• Исключено из поставки и не подлежит отгрузке (п. 4.3 ДС № 7): ", True),
        ("2 (две) штуки", True),
        (" — изделие ", False),
        ("№ 2", True),
        (" (отклонено по непроходному резьбовому калибру НЕ M170×4-6g) и изделие ", False),
        ("№ 13", True),
        (" (к контролю не предъявлялось и окончательно исключено из партии по согласованию Сторон).", False)
    ])
    _add_mixed_p(doc, [
        ("1.3. Окончательный объем поставки Штоков поршня по ДС № 7 составляет ровно ", False),
        ("14 (четырнадцать) штук", True),
        (". Исключение изделий № 2 и № 13 в порядке п. 4.3 ДС № 7 не является нарушением Договора и не влечет ответственности или штрафных санкций к Поставщику.", False)
    ])

    _add_p(doc, "2. Окончательность приемки по качеству, упаковке и разграничение ответственности", bold=True, space_before=4, space_after=3)
    _add_mixed_p(doc, [
        ("2.1. Покупатель подтверждает, что указанные в п. 1.2 настоящего Акта ", False),
        ("14 (четырнадцать) принятых штоков поршня", True),
        (" полностью соответствуют техническим требованиям Договора, согласованным критериям годности ДС № 7 и Приложения № 1 к ДС № 7. Подписание настоящего Акта подтверждает окончательное согласование и акцепт качества данных 14 (четырнадцати) изделий в порядке п. 4.1–4.2 ДС № 7.", False)
    ])
    _add_mixed_p(doc, [
        ("2.2. Покупатель подтверждает, что ", False),
        ("какие-либо претензии к Поставщику по качеству, материалу, геометрическим параметрам, хромовому покрытию, твердости, шероховатости, резьбе и иным проверенным характеристикам указанных 14 (четырнадцати) штоков поршня отсутствуют и в дальнейшем предъявлению не подлежат", True),
        (" (ст. 475, 483, 513 ГК РФ).", False)
    ])
    _add_mixed_p(doc, [
        ("2.3. Уполномоченный представитель Покупателя лично осмотрел подготовленную экспортную упаковку, защитную консервацию, маркировку и тару принятых ", False),
        ("14 (четырнадцати) штоков поршня", True),
        (", подтверждает, что товар надлежащим образом упакован, уложен, зафиксирован и опломбирован (запечатан) для последующей отгрузки, и каких-либо замечаний к упаковке, маркировке и состоянию изделий на момент завершения приемки не имеет.", False)
    ])
    _add_p(doc, "2.4. Настоящий Акт подтверждает окончательную приемку товара по качеству, количеству и состоянию упаковки на производственной площадке в КНР и не заменяет отгрузочные документы (УПД / товарную накладную) при передаче груза в РФ. После подписания настоящего Акта дальнейшая ответственность Поставщика в отношении принятых 14 (четырнадцати) штоков поршня ограничивается исключительно их сохранностью при погрузке в контейнер, транспортировке и фактической доставкой указанного количества изделий до места передачи Покупателю (СВХ в г. Санкт-Петербург). Дальнейшие претензии Покупателя по указанным 14 изделиям возможны исключительно в случае их недоставки (утраты в пути), недостачи по количеству либо явного механического повреждения тары/изделий, возникшего при перевозке.")

    _add_p(doc, "3. Заключительные положения", bold=True, space_before=4, space_after=3)
    _add_p(doc, "3.1. Настоящий Акт не изменяет твердую единичную цену продукции и условия взаиморасчетов, установленные ДС № 7, составлен в двух подлинных экземплярах равной юридической силы (по одному для каждой из Сторон) и является неотъемлемой частью ДС № 7 к Договору № 62/23/04/26 от 23.04.2026 г.", space_after=10)

    _add_signatures(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print("SAVED RODS ACT:", out_path)


def _parse_int_list(val: str):
    if not val:
        return []
    return sorted({int(x.strip()) for x in val.split(",") if x.strip()})


def build_tubes_act(out_path: Path, act_date: str, rejected: list[int], missing: list[int], sgs_inspector: str):
    excluded = sorted(set(rejected) | set(missing))
    accepted = [i for i in range(1, 33) if i not in excluded]
    pos1_acc = [i for i in accepted if 1 <= i <= 16]
    pos2_acc = [i for i in accepted if 17 <= i <= 24]
    pos3_acc = [i for i in accepted if 25 <= i <= 32]

    doc = _init_doc()
    _add_header_and_preamble(
        doc,
        ds_num="6",
        ds_date="05» ноября 2026 г.",
        place="г. Ляочэн (провинция Шаньдун, КНР)",
        act_date=f"«{act_date}»",
        sheet_ref=f"подписанного Листа инструментальной инспекции трубной продукции от {act_date} (Приложение № 2 к ДС № 6)",
    )
    doc.paragraphs[1].runs[0].text = "к Дополнительному соглашению № 6 от «05» ноября 2026 г."

    _add_p(doc, "1. Результаты выездной инструментальной приемки и согласованное количество", bold=True, space_before=4, space_after=3)
    _add_mixed_p(doc, [
        ("1.1. На производственной площадке завода-изготовителя в г. Ляочэн (провинция Шаньдун, КНР) проведена совместная сплошная инструментальная инспекция партии ", False),
        ("Трубной продукции", True),
        (" (Позиции № 1 и № 2 Приложения № 2 от 01.06.2026 г. к Договору, сталь Q345B, Ø500 × Ø420 мм, в общем количестве до 32 единиц) с участием эксперта независимой аккредитованной лаборатории SGS China (", False),
        (sgs_inspector, False),
        (") и уполномоченного представителя Покупателя Богданова Д.А.", False),
    ])
    _add_p(doc, "1.2. По результатам замеров поверенными приборами (наружный и внутренний диаметры, общая длина, разностенность ΔS, шероховатость Ra, перпендикулярность торцов А и Б, углы и глубина разделки кромок под сварку), а также проверки сертификата металлургического завода Daye Special Steel и свидетельствования PMI/УЗК, зафиксированным в Листе инструментальной инспекции (Приложение № 2 к ДС № 6), Стороны установили и окончательно согласовали следующее:")

    _add_mixed_p(doc, [
        ("• Принято Покупателем как полностью годное: всего ", True),
        (f"{len(accepted)} шт.", True),
        (" трубной продукции, в том числе:", False)
    ], space_after=2)
    _add_p(doc, f"  – Позиция № 1 (хонингованная труба Ø500×Ø420×2174 мм, без фасок): {len(pos1_acc)} шт. (номера: {', '.join(f'№ {x}' for x in pos1_acc) if pos1_acc else 'нет'});", space_after=1)
    _add_p(doc, f"  – Позиция № 2 (труба тип 2 Ø500×Ø420×1707 мм, без фасок): {len(pos2_acc)} шт. (номера: {', '.join(f'№ {x}' for x in pos2_acc) if pos2_acc else 'нет'});", space_after=1)
    _add_p(doc, f"  – Позиция № 3 (труба тип 2 Ø500×Ø420×1707 мм, с фасками 36×45° и 2×45°): {len(pos3_acc)} шт. (номера: {', '.join(f'№ {x}' for x in pos3_acc) if pos3_acc else 'нет'}).", space_after=2)

    excl_desc = []
    if rejected:
        excl_desc.append(f"отклонены по результатам замеров: {', '.join(f'№ {x}' for x in rejected)}")
    if missing:
        excl_desc.append(f"не предъявлялись к контролю: {', '.join(f'№ {x}' for x in missing)}")
    excl_text = "; ".join(excl_desc) if excl_desc else "отсутствуют"

    _add_mixed_p(doc, [
        ("• Исключено из поставки и не подлежит отгрузке: ", True),
        (f"{len(excluded)} шт.", True),
        (f" ({excl_text}).", False)
    ])
    _add_mixed_p(doc, [
        ("1.3. Окончательный объем поставки Трубной продукции по ДС № 6 составляет ровно ", False),
        (f"{len(accepted)} шт.", True),
        (" Исключение не принятых единиц из поставки не является нарушением Договора и не влечет ответственности или штрафных санкций к Поставщику.", False)
    ])

    _add_p(doc, "2. Окончательность приемки по качеству, упаковке и разграничение ответственности", bold=True, space_before=4, space_after=3)
    _add_mixed_p(doc, [
        ("2.1. Покупатель подтверждает, что указанные в п. 1.2 настоящего Акта ", False),
        (f"{len(accepted)} единиц принятой трубной продукции", True),
        (" полностью соответствуют техническим требованиям Договора, ДС № 6, Приложения № 1 и Приложения № 2 к ДС № 6.", False)
    ])
    _add_mixed_p(doc, [
        ("2.2. Покупатель подтверждает, что ", False),
        ("какие-либо претензии к Поставщику по качеству, марке стали, геометрическим параметрам, шероховатости, перпендикулярности торцов, разделке фасок и иным проверенным характеристикам указанных принятых изделий отсутствуют и в дальнейшем предъявлению не подлежат", True),
        (" (ст. 475, 483, 513 ГК РФ).", False)
    ])
    _add_p(doc, "2.3. Уполномоченный представитель Покупателя лично осмотрел подготовленную экспортную упаковку, защитную консервацию, заглушки/окантовку торцов, маркировку и тару принятых изделий, подтверждает, что товар надлежащим образом упакован, уложен, зафиксирован и опломбирован (запечатан) для последующей отгрузки, и каких-либо замечаний к упаковке, маркировке и состоянию изделий на момент завершения приемки не имеет.")
    _add_p(doc, "2.4. Настоящий Акт подтверждает окончательную приемку товара по качеству, количеству и состоянию упаковки на производственной площадке в КНР и не заменяет отгрузочные документы (УПД / товарную накладную) при передаче груза в РФ. После подписания настоящего Акта дальнейшая ответственность Поставщика в отношении принятых изделий ограничивается исключительно их сохранностью при погрузке в контейнер, транспортировке и фактической доставкой указанного количества изделий до места передачи Покупателю (СВХ в г. Санкт-Петербург). Дальнейшие претензии Покупателя возможны исключительно в случае недоставки (утраты в пути), недостачи по количеству либо явного механического повреждения тары/изделий, возникшего при перевозке.")

    _add_p(doc, "3. Заключительные положения", bold=True, space_before=4, space_after=3)
    _add_p(doc, "3.1. Настоящий Акт не изменяет твердую единичную цену продукции и условия взаиморасчетов (включая п. 3.4 ДС № 6 о зачете аванса за непринятые единицы), составлен в двух подлинных экземплярах равной юридической силы (по одному для каждой из Сторон) и является неотъемлемой частью ДС № 6 к Договору № 62/23/04/26 от 23.04.2026 г.", space_after=10)

    _add_signatures(doc)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print("SAVED TUBES ACT:", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генератор Актов промежуточной приемки (Договор 62/23/04/26)")
    parser.add_argument("--mode", choices=["rods", "tubes", "both"], default="rods")
    parser.add_argument("--out-dir", default=str(Path(__file__).parent / "output"))
    parser.add_argument("--date", default="13 ноября 2026 г.")
    parser.add_argument("--rejected", default="")
    parser.add_argument("--missing", default="")
    parser.add_argument("--sgs", default="эксперт SGS China")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    if args.mode in ("rods", "both"):
        build_rods_act(out_dir / "Акт_промежуточной_приемки_штоков_к_ДС_№7_(14_шт).docx")
    if args.mode in ("tubes", "both"):
        build_tubes_act(
            out_dir / "Акт_промежуточной_приемки_труб_к_ДС_№6.docx",
            act_date=args.date,
            rejected=_parse_int_list(args.rejected),
            missing=_parse_int_list(args.missing),
            sgs_inspector=args.sgs,
        )
