# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/build_china_kpi_erf.py
=================================================
Скрипт автономной сборки внешнего отчета 1С:УНФ:
«KPI китайских менеджеров (Снабжение)» (KPI_Китайских_Менеджеров.erf).

Структура отчета:
1. Заказ покупателя (с полем Покупатель с разделением)
2. Номенклатура
3. Поставщик (Фабрика КНР)
4. Приходная накладная

Фильтрация по периоду: строго по дате РАСХОДНОЙ НАКЛАДНОЙ (отгрузки клиенту).
Ресурсы: Количество, СтоимостьЗакупкиCNY, ПремияСнабженияCNY (1%).
"""

import os
import sys
import stat
import struct
import shutil
import tempfile
import html
import xml.etree.ElementTree as ET
import onec_dtools

sys.stdout.reconfigure(encoding='utf-8')

def remove_readonly(fn, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        fn(path)
    except Exception as e:
        print(f"Предупреждение при удалении {path}: {e}")

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
template_erf = os.path.join(base_dir, "KPIМенеджеров_new_fixed3.erf")
dst_project_erf = os.path.join(base_dir, "KPI_Китайских_Менеджеров.erf")
desktop_erf = os.path.join(r"C:\Users\Артем\Desktop", "KPI_Китайских_Менеджеров.erf")
path_sql = os.path.join(base_dir, "Запрос_Снабжение_CNY.sql")

print(f"Базовый шаблон: {template_erf}")
print(f"Файл SQL-запроса: {path_sql}")
print(f"Целевой отчет в проекте: {dst_project_erf}")
print(f"Целевой отчет на Рабочем столе: {desktop_erf}")

with open(path_sql, 'r', encoding='utf-8') as f:
    sql_query = f.read()

escaped_query = html.escape(sql_query)

# 1. Формируем doc1 (СхемаКомпоновкиДанных)
doc1_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<SchemaFile xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<dataCompositionSchema xmlns="http://v8.1c.ru/8.1/data-composition-system/schema">
		<dataSource>
			<name>ИсточникДанных1</name>
			<dataSourceType>Local</dataSourceType>
		</dataSource>
		<dataSet xsi:type="DataSetQuery">
			<name>НаборДанных_ЗакупкиCNY</name>
			<field xsi:type="DataSetFieldField">
				<dataPath>ЗаказПокупателя</dataPath>
				<field>ЗаказПокупателя</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Заказ покупателя</d5p1:content>
					</d5p1:item>
				</title>
				<role>
					<dimension xmlns="http://v8.1c.ru/8.1/data-composition-system/common">true</dimension>
				</role>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>Покупатель</dataPath>
				<field>Покупатель</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Покупатель</d5p1:content>
					</d5p1:item>
				</title>
				<role>
					<dimension xmlns="http://v8.1c.ru/8.1/data-composition-system/common">true</dimension>
				</role>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>Номенклатура</dataPath>
				<field>Номенклатура</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Номенклатура</d5p1:content>
					</d5p1:item>
				</title>
				<role>
					<dimension xmlns="http://v8.1c.ru/8.1/data-composition-system/common">true</dimension>
				</role>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>Поставщик</dataPath>
				<field>Поставщик</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Поставщик (Фабрика КНР)</d5p1:content>
					</d5p1:item>
				</title>
				<role>
					<dimension xmlns="http://v8.1c.ru/8.1/data-composition-system/common">true</dimension>
				</role>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>ПриходнаяНакладная</dataPath>
				<field>ПриходнаяНакладная</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Приходная накладная</d5p1:content>
					</d5p1:item>
				</title>
				<role>
					<dimension xmlns="http://v8.1c.ru/8.1/data-composition-system/common">true</dimension>
				</role>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>Количество</dataPath>
				<field>Количество</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Количество</d5p1:content>
					</d5p1:item>
				</title>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>СтоимостьЗакупкиCNY</dataPath>
				<field>СтоимостьЗакупкиCNY</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Закупка (юани CNY, ¥)</d5p1:content>
					</d5p1:item>
				</title>
				<appearance/>
				<inputParameters/>
			</field>
			<field xsi:type="DataSetFieldField">
				<dataPath>ПремияСнабженияCNY</dataPath>
				<field>ПремияСнабженияCNY</field>
				<title xmlns:d5p1="http://v8.1c.ru/8.1/data/core" xsi:type="d5p1:LocalStringType">
					<d5p1:item>
						<d5p1:lang>ru</d5p1:lang>
						<d5p1:content>Премия снабжения (1% CNY, ¥)</d5p1:content>
					</d5p1:item>
				</title>
				<appearance/>
				<inputParameters/>
			</field>
			<dataSource>ИсточникДанных1</dataSource>
			<query>{escaped_query}</query>
		</dataSet>
		<totalField>
			<dataPath>Количество</dataPath>
			<expression>Сумма(Количество)</expression>
		</totalField>
		<totalField>
			<dataPath>СтоимостьЗакупкиCNY</dataPath>
			<expression>Сумма(СтоимостьЗакупкиCNY)</expression>
		</totalField>
		<totalField>
			<dataPath>ПремияСнабженияCNY</dataPath>
			<expression>Сумма(ПремияСнабженияCNY)</expression>
		</totalField>
		<parameter>
			<name>НачалоПериода</name>
			<title xmlns:d4p1="http://v8.1c.ru/8.1/data/core" xsi:type="d4p1:LocalStringType">
				<d4p1:item>
					<d4p1:lang>ru</d4p1:lang>
					<d4p1:content>Начало периода</d4p1:content>
				</d4p1:item>
			</title>
			<valueType>
				<Type xmlns="http://v8.1c.ru/8.1/data/core">xs:dateTime</Type>
				<DateQualifiers xmlns="http://v8.1c.ru/8.1/data/core">
					<DateFractions>DateTime</DateFractions>
				</DateQualifiers>
			</valueType>
			<value xsi:type="xs:dateTime">0001-01-01T00:00:00</value>
			<useRestriction>true</useRestriction>
			<expression>&amp;Период.ДатаНачала</expression>
			<valueListAllowed>true</valueListAllowed>
			<inputParameters/>
		</parameter>
		<parameter>
			<name>КонецПериода</name>
			<title xmlns:d4p1="http://v8.1c.ru/8.1/data/core" xsi:type="d4p1:LocalStringType">
				<d4p1:item>
					<d4p1:lang>ru</d4p1:lang>
					<d4p1:content>Конец периода</d4p1:content>
				</d4p1:item>
			</title>
			<valueType>
				<Type xmlns="http://v8.1c.ru/8.1/data/core">xs:dateTime</Type>
				<DateQualifiers xmlns="http://v8.1c.ru/8.1/data/core">
					<DateFractions>DateTime</DateFractions>
				</DateQualifiers>
			</valueType>
			<value xsi:type="xs:dateTime">0001-01-01T00:00:00</value>
			<useRestriction>true</useRestriction>
			<expression>КонецПериода(&amp;Период.ДатаОкончания, "День")</expression>
			<valueListAllowed>true</valueListAllowed>
			<inputParameters/>
		</parameter>
		<parameter>
			<name>Период</name>
			<title xmlns:d4p1="http://v8.1c.ru/8.1/data/core" xsi:type="d4p1:LocalStringType">
				<d4p1:item>
					<d4p1:lang>ru</d4p1:lang>
					<d4p1:content>Период</d4p1:content>
				</d4p1:item>
			</title>
			<valueType>
				<Type xmlns="http://v8.1c.ru/8.1/data/core">StandardPeriod</Type>
			</valueType>
			<value xmlns:d4p1="http://v8.1c.ru/8.1/data/core" xsi:type="d4p1:StandardPeriod">
				<d4p1:variant xsi:type="d4p1:StandardPeriodVariant">Custom</d4p1:variant>
				<d4p1:startDate>0001-01-01T00:00:00</d4p1:startDate>
				<d4p1:endDate>0001-01-01T00:00:00</d4p1:endDate>
			</value>
			<useRestriction>false</useRestriction>
			<inputParameters/>
		</parameter>
		<parameter>
			<name>ПроцентПремии</name>
			<title xmlns:d4p1="http://v8.1c.ru/8.1/data/core" xsi:type="d4p1:LocalStringType">
				<d4p1:item>
					<d4p1:lang>ru</d4p1:lang>
					<d4p1:content>Процент премии снабжения (%)</d4p1:content>
				</d4p1:item>
			</title>
			<valueType>
				<Type xmlns="http://v8.1c.ru/8.1/data/core">xs:decimal</Type>
				<NumberQualifiers xmlns="http://v8.1c.ru/8.1/data/core">
					<Digits>5</Digits>
					<FractionDigits>2</FractionDigits>
					<AllowedSign>Any</AllowedSign>
				</NumberQualifiers>
			</valueType>
			<value xsi:type="xs:decimal">1</value>
			<useRestriction>false</useRestriction>
		</parameter>
		<settingsVariant>
			<name xmlns="http://v8.1c.ru/8.1/data-composition-system/settings">Основной</name>
			<presentation xmlns="http://v8.1c.ru/8.1/data-composition-system/settings" xsi:type="xs:string">Основной</presentation>
		</settingsVariant>
	</dataCompositionSchema>
</SchemaFile>"""

