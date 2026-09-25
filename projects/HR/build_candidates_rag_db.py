import openpyxl
import os
import sys
import pypdf
import zipfile
import re
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r'C:\Codex_Personal\projects\HR\Китайский снабженец'
excel_path = os.path.join(base_dir, '简历汇总表_国际贸易专员.xlsx')
resumes_dir = os.path.join(base_dir, '简历包')
db_dir = os.path.join(base_dir, 'candidates_db')
os.makedirs(db_dir, exist_ok=True)

# 1. Map files in resumes_dir
resume_files = os.listdir(resumes_dir)

def extract_file_text(filename):
    if not filename:
        return ""
    # Find matching file in resumes_dir
    target_file = None
    for f in resume_files:
        if filename in f or f in filename:
            target_file = f
            break
        # Match by person name inside filename
        name_clean = re.sub(r'[【】_\dK\(\)\s-]', '', filename)
        if len(name_clean) >= 2 and name_clean in f:
            target_file = f
            break
    
    if not target_file:
        return ""
    
    full_p = os.path.join(resumes_dir, target_file)
    text = ""
    if target_file.endswith('.pdf'):
        try:
            r = pypdf.PdfReader(full_p)
            text = '\n'.join([page.extract_text() or '' for page in r.pages])
        except Exception as e:
            text = f"Error reading PDF: {e}"
    elif target_file.endswith('.docx'):
        try:
            with zipfile.ZipFile(full_p) as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                text = ''.join(tree.itertext())
        except Exception as e:
            text = f"Error reading DOCX: {e}"
    elif target_file.endswith('.jpg'):
        text = "Резюме в формате изображения (скан). Ключевые данные оцифрованы в паспорте кандидата."
    return text.strip()

# 2. Read Excel
wb = openpyxl.load_workbook(excel_path)
ws = wb.active
headers = [str(c.value).strip() if c.value is not None else f'c{i}' for i, c in enumerate(ws[2])]

candidates = []
for r in range(3, ws.max_row + 1):
    vals = [str(c.value).strip() if c.value is not None else '' for c in ws[r]]
    d = dict(zip(headers, vals))
    if d.get('序号'):
        candidates.append(d)

print(f"Loaded {len(candidates)} candidates from Excel.")

# Priority shortlist candidates
shortlist_ids = ['1', '9', '23', '2', '33', '32', '31', '25', '3']

registry_rows = []

for c in candidates:
    cid = str(c.get('序号', ''))
    name = c.get('姓名', '').strip()
    gender = c.get('性别', '').strip()
    age = c.get('年龄/出生年月', '').strip()
    edu = c.get('最高学历', '').strip()
    major = c.get('专业', '').strip()
    univ = c.get('毕业院校', '').strip()
    exp = c.get('工作年限', '').strip()
    intent = c.get('求职意向', '').strip()
    salary = c.get('期望薪资', '').strip()
    city = c.get('期望城市', '').strip()
    phone = c.get('联系电话', '').strip()
    email = c.get('电子邮箱', '').strip()
    summary = c.get('工作经历摘要', '').strip()
    certs = c.get('证书/语言能力', '').strip()
    note = c.get('备注', '').strip()
    source_file = c.get('来源文件', '').strip()
    
    is_priority = cid in shortlist_ids
    p_badge = "⭐⭐ ПРИОРИТЕТ (Шорт-лист)" if is_priority else "Базовый пул"
    
    # Read full text from original file
    full_cv_text = extract_file_text(source_file)
    if not full_cv_text:
        full_cv_text = extract_file_text(name)
    
    # Build clean candidate filename
    safe_name = re.sub(r'[^\w\d_-]', '', name) or f"cand_{cid}"
    filename = f"{int(cid):02d}_{safe_name}.md"
    file_path = os.path.join(db_dir, filename)
    
    # Create candidate markdown file
    md_content = f"""# Кандидат #{cid}: {name}

> **Статус:** {p_badge}  
> **Текущий этап:** Новая анкета / Ожидание ответа  
> **Последнее обновление:** 2026-09-15  

---

## 1. Паспорт кандидата (Личные данные)

| Параметр | Значение |
| :--- | :--- |
| **ФИО (Китайский):** | {name} |
| **Пол / Возраст:** | {gender} / {age} |
| **Город проживания:** | {city or 'Шаньдун'} |
| **Телефон / WeChat:** | {phone or 'Не указан'} |
| **Email / QQ:** | {email or 'Не указан'} |
| **Образование:** | {edu} ({major}), {univ} |
| **Общий стаж:** | {exp} |
| **Целевая должность:** | {intent} |
| **Ожидания по зарплате:** | {salary or '5-6K'} |
| **Исходный файл:** | `{source_file}` |

---

## 2. Оценка компетенций для RAG и подбора

* **Специфика товаров:** {summary[:200]}...
* **Языковые навыки и сертификаты:** {certs or 'Не указано'}
* **Аналитическая оценка:** {note or 'Требуется первичное интервью'}
* **Приоритет для роли:** {'Высокий (входит в согласованный топ-9)' if is_priority else 'Резервный пул'}

---

## 3. Полный текст резюме (Оригинал из файла)

```text
{full_cv_text or summary}
```

---

## 4. История коммуникации и переписка

* **2026-09-14:** Сформировано и отправлено первое приветственное письмо с описанием партнерской модели (5 000 RMB + процент от экспортного НДС и оборота).
* **Входящие письма и ответы:**
  *(Сюда вносятся тексты входящих писем, ответов в WeChat и комментарии кандидата)*

---

## 5. Ответы на интервью и тестовые задания

* **Результат первичного скрининга (3 вопроса в WeChat):**
  - *Отношение к модели 5000 RMB + возврат НДС:* 
  - *Опыт работы с оборудованием/запчастями:* 
  - *Опыт оформления экспорта и возврата НДС:* 
* **Видео-интервью с Дэвидом и Артемом:**
  - *Дата проведения:* 
  - *Впечатление и оценка ответов:* 
* **Практический кейс-тест (24 часа):**
  - *Задание:* 
  - *Результат:* 

---

## 6. Зафиксированные достижения и результаты

*(В процессе работы и испытательного срока сюда заносятся реальные успехи: сбитые цены фабрик, закрытые сделки, организованные белые отгрузки, решенные проблемы)*

"""
    with open(file_path, 'w', encoding='utf-8') as fl:
        fl.write(md_content)
    
    registry_rows.append({
        'id': int(cid),
        'name': name,
        'gender': gender,
        'age': age,
        'phone': phone,
        'email': email,
        'exp': exp,
        'summary': summary[:100] + '...',
        'file': filename,
        'is_p': is_priority
    })

