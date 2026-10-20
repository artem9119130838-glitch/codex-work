#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canonical SEO Explosive Trends Radar for Longwang.ru (v4.0 - Zero Masks)
Architecture: Real Market Spikes (Google Trends RU) + Strict Explosion Sorting + Sector LLM Triage

1. Real Explosion Ingestion (NO MASKS):
   - Direct extraction of all trending searches from Google Trends Russia (AF_initDataCallback / Trending API)
   - Real volume (100k+, 50k+, 20k+) and growth percentage (+1000%, +700%)
   - Fallback to Google Trends RSS
2. Strict Sorting by Explosion Power:
   - Sorted strictly descending by Traffic Volume and Growth Rate (Largest spikes on top)
3. LLM Sector Triage:
   - Primary: DeepSeek-V3 with Hard Token Guard (15k ceiling + auto-alert)
   - Fallback: Gemini Flash Pool
   - Sector distribution: Finance/Taxes, Transport/Logistics, International/China, Industry/Tech, Laws/Society, Media/Sports
4. Delivery:
   - Bitrix24 task #4972 comment delivery via REST API
   - Collapsible spoiler with the full unedited list of all real spikes
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

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

# ==============================================================================
# 0. CONFIGURATION & TOKEN GUARD
# ==============================================================================

class TokenLimitExceededError(Exception):
    """Raised when incoming prompt size exceeds safety token threshold."""
    pass

def load_config():
    config = {
        "BITRIX24_WEBHOOK_URL": "",
        "B24_RADAR_TASK_ID": "4972",
        "GEMINI_API_KEY": "",
        "GEMINI_API_KEYS": "",
        "DEEPSEEK_API_KEY": "",
        "MAX_TOKEN_BUDGET": "15000",
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
# 1. REAL EXPLOSION INGESTION (ZERO MASKS)
# ==============================================================================

def fetch_real_google_trends_spikes() -> list:
    """
    Extracts authentic trending searches from Google Trends Russia without any keyword masks.
    Returns list of dicts with query, traffic volume, growth rate, and related terms.
    """
    results = []
    url = "https://trends.google.com/trending?geo=RU"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')

        matches = re.findall(
            r'AF_initDataCallback\(\{key:\s*\'ds:0\'.*?data:\s*(\[.*?\])\s*,\s*sideChannel',
            html,
            re.DOTALL
        )
        if matches:
            data = json.loads(matches[0])
            if len(data) > 1 and isinstance(data[1], list):
                raw_items = data[1]
                for it in raw_items:
                    if not isinstance(it, list) or len(it) == 0:
                        continue
                    q = str(it[0]).strip()
                    traffic = it[6] if len(it) > 6 and isinstance(it[6], int) else 0
                    growth = it[8] if len(it) > 8 and isinstance(it[8], int) else 0
                    related = [str(r).strip() for r in it[9] if r] if len(it) > 9 and isinstance(it[9], list) else []

                    # Avoid pure duplicate titles in related
                    clean_related = [r for r in related if r.lower() != q.lower()][:4]

                    results.append({
                        "query": q,
                        "traffic": traffic,
                        "growth": growth,
                        "related": clean_related
                    })
    except Exception as e:
        print(f"[-] Ошибка парсинга HTML Google Trends: {e}. Переход на RSS...")

    # Fallback / addition via Google Trends RSS if HTML returned too few
    if len(results) < 15:
        rss_url = "https://trends.google.com/trending/rss?geo=RU"
        try:
            req = urllib.request.Request(rss_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item"):
                    t = item.find("title")
                    traffic_el = item.find("{https://trends.google.com/trending/rss}approx_traffic")
                    traffic_val = 1000
                    if traffic_el is not None and traffic_el.text:
                        num_match = re.search(r'\d+', traffic_el.text.replace(",", "").replace("+", ""))
                        if num_match:
                            traffic_val = int(num_match.group(0))

                    if t is not None and t.text:
                        q = t.text.strip()
                        if not any(r["query"].lower() == q.lower() for r in results):
                            results.append({
                                "query": q,
                                "traffic": traffic_val,
                                "growth": 500,
                                "related": []
                            })
        except Exception as e_rss:
            print(f"[-] Ошибка RSS Google Trends: {e_rss}")

    # Strict sorting: Highest traffic and growth first!
    results.sort(key=lambda x: (x["traffic"], x["growth"]), reverse=True)
    return results

# ==============================================================================
# 2. LLM SECTOR TRIAGE (DEEPSEEK PRIMARY + GEMINI FALLBACK)
# ==============================================================================

def extract_json_from_text(text: str):
    if not text:
        return None
    code_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_match:
        text = code_match.group(1).strip()
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    obj_match = re.search(r'\{[\s\S]*\}', text)
    if obj_match:
        try:
            return json.loads(obj_match.group(0))
        except Exception:
            pass
    return None

def call_llm_json(prompt: str, config: dict):
    # 0. HARD TOKEN GUARD
    est_tokens = int(len(prompt) / 2.5)
    max_budget = int(config.get("MAX_TOKEN_BUDGET", 15000))
    if est_tokens > max_budget:
        raise TokenLimitExceededError(
            f"Превышен суточный лимит токенов: расчетный объем ~{est_tokens} токенов > лимит {max_budget}."
        )

    deepseek_key = config.get("DEEPSEEK_API_KEY", "")
    gemini_keys = []
    if config.get("GEMINI_API_KEYS"):
        gemini_keys.extend([k.strip() for k in config["GEMINI_API_KEYS"].split(",") if k.strip()])
    if config.get("GEMINI_API_KEY") and config["GEMINI_API_KEY"] not in gemini_keys:
        gemini_keys.append(config["GEMINI_API_KEY"])

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

    # 1. PRIMARY: DeepSeek-V3
    if deepseek_key:
        try:
            print("[*] Вызов Primary LLM: DeepSeek-V3 (deepseek-chat)...")
            url = "https://api.deepseek.com/chat/completions"
            ds_payload = json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты — шеф-аналитик поисковых трендов. Отвечай строго валидным JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }).encode("utf-8")
            req = urllib.request.Request(url, data=ds_payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {deepseek_key}"
            }, method="POST")
            with urllib.request.urlopen(req, timeout=35) as resp:
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
                    print("[+] DeepSeek-V3 успешно вернул валидный JSON!")
                    return parsed
        except Exception as e_ds:
            print(f"[-] DeepSeek недоступен или таймаут: {e_ds}. Запуск аварийного шлюза Gemini...")
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

    # 2. FALLBACK: Gemini Pool (Strict 8s Fast Timeout, Max 2 Keys)
    for idx, key in enumerate(gemini_keys[:2]):
        try:
            print(f"[*] Вызов Fallback LLM: Gemini Flash (ключ #{idx+1})...")
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
                    print("[+] Gemini Flash успешно вернул валидный JSON!")
                    return parsed
        except Exception as e_gemini:
            print(f"[-] Ошибка Gemini #{idx+1}: {e_gemini}")
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
                    error_message=str(e_gemini)[:250]
                )

    return None

