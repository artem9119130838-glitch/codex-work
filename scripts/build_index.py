#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/build_index.py
Нормализация и построение поискового индекса файлов личного контура (.ai/file_index.json).
"""

import os
import sys
import json
import fnmatch
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def load_aiignore(root):
    ignore_patterns = []
    aiignore_path = root / '.aiignore'
    if aiignore_path.exists():
        with open(aiignore_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    line = line.replace('\\', '/')
                    if line.endswith('/'):
                        ignore_patterns.append(line)
                        ignore_patterns.append(line + '*')
                    else:
                        ignore_patterns.append(line)
    return ignore_patterns

def should_ignore(path, root, ignore_patterns):
    rel_path = str(path.relative_to(root)).replace('\\', '/')
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path + '/', pattern):
            return True
        parts = rel_path.split('/')
        for part in parts:
            if fnmatch.fnmatch(part, pattern.rstrip('/')):
                return True
    return False

def check_for_secrets(filepath):
    # Документация и контракты правил не исключаются
    if filepath.suffix.lower() in ['.md', '.txt']:
        return False
    # Исключаем файлы в infrastructure_registry или секретные дампы
    if 'infrastructure_registry' in str(filepath).lower():
        return True
    dangerous = ['SECRET_KEY', 'PRIVATE_KEY', 'PASSWORD =', 'PASS =']
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(4096)
            for word in dangerous:
                if word in content.upper():
                    return True
    except Exception:
        pass
    return False

def extract_description(filepath):
    try:
        ext = filepath.suffix.lower()
        if ext == '.md':
            lines = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        lines.append(line)
                        if len(lines) >= 2:
                            break
            return " | ".join(lines)[:200]
        elif ext in ['.py', '.sh', '.ps1', '.bat']:
            methods = []
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(('def ', 'class ')):
                        methods.append(line.split('(')[0])
                        if len(methods) >= 4:
                            break
            summary = f"Code file. {', '.join(methods)}" if methods else "Executable script."
            return summary[:200]
        else:
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
    
    for path in root.rglob('*'):
        if path.is_dir():
            continue
        if should_ignore(path, root, ignore_patterns):
            continue
            
        rel_path = str(path.relative_to(root)).replace('\\', '/')
        if check_for_secrets(path):
            continue
            
        allowed_extensions = [
            '.py', '.md', '.json', '.yaml', '.yml', '.js', '.ts', 
            '.sh', '.ps1', '.bat', '.ini', '.conf', '.cfg', '.txt'
        ]
        if path.suffix.lower() in allowed_extensions:
            index[rel_path] = extract_description(path)
            
    ai_dir = root / '.ai'
    ai_dir.mkdir(exist_ok=True)
    
    with open(ai_dir / 'file_index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
        
    print(f"Индекс успешно создан: {len(index)} файлов проиндексировано.")

if __name__ == '__main__':
    main()
