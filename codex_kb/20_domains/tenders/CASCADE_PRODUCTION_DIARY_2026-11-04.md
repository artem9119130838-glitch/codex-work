# Реестр фактических изменений кода и конфигурации (04.11.2026 – 09.11.2026)

**Сервер:** `109.248.170.181:8000` (WireGuard: `10.10.0.1:8000`)  
**Ветки Git:** `main`, `main-test`  
**Диапазон коммитов:** `0835daf` .. `d4bf9d4`  

---

## 1. Таблица условий маршрутизации в `POST /documents/cascade-sieve`

Файл: `app/api/routers/document.py` (функция `cascade_sieve_endpoint`).  
Все проверки выполняются последовательно до перемещения папки в `03_stage3_approved_to_crm`. При срабатывании любого условия выполнение функции завершается возвратом соответствующего JSON-ответа.

| Порядок проверки | Проверяемое поле / условие в коде | Возвращаемый `action` | Возвращаемый `target_stage` | Возвращаемый `status` |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `stage1_res.get("has_ban") == True` (`has_national_regime_ban == true` и `has_national_regime_exceptions == false`) | `STAY_STAGE1` | `01_stage1_inbox_national_regime` | `BAN_REJECT` |
| **2** | `delivery_days is not None and delivery_days <= deadline_min` (`deadline_min = 10`) | `STAY_STAGE1` | `01_stage1_inbox_national_regime` | `REJECT_DEADLINE` |
| **3** | `delivery_days is None` | `MOVE_STAGE2` | `02_stage2_terms_and_payment` | `UNKNOWN_DEADLINE` |
| **4** | Хотя бы одно из полей `quotes["national_regime"]`, `quotes["payment_terms"]`, `quotes["delivery_time"]` входит в список `("", "—", "-", "null", "none", "цитата не найдена", "не найдено", "не указано", "ошибка обработки")` | `MOVE_STAGE2` | `02_stage2_terms_and_payment` | `MISSING_QUOTE_REVIEW` |
| **5** | `items_count > 15` (где `items_count = max(len(nomenclature_items), total_items_count)`) | `STAY_STAGE1` | `01_stage1_inbox_national_regime` | `REJECT_TOO_MANY_ITEMS` |
| **6** | `re.search(r'\b' + keyword, combined_item_text)` по списку `FSTEK_KEYWORDS` (`шифровани`, `криптографи`, `оптическ`, `тепловизор`, `лазер`, `радиостанц`, `раци[ияюей]\b`, `спецсплав`, `прицел`) | `MOVE_STAGE2` | `02_stage2_terms_and_payment` | `FSTEK_SUSPICION` |
| **7** | `len(nomenclature_items) == 0` (после чтения таблиц и текстового fallback) либо исключение `Exception` в блоке номенклатуры | `MOVE_STAGE2` | `02_stage2_terms_and_payment` | `UNKNOWN_NOMENCLATURE` |
| **8** | Все предыдущие условия не сработали | `MOVE_STAGE3` | `03_stage3_approved_to_crm` | `GREEN_APPROVED` |

### Отключенные проверки:
1. **`has_prepayment` (наличие аванса):** проверка удалена в коммите `839131e`. Отсутствие аванса (100% постоплата) не изменяет маршрут папки.
2. **`requires_conformity_certificate` (сертификат соответствия / ОТК):** проверка `REJECT_CERTIFICATE` удалена в коммите `616ec9b`. Поле продолжает извлекаться в `stage2_res`, но не влияет на `action` и `status`.
3. **`requires_qms_audit` (СМК ИСО 9001):** не проверяется и не изменяет маршрут папки.

---

## 2. Пофайловый перечень фактических изменений