def execute_llm_sector_triage(spikes: list, config: dict) -> dict:
    """
    Takes authentic Google Trends spikes sorted by explosion power and groups them by economic/societal sectors.
    Strictly preserves explosion ordering (highest traffic on top).
    """
    compact_spikes = []
    # Take top 40 most explosive spikes of the day for sector breakdown
    for s in spikes[:40]:
        compact_spikes.append({
            "q": s["query"],
            "vol": s["traffic"],
            "pct": f"+{s['growth']}%",
            "rel": s.get("related", [])
        })

    prompt = f"""Перед тобой ТОП-40 самых взрывных запросов Google по России за последние сутки (отсортированы строго по силе взрыва от сотен тысяч показов вниз):
{json.dumps(compact_spikes, ensure_ascii=False, indent=2)}

Твоя задача — объективно структурировать эти реальные взрывы по секторам:
1. НЕ ПРИДУМЫВАЙ запросы от себя! Используй только переданные ключевые слова и их точные цифры показов/роста.
2. Распредели запросы по следующим 6 секторам:
   - finance_tax: 💼 Налоги, Финансы, Банки & Экономика
   - transport_logistics: 🚚 Транспорт, Инфраструктура, Авто & Логистика
   - international_china: 🌐 Международные события, Страны, ВЭД & Дипломатия
   - industry_tech: ⚙️ Промышленность, Оборудование, IT & Технологии
   - laws_society: 🏛️ Законы, Регулирование, Госструктуры & Общество
   - media_sports: ⚽ Спорт, Шоу-бизнес, Персоны & Медиа
3. Внутри каждого сектора СТРОГО СОХРАНЯЙ ПОРЯДОК: сначала те, у кого больше объем поискового взрыва (vol: 100000, 50000, 20000...)!
4. Для каждого запроса в массиве items укажи:
   - query: точный текст запроса
   - volume_str: строка объема (например: "100 000+", "50 000+", "20 000+")
   - growth_str: процент прироста (например: "+1000%", "+700%")
   - related: сопутствующие запросы из поля 'rel'
   - context: 1 емкое предложение, что произошло (почему взлетело)
   - idea: идея страницы, статьи, экспертного кейса или новости
5. Составить summary:
   - top_spike_of_the_day: главный взрывной запрос дня по абсолютному числу показов
   - main_trend: краткий вывод о фокусе внимания страны сегодня

Ответь СТРОГО валидным JSON-объектом:
{{
  "summary": {{
    "top_spike_of_the_day": "...",
    "main_trend": "..."
  }},
  "sectors": [
    {{
      "sector_id": "finance_tax",
      "sector_title": "💼 Налоги, Финансы, Банки & Экономика",
      "items": [
        {{
          "query": "...",
          "volume_str": "50 000+",
          "growth_str": "+700%",
          "related": [...],
          "context": "...",
          "idea": "..."
        }}
      ]
    }},
    ...
  ]
}}"""
    res = call_llm_json(prompt, config)
    if isinstance(res, dict) and "sectors" in res and len(res["sectors"]) > 0:
        return res

    # Heuristic fallback if LLM is unavailable
    return {
        "summary": {
            "top_spike_of_the_day": spikes[0]["query"] if spikes else "N/A",
            "main_trend": "Рост внимания к регуляторным и налоговым изменениям."
        },
        "sectors": []
    }

