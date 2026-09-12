---
name: Windows Diagnostics
description: Диагностика Windows, решение проблем зависания Acrobat Reader и Проводника (Explorer), очистка системного реестра и кэша, скачивание бэкапов через SSH и инвентаризация системы.
---

# Навык: Диагностика Windows

Этот навык предназначен для решения системных проблем Windows, включая зависания программ просмотра PDF, Проводника, сетевых папок, очистки кэша, а также автоматизации локальных задач (бэкапы, инвентаризация ПК).

## 1. Решение проблем с блокировкой PDF (Adobe Acrobat)

### Симптомы:
* Ошибка при распаковке или сохранении в Total Commander: *"Нет доступа, или файл уже используется"*.
* PDF-файлы не открываются при двойном клике, а в процессах копятся невидимые копии `Acrobat.exe`.

### Инструкция по исправлению:
1. **Принудительное завершение зависших процессов:**
   Запустите команду в PowerShell для удаления зависших инстансов Acrobat, которые держат лок на файлы:
   ```powershell
   Stop-Process -Name Acrobat -Force -ErrorAction SilentlyContinue
   ```
2. **Отключение защищенного режима (bProtectedMode):**
   Отключите защищенный режим через реестр, предотвращая зависания Acrobat:
   ```powershell
   Set-ItemProperty -Path 'HKCU:\Software\Adobe\Adobe Acrobat\DC\Privileged' -Name bProtectedMode -Value 0
   ```
3. **Удаление временных заблокированных файлов:**
   Временные файлы обычно лежат по пути `C:\Users\Артем\AppData\Local\Temp\_tc\`. Удалите заблокированный PDF:
   ```powershell
   Remove-Item -Path "C:\Users\Артем\AppData\Local\Temp\_tc\*.pdf" -Force -ErrorAction SilentlyContinue
   ```

---

## 2. Устранение сетевых задержек в Проводнике (Explorer)

### Симптомы:
* При открытии Проводника Windows (Explorer) интерфейс «задумывается» или виснет на 10–30 секунд.
* Это связано с тем, что Explorer пытается опросить недоступные/сетевые папки, добавленные на боковую панель.

### Инструкция по исправлению:
1. **Проверка пользовательских папок (CLSID) в реестре:**
   Запустите команду, чтобы увидеть, какие сетевые/кастомные папки зарегистрированы в реестре пользователя:
   ```powershell
   Get-ChildItem HKCU:\Software\Classes\CLSID -ErrorAction SilentlyContinue | ForEach-Object { $p = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue; $instance = Get-ItemProperty (Join-Path $_.PSPath 'Instance\InitPropertyBag') -ErrorAction SilentlyContinue; if ($p.'System.IsPinnedToNameSpaceTree' -ne $null -or $instance.TargetFolderPath) { [PSCustomObject]@{Key=$_.PSChildName; Name=$p.'(default)'; Target=$instance.TargetFolderPath; Pinned=$p.'System.IsPinnedToNameSpaceTree'} } } | Format-Table -AutoSize
   ```
2. **Удаление проблемных сетевых путей:**
   Если вы видите сетевые пути (например, `\\ARTEM-HOME\Disk E`), которые сейчас недоступны или опрашиваются слишком долго, удалите эти ветки реестра (заменив `{CLSID}` на найденный ключ):
   ```powershell
   Remove-Item -Path 'HKCU:\Software\Classes\CLSID\{CLSID}' -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item -Path 'HKCU:\Software\Classes\WOW6432Node\CLSID\{CLSID}' -Recurse -Force -ErrorAction SilentlyContinue
   ```
3. **Перезапуск Проводника для применения изменений:**
   ```powershell
   Stop-Process -Name explorer -Force
   ```
4. **Резервные копии твиков реестра:**
   Резервные файлы `.reg` для восстановления находятся в каталоге:
   `C:\Users\Артем\Documents\explorer_nav_backup\`

---

## 3. Резервное копирование по SSH/SFTP (PowerShell)

Для скачивания бэкапов с VPS на локальный ПК под Windows с авторизацией по ключу и ротацией файлов:

### Скрипт скачивания бэкапов (download_vps_backup.ps1):
```powershell
# Конфигурация
$VpsIp = "109.248.170.181"
$SshKey = "C:\Users\Артем\.ssh\id_ed25519_wlisses"
$RemoteDir = "/Storage/vps_backups"
$LocalDir = "D:\Backups\VPS"
$LogFile = "D:\Backups\VPS\download.log"
$MaxDays = 30

