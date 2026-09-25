# Asset: Local Computer

## Workspace

Primary shared workspace:

```text
E:\Codex_Work
```

Purpose:

- central Codex workspace;
- stable knowledge base;
- active project files;
- archived old exports and one-off outputs;
- portable context between chats and possibly machines.

## Important Root Items

```text
E:\Codex_Work\AGENTS.md
E:\Codex_Work\CODEX_START_HERE.md
E:\Codex_Work\PROGRESS.md
E:\Codex_Work\CHAT_DISPATCHER.md
E:\Codex_Work\ГДЕ_ЧТО_ЛЕЖИТ.md
E:\Codex_Work\codex_kb
E:\Codex_Work\projects
E:\Codex_Work\chat_exports
E:\Codex_Work\Архив
```

## Inventory

Inventory folder:

```text
E:\Codex_Work\projects\local_inventory\inventory
```

Known scripts from exports:

```text
weekly_run.bat
open_latest_report.bat
make_snapshot.ps1
compare_snapshots.ps1
export_installed_programs.ps1
inventory_common.ps1
inventory_config.ps1
```

Workflow:

1. First run creates baseline.
2. Later runs compare new/changed/deleted files.
3. Review reports in Excel.
4. Move important changed data to `E:` manually or with FreeFileSync.

## Old AST GOZ Context

The older `CHAT_INDEX.md` and `CURRENT_STATE.md` mainly describe AST GOZ automation. They now live under:

```text
E:\Codex_Work\projects\tenders_ast_goz\legacy_context
```

They remain useful, but new global context should live in `codex_kb`.

## Known local paths from old work

- `C:\Users\Artem\Downloads\GOZ`
- `D:\server-backups\full-backup-2026-05-03_11-52`
- `E:\Codex_Work\Архив\old_outputs`
- `E:\Codex_Work\projects\n8n_bitrix\source_docs`

## Safety

- Do not overwrite old exports.
- Keep `chat_exports` as archive.
- Put reusable, stable facts into `codex_kb`.
- Put active working files into `projects`.
- Put one-off or superseded material into `Архив`.

## Hardware Specs & Known GPU Issues

