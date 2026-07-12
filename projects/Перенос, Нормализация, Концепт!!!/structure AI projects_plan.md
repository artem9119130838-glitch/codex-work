# Архитектурный план: 3-уровневая система правил ИИ и глобальные навыки

Этот план полностью переработан на основе предложенного вами архитектурного концепта (оценка: **10/10**). Мы разделяем правила ИИ на три независимых уровня, укрупняем навыки для экономии токенов и внедряем гибкую матрицу рисков (Decision Policy) и вайтлист для Git Push.

---

## 1. Новая архитектура правил ИИ

Мы внедрим идентичную структуру для обоих контуров (`C:\Codex_Personal` и `C:\Codex_Shared`).

```
Workspaces (C:\Codex_Personal и C:\Codex_Shared)
├── AGENTS.md                ← Краткий контракт ИИ (до 2 страниц, точка входа)
├── AI_RULES.md              ← Общие правила работы и TOKEN-FIRST
├── SECURITY.md              ← Матрица рисков (L0-L6) и правила аппрувов
├── SKILLS.md                ← Индекс доступных навыков
└── todo.md                  ← Локальный рабочий лог (вместо task.md)

Global Customizations (C:\Users\Артем\.gemini\config\skills\)
└── skills/
    ├── windows/             ← Диагностика Windows (Acrobat, Explorer, OneDrive)
    ├── linux/               ← Администрирование Linux/VPS (SSH, логи, Docker)
    ├── git/                 ← Git-воркфлоу (хуки, pre-push, whitelist)
    ├── 1c_unf/              ← Правила BSL, стандарты 1С, OData-запросы
    ├── n8n/                 ← Сценарии автоматизации n8n
    ├── excel/               ← Анализ таблиц и парсинг Excel
    └── session_management/  ← Сжатие сессии и SESSION_SUMMARY.md
```

### Детализация 3-х уровней:

1.  **Level 1: AGENTS.md (Контракт)**
    *   *Назначение:* Точка входа для ИИ при запуске. Содержит только базовую языковую политику (русский язык) и ссылки на файлы `AI_RULES.md` и `SECURITY.md`, которые ИИ должен прочитать при необходимости.
2.  **Level 2: AI_RULES.md & SECURITY.md (Политика и Риски)**
    *   *AI_RULES.md:* Содержит жесткие правила экономии токенов (**TOKEN-FIRST 4.0**: оценить нужность $\rightarrow$ прочитать контекст $\rightarrow$ прочитать часть $\rightarrow$ только потом полное чтение) и правила ведения логов в `todo.md`.
    *   *SECURITY.md:* **Decision Policy** с уровнями рисков от L0 (Чтение) до L6 (Production). Для каждого уровня четко определено, какие команды выполняются автономно, а какие требуют явного согласия пользователя (исключает лишние запросы разрешений).
3.  **Level 3: Global Skills (Навыки)**
    *   Навыки выносятся в глобальную директорию `C:\Users\Артем\.gemini\config\skills/`.
    *   ИИ сначала сверяется с индексом в `SKILLS.md` в корне проекта и загружает только тот навык, который нужен для текущей задачи. Это дает огромную экономию контекста и токенов.

---

## 2. Предложенные изменения по файлам