$Date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[$Date] Start backup download from $VpsIp" | Out-File $LogFile -Append

# Создание локальной папки при отсутствии
if (-not (Test-Path $LocalDir)) {
    New-Item -ItemType Directory -Force -Path $LocalDir
}

# 1. Скачивание файлов по SCP (через pscp из комплекта PuTTY или встроенный scp)
& scp.exe -i $SshKey -r "root@$VpsIp:$RemoteDir/*" $LocalDir

# 2. Ротация локальных бэкапов (удаление старше 30 дней)
Get-ChildItem -Path $LocalDir -File | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$MaxDays) } | ForEach-Object {
    Remove-Item $_.FullName -Force
    "[$(Get-Date)] Removed old local backup: $($_.Name)" | Out-File $LogFile -Append
}

"[$(Get-Date)] Backup download finished successfully" | Out-File $LogFile -Append
```

---

## 4. Локальная инвентаризация ПК (weekly-inventory-audit)

Для проведения еженедельного аудита системы ИИ должен запускать сбор сведений на PowerShell:

### Команды сбора инвентаризации:
*   **Свободное место на дисках:**
    `Get-Volume | Select-Object DriveLetter, FriendlyName, SizeRemaining, Size | Format-Table`
*   **Список установленных программ:**
    `Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | Format-Table`
*   **Программы в автозагрузке:**
    `Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table`

---

## 5. Разработка вспомогательных скриптов Windows (.bat)

При создании командных `.bat` файлов на Windows для автоматизации задач (туннели, бэкапы, запуски питон-скриптов) необходимо соблюдать следующие правила для предотвращения ошибок консоли `cmd.exe`:

1.  **Комментарии:** 
    *   **Запрещено** использовать символ `#` для комментариев. CMD воспринимает его как часть команды и выбрасывает синтаксические ошибки (например, `'-o' is not recognized`).
    *   **Используйте** `::` или `REM` для комментирования строк.
2.  **Рабочая директория (CWD):** 
    *   При запуске `.bat` двойным кликом CWD может сброситься в домашнюю папку пользователя (например, `C:\Users\Артем\Documents`).
    *   Всегда принудительно переходите в директорию запускаемого файла в начале батника с помощью `cd /d "%~dp0"` или указывайте жесткий абсолютный путь перехода `cd /d "C:\Path\To\Project"`.