### 2.1. `docker-compose.prod.yml` и `docker-compose.yml` (коммит `b8ceb52`)
* Добавлен сервис `rabbitmq`:
  * Образ: `rabbitmq:3-alpine`, имя контейнера: `tender-rabbitmq`.
  * Переменные окружения: `RABBITMQ_DEFAULT_USER=guest`, `RABBITMQ_DEFAULT_PASS=guest`.
  * Сеть: `tender-network`.
* Добавлен сервис `worker`:
  * Сборка из текущего `Dockerfile`, имя контейнера: `tender-worker-prod`.
  * Команда запуска: `["python3", "-u", "-m", "app.workers.tender_worker"]`.
  * Зависимость: `depends_on: [rabbitmq]`.
  * Подключенные тома: `./app:/app/app`, `./logs:/app/logs`.
* В сервисе `api` (`tender-rag-api-prod`) добавлен блок `depends_on: [rabbitmq, worker]`.

---

### 2.2. `app/api/routers/health.py` (коммит `c5d5a39`)
* Добавлен эндпоинт `GET /health/queue`.
* Логика работы: подключается к `RABBITMQ_URL` (`amqp://guest:guest@rabbitmq:5672/`), объявляет очередь `tender_processing` (`passive=True`) и возвращает JSON со значениями:
  * `rabbitmq_connected` (`bool`),
  * `queue_name` (`"tender_processing"`),
  * `worker_consumers` (`int` — количество активных консьюмеров очереди),
  * `queued_messages` (`int` — количество сообщений в очереди),
  * `in_process_fallback_ready` (`bool`).

---

### 2.3. `app/workers/tender_worker.py` (коммиты `cb19635`, `3e33fe6`)
* Из функции `run_stop_filters(text, tables_text)` и тела `execute_tender_pipeline(payload, trace_id)` удалены все блоки отбраковки (`REJECT_NATIONAL_REGIME`, `REJECT_DEADLINE`, `REJECT_QMS_AUDIT`, `REJECT_STRICT_TU`, `REJECT_TOO_MANY_ITEMS`, `FSTEK_REVIEW`).
* Функция `execute_tender_pipeline` при получении задачи из Папки 03 выполняет только:
  1. Извлечение текста из файлов (`extract_text_from_file`) и таблиц (`cascade_extract_tables`).
  2. Извлечение условий оплаты и сроков поставки (`LLMService.extract_payment_and_delivery_info`).
  3. Извлечение реквизитов заказчика, ИНН, НМЦК, дат и отчета на китайском языке (`LLMService.extract_tender_data`).
  4. Извлечение товарных позиций (`LLMService.extract_nomenclature_from_tables`) и их классификацию по ТН ВЭД (`VedAuditService.match_nomenclature`).
  5. Отправку итогового JSON-пакета на вебхук `N8N_WEBHOOK_URL` (`https://n8n.longwang.kz/webhook/tender-response`).

---

### 2.4. `app/services/nomenclature_parser.py` (коммит `65627b9`)
* **`KEYWORDS_SPEC`:** расширен список ключевых слов для определения файлов спецификаций: `["спецификация", "тз", "техническое задание", "расчет", "нмцк", "обоснование", "перечень", "товаров", "ведомость", "приложение"]`.
* **`extract_tables_from_excel(file_bytes, max_rows_per_sheet=450)`:**
  * *Было:* параметр `max_rows=100` применялся суммарно ко всей книге Excel; при достижении 100 строк цикл по листам прерывался (`break`).
  * *Стало:* счетчик `row_count` обнуляется для каждого листа книги (`for sheet_name in wb.sheetnames:`). С каждого листа извлекается до `450` непустых строк.
* **`extract_tables_from_word(file_bytes, max_rows_per_table=500, include_spec_paragraphs=False)`:**
  * *Было:* общий лимит `max_rows=300` на весь документ, дублирующиеся объединенные ячейки Word выводились повторно, текст вне таблиц (`doc.paragraphs`) не извлекался.
  * *Стало:* лимит установлен в `500` строк на каждую таблицу отдельно; добавлена фильтрация подряд идущих одинаковых значений ячеек в строке (`if not deduped or c != deduped[-1]`); если `include_spec_paragraphs == True` или сумма строк во всех таблицах файла `< 5`, к результату добавляется текст параграфов документа (`para_text[:20000]`).
