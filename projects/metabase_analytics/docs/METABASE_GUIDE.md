# Руководство по эксплуатации и деплою Аналитики Metabase

> **Контур:** Продакшн (VPS `109.248.170.181:3000`)  
> **Проект:** [metabase_analytics](file:///C:/Codex/projects/metabase_analytics/README.md)  
> **Связанный навык:** [metabase_analytics_ops](file:///C:/Users/Артем/.gemini/config/skills/metabase_analytics_ops/SKILL.md)

---

## 1. Общие сведения и доступ

* **Адрес входа:** `http://109.248.170.181:3000/auth/login`
* **Роли пользователей:**
  * **Администратор:** полный доступ к созданию запросов, настройке базы данных и коллекций.
  * **Менеджер:** режим *Только чтение* (`legacy-no-self-service`). Вкладка «Данные» и конструктор запросов скрыты, доступны только утвержденные дашборды в назначенной коллекции.
* **База данных Metabase:** Внутренняя БД H2 расположена на сервере по пути `/Storage/docker/metabase_data/metabase.db/metabase.db.mv.db`.

---

## 2. Потоки данных и регулярная синхронизация

### 2.1. Real-Time синхронизация через n8n
Для автоматического попадания новых и обновленных сделок в аналитику используется исходящий вебхук Битрикс24:
1. В Битрикс24 настроен исходящий вебхук на события:
   - `Создание сделки` (`ONCRMDEALADD`)
   - `Обновление сделки` (`ONCRMDEALUPDATE`)
2. Обработчик n8n парсит данные, вытягивает связанные названия компаний и ФИО ответственных и делает `UPSERT` в PostgreSQL `marketing_db`:
   - `analytics_closed_deals`
   - `analytics_deal_stage_history`

### 2.2. Пакетная синхронизация через Python
Для инкрементальной довыгрузки или исторического бэкфилла используется боевой скрипт:
```bash
py projects/metabase_analytics/scripts/sync_analytics_dwh.py --days 30 --dry-run
py projects/metabase_analytics/scripts/sync_analytics_dwh.py --days 30
```

---

## 3. Управление дашбордами и карточками через CLI

Для обновления SQL-запросов карточек, настройки параметров фильтрации по датам (`{{date_range}}`), создания пользователей и локализации используется канонический скрипт:
```bash
# Проверка планируемых изменений (Dry-run)
py projects/metabase_analytics/scripts/manage_metabase_dashboards.py --action update-cards --dry-run

# Боевое применение изменений карточек
py projects/metabase_analytics/scripts/manage_metabase_dashboards.py --action update-cards

# Настройка разделителей чисел (пробелы для тысяч) и русской локали
py projects/metabase_analytics/scripts/manage_metabase_dashboards.py --action patch-locale
```

---

## 4. Перечень ключевых карточек Дашборда № 4

1. **Карточка 54: Сквозная воронка**
   * Отображает распределение сделок по агрегированным группам (Отказ / Подача / Победа).
   * Поддерживает динамический диапазон дат `{{date_range}}`.
2. **Карточка 49: Выигранные тендеры - Детали**
   * Выводит финансовую детализацию: НМЦК, Сумма контракта, Абсолютная дельта (руб) и % снижения.
   * Итоговая строка: сумма по деньгам и средний процент снижения.
3. **Карточка 61: Динамика сквозной воронки по периодам (помесячно)**
   * Отражает динамику этапов по календарным месяцам.
4. **Карточка 62: Сравнение периодов (Google Analytics Style)**
   * Сравнительный срез эффективности текущего месяца относительно предыдущего.
5. **Динамика переходов (За весь период)**
   * Показывает интенсивность работы с воронкой в CRM (число переходов сделок между этапами за месяц).

---

## 5. Регламент резервного копирования и восстановления

### 5.1. Резервное копирование H2 базы
База данных Metabase останавливается и копируется скриптом `/Storage/run_server_backup.sh`:
```bash
docker stop metabase
cp /Storage/docker/metabase_data/metabase.db/metabase.db.mv.db /Storage/backups/metabase_$(date +%Y%m%d).db.mv.db
docker start metabase
```

### 5.2. Сброс пароля пользователя при утере доступа
При необходимости сбросить пароль без веб-интерфейса используется Docker CLI:
```bash
docker stop metabase && \
docker run --rm -v /Storage/docker/metabase_data:/metabase-data \
  -e MB_DB_FILE=/metabase-data/metabase.db/metabase.db \
  --entrypoint "/opt/java/openjdk/bin/java" \
  metabase/metabase:latest -jar /app/metabase.jar reset-password <EMAIL> && \
docker start metabase
```
