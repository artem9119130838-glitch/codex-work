import sys
from pathlib import Path
from session_compress import get_paths, create_summary, clean_scratch, run_git

paths = get_paths()

summary_paragraph = (
    "Сессия посвящена глубокому аудиту найма и адаптации операционного ассистента/заместителя руководителя: "
    "исследован кейс Чулпан Хузиной (причины провала: пассивность при срыве сроков, уход в параллельные Excel-таблицы, "
    "саботаж базы знаний Bitrix24), сформирован полный вводный пакет на 'ты' для нового заместителя Татьяны "
    "(фокус строго на логистике, снабжении и Bitrix24 без 1С/продаж), адаптирован реестр задач tasks_registry_tatyana.xlsx, "
    "и создана каноническая RAG-база кандидатов и сбоев снабжения/логистики в codex_kb/20_domains/hr_and_operations/ "
    "для сравнительного анализа в будущем."
)

completed = [
    "Аудит задач, переписки и причин сбоя испытательного срока Чулпан Хузиной",
    "Подготовка шпаргалки и вводного регламента на 'ты' для Татьяны с исключением 1С, продаж и бухгалтерии на первый месяц",
    "Адаптация реестра задач tasks_registry_tatyana.xlsx (задачи 1С/продаж отложены, добавлены фокусы контроля ФТС и Азата)",
    "Создание канонического RAG-домена codex_kb/20_domains/hr_and_operations/ с подробной матрицей сравнения кандидатов",
    "Создание реестра системных проблем снабжения и логистики OPERATIONAL_SUPPLY_LOGISTICS_ISSUES.md",
    "Актуализация бизнес-правил (независимость Сауле от Азата, запрет оплаты ЗПО без визы логиста) и KNOWLEDGE_MAP в codex_kb",
    "Фиксация регламента операционного ассистирования HR & Operations Guard в AGENTS.md",
    "Обезвреживание открытого пароля в тестовом скрипте read_salman_inbox.py",
    "Актуализация рабочего лога todo.md"
]

files = [
    "projects/HR/Татьяна/Шпаргалка_Операционного_Ассистента.md",
    "projects/HR/Татьяна/Анализ_Операционных_Ошибок_Кейс_Чулпан.md",
    "projects/HR/Татьяна/Структура_Бизнеса_и_Операционные_Правила.md",
    "projects/HR/Татьяна/tasks_registry_tatyana.xlsx",
    "projects/HR/Татьяна/Книга продаж.docx",
    "codex_kb/20_domains/hr_and_operations/README.md",
    "codex_kb/20_domains/hr_and_operations/CANDIDATES_HISTORY_AND_COMPARISON.md",
    "codex_kb/20_domains/hr_and_operations/OPERATIONAL_SUPPLY_LOGISTICS_ISSUES.md",
    "codex_kb/progress/HR_PROGRESS.md",
    "codex_kb/00_global/BUSINESS_RULES.md",
    "codex_kb/00_global/KNOWLEDGE_MAP.md",
    "codex_kb/20_domains/README.md",
    "projects/HR/read_salman_inbox.py",
    "AGENTS.md",
    "todo.md"
]

issues = [
    "Добавить Татьяну наблюдателем во все ключевые чаты и сделки Bitrix24",
    "Контроль прохождения 5-дневной программы 'Песочницы' в Bitrix24 Татьяной и приемка 5-минутного видео-скринкаста",
    "Оценка результатов работы Чулпан по предоставленному последнему шансу",
    "Проведение установочного созвона с Татьяной по итогам 2 недель наблюдения для принятия решения о постоянном контракте"
]

lessons = [
    "Операционный ассистент обязан быть контролером системы и поднимать тревогу сразу при провисании задач >= 2 дней, а не быть пассивным регистратором срывов",
    "Строгий запрет на создание параллельных Excel-таблиц (No-Excel Policy): вся работа и цифровые следы ведутся строго в CRM (Bitrix24)",
    "Снабжение (Азат) и логистика (Сауле) независимы: оплата любого ЗПО категорически запрещена до письменной верификации Сауле на таможенные риски",
    "Категорический запрет на хардкод паролей и секретов в скриптах репозитория (устранена уязвимость в read_salman_inbox.py)"
]

completed_fmt = "\n".join(f"- {t}" for t in completed)
files_fmt = "\n".join(f"- `{f}`" for f in files)
issues_fmt = "\n".join(f"- {i}" for i in issues)
lessons_fmt = "\n".join(f"- {l}" for l in lessons)

print("=== Сжатие сессии: Генерация SESSION_SUMMARY.md ===")
create_summary(paths["summary"], summary_paragraph, completed_fmt, files_fmt, issues_fmt, lessons_fmt)

clean_scratch(paths["scratch"])

git_root = paths["root"]
if (git_root / ".git").exists():
    print("\n--- Синхронизация с Git ---")
    run_git(["add", "."], "Добавление измененных и новых файлов в индекс Git", git_root)
    run_git(["commit", "-m", "HR & Operations: add Tatyana onboarding, Chulpan case analysis, RAG domain and session summary"], "Создание коммита сжатия", git_root)
    run_git(["push", "origin", "master"], "Отправка коммитов в репозиторий GitHub", git_root)
else:
    print(f"\n[INFO] Git не настроен в корне {git_root}. Изменения сохранены локально.")