* **`extract_text_from_pdf(file_bytes, max_chars=35000)`:**
  * Лимит символов увеличен с `20000` до `35000` (и с `10000` до `25000` для резервного чтения страниц).
  * Список ключевых слов табличных страниц дополнен маркерами `"техническое задание"`, `"п/п"`, `"позиц"`, `"товар"`, `"характеристик"`.
* **`cascade_extract_tables(files)`:**
  * Общий лимит возвращаемого текста таблиц увеличен с `40000` до `65000` символов.

---

### 2.5. `app/services/llm_service.py` (коммиты `65627b9`, `d4bf9d4`)
* **`_call_deepseek`:** таймаут HTTP-запроса к `https://api.deepseek.com/chat/completions` увеличен с `timeout=60` до `timeout=90` секунд.
* **`extract_nomenclature_from_tables(tables_text)`:**
  * *Было:* запрашивался JSON-массив `[{"name": "...", "quantity": 10.5, "unit": "шт"}]` без отдельного подсчета общего числа строк и без ограничения длины массива.
  * *Стало:* запрашивается JSON-объект со структурой:
    ```json
    {
      "total_items_count": 1,
      "items": [
        {
          "name": "Наименование товара и основные характеристики (как в таблице)",
          "quantity": 10.5,
          "unit": "шт"
        }
      ]
    }
    ```
  * В промпт добавлены 4 правила:
    1. При наличии сводной строки предмета закупки и детальной таблицы ТЗ/спецификации — считать позиции по детальной таблице.
    2. Не объединять однотипные товары, размеры, марки и артикулы в одну позицию.
    3. Записывать общее число позиций спецификации в поле `"total_items_count"`.
    4. При `total_items_count > 25` возвращать первые 25 позиций в массиве `"items"` и полное количество позиций в `"total_items_count"`.
  * При постобработке ответа в каждый элемент списка записываются оба ключа `"name"` и `"product_name"` с одинаковым значением, а также поле `"total_items_count" = max(len(items), int(extracted.get("total_items_count") or 0))`.
* **`classify_ved_products(product_names, web_hints=None)`:**
  * Добавлен необязательный параметр `web_hints: dict[str, list[str]] | None = None`.
  * Если для товара переданы строки в `web_hints[name]`, они подставляются в промпт под наименованием товара в блоке `[Справочные данные из интернет-базы таможенных деклараций ТН ВЭД: ...]`.

---

### 2.6. `app/services/ved_audit_service.py` и `app/api/routers/ved.py` (коммит `d4bf9d4`)
* **Разделение файлов Белой базы:**
  * Базовый файл (отслеживается в Git, только для чтения): `WHITE_BASE_JSON = app/data/white_nomenclature.json`.
  * Накопительный файл подтвержденных позиций (в каталоге `logs/`, исключенном из Git, общий том для контейнеров `api` и `worker`): `LEARNED_WHITE_BASE_JSON = logs/white_nomenclature_learned.json`.
  * В `VedAuditService._load_white_base_cache()` добавлена проверка `LEARNED_WHITE_BASE_JSON.stat().st_mtime != cls._learned_mtime`. При изменении файла на диске кэш в памяти перезагружается и объединяет записи из обоих файлов (записи из `learned` имеют приоритет при совпадении `normalized_name`).
