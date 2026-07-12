import os
import json
import fnmatch
from pathlib import Path

def load_aiignore(root):
    ignore_patterns = []
    aiignore_path = root / '.aiignore'
    if aiignore_path.exists():
        with open(aiignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # normalize path separators
                    line = line.replace('\\', '/')
                    # if it's a directory (ends with /), match it and everything inside
                    if line.endswith('/'):
                        ignore_patterns.append(line)
                        ignore_patterns.append(line + '*')
                    else:
                        ignore_patterns.append(line)
    return ignore_patterns

def should_ignore(path, root, ignore_patterns):
    rel_path = str(path.relative_to(root)).replace('\\', '/')
    for pattern in ignore_patterns:
        # Match directory prefixes or file patterns
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path + '/', pattern):
            return True
        # also match components of path (e.g. if node_modules/ is ignored, crm/node_modules/file.py should be ignored)
        parts = rel_path.split('/')
        for part in parts:
            if fnmatch.fnmatch(part, pattern.rstrip('/')):
                return True
    return False

def check_for_secrets(filepath):
    dangerous = ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'PRIVATE']
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # We check for UPPERCASE key assignments like API_KEY = "...", SECRET_TOKEN = "..."
            # to avoid false positives on standard code keywords, but be safe
            for word in dangerous:
                if word in content.upper():
                    # Simple heuristic: check if it looks like a variable assignment with secret
                    # e.g., PASSWORD = "xyz" or token: "abc"
                    lines = content.split('\n')
                    for line in lines:
                        if any(w in line.upper() for w in dangerous) and ('=' in line or ':' in line or 'define' in line.lower()):
                            # check if it contains actual values (quotes or alphanumeric sequences longer than 8 chars)
                            if any(q in line for q in ['"', "'"]) or len(line) > 20:
                                return True
    except Exception as e:
        pass
    return False

def extract_description(filepath):
    """Extracts summary description, class/def names, or top comments."""
    try:
        ext = filepath.suffix.lower()
        if ext == '.md':
            # read first 3 non-empty lines
            lines = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        lines.append(line)
                        if len(lines) >= 3:
                            break
            return " | ".join(lines)[:200]
        
        elif ext in ['.py', '.js', '.ts']:
            methods = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('def ') or line.startswith('class ') or line.startswith('function '):
                        methods.append(line.split('(')[0])
                        if len(methods) >= 5:
                            break
            summary = f"Code file. Definitions: {', '.join(methods)}" if methods else "Code file."
            return summary[:200]
        else:
            # generic first line
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        return line[:150]
    except Exception:
        pass
    return "No description available"

def main():
    root = Path('C:/Codex_Personal')
    ignore_patterns = load_aiignore(root)
    index = {}
    
    # We will walk through all files
    for path in root.rglob('*'):
        if path.is_dir():
            continue
        
        if should_ignore(path, root, ignore_patterns):
            continue
            
        rel_path = str(path.relative_to(root)).replace('\\', '/')
        
        # Check security
        if check_for_secrets(path):
            print(f"[WARNING] Файл {rel_path} содержит потенциальные секреты и был исключен из индексации.")
            continue
            
        # Index files that are likely text/code/configs
        allowed_extensions = [
            '.py', '.md', '.json', '.yaml', '.yml', '.js', '.ts', 
            '.sh', '.ps1', '.bat', '.ini', '.conf', '.cfg', '.txt'
        ]
        if path.suffix.lower() in allowed_extensions:
            index[rel_path] = extract_description(path)
            
    # Ensure .ai dir exists
    ai_dir = root / '.ai'
    ai_dir.mkdir(exist_ok=True)
    
    with open(ai_dir / 'file_index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    print(f"Индекс успешно создан: {len(index)} файлов проиндексировано.")

if __name__ == '__main__':
    main()
