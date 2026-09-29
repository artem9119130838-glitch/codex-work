# -*- coding: utf-8 -*-
"""
Execution script for session compression and git push.
Writes .ai/SESSION_SUMMARY.md, cleans scratch/, commits, and pushes to master.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(r"C:\Codex")
SUMMARY_PATH = ROOT_DIR / ".ai" / "SESSION_SUMMARY.md"
SCRATCH_DIR = ROOT_DIR / "scratch"

CURRENT_DT = time.strftime('%Y-%m-%d %H:%M:%S')

SUMMARY_PARAGRAPH = (
    "В ходе сессии проведена сплошная инженерная экспертиза и дефектовка партии 16 штоков гидроцилиндров "
    "Ø180×2574 мм (AISI 431, чертеж 20.11.32.67.068) с учетом отчетов завода и переписки с технологом Михаилом: "
    "пресечена попытка завода проточить ступени Ø179.9 → 179.6 мм (выдан жесткий СТОП-ОРДЕР из-за риска выдавливания уплотнений "
    "при давлении 250–350 бар), категорически отвергнуты предложения цеха по щеточной гальванике (刷镀) для штоков № 3 и № 15 "
    "и сошлифовке штока № 1 (неустранимый брак по твердости ТВЧ < 50 HRC), сформирован официальный трехъязычный пакет предписаний "
    "Word (.docx) на русском, английском и китайском языках, полностью переведена и устранена ошибка XML в англоязычной матрице "
    "предложений цеха DATASHEET ROD-try to repare_EN.xlsx, а эталонная таблица Таблица_проверки_штоков_16шт_v2_актуальная.xlsx "
    "синхронизирована по 53 колонкам со всеми утвержденными решениями."
)

COMPLETED_TASKS = """- Экспертиза `Report of the.docx` и технических рекомендаций технолога Михаила (LV Hydramax): выдан категорический СТОП-ОРДЕР на станочную сошлифовку ступеней Ø179.9 до 179.6 мм во избежание экструзии уплотнений при давлении 250–350 бар; заморожено согласование радиуса R0.5; затребованы замеры внутреннего диаметра дна канавок.
- Сверка файлов `DATASHEET ROD-3rd time inspection.xlsx` и `DATASHEET ROD-try to repare.xlsx`: доказана 100% идентичность исходных замеров, выделены все 6 пунктов предложений завода по ремонту (U) и блок щеточной гальваники (刷镀).
- Инженерная оценка предложений завода: отклонена щеточная гальваника на штоках № 3 и № 15 (слабая адгезия, сдвиговое расслоение под 35 МПа, риск задира хонингованной гильзы); отклонена перешлифовка штока № 1 (брак закалки ТВЧ 45.8 HRC); разрешена сошлифовка избытка хрома на № 7 и № 8 строго в пределах допуска f7 (179.917–179.957 мм).
- Генерация трех официальных предписаний Word (.docx): сформированы `ПРЕДПИСАНИЕ_ЗАВОДУ_ПО_РЕМОНТУ_И_ОТГРУЗКЕ_RU.docx`, `OFFICIAL_NOTICE_ON_REPAIR_AND_SHIPMENT_EN.docx` и `关于活塞杆修复方案的技术决议与发货前要求函_CN.docx` (с латинским дублем `..._CN.docx`) с синхронизацией в Downloads и проектный каталог.
- Ликвидация ошибки Excel (Openpyxl Merge Guard) и пересборка `DATASHEET ROD-try to repare_EN.xlsx`: устранены конфликтующие области объединения ячеек, размещен полный перевод технологии щеточного осаждения (строки 25–30, 6 тематических блоков) и технический вердикт РФ.
- Актуализация эталонной матрицы `Таблица_проверки_штоков_16шт_v2_актуальная.xlsx`: пересобрана на 53 колонки с интеграцией замеров дна канавок, стопора проточки до 179.6 мм и статусов по списанию штоков № 1, 3, 15.
- Фиксация новых регламентов в `AGENTS.md` и `SCRIPTS_CATALOG.md` через процедуру `/learn`."""

MODIFIED_FILES = """- `AGENTS.md` (внесен «Регламент дефектовки металлоизделий и работы с рекламациями заводов КНР»)
- `codex_kb/SCRIPTS_CATALOG.md` (зарегистрированы скрипты дефектовки и трехъязычных предписаний)
- `scripts/create_rod_excel.py` (обновлена генерация 53 колонок и v2_актуальная)
- `scripts/generate_three_letters.py` (генератор 3 документов Word RU/EN/CN)
- `scripts/rebuild_try_to_repare_en.py` (чистый генератор DATASHEET ROD-try to repare_EN.xlsx без XML-конфликтов)
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/Таблица_проверки_штоков_16шт_v2_актуальная.xlsx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/Таблица_проверки_штоков_16шт.xlsx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/Таблица_проверки_штоков_16шт_EN.xlsx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/reports/ПРЕДПИСАНИЕ_ЗАВОДУ_ПО_РЕМОНТУ_И_ОТГРУЗКЕ_RU.docx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/reports/OFFICIAL_NOTICE_ON_REPAIR_AND_SHIPMENT_EN.docx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/reports/关于活塞杆修复方案的技术决议与发货前要求函_CN.docx`
- `projects/Price creating/Договор_62230426_Штоки_и_Трубы/reports/DATASHEET ROD-try to repare_EN.xlsx`"""

LESSONS_LEARNED = """- **Openpyxl Merge Overlap Guard:** Нельзя накладывать новые объединенные ячейки поверх существующих без предварительной очистки исходных ranges. Пересечение диапазонов приводит к повреждению файла Excel и удалению текста. Для длинных пояснений под таблицами использовать раздельное построчное объединение строк с расчетом высоты строк (85–160 pt) и wrap_text=True.
- **Windows Python Encoding:** В любых скриптах, выводящих в терминал спецсимволы (Ø) или иероглифы, обязателен вызов `sys.stdout.reconfigure(encoding='utf-8')` во избежание падения консоли cp1251.
- **Защита от суррогатного ремонта фабрик (Anti-Brush Plating):** Фабрики КНР при браке пытаются применять дешевые ручные технологии (щеточная гальваника, перешлифовка). В силовой гидравлике это категорически недопустимо из-за риска экструзии уплотнений и отслоения покрытия под давлением 250–350 бар. Брак по твердости основы ТВЧ (<50 HRC) неустраним."""

OPEN_ISSUES = """- Получить от завода замеры внутреннего диаметра дна канавок (Groove Bottom ID) по штокам № 2, 4, 5, 6, 9, 10, 11, 14, 16.
- Получить видеозапись проверки резьб калибром НЕ M170x4-6g (останов ≤1.5..2 витка, особое внимание штокам № 6 и № 9).
- Передать производителю уплотнений в РФ замеры дна канавок для финального расчета профиля манжет.
- Зафиксировать с Дэвидом и заводом финансовое списание / бесплатное переизготовление штоков № 1, 3, 15."""

PROMPT_TXT = (
    "Продолжи работу по проекту Договора № 62230426 (Штоки Ø180x2574 мм и трубы гидроцилиндров).\n"
    "1. Ознакомься со сводкой в `.ai/SESSION_SUMMARY.md` и эталонной матрицей в `projects/Price creating/Договор_62230426_Штоки_и_Трубы/Таблица_проверки_штоков_16шт_v2_актуальная.xlsx`.\n"
    "2. Проверь поступление от завода замеров внутреннего диаметра дна канавок (Groove Bottom ID) и видеопроверки резьб калибром НЕ.\n"
    "3. При получении замеров дна канавок передать данные производителю уплотнений для подтверждения возможности сборки без выдавливания манжет.\n"
    "4. Контролировать процесс станочной перешлифовки избытка хрома на штоках № 7 и № 8 (строго в поле f7: 179.917–179.957 мм).\n"
    "5. Соблюдай 'Регламент дефектовки металлоизделий и рекламаций фабрик КНР' из AGENTS.md."
)

CONTENT = f"""# SESSION SUMMARY — Итоги сессии и handoff-контекст

**Дата и время сжатия (DT):** {CURRENT_DT}

---

## 🔍 Итог сессии в один абзац
{SUMMARY_PARAGRAPH}

---

## 1. Выполненные задачи (Успехи)
{COMPLETED_TASKS}

---

## 2. Измененные и новые файлы
{MODIFIED_FILES}

---

## 3. Критические ошибки и извлеченные уроки (Lessons Learned)
{LESSONS_LEARNED}

---

## 4. Открытые вопросы и следующие шаги
{OPEN_ISSUES}

---

## 🚀 Промпт для быстрого старта нового чата (Скопируйте в новый чат)

```text
{PROMPT_TXT}
```
"""

def clean_scratch(scratch_dir):
    if not scratch_dir.exists():
        return
    print("\n--- Очистка временных файлов (scratch) ---")
    for p in scratch_dir.iterdir():
        if p.is_file() and p.suffix.lower() in ['.py', '.txt', '.log']:
            try:
                p.unlink()
                print(f"Удален временный файл: {p.name}")
            except Exception as e:
                print(f"Не удалось удалить {p.name}: {e}")

def run_git(args, desc):
    git_path = r"C:\Program Files\Git\cmd\git.exe"
    ssh_candidates = [
        Path.home() / ".ssh" / "id_ed25519",
        Path("C:/Users/Артем/.ssh/id_ed25519"),
        Path("C:/Users/Artem/.ssh/id_ed25519"),
    ]
    ssh_key_path = None
    for cand in ssh_candidates:
        if cand.exists():
            ssh_key_path = str(cand).replace("\\", "/")
            break
    if not ssh_key_path:
        ssh_key_path = str(Path.home() / ".ssh" / "id_ed25519").replace("\\", "/")
        
    env = os.environ.copy()
    env["ALLOW_EXTERNAL_PUSH"] = "1"
    
    cmd = [git_path] + args
    if "push" in args:
        cmd = [git_path, "-c", f"core.sshCommand=ssh -i {ssh_key_path} -o IdentitiesOnly=yes"] + args
        
    print(f"Git command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(ROOT_DIR), env=env, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {desc}")
        if result.stdout:
            print(result.stdout.strip())
        return True
    else:
        print(f"WARNING/FAILURE: {desc}")
        if result.stderr:
            print(result.stderr.strip())
        return False

def main():
    SUMMARY_PATH.parent.mkdir(exist_ok=True)
    with open(SUMMARY_PATH, 'w', encoding='utf-8') as f:
        f.write(CONTENT.strip() + '\n')
    print(f"SESSION_SUMMARY.md created: {SUMMARY_PATH}")
    
    clean_scratch(SCRATCH_DIR)
    
    if (ROOT_DIR / ".git").exists():
        print("\n--- Синхронизация с Git ---")
        run_git(["add", "."], "Добавление измененных файлов в индекс")
        run_git(["commit", "-m", "Auto-compress: rod inspection defect guard, trilingual B2B letters, and master matrix update"], "Создание коммита сжатия")
        run_git(["push", "origin", "master"], "Отправка коммитов в репозиторий GitHub")

if __name__ == "__main__":
    main()
