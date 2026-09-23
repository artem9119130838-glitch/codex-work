from __future__ import annotations

import csv
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
ONE_C_FILE = ROOT / "vtb_1c_export.tsv"
PDF_WORDS_FILE = ROOT / "vtb_pdf_words.tsv"
PDF_TEXT_FILE = ROOT / "vtb_pdf_text.txt"
OUTPUT_CSV = ROOT / "vtb_discrepancies.csv"
OUTPUT_MD = ROOT / "vtb_discrepancies.md"
OUTPUT_DAILY_CSV = ROOT / "vtb_daily_mismatch.csv"

MAIN_ACCOUNT = "ВТБ Мама"
REAL_ACCOUNT_NO = "40817810540264002954"


DATE_RE = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
TIME_RE = re.compile(r"(\d{2}:\d{2})")
AMOUNT_RE = re.compile(r"([+-]?\d[\d\s]*,\d{2})")
DATE_WORD_RE = re.compile(r"^\d{2}\.\d{2}$")
YEAR_WORD_RE = re.compile(r"^20\d{2}$")


@dataclass
class Tx:
    source: str
    date: str
    time: str
    amount: float
    direction: str
    description: str
    account_from: str
    account_to: str
    comment: str
    raw: str


def parse_amount(text: str) -> float | None:
    text = (
        text.replace(" ", "")
        .replace("\xa0", "")
        .replace("_", "")
        .replace("O", "0")
        .replace("o", "0")
        .replace("О", "0")
        .replace("о", "0")
        .replace("З", "3")
        .replace("з", "3")
        .replace("l", "1")
        .replace("I", "1")
        .replace("—", "-")
        .replace("–", "-")
    )
    text = re.sub(r"[^0-9,.-]", "", text)
    if not text:
        return None
    if "," not in text:
        if "." in text and text.count(".") == 1:
            whole, frac = text.split(".")
            if len(frac) == 2:
                text = f"{whole},{frac}"
        elif len(text) >= 3:
            text = f"{text[:-2]},{text[-2:]}"
    if text.count(",") > 1:
        head, tail = text.rsplit(",", 1)
        head = head.replace(",", "")
        text = f"{head},{tail}"
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def norm_text(text: str) -> str:
    return " ".join(text.replace("\ufeff", "").split())


def normalize_ocr_digits(text: str) -> str:
    table = str.maketrans(
        {
            "O": "0",
            "o": "0",
            "О": "0",
            "о": "0",
            "З": "3",
            "з": "3",
            "I": "1",
            "l": "1",
            "М": "1",
            "M": "1",
            "В": "8",
            "в": "8",
            "д": "9",
            "Д": "9",
        }
    )
    return text.translate(table)


def parse_1c() -> list[Tx]:
    rows = list(csv.reader(ONE_C_FILE.open(encoding="utf-8"), delimiter="\t"))
    txs: list[Tx] = []
    for row in rows:
        if not row:
            continue
        raw = norm_text(row[0])
        if " от " not in raw or MAIN_ACCOUNT not in raw:
            continue
        date_match = DATE_RE.search(raw)
        time_match = TIME_RE.search(raw)
        amount_match = AMOUNT_RE.search(raw)
        if not (date_match and time_match and amount_match):
            continue
        amount = parse_amount(amount_match.group(1))
        if amount is None:
            continue

        accounts = re.findall(r"\[([^\]]+)\]", raw)
        account_from = ""
        account_to = ""
        if " из [" in raw and " в [" in raw:
            account_from = accounts[0] if len(accounts) > 0 else ""
            account_to = accounts[1] if len(accounts) > 1 else ""
        elif " из [" in raw:
            account_from = accounts[0] if accounts else ""
        elif " в [" in raw:
            account_to = accounts[0] if accounts else ""

        if f"из [{MAIN_ACCOUNT}]" in raw:
            signed = -amount
            direction = "expense"
        elif f"в [{MAIN_ACCOUNT}]" in raw:
            signed = amount
            direction = "income"
        else:
            continue

        txs.append(
            Tx(
                source="1C",
                date=date_match.group(1),
                time=time_match.group(1),
                amount=round(signed, 2),
                direction=direction,
                description=raw.split(":", 1)[0],
                account_from=account_from,
                account_to=account_to,
                comment=raw,
                raw=raw,
            )
        )
    return txs


def parse_1c_summary() -> dict[str, float]:
    rows = list(csv.reader(ONE_C_FILE.open(encoding="utf-8"), delimiter="\t"))
    result: dict[str, float] = {}
    for row in rows:
        cells = [norm_text(c) for c in row if norm_text(c)]
        if not cells:
            continue
        text = " | ".join(cells)
        if text.startswith("ВТБ Мама | 49 920,30 руб. | 2 359 947,54 руб. | 2 331 918,35 руб. | 77 949,49 руб."):
            result["start_balance"] = 49920.30
            result["income_total"] = 2359947.54
            result["expense_total"] = 2331918.35
            result["end_balance"] = 77949.49
            break
    return result


