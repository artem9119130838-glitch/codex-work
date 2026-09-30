import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

MASTER_TEMPLATE_PATH = r"D:\Документы Victus\Рабочее\Шаблоны\Заявки\Запрос КП пример заполнения.xlsx"
DESKTOP_DIR = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\Артем"), "Desktop")

# База готовых спецификаций по подтвержденным заявкам (наработки из архива)
KNOWN_SPECIFICATIONS = {
    "волтайр": [
        {
            "num": 1,
            "brand": "OEM / Китай",
            "pname_cn": "85寸内胎硫化机 (主机)",
            "model": "85\" Dome type, 1 cavity (2250 kN / 225t)",
            "name_ru": "Вулканизационный пресс 85” косоугольный, однокамерный, центрический (тип нагрева Dome, усилие 2250 кН/225 т, диаметр камер 535-711 мм, высота ПФ 420-760 мм, макс. вес ПФ 4800 кг, 380В/15кВт, цвет RAL 7035)",
            "qty": 2,
        },
        {
            "num": 2,
            "brand": "VALAS / ARMSTRONG",
            "pname_cn": "阀组梯级系统 (蒸汽、冷凝水、空气、真空)",
            "model": "Cascade valve system for 85\" press",
            "name_ru": "Система каскадов клапанов (пар 0,8-1,0 МПа / 170-185 °С, конденсат, воздух 0,02-0,05 МПа, вакуум -0,06...-0,08 МПа; фланцевые клапаны VALAS, конденсатоотводчик ARMSTRONG)",
            "qty": 2,
        },
        {
            "num": 3,
            "brand": "OEM / Китай",
            "pname_cn": "自动润滑系统",
            "model": "Lubrication system for 85\" press",
            "name_ru": "Смазочная система вулканизационного пресса 85” (централизованная)",
            "qty": 2,
        },
        {
            "num": 4,
            "brand": "Siemens / Weintek / SMC / Schneider",
            "pname_cn": "电气控制系统套装 (PLC西门子, 触摸屏, SMC气动)",
            "model": "Control system 380V±10% / 50Hz",
            "name_ru": "Комплект системы управления (ПЛК Siemens, сенсорный экран Weintek/Advantech, пневматика SMC, датчики давления/температуры Jumo, низковольтные элементы Schneider, интерфейсные кабели)",
            "qty": 2,
        },
        {
            "num": 5,
            "brand": "OEM / Китай",
            "pname_cn": "两年运行备件包 (ZIP)",
            "model": "Spare parts kit for 2 years (п. 9.2 ТЗ)",
            "name_ru": "Комплект ЗИП с учетом 2-х летней эксплуатации оборудования (уплотнения, быстроизнашивающиеся детали, клапаны)",
            "qty": 2,
        }
    ],
    "муромец": [
        {
            "num": 1,
            "brand": "Alfa Laval",
            "pname_cn": "造水机密封垫包 (Gasket set for JWP-16-C40)",
            "model": "98517802 / art. 3263-0964-6",
            "name_ru": "Набор прокладок для опреснителя Alfa Laval JWP-16-C40 (судно Viktor Vasnetsov); article 3263-0964-6, кат. № 98517802",
            "qty": 1,
        },
        {
            "num": 2,
            "brand": "Alfa Laval",
            "pname_cn": "压力真空表 (Compound gauge -100%..2 Bar, D100 3/8\" BN)",
            "model": "98430308-00",
            "name_ru": "Мановакуумметр Compound gauge -100% - 2 Bar LB/in2, D100 3/8'' BN для опреснителя Alfa Laval JWP-16-C40; Art. № 98430308-00",
            "qty": 1,
        },
        {
            "num": 3,
            "brand": "Alfa Laval",
            "pname_cn": "黄铜视镜带垫圈 (Sight Glass incl. Gasket 1 1/2\" BRASS)",
            "model": "98435689-00",
            "name_ru": "Смотровое стекло в сборе с прокладкой Sight Glass incl Gasket 1 1/2'' BRASS для опреснителя Alfa Laval JWP-16-C40; Art. № 98435689-00",
            "qty": 1,
        }
    ],
    "вентэлектро": [
        {
            "num": 1,
            "brand": "GEMU",
            "pname_cn": "隔膜阀 602 10D17F35400TM 1507",
            "model": "602 10D17F35400TM 1507",
            "name_ru": "GEMU Мембранные клапаны 602 10D17F35400TM 1507",
            "qty": 53,
        }
    ],
    "инфамед": [
        {
            "num": 1,
            "brand": "GEMU",
            "pname_cn": "隔膜 (Diaphragms) MG10, MG25, MG40",
            "model": "MG10, MG25, MG40 (EPDM/PTFE)",
            "name_ru": "Мембраны GEMU для мембранных клапанов (типоразмеры MG10, MG25, MG40)",
            "qty": 1,
        }
    ]
}