* **Поиск примеров таможенного декларирования в интернете (`VedAuditService.search_hs_code_in_web(product_name, timeout=3.5)`):**
  * Формирует поисковый запрос из очищенного наименования товара (удаляются номера ГОСТ/ТУ, размеры вида `120х50` и предлоги).
  * Выполняет HTTP GET запрос к `https://www.ifcg.ru/kb/tnved/search/?q=<запрос>` с таймаутом `3.5` секунды.
  * Извлекает регулярным выражением `href=["\']/kb/tnved/(\d{10})/?["\']` 10-значные коды ТН ВЭД и текстовые описания деклараций (до 5 уникальных примеров).
  * При любой сетевой ошибке или превышении таймаута возвращает `{"found": False, "query_used": "", "top_codes": [], "examples": []}` без генерации исключений.
* **Онлайн-проверка пошлины ЕТТ ЕАЭС (`VedAuditService.fetch_live_ett_tariff_from_web(clean_code, timeout=3.0)`):**
  * Вызывается внутри `query_ett_tariff(hs_code_candidate)`, если 10-значный код не найден в PostgreSQL и локальном файле `app/data/ett_customs_tariff.json`.
  * Выполняет HTTP GET запрос к `https://www.ifcg.ru/kb/tnved/{clean_code}/` с таймаутом `3.0` секунды.
  * Извлекает значение поля `Импортная пошлина:` (числовой процент или `"Беспошлинно"` -> `0.0%`) и возвращает структуру тарифа с флагом `"web_verified": True`.
* **Каскадный пайплайн `VedAuditService.match_nomenclature(nomenclature_data)`:**
  1. Проверяет каждую позицию через `find_in_white_base(product_name, threshold=0.75)`. При совпадении присваивает `ved_source = "WHITE_BASE"`.
  2. Для ненайденных позиций запускает параллельный опрос `search_hs_code_in_web` через `ThreadPoolExecutor(max_workers=5)`.
  3. Передает список ненайденных товаров и словарь `web_hints` в `LLMService.classify_ved_products(chunk, web_hints=chunk_hints)`.
  4. Проверяет полученный код ТН ВЭД через `query_ett_tariff(candidate_hs)` (локальная база + онлайн-тариф) и присваивает `ved_source`:
     * `"WEB_ETT_10"` — 10-значный код найден с участием веб-поиска и подтвержден тарифом ЕТТ;
     * `"ETT_OFFICIAL_10"` — 10-значный код определен ИИ и подтвержден тарифом ЕТТ;
     * `"ETT_RANGE_SUB"` — совпадение на уровне 4–6 знаков (вилка пошлин);
     * `"AI_FALLBACK"` — код не найден в справочнике тарифов.
* **Сохранение проверенных позиций (`VedAuditService.add_verified_item` и `POST /ved/learn`):**
  * Добавлена валидация длины очищенного кода ТН ВЭД: `6 <= len(clean_code) <= 10` (при несоответствии запись отклоняется и функция возвращает `False`).
  * Параметр `duty_rate` в `POST /ved/learn` сделан необязательным (`float | None = None`). Если `duty_rate is None` или `< 0`, ставка пошлины автоматически запрашивается через `query_ett_tariff(clean_code)`.
  * Запись сохраняется в PostgreSQL (при наличии `DATABASE_URL`) и в `logs/white_nomenclature_learned.json`.
* **Новый эндпоинт `POST /ved/classify` (`app/api/routers/ved.py`):**
  * Принимает список товаров `{"items": [{"name": "...", "quantity": 1, "unit": "шт"}]}` и возвращает результат работы `VedAuditService.match_nomenclature(raw_items)`.

---

### 2.7. `app/api/routers/document.py` (коммиты `7a4495b`, `3e33fe6`, `65627b9`, `d4bf9d4`)
* В `POST /documents/prefilter` добавлен перехват ошибок подключения к RabbitMQ с запуском `asyncio.create_task(execute_tender_pipeline(payload, trace_id))` внутри процесса API.
* В `POST /documents/cascade-sieve`:
  * Добавлен вызов `LLMService.extract_nomenclature_from_tables(combined_text[:25000])`, если из таблиц (`cascade_extract_tables`) вернулся пустой список позиций.
  * Для папок с `items_count <= 15` добавлен вызов `stage2_res["ved_items"] = VedAuditService.match_nomenclature(nomenclature_items)`.
  * Перед возвратом любого ответа вызывается `_finalize_verdict`, записывающий данные папки в локальный Excel-файл `logs/cascade_audit_registry.xlsx` (Лист 1: `"Реестр для Александры"`, Лист 2: `"Верификация ТН ВЭД"`).