def load_pdf_words() -> dict[int, list[dict[str, str | int]]]:
    pages: dict[int, list[dict[str, str | int]]] = defaultdict(list)
    lines = PDF_WORDS_FILE.read_text(encoding="utf-8").splitlines()[1:]
    for line in lines:
        page, y, x, w, h, text = line.split("\t", 5)
        pages[int(page)].append(
            {
                "page": int(page),
                "y": int(y),
                "x": int(x),
                "w": int(w),
                "h": int(h),
                "text": norm_text(text),
            }
        )
    return pages


def join_words(words: Iterable[dict[str, str | int]]) -> str:
    return " ".join(
        w["text"] for w in sorted(words, key=lambda r: (int(r["y"]), int(r["x"])))
    )


def extract_date_anchors(page_words: list[dict[str, str | int]]) -> list[int]:
    by_y: dict[int, list[dict[str, str | int]]] = defaultdict(list)
    for word in page_words:
        by_y[int(word["y"])].append(word)

    anchors: list[int] = []
    for y in sorted(by_y):
        line = sorted(by_y[y], key=lambda r: int(r["x"]))
        xs = [int(w["x"]) for w in line]
        texts = [str(w["text"]) for w in line]
        if not xs or min(xs) > 120:
            continue
        for i in range(len(texts) - 2):
            if DATE_WORD_RE.match(texts[i]) and YEAR_WORD_RE.match(texts[i + 1]):
                anchors.append(y)
                break
    cleaned: list[int] = []
    for y in anchors:
        if not cleaned or y - cleaned[-1] > 25:
            cleaned.append(y)
    return cleaned


def split_rows(page_words: list[dict[str, str | int]]) -> list[list[dict[str, str | int]]]:
    anchors = extract_date_anchors(page_words)
    if not anchors:
        return []
    rows: list[list[dict[str, str | int]]] = []
    sorted_words = sorted(page_words, key=lambda r: (int(r["y"]), int(r["x"])))
    for idx, start in enumerate(anchors):
        end = anchors[idx + 1] - 12 if idx + 1 < len(anchors) else 10**9
        row_words = [w for w in sorted_words if start - 6 <= int(w["y"]) < end]
        rows.append(row_words)
    return rows


def bucket_text(row_words: list[dict[str, str | int]], x1: int, x2: int) -> str:
    return join_words(w for w in row_words if x1 <= int(w["x"]) < x2)


def bucket_lines(
    row_words: list[dict[str, str | int]], x1: int, x2: int
) -> list[tuple[int, str]]:
    buckets: dict[int, list[dict[str, str | int]]] = defaultdict(list)
    for word in row_words:
        x = int(word["x"])
        if x1 <= x < x2:
            buckets[int(word["y"])].append(word)
    return [(y, join_words(words)) for y, words in sorted(buckets.items())]


def parse_ocr_amount_line(text: str) -> float | None:
    text = normalize_ocr_digits(text)
    sign = -1 if "-" in text else 1
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) < 3:
        return None
    return round(sign * (int(digits) / 100.0), 2)


def parse_pdf_row(row_words: list[dict[str, str | int]]) -> Tx | None:
    date_text = bucket_text(row_words, 0, 120)
    process_text = bucket_text(row_words, 120, 240)
    amount_text = bucket_text(row_words, 240, 420)
    commission_text = bucket_text(row_words, 570, 640)
    desc_text = bucket_text(row_words, 640, 4000)

    date_norm = normalize_ocr_digits(date_text)
    date_match = re.search(r"(\d{2}\.\d{2})\s+(20\d{2}).*?(\d{2}:\d{2})", date_norm)
    if not date_match:
        return None
    date = f"{date_match.group(1)}.{date_match.group(2)}"
    time = date_match.group(3)

    amount_lines = bucket_lines(row_words, 240, 420)
    selected_amount_line = ""
    for _, line in amount_lines:
        if "-" in line:
            selected_amount_line = line
            break
    if not selected_amount_line and amount_lines:
        selected_amount_line = amount_lines[0][1]

    amount = parse_ocr_amount_line(selected_amount_line or amount_text)
    if amount is None:
        return None
    direction = "income" if amount > 0 else "expense"

    description = norm_text(desc_text)
    raw = " | ".join(
        [
            date_text,
            process_text,
            amount_text,
            commission_text,
            desc_text,
        ]
    )

    account_from = REAL_ACCOUNT_NO if amount < 0 else ""
    account_to = REAL_ACCOUNT_NO if amount > 0 else ""
    return Tx(
        source="PDF",
        date=date,
        time=time,
        amount=round(amount, 2),
        direction=direction,
        description=description,
        account_from=account_from,
        account_to=account_to,
        comment=norm_text(process_text),
        raw=norm_text(raw),
    )


