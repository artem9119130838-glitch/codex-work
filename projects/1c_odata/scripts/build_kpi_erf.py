# -*- coding: utf-8 -*-
"""
Канонический скрипт сборки внешнего отчета 1С «KPI Менеджеров» (KPIМенеджеров_new_fixed3.erf)
с динамическим расчетом 64-битных смещений заголовка потока СКД (len1, len2)
для гарантированного предотвращения ошибок парсинга XDTO (Extra content at the end of the document).
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
template_erf = os.path.join(base_dir, "KPIМенеджеров_new_fixed3.erf.bak")
if not os.path.exists(template_erf):
    template_erf = os.path.join(base_dir, "KPIМенеджеров_new_fixed3.erf")

dst_erf = os.path.join(base_dir, "KPIМенеджеров_new_fixed3.erf")
desktop_erf = os.path.join(r"C:\Users\Артем\Desktop", "KPIМенеджеров_new_fixed3.erf")
path_sql_fact = os.path.join(base_dir, "Запрос_Факт.sql")

print(f"Шаблон отчета: {template_erf}")
print(f"Файл запроса Факт: {path_sql_fact}")

with open(path_sql_fact, 'r', encoding='utf-8') as f:
    new_query_fact = f.read()

# Создаем временную рабочую директорию
temp_work_dir = tempfile.mkdtemp()
try:
    # 1. Распаковываем шаблон отчета
    unpacked_dir = os.path.join(temp_work_dir, "unpacked")
    onec_dtools.extract(template_erf, unpacked_dir)
    print("Отчет успешно распакован во временную директорию.")

    # 2. Читаем бинарный поток СКД 49cba0ff-2c09-4d73-8af1-60811e06c46e.0
    stream_file = os.path.join(unpacked_dir, "49cba0ff-2c09-4d73-8af1-60811e06c46e.0")
    with open(stream_file, 'rb') as f:
        raw_data = f.read()

    p1 = raw_data.find(b'<?xml')
    p2 = raw_data.find(b'<?xml', p1 + 5)
    p3 = raw_data.find(b'<?xml', p2 + 5)

    doc1_raw = raw_data[p1:p2-3].decode('utf-8')
    doc2_raw = raw_data[p2:p3-3].decode('utf-8')
    doc3_raw = raw_data[p3:].decode('utf-8')

    # 3. Подставляем обновленный SQL-запрос факта
    escaped_fact = html.escape(new_query_fact)
    target_fact_name = "<name>НаборДанных_Факт</name>"
    idx_fact = doc1_raw.find(target_fact_name)
    if idx_fact == -1:
        raise ValueError("НаборДанных_Факт не найден в СКД!")

    q_fact_start = doc1_raw.find("<query>", idx_fact)
    q_fact_end = doc1_raw.find("</query>", q_fact_start)
    doc1_raw = doc1_raw[:q_fact_start+7] + "\n" + escaped_fact + "\n" + doc1_raw[q_fact_end:]

    # 4. Проверяем валидность XML всех трех документов СКД
    ET.fromstring(doc1_raw.encode('utf-8'))
    ET.fromstring(doc2_raw.encode('utf-8'))
    ET.fromstring(doc3_raw.encode('utf-8'))
    print("XML-схемы валидны.")

    # 5. Собираем бинарный поток СКД с точными заголовками len1, len2
    doc1_bytes = doc1_raw.encode('utf-8')
    doc2_bytes = doc2_raw.encode('utf-8')
    doc3_bytes = doc3_raw.encode('utf-8')
    BOM = b'\xef\xbb\xbf'

    len1 = len(doc1_bytes) + len(BOM)
    len2 = len(doc2_bytes) + len(BOM)

    header = struct.pack('<IIQQ', 0, 1, len1, len2)
    new_stream_content = header + BOM + doc1_bytes + BOM + doc2_bytes + BOM + doc3_bytes

    with open(stream_file, 'wb') as f:
        f.write(new_stream_content)

    # 6. Компиляция внешнего отчета (.erf)
    temp_built_erf = os.path.join(temp_work_dir, "built.erf")
    onec_dtools.build(unpacked_dir, temp_built_erf)
    print(f"Отчет успешно собран: {os.path.getsize(temp_built_erf)} байт.")

    # 7. Верификация распаковкой
    verify_dir = os.path.join(temp_work_dir, "verify")
    onec_dtools.extract(temp_built_erf, verify_dir)
    with open(os.path.join(verify_dir, "49cba0ff-2c09-4d73-8af1-60811e06c46e.0"), 'rb') as vf:
        v_data = vf.read()
    vb1, vb2, vlen1, vlen2 = struct.unpack('<IIQQ', v_data[:24])
    vp1 = v_data.find(b'<?xml')
    vp2 = v_data.find(b'<?xml', vp1 + 5)
    vp3 = v_data.find(b'<?xml', vp2 + 5)
    assert vlen1 == vp2 - vp1, f"len1 mismatch: {vlen1} vs {vp2 - vp1}"
    assert vlen2 == vp3 - vp2, f"len2 mismatch: {vlen2} vs {vp3 - vp2}"
    print("Верификация успешна: бинарные смещения len1 и len2 совпадают на 100%!")

    # 8. Копирование готового отчета в целевые директории
    shutil.copy2(temp_built_erf, dst_erf)
    print(f"Обновлен файл в проекте: {dst_erf}")

    if os.path.exists(os.path.dirname(desktop_erf)):
        shutil.copy2(temp_built_erf, desktop_erf)
        print(f"Обновлен файл на Рабочем столе: {desktop_erf}")

finally:
    shutil.rmtree(temp_work_dir, onexc=remove_readonly)
    print("Временные файлы очищены.")
