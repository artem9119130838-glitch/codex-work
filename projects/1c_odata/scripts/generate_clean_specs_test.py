import os
import sys

sys.path.insert(0, os.path.abspath(r"C:\Codex\projects\1c_odata\scripts"))
from generate_supply_rfq_excel import generate_rfq_excel

def build_all_clean_specifications():
    specs = {}

    # 1. Стройкомплекс 78: Endress+Hauser & Baumer
    specs["eh_baumer"] = {
        "company": "ООО «СТРОЙКОМПЛЕКС 78»",
        "subject": "Endress+Hauser 质量流量计 & Baumer 传感器",
        "resp_id": 30, # Miss Wang
        "resp_name": "Miss Wang",
        "deal_title": "ООО «СТРОЙКОМПЛЕКС 78», Endress+Hauser / Baumer, 流量计及传感器 (2项), Расходомер E+H Promass F 100 и датчики Baumer (2 поз., 3 шт.)",
        "items": [
            {
                "num": 1,
                "brand": "Endress+Hauser",
                "pname_cn": "科氏力质量流量计 Promass F 100",
                "model": "8F1B08AADMAAASAD2SA+",
                "name_ru": "Высокоточный кориолисовый расходомер Endress+Hauser Promass F 100",
                "qty": 1
            },
            {
                "num": 2,
                "brand": "Baumer",
                "pname_cn": "超声波测距传感器",
                "model": "UR18.DA0-IA1B.7BO (арт. 11135775)",
                "name_ru": "Датчик ультразвуковой Baumer UR18.DA0-IA1B.7BO (арт. 11135775)",
                "qty": 2
            }
        ]
    }

    # 2. Стройкомплекс 78: Lenze мотор-редукторы
    specs["lenze"] = {
        "company": "ООО «СТРОЙКОМПЛЕКС 78»",
        "subject": "Lenze 伞齿轮减速电机",
        "resp_id": 44, # Liyan Wang
        "resp_name": "Liyan Wang",
        "deal_title": "ООО «СТРОЙКОМПЛЕКС 78», Lenze, 减速电机清单 (3项), Мотор-редукторы Lenze коническо-цилиндрические (3 поз., 3 шт.)",
        "items": [
            {
                "num": 1,
                "brand": "Lenze",
                "pname_cn": "伞齿轮-圆柱齿轮减速电机 (1.5 kW)",
                "model": "G50BH132MVCK2C (Код: 10000176997031, MHEMAXX090-32C1C, i=10.677)",
                "name_ru": "Мотор-редуктор Lenze G50BH132MVCK2C, электродвигатель MHEMAXX090-32C1C, 1.5 кВт, i=10.677, n2=134.4 об/мин, M2=103 Нм",
                "qty": 1
            },
            {
                "num": 2,
                "brand": "Lenze",
                "pname_cn": "重载伞齿轮-圆柱齿轮减速器 (P1≈4.5 kW)",
                "model": "G50BS221MHBR3C00 (Код: 10000177008666, i=76.907)",
                "name_ru": "Редуктор высокой нагрузки Lenze G50BS221MHBR3C00, i=76.907, n2=41.8 об/мин, M2=1029 Нм, вес 82.6 кг",
                "qty": 1
            },
            {
                "num": 3,
                "brand": "Lenze",
                "pname_cn": "伞齿轮-圆柱齿轮减速电机 (3.0 kW)",
                "model": "G50BH185MVBR2C00 (Код: 10000176994510, MHEMAXX100-32C1C, i=12.693)",
                "name_ru": "Мотор-редуктор Lenze G50BH185MVBR2C00, электродвигатель MHEMAXX100-32C1C, 3.0 кВт, i=12.693, n2=113.8 об/мин, M2=244 Нм",
                "qty": 1
            }
        ]
    }

    # 3. Стройкомплекс 78: RUF клапаны
    specs["ruf_valves"] = {
        "company": "ООО «СТРОЙКОМПЛЕКС 78»",
        "subject": "RUF 阀门及阀芯清单",
        "resp_id": 84, # Юйнань Ли
        "resp_name": "玉南 (Юйнань) 李",
        "deal_title": "ООО «СТРОЙКОМПЛЕКС 78», RUF, 阀门及阀芯清单 (7项), Клапаны и гидрораспределители RUF (7 поз., 7 шт.)",
        "items": [
            {"num": 1, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020858", "name_ru": "Клапан RUF 1020858", "qty": 1},
            {"num": 2, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020834", "name_ru": "Клапан RUF 1020834", "qty": 1},
            {"num": 3, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020835", "name_ru": "Клапан RUF 1020835", "qty": 1},
            {"num": 4, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020837", "name_ru": "Клапан RUF 1020837", "qty": 1},
            {"num": 5, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020860", "name_ru": "Клапан RUF 1020860", "qty": 1},
            {"num": 6, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020838", "name_ru": "Клапан RUF 1020838", "qty": 1},
            {"num": 7, "brand": "RUF", "pname_cn": "液压阀 / 阀芯", "model": "1020798", "name_ru": "Клапан RUF 1020798", "qty": 1},
        ]
    }

    # 4. Валерий Талипов: Thyssenkrupp & Flender B3SH
    specs["reductors"] = {
        "company": "Валерий Талипов (ООО «Логика»)",
        "subject": "Thyssenkrupp & Flender 工业减速机",
        "resp_id": 44, # Liyan Wang
        "resp_name": "Liyan Wang",
        "deal_title": "Валерий Талипов, Thyssenkrupp / Flender, 重型齿轮减速机 (4项), Редукторы конвейерные Thyssenkrupp и Flender B3SH (4 поз., 4 шт.)",
        "items": [
            {
                "num": 1,
                "brand": "Flender / ЦПТ",
                "pname_cn": "三级圆锥-圆柱齿轮减速机",
                "model": "B3SH18 A25",
                "name_ru": "Редуктор конвейера B3SH18 A25 трехступенчатый коническо-цилиндрический ЦПТ",
                "qty": 1
            },
            {
                "num": 2,
                "brand": "Flender / ЦПТ",
                "pname_cn": "三级圆锥-圆柱齿轮减速机",
                "model": "B3SH18 C25",
                "name_ru": "Редуктор конвейера B3SH18 C25 трехступенчатый коническо-цилиндрический ЦПТ",
                "qty": 1
            },
            {
                "num": 3,
                "brand": "Thyssenkrupp",
                "pname_cn": "桥式输送机驱动减速机 (左装)",
                "model": "4567220A",
                "name_ru": "Редуктор привода мостового конвейера левый 4567220A Thyssenkrupp",
                "qty": 1
            },
            {
                "num": 4,
                "brand": "Thyssenkrupp",
                "pname_cn": "桥式输送机驱动减速机 (右装)",
                "model": "4567220B (KSFq280So)",
                "name_ru": "Редуктор привода мостового конвейера правый 4567220B Thyssenkrupp KSFq280So",
                "qty": 1
            }
        ]
    }

    # 5. ООО «Единая Служба Снабжения»: Flender
    specs["flender"] = {
        "company": "ООО «ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ»",
        "subject": "Flender 联轴器弹性柱销组件",
        "resp_id": 84, # Юйнань Ли
        "resp_name": "玉南 (Юйнань) 李",
        "deal_title": "ООО «ЕДИНАЯ СЛУЖБА СНАБЖЕНИЯ», Flender, 联轴器配件, Палец с буфером в сборе муфты Flender 2LC0132 (72 шт.)",
        "items": [
            {
                "num": 1,
                "brand": "Flender",
                "pname_cn": "联轴器弹性销轴组件 (含缓冲胶圈)",
                "model": "2LC0132-2WC00-0AA0",
                "name_ru": "Палец с буфером в сборе муфты Flender (артикул 2LC0132-2WC00-0AA0) или качественный аналог",
                "qty": 72
            }
        ]
    }

    # 6. АО «ПЗ «Машиностроитель»: Печь камерная
    specs["pzmash"] = {
        "company": "АО «ПЗ «МАШИНОСТРОИТЕЛЬ»",
        "subject": "箱式保护气氛电炉 (1100°C 氩气气氛)",
        "resp_id": 84, # Юйнань Ли
        "resp_name": "玉南 (Юйнань) 李",
        "deal_title": "АО «ПЗ «МАШИНОСТРОИТЕЛЬ», 箱式电炉, 箱式保护气氛热处理炉 (1100°C), Камерная электропечь с защитной атмосферой аргона (1 шт.)",
        "items": [
            {
                "num": 1,
                "brand": "OEM / Китай",
                "pname_cn": "箱式保护气氛热处理电炉 (配辅助设备冷水机和压缩机)",
                "model": "Tmax=1100°C, 炉膛≥1600x1200x600mm, 90kW, 氩气保护",
                "name_ru": "Камерная электропечь для нагрева и термообработки в защитной атмосфере аргона (до 1100 °С, камера 1600х1200х600 мм, мощность до 90 кВт, чиллер и компрессор в комплекте)",
                "qty": 1
            }
        ]
    }

    return specs

if __name__ == "__main__":
    specs = build_all_clean_specifications()
    print("=== ВАЛИДАЦИЯ ЧИСТЫХ СПЕЦИФИКАЦИЙ ===")
    for k, s in specs.items():
        print(f"\n[{k.upper()}] {s['company']} | Ответственный: {s['resp_name']} (ID {s['resp_id']})")
        print(f"  Сделка: {s['deal_title']}")
        for it in s["items"]:
            print(f"    - №{it['num']} Brand: {it['brand']} | CN: {it['pname_cn']} | Model: {it['model']} | Qty: {it['qty']}")
