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

* **Ноутбук**: HP Victus by HP Laptop 16-d1xxx (BIOS F.20)
* **Процессор**: Intel Core 12th Gen
* **Видеоадаптеры**:
  * Встроенный: Intel(R) Iris(R) Xe Graphics
  * Дискретный: NVIDIA GeForce RTX 3060 Laptop GPU
* **Особенность портов**: Внешние выходы (HDMI, USB Type-C DisplayPort) разведены напрямую на дискретную графику NVIDIA. Если видеокарта NVIDIA отключена или находится в состоянии ошибки, внешние мониторы работать не будут.

### ⚠️ Проблема с кодом ошибки 43 (CM_PROB_FAILED_POST_START)
При фоновом обновлении драйверов через Windows Update (например, версия `32.0.15.9282`) видеокарта NVIDIA падает в ошибку Код 43, сопровождаемую аппаратным сбоем питания шины PCIe (`WHEA-Logger`).

**Алгоритм восстановления**:
1. Переключить видеокарту в Диспетчере устройств на драйвер **"Базовый видеоадаптер (Microsoft)"**.
2. Заблокировать установку драйверов от Microsoft: открыть `sysdm.cpl` -> вкладка **Оборудование** -> **Параметры установки устройств** -> выбрать **Нет** -> Сохранить.
3. Скачать официальный драйвер с сайта NVIDIA и запустить **чистую установку** (Clean Installation).
4. Если ошибка сохраняется, сбросить контроллер питания (EC Reset): полностью выключить ноутбук, отключить все кабели и зарядное устройство, зажать кнопку питания на **40 секунд**. Подключить зарядку и включить ноутбук.

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

