```markdown
# Implementation Plan: TOKEN‑FIRST VIBE ENGINEERING for Antigravity

**Версия:** 1.0  
**Цель:** внедрение политики минимального расхода токенов и предварительного расчёта затрат в среде Antigravity (API Gemini, контекстные окна, субагенты).  
**Базовый стандарт:** [TOKEN‑FIRST VIBE ENGINEERING](./TOKEN_FIRST_STANDARD.md) (далее – Стандарт).  
**Принципы:** экономия без усложнения, без потери качества кода и данных, безопасность выше всего.

---

## 1. Особенности Antigravity, учтённые в плане

| Особенность | Как учтено |
|-------------|-------------|
| Контекст передаётся целиком при каждом вызове | Внедряем **Preflight Gateway** – локальный перехватчик, обрезающий контекст до минимального |
| Автоматические субагенты (grep, file read) | Ограничиваем историю субагента до 2000 токенов, передаём только текущую задачу |
| Нет встроенного кэширования контекста | Реализуем свой **Session Compression** – при длинных сессиях заменяем историю кратким итогом |
| Работа через API Gemini (Flash, Pro, Flash-8B) | Роутер моделей на основе ключевых слов в промпте + ручное переключение через мета-команды |
| Файловая система Windows (C:\Codex_Shared) | Все скрипты – на Python, с поддержкой путей с обратным слешем и `pathlib` |

---

## 2. Архитектура внедрения (как это работает в Antigravity)

```
Пользователь пишет промпт
        │
        ▼
┌───────────────────┐
│ Preflight Gateway │ ← оценивает токены, стоимость, блокирует при превышении
└───────────────────┘
        │ (если ОК)
        ▼
┌───────────────────┐
│  Context Cutter   │ ← обрезает контекст до разрешённого (макс 32k токенов)
└───────────────────┘
        │
        ▼
┌───────────────────┐
│    Model Router   │ ← выбирает Flash-8B / Flash / Pro на основе задачи
└───────────────────┘
        │
        ▼
┌───────────────────┐
│   API Call to     │
│   Antigravity     │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Budget Enforcer   │ ← обновляет счётчики, при исчерпании блокирует
└───────────────────┘
```

**Всё это работает прозрачно для пользователя.** Единственное видимое изменение – иногда появляются предупреждения или запросы подтверждения.

---

## 3. Пошаговый план реализации

### Фаза 0: Подготовка (1 час)

**Создать структуру каталогов и файлы:**

```
C:\Codex_Shared\
├── .ai\
│   ├── file_index.json        (будет создан позже)
│   ├── architecture.md        (заполнить вручную)
│   └── budgets.yaml
├── scripts\
│   ├── preflight.py
│   ├── budget_enforcer.py
│   ├── build_index.py
│   └── session_compress.py
├── .aiignore                  (список исключаемых папок/файлов)
└── AGENTS.md                  (обновлённый, с лимитами из Стандарта)
```

**Содержимое `budgets.yaml` (начальное, щадящее):**
```yaml
daily:
  flash: 5.0      # USD
  pro: 1.0
  flash_8b: 0.5   # очень дёшево, можно много
session:
  max_cost: 0.50
request:
  max_cost: 0.01
```

**Содержимое `.aiignore` (стандартное):**
```
node_modules/
dist/
build/
.git/
.cache/
__pycache__/
*.log
*.tmp
*.pyc
```

---

### Фаза 1: Скрипты (2–3 часа)

#### 3.1 `build_index.py` – создание `file_index.json`

```python
import os
import json
from pathlib import Path

def extract_description(filepath):
    """Извлекает первую строку документации или имя класса/функции."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('def ') or line.startswith('class '):
                    return line[:80]
                if line.startswith('"""') or line.startswith("'''"):
                    # следующая строка - описание
                    next_line = next(f).strip()
                    return next_line[:100]
    except:
        return "No description"
    return "..."

