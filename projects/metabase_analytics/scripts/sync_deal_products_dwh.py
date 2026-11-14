#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Product & Supplier Analytics Pipeline: sync_deal_products_dwh.py
Version: 1.0 (2026-11-11)

Extracts qualified deals (Customer pipeline from EXECUTING+ including historical
drops via crm.stagehistory.list, and Tender pipeline submitted/won/lost bids)
since a target date (default 2026-05-01), collects product composition from
CRM fields/productrows/tasks/comments/attached files, classifies products into
granular groups + supplier pools, generates a multi-level Excel report, and
upserts into PostgreSQL DWH (`analytics_deal_products`).

Supports:
- --dry-run
- --since-date YYYY-MM-DD (default: 2026-05-01)
- --extract-dossier
- --classify-batch
- --export-excel
- --sync-dwh
- Zero Secrets Policy
"""

import os
import sys
import io
import re
import json
import time
import argparse
import datetime
import urllib.request
import urllib.parse
import urllib.error

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.path.join(BASE_DIR, "scratch")
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
FILES_CACHE_DIR = os.path.join(SCRATCH_DIR, "deal_files_cache")
DOSSIER_PATH = os.path.join(SCRATCH_DIR, "deal_products_dossier.json")
MAPPING_PATH = os.path.join(DATA_DIR, "deal_products_mapping.json")
EXCEL_PATH = os.path.join(DOCS_DIR, "DEAL_PRODUCTS_AND_SUPPLIERS_REPORT_2026.xlsx")

for d in (SCRATCH_DIR, DATA_DIR, DOCS_DIR, FILES_CACHE_DIR):
    os.makedirs(d, exist_ok=True)


def load_env_candidates():
    candidates = [
        os.path.join(BASE_DIR, ".env"),
        os.path.join(BASE_DIR, "..", "1c_odata", ".env"),
        "/Storage/scripts/metabase_analytics/.env",
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k not in os.environ and v:
                                os.environ[k] = v
            except Exception:
                pass


load_env_candidates()

B24_URL = (os.environ.get("B24_WEBHOOK_URL") or os.environ.get("BITRIX24_WEBHOOK_URL", "")).rstrip("/")
B24_PORTAL = "https://b24-g4wfjq.bitrix24.ru"
PG_HOST = os.environ.get("PG_HOST", "10.10.0.1")
PG_PORT = int(os.environ.get("PG_PORT", 5433))
PG_DBNAME = os.environ.get("PG_DBNAME", "marketing_db")
PG_USER = os.environ.get("PG_USER", "vector_user")
PG_PASS = os.environ.get("PG_PASS", "")

CLOSE_REASON_MAP = {
    "306": "Национальный режим (запрет)",
    "308": "Требуется товар российского происхождения",
    "310": "Эквивалент не допускается",
    "312": "Закупка нерентабельна",
    "314": "Не нашли поставщика",
    "316": "Не получили коммерческое предложение",
    "318": "Получили коммерческое предложение слишком поздно",
    "320": "Коммерческое предложение не соответствует требованиям",
    "322": "Не успели подготовить заявку",
    "324": "Не успели подать заявку",
    "326": "Проиграли по цене",
    "328": "Заявка отклонена из-за ошибок заполнения",
    "330": "Проиграли по неценовым критериям",
    "332": "Другое",
    "334": "Запрет на экспорт из Китая",
    "336": "Недостаточный срок поставки",
    "406": "Не предоставили тех. данные, шильду",
}

CLIENT_REASON_MAP = {
    "370": "Нет ответа от клиента (пропал)",
    "372": "Отказ без объяснения причин",
    "374": "Не предоставил данные / шильдик / ТЗ",
    "376": "Дорого покупателю / Конкурент дешевле",
    "378": "Хотел постоплату (отказ от предоплаты)",
    "380": "Не устроили условия договора",
    "382": "Не устроил срок поставки",
    "384": "Купил аналог / нашел сам",
    "386": "Купил у конкурентов из наличия в РФ",
    "388": "Отпала потребность у заказчика",
    "390": "Отказался конечный заказчик (посредник)",
    "392": "Не нашли поставщика / товар в Китае",
    "394": "Снят с производства / нет на складах КНР",
    "396": "Запрет на экспорт из Китая",
    "398": "Закупка нерентабельна (маленькая партия)",
    "400": "Техническая невозможность",
    "402": "Дубль / объединен с другой сделкой",
    "404": "Другое (Заказчики)",
}

USER_MAP = {
    "14": "Сауле Бестова (экс-сотрудник)",
    "38": "Александра Пономарева",
    "20": "Азат Денишов",
    "16": "Анжелика Павлова",
    "36": "Чулпан Хузина",
    "1": "Артем",
    "26": "Салман",
}

SUPPLY_USER_MAP = {
    "20": "Азат Денишов",
    "30": "Miss Wang (Дечжоу)",
    "86": "Cindy Qian (Дечжоу)",
    "84": "Юйнань Ли (Дечжоу)",
    "44": "Liyan Wang (Дечжоу)",
    "38": "Александра Пономарева",
    "14": "Сауле Бестова (экс-сотрудник)",
}

STAGE_NAMES = {
    "NEW": "Заявка на расчет",
    "PREPARATION": "Расчет КП",
    "PREPAYMENT_INVOICE": "КП отправлен, требует ОКК",
    "EXECUTING": "Согласование КП",
    "FINAL_INVOICE": "Ожидает оплаты",
    "1": "В работе",
    "UC_UVHNXE": "Требуется заказать товар",
    "UC_Y7FU08": "Товар заказан и оплачен",
    "UC_97AEGE": "Товар прибыл, ожидает отправки",
    "2": "В пути (международном)",
    "UC_8CYR5V": "Товар прибыл в РФ, отправить!",
    "3": "Отправлен клиенту",
    "WON": "Сделка успешна",
    "LOSE": "Сделка провалена",
    "C4:NEW": "Анализ тендера",
    "C4:UC_8F7MST": "Поиск товара, анализ ВЭД",
    "C4:PREPARATION": "Расчет КП",
    "C4:UC_X1NI23": "Подготовка документов",
    "C4:UC_5Y3KYZ": "Загрузить на ЭТП",
    "C4:PREPAYMENT_INVOICE": "Заявка подана / Ожидание",
    "C4:EXECUTING": "Победа / Заключение договора",
    "C4:FINAL_INVOICE": "Исполнение договора",
    "C4:WON": "Не взяли в работу",
    "C4:LOSE": "Проигрыш",
    "C4:APOLOGY": "Не смогли отработать",
    "C4:UC_VSDEUH": "Закупки отменены заказчиком",
}

CAT0_SUCCESS_STAGES = {"FINAL_INVOICE", "1", "UC_UVHNXE", "UC_Y7FU08", "UC_97AEGE", "2", "UC_8CYR5V", "3", "WON"}
CAT0_QUALIFIED_STAGES = {"EXECUTING"} | CAT0_SUCCESS_STAGES
WON_STAGES_CAT0 = {"1", "FINAL_INVOICE", "UC_UVHNXE", "UC_Y7FU08", "UC_97AEGE", "2", "UC_8CYR5V", "3", "WON"}
WON_STAGES_CAT4 = {"C4:EXECUTING", "C4:FINAL_INVOICE"}
KNOWN_WON_DEALS = {"514", "1010", "766", "942", "840", "1332", "1278", "712", "762", "1890", "1892", "996"}
TENDER_SUBMITTED_STAGES = {"C4:PREPAYMENT_INVOICE", "C4:EXECUTING", "C4:FINAL_INVOICE"}

FILE_FIELDS = [
    "UF_CRM_1787307777328",  # ТЗ
    "UF_CRM_1785473761455",  # 技术任务书
    "UF_CRM_1785180903",     # Тех задание заказчика
    "UF_CRM_1771439859",     # Файл из 1С
    "UF_CRM_1787024458735",  # Документы на подачу
]


def parse_amt(val):
    if not val:
        return 0.0
    try:
        return float(str(val).split("|")[0].strip())
    except Exception:
        return 0.0


def b24_call(method, params=None):
    if not B24_URL:
        raise ValueError("B24_WEBHOOK_URL / BITRIX24_WEBHOOK_URL is not set!")
    url = f"{B24_URL}/{method}.json"
    data = json.dumps(params or {}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                return res.get("result")
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None


def _encode_b24_cmd(method, params):
    parts = []
    def flatten(prefix, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                flatten(f"{prefix}[{k}]" if prefix else str(k), v)
        elif isinstance(obj, list):
            for idx, v in enumerate(obj):
                flatten(f"{prefix}[{idx}]", v)
        else:
            parts.append(f"{urllib.parse.quote(str(prefix))}={urllib.parse.quote(str(obj))}")
    flatten("", params or {})
    return f"{method}?" + "&".join(parts) if parts else method


def b24_batch(commands_dict):
    """Executes up to 50 commands per Bitrix24 batch request. Returns dict {key: result}."""
    results = {}
    keys = list(commands_dict.keys())
    for i in range(0, len(keys), 50):
        chunk_keys = keys[i:i + 50]
        cmd_payload = {k: _encode_b24_cmd(commands_dict[k][0], commands_dict[k][1]) for k in chunk_keys}
        res = b24_call("batch", {"halt": 0, "cmd": cmd_payload})
        if isinstance(res, dict) and "result" in res:
            res_map = res.get("result") or {}
            if isinstance(res_map, dict):
                for k in chunk_keys:
                    results[k] = res_map.get(k)
        print(f"  [batch] processed {min(i + 50, len(keys))}/{len(keys)}", flush=True)
        time.sleep(0.15)
    return results


def fetch_deals_since(since_date_str, max_pages=200):
    items = []
    seen_ids = set()
    start = 0
    for _ in range(max_pages):
        res = b24_call("crm.deal.list", {
            "filter": {">=DATE_CREATE": f"{since_date_str}T00:00:00"},
            "select": ["*", "UF_*"],
            "order": {"ID": "DESC"},
            "start": start,
        })
        chunk = res if isinstance(res, list) else []
        if not chunk:
            break
        new_in_page = 0
        for item in chunk:
            did = str(item.get("ID") or "")
            if did and did in seen_ids:
                continue
            if did:
                seen_ids.add(did)
            items.append(item)
            new_in_page += 1
        if new_in_page == 0 or len(chunk) < 50:
            break
        start += len(chunk)
        time.sleep(0.15)
    return items


def fetch_group14_tasks_map(since_date_str, max_pages=200):
    deal_tasks = {}
    seen_tids = set()
    start = 0
    for _ in range(max_pages):
        res = b24_call("tasks.task.list", {
            "filter": {"GROUP_ID": 14, ">=CREATED_DATE": f"{since_date_str}T00:00:00"},
            "select": ["ID", "TITLE", "DESCRIPTION", "RESPONSIBLE_ID", "STATUS", "UF_CRM_TASK", "CREATED_DATE"],
            "order": {"ID": "DESC"},
            "start": start,
        })
        tasks = res.get("tasks", []) if isinstance(res, dict) else []
        if not tasks:
            break
        new_in_page = 0
        for t in tasks:
            tid = str(t.get("id") or "")
            if tid and tid in seen_tids:
                continue
            if tid:
                seen_tids.add(tid)
            new_in_page += 1
            uf_crm = t.get("ufCrmTask") or []
            for item in uf_crm:
                if isinstance(item, str) and item.startswith("D_"):
                    did = item[2:]
                    deal_tasks.setdefault(did, []).append(t)
        if new_in_page == 0 or len(tasks) < 50:
            break
        start += len(tasks)
        time.sleep(0.12)
    return deal_tasks


def strip_bb_html(text):
    if not text:
        return ""
    s = re.sub(r"<style[^>]*>.*?</style>", " ", str(text), flags=re.I | re.S)
    s = re.sub(r"[a-z]\\:\*\s*\{[^}]*\}", " ", s, flags=re.I)
    s = re.sub(r"\.[a-z0-9_-]+\s*\{[^}]*\}", " ", s, flags=re.I)
    s = re.sub(r"\[/?[a-zA-Z0-9_=:/.\-\s]+\]", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&laquo;", "«").replace("&raquo;", "»").replace("&quot;", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_text_from_bytes(fname, raw_bytes):
    ext = os.path.splitext(fname.lower())[1]
    try:
        if ext == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            txt = "\n".join((p.extract_text() or "") for p in reader.pages[:4])
            return re.sub(r"\s+", " ", txt).strip()[:1800]
        elif ext == ".docx":
            import docx
            doc = docx.Document(io.BytesIO(raw_bytes))
            parts = [p.text.strip() for p in doc.paragraphs[:40] if p.text.strip()]
            for t in doc.tables[:3]:
                for r in t.rows[:15]:
                    parts.append(" | ".join(c.text.strip().replace("\n", " ") for c in r.cells))
            return re.sub(r"\s+", " ", " ; ".join(parts)).strip()[:1800]
        elif ext == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), data_only=True, read_only=True)
            parts = []
            for sname in wb.sheetnames[:2]:
                ws = wb[sname]
                cnt = 0
                for row in ws.iter_rows(values_only=True):
                    if any(c is not None for c in row):
                        parts.append(" | ".join("" if c is None else str(c).strip() for c in row if c is not None))
                        cnt += 1
                        if cnt >= 25:
                            break
            wb.close()
            return re.sub(r"\s+", " ", " ; ".join(parts)).strip()[:1800]
    except Exception as e:
        return f"[parse_err: {e}]"
    return ""


def download_b24_field_file(deal_id, field_val):
    """Downloads file(s) from Bitrix24 deal file field dict/list and extracts text."""
    entries = field_val if isinstance(field_val, list) else ([field_val] if isinstance(field_val, dict) else [])
    texts = []
    for entry in entries[:2]:
        if not isinstance(entry, dict):
            continue
        dl_url = entry.get("downloadUrl") or ""
        fid = entry.get("id") or "x"
        if not dl_url:
            continue
        if dl_url.startswith("/"):
            # Try webhook-based disk download or portal URL with auth if accessible
            full_url = f"{B24_PORTAL}{dl_url}"
        else:
            full_url = dl_url

        # Check cache
        cached = [fn for fn in os.listdir(FILES_CACHE_DIR) if fn.startswith(f"{deal_id}_{fid}_")]
        if cached:
            fpath = os.path.join(FILES_CACHE_DIR, cached[0])
            with open(fpath, "rb") as fp:
                raw = fp.read()
            txt = extract_text_from_bytes(cached[0], raw)
            if txt:
                texts.append(f"[{cached[0]}]: {txt}")
            continue

        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                cd = resp.headers.get("Content-Disposition", "")
                m = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)', cd, re.I)
                fname = urllib.parse.unquote(m.group(1)) if m else f"file_{fid}.bin"
                raw = resp.read(8 * 1024 * 1024)
            safe_name = re.sub(r'[\\/:*?"<>|]+', "_", fname)
            fpath = os.path.join(FILES_CACHE_DIR, f"{deal_id}_{fid}_{safe_name}")
            if raw and not raw.lstrip()[:20].lower().startswith(b"<!doctype"):
                with open(fpath, "wb") as fp:
                    fp.write(raw)
                txt = extract_text_from_bytes(safe_name, raw)
                if txt:
                    texts.append(f"[{safe_name}]: {txt}")
        except Exception:
            pass
    return texts


def classify_deal_outcome(d):
    deal_id = str(d.get("ID"))
    title = d.get("TITLE") or "Без названия"
    category_id = str(d.get("CATEGORY_ID", "0"))
    stage_raw = str(d.get("STAGE_ID", "NEW"))
    tender_number = d.get("UF_CRM_TP_11") or d.get("UF_CRM_1714470984", "")
    reason_raw = str(d.get("UF_CRM_1784273768") or d.get("UF_CRM_1714470999") or "")
    client_reason_raw = str(d.get("UF_CRM_CLIENT_REASON") or "")

    is_tender = (
        (category_id == "4")
        or bool(tender_number)
        or stage_raw.startswith("C4:")
        or ("Тендер" in str(title))
        or ("Поставка" in str(title) and bool(tender_number))
    )
    pipeline_name = "Тендеры" if is_tender else "Заказчики (Прямые продажи)"
    stage_display = STAGE_NAMES.get(stage_raw, stage_raw)

    is_won = False
    if is_tender:
        if stage_raw == "C4:WON":
            close_reason = CLOSE_REASON_MAP.get(reason_raw, "Не взяли в работу")
        elif (
            (category_id == "0" and stage_raw in WON_STAGES_CAT0 and (bool(tender_number) or deal_id in KNOWN_WON_DEALS))
            or (stage_raw in WON_STAGES_CAT4)
            or (deal_id in KNOWN_WON_DEALS)
        ):
            is_won = True
            close_reason = "Выигран в тендере"
            stage_display = f"Победа ({stage_display})"
        elif stage_raw == "C4:LOSE":
            close_reason = CLOSE_REASON_MAP.get(reason_raw, "Проиграли по цене")
        elif stage_raw in ("C4:APOLOGY", "C4:UC_VSDEUH"):
            close_reason = CLOSE_REASON_MAP.get(reason_raw, "Не смогли отработать" if stage_raw == "C4:APOLOGY" else "Закупки отменены заказчиком")
        else:
            close_reason = CLOSE_REASON_MAP.get(reason_raw, "В работе" if not reason_raw else f"Код {reason_raw}")

        if is_won:
            outcome_bucket, outcome_label = "1_SUCCESS", "Победа / Контракт"
        elif stage_raw == "C4:PREPAYMENT_INVOICE":
            outcome_bucket, outcome_label = "2_REVIEW", "Заявка подана / Ожидание"
        elif stage_raw == "C4:LOSE" and close_reason == "Проиграли по цене":
            outcome_bucket, outcome_label = "3_LOST_PRICE", "Проигрыш по цене (торги)"
        else:
            outcome_bucket, outcome_label = "4_LOST_OTHER", "Отклонение / Отмена после подачи"
    else:
        if stage_raw == "WON":
            is_won = True
            close_reason = "Прямые продажи (Успешно)"
        elif stage_raw == "LOSE":
            close_reason = CLIENT_REASON_MAP.get(client_reason_raw) or CLOSE_REASON_MAP.get(reason_raw) or "Отказ (Прямые продажи)"
        else:
            close_reason = "В работе"

        if stage_raw in CAT0_SUCCESS_STAGES:
            outcome_bucket, outcome_label = "1_SUCCESS", f"Оплата / В работе ({stage_display})"
        elif stage_raw == "EXECUTING":
            outcome_bucket, outcome_label = "2_REVIEW", "Согласование КП"
        elif stage_raw == "LOSE" and ("дорог" in close_reason.lower() or "конкурент" in close_reason.lower() or "цене" in close_reason.lower()):
            outcome_bucket, outcome_label = "3_LOST_PRICE", "Отвал по цене (после согласования)"
        else:
            outcome_bucket, outcome_label = "4_LOST_OTHER", "Отвал прочий (после согласования)"

    return {
        "pipeline_name": pipeline_name,
        "is_tender": is_tender,
        "is_won": is_won,
        "stage_raw": stage_raw,
        "stage_display": stage_display,
        "close_reason": close_reason,
        "outcome_bucket": outcome_bucket,
        "outcome_label": outcome_label,
    }


def extract_dossier(since_date_str, skip_files=False, dry_run=False):
    print(f"=== [1/4] Fetching deals from Bitrix24 since {since_date_str} ===", flush=True)
    all_deals = fetch_deals_since(since_date_str)
    print(f"[OK] Loaded {len(all_deals)} total deals since {since_date_str}.", flush=True)

    # Pre-classify and identify deals needing stagehistory verification
    classified = {}
    need_history_ids = []
    direct_keep_ids = []

    for d in all_deals:
        did = str(d["ID"])
        meta = classify_deal_outcome(d)
        classified[did] = (d, meta)
        stg = meta["stage_raw"]
        if meta["is_tender"]:
            if meta["is_won"] or stg in ("C4:PREPAYMENT_INVOICE", "C4:LOSE"):
                direct_keep_ids.append(did)
            elif stg in ("C4:UC_VSDEUH", "C4:APOLOGY", "C4:WON"):
                need_history_ids.append(did)
        else:
            if stg in CAT0_QUALIFIED_STAGES:
                direct_keep_ids.append(did)
            elif stg == "LOSE":
                need_history_ids.append(did)

    print(f"Direct qualified deals: {len(direct_keep_ids)} | Checking stagehistory for {len(need_history_ids)} closed/other deals...")

    hist_cmds = {did: ("crm.stagehistory.list", {"entityTypeId": 2, "filter": {"OWNER_ID": did}}) for did in need_history_ids}
    hist_res = b24_batch(hist_cmds)

    # Also fetch stagehistory for direct_keep_ids to record reached_stage_max
    direct_hist_cmds = {did: ("crm.stagehistory.list", {"entityTypeId": 2, "filter": {"OWNER_ID": did}}) for did in direct_keep_ids}
    direct_hist_res = b24_batch(direct_hist_cmds)

    selected_deals = []
    stage_max_map = {}

    for did in direct_keep_ids:
        d, meta = classified[did]
        items = (direct_hist_res.get(did) or {}).get("items", []) if isinstance(direct_hist_res.get(did), dict) else []
        stages_passed = [it.get("STAGE_ID") for it in items if it.get("STAGE_ID")]
        stage_max_map[did] = stages_passed or [meta["stage_raw"]]
        selected_deals.append((did, d, meta))

    hist_recovered = 0
    for did in need_history_ids:
        d, meta = classified[did]
        items = (hist_res.get(did) or {}).get("items", []) if isinstance(hist_res.get(did), dict) else []
        stages_passed = [it.get("STAGE_ID") for it in items if it.get("STAGE_ID")]
        if meta["is_tender"]:
            if any(s in TENDER_SUBMITTED_STAGES for s in stages_passed):
                stage_max_map[did] = stages_passed
                selected_deals.append((did, d, meta))
                hist_recovered += 1
        else:
            if any(s in CAT0_QUALIFIED_STAGES for s in stages_passed):
                stage_max_map[did] = stages_passed
                selected_deals.append((did, d, meta))
                hist_recovered += 1

    print(f"[OK] Selected {len(selected_deals)} qualified deals (including {hist_recovered} recovered from stagehistory).")

    # Fetch Group 14 tasks map + per-deal productrows, timeline comments, activities, tasks
    print("Fetching Group 14 supply tasks, productrows, comments, and activities...")
    g14_map = fetch_group14_tasks_map(since_date_str)

    prod_cmds = {did: ("crm.deal.productrows.get", {"id": did}) for did, _, _ in selected_deals}
    tl_cmds = {did: ("crm.timeline.comment.list", {"filter": {"ENTITY_ID": did, "ENTITY_TYPE": "deal"}}) for did, _, _ in selected_deals}
    act_cmds = {did: ("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 2, "OWNER_ID": did}, "order": {"ID": "DESC"}, "select": ["ID", "SUBJECT", "DESCRIPTION", "TYPE_ID", "DIRECTION", "FILES"]}) for did, _, _ in selected_deals}
    # For deals without g14 tasks in since_date range, fetch tasks directly by UF_CRM_TASK
    missing_task_dids = [did for did, _, _ in selected_deals if did not in g14_map]
    task_cmds = {did: ("tasks.task.list", {"filter": {"UF_CRM_TASK": f"D_{did}"}, "select": ["ID", "TITLE", "DESCRIPTION", "RESPONSIBLE_ID", "GROUP_ID", "STATUS", "UF_CRM_TASK"]}) for did in missing_task_dids}

    prod_res = b24_batch(prod_cmds)
    tl_res = b24_batch(tl_cmds)
    act_res = b24_batch(act_cmds)
    extra_tasks_res = b24_batch(task_cmds)

    # Collect task IDs and company IDs (both customer companies & supplier companies from tasks)
    all_task_ids = []
    deal_tasks_final = {}
    supplier_company_ids = set()
    customer_company_ids = set()

    for did, d, _ in selected_deals:
        if d.get("COMPANY_ID"):
            customer_company_ids.add(str(d["COMPANY_ID"]))
        tlist = g14_map.get(did) or ((extra_tasks_res.get(did) or {}).get("tasks", []) if isinstance(extra_tasks_res.get(did), dict) else [])
        deal_tasks_final[did] = tlist
        for t in tlist[:5]:
            tid = str(t.get("id") or "")
            if tid:
                all_task_ids.append(tid)
            for crm_ref in (t.get("ufCrmTask") or []):
                if isinstance(crm_ref, str) and crm_ref.startswith("CO_"):
                    supplier_company_ids.add(crm_ref[3:])

    print(f"Fetching comments for {len(all_task_ids)} tasks and profiles for {len(supplier_company_ids)} supplier companies + {len(customer_company_ids)} customers...")
    tcomm_cmds = {tid: ("task.commentitem.getlist", {"TASKID": tid, "ORDER": {"ID": "DESC"}}) for tid in set(all_task_ids)}
    tcomm_res = b24_batch(tcomm_cmds)

    all_coids = supplier_company_ids | customer_company_ids
    comp_cmds = {coid: ("crm.company.get", {"id": coid}) for coid in all_coids}
    comp_res = b24_batch(comp_cmds)

    dossier = []
    parsed_files_count = 0

    for did, d, meta in selected_deals:
        title = d.get("TITLE") or ""
        prods = prod_res.get(did) if isinstance(prod_res.get(did), list) else []
        prod_names = [f"{p.get('PRODUCT_NAME')} (x{p.get('QUANTITY', 1)})" for p in prods if p.get("PRODUCT_NAME")]

        tlist = deal_tasks_final.get(did, [])
        g14_tasks = [t for t in tlist if str(t.get("groupId")) == "14"]
        main_tasks = g14_tasks or tlist

        supply_resp = ""
        attached_suppliers = []
        task_texts = []
        task_comments_texts = []

        for t in main_tasks[:5]:
            tid = str(t.get("id") or "")
            rid = str(t.get("responsibleId") or "")
            if not supply_resp and rid:
                supply_resp = SUPPLY_USER_MAP.get(rid, USER_MAP.get(rid, f"User {rid}"))
            t_title = t.get("title") or ""
            t_desc = strip_bb_html(t.get("description") or "")[:600]
            if t_title or t_desc:
                task_texts.append(f"{t_title} :: {t_desc}")
            for crm_ref in (t.get("ufCrmTask") or []):
                if isinstance(crm_ref, str) and crm_ref.startswith("CO_"):
                    coid = crm_ref[3:]
                    cobj = comp_res.get(coid) or {}
                    if cobj.get("TITLE"):
                        attached_suppliers.append(f"{cobj['TITLE']} ({strip_bb_html(cobj.get('COMMENTS') or '')[:150]})")
            comms = tcomm_res.get(tid) if isinstance(tcomm_res.get(tid), list) else []
            for cm in comms[:6]:
                msg = strip_bb_html(cm.get("POST_MESSAGE") or "")
                if msg and len(msg) > 8 and not msg.startswith("Поступила заявка от клиента"):
                    task_comments_texts.append(msg[:400])

        tl_list = tl_res.get(did) if isinstance(tl_res.get(did), list) else []
        tl_texts = [strip_bb_html(c.get("COMMENT") or "")[:350] for c in tl_list[:5] if c.get("COMMENT")]

        act_list = act_res.get(did) if isinstance(act_res.get(did), list) else []
        act_subjects = []
        act_snippets = []
        act_file_ids = []
        for a in act_list[:8]:
            subj = strip_bb_html(a.get("SUBJECT") or "")
            desc = strip_bb_html(a.get("DESCRIPTION") or "")
            if subj:
                act_subjects.append(subj[:150])
            if desc and len(desc) > 15:
                act_snippets.append(f"[{a.get('TYPE_ID')}] {subj[:60]}: {desc[:320]}")
            for fl in (a.get("FILES") or []):
                if isinstance(fl, dict) and fl.get("id"):
                    act_file_ids.append(fl["id"])

        deal_comments = strip_bb_html(d.get("COMMENTS") or "")[:600]
        last_comment = strip_bb_html(d.get("UF_CRM_DEAL_LASTCOMMENT") or "")[:300]
        pin_comment = strip_bb_html(d.get("UF_CRM_DEAL_PINCOMMENT") or "")[:300]

        # Parse files from UF_CRM_* if productrows empty or title looks generic
        file_snippets = []
        generic_title = (not prod_names) and (
            len(title) < 25
            or "поставка товара" in title.lower()
            or "заявка" in title.lower()
            or "сборный" in title.lower()
            or "тендер" in title.lower()
            or title.strip().isdigit()
        )
        if not skip_files and (generic_title or not task_texts):
            for ffield in FILE_FIELDS:
                fval = d.get(ffield)
                if fval:
                    txts = download_b24_field_file(did, fval)
                    if txts:
                        file_snippets.extend(txts)
                        parsed_files_count += 1
                    if len(file_snippets) >= 2:
                        break

        cust_obj = comp_res.get(str(d.get("COMPANY_ID") or "")) or {}
        customer_name = cust_obj.get("TITLE") or str(d.get("COMPANY_ID") or "")

        stages_passed = stage_max_map.get(did, [meta["stage_raw"]])
        reached_names = " -> ".join(STAGE_NAMES.get(s, s) for s in stages_passed[-4:])

        dossier.append({
            "deal_id": did,
            "pipeline_name": meta["pipeline_name"],
            "title": title,
            "tender_number": d.get("UF_CRM_TP_11") or "",
            "customer_name": customer_name,
            "date_create": (d.get("DATE_CREATE") or "")[:19].replace("T", " "),
            "date_close": (d.get("CLOSEDATE") or "")[:19].replace("T", " ") if d.get("CLOSED") == "Y" else None,
            "current_stage_id": meta["stage_raw"],
            "current_stage_name": meta["stage_display"],
            "reached_stage_max": reached_names[:120],
            "outcome_bucket": meta["outcome_bucket"],
            "outcome_label": meta["outcome_label"],
            "close_reason": meta["close_reason"],
            "responsible_name": USER_MAP.get(str(d.get("ASSIGNED_BY_ID")), f"ID {d.get('ASSIGNED_BY_ID')}"),
            "supply_responsible_name": supply_resp or "Не назначен",
            "deal_amount": parse_amt(d.get("UF_CRM_1776272639039")) or parse_amt(d.get("OPPORTUNITY")),
            "product_rows": prod_names,
            "deal_comments": deal_comments,
            "last_comment": last_comment,
            "pin_comment": pin_comment,
            "timeline_comments": tl_texts,
            "task_texts": task_texts[:3],
            "task_comments": task_comments_texts[:4],
            "attached_suppliers": attached_suppliers,
            "activity_subjects": act_subjects[:4],
            "activity_snippets": act_snippets[:4],
            "file_snippets": file_snippets[:2],
            "b24_url": f"{B24_PORTAL}/crm/deal/details/{did}/",
        })

    with open(DOSSIER_PATH, "w", encoding="utf-8") as fp:
        json.dump(dossier, fp, ensure_ascii=False, indent=2)

    # Summary stats
    by_pipe = {}
    by_outcome = {}
    with_prods = sum(1 for x in dossier if x["product_rows"])
    with_supps = sum(1 for x in dossier if x["attached_suppliers"])
    with_tcomms = sum(1 for x in dossier if x["task_comments"])
    with_files = sum(1 for x in dossier if x["file_snippets"])
    for x in dossier:
        by_pipe[x["pipeline_name"]] = by_pipe.get(x["pipeline_name"], 0) + 1
        by_outcome[x["outcome_bucket"]] = by_outcome.get(x["outcome_bucket"], 0) + 1

    print("\n=== DOSSIER EXTRACTION SUMMARY ===", flush=True)
    print(f"Total qualified deals: {len(dossier)}")
    print(f"By pipeline: {by_pipe}")
    print(f"By outcome: {by_outcome}")
    print(f"ProductRows: {with_prods} | Attached Suppliers: {with_supps} | Task Comments: {with_tcomms} | Parsed Files: {with_files}")
    print(f"Saved dossier to: {DOSSIER_PATH}")
    return dossier


def load_or_merge_mapping(merge_batches=False):
    mapping = {}
    if os.path.exists(MAPPING_PATH):
        try:
            with open(MAPPING_PATH, "r", encoding="utf-8") as fp:
                mapping = json.load(fp)
        except Exception:
            mapping = {}

    if not merge_batches:
        return mapping

    merged_new = 0
    for idx in (1, 2, 3):
        part_path = os.path.join(SCRATCH_DIR, f"classified_{idx}.json")
        if os.path.exists(part_path):
            try:
                with open(part_path, "r", encoding="utf-8") as fp:
                    part = json.load(fp)
                if isinstance(part, dict):
                    for k, v in part.items():
                        mapping[str(k)] = v
                        merged_new += 1
            except Exception as e:
                print(f"[WARNING] Failed to load {part_path}: {e}")

    if merged_new > 0:
        with open(MAPPING_PATH, "w", encoding="utf-8") as fp:
            json.dump(mapping, fp, ensure_ascii=False, indent=2)
        print(f"[OK] Merged {merged_new} deal classifications into {MAPPING_PATH} (total: {len(mapping)}).", flush=True)
    return mapping


def build_product_rows(dossier, mapping):
    rows = []
    unmapped = []
    for d in dossier:
        did = str(d["deal_id"])
        m = mapping.get(did)
        items = m.get("items") if isinstance(m, dict) else None
        if not items:
            unmapped.append(did)
            items = [{
                "raw_item_name": d["title"][:120],
                "wide_group": "Не классифицировано",
                "narrow_group": "Требует уточнения",
                "procurement_nature": "Серийный КНР",
                "brand_or_spec": d["title"][:80],
                "supplier_pool_type": "Не определено",
                "supplier_profile": "Требует уточнения",
                "actual_supplier": "; ".join(d.get("attached_suppliers") or [])[:250],
                "supplier_interaction_comment": d.get("close_reason") or "",
            }]

        is_multi = len(items) > 1
        src = "PRODUCTROWS" if d.get("product_rows") else ("FILES" if d.get("file_snippets") else "CRM_BATCH")
        for idx, it in enumerate(items, 1):
            rows.append({
                "deal_id": did,
                "item_index": idx,
                "pipeline_name": d["pipeline_name"],
                "title": d["title"][:500],
                "tender_number": (d.get("tender_number") or "")[:255],
                "customer_name": (d.get("customer_name") or "")[:255],
                "date_create": d.get("date_create"),
                "date_close": d.get("date_close"),
                "current_stage_id": d["current_stage_id"],
                "current_stage_name": d["current_stage_name"][:120],
                "reached_stage_max": (d.get("reached_stage_max") or "")[:120],
                "outcome_bucket": d["outcome_bucket"],
                "outcome_label": d["outcome_label"][:120],
                "close_reason": (d.get("close_reason") or "")[:255],
                "responsible_name": (d.get("responsible_name") or "")[:255],
                "supply_responsible_name": (d.get("supply_responsible_name") or "")[:255],
                "deal_amount": float(d.get("deal_amount") or 0.0),
                "is_multi_item": is_multi,
                "raw_item_name": (it.get("raw_item_name") or d["title"])[:300],
                "wide_group": (it.get("wide_group") or "Прочее")[:150],
                "narrow_group": (it.get("narrow_group") or "Прочее")[:180],
                "procurement_nature": (it.get("procurement_nature") or "Серийный КНР")[:80],
                "brand_or_spec": (it.get("brand_or_spec") or "")[:180],
                "supplier_pool_type": (it.get("supplier_pool_type") or "Не определено")[:150],
                "supplier_profile": (it.get("supplier_profile") or "Прочее")[:200],
                "actual_supplier": (it.get("actual_supplier") or "; ".join(d.get("attached_suppliers") or []))[:255],
                "supplier_interaction_comment": (it.get("supplier_interaction_comment") or d.get("close_reason") or "")[:500],
                "extraction_source": src,
                "b24_url": d["b24_url"],
            })

    if unmapped:
        print(f"[WARNING] {len(unmapped)} deals not yet in mapping: {unmapped[:10]}")
    return rows


def _calc_metrics(sub_rows):
    total_pos = len(sub_rows)
    uniq_deals = len({r["deal_id"] for r in sub_rows})
    # Count unique deals per outcome bucket inside this group to avoid multi-item skew
    deal_outcomes = {}
    for r in sub_rows:
        deal_outcomes[r["deal_id"]] = r["outcome_bucket"]
    succ = sum(1 for v in deal_outcomes.values() if v == "1_SUCCESS")
    rev = sum(1 for v in deal_outcomes.values() if v == "2_REVIEW")
    l_price = sum(1 for v in deal_outcomes.values() if v == "3_LOST_PRICE")
    l_oth = sum(1 for v in deal_outcomes.values() if v == "4_LOST_OTHER")
    closed_cnt = succ + l_price + l_oth
    win_closed = round(succ / closed_cnt * 100, 1) if closed_cnt else 0.0
    win_all = round(succ / uniq_deals * 100, 1) if uniq_deals else 0.0
    return total_pos, uniq_deals, succ, rev, l_price, l_oth, win_closed, win_all


def export_excel(rows, out_path=EXCEL_PATH):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    wb = openpyxl.Workbook()
    thin = Side(border_style="thin", color="D9E1F2")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    hdr_fill = PatternFill("solid", fgColor="1F4E78")
    hdr_font = Font(bold=True, color="FFFFFF", size=10)
    l0_fill = PatternFill("solid", fgColor="D9E1F2")
    l0_font = Font(bold=True, color="1F4E78", size=10)
    l1_fill = PatternFill("solid", fgColor="EDF2F8")
    l1_font = Font(bold=True, color="2F5597", size=10)
    l2_font = Font(color="222222", size=9)
    link_font = Font(color="0563C1", underline="single", size=9)

    def write_hierarchy_sheet(ws, title_text, axis_mode):
        ws.title = title_text
        ws.views.sheetView[0].showOutlineSymbols = True
        ws.sheet_properties.outlinePr.summaryBelow = False
        ws.freeze_panes = "A2"

        if axis_mode == "products":
            headers = [
                "Группа / Подгруппа / Позиция", "Характер закупки", "Бренд / Изделие",
                "Направление поставщика", "Позиций", "Уникальных сделок",
                "Успех / Оплата", "Согласование / Ожидание", "Проигрыш (цена)",
                "Отклонение / Прочее", "% Успеха (заверш.)", "% Успеха (всего)",
                "Статус / Комментарий взаимодействия", "Сделка Б24"
            ]
        else:
            headers = [
                "Пул поставщиков / Профиль / Подгруппа", "Широкая группа", "Характер закупки",
                "Бренд / Факт. поставщик", "Позиций", "Уникальных сделок",
                "Успех / Оплата", "Согласование / Ожидание", "Проигрыш (цена)",
                "Отклонение / Прочее", "% Успеха (заверш.)", "% Успеха (всего)",
                "Статус / Комментарий взаимодействия", "Сделка Б24"
            ]

        ws.append(headers)
        for c_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=c_idx)
            cell.fill = hdr_fill
            cell.font = hdr_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border
        ws.row_dimensions[1].height = 28

        key0 = "wide_group" if axis_mode == "products" else "supplier_pool_type"
        key1 = "narrow_group" if axis_mode == "products" else "supplier_profile"

        grp0 = {}
        for r in rows:
            grp0.setdefault(r[key0], []).append(r)

        # Sort level 0 by unique deals desc
        sorted_g0 = sorted(grp0.items(), key=lambda kv: (-len({x["deal_id"] for x in kv[1]}), kv[0]))

        row_num = 2
        for g0_name, g0_rows in sorted_g0:
            m0 = _calc_metrics(g0_rows)
            ws.append([g0_name, "", "", "", m0[0], m0[1], m0[2], m0[3], m0[4], m0[5], m0[6], m0[7], "", ""])
            for c_idx in range(1, len(headers) + 1):
                c = ws.cell(row=row_num, column=c_idx)
                c.fill = l0_fill
                c.font = l0_font
                c.border = border
                if 5 <= c_idx <= 12:
                    c.alignment = Alignment(horizontal="center")
            ws.row_dimensions[row_num].outlineLevel = 0
            row_num += 1

            grp1 = {}
            for r in g0_rows:
                grp1.setdefault(r[key1], []).append(r)
            sorted_g1 = sorted(grp1.items(), key=lambda kv: (-len({x["deal_id"] for x in kv[1]}), kv[0]))

            for g1_name, g1_rows in sorted_g1:
                m1 = _calc_metrics(g1_rows)
                ws.append([f"  ↳ {g1_name}", "", "", "", m1[0], m1[1], m1[2], m1[3], m1[4], m1[5], m1[6], m1[7], "", ""])
                for c_idx in range(1, len(headers) + 1):
                    c = ws.cell(row=row_num, column=c_idx)
                    c.fill = l1_fill
                    c.font = l1_font
                    c.border = border
                    if 5 <= c_idx <= 12:
                        c.alignment = Alignment(horizontal="center")
                ws.row_dimensions[row_num].outlineLevel = 1
                row_num += 1

                sorted_items = sorted(g1_rows, key=lambda x: (x["outcome_bucket"], x["brand_or_spec"], x["deal_id"]))
                for it in sorted_items:
                    b_val = it["outcome_bucket"]
                    s_flag = 1 if b_val == "1_SUCCESS" else 0
                    r_flag = 1 if b_val == "2_REVIEW" else 0
                    p_flag = 1 if b_val == "3_LOST_PRICE" else 0
                    o_flag = 1 if b_val == "4_LOST_OTHER" else 0
                    comm = f"[{it['pipeline_name'][:7]} | {it['outcome_label']}] {it['supplier_interaction_comment']}"
                    if axis_mode == "products":
                        vals = [
                            f"      • {it['raw_item_name']}", it["procurement_nature"], it["brand_or_spec"],
                            f"{it['supplier_pool_type']} ({it['supplier_profile']})",
                            1, 1, s_flag, r_flag, p_flag, o_flag, "-", "-", comm, f"#{it['deal_id']}"
                        ]
                    else:
                        brand_supp = it["brand_or_spec"] + (f" | {it['actual_supplier']}" if it["actual_supplier"] else "")
                        vals = [
                            f"      • {it['narrow_group']}: {it['raw_item_name']}", it["wide_group"],
                            it["procurement_nature"], brand_supp,
                            1, 1, s_flag, r_flag, p_flag, o_flag, "-", "-", comm, f"#{it['deal_id']}"
                        ]
                    ws.append(vals)
                    for c_idx in range(1, len(headers) + 1):
                        c = ws.cell(row=row_num, column=c_idx)
                        c.font = l2_font
                        c.border = border
                        if 5 <= c_idx <= 12:
                            c.alignment = Alignment(horizontal="center")
                    link_cell = ws.cell(row=row_num, column=14)
                    link_cell.hyperlink = it["b24_url"]
                    link_cell.font = link_font
                    ws.row_dimensions[row_num].outlineLevel = 2
                    ws.row_dimensions[row_num].hidden = True
                    row_num += 1

        widths = [46, 24, 24, 32, 10, 12, 12, 14, 12, 12, 13, 13, 48, 12]
        for idx, w in enumerate(widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = w
        ws.auto_filter.ref = f"A1:N{row_num - 1}"

    ws1 = wb.active
    write_hierarchy_sheet(ws1, "Группы_Товаров", "products")
    ws2 = wb.create_sheet()
    write_hierarchy_sheet(ws2, "Пулы_Поставщиков", "suppliers")

    # Sheet 3: Flat sortable register
    ws3 = wb.create_sheet("Реестр_Детально")
    ws3.freeze_panes = "A2"
    reg_headers = [
        "ID сделки", "Воронка", "Дата создания", "Итоговый статус", "Причина закрытия",
        "Широкая группа", "Узкая подгруппа", "Характер закупки", "Бренд / Изделие",
        "Наименование позиции", "Тип пула поставщика", "Профиль поставщика",
        "Факт. поставщик", "Взаимодействие с поставщиком / комментарий",
        "Заказчик", "Ответственный", "Снабжение КНР", "Макс. стадия", "Сборная", "Ссылка Б24"
    ]
    ws3.append(reg_headers)
    for c_idx in range(1, len(reg_headers) + 1):
        cell = ws3.cell(row=1, column=c_idx)
        cell.fill = hdr_fill
        cell.font = hdr_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border
    ws3.row_dimensions[1].height = 28

    for r_idx, it in enumerate(sorted(rows, key=lambda x: (x["date_create"] or "", x["deal_id"], x["item_index"]), reverse=True), 2):
        ws3.append([
            int(it["deal_id"]) if it["deal_id"].isdigit() else it["deal_id"],
            it["pipeline_name"],
            (it["date_create"] or "")[:10],
            it["outcome_label"],
            it["close_reason"],
            it["wide_group"],
            it["narrow_group"],
            it["procurement_nature"],
            it["brand_or_spec"],
            it["raw_item_name"],
            it["supplier_pool_type"],
            it["supplier_profile"],
            it["actual_supplier"],
            it["supplier_interaction_comment"],
            it["customer_name"],
            it["responsible_name"],
            it["supply_responsible_name"],
            it["reached_stage_max"],
            "Да" if it["is_multi_item"] else "Нет",
            it["b24_url"],
        ])
        lcell = ws3.cell(row=r_idx, column=20)
        lcell.hyperlink = it["b24_url"]
        lcell.font = link_font

    reg_widths = [11, 20, 12, 24, 28, 28, 28, 22, 22, 36, 28, 32, 24, 45, 24, 20, 20, 28, 10, 18]
    for idx, w in enumerate(reg_widths, 1):
        ws3.column_dimensions[openpyxl.utils.get_column_letter(idx)].width = w
    ws3.auto_filter.ref = f"A1:T{len(rows) + 1}"

    wb.save(out_path)
    print(f"[OK] Saved multi-level Excel report ({len(rows)} rows) to: {out_path}", flush=True)


def sync_dwh(rows, dry_run=False):
    print(f"=== Syncing {len(rows)} product rows to PostgreSQL DWH (Dry-Run: {dry_run}) ===", flush=True)
    by_wide = {}
    by_pool = {}
    for r in rows:
        by_wide[r["wide_group"]] = by_wide.get(r["wide_group"], 0) + 1
        by_pool[r["supplier_pool_type"]] = by_pool.get(r["supplier_pool_type"], 0) + 1
    print("Top wide_groups:", sorted(by_wide.items(), key=lambda x: -x[1])[:8])
    print("Supplier pools:", sorted(by_pool.items(), key=lambda x: -x[1]))

    if dry_run:
        print("[DRY-RUN] Sample 3 rows:")
        for r in rows[:3]:
            print(" ", r["deal_id"], "|", r["wide_group"], "->", r["narrow_group"], "|", r["procurement_nature"], "|", r["supplier_pool_type"])
        print("[DRY-RUN] PostgreSQL write skipped.")
        return

    import psycopg2
    from psycopg2.extras import execute_values

    if not PG_PASS:
        raise ValueError("PG_PASS environment variable is not set!")

    conn = psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME, user=PG_USER, password=PG_PASS)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics_deal_products (
            deal_id VARCHAR(50) NOT NULL,
            item_index INT NOT NULL DEFAULT 1,
            pipeline_name VARCHAR(100),
            title VARCHAR(500),
            tender_number VARCHAR(255),
            customer_name VARCHAR(255),
            date_create TIMESTAMP,
            date_close TIMESTAMP,
            current_stage_id VARCHAR(50),
            current_stage_name VARCHAR(120),
            reached_stage_max VARCHAR(120),
            outcome_bucket VARCHAR(50),
            outcome_label VARCHAR(120),
            close_reason VARCHAR(255),
            responsible_name VARCHAR(255),
            supply_responsible_name VARCHAR(255),
            deal_amount NUMERIC DEFAULT 0,
            is_multi_item BOOLEAN DEFAULT FALSE,
            raw_item_name TEXT,
            wide_group VARCHAR(150),
            narrow_group VARCHAR(180),
            procurement_nature VARCHAR(80),
            brand_or_spec VARCHAR(180),
            supplier_pool_type VARCHAR(150),
            supplier_profile VARCHAR(200),
            actual_supplier VARCHAR(255),
            supplier_interaction_comment TEXT,
            extraction_source VARCHAR(50),
            b24_url VARCHAR(500),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            PRIMARY KEY (deal_id, item_index)
        );
        CREATE INDEX IF NOT EXISTS idx_deal_prod_wide ON analytics_deal_products(wide_group);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_narrow ON analytics_deal_products(narrow_group);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_pool ON analytics_deal_products(supplier_pool_type);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_nature ON analytics_deal_products(procurement_nature);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_outcome ON analytics_deal_products(outcome_bucket);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_pipeline ON analytics_deal_products(pipeline_name);
        CREATE INDEX IF NOT EXISTS idx_deal_prod_date_create ON analytics_deal_products(date_create);
    """)

    deal_ids = list({r["deal_id"] for r in rows})
    cur.execute("DELETE FROM analytics_deal_products WHERE deal_id = ANY(%s);", (deal_ids,))

    tuples = [
        (
            r["deal_id"], r["item_index"], r["pipeline_name"], r["title"], r["tender_number"],
            r["customer_name"], r["date_create"], r["date_close"], r["current_stage_id"],
            r["current_stage_name"], r["reached_stage_max"], r["outcome_bucket"], r["outcome_label"],
            r["close_reason"], r["responsible_name"], r["supply_responsible_name"], r["deal_amount"],
            r["is_multi_item"], r["raw_item_name"], r["wide_group"], r["narrow_group"],
            r["procurement_nature"], r["brand_or_spec"], r["supplier_pool_type"], r["supplier_profile"],
            r["actual_supplier"], r["supplier_interaction_comment"], r["extraction_source"], r["b24_url"]
        )
        for r in rows
    ]
    execute_values(cur, """
        INSERT INTO analytics_deal_products (
            deal_id, item_index, pipeline_name, title, tender_number,
            customer_name, date_create, date_close, current_stage_id,
            current_stage_name, reached_stage_max, outcome_bucket, outcome_label,
            close_reason, responsible_name, supply_responsible_name, deal_amount,
            is_multi_item, raw_item_name, wide_group, narrow_group,
            procurement_nature, brand_or_spec, supplier_pool_type, supplier_profile,
            actual_supplier, supplier_interaction_comment, extraction_source, b24_url
        ) VALUES %s
    """, tuples, page_size=200)

    conn.commit()
    cur.close()
    conn.close()
    print(f"[SUCCESS] Upserted {len(tuples)} rows across {len(deal_ids)} deals into PostgreSQL DWH.")


