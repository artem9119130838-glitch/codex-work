import sys
from pathlib import Path

def create_summary(completed_tasks, modified_files, open_issues):
    summary_path = Path('C:/Codex_Personal/.ai/SESSION_SUMMARY.md')
    summary_path.parent.mkdir(exist_ok=True)
    
    content = f"""# SESSION SUMMARY

## Выполненные задачи
{completed_tasks}

## Измененные файлы
{modified_files}

## Открытые вопросы и следующие шаги
{open_issues}
"""
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
        
    print(f"[SESSION COMPRESS] Сводка создана: {summary_path}")
    print(f"Вы можете скопировать этот файл и передать в новый чат, сбросив текущую историю.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        print("=== Сжатие сессии чата ===")
        completed = input("Что было сделано? (через запятую или списком): ")
        files = input("Какие файлы изменены? (через запятую или списком): ")
        issues = input("Какие открытые вопросы или следующие шаги?: ")
        
        # formatting
        completed_fmt = "\n".join(f"- {t.strip()}" for t in completed.split(',') if t.strip())
        files_fmt = "\n".join(f"- `{f.strip()}`" for f in files.split(',') if f.strip())
        issues_fmt = "\n".join(f"- {i.strip()}" for i in issues.split(',') if i.strip())
        
        create_summary(completed_fmt, files_fmt, issues_fmt)
    else:
        # standard call with args
        # python session_compress.py "JWT bug fixed" "login.py, auth.py" "Check tokens expiration"
        completed = sys.argv[1] if len(sys.argv) > 1 else "- Не указано"
        files = sys.argv[2] if len(sys.argv) > 2 else "- Не указано"
        issues = sys.argv[3] if len(sys.argv) > 3 else "- Не указано"
        
        # Format files list if comma-separated
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
            
        create_summary(completed_fmt, files_fmt, issues_fmt)

if __name__ == '__main__':
    main()