def main():
    root = Path('C:/Codex_Shared')
    index = {}
    for py_file in root.rglob('*.py'):
        if any(ignore in py_file.parts for ignore in ['.ai', 'node_modules', '__pycache__']):
            continue
        rel_path = py_file.relative_to(root)
        index[str(rel_path)] = extract_description(py_file)
    with open(root / '.ai' / 'file_index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"Индекс создан: {len(index)} файлов")

if __name__ == '__main__':
    main()
```

**Запуск:** после каждого значительного изменения кода или по требованию пользователя.

#### 3.2 `preflight.py` – перехват и проверка запроса

Встраивается как обёртка перед отправкой запроса в API Antigravity.

```python
import tiktoken
import yaml
from pathlib import Path

def estimate_tokens(text, model="gemini"):
    enc = tiktoken.get_encoding("cl100k_base")  # близко к Gemini
    return len(enc.encode(text))

def check_request(prompt, context, model_name):
    with open(Path('C:/Codex_Shared/.ai/budgets.yaml')) as f:
        limits = yaml.safe_load(f)
    input_tokens = estimate_tokens(prompt + context)
    # грубая оценка стоимости (обновить по текущим тарифам)
    if model_name == 'pro':
        cost = input_tokens / 1_000_000 * 2.5
    else:
        cost = input_tokens / 1_000_000 * 0.075
    if cost > limits['request']['max_cost'] or input_tokens > 32000:
        print(f"\n⚠️ Preflight: стоимость ~${cost:.4f}, токенов {input_tokens}")
        resp = input("Разрешить? (force/abort): ")
        if resp.lower() != 'force':
            raise Exception("Request blocked by Preflight")
    return True
```

**Интеграция:** пользователь перед вызовом Antigravity запускает `python scripts/preflight.py "мой промпт"` или скрипт автоматически подхватывается через обёртку CLI.

#### 3.3 `budget_enforcer.py` – учёт расходов

Хранит в `token_usage.jsonl` каждый вызов и проверяет дневные лимиты.

```python
import json
from datetime import date
from pathlib import Path

LOG_FILE = Path('C:/Codex_Shared/.ai/token_usage.jsonl')
BUDGET_FILE = Path('C:/Codex_Shared/.ai/budgets.yaml')

def log_call(model, input_tokens, output_tokens, cost_usd, task):
    with open(LOG_FILE, 'a') as f:
        record = {
            'date': str(date.today()),
            'model': model,
            'input': input_tokens,
            'output': output_tokens,
            'cost': cost_usd,
            'task': task[:200]
        }
        f.write(json.dumps(record) + '\n')

def check_daily_budget():
    today = str(date.today())
    total_cost = 0.0
    with open(LOG_FILE, 'r') as f:
        for line in f:
            rec = json.loads(line)
            if rec['date'] == today:
                total_cost += rec['cost']
    with open(BUDGET_FILE) as f:
        limits = yaml.safe_load(f)
    daily_limit = limits['daily']['flash'] + limits['daily']['pro']
    if total_cost > daily_limit:
        raise Exception(f"Дневной бюджет ${daily_limit} превышен. Запросы заблокированы.")
```

Вызывается перед каждым запросом после preflight.

---

### Фаза 2: Настройка роутера моделей (15 минут)

В Antigravity нет встроенного классификатора. Реализуем через **мета-команды в промпте**:

| Если промпт содержит… | Модель |
|----------------------|--------|
| `#flash8b` или `grep`, `summary`, `test`, `docs` | `gemini-2.0-flash-8b` |
| `#flash` (по умолчанию) | `gemini-2.0-flash` |
| `#pro` или `architecture`, `design`, `debug hard` | `gemini-1.5-pro` |

Пользователь просто добавляет в начало промпта:  
`#pro Исправь критический баг в распределённой транзакции` – тогда пойдёт через дорогую модель.

**Альтернатива:** скрипт-анализатор ключевых слов, автоматически выбирающий модель без тегов (но тогда возможны ошибки). Рекомендуется явные теги.

---

### Фаза 3: Обновление AGENTS.md (10 минут)

Добавить в `C:\Codex_Shared\AGENTS.md` раздел **TOKEN LIMITS** (копия из Стандарта, п.3). А также ссылку на этот Implementation Plan.

```markdown
# AGENTS.md for C:\Codex_Shared

## Обязательные лимиты для всех ИИ-ассистентов (Antigravity, Claude, и др.)

| Действие | Лимит |
|----------|-------|
| Чтение файла без строк | запрещено для файлов >50 строк |
| Максимум строк за view_file | 200 |
| Глубина grep | 3 уровня |
| … (полная таблица) |

## Экономия токенов – см. TOKEN_FIRST_STANDARD.md и ImplementationPlan.md
```

---

### Фаза 4: Пилотное тестирование (2 дня)

**Выбрать один проект** в `C:\Codex_Shared`, не критичный для бизнеса.

1. Выполнить `build_index.py`.
2. Включить **только Preflight в режиме warn** (не блокировать).
3. Разработчики используют промпты по шаблону (см. Стандарт п.5.2).
4. Собирать логи `token_usage.jsonl` для анализа.
5. Замерить расход токенов до и после (хотя бы приблизительно).

**Критерий успеха:** снижение расхода на **60%+** без увеличения числа итераций на задачу.

---

### Фаза 5: Полное внедрение (1 неделя)

- Включить Preflight в режиме **block**.
- Активировать Budget Enforcer с дневными лимитами.
- Добавить в общий чат команду `/session compress` – вручную сжимать историю при необходимости.
- Провести обучение команды: 15-минутный вебинар по новым правилам.

---

## 4. Инструкция для разработчиков (Antigravity-specific)

### 4.1 Как писать промпты (быстрый шаблон)

```markdown
#flash   (или #pro, если нужно)
ЗАДАЧА: <описание>
ФАЙЛЫ: <пути и строки>
РЕЗУЛЬТАТ: <чего ждёте>
НЕ ДЕЛАТЬ: <запреты>
```

### 4.2 Команды для управления экономией

| Команда | Действие |
|---------|----------|
| `/estimate "мой промпт"` | Оценить стоимость перед отправкой |
| `/session compress` | Сжать историю чата в краткий итог |
| `/budget status` | Показать остаток дневного бюджета |
| `/force` | Принудительно отправить запрос, даже если preflight блокирует (осторожно) |

### 4.3 Что делать, если Antigravity отвечает «недостаточно контекста»

Не пытаться угадать. Добавить в промпт:
```
Уточни, какие именно файлы или строки тебе нужны для ответа.
```
ИИ перечислит их – вы скопируете и перешлёте с разрешением.

---

## 5. Безопасность и контроль качества

### 5.1 Проверка перед кэшированием (если используем Context Caching)

```python
def safe_to_cache(text):
    dangerous = ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'PRIVATE']
    return not any(d in text.upper() for d in dangerous)
```

Кэшируем только `.ai/architecture.md` и `file_index.json`, которые не содержат секретов.

### 5.2 Метрики качества (еженедельный отчёт)

Скрипт `quality_report.py` анализирует `token_usage.jsonl` и выдаёт:
- Среднее число запросов на задачу (чем меньше, тем лучше)
- Процент запросов, потребовавших `/force` (не должно быть >10%)
- Общая экономия в долларах

Если качество падает (задач стало решаться с первой попытки на 10% меньше), увеличить лимит входных токенов до 40k и пересмотреть индексы.

---

## 6. Риски и их mitigation

| Риск | Вероятность | Mitigation |
|------|-------------|-------------|
| Разработчики забывают писать теги #flash/#pro | Средняя | Preflight по умолчанию выбирает Flash; отсутствие тега не блокирует |
| Индекс устаревает, ИИ не видит новые файлы | Высокая | `build_index.py` автоматически запускать pre-commit хуком |
| Preflight блокирует критический срочный запрос | Низкая | Команда `/force` позволяет обойти (но логируется) |
| Сложность внедрения отвлекает от разработки | Средняя | Все скрипты готовы, нужно только запустить; обучение 15 минут |

---

## 7. Что делать, если не работает (откат)

В любой момент можно **отключить** Preflight и Budget Enforcer, удалив из PATH обёртку. Все оригинальные файлы проекта остаются нетронутыми. `file_index.json` просто не используется, если его не читать.

Для полного отката:  
- Удалить `scripts/preflight.py` из автозагрузки.  
- Восстановить старый `AGENTS.md` из бэкапа.  
- Продолжать пользоваться Antigravity как раньше.

---

## 8. Ожидаемые результаты через 2 недели после полного внедрения

| Показатель | До | После | Изменение |
|------------|----|-------|------------|
| Средняя стоимость сессии (10 промптов) | $0.45 | $0.06 | **-87%** |
| Токенов на исправление одного бага | 25k | 3k | **-88%** |
| Время ответа модели (за счёт меньшего контекста) | 3 сек | 1.2 сек | **-60%** |
| Удовлетворённость разработчиков (субъективно) | 80% | 85% | +5% (меньше ждут, платят меньше) |

---

## 9. Чек-лист для завершения установки

- [ ] Созданы папки `.ai` и `scripts`
- [ ] Заполнен `architecture.md` (коротко, 500–1000 токенов)
- [ ] Запущен `build_index.py` – создан `file_index.json`
- [ ] Настроен `budgets.yaml` (дневные лимиты)
- [ ] Preflight Gateway протестирован в режиме warn
- [ ] AGENTS.md обновлён, добавлены лимиты
- [ ] Проведён пилот на одном проекте, замерена экономия >50%
- [ ] Включён блокирующий режим preflight
- [ ] Разработчики обучены шаблонам промптов и командам
- [ ] Настроен еженедельный отчёт по метрикам

---

**Дата утверждения:** ________  
**Ответственный за внедрение:** (ваше имя)  
**Подпись:** ________

```