3.  **Кодировка и пути:**
    *   Если в имени профиля пользователя Windows содержатся русские буквы (например, `C:\Users\Артем\`), раскрытие системной переменной `%USERPROFILE%` внутри SSH-параметров в UTF-8 кодировке (`chcp 65001`) может сбоить.
    *   Используйте полные жесткие абсолютные пути к ключам и файлам конфигурации для исключения ошибок кодировки.


## 6. Запуск PowerShell команд с переменными окружения из внешних сред

При вызове дочерних процессов PowerShell из внешних сред (терминал ассистента, API-клиенты, планировщики) с установкой переменных окружения необходимо предотвращать преждевременное раскрытие символа `$` родительской оболочкой:

1.  **Экранирование символа `$` (Рекомендуется для двойных кавычек):**
    Используйте обратный апостроф (backtick) `` ` `` перед знаком доллара, чтобы родительский PowerShell передал его дочернему без изменений:
    ```powershell
    powershell -ExecutionPolicy Bypass -Command "`$env:ALLOW_EXTERNAL_PUSH = '1'; git push"
    ```
2.  **Использование одинарных кавычек:**
    Если команда оборачивается в одинарные кавычки для `-Command`, раскрытие переменных также блокируется, но внутренние строки должны быть в двойных кавычках:
    ```powershell
    powershell -ExecutionPolicy Bypass -Command '$env:ALLOW_EXTERNAL_PUSH = "1"; git push'
    ```
3.  **Ограничения CMD-оболочки:**
    При обходе через CMD (`set VAR=val && command`) учитывайте, что утилиты вроде `git` или `ssh` могут отсутствовать в `PATH` CMD, в то время как в PowerShell они доступны. Отдавайте предпочтение PowerShell с экранированием.

---

## 7. Запуск Python и Git в терминале Windows

1. **Вызов Python**: На данном хосте Windows стандартный вызов `python` недоступен в консоли или вызывает магазин приложений. Запуск интерпретатора Python и скриптов должен осуществляться исключительно через лаунчер `py` (например, `py scripts/inventory.py`).
2. **Ограничения Git в PATH**: Утилита `git` может отсутствовать в глобальной переменной `%PATH%` для системных фоновых процессов, из-за чего встроенные инструменты поиска (например, `grep_search` в папках Git-репозиториев) падают с ошибкой `exec: "git": executable file not found`.
   * **Решение**: При вызове git в терминале использовать полный абсолютный путь `C:\Program Files\Git\cmd\git.exe`. При сбоях встроенного `grep_search` осуществлять поиск через чтение файлов `view_file` или запуск `rg` (ripgrep) напрямую в терминале PowerShell.


## 8. Создание конфигурационных файлов FreeFileSync (.ffs_gui) вручную

При генерации или автоматическом редактировании XML-конфигураций FreeFileSync (`.ffs_gui` или `.ffs_batch`) строго соблюдайте следующие правила разметки:

1. **Экранирование спецсимволов XML**:
   * **Запрещено** использовать символ `>` (например, в стрелках переходов `->`) или `<` напрямую внутри текстовых полей, таких как `<Notes>...</Notes>`. Это приводит к падению парсера FreeFileSync с ошибкой разбора XML.
   * **Используйте** экранирование (`&gt;`, `&lt;`) или текстовые аналоги (например, `to`, `into`).
2. **Параметры различий (Differences) для режима Update (Обновить)**:
   * **Запрещено** использовать значение `"ignore"` для атрибутов `RightNewer` и `RightOnly` внутри тега `<Differences>`. Данное значение не поддерживается парсером и сбрасывает настройки в дефолт.
   * **Используйте** валидное значение `"none"` для обозначения действия "Ничего не делать" (Do nothing).
   * Пример корректной строки для режима Update:
     ```xml
     <Differences LeftOnly="right" LeftNewer="right" RightNewer="none" RightOnly="none"/>
     ```


---

## 9. Кириллица в путях пользователей и сбои ИИ-библиотек (Whisper, ggml)

### Проблема:
Многие C++ библиотеки и порты ИИ (например, `whisper.cpp`, `ggml`) некорректно обрабатывают пути к файлам с кодировкой Юникод/кириллицей (например, `C:\Users\Артем\AppData\Local\...`). Программы (такие как Subtitle Edit) вылетают за доли секунды без ошибок или не могут загрузить скачанные модели.

### Решение:
1. **Перенос моделей в чистые пути**: Скачивать и сохранять тяжелые файлы моделей (`.bin`) по путям, не содержащим кириллицы (например, в `C:\Save\ggml-small.bin`).
2. **Использование портативных версий (Portable)**: Вместо установки программ в стандартный профиль (`AppData`), распаковывать их портативные версии в папки без русских букв (например, `C:\Save\SubtitleEdit`). Программы будут хранить настройки, библиотеки и кэш локально, избегая падений.

---

## 10. Замена файлов закладок Edge при активной синхронизации

### Проблема:
При замене файла `Bookmarks` в профиле Edge (`User Data\Default`) с целью очистки дубликатов, браузер при следующем запуске скачивает старую версию из облака Microsoft и полностью перезаписывает локальный файл, возвращая дубликаты.

### Решение (Алгоритм чистой замены):
1. **Отключение Edge**: Завершить все процессы браузера в памяти:
   ```powershell
   Stop-Process -Name msedge -Force -ErrorAction SilentlyContinue
   ```
2. **Сброс облака**: Открыть настройки синхронизации `edge://settings/profiles/sync`, отключить синхронизацию Избранного (Favorites) и выполнить **Сброс данных синхронизации** на серверах Microsoft.
3. **Замена файла**: Заменить файл `Bookmarks` на очищенную версию, пока браузер закрыт.
4. **Синхронизация очищенных данных**: Запустить Edge. Новая очищенная локальная копия закладок автоматически загрузится в облако как основная.

---

## 11. Перенос настроек и данных Punto Switcher от Яндекс

### Проблема/Задача:
Пользователь хочет полностью перенести все настройки программы, правила автозамены и списки исключений (например, для 1С УНФ, n8n, VPN и др.) на новый ноутбук.

### Особенности хранения данных:
1. **Основной каталог настроек**:
   `%AppData%\Yandex\Punto Switcher\User Data` (абсолютный путь: `C:\Users\<Имя_Пользователя>\AppData\Roaming\Yandex\Punto Switcher\User Data`).
2. **Исключения и правила (user.dic)**:
   В некоторых версиях Punto Switcher списки программ-исключений (для которых отключено автопереключение) записываются напрямую в файл **`user.dic`** (пользовательский словарь) с префиксом **`_PE`** (например, `_PE unf`, `_PE n8n`, `_PE vpn`). Отдельные файлы `prog_ex.dat` при этом отсутствуют.
3. **Автозамена (replace.dat)**:
   Пары автозамены хранятся в файле `replace.dat`, который создается только при наличии хотя бы одной записи.

### Алгоритм переноса на новый ПК:
1. Закрыть Punto Switcher (выход через контекстное меню в трее) на обоих ПК.
2. Скопировать из папки `%AppData%\Yandex\Punto Switcher\User Data` старого ПК файлы:
   * **`preferences.xml`** — основные настройки и горячие клавиши.
   * **`user.dic`** — все исключения (программы, заголовки окон) и словари.
   * **`replace.dat`** — автозамены (при наличии).
3. Установить и запустить программу на новом ПК (для инициализации папок), затем закрыть её.
4. Скопировать сохраненные файлы в аналогичную папку `%AppData%\Yandex\Punto Switcher\User Data\` на новом ПК с заменой.
5. Запустить Punto Switcher.

---

## 12. Миграция окружения Antigravity и синхронизация между Victus и MateBook

### 1. Архитектура разделения:
- **Git (`codex-work.git`)**: исходный код, документация, скрипты, база знаний (`codex_kb`). Синхронизируется через `git push` / `git pull`.
- **FreeFileSync (`Mirror_E_Home`)**: тяжелые дистрибутивы (`SOFT`), базы данных (`SOFT_D`), архивы (`SAVE`), документы, сессии приложений и служебные профили Antigravity (`.gemini`).

### 2. Таблица кросс-путей:
| Ресурс | HP Victus | Внешний диск | Huawei MateBook 14 |
| :--- | :--- | :--- | :--- |
| Репозиторий | `E:\Codex_Work` | `Mirror_E_Home\Codex_Work` | `C:\Codex_Personal` |
| Профиль пользователя | `C:\Users\Артем` | `Mirror_E_Home\.gemini` / `.ssh` | `C:\Users\Artem` |
| Дистрибутивы ПО | `E:\SOFT` | `Mirror_E_Home\SOFT` | `D:\Дистрибутивы` |
| Установленный софт/базы | `D:\Soft` | `Mirror_E_Home\SOFT_D` | `D:\Soft` |
| Сохранения/архивы | `E:\SAVE` | `Mirror_E_Home\SAVE` | `D:\Save E` |
| Документы | `E:\Документы` | `Mirror_E_Home\Документы` | `D:\Документы Sync E` |

### 3. Обязательная адаптация путей Antigravity:
При смене компьютера с кириллицей на латиницу (`Артем` ⮂ `Artem`) пути в служебных файлах Antigravity (`antigravity_state.pbtxt`, `.codex-global-state.json`) становятся недействительными.
- При миграции на MateBook: заменять `Артем` ➔ `Artem`, `E:\Codex_Work` ➔ `C:\Codex_Personal`.
- При миграции на Victus: запускать скрипт `fix_paths_for_victus.py` для обратной замены `Artem` ➔ `Артем`, `C:\Codex_Personal` ➔ `E:\Codex_Work`.
