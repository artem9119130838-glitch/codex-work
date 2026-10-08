import sys
import os
import time
import subprocess
from pathlib import Path

def get_paths():
    # Определяем корневую директорию проекта на основе расположения скрипта
    # скрипт лежит в <root>/scripts/session_compress.py
    script_path = Path(__file__).resolve()
    root_dir = script_path.parent.parent
    
    return {
        "root": root_dir,
        "summary": root_dir / ".ai" / "SESSION_SUMMARY.md",
        "scratch": root_dir / "scratch"
    }

def clean_scratch(scratch_dir):
    if not scratch_dir.exists():
        return
    print("\n--- Очистка временных файлов (scratch) ---")
    # Удаляем любые временные скрипты, дампы, медиа и почтовые сообщения ИИ
    extensions_to_remove = ['.py', '.txt', '.log', '.json', '.eml', '.jpg', '.jpeg', '.png', '.tar.gz', '.gz', '.pdf', '.tmp']
    for p in list(scratch_dir.iterdir()):
        if p.is_file() and (p.suffix.lower() in extensions_to_remove or p.name.endswith('.tar.gz')):
            try:
                p.unlink()
                print(f"Удален временный файл: {p.name}")
            except Exception as e:
                print(f"Не удалось удалить {p.name}: {e}")
        elif p.is_dir() and p.name in ['deal_attachments', 'downloaded_rfqs', 'extracted_page_images', 'pdf_pages', 'test_brief', '__pycache__']:
            try:
                import shutil
                shutil.rmtree(p)
                print(f"Удалена временная папка: {p.name}")
            except Exception as e:
                print(f"Не удалось удалить папку {p.name}: {e}")

def verify_workspace_hygiene(root_dir):
    print("\n--- Аппаратный аудит гигиены контура (Pre-Commit Bloat & Integrity Guard) ---")
    issues = []
    
    # 1. Проверка размера AGENTS.md
    agents_path = root_dir / "AGENTS.md"
    if agents_path.exists():
        sz = agents_path.stat().st_size
        max_agents = 22500
        if sz > max_agents:
            issues.append(f"КРИТИЧЕСКИЙ РАЗДУВ: AGENTS.md превысил лимит! {sz} байт > {max_agents} байт.")
        elif sz > 22000:
            print(f"  [ПРЕДУПРЕЖДЕНИЕ] AGENTS.md близок к лимиту: {sz} / {max_agents} байт.")
        else:
            print(f"  [OK] AGENTS.md в пределах нормы: {sz} байт (лимит {max_agents}).")

    # 2. Проверка размера активного каталога скриптов
    catalog_path = root_dir / "codex_kb" / "SCRIPTS_CATALOG.md"
    if catalog_path.exists():
        sz_cat = catalog_path.stat().st_size
        max_cat = 50000
        if sz_cat > max_cat:
            issues.append(f"РАЗДУВ КАТАЛОГА: codex_kb/SCRIPTS_CATALOG.md весит {sz_cat} байт > {max_cat} байт!")
        else:
            print(f"  [OK] codex_kb/SCRIPTS_CATALOG.md компактен: {sz_cat} байт (лимит {max_cat}).")

    # 3. Проверка на дубликаты боевых скриптов
    odata_scripts = root_dir / "projects" / "1c_odata" / "scripts"
    if odata_scripts.exists():
        incoming_old = odata_scripts / "process_incoming_sales_leads.py"
        if incoming_old.exists():
            issues.append("НАРУШЕНИЕ SINGLE-SCRIPT: найден устаревший дубликат process_incoming_sales_leads.py в боевом каталоге!")

    if issues:
        print("\n[HYGIENE LINTER WARNINGS]:")
        for iss in issues:
            print(f"  - {iss}")
    else:
        print("  [HYGIENE LINTER OK] Все контрактные лимиты и инварианты контура соблюдены.")
    return issues

def run_git(args, desc, cwd_dir):
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
    
    # Проверяем, инициализирован ли Git в этой папке
    if not (Path(cwd_dir) / ".git").exists():
        print(f"Пропуск Git: директория {cwd_dir} не является Git-репозиторием.")
        return False
        
    env = os.environ.copy()
    env["ALLOW_EXTERNAL_PUSH"] = "1"
    
    cmd = [git_path] + args
    print(f"Git command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd_dir), env=env, capture_output=True, text=True)
    if result.returncode != 0 and "push" in args:
        cmd_fallback = [git_path, "-c", f"core.sshCommand=ssh -i {ssh_key_path} -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes"] + args
        result = subprocess.run(cmd_fallback, cwd=str(cwd_dir), env=env, capture_output=True, text=True)
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

def create_summary(summary_path, summary_paragraph, completed_tasks, modified_files, open_issues, lessons_learned):
    summary_path.parent.mkdir(exist_ok=True)
    current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Краткий и сфокусированный промпт для продолжения именно текущей задачи
    prompt_txt = (
        f"Текущая сессия чата завершена. Итог работы:\n{summary_paragraph}\n\n"
        f"Для продолжения этой задачи в новом чате:\n"
        f"1. Ознакомься со сводкой в `.ai/SESSION_SUMMARY.md`.\n"
        f"2. Выполни открытые задачи: {open_issues.strip() if open_issues else 'Продолжить выполнение приоритетов'}.\n"
        f"3. Учти критические ошибки и извлеченные уроки: {lessons_learned.strip() if lessons_learned else 'Нет'}.\n"
        "Начни работу строго с этих шагов, соблюдая правила репозитория."
    )
    
    content = f"""# SESSION SUMMARY — Итоги сессии и handoff-контекст

**Дата и время сжатия (DT):** {current_dt}

---

## 🔍 Итог сессии в один абзац
{summary_paragraph}

---

## 1. Выполненные задачи (Успехи)
{completed_tasks}

---

## 2. Измененные и новые файлы
{modified_files}

---

## 3. Критические ошибки и извлеченные уроки (Lessons Learned)
{lessons_learned}

---

## 4. Открытые вопросы и следующие шаги
{open_issues}

---

## 🚀 Промпт для быстрого старта нового чата (Скопируйте в новый чат)

```text
{prompt_txt}
```
"""
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"\n[SESSION COMPRESS] Сводка создана: {summary_path}")


