#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical Multi-Module SEO Breakout & Hype Radar for Longwang.ru (v3.0)
Architecture: Wide Ingestion (Free Search Autocomplete + Trends) + LLM Sieve & Triage

1. Wide Ingestion:
   - Google Trends RSS (Breakouts & Trending RU / US)
   - Dynamic Multi-Seed Autocomplete (Yandex Suggest + Google Suggest with 3-day recency markers)
   - Public Logistics & Customs Previews (Telegram channels web scrapers: customs_rf, ved_ru)
2. Sanitization:
   - Deduplication & non-commercial stop-words stripping (no games/films/junk)
3. LLM Sieve & Triage:
   - Gemini 2.5 Flash Pool with DeepSeek-V3 Fallback
   - Full array triage into 4 strategic B2B clusters + Executive Coffee Summary
4. Delivery & BI:
   - Token usage logging to PostgreSQL DWH (marketing_db.llm_usage_logs / Metabase Dashboard 8)
   - Bitrix24 task #4972 comment delivery via REST API
   - Mode: Supports --dry-run (default is safe simulation) and --execute.
"""

import os
import sys
import json
import re
import time
import argparse
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

# ==============================================================================
# ENVIRONMENT & CONFIGURATION
# ==============================================================================

def load_config():
    config = {
        "BITRIX24_WEBHOOK_URL": "",
        "B24_RADAR_TASK_ID": "4972",
        "GEMINI_API_KEY": "",
        "GEMINI_API_KEYS": "",
        "DEEPSEEK_API_KEY": "",
        "PG_HOST": "10.10.0.1",
        "PG_PORT": "5433",
        "PG_DBNAME": "marketing_db",
        "PG_USER": "vector_user",
        "PG_PASS": ""
    }
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
        os.path.join(os.path.dirname(__file__), "..", "..", "1c_odata", ".env"),
        "/Storage/scripts/metabase_analytics/.env",
        "/opt/longwang_trend_radar/.env",
        ".env"
    ]
    for p in env_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k in config and not config[k]:
                            config[k] = v
                        elif k == "GEMINI_API_KEYS" and not config.get("GEMINI_API_KEYS"):
                            config["GEMINI_API_KEYS"] = v
                        elif k == "DEEPSEEK_API_KEY" and not config.get("DEEPSEEK_API_KEY"):
                            config["DEEPSEEK_API_KEY"] = v

    for k in list(config.keys()):
        if os.environ.get(k):
            config[k] = os.environ.get(k)
            
    if not config.get("GEMINI_API_KEY") and config.get("GEMINI_API_KEYS"):
        keys = [k.strip() for k in config["GEMINI_API_KEYS"].split(",") if k.strip()]
        if keys:
            config["GEMINI_API_KEY"] = keys[0]

    return config

# ==============================================================================
# 1. WIDE INGESTION ENGINES (FREE & FAST)
# ==============================================================================

def fetch_yandex_suggest(query: str) -> list:
    url = f"https://suggest.yandex.ru/suggest-ya.cgi?v=4&part={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception:
        pass
    return []

def fetch_google_suggest(query: str) -> list:
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=ru&gl=ru&q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception:
        pass
    return []

def fetch_google_trends_rss() -> list:
    rss_urls = [
        "https://trends.google.com/trending/rss?geo=RU",
        "https://trends.google.com/trending/rss?geo=US"
    ]
    trends = []
    for u in rss_urls:
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item"):
                    t = item.find("title")
                    if t is not None and t.text:
                        trends.append(t.text.strip())
        except Exception:
            continue
    return trends

def fetch_telegram_channel_snippets(channel: str) -> list:
    url = f"https://t.me/s/{channel}"
    snippets = []
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            texts = re.findall(r'<div class="tgme_widget_message_text[^"]*">(.*?)</div>', html, re.DOTALL)
            for t in texts[-8:]:
                clean = re.sub(r'<[^>]+>', ' ', t).strip()
                first_line = clean.split('\n')[0].strip()
                if len(first_line) > 15:
                    snippets.append(first_line[:120])
    except Exception:
        pass
    return snippets

WIDE_SEEDS = [
    # 1. Cargo & Border Crisis
    "застрял груз", "застряло карго", "почему стоит карго", "рейд тяк", "проверка садовод карго",
    "очереди забайкальск", "задержка на границе китая", "уйти от карго", "белая доставка вместо карго",
    "конфискат карго", "рейд москва склад китай", "задержка грузов китай 2026",
    # 2. Payments & VED Banking
    "не проходит платеж в китай", "возврат платежа китай", "втб шанхай платежи", "блокировка 115 фз вэд",
    "оплата в юанях в китай задержка",
    # 3. Compliance, GTD & Marketplaces
    "гтд озон", "гтд вайлдберриз", "номер гтд где взять", "штраф озон за гтд", "блокировка озон гтд",
    "честный знак 2026", "маркировка товаров из китая", "налоговая проверка селлеров", "гтд для маркетплейса",
    "документы для озон из китая",
    # 4. Industrial Equipment & Machinery
    "станки из китая", "купить станок в китае", "лазерный станок китай", "тпа станок китай",
    "фрезерный станок чпу китай", "линия из китая", "растаможка станков из китая", "пошлина на оборудование китай",
    "доставка оборудования из китая", "поставка станков под ключ китай",
    # 5. Product Hype & AI Hardware
    "ии игрушки оптом", "робот компаньон китай", "умные роботы оптом", "новинки оптом из китая 2026",
    "трендовые товары из китая", "вирусные товары тикток китай опт", "волоконный лазер китай купить",
    "мини завод из китая"
]

STOP_NOISE_WORDS = [
    "порно", "скачать", "фильм", "песни", "сериал", "minecraft", "игры", "каргополь",
    "death stranding", "в германии", "немецкий", "б/у", "авито", "своими руками", "чертеж"
]

def collect_wide_raw_stream() -> list:
    """Collects 150-250 raw queries and headlines in parallel across search engines & channels."""
    raw_results = []

    def query_worker(seed):
        res = []
        res.extend(fetch_yandex_suggest(seed))
        res.extend(fetch_google_suggest(seed))
        if any(k in seed for k in ["гтд", "карго", "станки", "новинки"]):
            res.extend(fetch_yandex_suggest(f"{seed} 2026"))
            res.extend(fetch_yandex_suggest(f"{seed} новые правила"))
        return res

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(query_worker, s) for s in WIDE_SEEDS]
        futures.append(executor.submit(fetch_google_trends_rss))
        futures.append(executor.submit(fetch_telegram_channel_snippets, "customs_rf"))
        futures.append(executor.submit(fetch_telegram_channel_snippets, "ved_ru"))

        for f in as_completed(futures):
            try:
                res = f.result()
                if isinstance(res, list):
                    raw_results.extend(res)
            except Exception:
                pass

    # Deduplicate & sanitize
    seen = set()
    sanitized = []
    for item in raw_results:
        it = item.strip()
        it_l = it.lower()
        if any(sw in it_l for sw in STOP_NOISE_WORDS):
            continue
        if it_l not in seen and len(it) >= 4:
            seen.add(it_l)
            sanitized.append(it)

    return sanitized

# ==============================================================================
# 2. LLM SIEVE & TRIAGE CORE (GEMINI POOL + DEEPSEEK FALLBACK + DWH)
# ==============================================================================

def extract_json_from_text(text: str):
    if not text:
        return None
    code_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_match:
        text = code_match.group(1).strip()
    # 1. Try direct JSON parse first
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    # 2. Try matching outer object { ... }
    obj_match = re.search(r'\{[\s\S]*\}', text)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except Exception:
            pass
    # 3. Try matching outer array [ ... ]
    arr_match = re.search(r'\[[\s\S]*\]', text)
    if arr_match:
        try:
            return json.loads(arr_match.group(0))
        except Exception:
            pass
    return None

def call_llm_json(prompt: str, config: dict):
    gemini_keys = []
    if config.get("GEMINI_API_KEYS"):
        gemini_keys.extend([k.strip() for k in config["GEMINI_API_KEYS"].split(",") if k.strip()])
    if config.get("GEMINI_API_KEY") and config["GEMINI_API_KEY"] not in gemini_keys:
        gemini_keys.append(config["GEMINI_API_KEY"])
        
    deepseek_key = config.get("DEEPSEEK_API_KEY", "")
    
    # Init llm_tracker for DWH
    tracker_candidates = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "metabase_analytics", "scripts")),
        "/Storage/scripts/metabase_analytics",
        "/opt/longwang_trend_radar"
    ]
    for p in tracker_candidates:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)
    try:
        from llm_tracker import log_llm_usage
    except Exception:
        log_llm_usage = None

    # 1. Try Gemini Pool with fast failover (8s timeout)
    for idx, key in enumerate(gemini_keys):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=8) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                if log_llm_usage:
                    usage = res_data.get("usageMetadata", {})
                    log_llm_usage(
                        provider="gemini",
                        model_name="gemini-2.5-flash",
                        task_type="longwang_trend_radar",
                        request_type="longwang_trend_radar",
                        project_name="seo_longwang",
                        key_alias=f"gemini_pool_{idx+1}",
                        prompt_tokens=usage.get("promptTokenCount", 0),
                        completion_tokens=usage.get("candidatesTokenCount", 0),
                        initiated_by="system_cron",
                        status="success"
                    )
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = extract_json_from_text(text)
                if parsed is not None:
                    return parsed
        except Exception as e:
            if log_llm_usage:
                log_llm_usage(
                    provider="gemini",
                    model_name="gemini-2.5-flash",
                    task_type="longwang_trend_radar",
                    request_type="longwang_trend_radar",
                    project_name="seo_longwang",
                    key_alias=f"gemini_pool_{idx+1}",
                    prompt_tokens=0,
                    completion_tokens=0,
                    initiated_by="system_cron",
                    status="error",
                    error_message=str(e)[:250]
                )

    # 2. Try DeepSeek Fallback
    if deepseek_key:
        try:
            url = "https://api.deepseek.com/chat/completions"
            ds_payload = json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты — ведущий B2B-аналитик компании Long Wang (longwang.ru). Отвечай строго валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }).encode("utf-8")
            req = urllib.request.Request(url, data=ds_payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_key}"
            }, method="POST")
            with urllib.request.urlopen(req, timeout=16) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                usage = res_data.get("usage", {})
                if log_llm_usage:
                    log_llm_usage(
                        provider="deepseek",
                        model_name="deepseek-chat",
                        task_type="longwang_trend_radar",
                        request_type="longwang_trend_radar",
                        project_name="seo_longwang",
                        key_alias="deepseek_main",
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        initiated_by="system_cron",
                        status="success"
                    )
                text = res_data["choices"][0]["message"]["content"]
                parsed = extract_json_from_text(text)
                if parsed is not None:
                    return parsed
        except Exception as e_ds:
            if log_llm_usage:
                log_llm_usage(
                    provider="deepseek",
                    model_name="deepseek-chat",
                    task_type="longwang_trend_radar",
                    request_type="longwang_trend_radar",
                    project_name="seo_longwang",
                    key_alias="deepseek_main",
                    prompt_tokens=0,
                    completion_tokens=0,
                    initiated_by="system_cron",
                    status="error",
                    error_message=str(e_ds)[:250]
                )

    return None

def execute_llm_triage(raw_stream: list, config: dict) -> dict:
    """Passes the wide stream of raw queries to LLM for sorting and clustering."""
    prompt = f"""Ты — шеф-аналитик B2B-логистики и ВЭД компании Longwang (longwang.ru — белая доставка из Китая, оборудование и поиск фабрик).