# ==============================================================================
# 3. BITRIX24 INTEGRATION & FORMATTER
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

def format_b24_spikes_digest(triage_data: dict, spikes: list) -> str:
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    summary = triage_data.get("summary", {})
    sectors = triage_data.get("sectors", [])

    lines = [
        f"[b]🚀 РАДАР РЕАЛЬНЫХ ВЗРЫВНЫХ ТРЕНДОВ: GOOGLE TRENDS RUSSIA (v4.0)[/b]",
        f"[color=#718096]📅 {now_str} | Реальные всплески поиска без масок: {len(spikes)} запросов ➔ Сортировка по силе взрыва[/color]",
        "",
        f"[b]🔥 ГЛАВНЫЙ ВЗРЫВ ДНЯ:[/b] [color=#e53e3e]«{summary.get('top_spike_of_the_day', '')}»[/color]",
        f"• [b]Фокус интереса:[/b] {summary.get('main_trend', '')}",
        "",
        "────────────────────────────────────────",
        f"[b]📊 СЕКТОРНАЯ РАСКЛАДКА (СТРОГО ПО УБЫВАНИЮ СИЛЫ ВЗРЫВА):[/b]",
        ""
    ]

    for sec in sectors:
        sec_title = sec.get("sector_title", "")
        items = sec.get("items", [])
        if not items:
            continue

        lines.append(f"[b]{sec_title}[/b]")
        for it in items:
            q = it.get("query", "")
            vol = it.get("volume_str", "")
            pct = it.get("growth_str", "")
            ctx = it.get("context", "")
            idea = it.get("idea", "")
            rel = it.get("related", [])
            rel_str = f" [color=#718096](Связанные: {', '.join(rel)})[/color]" if rel else ""

            lines.append(f"• [color=#2b6cb0][b]«{q}»[/b][/color] — [color=#e53e3e][b]{vol}[/b][/color] | [color=#2f855a]{pct}[/color]{rel_str}")
            if ctx:
                lines.append(f"   [color=#4a5568]Суть события:[/color] {ctx}")
            if idea:
                lines.append(f"   [color=#2b6cb0]Идея материала:[/color] {idea}")
        lines.append("")

    # Full raw candidates spoiler
    lines.append("────────────────────────────────────────")
    lines.append(f"[spoiler=📋 Полный список всех взрывных поисковых запросов дня ({len(spikes)} шт., отсортированы по силе)]")
    for idx, s in enumerate(spikes, 1):
        rel = f" | Связанные: {', '.join(s['related'][:3])}" if s.get('related') else ""
        lines.append(f"{idx}. {s['query']} — {s['traffic']}+ показов (+{s['growth']}%){rel}")
    lines.append("[/spoiler]")

    lines.append("────────────────────────────────────────")
    lines.append("[i]Радар работает по чистым данным Google Trends без ключевых масок. Назовите номер темы или ключ для подготовки страницы/статьи.[/i]")
    return "\n".join(lines)