# 2. Формируем doc2 (Настройки СКД)
# Иерархия: Заказ покупателя + Покупатель -> Номенклатура -> Поставщик -> Приходная накладная
doc2_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Settings xmlns="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:pal="http://v8.1c.ru/8.1/data/ui/colors/palette" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<selection>
		<item xsi:type="SelectedItemField">
			<field>ЗаказПокупателя</field>
		</item>
		<item xsi:type="SelectedItemField">
			<field>Покупатель</field>
		</item>
		<item xsi:type="SelectedItemField">
			<field>Количество</field>
		</item>
		<item xsi:type="SelectedItemField">
			<field>СтоимостьЗакупкиCNY</field>
		</item>
		<item xsi:type="SelectedItemField">
			<field>ПремияСнабженияCNY</field>
		</item>
	</selection>
	<dataParameters>
		<dcscor:item xsi:type="SettingsParameterValue">
			<dcscor:use>false</dcscor:use>
			<dcscor:parameter>Период</dcscor:parameter>
			<dcscor:value xsi:type="v8:StandardPeriod">
				<v8:variant xsi:type="v8:StandardPeriodVariant">Custom</v8:variant>
				<v8:startDate>0001-01-01T00:00:00</v8:startDate>
				<v8:endDate>0001-01-01T00:00:00</v8:endDate>
			</dcscor:value>
			<userSettingID>12885978-9f1a-4c69-91cf-4763d365e0eb</userSettingID>
		</dcscor:item>
		<dcscor:item xsi:type="SettingsParameterValue">
			<dcscor:use>true</dcscor:use>
			<dcscor:parameter>ПроцентПремии</dcscor:parameter>
			<dcscor:value xsi:type="xs:decimal">1</dcscor:value>
			<userSettingID>abf24cdb-4067-4fe1-8f58-ef0b42f081f4</userSettingID>
		</dcscor:item>
	</dataParameters>
	<item xsi:type="StructureItemGroup">
		<groupItems>
			<item xsi:type="GroupItemField">
				<field>ЗаказПокупателя</field>
				<groupType>Items</groupType>
				<periodAdditionType>None</periodAdditionType>
				<periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionBegin>
				<periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionEnd>
			</item>
			<item xsi:type="GroupItemField">
				<field>Покупатель</field>
				<groupType>Items</groupType>
				<periodAdditionType>None</periodAdditionType>
				<periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionBegin>
				<periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionEnd>
			</item>
		</groupItems>
		<order>
			<item xsi:type="OrderItemAuto"/>
		</order>
		<selection>
			<item xsi:type="SelectedItemAuto"/>
		</selection>
		<item xsi:type="StructureItemGroup">
			<groupItems>
				<item xsi:type="GroupItemField">
					<field>Номенклатура</field>
					<groupType>Items</groupType>
					<periodAdditionType>None</periodAdditionType>
					<periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionBegin>
					<periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionEnd>
				</item>
			</groupItems>
			<order>
				<item xsi:type="OrderItemAuto"/>
			</order>
			<selection>
				<item xsi:type="SelectedItemAuto"/>
			</selection>
			<item xsi:type="StructureItemGroup">
				<groupItems>
					<item xsi:type="GroupItemField">
						<field>Поставщик</field>
						<groupType>Items</groupType>
						<periodAdditionType>None</periodAdditionType>
						<periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionBegin>
						<periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionEnd>
					</item>
				</groupItems>
				<order>
					<item xsi:type="OrderItemAuto"/>
				</order>
				<selection>
					<item xsi:type="SelectedItemAuto"/>
				</selection>
				<item xsi:type="StructureItemGroup">
					<groupItems>
						<item xsi:type="GroupItemField">
							<field>ПриходнаяНакладная</field>
							<groupType>Items</groupType>
							<periodAdditionType>None</periodAdditionType>
							<periodAdditionBegin xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionBegin>
							<periodAdditionEnd xsi:type="xs:dateTime">0001-01-01T00:00:00</periodAdditionEnd>
						</item>
					</groupItems>
					<order>
						<item xsi:type="OrderItemAuto"/>
					</order>
					<selection>
						<item xsi:type="SelectedItemAuto"/>
					</selection>
				</item>
			</item>
		</item>
	</item>