def parse_pdf() -> list[Tx]:
    reader = PdfReader(str(ROOT / "c07a4921-671a-4f7c-b25a-8a3903335e8e.pdf"))
    full_text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    PDF_TEXT_FILE.write_text(full_text, encoding="utf-8")
    lines = [norm_text(line) for line in full_text.splitlines()]

    txs: list[Tx] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", line):
            i += 1
            continue

        date = line
        if i + 5 >= len(lines):
            break

        line2 = lines[i + 1]
        m = re.match(
            r"^(\d{2}:\d{2}:\d{2}) (\d{2}\.\d{2}\.\d{4}) ([-\d,\.]+) RUB ([\d,\.]+)$",
            line2,
        )
        if not m:
            i += 1
            continue

        time = m.group(1)
        amount = parse_amount(m.group(3).replace(".", ","))
        income = parse_amount(m.group(4).replace(".", ","))
        line3 = lines[i + 2]
        line4 = lines[i + 3]
        line5 = lines[i + 4]
        line6 = lines[i + 5]
        if line3 != "RUB" or line5 != "RUB":
            i += 1
            continue

        expense = parse_amount(line4.replace(".", ","))
        commission = parse_amount(line6.replace(".", ","))
        desc_lines: list[str] = []
        j = i + 6
        while j < len(lines):
            nxt = lines[j]
            if re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", nxt):
                break
            if nxt and not re.fullmatch(r"\d+", nxt):
                desc_lines.append(nxt)
            j += 1

        if amount is None:
            i = j
            continue
        signed = round(amount, 2)
        direction = "income" if signed > 0 else "expense"
        description = " ".join(desc_lines)
        card_match = re.search(r"по карте \*(\d{4})", description)
        target_match = re.search(r"счет (\d{4})", description)

        account_from = REAL_ACCOUNT_NO if signed < 0 else ""
        account_to = REAL_ACCOUNT_NO if signed > 0 else ""
        if card_match and signed < 0:
            account_from = f"{REAL_ACCOUNT_NO} / карта *{card_match.group(1)}"
        if target_match and signed > 0:
            account_to = target_match.group(1)

        txs.append(
            Tx(
                source="PDF",
                date=date,
                time=time[:5],
                amount=signed,
                direction=direction,
                description=description,
                account_from=account_from,
                account_to=account_to,
                comment=f"Обработка банком: {m.group(2)}; комиссия: {commission or 0:.2f}; приход: {income or 0:.2f}; расход: {expense or 0:.2f}",
                raw=" | ".join([date, line2, line3, line4, line5, line6, description]),
            )
        )
        i = j

    return txs


def parse_pdf_summary() -> dict[str, float]:
    first_page = (PdfReader(str(ROOT / "c07a4921-671a-4f7c-b25a-8a3903335e8e.pdf")).pages[0].extract_text() or "")
    result: dict[str, float] = {}
    patterns = {
        "start_balance": r"Баланс на начало периода ([\d,\.]+) RUB",
        "income_total": r"Поступления ([\d,\.]+) RUB",
        "end_balance": r"Баланс на конец периода ([\d,\.]+) RUB",
        "expense_total": r"Расходные операции ([\d,\.]+) RUB",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, first_page)
        if m:
            result[key] = parse_amount(m.group(1).replace(".", ",")) or 0.0
    return result


def tx_key(tx: Tx) -> tuple[str, float]:
    return tx.date, round(tx.amount, 2)


def compare(pdf_txs: list[Tx], one_c_txs: list[Tx]) -> tuple[list[Tx], list[Tx]]:
    one_c_pool: dict[tuple[str, float], list[Tx]] = defaultdict(list)
    for tx in one_c_txs:
        one_c_pool[tx_key(tx)].append(tx)

    unmatched_pdf: list[Tx] = []
    for tx in pdf_txs:
        key = tx_key(tx)
        if one_c_pool[key]:
            one_c_pool[key].pop()
        else:
            unmatched_pdf.append(tx)

    unmatched_1c: list[Tx] = []
    for leftovers in one_c_pool.values():
        unmatched_1c.extend(leftovers)
    return unmatched_pdf, unmatched_1c


def money(value: float) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    return f"{sign}{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ")


