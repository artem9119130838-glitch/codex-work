# Рабочий лог задач (Personal)

- [x] Временный перенос проектов, документов и ИИ-окружения с Victus на новый ноутбук MateBook 14 (выполнен 13.08.2026).
- [x] Подготовка обратного переноса на Victus: создание конфигураций FreeFileSync (`1_MateBook_to_External.ffs_gui`, `2_External_to_Victus.ffs_gui`), скрипта адаптации путей Antigravity `fix_paths_for_victus.py` и инструкций по проверке.
- [x] Синхронизация данных с MateBook на внешний диск `E:\Mirror_E_Home` и развертывание на Victus:
  * Ветка `master` репозитория `C:\Codex_Personal` синхронизирована без конфликтов;
  * Настроен и валидирован профиль `E:\Mirror_E_Home\2_External_to_Victus.ffs_gui` (все 24 пары исправлены под фактические диски Victus);
  * В фильтр FreeFileSync добавлены исключения: `SAVE` (`Архив Бизнесов`, `iMac`, `Архивы Сайтов` — экономия ~125 ГБ) и `SOFT_D` (`Huawei Service`, `8.5.1.1150`, `Telegram Desktop`, `DigiKam`, `qBittorrent`, `DupeGuru` — экономия ~3.1 ГБ);
  * Проведен полный комплекс верификации (Python 8 библиотек OK, Git, SSH GitHub/VPS, 9/9 локальных путей, профили Edge, Punto Switcher, MobaXterm).
- [x] Внедрена политика разграничения доступов (Strict Change Policy):
  * Личный Git (`artem9119130838-glitch/codex-work.git`) — запись разрешена;
  * Рабочий Git (`wlissespanchame370-cyber/*`, включая `tender-rag-api`) — строго Read-Only;
  * VPS (`109.248.170.181`) — строго после предварительного согласования.
- [x] Проведен комплексный технический аудит наработок Михаила в ветке `main-test` (`wlissespanchame370-cyber/tender-rag-api`):
  * Изучены `daily_schedule_phase2.md`, логика каскадного отсева и принятие гипотез руководителя;
  * Выявлены критические ошибки: сломанный импорт `get_rabbitmq_channel` в `document.py`, отсутствие векторов эмбеддингов в `white_base_init.sql` (все NULL) + синтаксическая ошибка SQL на строке 17, хардкод путей MacOS в `import_white_base.py`, синхронный опрос Gemini в цикле без использования пула ключей.
