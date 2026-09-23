# Workspace Manifest & Architecture (Personal)

## 1. Meta
- **Project type**: Windows + 1C + Docker + n8n + local computer inventory
- **Security level**: L0-L6 (detailed in [SECURITY.md](file:///C:/Codex_Personal/SECURITY.md))
- **Language policy**: ru (Russian) strictly for communication
- **Encoding**: UTF-8 BOM
- **Entry point**: [AGENTS.md](file:///C:/Codex_Personal/AGENTS.md)
- **Core rules**: [AI_RULES.md](file:///C:/Codex_Personal/AI_RULES.md)
- **Skills index**: [SKILLS.md](file:///C:/Codex_Personal/SKILLS.md)

## 2. Схема взаимодействия правил
```
[MANIFEST.md] (Манифест и Архитектура)
       ↓
[AGENTS.md] (Точка входа / ИИ-контракт)
  ┌────┴──────────────────────────┐
  ▼                               ▼
[AI_RULES.md] (TOKEN-FIRST)     [SECURITY.md] (Decision Policy L0-L6)
  └────┬──────────────────────────┘
       ▼
[SKILLS.md] (Индекс навыков)
       ▼
[Глобальные навыки] (windows, linux, git, 1c_unf, session_management)
```

## 3. Приоритет правил при конфликтах
1. [SECURITY.md](file:///C:/Codex_Personal/SECURITY.md) — Безопасность и лимиты (высший приоритет).
2. [AGENTS.md](file:///C:/Codex_Personal/AGENTS.md) — Идентичность и специфика контура.
3. [AI_RULES.md](file:///C:/Codex_Personal/AI_RULES.md) — Стандарты разработки и экономия токенов.
4. Правила конкретных проектов.
5. Глобальные навыки (Skills).