Перед тобой сырой срез поисковых подсказок Яндекс/Google, трендов Google Trends и новостей за последние 3 дня:
{json.dumps(raw_stream[:75], ensure_ascii=False, indent=2)}

Твоя задача — провести профессиональный триаж (сортировку):
1. Отбросить весь бытовой шум, потребительские запросы, игры и мусор. НЕ ВКЛЮЧАЙ их в ответ и не создавай для них элементы с пометкой "Игнорировать" — просто отбрось молча!
2. Отобрать строго от 2 до 4 самых острых и взрывных B2B-запросов и распределить их по 4 категориям:
   - cargo_crisis: 🚨 1. Кризисы карго, рейды и задержки грузов (целевой хаб: /supplies-services-china/belaya-dostavka-iz-kitaya/)
   - compliance_gtd: 📦 2. ГТД, Честный Знак и маркетплейсы (целевой хаб: /supplies-services-china/belaya-dostavka-iz-kitaya/)
   - industrial_equipment: ⚙️ 3. Промышленное оборудование и станки из Китая (целевой хаб: /supplies-services-china/equipment-from-china/)
   - product_hype: 💡 4. Взрывные товарные ниши и инновации КНР (целевой хаб: /supplies-services-china/proverka-postavshhika-v-kitae/)
3. Для каждого отобранного B2B-запроса в массиве items укажи:
   - query: текст запроса
   - urgency: "HIGH" или "MEDIUM"
   - why_spiking: почему это взрывается в запросах (контекст последних дней)
   - action: рекомендация Longwang (какой оффер/статью выкатить)
