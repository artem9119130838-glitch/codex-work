#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/inspect_doc.py
======================
Канонический инструмент безопасного чтения, парсинга и конвертации
документов (PDF, DOCX, XLSX, TXT, изображения) и директорий на Windows в UTF-8.

Предотвращает UnicodeEncodeError (Windows cp1251 charmap) и ликвидирует
необходимость создания одноразовых scratch-скриптов.

Использование:
    py scripts/inspect_doc.py --file "путь/к/документу.pdf" [--stdout] [--output out.txt] [--summary]
    py scripts/inspect_doc.py --file "документ.docx" [--table-format markdown|csv]
    py scripts/inspect_doc.py --file "таблица.xlsx" [--sheet "Лист1"] [--max-rows 50]
    py scripts/inspect_doc.py --dir "путь/к/папке" [--recursive]
"""

import sys
import os
import argparse
from pathlib import Path

# Принудительная перенастройка stdout/stderr в UTF-8 для предотвращения ошибок charmap на Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def inspect_pdf(path: Path, max_pages: int = None) -> str:
    """Извлечение текста и метаданных из PDF через pypdf."""
    try:
        import pypdf
    except ImportError:
        return "[ОШИБКА] Библиотека 'pypdf' не установлена. Запустите: py -m pip install pypdf"

    reader = pypdf.PdfReader(str(path))
    total_pages = len(reader.pages)
    lines = [f"=== PDF ИНСПЕКЦИЯ: {path.name} (Всего страниц: {total_pages}) ===\n"]

    pages_to_read = total_pages if max_pages is None else min(max_pages, total_pages)
    for i in range(pages_to_read):
        page = reader.pages[i]
        lines.append(f"--- СТРАНИЦА {i+1} / {total_pages} ---")
        text = page.extract_text() or "[Страница пуста или содержит только изображения]"
        lines.append(text.strip())
        lines.append("")

    return "\n".join(lines)


def inspect_docx(path: Path) -> str:
    """Извлечение абзацев и таблиц из Word DOCX через python-docx."""
    try:
        import docx
    except ImportError:
        return "[ОШИБКА] Библиотека 'python-docx' не установлена. Запустите: py -m pip install python-docx"

    doc = docx.Document(str(path))
    lines = [f"=== WORD DOCX ИНСПЕКЦИЯ: {path.name} ===\n"]

    if doc.paragraphs:
        lines.append("--- ТЕКСТ ДОКУМЕНТА ---")
        for p in doc.paragraphs:
            txt = p.text.strip()
            if txt:
                lines.append(txt)
        lines.append("")

    if doc.tables:
        lines.append(f"--- ТАБЛИЦЫ ({len(doc.tables)} шт.) ---")
        for t_idx, table in enumerate(doc.tables):
            lines.append(f"\n[Таблица #{t_idx+1}: {len(table.rows)} строк, {len(table.columns)} колонок]")
            for r_idx, row in enumerate(table.rows):
                row_cells = [c.text.strip().replace("\n", " ") for c in row.cells]
                lines.append(f"  Строка {r_idx+1:2d} | " + " | ".join(row_cells))
        lines.append("")

    return "\n".join(lines)


def inspect_xlsx(path: Path, sheet_name: str = None, max_rows: int = 100) -> str:
    """Извлечение данных из Excel XLSX через openpyxl."""
    try:
        import openpyxl
    except ImportError:
        return "[ОШИБКА] Библиотека 'openpyxl' не установлена. Запустите: py -m pip install openpyxl"

    wb = openpyxl.load_workbook(str(path), data_only=True, read_only=True)
    lines = [f"=== EXCEL XLSX ИНСПЕКЦИЯ: {path.name} (Листы: {wb.sheetnames}) ===\n"]

    sheets = [sheet_name] if sheet_name and sheet_name in wb.sheetnames else wb.sheetnames
    for s_name in sheets:
        ws = wb[s_name]
        lines.append(f"--- ЛИСТ: {s_name} (макс. {max_rows} строк) ---")
        row_count = 0
        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                row_str = " | ".join("" if c is None else str(c).strip().replace("\n", " ") for c in row)
                lines.append(f"  {row_count+1:3d} | {row_str}")
                row_count += 1
                if row_count >= max_rows:
                    lines.append(f"  ... [показано {max_rows} строк]")
                    break
        lines.append("")

    wb.close()
    return "\n".join(lines)


def inspect_image(path: Path) -> str:
    """Извлечение метаданных и размеров изображения через Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return f"[ИНФО] Файл изображения: {path.name}, размер на диске: {path.stat().st_size} байт"

    try:
        with Image.open(str(path)) as im:
            return (
                f"=== ИЗОБРАЖЕНИЕ: {path.name} ===\n"
                f"Формат: {im.format} | Разрешение: {im.size[0]}x{im.size[1]} px | Режим: {im.mode}\n"
                f"Размер файла: {path.stat().st_size:,} байт\n"
            )
    except Exception as e:
        return f"[ОШИБКА] Не удалось открыть изображение {path.name}: {e}"