### [NEW] [AGENTS.md](file:///C:/Codex_Personal/AGENTS.md) / [AGENTS.md](file:///C:/Codex_Shared/AGENTS.md)
Краткий контракт. Описывает базовые правила и ссылается на новые файлы:
*   [AI_RULES.md](file:///C:/Codex_Personal/AI_RULES.md)
*   [SECURITY.md](file:///C:/Codex_Personal/SECURITY.md)

### [NEW] [AI_RULES.md](file:///C:/Codex_Personal/AI_RULES.md) / [AI_RULES.md](file:///C:/Codex_Shared/AI_RULES.md)
Политики ведения работы и жесткая экономия токенов.

### [NEW] [SECURITY.md](file:///C:/Codex_Personal/SECURITY.md) / [SECURITY.md](file:///C:/Codex_Shared/SECURITY.md)
Матрица рисков Decision Policy (L0-L6).

### [NEW] [SKILLS.md](file:///C:/Codex_Personal/SKILLS.md) / [SKILLS.md](file:///C:/Codex_Shared/SKILLS.md)
Индекс навыков для быстрого поиска ИИ.

### [MODIFY] [C:\Codex_Shared\.aiignore](file:///C:/Codex_Shared/.aiignore)
Добавление папки `C:/Codex_Personal/` для исключения доступа ИИ-агента.

---

### Создание глобальных навыков (C:\Users\Артем\.gemini\config\skills\)

#### [NEW] [SKILL.md (windows)](file:///C:/Users/Артем/.gemini/config/skills/windows/SKILL.md)
Высокоуровневый навык диагностики Windows (блокировка Acrobat, зависание Проводника из-за сети, настройки реестра).

#### [NEW] [SKILL.md (linux)](file:///C:/Users/Артем/.gemini/config/skills/linux/SKILL.md)
Высокоуровневый навык администрирования серверов Linux (логи, SSH, аудит, Docker).

#### [NEW] [SKILL.md (git)](file:///C:/Users/Артем/.gemini/config/skills/git/SKILL.md)
Высокоуровневый навык работы с Git.

#### [NEW] [SKILL.md (1c_unf)](file:///C:/Users/Артем/.gemini/config/skills/1c_unf/SKILL.md)
Высокоуровневый навык разработки и интеграции 1С.

#### [NEW] [SKILL.md (session_management)](file:///C:/Users/Артем/.gemini/config/skills/session_management/SKILL.md)
Навык сжатия сессии и подготовки `SESSION_SUMMARY.md`.

---

### Реализация Pre-Push вайтлиста

Вместо хардкода репозитория в скрипте хука, мы сделаем pre-push хук с поддержкой вайтлиста.

#### [NEW] [allowed_remotes.txt](file:///C:/codex_home/.git_hooks/allowed_remotes.txt)
Текстовый файл со списком разрешенных паттернов для пуша:
```text
github.com/artem9119130838/*
# Сюда можно будет добавлять другие репозитории
```

#### [NEW] [pre-push](file:///C:/codex_home/.git_hooks/pre-push)
Динамический Bash-скрипт хука:
```bash
#!/bin/sh

remote_name="$1"
remote_url="$2"
whitelist_file="C:/codex_home/.git_hooks/allowed_remotes.txt"

# 1. Проверяем наличие вайтлиста
if [ ! -f "$whitelist_file" ]; then
    echo "SECURITY ERROR: Whitelist file not found at $whitelist_file"
    exit 1
fi

# 2. Проверяем URL по вайтлисту (поддерживаем простые маски через grep)
matched=0
while IFS= read -r pattern || [ -n "$pattern" ]; do
    # Игнорируем пустые строки и комментарии
    [ -z "$pattern" ] && continue
    echo "$pattern" | grep -q "^#" && continue

    # Преобразуем маску * в регулярное выражение
    regex=$(echo "$pattern" | sed 's/\*/.*/g')
    if echo "$remote_url" | grep -iq "$regex"; then
        matched=1
        break
    fi
done < "$whitelist_file"

if [ "$matched" = "1" ]; then
    exit 0
fi

# 3. Проверяем переменную принудительного обхода
if [ "$ALLOW_EXTERNAL_PUSH" = "1" ]; then
    echo "WARNING: Push to external repository allowed by ALLOW_EXTERNAL_PUSH=1."
    exit 0
fi

# 4. Блокируем пуш
echo ""
echo "========================================= SECURITY ALERT ========================================="
echo "PUSH BLOCKED: The remote repository URL is not in the whitelist:"
echo "  $remote_url"
echo ""
echo "To allow this push, either add the pattern to: $whitelist_file"
echo "Or bypass it temporarily:"
echo "  In PowerShell: \$env:ALLOW_EXTERNAL_PUSH='1'; git push"
echo "  In CMD:        set ALLOW_EXTERNAL_PUSH=1 && git push"
echo "  In Git Bash:   ALLOW_EXTERNAL_PUSH=1 git push"
echo "=================================================================================================="
echo ""
exit 1
```

---

## 3. План верификации

### Автоматические тесты
1. **Проверка Pre-push хука:**
   - Пуш в `github.com/artem9119130838-glitch/codex-work.git` $\rightarrow$ Должен пройти (dry-run).
   - Пуш в любой сторонний репозиторий $\rightarrow$ Должен быть заблокирован.
   - Пуш во внешний репозиторий с переменной `ALLOW_EXTERNAL_PUSH=1` $\rightarrow$ Должен пройти (dry-run).
2. **Проверка изоляции контуров:**
   - Попытка сканирования ИИ-агентом из `C:\Codex_Shared` каталога `C:\Codex_Personal` $\rightarrow$ Игнорирование.