def build_default_item(item_subject: str, company_name: str) -> dict:
    """Генерирует базовую позицию, если нет детализированной спецификации."""
    # Извлекаем бренд если есть латиница
    brand_match = re.search(r'\b([A-Za-z0-9\-]+)\b', item_subject)
    brand = brand_match.group(1) if brand_match else "OEM / Китай"
    
    clean_subj = item_subject.strip()
    return {
        "num": 1,
        "brand": brand,
        "pname_cn": clean_subj,
        "model": clean_subj,
        "name_ru": f"Запрос на поставку: {clean_subj} ({company_name})",
        "qty": 1
    }


def generate_rfq_excel(company_name: str, item_subject: str, items: list = None, output_filename: str = None) -> str:
    """
    Создает чистовой Excel по эталонному шаблону Запрос КП пример заполнения.xlsx,
    заполняя позиции спецификации, шрифты Calibri 10, рамки и ширину колонок.
    Возвращает путь к сохраненному файлу на Рабочем столе.
    """
    if not os.path.exists(MASTER_TEMPLATE_PATH):
        raise FileNotFoundError(f"Мастер-шаблон не найден: {MASTER_TEMPLATE_PATH}")

    # Очищаем наименования для имени файла
    clean_comp = re.sub(r'["«»АООООПАОЗАО]', '', company_name).strip() or "Клиент"
    clean_item = re.sub(r'[\\/*?:"<>|]', '', item_subject).strip()[:35] or "Оборудование"

    if not output_filename:
        output_filename = f"Запрос КП {clean_item} {clean_comp}.xlsx"
        # Для Волтайр-Пром сохраняем каноническое имя если подходит
        if "волтайр" in company_name.lower():
            output_filename = "Запрос КП пресс для автокамер 85 Волтайр-Пром.xlsx"
        elif "муромец" in company_name.lower():
            output_filename = "Запрос КП Alfa Laval опреснитель JWP-16-C40 Илья Муромец.xlsx"

    output_path = os.path.join(DESKTOP_DIR, output_filename)

    # Определяем состав позиций
    final_items = items
    if not final_items:
        # Проверяем известную базу заявок
        low_comp = company_name.lower()
        for key, spec in KNOWN_SPECIFICATIONS.items():
            if key in low_comp:
                final_items = spec
                break

    if not final_items:
        final_items = [build_default_item(item_subject, company_name)]

    # Открываем мастер-шаблон
    wb = openpyxl.load_workbook(MASTER_TEMPLATE_PATH)
    ws = wb.active
    ws.title = "Запрос КП"

    # Стили по стандарту create_tender_excel.py
    font_data = Font(name="Calibri", size=10)
    font_num = Font(name="Calibri", size=10, bold=True)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_center = Alignment(horizontal="center", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    # Очищаем строки шаблона со 2-й и далее
    for r in range(2, ws.max_row + 1):
        for c in range(1, ws.max_column + 1):
            ws.cell(r, c).value = None

    # Заполняем позиции
    for idx, it in enumerate(final_items, start=2):
        ws.cell(idx, 1).value = it.get("num", idx - 1)
        ws.cell(idx, 1).font = font_num
        ws.cell(idx, 1).alignment = align_center
        ws.cell(idx, 1).border = thin_border

        ws.cell(idx, 2).value = it.get("brand", "OEM")
        ws.cell(idx, 2).font = font_data
        ws.cell(idx, 2).alignment = align_center
        ws.cell(idx, 2).border = thin_border

        ws.cell(idx, 3).value = it.get("pname_cn", "")
        ws.cell(idx, 3).font = font_data
        ws.cell(idx, 3).alignment = align_left
        ws.cell(idx, 3).border = thin_border

        ws.cell(idx, 4).value = it.get("model", "")
        ws.cell(idx, 4).font = font_data
        ws.cell(idx, 4).alignment = align_left
        ws.cell(idx, 4).border = thin_border

        ws.cell(idx, 5).value = it.get("name_ru", "")
        ws.cell(idx, 5).font = font_data
        ws.cell(idx, 5).alignment = align_left
        ws.cell(idx, 5).border = thin_border

        ws.cell(idx, 6).value = it.get("qty", 1)
        ws.cell(idx, 6).font = font_data
        ws.cell(idx, 6).alignment = align_center
        ws.cell(idx, 6).border = thin_border

        # Колонки цен оставляем пустыми для заполнения фабрикой
        ws.cell(idx, 7).value = None
        ws.cell(idx, 7).border = thin_border

        ws.cell(idx, 8).value = None
        ws.cell(idx, 8).border = thin_border

    # Высоты строк
    ws.row_dimensions[1].height = 28
    for r in range(2, len(final_items) + 2):
        ws.row_dimensions[r].height = 45

    # Ширина колонок
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 32
    ws.column_dimensions['D'].width = 30
    ws.column_dimensions['E'].width = 50
    ws.column_dimensions['F'].width = 12
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 20

    wb.save(output_path)
    print(f"[EXCEL-GEN] Успешно сформирован файл: {output_path} (позиций: {len(final_items)})")
    return output_path


if __name__ == "__main__":
    comp = sys.argv[1] if len(sys.argv) > 1 else "АО «Волтайр-Пром»"
    item = sys.argv[2] if len(sys.argv) > 2 else '85" 内胎硫化机'
    res = generate_rfq_excel(comp, item)
    print(f"Результат: {res}")