</Settings>"""

# 3. doc3 (Схема настроек)
doc3_xml = """<?xml version="1.0" encoding="UTF-8"?>
<SchemaFile xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<dataCompositionSchema xmlns="http://v8.1c.ru/8.1/data-composition-system/schema"/>
</SchemaFile>"""

# Валидация XML
ET.fromstring(doc1_xml.encode('utf-8'))
ET.fromstring(doc2_xml.encode('utf-8'))
ET.fromstring(doc3_xml.encode('utf-8'))
print("Все 3 XML-документа СКД успешно валидированы.")

# Сборка пакета ERF
temp_work_dir = tempfile.mkdtemp()
try:
    unpacked_dir = os.path.join(temp_work_dir, "unpacked")
    onec_dtools.extract(template_erf, unpacked_dir)
    print("Базовый архив распакован.")

    # Обновляем метаданные отчета в файле 70f354b8-52b2-4879-bbd6-f8ad8870122c
    meta_file = os.path.join(unpacked_dir, "70f354b8-52b2-4879-bbd6-f8ad8870122c")
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta_content = f.read()

    meta_content = meta_content.replace('"KPIМенеджеров"', '"KPIКитайскихМенеджеров"')
    meta_content = meta_content.replace('{1,"ru","KPIМенеджеров"}', '{1,"ru","KPI китайских менеджеров (Снабжение)"}')
    with open(meta_file, 'w', encoding='utf-8') as f:
        f.write(meta_content)
    print("Метаданные объекта отчета обновлены (KPIКитайскихМенеджеров).")

    # Пакуем поток СКД 49cba0ff-2c09-4d73-8af1-60811e06c46e.0
    stream_file = os.path.join(unpacked_dir, "49cba0ff-2c09-4d73-8af1-60811e06c46e.0")
    doc1_bytes = doc1_xml.encode('utf-8')
    doc2_bytes = doc2_xml.encode('utf-8')
    doc3_bytes = doc3_xml.encode('utf-8')

    BOM = b'\xef\xbb\xbf'
    len1 = len(doc1_bytes) + len(BOM)
    len2 = len(doc2_bytes) + len(BOM)

    header = struct.pack('<IIQQ', 0, 1, len1, len2)
    new_stream = header + BOM + doc1_bytes + BOM + doc2_bytes + BOM + doc3_bytes

    with open(stream_file, 'wb') as f:
        f.write(new_stream)
    print(f"Поток СКД сформирован: len1={len1}, len2={len2}, всего={len(new_stream)} байт.")

    # Компиляция ERF
    built_erf = os.path.join(temp_work_dir, "built.erf")
    onec_dtools.build(unpacked_dir, built_erf)
    print(f"Отчет успешно скомпилирован: {os.path.getsize(built_erf)} байт.")

    # Верификация распаковкой
    verify_dir = os.path.join(temp_work_dir, "verify")
    onec_dtools.extract(built_erf, verify_dir)
    with open(os.path.join(verify_dir, "49cba0ff-2c09-4d73-8af1-60811e06c46e.0"), 'rb') as vf:
        v_data = vf.read()
    vb1, vb2, vlen1, vlen2 = struct.unpack('<IIQQ', v_data[:24])
    vp1 = v_data.find(b'<?xml')
    vp2 = v_data.find(b'<?xml', vp1 + 5)
    vp3 = v_data.find(b'<?xml', vp2 + 5)
    assert vlen1 == vp2 - vp1, f"len1 mismatch: {vlen1} vs {vp2 - vp1}"
    assert vlen2 == vp3 - vp2, f"len2 mismatch: {vlen2} vs {vp3 - vp2}"
    print("Верификация успешна: бинарные смещения потока СКД точны на 100%!")

    # Копирование в проект и на Рабочий стол
    shutil.copy2(built_erf, dst_project_erf)
    print(f"Файл сохранен в проекте: {dst_project_erf}")
    shutil.copy2(built_erf, desktop_erf)
    print(f"Файл сохранен на Рабочем столе: {desktop_erf}")

finally:
    shutil.rmtree(temp_work_dir, onexc=remove_readonly)
    print("Временные файлы удалены.")