* Добавлен эндпоинт `GET /documents/cascade-audit-excel` для скачивания файла `logs/cascade_audit_registry.xlsx`.

---

### 2.8. `scripts/google_apps_script_cascade_sync.js` (коммиты `7a4495b`, `b1a6426`, `d4bf9d4`)
* В `CONFIG.ENVIRONMENTS.PROD` добавлен адрес `vedLearnUrl: 'http://109.248.170.181:8000/ved/learn'`.
* Добавлена функция `getOrCreateAuditSheet()`:
  * Создает (или открывает по `PropertiesService.getScriptProperties().getProperty('cascade_audit_sheet_id')`) таблицу `Реестр каскадной верификации тендеров (Аудит Александры)` на Google Диске в родительской директории Папки 01.
  * Формирует **Лист 1 (`Реестр для Александры`)** из 19 колонок:
    `1: №`, `2: Дата и время`, `3: Папка закупки`, `4: Ссылка на папку`, `5: Заказчик`, `6: НМЦК`, `7: Статус каскада`, `8: Целевая папка`, `9: Причина / Комментарий ИИ`, `10: ЦИТАТА: Условия оплаты`, `11: Вывод ИИ: Расчеты и оплата`, `12: ЦИТАТА: Срок поставки`, `13: Вывод ИИ: Срок (дней)`, `14: ЦИТАТА: Нацрежим ПП РФ № 1875`, `15: Вывод ИИ: Статус нацрежима`, `16: Позиций в ТЗ`, `17: Состав позиций (кратко)`, `18: ПРОВЕРКА АЛЕКСАНДРЫ (ОК)`, `19: Замечания Александры`.
* Добавлена функция `formatStageLabel(action, targetStage)`:
  * Преобразует код действия в фиксированные значения колонки 8 (`Целевая папка`):
    * `STAY_STAGE1` -> `"Папка 01 (Отбраковано)"`
    * `MOVE_STAGE2` -> `"Папка 02 (На ручную проверку)"`
    * `MOVE_STAGE3` -> `"Папка 03 (Одобрено в CRM)"`
* Добавлена функция `appendAuditRowToSheet(folder, result)`:
  * Проверяет наличие `folderId` в колонке 4 (`Ссылка на папку`). Если строка уже существует — обновляет только колонку 8 (`Целевая папка`) и цвет ячейки статуса (колонка 7), не изменяя остальные ячейки строки. Если `folderId` отсутствует — дописывает новую строку в конец листа.
* Добавлена функция `backfillProcessedFoldersToSheet()`:
  * Сканирует Папки 01, 02 и 03 на наличие папок с текстом `[КАСКАДНЫЙ ВЕРДИКТ:` в описании (`folder.getDescription()`), извлекает регулярными выражениями статус, код действия и 3 цитаты и передает их в `appendAuditRowToSheet`.
* Добавлена функция `getOrCreateVedSheet()` и `appendVedRowsToSheet(folder, result)`:
  * Создает в той же книге **Лист 2 (`Верификация ТН ВЭД`)** из 16 колонок:
    `1: №`, `2: Дата и время`, `3: Папка закупки`, `4: Ссылка на папку`, `5: Наименование товара (из ТЗ)`, `6: Кол-во и ед. изм.`, `7: Предложенный код ТН ВЭД`, `8: Ставка пошлины (%)`, `9: Разрешительные документы (ТР ТС)`, `10: Источник кода`, `11: Обоснование ИИ и примеры из интернета`, `12: ПОДТВЕРЖДЕНИЕ АЛЕКСАНДРЫ (ОК / Исправлено)`, `13: Правильный код ТН ВЭД (если исправлено)`, `14: Правильная пошлина % (опц.)`, `15: Комментарий Александры`, `16: Статус Белой базы`.
  * Записывает массив `result.details.ved_items` с проверкой дублей по связке `(folderId + Наименование товара)`.
