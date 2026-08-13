---
name: tender_automation
description: Автоматизация АСТ ГОЗ через DOM-селекторы, парсинг DOCX/PDF спецификаций с MarkItDown и Gemini, лимитирование RPM и слияние лотов в Excel.
---

# Навык: Автоматизация тендеров и парсинг (tender_automation)

Этот навык применяется при написании роботов для портала АСТ ГОЗ, разборе спецификаций тендерной документации и извлечении данных.

## 1. Парсинг таблиц и текстов из DOCX и PDF на Python

Для извлечения спецификаций из тендерной документации ИИ должен использовать проверенные методы:

### Чтение таблиц DOCX (Python-скрипт):
```python
import docx

def extract_tables_from_docx(file_path):
    doc = docx.Document(file_path)
    extracted_data = []
    
    for table_idx, table in enumerate(doc.tables):
        table_data = []
        for row in table.rows:
            row_data = [cell.text.strip().replace('\n', ' ') for cell in row.cells]
            # Дедупликация объединенных ячеек в строке
            table_data.append(row_data)
        extracted_data.append({
            "table_index": table_idx,
            "data": table_data
        })
    return extracted_data
```

### Парсинг PDF с табличной разметкой (через pdfplumber):
```python
import pdfplumber

def extract_pdf_tables(file_path):
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            extracted = page.extract_tables()
            for table in extracted:
                tables.append({
                    "page": page_idx + 1,
                    "data": table
                })
    return tables
```

---

## 2. Управление квотами LLM и Rate Limiting

При пакетной обработке тендерной документации (нарезка на чанки, извлечение спецификаций через Gemini/DeepSeek) строго следовать регламенту навыка **[llm_quota_and_fallback_manager](file:///C:/Users/Артем/.gemini/config/skills/llm_quota_and_fallback_manager/SKILL.md)**:
* Соблюдать RPM Burst Pacing (пауза 5 сек между пакетными запросами).
* Обрабатывать ошибку 429 через адаптивный парсинг `retryDelay` и автоматический фолбэк на DeepSeek API.
* Логировать расход токенов в таблицу `llm_usage_logs`.

---

## 3. Автоматизация АСТ ГОЗ через DOM-селекторы (Playwright/Puppeteer)

**Критическое правило:** Категорически запрещено использовать клики по статическим координатам (X, Y) экрана, так как это приводит к сбоям при изменении разрешения. Использовать только DOM-селекторы.

### Примеры селекторов для АСТ ГОЗ:
*   **Кнопка входа по сертификату:**
    `page.locator("a.btn-cert-login, .cert-login-btn")`
*   **Поле поиска тендеров по номеру:**
    `page.locator("input[name='searchNumber'], input#search_input")`
*   **Ссылка на скачивание документации лота:**
    `page.locator("a[href*='downloadDocument'], .download-link-class")`

### Шаблон стабильного ожидания элементов:
```javascript
// Playwright JS-шаблон
const button = page.locator('button#submit-tender');
await button.waitFor({ state: 'visible', timeout: 15000 });
await button.click();
```

---

## 4. Слияние и дедупликация лотов в Excel

При объединении файлов Excel (`excel-lot-consolidation`) ИИ должен сохранять оригинальные формулы цен и рассчитывать суммы:
```python
import openpyxl

def merge_excel_lots(file_paths, output_path):
    wb_dest = openpyxl.Workbook()
    ws_dest = wb_dest.active
    ws_dest.title = "Consolidated Lots"
    
    header_written = False
    for path in file_paths:
        wb_src = openpyxl.load_workbook(path, data_only=False) # data_only=False сохраняет формулы!
        ws_src = wb_src.active
        
        for row_idx, row in enumerate(ws_src.iter_rows(values_only=False)):
            if row_idx == 0:
                if not header_written:
                    ws_dest.append([cell.value for cell in row])
                    header_written = True
                continue
            ws_dest.append([cell.value for cell in row])
            
    wb_dest.save(output_path)
```

---

## 5. Модификация документов с сохранением форматирования (DOCX и XLSX)

### Безопасное изменение текстов в DOCX (Preserving Styles)
При изменении текста параграфа или ячейки таблицы через прямую запись `paragraph.text = "..."` библиотека `python-docx` удаляет все внутренние текстовые блоки (`runs`) и сбрасывает форматирование (жирный шрифт, курсив, размер, цвет). 

Для сохранения стилей необходимо обновлять текст точечно в существующих объектах `run`:

```python
def update_paragraph_text_keep_formatting(paragraph, new_text_runs):
    """
    paragraph: объект docx.text.paragraph.Paragraph
    new_text_runs: список строк, заменяющих текст в соответствующих runs
    """
    # Обновляем текст в первых runs, которые соответствуют новым текстам
    for i, text in enumerate(new_text_runs):
        if i < len(paragraph.runs):
            paragraph.runs[i].text = text
            
    # Зануляем текст в оставшихся runs (если исходных runs было больше)
    for run in paragraph.runs[len(new_text_runs):]:
        run.text = ""
```

*Пример обновления ячейки таблицы, где весь текст находится в одном стиле (одном run):*
```python
cell = table.rows[row_idx].cells[col_idx]
if cell.paragraphs[0].runs:
    # Записываем новый текст в первый run, сохраняя его стили
    cell.paragraphs[0].runs[0].text = "Новый текст"
    # Очищаем остальные runs в этом параграфе
    for run in cell.paragraphs[0].runs[1:]:
        run.text = ""
else:
    cell.text = "Новый текст" # Если runs не было
```

### Безопасное редактирование XLSX (Preserving Formulas)
Чтобы обновить данные в Excel-файле и при этом не сломать формулы связей умных таблиц:
1. Загружайте файл строго с флагом `data_only=False` (по умолчанию), чтобы openpyxl считывал и сохранял формулы, а не их последние вычисленные статические значения.
2. Изменяйте только ячейки с исходными данными (например, цены в CNY). Ячейки с формулами (например, расчет цены в RUB) не трогайте — Excel автоматически пересчитает их при первом открытии файла пользователем.
3. Сохраняйте файл методом `wb.save(file_path)`.
```

