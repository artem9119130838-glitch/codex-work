import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional, Tuple


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)\s*$")


@dataclass(frozen=True)
class Section:
    title: str
    lines: List[str]


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig", errors="strict") as f:
        return f.read()


def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_sections(md_text: str) -> List[Section]:
    lines = md_text.split("\n")
    sections: List[Section] = []

    current_title = ""
    current_lines: List[str] = []

    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if current_lines:
                sections.append(Section(title=current_title, lines=current_lines))
            current_title = m.group(2).strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append(Section(title=current_title, lines=current_lines))

    return sections


def _word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def _chunk_text_preserving_code_fences(lines: List[str], target_words: int, max_words: int) -> List[str]:
    chunks: List[str] = []
    current: List[str] = []
    current_words = 0
    in_code_fence = False

    def flush() -> None:
        nonlocal current, current_words
        chunk_text = "\n".join(current).strip("\n")
        if chunk_text:
            chunks.append(chunk_text)
        current = []
        current_words = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence

        line_words = _word_count(line)

        # If we are not in a code block, try to keep chunks near target size.
        if (not in_code_fence) and current and (current_words >= target_words) and (current_words + line_words > max_words):
            flush()

        current.append(line)
        current_words += line_words

        # Soft flush if we exceed max_words outside code.
        if (not in_code_fence) and current_words >= max_words:
            flush()

    flush()
    return chunks


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def iter_chunks(
    source_path: str,
    md_text: str,
    category: str,
    target_words: int,
    max_words: int,
) -> Iterator[dict]:
    sections = _split_sections(md_text)
    chunk_index = 0

    for section in sections:
        section_text = "\n".join(section.lines).strip("\n")
        if not section_text.strip():
            continue

        chunk_texts = _chunk_text_preserving_code_fences(section.lines, target_words=target_words, max_words=max_words)
        for chunk_text in chunk_texts:
            yield {
                "source_path": source_path,
                "source_section": section.title or None,
                "chunk_index": chunk_index,
                "content": chunk_text,
                "category": category,
                "content_hash": _sha256(chunk_text),
            }
            chunk_index += 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse markdown into RAG chunks (JSONL). No network calls.")
    parser.add_argument("--in", dest="in_path", required=True, help="Input .md path")
    parser.add_argument("--out", dest="out_path", required=True, help="Output JSONL path")
    parser.add_argument("--category", required=True, help="Category label for all chunks (e.g. infrastructure/methods/logistics)")
    parser.add_argument("--target-words", type=int, default=900, help="Target chunk size in words (default: 900)")
    parser.add_argument("--max-words", type=int, default=1200, help="Hard-ish cap for chunk size in words (default: 1200)")
    args = parser.parse_args()

    in_path = os.path.abspath(args.in_path)
    out_path = os.path.abspath(args.out_path)

    md_text = _normalize_newlines(_read_text(in_path))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for item in iter_chunks(
            source_path=in_path,
            md_text=md_text,
            category=args.category,
            target_words=max(50, args.target_words),
            max_words=max(args.target_words, args.max_words),
        ):
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

