#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Run a matrix of extractor variants for EXACTLY one lot and record results.

Design goals:
- Do not lose any hypothesis (append-only results log).
- Keep runs economical: one lot, one eval per variant.
- Produce human-readable artifacts (per-variant eval .md + summary table .md).

Usage example (PowerShell):
  py -3 -X utf8 ACT\tries\run_matrix_onlylot.py ^
    --gold-xlsx "...\Сводка_лотов_верная 19-05.xlsx" ^
    --lots-root "...\ACT\тест\_РАЗОБРАНО 19-05" ^
    --only-lot "27-05__..." ^
    --out-dir "...\ACT\тест\_MATRIX"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def _safe_name(s: str) -> str:
    # stable Windows-safe stem
    bad = '<>:"/\\|?*'
    out = "".join("_" if c in bad else c for c in s)
    out = out.strip(" .")
    return out or "LOT"


def _read_try_meta(py_path: Path) -> dict[str, str]:
    """
    Parse lightweight metadata from top comment block.
    Not strict; missing keys become empty strings.
    """
    meta = {"TRY_ID": "", "HYPOTHESIS": "", "BASED_ON": "", "CREATED_AT": ""}
    try:
        head = py_path.read_text(encoding="utf-8", errors="replace").splitlines()[:60]
    except Exception:
        return meta
    for line in head:
        line = line.strip().lstrip("#").strip()
        for k in list(meta.keys()):
            if line.startswith(k + ":"):
                meta[k] = line.split(":", 1)[1].strip()
    if not meta["TRY_ID"]:
        meta["TRY_ID"] = py_path.stem
    return meta


def _run_eval(*, eval_py: Path, gold_xlsx: Path, lots_root: Path, extractor_py: Path, out_md: Path, only_lot: str) -> int:
    cmd = [
        "py",
        "-3",
        "-X",
        "utf8",
        str(eval_py),
        str(gold_xlsx),
        str(lots_root),
        str(extractor_py),
        str(out_md),
        "15",
        "--only-lot",
        only_lot,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or "")
    return int(proc.returncode)


def _parse_eval_summary(md_text: str) -> dict[str, Any]:
    # Minimal parsing: look for "- payment ok: X/Y" etc.
    out: dict[str, Any] = {"payment_ok": None, "delivery_ok": None, "both_ok": None, "total": None}
    for ln in md_text.splitlines():
        ln = ln.strip()
        if ln.startswith("- total lots:"):
            out["total"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("- payment ok:"):
            out["payment_ok"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("- delivery ok:"):
            out["delivery_ok"] = ln.split(":", 1)[1].strip()
        elif ln.startswith("- both ok:"):
            out["both_ok"] = ln.split(":", 1)[1].strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold-xlsx", required=True)
    ap.add_argument("--lots-root", required=True)
    ap.add_argument("--only-lot", required=True, help="Exact lot folder name (as in lots_root subdir).")
    ap.add_argument("--out-dir", required=True, help="Directory for artifacts (per-variant eval + summary).")
    ap.add_argument("--eval-py", default=str(Path(__file__).resolve().parents[1] / "eval_min_context_vs_gold_19_05.py"))
    ap.add_argument("--variants-dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--variants-glob", default="*.py", help="Glob inside variants-dir (default: *.py).")
    ap.add_argument("--results-jsonl", default=str(Path(__file__).resolve().parent / "results.jsonl"))
    args = ap.parse_args()

    gold_xlsx = Path(args.gold_xlsx).resolve()
    lots_root = Path(args.lots_root).resolve()
    only_lot = str(args.only_lot).strip()
    out_dir = Path(args.out_dir).resolve()
    eval_py = Path(args.eval_py).resolve()
    variants_dir = Path(args.variants_dir).resolve()
    results_jsonl = Path(args.results_jsonl).resolve()

    out_dir.mkdir(parents=True, exist_ok=True)

    variants = sorted(variants_dir.glob(args.variants_glob), key=lambda p: p.name.lower())
    # exclude helper script itself and any non-extractor utilities
    variants = [p for p in variants if p.suffix.lower() == ".py" and p.name not in {"run_matrix_onlylot.py"}]
    if not variants:
        print(f"No variants found in {variants_dir} matching {args.variants_glob}", file=sys.stderr)
        return 2

    run_id = _ts()
    lot_safe = _safe_name(only_lot)[:80]
    summary_rows: list[dict[str, Any]] = []

    for var in variants:
        meta = _read_try_meta(var)
        out_md = out_dir / f"EVAL__{lot_safe}__{var.stem}__{run_id}.md"
        rc = _run_eval(
            eval_py=eval_py,
            gold_xlsx=gold_xlsx,
            lots_root=lots_root,
            extractor_py=var,
            out_md=out_md,
            only_lot=only_lot,
        )
        md_text = out_md.read_text(encoding="utf-8", errors="replace") if out_md.exists() else ""
        summary = _parse_eval_summary(md_text) if md_text else {}
        row = {
            "run_id": run_id,
            "ts": datetime.now().isoformat(timespec="seconds"),
            "only_lot": only_lot,
            "variant_file": str(var),
            "try_id": meta.get("TRY_ID", var.stem),
            "hypothesis": meta.get("HYPOTHESIS", ""),
            "based_on": meta.get("BASED_ON", ""),
            "created_at": meta.get("CREATED_AT", ""),
            "returncode": rc,
            "payment_ok": summary.get("payment_ok"),
            "delivery_ok": summary.get("delivery_ok"),
            "both_ok": summary.get("both_ok"),
            "total": summary.get("total"),
            "eval_md": str(out_md),
        }
        summary_rows.append(row)

        # append-only results log
        results_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with results_jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # write a compact summary markdown
    summary_md = out_dir / f"MATRIX__{lot_safe}__{run_id}.md"
    lines = []
    lines.append(f"# MATRIX (only-lot)\n")
    lines.append(f"- only_lot: `{only_lot}`")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- variants_dir: `{variants_dir}`")
    lines.append(f"- results_jsonl: `{results_jsonl}`")
    lines.append("")
    lines.append("| try_id | PAY ok | DEL ok | both ok | rc | variant | eval_md |")
    lines.append("|---|---:|---:|---:|---:|---|---|")
    for r in summary_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r.get("try_id", "")),
                    str(r.get("payment_ok", "")),
                    str(r.get("delivery_ok", "")),
                    str(r.get("both_ok", "")),
                    str(r.get("returncode", "")),
                    Path(str(r.get("variant_file", ""))).name,
                    Path(str(r.get("eval_md", ""))).name,
                ]
            )
            + " |"
        )
    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[DONE] {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