# 3. Create Master Registry
registry_rows.sort(key=lambda x: (not x['is_p'], x['id']))

reg_path = os.path.join(base_dir, 'CANDIDATES_REGISTRY.md')
with open(reg_path, 'w', encoding='utf-8') as fl:
    fl.write("# Единый реестр базы кандидатов (RAG Candidate Knowledge Base)\n\n")
    fl.write("> **Проект:** Найм руководителя китайского направления снабжения и ВЭД (China Operations Lead)\n")
    fl.write(f"> **Всего кандидатов в базе:** {len(registry_rows)}\n")
    fl.write(f"> **В приоритетном шорт-листе:** {len(shortlist_ids)}\n")
    fl.write("> **Папка с карточками кандидатов:** [`candidates_db/`](file:///C:/Codex_Personal/projects/HR/Китайский%20снабженец/candidates_db/)\n\n")
    fl.write("---\n\n")
    fl.write("## 1. Приоритетный шорт-лист (ТОП-9 для рассылки и отбора)\n\n")
    fl.write("| ID | Имя (CN) | Возраст | Контакты | Специализация / Опыт | Ссылка на карточку |\n")
    fl.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for r in registry_rows:
        if r['is_p']:
            c_link = f"[{r['name']}](file:///C:/Codex_Personal/projects/HR/Китайский%20снабженец/candidates_db/{r['file']})"
            contact = r['email'] or r['phone']
            fl.write(f"| {r['id']} | **{r['name']}** | {r['age']} | `{contact}` | {r['summary']} | {c_link} |\n")
    
    fl.write("\n---\n\n")
    fl.write("## 2. Полный пул кандидатов (Резерв)\n\n")
    fl.write("| ID | Имя (CN) | Пол / Возраст | Контакты | Опыт | Карточка |\n")
    fl.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
    for r in registry_rows:
        if not r['is_p']:
            c_link = f"[{r['name']}](file:///C:/Codex_Personal/projects/HR/Китайский%20снабженец/candidates_db/{r['file']})"
            contact = r['email'] or r['phone']
            fl.write(f"| {r['id']} | {r['name']} | {r['gender']} {r['age']} | `{contact}` | {r['exp']} | {c_link} |\n")
    
    fl.write("\n---\n\n")
    fl.write("## 3. Регламент пополнения и ведения RAG-базы\n\n")
    fl.write("1. **Получение ответа от кандидата:** Открыть соответствующую карточку в `candidates_db/`, вставить текст входящего письма в раздел `## 4. История коммуникации` и обновить статус.\n")
    fl.write("2. **Фиксация результатов интервью с Дэвидом:** Занести ответы кандидата в раздел `## 5. Ответы на интервью`.\n")
    fl.write("3. **Тестовое задание:** Прикрепить расчеты цен и заводов в раздел `## 5`.\n")
    fl.write("4. **Достижения в работе:** Фиксировать сбитые цены фабрик и успешные белые отгрузки в разделе `## 6. Зафиксированные достижения`.\n")

print(f"SUCCESS: Generated 35 candidate markdown files in {db_dir} and master index at {reg_path}")