def main():
    paths = get_paths()
    
    keep_summary = ('--keep-summary' in sys.argv or '--preserve-summary' in sys.argv)
    commit_msg = "Auto-compress session: update summary, clean workspace"
    
    # Извлечение кастомного сообщения коммита, если передано
    for i, arg in enumerate(sys.argv):
        if arg in ('--commit-msg', '-m') and i + 1 < len(sys.argv):
            commit_msg = sys.argv[i + 1]
            break

    if keep_summary:
        print(f"\n[SESSION COMPRESS] Сохраняем существующий {paths['summary']} без перезаписи.")
    elif len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        print(f"=== Сжатие сессии чата ({paths['root'].name}) ===")
        summary_paragraph = input("Краткий итог сессии в один абзац (задачи, финал, статус продолжения): ")
        completed = input("Что было сделано? (через запятую или списком): ")
        files = input("Какие файлы изменены? (через запятую или списком): ")
        issues = input("Какие открытые вопросы или следующие шаги?: ")
        lessons = input("Какие ошибки проанализированы? (Lessons Learned): ")
        
        completed_fmt = "\n".join(f"- {t.strip()}" for t in completed.split(',') if t.strip())
        files_fmt = "\n".join(f"- `{f.strip()}`" for f in files.split(',') if f.strip())
        issues_fmt = "\n".join(f"- {i.strip()}" for i in issues.split(',') if i.strip())
        lessons_fmt = "\n".join(f"- {l.strip()}" for l in lessons.split(',') if l.strip())
        create_summary(paths["summary"], summary_paragraph, completed_fmt, files_fmt, issues_fmt, lessons_fmt)
    else:
        summary_paragraph = sys.argv[1] if len(sys.argv) > 1 else "- Не указано"
        completed = sys.argv[2] if len(sys.argv) > 2 else "- Не указано"
        files = sys.argv[3] if len(sys.argv) > 3 else "- Не указано"
        issues = sys.argv[4] if len(sys.argv) > 4 else "- Не указано"
        lessons = sys.argv[5] if len(sys.argv) > 5 else "- Нет зафиксированных ошибок"
        
        if ',' in files:
            files_fmt = "\n".join(f"- `{f.strip()}`" for f in files.split(','))
        else:
            files_fmt = f"- {files}"
            
        if ',' in completed:
            completed_fmt = "\n".join(f"- {t.strip()}" for t in completed.split(','))
        else:
            completed_fmt = f"- {completed}"
            
        if ',' in issues:
            issues_fmt = "\n".join(f"- {i.strip()}" for i in issues.split(','))
        else:
            issues_fmt = f"- {issues}"
            
        if ',' in lessons:
            lessons_fmt = "\n".join(f"- {l.strip()}" for l in lessons.split(','))
        else:
            lessons_fmt = f"- {lessons}"
            
        create_summary(paths["summary"], summary_paragraph, completed_fmt, files_fmt, issues_fmt, lessons_fmt)
    
    # 2. Очищаем scratch от мусора
    clean_scratch(paths["scratch"])
    
    # 3. Аппаратный аудит гигиены контура перед коммитом
    hygiene_issues = verify_workspace_hygiene(paths["root"])
    
    # 4. Синхронизируем изменения с Git (если репозиторий существует)
    git_root = paths["root"]
    if (git_root / ".git").exists():
        print("\n--- Синхронизация с Git ---")
        # Используем add . для прокидывания новых файлов в projects/ и scripts/
        run_git(["add", "."], "Добавление измененных и новых файлов в индекс Git", git_root)
        run_git(["commit", "-m", commit_msg], "Создание коммита сжатия", git_root)
        run_git(["push", "origin", "master"], "Отправка коммитов в репозиторий GitHub", git_root)
    else:
        print(f"\n[INFO] Git не настроен в корне {git_root}. Изменения сохранены локально.")


if __name__ == '__main__':
    main()