* Добавлена функция `syncVerifiedVedItemsToWhiteBase()` (вызывается внутри `runFullCascadeSync()`):
  * Считывает строки листа `Верификация ТН ВЭД`, где в колонке 16 (`Статус Белой базы`) нет символа `✅`, а в колонке 12 указано одно из значений `("ок", "ok", "да", "исправлено", "проверено")` либо в колонке 13 заполнено от 6 до 10 цифр кода ТН ВЭД.
  * Отправляет отобранные позиции POST-запросом на `http://109.248.170.181:8000/ved/learn`.
  * При ответе `HTTP 200` записывает в колонку 16 значение `"✅ Сохранено в Белую базу (<дата и время>)"`.

---

### 2.9. `workflows/n8n/Cascade_VED_Audit_Bitrix24_v2.json` (коммиты `ea1e9ea`, `3aae839`)
* Узел **`Parse JSON Answer1`:** из переменной `chatMessage` удалена подстрока `"== КАСКАДНЫЙ КОНВЕЙЕР (ПАПКА 03: ЗЕЛЕНЫЙ КОРИДОР) ==\n"`.
* Узел **`Create Task1`:** параметры создания задачи в Битрикс24 изменены на:
  * `fields[RESPONSIBLE_ID] = "38"`
  * `fields[CREATED_BY] = "38"`
  * `fields[ACCOMPLICES][0] = "20"`, `fields[ACCOMPLICES][1] = "84"`, `fields[ACCOMPLICES][2] = "30"`, `fields[ACCOMPLICES][3] = "86"`.

---

## 3. Фактические ответы сервера при тестировании (`109.248.170.181:8000`)

1. **Запрос `GET http://109.248.170.181:8000/health/queue`:**
   ```json
   {
     "status": "ok",
     "mode": "rabbitmq_container",
     "rabbitmq_connected": true,
     "queue_name": "tender_processing",
     "worker_consumers": 1,
     "queued_messages": 0,
     "in_process_fallback_ready": true
   }
   ```

2. **Запрос `POST http://109.248.170.181:8000/documents/cascade-sieve`** (входные данные: `Договор.docx` с `requires_conformity_certificate = true`, срок 35 дней, все 3 цитаты присутствуют; `Спецификация.xlsx` — Лист 1 на 115 строк текста, Лист 2 на 42 строки товарных позиций):
   ```json
   {
     "action": "STAY_STAGE1",
     "status": "REJECT_TOO_MANY_ITEMS",
     "reason": "Отбраковано: слишком большая номенклатура (42 позиций > 15).",
     "items_count": 42,
     "requires_cc": true
   }
   ```

3. **Запрос `POST http://109.248.170.181:8000/ved/classify`** (входные данные: позиция №1 `"Сопло 3D, 1,2 мм IIVI"`, позиция №2 `"Осциллограф цифровой запоминающий DS1104Z"`):
   ```json
   {
     "items": [
       {
         "name": "Сопло 3D, 1,2 мм IIVI",
         "white_base_match": true,
         "web_search_used": false,
         "ved_source": "WHITE_BASE",
         "hs_code": "8466 93 700 0",
         "duty": "0%",
         "match_confidence": 0.9
       },
       {
         "name": "Осциллограф цифровой запоминающий DS1104Z",
         "white_base_match": false,
         "ai_classified": true,
         "web_search_used": true,
         "official_ett_verified": true,
         "ved_source": "WEB_ETT_10",
         "hs_code": "9030 20 100 0",
         "duty": "5%"
       }
     ]
   }
   ```
