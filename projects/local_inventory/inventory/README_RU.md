# Инвентаризация файлов и программ

## Что это делает
- `make_snapshot.ps1` делает снимок файлов по выбранным папкам на C: и D:
- `compare_snapshots.ps1` сравнивает два последних снимка и делает отчёт изменений
- `export_installed_programs.ps1` сохраняет список установленных программ
- `weekly_run.bat` запускает всё подряд одной командой
- `open_latest_report.bat` открывает последний Excel-отчёт

## Куда смотреть
- `snapshots`
- `reports`
- `programs`

## Как пользоваться
1. Двойной клик по `weekly_run.bat`
2. После завершения можно открыть последний отчёт двойным кликом по `open_latest_report.bat`

или вручную:

1. `powershell -ExecutionPolicy Bypass -File .\make_snapshot.ps1`
2. `powershell -ExecutionPolicy Bypass -File .\compare_snapshots.ps1`
3. `powershell -ExecutionPolicy Bypass -File .\export_installed_programs.ps1`

## Excel
Все результаты сохраняются:
- в `CSV`
- и в `XLSX`

Файлы `.xlsx` открываются в Excel с автофильтром, так что их можно сразу сортировать и фильтровать.

## Настройка под другой компьютер
Откройте `inventory_config.ps1` и при необходимости поменяйте:
- `SnapshotRoots`
- `ExcludePatterns`

Сейчас в конфиге используются шаблоны:
- `C:\Users\*\Desktop`
- `C:\Users\*\Downloads`
- `C:\Users\*\Documents`
- `C:\Users\*\AppData\Roaming`

Это значит, что он подходит и для `Artem`, и для `Артем`, и для похожих профилей без ручной правки имени пользователя.