* **Ноутбук**: HP Victus by HP Laptop 16-d1xxx (SKU `650R1PA#AB2`, S/N `5CD2379N3H`, Motherboard `8A25`, BIOS `F.20`)
* **ОС**: Windows 11 Pro, сборка 26200 (25H2)
* **Процессор**: Intel Core i7-12700H (12th Gen Alder Lake)
* **Матрица экрана**: Innolux / Chi Mei N161HCA-GA1 (16.1" FHD 1920x1080, 144 Гц, PnP ID: `DISPLAY\CMN1619`)
* **Видеоадаптеры**:
  * Встроенный: Intel(R) Iris(R) Xe Graphics (`PCI\VEN_8086&DEV_46A6&SUBSYS_8A25103C`)
  * Дискретный: NVIDIA GeForce RTX 3060 Laptop GPU (`PCI\VEN_10DE&DEV_2520&SUBSYS_8A25103C`)
* **Внешний монитор**: `MS27HQ-v1` (27" QHD IPS), подключение через HDMI напрямую к NVIDIA.
* **Особенность портов**: Внешний HDMI-разъём аппаратно распаян напрямую на дискретную графику NVIDIA RTX 3060. Экран ноутбука подключен по eDP к видеочипу Intel.

### Текущий статус графической подсистемы (Сентябрь 2026):
1. **Проблема черного экрана на Intel Iris Xe**:
   * При установке и активации полноценного видеодрайвера Intel (ветки 7085, 7088) экран ноутбука гаснет в чёрный экран.
   * Система загружается и работает только при переключении чипа Intel на **«Базовый видеоадаптер (Майкрософт)»** (`basicdisplay.sys`, 1920x1080@60Hz).
   * Корень проблемы: конфликт управления подсветкой/ШИМ матрицы eDP, включение Panel Self Refresh (PSR2) в драйвере Intel, либо сбой инициализации вывода в Windows 11 25H2.
2. **Проблема второго (внешнего) монитора**:
   * Пока видеокарта Intel работает на Базовом драйвере Microsoft, Windows WDDM блокирует расширение рабочего стола (`Win + P` ➔ «Расширить») на внешний монитор NVIDIA.
3. **Драйвер NVIDIA и Код 43**:
   * Для видеокарты NVIDIA требуется пакет `nvhmi.inf` (например, `32.0.15.9649` с буквой «i» — Intel Optimus). При ручной установке стандартного мобильного пакета `nvhm.inf` (`32.0.15.9282`) видеокарта падает в ошибку **Код 43** (`CM_PROB_FAILED_POST_START`).
4. **Сброс кэша экранов и твики стабильности**:
   * Скрипт `СБРОС_КЭША_ДИСПЛЕЕВ.bat` очищает повреждённый кэш `GraphicsDrivers\Configuration` (фантомные профили `SIMULATED` и `MSNILNOEDID`), отключает «Быстрый запуск» (`HiberbootEnabled = 0`) и баг MPO в Windows 11 (`DisableOverlays = 1`).
5. **Конфигурация загрузчика BCD и Safe Mode**:
   * Включена классическая клавиша `F8` (`bcdedit /set {default} bootmenupolicy legacy`).
   * Меню загрузки скрыто (`timeout 0`), лишняя искусственная запись Safe Mode удалена из `msconfig` / BCD. Загрузка происходит мгновенно в штатную Windows 11.
   * При сбоях экрана безопасный режим вызывается нажатием `F8` (или `Fn + F8`) при включении ноутбука.
   * Скрипты на Рабочем столе: `ВКЛЮЧИТЬ_КЛАВИШУ_F8.bat`, `УДАЛИТЬ_ЛИШНЕЕ_МЕНЮ_ЗАГРУЗКИ.bat`, памятка `ВАЖНЫЕ_КОМАНДЫ_И_SAFE_MODE.md`.

### Нейтрализация всплывающих окон Adobe Acrobat:
* Выполнена полная блокировка сервисов проверки лицензии Adobe Genuine:
  - Папки переименованы в `C:\Program Files\Adobe\Acrobat DC\Acrobat\GC_disabled` и `cefWorkflow_disabled`.
  - Внесены корпоративные политики `FeatureLockDown` в реестр (`bAcroSuppressUpsell=1`, `bToggleAdobeDocumentServices=1`, `bDontShowMsgWhenViewingDoc=1`).
  - Серверы телеметрии/лицензирования перенаправлены на `0.0.0.0` в `C:\Windows\System32\drivers\etc\hosts`.
  - Скрипт: `scripts/fix_acrobat_genuine.ps1`.

## Ноутбуки личного контура и схема синхронизации

Контур использует два рабочих ноутбука:
1. **HP Victus 16** (Основной домашний ноутбук / рабочая станция):
   - Пользователь Windows: `Артем` (`C:\Users\Артем`)
   - Рабочий репозиторий Codex: `E:\Codex_Work`
   - Локальные диски с данными: `E:\` и `D:\`
   - Внешний накопитель для бэкапа монтируется обычно как: `F:\`
2. **Huawei MateBook 14** (Мобильный рабочий ноутбук):
   - Пользователь Windows: `Artem` (`C:\Users\Artem`, чистая латиница)
   - Рабочий репозиторий Codex: `C:\Codex_Personal`
   - Локальные диски с данными: `C:\` и `D:\`
   - Внешний накопитель для бэкапа монтируется обычно как: `E:\`

### Карта синхронизации через внешний диск (Mirror_E_Home)

* **Git (`artem9119130838-glitch/codex-work.git`)**: Первичный транспортный слой для исходного кода, базы знаний, скриптов и документации.
* **FreeFileSync (`Mirror_E_Home`)**: Транспортный слой для тяжелых дистрибутивов, баз данных, сессий приложений и профилей AppData:
  - `E:\Mirror_E_Home\SOFT` ⮂ Victus: `E:\SOFT` ⮂ MateBook: `D:\Дистрибутивы`
  - `E:\Mirror_E_Home\SOFT_D` ⮂ Victus: `D:\Soft` ⮂ MateBook: `D:\Soft`
  - `E:\Mirror_E_Home\SAVE` ⮂ Victus: `E:\SAVE` ⮂ MateBook: `D:\Save E`
  - `E:\Mirror_E_Home\Документы` ⮂ Victus: `E:\Документы` ⮂ MateBook: `D:\Документы Sync E`
  - `E:\Mirror_E_Home\Codex_Work` ⮂ Victus: `E:\Codex_Work` ⮂ MateBook: `C:\Codex_Personal`
  - `E:\Mirror_E_Home\.gemini` ⮂ Victus: `C:\Users\Артем\.gemini` ⮂ MateBook: `C:\Users\Artem\.gemini`
  - `E:\Mirror_E_Home\.ssh` ⮂ Victus: `C:\Users\Артем\.ssh` ⮂ MateBook: `C:\Users\Artem\.ssh`
  - Профили AppData (Telegram, WeChat, DBeaver, NovoFon, dupeGuru, Direct Commander, DigiKam, Movavi, Punto Switcher, MobaXterm, 1C, Edge Bookmarks).
* **Скрипт адаптации путей Antigravity**: При возврате на Victus обязательно запускать `py F:\Mirror_E_Home\fix_paths_for_victus.py` для коррекции `Artem` ➔ `Артем` и `C:\Codex_Personal` ➔ `E:\Codex_Work` в служебных файлах Antigravity.