def main():
    parser = argparse.ArgumentParser(description="Deal Products & Supplier Pools Analytics Pipeline")
    parser.add_argument("--since-date", default="2026-05-01", help="Start date YYYY-MM-DD (default: 2026-05-01)")
    parser.add_argument("--extract-dossier", action="store_true", help="Extract deals, stage history, tasks, files into JSON dossier")
    parser.add_argument("--skip-files", action="store_true", help="Skip downloading attached deal files during dossier extraction")
    parser.add_argument("--merge-batches", action="store_true", help="Merge classified_1..3.json into canonical mapping JSON")
    parser.add_argument("--export-excel", action="store_true", help="Export multi-level Excel report to docs/")
    parser.add_argument("--sync-dwh", action="store_true", help="Sync classified product rows into PostgreSQL DWH")
    parser.add_argument("--dry-run", action="store_true", help="Run without modifying DWH")
    args = parser.parse_args()

    dossier = None
    if args.extract_dossier:
        dossier = extract_dossier(args.since_date, skip_files=args.skip_files, dry_run=args.dry_run)
    elif os.path.exists(DOSSIER_PATH):
        with open(DOSSIER_PATH, "r", encoding="utf-8") as fp:
            dossier = json.load(fp)

    if args.merge_batches or args.export_excel or args.sync_dwh:
        if not dossier:
            dossier = extract_dossier(args.since_date, skip_files=args.skip_files, dry_run=args.dry_run)
        mapping = load_or_merge_mapping(merge_batches=args.merge_batches)
        rows = build_product_rows(dossier, mapping)
        if args.export_excel:
            export_excel(rows)
        if args.sync_dwh:
            sync_dwh(rows, dry_run=args.dry_run)
    elif not args.extract_dossier:
        extract_dossier(args.since_date, skip_files=args.skip_files, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
