# Реестр канонических скриптов контура (`C:\Codex\scripts`)

В данной директории содержатся общесистемные боевые скрипты личного контура Артема.

---

## 🛠️ Общесистемные инструменты

| Скрипт | Назначение | Команда запуска |
|---|---|---|
| `inspect_doc.py` | Универсальный инспектор документов (PDF, DOCX, XLSX, TXT, картинок) и безопасный листинг папок в UTF-8 без сбоев Windows cp1251 charmap | `py scripts/inspect_doc.py --file <путь> [--stdout] [--output out.txt]` |
| `session_compress.py` | Автоматическое сжатие сессии ИИ, синхронизация правил, фиксация `.ai/SESSION_SUMMARY.md` и коммит в Git | `py scripts/session_compress.py` |
| `check_and_clean_pc.py` | Комплексная диагностика и очистка ПК (диск C:, GPU, реестр, кэш) | `py scripts/check_and_clean_pc.py` |
| `full_gravity_audit.py` | Полная ревизия контура, отсев вендорных библиотек, пересборка каталога | `py scripts/full_gravity_audit.py` |
| `format_universal_word_kp.py` | Генератор и форматтер коммерческих предложений Word/PDF | `py scripts/format_universal_word_kp.py` |