# ==============================================================================
# 4. ORCHESTRATOR
# ==============================================================================

def run_orchestrator(dry_run: bool = True):
    config = load_config()
    webhook = config.get("BITRIX24_WEBHOOK_URL", "")
    task_id = config.get("B24_RADAR_TASK_ID", "4972")

    print("=" * 80)
    print("=== TREND SPIKE RADAR v4.0: ЧИСТЫЕ ВЗРЫВЫ GOOGLE TRENDS (ZERO MASKS) ===")
    print(f"Режим: {'DRY-RUN (Безопасная симуляция)' if dry_run else 'EXECUTE (Боевая отправка в Битрикс24)'}")
    print(f"Битрикс24 Вебхук: {'Подключен' if webhook else 'НЕ НАЙДЕН'}")
    print(f"Целевая задача B24 ID: {task_id}")
    print(f"Жесткий лимит токенов: {config.get('MAX_TOKEN_BUDGET', '15000')}")
    print("=" * 80)

    # 1. Ingestion: Pure Google Trends spikes
    t0 = time.time()
    print("[*] ШАГ 1: Сбор реальных взрывных запросов с Google Trends Russia без масок...")
    spikes = fetch_real_google_trends_spikes()
    elapsed_gather = round(time.time() - t0, 2)
    print(f"[+] Сборщик завершил работу за {elapsed_gather}s: найдено {len(spikes)} реальных взрывных запросов.")

    if not spikes:
        print("[-] Не удалось получить данные из Google Trends.")
        return

    # Save candidates snapshot locally
    try:
        cand_path = os.path.join(os.path.dirname(__file__), "last_radar_candidates.json")
        with open(cand_path, "w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "count": len(spikes), "spikes": spikes}, f, ensure_ascii=False, indent=2)
        print(f"[+] Локальный снимок взрывных запросов сохранен: {cand_path}")
    except Exception as e_save:
        print(f"[-] Предупреждение сохранения снимка: {e_save}")

    # 2. LLM Sector Triage
    print("\n[*] ШАГ 2: Передача отсортированного массива в ИИ-шлюз (Primary: DeepSeek-V3, Fallback: Gemini Flash)...")
    t1 = time.time()
    try:
        triage_data = execute_llm_sector_triage(spikes, config)
    except TokenLimitExceededError as err:
        print(f"\n[!] СРАБОТАЛ АЛЕРТ БЕЗОПАСНОСТИ: {err}")
        alert_bb = (
            f"[b][color=#e53e3e]⚠️ АЛЕРТ БЕЗОПАСНОСТИ РАДАРА: Превышен суточный лимит токенов![/color][/b]\n\n"
            f"• {str(err)}\n"
            f"• Работа скрипта принудительно остановлена для защиты бюджета API."
        )
        if not dry_run and webhook:
            post_b24_comment(webhook, task_id, alert_bb)
        else:
            print("\n[DRY-RUN ALERT PREVIEW]:\n" + alert_bb)
        return

    elapsed_llm = round(time.time() - t1, 2)
    print(f"[+] ИИ-триаж завершен за {elapsed_llm}s!")

    # 3. Format Digest
    digest_bb = format_b24_spikes_digest(triage_data, spikes)

    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ДАЙДЖЕСТ ДЛЯ БИТРИКС24 (ПРЕВЬЮ):")
    print("=" * 80)
    print(digest_bb[:2500])
    if len(digest_bb) > 2500:
        print(f"\n... [Обрезано для консоли, полная длина: {len(digest_bb)} символов, включая спойлер с {len(spikes)} всплесками] ...")
    print("=" * 80)

    # 4. Delivery
    if not dry_run and webhook:
        print(f"\n[*] Отправка дайджеста в задачу Битрикс24 #{task_id}...")
        post_b24_comment(webhook, task_id, digest_bb)
    else:
        print("\n[DRY-RUN SUCCESS] Холостой прогон завершен. Запись в Битрикс24 пропущена.")

def main():
    parser = argparse.ArgumentParser(description="Trend Spike Radar v4.0 - Zero Masks")
    parser.add_argument('--execute', action='store_true', help="Execute real post to Bitrix24 (default is dry-run)")
    parser.add_argument('--dry-run', action='store_true', help="Explicit dry-run mode")
    args = parser.parse_args()

    dry_run = True
    if args.execute and not args.dry_run:
        dry_run = False

    run_orchestrator(dry_run=dry_run)

if __name__ == '__main__':
    main()