- [x] Выполнение задачи Михаила по созданию карты архитектуры сети docs/ARCHITECTURE_MAP.md на VPS и пуш в GitHub ветки main (artem9119130838-glitch и wlissespanchame370-cyber).
- [x] Настройка изолированного окружения для Михаила на VPS (пользователь `mikhail`, доступ только к `/home/mikhail/tender-rag-api`, запрет прямого Docker, белый список в `sudoers` только для деплоя и логов своих сервисов, блокировка 1С и Postgres, сохранение ключа `id_ed25519_mikhail`).
- [x] Развертывание демона автодеплоя по вебхуку `tender-webhook-deploy.service` (порт 9876) с защитой секретным токеном.
- [x] Ликвидация сбоя n8n и защита от раздувания базы: сжатие `database.sqlite` в `n8n-eng` с 14 ГБ до 1.26 МБ, устранение ошибки миграции `CreateTagEntity`, включение `EXECUTIONS_DATA_SAVE_ON_SUCCESS=none`, `EXECUTIONS_DATA_MAX_AGE=48` и еженедельного скрипта обслуживания SQLite в `cron.weekly`.
- [x] Полная синхронизация мастер-каталогов и базы знаний: сохранение локальных копий VPS-скриптов в `scripts/vps/`, регистрация в [SCRIPTS_CATALOG.md](file:///C:/Codex_Personal/codex_kb/SCRIPTS_CATALOG.md) (Домены 6 и 14), актуализация [SERVER_VPS.md](file:///C:/Codex_Personal/codex_kb/10_assets/SERVER_VPS.md), реестра 14 доменов в [GRAVITY_CONTROL_CENTER.md](file:///C:/Codex_Personal/codex_kb/00_control/GRAVITY_CONTROL_CENTER.md) и подтверждение индекса всех 12 навыков в [SKILLS.md](file:///C:/Codex_Personal/SKILLS.md).
- [x] Решить проблему приведения типов параметров периода (`&НачалоПериода` и `&КонецПериода` в СКД) и задвоения себестоимости при интеграции пакетного SQL-запроса в отчет `KPIМенеджеров.erf`.
- [x] Добавлена иконка MAX со ссылкой на бота и адрес почты прописью в шапку сайта [longwang.ru](http://longwang.ru) (исправлена верстка иконки в [custom.css](file:///C:/Codex_Personal/projects/GoW%20Project/themes/themes/longwang/custom.css)).
- [x] Восстановлен доступ и сброшены пароли в Metabase: учетные данные (`admin@tender-rag.local` / `Artem12345`, `manager@tender-rag.local` / `manager12345`) и быстрая команда CLI-сброса сохранены в базе знаний и навыке `metabase_analytics_ops`.
- [/] Найм руководителя снабжения и ВЭД в Китае:
  * Зафиксирован отказ Nancy Qin (覃显清, Дечжоу);
  * В диалоге топ-кандидат Ван Ванъюн (王万勇, Дечжоу, экс-Alibaba/Meituan);
  * **18.09 получен положительный ответ от кандидата №31 Анны / 安女士 («快乐女孩», 465387856@qq.com, Циндао, 7 лет стажа ВЭД/1688)**: безоговорочно согласна на базовый оклад 5000 RMB + мотивационный пул (1% GMV + 10% 退税), имеет выходы на машиностроение и логистику, запросила онлайн-интервью. Подготовлен план созвона с Дэвидом.
- [/] Восстановление графической подсистемы HP Victus 16 (i7-12700H, RTX 3060, CMN1619):
  * [x] Устранена ошибка NVIDIA Код 43 (возврат на Optimus пакет `32.0.15.9649` `nvhmi.inf`, статус OK).
  * [x] Очищен кэш поврежденных мониторов `SIMULATED` в реестре, отключен баг MPO (`DisableOverlays = 1`) и гибридный сон (`HiberbootEnabled = 0`).
  * [x] Настроен загрузчик BCD: включена классическая клавиша `F8` (`legacy`), удален лишний дубликат меню Safe Mode, отключен таймаут загрузчика для мгновенного старта.
  * [x] Полностью заблокированы баннеры проверки лицензии Adobe Acrobat (`fix_acrobat_genuine.ps1`).
  * [/] Локализация причин черного экрана Intel Iris Xe (PSR2/DRRS/Link Training 144 Гц), подготовка чистого отката на заводской OEM-драйвер HP SP148389 (31.0.101.4502) через DDU в Safe Mode и восстановление вывода на внешний монитор MS27HQ-v1 по HDMI.


- [x] Разработка и регистрация конвейера follow-up сделок: скрипты `process_today_followup_deals.py` и `deal_followup_pipeline.py` скопированы в личный контур, добавлены быстрые фразы-триггеры «follow up deals today» (или «ащддщ up deals today») в `AGENTS.md`, `GRAVITY_CONTROL_CENTER.md`, `SKILLS.md`, `email_ai_pipelines` и `SCRIPTS_CATALOG.md`.
- [x] Синхронизация и деплой проекта `tender-extraction-lab`:
  * Слияние веток Михаила (`mikhail-origin/main` и `mikhail-origin/feature/new-tender-filter`) с локальной веткой `main` (Wait Random, наблюдатели Битрикса, ban-префильтрация лотов `tender_lot_parser_v7.py`);
  * Создание бэкапа рабочей версии кода на VPS (`/Storage/backups/tender-rag-api/2026-08-26/`);
  * Внедрение суточного стоп-лосса DeepSeek ($0.30/день), мягкой деградации эмбеддингов, русскоязычного промпта и персональных алертов администратору (`im.notify.personal.add`);
  * Пересборка Docker-контейнеров на VPS (`pandas`, `openpyxl`), сохранение целостности Metabase, успешный Health Check (`200 OK`);
  * Формирование отчета для Михаила `docs/sync_report_2026-08-26.md` и пуш во все репозитории GitHub (`origin/main`, `mikhail-origin/main`).

## Архив выполненных задач:
- [x] Очистка переполненного диска /Storage на VPS, устранение дублирования бэкапов в cron, обновление логики скрипта backup-sql.sh (с защитой от удаления последнего бэкапа и отправкой алертов при сбоях в n8n) и перезапуск зависшей службы 1С.
- [x] Проверка доступов Чулпан (25chulpan@gmail.com) на Google Диске руководителя artem9119130838@gmail.com
- [x] Восстановление сетевого доступа к VPS-серверу 109.248.170.181 (диагностика блокировок, решение конфликта портов Apache/Nginx, локализация проблемы на стороне T2 Mobile ISP).
* Полный список выполненных задач перенесен в файл [todo_archive.md](file:///C:/Codex_Personal/todo_archive.md).
