#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


def norm_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def norm_compact(value: object) -> str:
    text = norm_text(value).lower()
    text = re.sub(r"[^0-9a-zа-яё]+", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def loose_match(gold_value: object, parsed_value: object) -> bool:
    g = norm_compact(gold_value)
    p = norm_compact(parsed_value)
    if not g and not p:
        return True
    if not g or not p:
        return False
    if g == p:
        return True
    if len(g) > 15 and p in g:
        return True
    if len(p) > 15 and g in p:
        return True
    return False


def lot_key_from_folder_path(folder_value: object) -> str:
    if folder_value is None:
        return ""
    folder = str(folder_value)
    name = folder.replace("/", "\\").rstrip("\\").split("\\")[-1]
    return name.strip()


def clip(text: str, n: int = 220) -> str:
    t = norm_text(text)
    if len(t) <= n:
        return t
    return t[: n - 1].rstrip() + "…"


@dataclass(frozen=True)
class ParsedLot:
    lot_name: str
    payment_context: str
    delivery_context: str
    source_files: List[str]
    has_reference: bool


def run_extractor(extractor_py: Path, lots_root: Path, *, only_lot: str = "") -> List[ParsedLot]:
    """
    Runs tender_min_context_extractor_v1.py and parses JSONL from stdout.
    Uses `py -3 -X utf8` to avoid mojibake in captured output.
    """
    cmd: List[str] = ["py", "-3", "-X", "utf8", str(extractor_py), str(lots_root)]
    only = (only_lot or "").strip()
    if only:
        cmd += ["--only-lot", only]
        # avoid scanning the whole lots_root in legacy extractors
        cmd += ["--limit", "1"]
    else:
        cmd += ["--limit", "0"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"Extractor failed ({proc.returncode}). stderr:\n{proc.stderr}")

    lots: List[ParsedLot] = []
    for ln in proc.stdout.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        row = json.loads(ln)
        lots.append(
            ParsedLot(
                lot_name=str(row.get("lot_name", "")).strip(),
                payment_context=norm_text(row.get("payment_context", "")),
                delivery_context=norm_text(row.get("delivery_context", "")),
                source_files=list(row.get("source_files", []) or []),
                has_reference=bool(row.get("has_reference", False)),
            )
        )
    return lots


def main(
    gold_xlsx: Path,
    lots_root: Path,
    extractor_py: Path,
    out_md: Path,
    *,
    sample: int = 15,
    only_lot: str = "",
) -> int:
    gold = pd.read_excel(gold_xlsx).fillna("")
    if "Папка" not in gold.columns:
        raise ValueError("В gold таблице не найдена колонка 'Папка'")

    gold["lot_key"] = gold["Папка"].apply(lot_key_from_folder_path)
    gold = gold[gold["lot_key"] != ""].copy()

    only = (only_lot or "").strip()
    if only:
        gold = gold[gold["lot_key"] == only].copy()
        if gold.empty:
            print(f"only-lot not found in gold: {only}", file=sys.stderr)
            return 2

    parsed_lots = run_extractor(extractor_py, lots_root, only_lot=only)
    parsed_map: Dict[str, ParsedLot] = {p.lot_name: p for p in parsed_lots if p.lot_name}

    rows: List[Dict[str, Any]] = []
    for _, r in gold.iterrows():
        key = str(r.get("lot_key", "")).strip()
        p = parsed_map.get(key)
        pay_gold = r.get("Условия оплаты верно", "")
        del_gold = r.get("Срок поставки верно", "")
        pay_parsed = "" if p is None else p.payment_context
        del_parsed = "" if p is None else p.delivery_context

        rows.append(
            {
                "lot_key": key,
                "pay_ok": loose_match(pay_gold, pay_parsed),
                "del_ok": loose_match(del_gold, del_parsed),
                "pay_gold": norm_text(pay_gold),
                "del_gold": norm_text(del_gold),
                "pay_parsed": norm_text(pay_parsed),
                "del_parsed": norm_text(del_parsed),
                "src": "" if p is None else ", ".join(p.source_files),
            }
        )

    df = pd.DataFrame(rows)
    pay_ok = int(df["pay_ok"].sum())
    del_ok = int(df["del_ok"].sum())
    total = len(df)

    bad = df[~(df["pay_ok"] & df["del_ok"])].copy()

    lines: List[str] = []
    lines.append(f"# Eval: min_context vs gold (19-05)")
    lines.append("")
    lines.append(f"- gold: `{gold_xlsx}`")
    lines.append(f"- lots_root: `{lots_root}`")
    lines.append(f"- extractor: `{extractor_py}`")
    lines.append("")
    lines.append(f"## Summary")
    lines.append(f"- total lots: {total}")
    lines.append(f"- payment ok: {pay_ok}/{total}")
    lines.append(f"- delivery ok: {del_ok}/{total}")
    lines.append(f"- both ok: {int((df['pay_ok'] & df['del_ok']).sum())}/{total}")
    lines.append("")

    # Show a small actionable sample of failures.
    lines.append(f"## Sample mismatches (first {min(sample, len(bad))})")
    lines.append("")
    shown = bad.head(sample).to_dict(orient="records")
    for row in shown:
        lines.append(f"### {row['lot_key']}")
        lines.append(f"- src: {row.get('src','')}")
        if not row["pay_ok"]:
            lines.append(f"- PAY gold: {clip(row['pay_gold'])}")
            lines.append(f"- PAY parsed: {clip(row['pay_parsed'])}")
        if not row["del_ok"]:
            lines.append(f"- DEL gold: {clip(row['del_gold'])}")
            lines.append(f"- DEL parsed: {clip(row['del_parsed'])}")
        lines.append("")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"[DONE] {out_md}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Eval extractor output vs human-gold (19-05).")
    ap.add_argument("gold_xlsx", help="Path to gold XLSX")
    ap.add_argument("lots_root", help="Lots root folder containing lot subfolders")
    ap.add_argument("extractor_py", help="Extractor .py to run (prints JSONL)")
    ap.add_argument("out_md", help="Output markdown report path")
    ap.add_argument("sample_n", nargs="?", type=int, default=15, help="How many mismatches to print (default: 15)")
    ap.add_argument("--only-lot", default="", help="(optional) Evaluate exactly one lot folder name")
    args = ap.parse_args()

    raise SystemExit(
        main(
            Path(args.gold_xlsx),
            Path(args.lots_root),
            Path(args.extractor_py),
            Path(args.out_md),
            sample=int(args.sample_n),
            only_lot=str(args.only_lot or "").strip(),
        )
    )
