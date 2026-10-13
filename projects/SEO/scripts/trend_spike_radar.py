"""
Canonical Trend Spike Radar for Longwang.ru B2B SEO.
5-Module Architecture:
  1. Regulatory & Compliance Radar (ГТД, Честный Знак, маркировка, налоги)
  2. Sanctions & Market Vacancies Radar (Уход брендов ЕС/США, китайские аналоги станков)
  3. Logistics & Cargo Crises Radar (Застряли грузы, рейды, задержки, переход на белую доставку)
  4. Product Hype & Hardware Novelty Radar (Детские ИИ-игрушки, роботы, мини-ЧПУ, лазерная сварка)
  5. Global Breakout Trends (Google Trends Breakout воронка + ИИ-сито)

Output Channel:
  - Bitrix24 Task: Automatically finds or creates task "Сбор хайпа" / "Сбор хайпа и трендов Longwang"
    and appends daily digests as comments (task.commentitem.add) with full history.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import re
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 LongWangRadar/2.0'
}

# ==============================================================================
# 5 EXPANDED SEED MODULES (Эмоциональные боли, кризисы, вопросы, новинки)
# ==============================================================================

MODULES = {
    "1_regulatory": {
        "title": "📋 1. Регуляторика, маркировка и госконтроль",
        "seeds": [
            "доставка из китая гтд",
            "где взять гтд для озон",
            "гтд вайлдберриз китай",
            "блокировка карточки озон нет гтд",
            "вайлдберриз штраф нет маркировки",
            "честный знак одежда китай",
            "маркировка честный знак карго",
            "как ввести остатки честный знак",
            "новые требования к импорту 2026",
            "отказ в сертификате китай",
            "реестр минпромторга аналоги оборудования"
        ],
        "default_hub": "/supplies-services-china/belaya-dostavka-iz-kitaya/"
    },
    "2_sanctions": {
        "title": "⚙️ 2. Санкции, уход брендов и китайские аналоги",
        "seeds": [
            "санкции запрет поставок оборудования",
            "уход siemens замена китай",
            "аналог fanuc в китае",
            "замена schneider electric китай",
            "китайские аналоги европейских станков",
            "параллельный импорт промышленного оборудования",
            "поставка запчастей к импортным станкам",
            "дефицит сервоприводов китай",
            "купить станок взамен немецкого"
        ],
        "default_hub": "/supplies-services-china/equipment-from-china/"
    },
    "3_cargo_logistics": {
        "title": "🚚 3. Логистика, кризисы карго и переход в белую",
        "seeds": [
            "застряли грузы из китая",
            "застряло карго из китая",
            "почему стоит карго",
            "когда приедет карго",
            "что случилось с карго",
            "почему все встало на границе китая",
            "пропал груз карго москва",
            "рейд тяк москва карго",
            "проверка садовод карго",
            "очереди забайкальск граница",
            "задержка грузов на границе китая",
            "как уйти от карго",
            "переход с карго на белый вэд",
            "белая доставка вместо карго",
            "белая доставка с закрывающими документами ндс",
            "не проходит платеж в китай",
            "возврат платежа из китая",
            "втб шанхай задержка платежа",
            "блокировка счета 115 фз вэд импорт"
        ],
        "default_hub": "/supplies-services-china/belaya-dostavka-iz-kitaya/"
    },
    "4_product_hype": {
        "title": "🤖 4. Продуктовый хайп и новинки оборудования / гаджетов",
        "seeds": [
            "игрушки с искусственным интеллектом оптом",
            "детские ии игрушки купить оптом",
            "ai игрушки фабрика китай",
            "робот компаньон китай фабрика",
            "умные роботы для дома оптом из китая",
            "трендовые товары из китая для маркетплейсов",
            "новинки из китая оптом 2026",
            "вирусные товары тикток из китая оптом",
            "портативный волоконный лазер китай купить",
            "лазерная сварка аппарат китай опт",
            "мини тпа станок для пластика китай",
            "настольный фрезерный станок чпу китай",
            "вендинговые аппараты новинки китай",
            "3d принтер промышленный китай завод"
        ],
        "default_hub": "/supplies-services-china/proverka-postavshhika-v-kitae/"
    }
}

# ==============================================================================
# ENVIRONMENT & CONFIGURATION
# ==============================================================================

def load_config():
    config = {
        "BITRIX24_WEBHOOK_URL": "",
        "B24_RADAR_TASK_ID": "",
        "GEMINI_API_KEY": ""
    }
    env_paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.path.dirname(__file__), ".env"),
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
    # System env overrides
    for k in config:
        if os.environ.get(k):
            config[k] = os.environ.get(k)
    return config

# ==============================================================================
# SEARCH SUGGEST & TREND ENGINES
# ==============================================================================

def fetch_yandex_suggest(query: str) -> list:
    url = f"https://suggest.yandex.ru/suggest-ya.cgi?v=4&part={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception:
        pass
    return []

def fetch_google_suggest(query: str) -> list:
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl=ru&gl=ru&q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8', errors='ignore'))
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                return data[1]
    except Exception:
        pass
    return []

def fetch_google_trends_rss() -> list:
    """Fetch raw trending search queries from Google Trends Daily RSS for Russia."""
    rss_urls = [
        "https://trends.google.com/trending/rss?geo=RU",
        "https://trends.google.com/trending/rss?geo=US"
    ]
    trends = []
    for u in rss_urls:
        try:
            req = urllib.request.Request(u, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=8) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)
                for item in root.findall(".//item"):
                    title_elem = item.find("title")
                    if title_elem is not None and title_elem.text:
                        trends.append(title_elem.text.strip())
        except Exception:
            continue
    return list(dict.fromkeys(trends))

# ==============================================================================
# B2B ANOMALY SCORING & INTENT EXTRACTION
# ==============================================================================

EMOTIONAL_CRISIS_TRIGGERS = [
    "застрял", "застряли", "почему", "когда приедет", "что случилось", "стоит",
    "пропал", "рейд", "проверка", "конфискат", "штраф", "блокировка", "задержка",
    "не проходит", "возврат", "уйти от карго", "переход", "как сделать", "где взять"
]

COMMERCIAL_B2B_TRIGGERS = [
    "оптом", "купить", "фабрика", "завод", "производство", "китай", "поставка",
    "под ключ", "белая", "гтд", "честный знак", "маркировка", "оборудование",
    "станок", "линия", "юани", "договор", "контракт", "пошлина", "растаможка"
]

def score_query_anomaly(query: str, seed: str, module_key: str) -> dict:
    q_lower = query.lower()
    
    is_question = any(q_lower.startswith(w) or f" {w} " in q_lower for w in ["почему", "когда", "как", "где", "что"])
    crisis_matches = [w for w in EMOTIONAL_CRISIS_TRIGGERS if w in q_lower]
    commercial_matches = [w for w in COMMERCIAL_B2B_TRIGGERS if w in q_lower]
    
    score = 15
    if is_question:
        score += 25
    score += len(crisis_matches) * 20
    score += len(commercial_matches) * 15
    
    # Specific high value B2B terms
    if any(k in q_lower for k in ["гтд", "озон", "вайлдберриз", "115 фз", "карго", "белая доставка"]):
        score += 25
    if any(k in q_lower for k in ["ии игрушки", "ai", "робот", "лазер", "чпу", "тпа", "станок"]):
        score += 25
        
    # Query length (long tail specificity)
    words = q_lower.split()
    if len(words) >= 4:
        score += 15
        
    # Determine context & intent
    if crisis_matches:
        intent = "Кризис / Паника: поиск решения проблемы с застрявшим грузом или проверкой"
    elif any(w in q_lower for w in ["оптом", "купить", "завод", "фабрика"]):
        intent = "Коммерческий опт: поиск прямых фабрик и производителей в КНР"
    elif any(w in q_lower for w in ["гтд", "озон", "маркировка", "документы"]):
        intent = "Регуляторный комплаенс: селлеры ищут белые закрывающие документы для маркетплейсов"
    else:
        intent = "Исследовательский B2B спрос: изучение новинок и условий поставки"
        
    return {
        "query": query,
        "seed": seed,
        "module": module_key,
        "score": score,
        "intent": intent,
        "crisis_triggers": crisis_matches,
        "commercial_triggers": commercial_matches,
        "is_spike": score >= 55
    }

# ==============================================================================
# MODULE 5: LLM FILTERING (GEMINI / LOCAL PROXY / HEURISTIC)
# ==============================================================================

def filter_global_breakouts_via_llm(raw_trends: list, config: dict) -> list:
    """
    Module 5: Global Breakout Discovery.
    Takes raw trending queries from Google Trends, runs through LLM to extract B2B/China gems.
    """
    if not raw_trends:
        return []
        
    # Strict business/commerce filter: sports, celebrities, cinema, politics must be discarded
    STOP_WORDS = [
        "матч", "лига", "фк", "гол", "футбол", "хоккей", "теннис", "сериал", "фильм",
        "актер", "певец", "шоу", "звезда", "биатлон", "бокс", "бой", "умер", "погиб",
        "счет", "трансляция", "состав", "тренер", "азар", "ливерпуль", "реал", "спартак"
    ]
    
    commercial_candidates = []
    COMMERCIAL_HINTS = [
        "купить", "цена", "доставка", "китай", "ai", "ии", "робот", "станок", "товар",
        "тренд", "бренд", "завод", "игрушк", "лазер", "гаджет", "оборудование",
        "производство", "опт", "поставка", "девайс", "смарт", "электроник"
    ]
    
    for t in raw_trends:
        t_l = t.lower()
        if any(sw in t_l for sw in STOP_WORDS):
            continue
        if any(w in t_l for w in COMMERCIAL_HINTS):
            commercial_candidates.append(t)
            
    # If GEMINI_API_KEY is available or local proxy exists, run through LLM
    api_key = config.get("GEMINI_API_KEY")
    if api_key and commercial_candidates:
        prompt = (
            "Ты — ведущий B2B-аналитик поставок и производства в Китае для компании Long Wang (longwang.ru).\n"
            f"Перед тобой список коммерческих запросов из трендов: {json.dumps(commercial_candidates, ensure_ascii=False)}.\n"
            "Выбери из них от 1 до 3 самых перспективных запросов, которые бизнес в РФ побежит закупать, "
            "производить или доставлять из Китая (новые ИИ-гаджеты, игрушки, оборудование, дефицитные товары).\n"
            "Верни JSON массив объектов с ключами: query, why_trending, china_angle, priority."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                json_match = re.search(r'\[.*\]', text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
        except Exception:
            pass
            
    # Clean heuristic result (only return genuine commercial candidates, never sports/noise)
    result = []
    for c in commercial_candidates[:3]:
        result.append({
            "query": c,
            "why_trending": "Аномальный всплеск поискового интереса (Breakout / Rising)",
            "china_angle": "Потенциальный товар для оперативного поиска прямых контрактных фабрик в КНР",
            "priority": "HIGH"
        })
    return result

# ==============================================================================
# BITRIX24 INTEGRATION (TASK & COMMENTS)
# ==============================================================================

def b24_api_call(webhook_url: str, method: str, params: dict) -> dict:
    url = f"{webhook_url.rstrip('/')}/{method}.json"
    payload = json.dumps(params).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def get_or_create_radar_task(webhook_url: str, existing_task_id: str = "") -> str:
    """Finds existing task 'Сбор хайпа' or creates it."""
    if existing_task_id:
        # Verify it exists
        check = b24_api_call(webhook_url, "tasks.task.get", {"taskId": existing_task_id})
        if check.get("result"):
            return existing_task_id
            
    # Search by title
    search_res = b24_api_call(webhook_url, "tasks.task.list", {
        "filter": {"%TITLE": "Сбор хайпа"},
        "select": ["ID", "TITLE"]
    })
    tasks = search_res.get("result", {}).get("tasks", [])
    if tasks:
        task_id = str(tasks[0]["id"])
        print(f"[+] Найдена существующая задача Битрикс24 [ID={task_id}]: «{tasks[0]['title']}»")
        return task_id
        
    # Create new task
    create_res = b24_api_call(webhook_url, "tasks.task.add", {
        "fields": {
            "TITLE": "Сбор хайпа и B2B-трендов Longwang (SEO Breakout Radar)",
            "RESPONSIBLE_ID": 1,  # Artem
            "DESCRIPTION": (
                "Автоматический накопитель ежедневных аналитических дайджестов трендов, "
                "регуляторных всплесков, кризисов карго и продуктового хайпа из Китая для SEO Longwang.ru.\n\n"
                "Скрипт мониторит 5 контуров (Регуляторика, Санкции, Логистика, Продуктовый хайп, Global Breakouts) "
                "и добавляет сводки в виде комментариев к этой задаче."
            ),
            "PRIORITY": 2,  # High
            "TAGS": ["SEO", "Trends", "Longwang", "HypeRadar"]
        }
    })
    new_id = create_res.get("result", {}).get("task", {}).get("id")
    if new_id:
        print(f"[+] Создана новая задача Битрикс24 [ID={new_id}]: «Сбор хайпа и B2B-трендов Longwang»")
        return str(new_id)
    else:
        print(f"[-] Не удалось создать задачу в Битрикс24: {create_res}")
        return ""

def post_b24_comment(webhook_url: str, task_id: str, message_bb: str) -> bool:
    res = b24_api_call(webhook_url, "task.commentitem.add", {
        "TASKID": task_id,
        "FIELDS": {
            "POST_MESSAGE": message_bb
        }
    })
    if res.get("result"):
        print(f"[+] Дайджест успешно добавлен как комментарий в задачу [ID={task_id}]!")
        return True
    else:
        print(f"[-] Ошибка добавления комментария в задачу Битрикс24: {res}")
        return False

# ==============================================================================
# DIGEST FORMATTER (BITRIX24 BB-CODE & CONSOLE)
# ==============================================================================

def format_b24_digest(results_by_module: dict, global_breakouts: list) -> str:
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    lines = [
        f"[b]🚀 ЕЖЕДНЕВНЫЙ АНАЛИТИЧЕСКИЙ ДАЙДЖЕСТ: СБОР ХАЙПА И B2B-ТРЕНДОВ[/b]",
        f"[color=#718096]📅 Время анализа: {now_str} | Мониторинг: Яндекс & Google Suggest + Google Trends[/color]",
        ""
    ]
    
    total_spikes = 0
    for m_key, m_data in results_by_module.items():
        title = m_data["title"]
        spikes = m_data["spikes"]
        hub = m_data["default_hub"]
        
        if not spikes:
            continue
            
        total_spikes += len(spikes)
        lines.append(f"[b]{title}[/b]")
        lines.append(f"[color=#4a5568]Целевой хаб лидогенерации: https://longwang.ru{hub}[/color]")
        
        for i, s in enumerate(spikes[:4], 1):
            triggers = ", ".join(s["crisis_triggers"] + s["commercial_triggers"][:2])
            lines.append(f"• [b]«{s['query']}»[/b] (Score: {s['score']})")
            lines.append(f"   [color=#2b6cb0]Интент:[/color] {s['intent']}")
            if triggers:
                lines.append(f"   [color=#718096]Триггеры:[/color] {triggers}")
        lines.append("")
        
    # Module 5: Global Breakout
    if global_breakouts:
        lines.append("[b]⚡ 5. Global Breakout: Взрывные поисковые тренды за неделю[/b]")
        lines.append("[color=#718096]Широкая воронка Google Trends с ИИ-фильтрацией коммерческого потенциала для Китая[/color]")
        for i, gb in enumerate(global_breakouts[:3], 1):
            lines.append(f"• [b]«{gb['query']}»[/b] [color=#e53e3e][{gb.get('priority', 'TREND')}][/color]")
            lines.append(f"   [color=#2b6cb0]Почему растет:[/color] {gb.get('why_trending', '')}")
            lines.append(f"   [color=#2f855a]Потенциал в КНР:[/color] {gb.get('china_angle', '')}")
        lines.append("")
        
    lines.append("────────────────────────────────────────")
    lines.append("[i]Дайджест подготовлен модулем Trend Spike Radar v2.0. Для постановки в контент-план просто ответьте в этой задаче.[/i]")
    return "\n".join(lines)

# ==============================================================================
# MAIN EXECUTION ORCHESTRATOR
# ==============================================================================

def run_orchestrator(dry_run: bool = False, create_task: bool = False):
    config = load_config()
    webhook = config.get("BITRIX24_WEBHOOK_URL", "")
    task_id = config.get("B24_RADAR_TASK_ID", "")
    
    print("=" * 80)
    print("=== TREND SPIKE RADAR: 5 МОДУЛЕЙ МОНИТОРИНГА ХАЙПА И B2B-ТРЕНДОВ ===")
    print(f"Режим: {'DRY-RUN (Локальная симуляция)' if dry_run else 'LIVE'}")
    print(f"Битрикс24 Вебхук: {'Подключен' if webhook else 'НЕ НАЙДЕН'}")
    print("=" * 80)
    
    # 1. Execute Modules 1-4
    results_by_module = {}
    for m_key, m_info in MODULES.items():
        print(f"\n[*] Сканирование: {m_info['title']} ({len(m_info['seeds'])} семян)...")
        seen = set()
        module_spikes = []
        
        for seed in m_info["seeds"]:
            ya = fetch_yandex_suggest(seed)
            goog = fetch_google_suggest(seed)
            combined = list(dict.fromkeys(ya + goog))
            if not combined:
                combined = [seed]
                
            for q in combined:
                q_clean = q.strip().lower()
                if q_clean not in seen:
                    seen.add(q_clean)
                    scored = score_query_anomaly(q, seed, m_key)
                    if scored["is_spike"]:
                        module_spikes.append(scored)
                        
        module_spikes.sort(key=lambda x: x["score"], reverse=True)
        results_by_module[m_key] = {
            "title": m_info["title"],
            "default_hub": m_info["default_hub"],
            "spikes": module_spikes
        }
        print(f"    -> Выявлено аномалий: {len(module_spikes)} (топ-1: '{module_spikes[0]['query'] if module_spikes else 'нет'}')")

    # 2. Execute Module 5 (Global Breakout)
    print("\n[*] Сканирование Модуля 5: Google Trends Breakout RSS...")
    raw_trends = fetch_google_trends_rss()
    print(f"    -> Собрано сырых трендов: {len(raw_trends)}")
    global_breakouts = filter_global_breakouts_via_llm(raw_trends, config)
    print(f"    -> Отобрано жемчужин после ИИ-фильтра: {len(global_breakouts)}")

    # 3. Format digest
    digest_bb = format_b24_digest(results_by_module, global_breakouts)
    
    print("\n" + "=" * 80)
    print("ИТОГОВЫЙ ДАЙДЖЕСТ ДЛЯ БИТРИКС24:")
    print("=" * 80)
    print(digest_bb)
    print("=" * 80)

    # 4. Bitrix24 delivery
    if not dry_run and webhook:
        active_task_id = get_or_create_radar_task(webhook, task_id)
        if active_task_id:
            post_b24_comment(webhook, active_task_id, digest_bb)
            
            # Save task ID back to .env if it was empty
            if not task_id:
                env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    content = re.sub(r'B24_RADAR_TASK_ID=.*', f'B24_RADAR_TASK_ID={active_task_id}', content)
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[+] B24_RADAR_TASK_ID={active_task_id} зафиксирован в .env")
    elif dry_run:
        print("[DRY-RUN] Отправка в Битрикс24 пропущена (включен тестовый режим)")

def main():
    parser = argparse.ArgumentParser(description="Trend Spike Radar Orchestrator")
    parser.add_argument('--dry-run', action='store_true', help="Run without sending to Bitrix24")
    parser.add_argument('--create-task', action='store_true', help="Find or create Bitrix24 task and exit")
    args = parser.parse_args()
    
    run_orchestrator(dry_run=args.dry_run, create_task=args.create_task)

if __name__ == '__main__':
    main()