def inspect_text(path: Path) -> str:
    """Чтение текстовых файлов с автоопределением кодировки."""
    encodings = ["utf-8", "utf-8-sig", "gb18030", "gbk", "cp1251", "latin-1"]
    content = None
    used_enc = None

    raw = path.read_bytes()
    for enc in encodings:
        try:
            content = raw.decode(enc)
            used_enc = enc
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if content is None:
        content = raw.decode("utf-8", errors="replace")
        used_enc = "utf-8 (с заменой ошибок)"

    return f"=== ТЕКСТОВЫЙ ФАЙЛ: {path.name} (Кодировка: {used_enc}, строк: {len(content.splitlines())}) ===\n\n{content}"


def inspect_directory(dir_path: Path, recursive: bool = False) -> str:
    """Безопасный листинг директории с UTF-8 именами и размерами."""
    lines = [f"=== ДИРЕКТОРИЯ: {dir_path.resolve()} ===\n"]
    if not dir_path.exists() or not dir_path.is_dir():
        return f"[ОШИБКА] Директория '{dir_path}' не существует."

    items = list(dir_path.rglob("*") if recursive else dir_path.iterdir())
    items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

    lines.append(f"Всего объектов: {len(items)}")
    lines.append("-" * 70)
    for p in items:
        rel = p.relative_to(dir_path)
        if p.is_dir():
            lines.append(f"  [DIR]  {rel}/")
        else:
            lines.append(f"  [FILE] {rel} ({p.stat().st_size:,} байт)")
    lines.append("-" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Универсальный инспектор документов и папок в UTF-8.")
    parser.add_argument("--file", "-f", help="Путь к документу (PDF, DOCX, XLSX, TXT, изображение).")
    parser.add_argument("--dir", "-d", help="Путь к директории для безопасного листинга.")
    parser.add_argument("--output", "-o", help="Сохранить результат в файл (UTF-8).")
    parser.add_argument("--stdout", action="store_true", help="Вывести результат в стандартный вывод.")
    parser.add_argument("--summary", action="store_true", help="Только краткая сводка структуры.")
    parser.add_argument("--sheet", help="Имя листа для XLSX.")
    parser.add_argument("--max-rows", type=int, default=100, help="Макс. строк для XLSX (дефолт 100).")
    parser.add_argument("--pages", type=int, help="Макс. страниц для PDF.")
    parser.add_argument("--recursive", action="store_true", help="Рекурсивный листинг директории.")

    args = parser.parse_args()

    if not args.file and not args.dir:
        parser.print_help()
        sys.exit(1)

    result_text = ""

    if args.dir:
        result_text = inspect_directory(Path(args.dir), recursive=args.recursive)
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"[ОШИБКА] Файл '{file_path}' не найден.", file=sys.stderr)
            sys.exit(1)

        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            result_text = inspect_pdf(file_path, max_pages=args.pages)
        elif suffix in [".docx", ".doc"]:
            result_text = inspect_docx(file_path)
        elif suffix in [".xlsx", ".xlsm"]:
            result_text = inspect_xlsx(file_path, sheet_name=args.sheet, max_rows=args.max_rows)
        elif suffix in [".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"]:
            result_text = inspect_image(file_path)
        else:
            result_text = inspect_text(file_path)

    # Запись в файл, если указан --output
    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(result_text, encoding="utf-8")
        print(f"[OK] Результат сохранен в: {out_p.resolve()} ({len(result_text.splitlines())} строк)")

    # Вывод в stdout (по умолчанию, если не указан --output, либо если указан --stdout)
    if args.stdout or not args.output:
        print(result_text)


if __name__ == "__main__":
    main()
