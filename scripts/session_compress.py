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
    # Удаляем только временные скрипты и отчеты ИИ (.py, .txt, .log)
    # Сохраняем пользовательские файлы (.erf, .xlsx) и другие форматы
    extensions_to_remove = ['.py', '.txt', '.log']
    for p in scratch_dir.iterdir():
        if p.is_file() and p.suffix.lower() in extensions_to_remove:
            try:
                p.unlink()
                print(f"Удален временный файл: {p.name}")
            except Exception as e:
                print(f"Не удалось удалить {p.name}: {e}")

def run_git(args, desc, cwd_dir):
    git_path = r"C:\Program Files\Git\cmd\git.exe"
    ssh_key_path = r"C:/Users/Артем/.ssh/id_ed25519"
    
    # Проверяем, инициализирован ли Git в этой папке
    if not (Path(cwd_dir) / ".git").exists():
        print(f"Пропуск Git: директория {cwd_dir} не является Git-репозиторием.")
        return False
        
    env = os.environ.copy()
    env["ALLOW_EXTERNAL_PUSH"] = "1"
    
    cmd = [git_path] + args
    if "push" in args:
        cmd = [git_path, "-c", f"core.sshCommand=ssh -i {ssh_key_path} -o IdentitiesOnly=yes"] + args
        
    print(f"Git command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(cwd_dir), env=env, capture_output=True, text=True)
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

def create_summary(summary_path, completed_tasks, modified_files, open_issues, lessons_learned):
    summary_path.parent.mkdir(exist_ok=True)
    current_dt = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Динамический промпт без готовых указаний
    prompt_txt = (
        "Привет! Мы продолжаем работу над проектом.\n"
        "Прочитай файл `.ai/SESSION_SUMMARY.md` и правила в репозитории для понимания контекста.\n\n"
        f"Наша текущая задача / проблемы: {open_issues.replace('- ', '') if open_issues else 'Продолжить выполнение приоритетов проекта'}.\n\n"
        "Проанализируй текущее состояние системы и предложи оптимальные следующие шаги. "
        "Спланируй свои действия самостоятельно на основе данных в SESSION_SUMMARY.md."
    )
    
    content = f"""# SESSION SUMMARY — Итоги сессии и handoff-контекст

**Дата и время сжатия (DT):** {current_dt}

Этот файл содержит подробную техническую сводку изменений, анализ ошибок и инструкции для ИИ-ассистентов в последующих сессиях чата.

---

## 1. Выполненные задачи
{completed_tasks}

---

## 2. Измененные и новые файлы
{modified_files}

---

## 3. Анализ ошибок и уроки (Lessons Learned)
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
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        print(f"=== Сжатие сессии чата ({paths['root'].name}) ===")
        completed = input("Что было сделано? (через запятую или списком): ")
        files = input("Какие файлы изменены? (через запятую или списком): ")
        issues = input("Какие открытые вопросы или следующие шаги?: ")
        lessons = input("Какие ошибки проанализированы? (Lessons Learned): ")
        
        completed_fmt = "\n".join(f"- {t.strip()}" for t in completed.split(',') if t.strip())
        files_fmt = "\n".join(f"- `{f.strip()}`" for f in files.split(',') if f.strip())
        issues_fmt = "\n".join(f"- {i.strip()}" for i in issues.split(',') if i.strip())
        lessons_fmt = "\n".join(f"- {l.strip()}" for l in lessons.split(',') if l.strip())
    else:
        completed = sys.argv[1] if len(sys.argv) > 1 else "- Не указано"
        files = sys.argv[2] if len(sys.argv) > 2 else "- Не указано"
        issues = sys.argv[3] if len(sys.argv) > 3 else "- Не указано"
        lessons = sys.argv[4] if len(sys.argv) > 4 else "- Нет зафиксированных ошибок"
        
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
            
    # 1. Создаем сводку
    create_summary(paths["summary"], completed_fmt, files_fmt, issues_fmt, lessons_fmt)
    
    # 2. Очищаем scratch от мусора
    clean_scratch(paths["scratch"])
    
    # 3. Синхронизируем изменения с Git (если репозиторий существует)
    git_root = paths["root"]
    if (git_root / ".git").exists():
        print("\n--- Синхронизация с Git ---")
        run_git(["add", "-u"], "Добавление измененных файлов в индекс Git", git_root)
        # Относительный путь к сводке для git add
        rel_summary = os.path.relpath(paths["summary"], git_root)
        run_git(["add", rel_summary], "Добавление SESSION_SUMMARY в индекс Git", git_root)
        run_git(["commit", "-m", "Auto-compress session: update summary, clean workspace"], "Создание коммита сжатия", git_root)
        run_git(["push", "origin", "master"], "Отправка коммитов в репозиторий GitHub", git_root)
    else:
        print(f"\n[INFO] Git не настроен в корне {git_root}. Изменения сохранены локально.")

if __name__ == '__main__':
    main()
