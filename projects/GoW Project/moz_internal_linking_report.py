#!/usr/bin/env python3
"""
Build a multi-sheet internal linking workbook from Screaming Frog exports.

Inputs from the working directory:
    - internal_all.csv
    - content_all.csv
    - ai_all.csv
    - all_inlinks.csv
    - near_duplicates_report.csv (optional, recommended)

Inputs:
    - content_near_duplicates.csv (optional, recommended)

Outputs:
    - internal_linking_report.xlsx
    - target_summary.csv
    - report_targets.csv
    - report_opportunities.csv
    - filtered_inlinks.csv
    - redirect_canonical_fixes.csv
    - link_type_summary.csv
    - required_links_audit.csv
    - hub_children_audit.csv
    - cannibalization_report.csv
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    from openpyxl import Workbook
except ImportError:  # pragma: no cover
    Workbook = None


TARGET_INCLUDE_PATTERNS = ["/supplies-services-china/"]
TARGET_EXCLUDE_PATTERNS = [
    "/page/",
    "/tag/",
    "/category/",
    "/author/",
    "/wp-content/",
    "/wp-json/",
]
SOURCE_EXCLUDE_PATTERNS = ["/wp-content/", "/wp-json/"]
BAD_DESTINATION_PARTS = ["/wp-content/", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"]
EXCLUDED_LINK_PATH_PARTS = ("breadcrumb", "breadcrumbs")
EXCLUDED_ANCHORS = {"главная страница"}
COMMERCIAL_BASE = "/supplies-services-china/"
MEANINGFUL_POSITIONS = {"content", "cards"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate internal linking reports from Screaming Frog exports.")
    parser.add_argument("--internal", default="internal_all.csv")
    parser.add_argument("--content", default="content_all.csv")
    parser.add_argument("--ai", default="ai_all.csv")
    parser.add_argument("--inlinks", default="all_inlinks.csv")
    parser.add_argument("--near-duplicates", default="content_near_duplicates.csv")
    parser.add_argument("--near-duplicates-report", default="near_duplicates_report.csv")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--min-similarity", type=float, default=0.55)
    parser.add_argument("--output-dir", default=".")
    return parser.parse_args()


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def safe_int(value: str) -> int:
    try:
        return int(float((value or "").replace(",", ".")))
    except ValueError:
        return 0


def safe_float(value: str) -> float:
    try:
        return float((value or "").replace(",", "."))
    except ValueError:
        return 0.0


def normalize_url(url: str) -> str:
    return (url or "").strip()


def path_matches(url: str, patterns: Sequence[str]) -> bool:
    lowered = url.lower()
    return any(pattern.lower() in lowered for pattern in patterns)


def is_target_url(url: str) -> bool:
    return path_matches(url, TARGET_INCLUDE_PATTERNS) and not path_matches(url, TARGET_EXCLUDE_PATTERNS)


def is_source_url(url: str) -> bool:
    lowered = url.lower()
    return lowered.startswith("http") and not path_matches(url, SOURCE_EXCLUDE_PATTERNS)


def is_valid_destination(url: str) -> bool:
    lowered = normalize_url(url).lower()
    return lowered.startswith("http") and not any(part in lowered for part in BAD_DESTINATION_PARTS)


def commercial_tail(url: str) -> str:
    lowered = url.lower()
    marker = COMMERCIAL_BASE.lower()
    idx = lowered.find(marker)
    if idx == -1:
        return ""
    return url[idx + len(marker):].strip("/")


def split_segments(url: str) -> List[str]:
    tail = commercial_tail(url)
    return [segment for segment in tail.split("/") if segment]


def rows_by_address(rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    result: Dict[str, Dict[str, str]] = {}
    for row in rows:
        address = normalize_url(row.get("Address", ""))
        if address:
            result[address] = row
    return result


def merge_optional_rows(base_rows: Dict[str, Dict[str, str]], optional_rows: Iterable[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    merged = dict(base_rows)
    for row in optional_rows:
        address = normalize_url(row.get("Address", ""))
        if not address:
            continue
        current = dict(merged.get(address, {}))
        current.update(row)
        merged[address] = current
    return merged


def merge_internal_and_content(internal_rows: List[Dict[str, str]], content_rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    internal_map = rows_by_address(internal_rows)
    content_map = rows_by_address(content_rows)
    merged: Dict[str, Dict[str, str]] = {}
    for url in sorted(set(internal_map) | set(content_map)):
        merged[url] = {}
        merged[url].update(content_map.get(url, {}))
        merged[url].update(internal_map.get(url, {}))
    return merged


def parse_embedding(raw: str) -> List[float]:
    if not raw:
        return []
    try:
        return [float(part) for part in raw.split(",") if part]
    except ValueError:
        return []


def embedding_map(rows: Iterable[Dict[str, str]]) -> Dict[str, List[float]]:
    result: Dict[str, List[float]] = {}
    for row in rows:
        address = normalize_url(row.get("Address", ""))
        embedding = parse_embedding(row.get("Extract embeddings from page content", ""))
        if address and embedding:
            result[address] = embedding
    return result


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def classify_position(row: Dict[str, str]) -> str:
    position = (row.get("Link Position") or "").strip().lower()
    link_path = (row.get("Link Path") or "").lower()
    if any(part in link_path for part in EXCLUDED_LINK_PATH_PARTS) or position == "breadcrumbs":
        return "Breadcrumbs"
    mapping = {
        "content": "Content",
        "cards": "Cards",
        "header": "Header",
        "footer": "Footer",
        "navigation": "Navigation",
        "aside": "Aside",
        "head": "Head",
    }
    if position in mapping:
        return mapping[position]
    if not position:
        return "Unclassified"
    return position.title()


def first_present(row: Dict[str, str], names: Sequence[str]) -> str:
    for name in names:
        if row.get(name):
            return row.get(name, "")
    return ""


def canonical_target_map(merged_rows: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    canonical_map: Dict[str, str] = {}
    for url, row in merged_rows.items():
        final_url = url
        redirect_url = normalize_url(row.get("Redirect URL", ""))
        canonical_url = normalize_url(row.get("Canonical Link Element 1", ""))
        if redirect_url:
            final_url = redirect_url
        elif canonical_url.startswith("http"):
            final_url = canonical_url
        canonical_map[url] = final_url
    return canonical_map


def resolved_url(url: str, canonical_map: Dict[str, str]) -> str:
    seen = set()
    current = normalize_url(url)
    while current and current not in seen and current in canonical_map:
        seen.add(current)
        nxt = canonical_map.get(current, current)
        if not nxt or nxt == current:
            break
        current = nxt
    return current or normalize_url(url)


def is_meaningful_link(row: Dict[str, str]) -> bool:
    if (row.get("Type") or "").strip().lower() != "hyperlink":
        return False
    if (row.get("Follow") or "").strip().lower() != "true":
        return False
    if (row.get("Link Origin") or "").strip().lower() != "html":
        return False
    if not is_valid_destination(row.get("Destination", "")):
        return False
    anchor = (row.get("Anchor") or "").strip().lower()
    if anchor in EXCLUDED_ANCHORS:
        return False
    source = normalize_url(row.get("Source", ""))
    destination = normalize_url(row.get("Destination", ""))
    if not source or not destination or source == destination:
        return False
    return True


def build_link_indexes(
    inlink_rows: List[Dict[str, str]],
    canonical_map: Dict[str, str],
) -> Tuple[List[Dict[str, object]], Dict[str, Counter], Dict[str, Dict[str, set]], Dict[str, Dict[str, Counter]]]:
    kept_rows: List[Dict[str, object]] = []
    counts_by_target: Dict[str, Counter] = defaultdict(Counter)
    donors_by_target: Dict[str, Dict[str, set]] = defaultdict(lambda: defaultdict(set))
    positions_by_pair: Dict[str, Dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))

    for raw in inlink_rows:
        if not is_meaningful_link(raw):
            continue
        source = normalize_url(raw.get("Source", ""))
        destination = normalize_url(raw.get("Destination", ""))
        resolved_destination = resolved_url(destination, canonical_map)
        category = classify_position(raw)
        row = dict(raw)
        row["Resolved Destination"] = resolved_destination
        row["Position Category"] = category
        kept_rows.append(row)
        counts_by_target[resolved_destination][category] += 1
        donors_by_target[resolved_destination][category].add(source)
        positions_by_pair[resolved_destination][source][category] += 1

    return kept_rows, counts_by_target, donors_by_target, positions_by_pair


def build_target_report(target_urls: List[str], merged_rows: Dict[str, Dict[str, str]], counts_by_target: Dict[str, Counter], donors_by_target: Dict[str, Dict[str, set]]) -> List[Dict[str, object]]:
    report: List[Dict[str, object]] = []
    for url in target_urls:
        row = merged_rows[url]
        counts = counts_by_target.get(url, Counter())
        donors = donors_by_target.get(url, {})
        report.append(
            {
                "Целевая URL": url,
                "Title": row.get("Title 1", ""),
                "H1": row.get("H1-1", ""),
                "Indexability": row.get("Indexability", ""),
                "Word Count": safe_int(row.get("Word Count", "")),
                "Spelling Errors": safe_int(first_present(row, ["Spelling Errors", "No. Spelling Errors"])),
                "Grammar Errors": safe_int(first_present(row, ["Grammar Errors", "No. Grammar Errors"])),
                "Closest Near Duplicate Score": safe_float(row.get("Closest Near Duplicate Match", "")),
                "Near Duplicates": safe_int(row.get("No. Near Duplicates", "")),
                "Closest Semantic Match": row.get("Closest Semantically Similar Address", ""),
                "Semantic Similarity Score": safe_float(row.get("Semantic Similarity Score", "")),
                "Semantically Similar Pages": safe_int(row.get("No. Semantically Similar", "")),
                "Content Inlinks": counts.get("Content", 0),
                "Card Inlinks": counts.get("Cards", 0),
                "Breadcrumb Inlinks": counts.get("Breadcrumbs", 0),
                "Header/Footer Inlinks": counts.get("Header", 0) + counts.get("Footer", 0),
                "Unique Content Donors": len(donors.get("Content", set())),
                "Unique Card Donors": len(donors.get("Cards", set())),
            }
        )
    report.sort(key=lambda item: (item["Content Inlinks"], item["Card Inlinks"], item["Целевая URL"]))
    return report


def build_opportunities(target_urls: List[str], source_urls: List[str], merged_rows: Dict[str, Dict[str, str]], embeddings: Dict[str, List[float]], positions_by_pair: Dict[str, Dict[str, Counter]], counts_by_target: Dict[str, Counter], top_k: int, min_similarity: float) -> List[Dict[str, object]]:
    report: List[Dict[str, object]] = []
    for target_url in target_urls:
        target_embedding = embeddings.get(target_url)
        if not target_embedding:
            continue
        target_row = merged_rows[target_url]
        candidates: List[Tuple[float, str]] = []
        for source_url in source_urls:
            if source_url == target_url:
                continue
            pair_positions = positions_by_pair.get(target_url, {}).get(source_url, Counter())
            if pair_positions.get("Content", 0) or pair_positions.get("Cards", 0):
                continue
            similarity = cosine_similarity(target_embedding, embeddings.get(source_url, []))
            if similarity < min_similarity:
                continue
            candidates.append((similarity, source_url))
        candidates.sort(key=lambda item: item[0], reverse=True)
        for rank, (similarity, source_url) in enumerate(candidates[:top_k], start=1):
            source_row = merged_rows[source_url]
            existing = positions_by_pair.get(target_url, {}).get(source_url, Counter())
            report.append(
                {
                    "Целевая URL": target_url,
                    "Title целевой": target_row.get("Title 1", ""),
                    "H1 целевой": target_row.get("H1-1", ""),
                    "Текущих Content Inlinks": counts_by_target.get(target_url, Counter()).get("Content", 0),
                    "Текущих Card Inlinks": counts_by_target.get(target_url, Counter()).get("Cards", 0),
                    "URL донора": source_url,
                    "Title донора": source_row.get("Title 1", ""),
                    "H1 донора": source_row.get("H1-1", ""),
                    "Cosine Similarity": round(similarity, 6),
                    "Приоритет донора": rank,
                    "Уже есть слабая ссылка": "yes" if sum(existing.values()) else "no",
                    "Текущие позиции ссылки": ", ".join(sorted(k for k, v in existing.items() if v)),
                }
            )
    report.sort(key=lambda item: (item["Текущих Content Inlinks"], item["Текущих Card Inlinks"], -item["Cosine Similarity"]))
    return report


def build_redirect_and_canonical_report(inlink_rows: List[Dict[str, str]], merged_rows: Dict[str, Dict[str, str]], canonical_map: Dict[str, str]) -> List[Dict[str, object]]:
    report: List[Dict[str, object]] = []
    for row in inlink_rows:
        if not is_meaningful_link(row):
            continue
        source = normalize_url(row.get("Source", ""))
        destination = normalize_url(row.get("Destination", ""))
        dest_row = merged_rows.get(destination)
        if not source or not destination or not dest_row:
            continue
        status_code = (dest_row.get("Status Code") or "").strip()
        redirect_url = normalize_url(dest_row.get("Redirect URL", ""))
        canonical_url = normalize_url(dest_row.get("Canonical Link Element 1", ""))
        resolved = resolved_url(destination, canonical_map)
        if status_code.startswith("3") and redirect_url:
            problem_type = "Внутренняя ссылка ведет на редирект"
        elif canonical_url.startswith("http") and canonical_url != destination:
            problem_type = "Внутренняя ссылка ведет на неканоничный URL"
        else:
            continue
        report.append(
            {
                "Источник": source,
                "Назначение сейчас": destination,
                "Каноничная цель": resolved,
                "Куда заменить": resolved,
                "Тип проблемы": problem_type,
                "Позиция ссылки": row.get("Link Position", ""),
                "Категория позиции": classify_position(row),
                "Анкор": row.get("Anchor", ""),
                "Alt текст": row.get("Alt Text", ""),
                "Путь ссылки": row.get("Link Path", ""),
                "Статус URL назначения": status_code,
            }
        )
    report.sort(key=lambda item: (item["Тип проблемы"], item["Источник"], item["Назначение сейчас"]))
    return report


def parent_chain(url: str, merged_rows: Dict[str, Dict[str, str]]) -> List[str]:
    segments = split_segments(url)
    if len(segments) < 2:
        return []
    parents: List[str] = []
    for depth in range(1, len(segments)):
        parent = f"https://longwang.ru{COMMERCIAL_BASE}{'/'.join(segments[:depth])}/"
        if parent in merged_rows:
            parents.append(parent)
    return parents


def build_required_links_audit(target_urls: List[str], merged_rows: Dict[str, Dict[str, str]], positions_by_pair: Dict[str, Dict[str, Counter]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for target in target_urls:
        for parent in parent_chain(target, merged_rows):
            positions = positions_by_pair.get(target, {}).get(parent, Counter())
            rows.append(
                {
                    "Целевая URL": target,
                    "Обязательный источник": parent,
                    "Тип связи": "Parent to Child",
                    "Есть Content ссылка": positions.get("Content", 0),
                    "Есть Card ссылка": positions.get("Cards", 0),
                    "Другие позиции": ", ".join(sorted(k for k, v in positions.items() if v and k not in {"Content", "Cards"})),
                    "Статус": "OK" if positions.get("Content", 0) or positions.get("Cards", 0) else "Missing",
                }
            )
    rows.sort(key=lambda item: (item["Статус"], item["Обязательный источник"], item["Целевая URL"]))
    return rows


def build_hub_children_audit(target_urls: List[str], merged_rows: Dict[str, Dict[str, str]], positions_by_pair: Dict[str, Dict[str, Counter]]) -> List[Dict[str, object]]:
    children_by_parent: Dict[str, List[str]] = defaultdict(list)
    for target in target_urls:
        chain = parent_chain(target, merged_rows)
        if chain:
            children_by_parent[chain[-1]].append(target)
    rows: List[Dict[str, object]] = []
    for parent, children in sorted(children_by_parent.items()):
        if len(children) < 2:
            continue
        for child in sorted(children):
            positions = positions_by_pair.get(child, {}).get(parent, Counter())
            rows.append(
                {
                    "Hub URL": parent,
                    "Child URL": child,
                    "Child Title": merged_rows.get(child, {}).get("Title 1", ""),
                    "Child H1": merged_rows.get(child, {}).get("H1-1", ""),
                    "Content Links from Hub": positions.get("Content", 0),
                    "Card Links from Hub": positions.get("Cards", 0),
                    "Other Positions": ", ".join(sorted(k for k, v in positions.items() if v and k not in {"Content", "Cards"})),
                    "Status": "OK" if positions.get("Content", 0) or positions.get("Cards", 0) else "Missing",
                }
            )
    rows.sort(key=lambda item: (item["Hub URL"], item["Status"], item["Child URL"]))
    return rows


def build_cannibalization_report(
    near_duplicate_rows: List[Dict[str, str]],
    merged_rows: Dict[str, Dict[str, str]],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    seen = set()
    for row in near_duplicate_rows:
        address = normalize_url(row.get("Address", ""))
        duplicate = normalize_url(row.get("Near Duplicate Address", ""))
        if not address or not duplicate:
            continue
        if not is_target_url(address) or not is_target_url(duplicate):
            continue
        pair_key = tuple(sorted([address, duplicate]))
        if pair_key in seen:
            continue
        seen.add(pair_key)
        source = merged_rows.get(address, {})
        target = merged_rows.get(duplicate, {})
        rows.append(
            {
                "URL 1": address,
                "Title 1": source.get("Title 1", ""),
                "H1 1": source.get("H1-1", ""),
                "URL 2": duplicate,
                "Title 2": target.get("Title 1", ""),
                "H1 2": target.get("H1-1", ""),
                "Similarity": safe_float(row.get("Similarity", "")),
                "Risk": "High" if safe_float(row.get("Similarity", "")) >= 90 else "Medium",
            }
        )
    rows.sort(key=lambda item: (-item["Similarity"], item["URL 1"], item["URL 2"]))
    return rows


def build_target_summary(target_report: List[Dict[str, object]], opportunities: List[Dict[str, object]], redirect_fixes: List[Dict[str, object]]) -> List[Dict[str, object]]:
    opportunities_by_target: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in opportunities:
        opportunities_by_target[str(row["Целевая URL"])].append(row)
    redirect_counts: Counter = Counter()
    for row in redirect_fixes:
        redirect_counts[str(row["Каноничная цель"])] += 1
    summary: List[Dict[str, object]] = []
    for row in target_report:
        target = str(row["Целевая URL"])
        opps = opportunities_by_target.get(target, [])
        best = [str(item["URL донора"]) for item in opps[:3]]
        content_inlinks = int(row.get("Content Inlinks", 0))
        card_inlinks = int(row.get("Card Inlinks", 0))
        priority = max(0, 10 - content_inlinks) + max(0, 4 - card_inlinks) + min(len(opps), 10)
        summary.append(
            {
                "Целевая URL": target,
                "Title": row.get("Title", ""),
                "H1": row.get("H1", ""),
                "Content Inlinks": content_inlinks,
                "Card Inlinks": card_inlinks,
                "Unique Content Donors": row.get("Unique Content Donors", 0),
                "Unique Card Donors": row.get("Unique Card Donors", 0),
                "Near Duplicates": row.get("Near Duplicates", 0),
                "Semantically Similar Pages": row.get("Semantically Similar Pages", 0),
                "Opportunities": len(opps),
                "Best Donor 1": best[0] if len(best) > 0 else "",
                "Best Donor 2": best[1] if len(best) > 1 else "",
                "Best Donor 3": best[2] if len(best) > 2 else "",
                "Redirect/Canonical Link Fixes": redirect_counts.get(target, 0),
                "Priority Score": priority,
            }
        )
    summary.sort(key=lambda item: (-item["Priority Score"], item["Content Inlinks"], item["Целевая URL"]))
    return summary


def build_link_type_summary(target_urls: List[str], counts_by_target: Dict[str, Counter], donors_by_target: Dict[str, Dict[str, set]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for url in target_urls:
        counts = counts_by_target.get(url, Counter())
        donors = donors_by_target.get(url, {})
        categories = sorted(set(counts) | set(donors))
        row: Dict[str, object] = {"Целевая URL": url}
        for category in categories:
            row[f"{category} Inlinks"] = counts.get(category, 0)
            row[f"{category} Unique Donors"] = len(donors.get(category, set()))
        rows.append(row)
    rows.sort(key=lambda item: item["Целевая URL"])
    return rows


def rename_filtered_rows(rows: List[Dict[str, object]]) -> List[Dict[str, object]]:
    renamed: List[Dict[str, object]] = []
    for row in rows:
        renamed.append(
            {
                "Тип ссылки": row.get("Type", ""),
                "Источник": row.get("Source", ""),
                "Назначение": row.get("Resolved Destination", row.get("Destination", "")),
                "Исходное назначение": row.get("Destination", ""),
                "Анкор": row.get("Anchor", ""),
                "Alt текст": row.get("Alt Text", ""),
                "Follow": row.get("Follow", ""),
                "Позиция ссылки": row.get("Link Position", ""),
                "Категория позиции": row.get("Position Category", ""),
                "Путь ссылки": row.get("Link Path", ""),
                "Происхождение": row.get("Link Origin", ""),
                "Статус код": row.get("Status Code", ""),
            }
        )
    return renamed


def glossary_rows() -> List[Dict[str, str]]:
    return [
        {"Sheet": "TargetSummary", "Column": "Priority Score", "Meaning": "Черновой приоритет: мало Content/Card ссылок и много opportunities = выше в списке."},
        {"Sheet": "TargetSummary", "Column": "Best Donor 1-3", "Meaning": "Лучшие кандидаты-доноры по embeddings без нормальной Content/Card ссылки на целевую страницу."},
        {"Sheet": "Targets", "Column": "Closest Near Duplicate Score", "Meaning": "Это не URL, а числовой score самого близкого near duplicate из Screaming Frog."},
        {"Sheet": "Targets", "Column": "Content Inlinks", "Meaning": "Ссылки из контента после очистки breadcrumbs и мусора."},
        {"Sheet": "Targets", "Column": "Card Inlinks", "Meaning": "Ссылки из карточек/плитки, которые Screaming Frog разметил как Cards."},
        {"Sheet": "Opportunities", "Column": "Уже есть слабая ссылка", "Meaning": "С донорской страницы уже есть какая-то ссылка, но не Content/Card или она идет на старую цель."},
        {"Sheet": "LinkTypeSummary", "Column": "Category Inlinks / Unique Donors", "Meaning": "Разбивка по типам позиций ссылок: Content, Cards, Breadcrumbs, Header, Footer и т.д."},
        {"Sheet": "RequiredLinksAudit", "Column": "Статус", "Meaning": "Проверка обязательной связи родительской страницы с дочерней по архитектуре URL."},
        {"Sheet": "HubChildrenAudit", "Column": "Status", "Meaning": "Есть ли у хаба нормальная ссылка на дочернюю страницу через Content или Cards."},
        {"Sheet": "Cannibalization", "Column": "Similarity", "Meaning": "Насколько два URL похожи по near duplicates из Screaming Frog. Это уже пары страниц, а не одиночный score."},
        {"Sheet": "RedirectFixes", "Column": "Куда заменить", "Meaning": "Финальный каноничный URL, на который стоит переписать внутреннюю ссылку."},
        {"Sheet": "FilteredInlinks", "Column": "Категория позиции", "Meaning": "Нормализованный тип позиции: Content, Cards, Breadcrumbs, Header, Footer и т.д."},
    ]


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames: List[str] = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def autosize_worksheet(ws) -> None:
    for column_cells in ws.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, min(len(value), 80))
        ws.column_dimensions[column_letter].width = max(14, min(max_length + 2, 80))


def write_xlsx(path: Path, sheets: List[Tuple[str, List[Dict[str, object]]]]) -> bool:
    if Workbook is None:
        return False
    wb = Workbook()
    wb.remove(wb.active)
    for sheet_name, rows in sheets:
        ws = wb.create_sheet(title=sheet_name[:31])
        if not rows:
            ws.append(["Нет данных"])
            continue
        headers: List[str] = []
        seen = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    headers.append(key)
        ws.append(headers)
        for row in rows:
            ws.append([row.get(header, "") for header in headers])
        ws.freeze_panes = "A2"
        autosize_worksheet(ws)
    wb.save(path)
    return True


def main() -> int:
    args = parse_args()
    base = Path.cwd()
    internal_path = (base / args.internal).resolve()
    content_path = (base / args.content).resolve()
    ai_path = (base / args.ai).resolve()
    inlinks_path = (base / args.inlinks).resolve()
    near_duplicates_path = (base / args.near_duplicates).resolve()
    near_duplicates_report_path = (base / args.near_duplicates_report).resolve()
    output_dir = (base / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    required = [internal_path, content_path, ai_path, inlinks_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("Missing required files:", file=sys.stderr)
        for item in missing:
            print(f"  - {item}", file=sys.stderr)
        return 1

    internal_rows = load_csv(internal_path)
    content_rows = load_csv(content_path)
    ai_rows = load_csv(ai_path)
    inlink_rows = load_csv(inlinks_path)
    near_duplicate_rows = load_csv(near_duplicates_path) if near_duplicates_path.exists() else []
    near_duplicate_report_rows = load_csv(near_duplicates_report_path) if near_duplicates_report_path.exists() else []

    merged_rows = merge_internal_and_content(internal_rows, content_rows)
    if near_duplicate_rows:
        merged_rows = merge_optional_rows(merged_rows, near_duplicate_rows)
    embeddings = embedding_map(ai_rows)
    canonical_map = canonical_target_map(merged_rows)
    kept_inlinks, counts_by_target, donors_by_target, positions_by_pair = build_link_indexes(inlink_rows, canonical_map)

    all_target_urls = [
        url
        for url, row in merged_rows.items()
        if is_target_url(url) and row.get("Indexability", "") == "Indexable"
    ]
    target_urls = list(all_target_urls)
    target_urls.sort()
    source_urls = [
        url
        for url, row in merged_rows.items()
        if is_source_url(url) and row.get("Indexability", "") == "Indexable" and url in embeddings
    ]
    source_urls.sort()

    target_report = build_target_report(target_urls, merged_rows, counts_by_target, donors_by_target)
    opportunity_target_urls = [url for url in target_urls if url in embeddings]
    opportunities = build_opportunities(
        opportunity_target_urls,
        source_urls,
        merged_rows,
        embeddings,
        positions_by_pair,
        counts_by_target,
        args.top_k,
        args.min_similarity,
    )
    redirect_fixes = build_redirect_and_canonical_report(inlink_rows, merged_rows, canonical_map)
    target_summary = build_target_summary(target_report, opportunities, redirect_fixes)
    link_type_summary = build_link_type_summary(target_urls, counts_by_target, donors_by_target)
    required_links = build_required_links_audit(target_urls, merged_rows, positions_by_pair)
    hub_children = build_hub_children_audit(target_urls, merged_rows, positions_by_pair)
    cannibalization = build_cannibalization_report(near_duplicate_report_rows, merged_rows)
    filtered_inlinks = rename_filtered_rows(kept_inlinks)

    write_csv(output_dir / "target_summary.csv", target_summary)
    write_csv(output_dir / "report_targets.csv", target_report)
    write_csv(output_dir / "report_opportunities.csv", opportunities)
    write_csv(output_dir / "filtered_inlinks.csv", filtered_inlinks)
    write_csv(output_dir / "redirect_canonical_fixes.csv", redirect_fixes)
    write_csv(output_dir / "link_type_summary.csv", link_type_summary)
    write_csv(output_dir / "required_links_audit.csv", required_links)
    write_csv(output_dir / "hub_children_audit.csv", hub_children)
    write_csv(output_dir / "cannibalization_report.csv", cannibalization)

    xlsx_created = write_xlsx(
        output_dir / "internal_linking_report.xlsx",
        [
            ("TargetSummary", target_summary),
            ("Targets", target_report),
            ("Opportunities", opportunities),
            ("LinkTypeSummary", link_type_summary),
            ("RequiredLinksAudit", required_links),
            ("HubChildrenAudit", hub_children),
            ("Cannibalization", cannibalization),
            ("RedirectFixes", redirect_fixes),
            ("FilteredInlinks", filtered_inlinks),
            ("Glossary", glossary_rows()),
        ],
    )

    print(f"Target summary: {output_dir / 'target_summary.csv'}")
    print(f"Targets report: {output_dir / 'report_targets.csv'}")
    print(f"Opportunities report: {output_dir / 'report_opportunities.csv'}")
    print(f"Link type summary: {output_dir / 'link_type_summary.csv'}")
    print(f"Required links audit: {output_dir / 'required_links_audit.csv'}")
    print(f"Hub children audit: {output_dir / 'hub_children_audit.csv'}")
    print(f"Cannibalization report: {output_dir / 'cannibalization_report.csv'}")
    print(f"Redirect/canonical fixes: {output_dir / 'redirect_canonical_fixes.csv'}")
    print(f"Filtered inlinks: {output_dir / 'filtered_inlinks.csv'}")
    if xlsx_created:
        print(f"Excel workbook: {output_dir / 'internal_linking_report.xlsx'}")
    else:
        print("Excel workbook was not created because openpyxl is not installed.")
    print(f"Embeddings rows found: {len(embeddings)}")
    if not embeddings:
        print("Warning: no embeddings found in ai_all.csv (column 'Extract embeddings from page content' is empty).")
        print("Targets/links sheets were built without semantic opportunities.")
    print(f"Targets analysed: {len(target_report)}")
    print(f"Opportunities found: {len(opportunities)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