def write_outputs(unmatched_pdf: list[Tx], unmatched_1c: list[Tx]) -> None:
    rows: list[dict[str, str]] = []
    for tx in unmatched_pdf:
        rows.append(
            {
                "side": "Есть в PDF, нет в 1С",
                "date": tx.date,
                "time": tx.time,
                "amount": money(tx.amount),
                "direction": tx.direction,
                "comment": tx.description or tx.comment,
                "account_from": tx.account_from,
                "account_to": tx.account_to,
                "raw": tx.raw,
            }
        )
    for tx in unmatched_1c:
        rows.append(
            {
                "side": "Есть в 1С, нет в PDF",
                "date": tx.date,
                "time": tx.time,
                "amount": money(tx.amount),
                "direction": tx.direction,
                "comment": tx.comment,
                "account_from": tx.account_from,
                "account_to": tx.account_to,
                "raw": tx.raw,
            }
        )

    rows.sort(key=lambda r: (datetime.strptime(r["date"], "%d.%m.%Y"), r["time"], r["side"]))

    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "side",
                "date",
                "time",
                "amount",
                "direction",
                "comment",
                "account_from",
                "account_to",
                "raw",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    pdf_delta = round(sum(tx.amount for tx in unmatched_pdf), 2)
    one_c_delta = round(sum(tx.amount for tx in unmatched_1c), 2)
    net_delta = round(pdf_delta - one_c_delta, 2)

    lines = [
        "# Сверка ВТБ",
        "",
        f"- Операций в PDF: {len(unmatched_pdf)} не сопоставлено с 1С",
        f"- Операций в 1С: {len(unmatched_1c)} не сопоставлено с PDF",
        f"- Сумма несопоставленных операций PDF: {money(pdf_delta)} руб.",
        f"- Сумма несопоставленных операций 1С: {money(one_c_delta)} руб.",
        f"- Чистое расхождение (PDF - 1С): {money(net_delta)} руб.",
        "",
        "| Сторона | Дата | Время | Сумма | Направление | Комментарий | Откуда | Куда |",
        "|---|---|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        safe_comment = row["comment"].replace("|", "/")
        lines.append(
            f"| {row['side']} | {row['date']} | {row['time']} | {row['amount']} | "
            f"{row['direction']} | {safe_comment} | {row['account_from']} | {row['account_to']} |"
        )
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_daily_mismatch(one_c_txs: list[Tx], pdf_txs: list[Tx]) -> None:
    by_date_1c: dict[str, list[Tx]] = defaultdict(list)
    by_date_pdf: dict[str, list[Tx]] = defaultdict(list)
    for tx in one_c_txs:
        by_date_1c[tx.date].append(tx)
    for tx in pdf_txs:
        by_date_pdf[tx.date].append(tx)

    rows: list[dict[str, str]] = []
    all_dates = sorted(set(by_date_1c) | set(by_date_pdf), key=lambda s: datetime.strptime(s, "%d.%m.%Y"))
    for date in all_dates:
        sum_1c = round(sum(tx.amount for tx in by_date_1c[date]), 2)
        sum_pdf = round(sum(tx.amount for tx in by_date_pdf[date]), 2)
        delta = round(sum_pdf - sum_1c, 2)
        if abs(delta) < 0.01:
            continue
        rows.append(
            {
                "date": date,
                "sum_1c": money(sum_1c),
                "sum_pdf": money(sum_pdf),
                "delta_pdf_minus_1c": money(delta),
                "count_1c": str(len(by_date_1c[date])),
                "count_pdf": str(len(by_date_pdf[date])),
                "comments_1c": " || ".join(tx.comment for tx in by_date_1c[date][:5]),
                "comments_pdf": " || ".join(tx.description for tx in by_date_pdf[date][:10]),
            }
        )

    with OUTPUT_DAILY_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "sum_1c",
                "sum_pdf",
                "delta_pdf_minus_1c",
                "count_1c",
                "count_pdf",
                "comments_1c",
                "comments_pdf",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    one_c_txs = parse_1c()
    pdf_txs = parse_pdf()
    unmatched_pdf, unmatched_1c = compare(pdf_txs, one_c_txs)
    write_outputs(unmatched_pdf, unmatched_1c)
    write_daily_mismatch(one_c_txs, pdf_txs)
    one_c_summary = parse_1c_summary()
    pdf_summary = parse_pdf_summary()
    print(f"1C tx count: {len(one_c_txs)}")
    print(f"PDF tx count: {len(pdf_txs)}")
    print(f"1C summary: {one_c_summary}")
    print(f"PDF summary: {pdf_summary}")
    print(f"PDF unmatched: {len(unmatched_pdf)}")
    print(f"1C unmatched: {len(unmatched_1c)}")
    print(f"Report: {OUTPUT_MD}")
    print(f"CSV: {OUTPUT_CSV}")
    print(f"Daily CSV: {OUTPUT_DAILY_CSV}")


if __name__ == "__main__":
    main()