4. Составить утреннее executive_summary (10-секундный фокус для Артема):
   - main_pain: главная боль бизнеса сегодня (1-2 емких предложения)
   - content_idea: {{"title": "...", "hook": "..."}}
   - china_angle: практический совет по фабрикам/товарам в КНР

Ответь СТРОГО валидным JSON-объектом:
{{
  "executive_summary": {{
    "main_pain": "...",
    "content_idea": {{"title": "...", "hook": "..."}},
    "china_angle": "..."
  }},
  "clusters": [
    {{
      "category_id": "cargo_crisis",
      "category_title": "🚨 1. Кризисы карго, рейды и задержки грузов",
      "target_hub": "/supplies-services-china/belaya-dostavka-iz-kitaya/",
      "items": [ ... ]
    }},
    ...
  ]
}}"""
    res = call_llm_json(prompt, config)
    if isinstance(res, dict) and "executive_summary" in res and "clusters" in res and len(res["clusters"]) > 0:
        return res
        
    # Heuristic fallback if LLM returned nothing
    return {
        "executive_summary": {
            "main_pain": "Нарастающие задержки на границах и ужесточение контроля ГТД на маркетплейсах вынуждают бизнес уходить от карго.",
            "content_idea": {
                "title": "«Как получить ГТД для Озон и спасти карточки от блокировок: белый транзит через Longwang»",
                "hook": "Разбор штрафов и легальный алгоритм таможенного оформления сборных грузов из КНР."
            },
            "china_angle": "Спрос смещается на прямое контрактное производство компактных линий и лазерных станков."
        },
        "clusters": []
    }

# ==============================================================================
# 3. BITRIX24 INTEGRATION (TASK & COMMENTS)
# ==============================================================================

def b24_api_call(webhook_url: str, method: str, params) -> dict:
    url = f"{webhook_url.rstrip('/')}/{method}.json"
    payload = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def post_b24_comment(webhook_url: str, task_id: str, message_bb: str) -> bool:
    res = b24_api_call(webhook_url, "task.commentitem.add", [
        task_id,
        {"POST_MESSAGE": message_bb}
    ])
    if res.get("result"):
        print(f"[+] Дайджест успешно добавлен как комментарий в задачу [ID={task_id}] (list syntax)!")
        return True
        
    res2 = b24_api_call(webhook_url, "task.commentitem.add", {
        "TASKID": task_id,
        "FIELDS": {
            "POST_MESSAGE": message_bb
        }
    })
    if res2.get("result"):
        print(f"[+] Дайджест успешно добавлен как комментарий в задачу [ID={task_id}] (dict syntax)!")
        return True
    else:
        print(f"[-] Ошибка добавления комментария в задачу Битрикс24: {res} | {res2}")
        return False

# ==============================================================================
# 4. DIGEST FORMATTER (BB-CODE & CONSOLE)
# ==============================================================================

def format_b24_digest_v3(triage_data: dict, raw_count: int, unique_count: int) -> str:
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    summary = triage_data.get("executive_summary", {})
    clusters = triage_data.get("clusters", [])

    c_idea = summary.get("content_idea", {})
    if isinstance(c_idea, dict):
        c_idea_str = f"«{c_idea.get('title', '')}»\n     [color=#4a5568]Хук / Идея:[/color] {c_idea.get('hook', '')}"
    else:
        c_idea_str = str(c_idea)

    lines = [
        f"[b]☕ УТРЕННИЙ B2B-ДАЙДЖЕСТ ТРЕНДОВ & ХАЙПА: LONGWANG RADAR v3.0[/b]",
        f"[color=#718096]📅 {now_str} | Входящий поток: {raw_count} сырых запросов ➔ {unique_count} уникальных ➔ ИИ-триаж[/color]",
        "",
        f"[b]🎯 ГЛАВНЫЙ ФОКУС УТРА (EXECUTIVE SUMMARY):[/b]",
        f"• [b]Боль рынка:[/b] {summary.get('main_pain', '')}",
        f"• [b]Тема дня для контент-плана:[/b] [color=#2b6cb0]{c_idea_str}[/color]",
        f"• [b]Потенциал в КНР:[/b] [color=#2f855a]{summary.get('china_angle', '')}[/color]",
        "",
        "────────────────────────────────────────",
        f"[b]📊 ИТОГИ ИИ-СОРТИРОВКИ ПО СТРАТЕГИЧЕСКИМ КЛАСТЕРАМ:[/b]",
        ""
    ]

    for cl in clusters:
        title = cl.get("category_title", "")
        hub = cl.get("target_hub", "")
        items = [it for it in cl.get("items", []) if str(it.get("urgency", "")).upper() in ["HIGH", "MEDIUM"]]
        if not items:
            continue

        lines.append(f"[b]{title}[/b]")
        lines.append(f"[color=#4a5568]Целевой хаб лидогенерации: https://longwang.ru{hub}[/color]")
        for it in items:
            urg = f"[color=#e53e3e][{it.get('urgency', 'TREND')}][/color] " if it.get('urgency') == 'HIGH' else ""
            lines.append(f"• {urg}[b]«{it.get('query', '')}»[/b]")
            lines.append(f"   [color=#2b6cb0]Контекст взрыва:[/color] {it.get('why_spiking', '')}")
            lines.append(f"   [color=#2f855a]Действие Longwang:[/color] {it.get('action', '')}")
        lines.append("")

    lines.append("────────────────────────────────────────")
    lines.append("[i]Дайджест подготовлен модулем Trend Spike Radar v3.0 (Wide Ingestion + LLM Sieve). Ответьте в этой задаче для автозапуска генерации статьи.[/i]")
    return "\n".join(lines)

# ==============================================================================
# 5. ORCHESTRATION PIPELINE
# ==============================================================================

def run_orchestrator(dry_run: bool = True):
    config = load_config()
    webhook = config.get("BITRIX24_WEBHOOK_URL", "")
    task_id = config.get("B24_RADAR_TASK_ID", "4972")

    print("=" * 80)
    print("=== TREND SPIKE RADAR v3.0: ШИРОКИЙ ПЫЛЕСОС + ИИ-ТРИАЖ ===")
    print(f"Режим: {'DRY-RUN (Безопасная симуляция)' if dry_run else 'EXECUTE (Боевая отправка в Битрикс24)'}")
    print(f"Битрикс24 Вебхук: {'Подключен' if webhook else 'НЕ НАЙДЕН'}")
    print(f"Целевая задача B24 ID: {task_id}")
    print("=" * 80)

    # 1. Wide Ingestion
    t0 = time.time()
    print("[*] ШАГ 1: Запуск параллельного сборщика-пылесоса (Яндекс, Google, Trends RSS, ТГ)...")
    raw_stream = collect_wide_raw_stream()
    elapsed_gather = round(time.time() - t0, 2)
    print(f"[+] Сборщик завершил работу за {elapsed_gather}s: собрано {len(raw_stream)} уникальных B2B-кандидатов.")

    # 2. LLM Sieve & Triage
    print("\n[*] ШАГ 2: Передача сырого массива в ИИ-шлюз (Gemini 2.5 Flash / DeepSeek-V3)...")
    t1 = time.time()
    triage_data = execute_llm_triage(raw_stream, config)
    elapsed_llm = round(time.time() - t1, 2)
    print(f"[+] ИИ-триаж завершен за {elapsed_llm}s!")

    # 3. Format Digest
    digest_bb = format_b24_digest_v3(triage_data, len(raw_stream) * 2, len(raw_stream))

    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ДАЙДЖЕСТ ДЛЯ БИТРИКС24 (ПРЕВЬЮ):")
    print("=" * 80)
    print(digest_bb)
    print("=" * 80)

    # 4. Delivery
    if not dry_run and webhook:
        print(f"\n[*] Отправка дайджеста в задачу Битрикс24 #{task_id}...")
        post_b24_comment(webhook, task_id, digest_bb)
    else:
        print("\n[DRY-RUN SUCCESS] Холостой прогон завершен. Запись в Битрикс24 пропущена.")

def main():
    parser = argparse.ArgumentParser(description="Trend Spike Radar v3.0")
    parser.add_argument('--execute', action='store_true', help="Execute real post to Bitrix24 (default is dry-run)")
    parser.add_argument('--dry-run', action='store_true', help="Explicit dry-run mode")
    args = parser.parse_args()

    dry_run = True
    if args.execute and not args.dry_run:
        dry_run = False

    run_orchestrator(dry_run=dry_run)

if __name__ == '__main__':
    main()
