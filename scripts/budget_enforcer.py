import sys
import json
import yaml
from datetime import date
from pathlib import Path

LOG_FILE = Path('C:/Codex_Personal/.ai/token_usage.jsonl')
BUDGET_FILE = Path('C:/Codex_Personal/.ai/budgets.yaml')

def calculate_cost(input_tokens, output_tokens, model):
    # Rates per 1M tokens
    rates = {
        'flash': {
            'input_short': 0.075,
            'input_long': 0.15,
            'output_short': 0.30,
            'output_long': 0.60
        },
        'pro': {
            'input_short': 1.25,
            'input_long': 2.50,
            'output_short': 5.00,
            'output_long': 10.00
        },
        'flash_8b': {
            'input_short': 0.0375,
            'input_long': 0.075,
            'output_short': 0.15,
            'output_long': 0.30
        }
    }
    
    is_long_in = input_tokens > 128000
    is_long_out = (input_tokens + output_tokens) > 128000
    
    if model == 'pro':
        in_rate = rates['pro']['input_long'] if is_long_in else rates['pro']['input_short']
        out_rate = rates['pro']['output_long'] if is_long_out else rates['pro']['output_short']
    elif model == 'flash_8b':
        in_rate = rates['flash_8b']['input_long'] if is_long_in else rates['flash_8b']['input_short']
        out_rate = rates['flash_8b']['output_long'] if is_long_out else rates['flash_8b']['output_short']
    else:  # default flash
        in_rate = rates['flash']['input_long'] if is_long_in else rates['flash']['input_short']
        out_rate = rates['flash']['output_long'] if is_long_out else rates['flash']['output_short']
        
    cost = (input_tokens / 1_000_000.0) * in_rate + (output_tokens / 1_000_000.0) * out_rate
    return cost

def load_limits():
    default_limits = {
        'daily': {'flash': 5.0, 'pro': 1.0, 'flash_8b': 0.5},
        'session': {'max_cost': 0.50},
        'request': {'max_cost': 0.01}
    }
    if BUDGET_FILE.exists():
        try:
            with open(BUDGET_FILE, 'r') as f:
                limits = yaml.safe_load(f)
                if limits:
                    return limits
        except Exception:
            pass
    return default_limits

def get_today_spent():
    today = str(date.today())
    spent = {'total': 0.0, 'flash': 0.0, 'pro': 0.0, 'flash_8b': 0.0}
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get('date') == today:
                        model = rec.get('model', 'flash')
                        cost = rec.get('cost', 0.0)
                        spent['total'] += cost
                        if model in spent:
                            spent[model] += cost
                except Exception:
                    pass
    return spent

def log_usage(model, input_tokens, output_tokens, task=""):
    cost = calculate_cost(input_tokens, output_tokens, model)
    
    # Ensure directory exists
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    record = {
        'date': str(date.today()),
        'model': model,
        'input': input_tokens,
        'output': output_tokens,
        'cost': cost,
        'task': task[:150]
    }
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
    print(f"[BUDGET LOGGER] Запись добавлена. Модель: {model.upper()}, токенов: In {input_tokens} / Out {output_tokens}, Стоимость: ${cost:.6f}")

def check_budget():
    limits = load_limits()
    spent = get_today_spent()
    
    # Calculate daily total budget
    daily_flash_limit = limits.get('daily', {}).get('flash', 5.0)
    daily_pro_limit = limits.get('daily', {}).get('pro', 1.0)
    daily_8b_limit = limits.get('daily', {}).get('flash_8b', 0.5)
    
    # Check flash models
    if spent['flash'] > daily_flash_limit:
        print(f"[BUDGET ALARM] Дневной лимит для Flash моделей (${daily_flash_limit}) превышен! Потрачено: ${spent['flash']:.4f}")
        return False
        
    # Check pro models
    if spent['pro'] > daily_pro_limit:
        print(f"[BUDGET ALARM] Дневной лимит для Pro моделей (${daily_pro_limit}) превышен! Потрачено: ${spent['pro']:.4f}")
        return False
        
    # Check total budget
    total_limit = daily_flash_limit + daily_pro_limit + daily_8b_limit
    if spent['total'] > total_limit:
        print(f"[BUDGET ALARM] Суммарный дневной бюджет (${total_limit}) превышен! Потрачено: ${spent['total']:.4f}")
        return False
        
    return True

def show_status():
    limits = load_limits()
    spent = get_today_spent()
    
    daily_flash_limit = limits.get('daily', {}).get('flash', 5.0)
    daily_pro_limit = limits.get('daily', {}).get('pro', 1.0)
    daily_8b_limit = limits.get('daily', {}).get('flash_8b', 0.5)
    
    print("\n=== СОСТОЯНИЕ БЮДЖЕТА API ===")
    print(f"Дата: {date.today()}")
    print(f"Gemini Flash: Потрачено: ${spent['flash']:.4f} / Лимит: ${daily_flash_limit:.4f} (Остаток: ${(daily_flash_limit - spent['flash']):.4f})")
    print(f"Gemini Pro:   Потрачено: ${spent['pro']:.4f} / Лимит: ${daily_pro_limit:.4f} (Остаток: ${(daily_pro_limit - spent['pro']):.4f})")
    print(f"Gemini 8B:    Потрачено: ${spent['flash_8b']:.4f} / Лимит: ${daily_8b_limit:.4f} (Остаток: ${(daily_8b_limit - spent['flash_8b']):.4f})")
    print(f"Всего сегодня: Потрачено: ${spent['total']:.4f} / Лимит: ${(daily_flash_limit + daily_pro_limit + daily_8b_limit):.4f}")
    
    # Calculate savings compared to no standard (assuming standard saves ~90%)
    no_std_estimate = spent['total'] / 0.10
    savings = no_std_estimate - spent['total']
    if spent['total'] > 0:
        print(f"Оценочная экономия сегодня благодаря TOKEN-FIRST: ${savings:.4f} USD (~{savings * 90:.2f} RUB)")

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python budget_enforcer.py check")
        print("  python budget_enforcer.py status")
        print("  python budget_enforcer.py log <model> <input_tokens> <output_tokens> [task]")
        sys.exit(0)
        
    cmd = sys.argv[1]
    
    if cmd == 'check':
        if check_budget():
            print("✅ Бюджет в норме.")
            sys.exit(0)
        else:
            sys.exit(1)
            
    elif cmd == 'status':
        show_status()
        
    elif cmd == 'log':
        if len(sys.argv) < 5:
            print("Ошибка: недостаточно аргументов для логирования.")
            sys.exit(1)
        model = sys.argv[2]
        try:
            in_tokens = int(sys.argv[3])
            out_tokens = int(sys.argv[4])
        except ValueError:
            print("Ошибка: количество токенов должно быть целым числом.")
            sys.exit(1)
        task = sys.argv[5] if len(sys.argv) > 5 else ""
        log_usage(model, in_tokens, out_tokens, task)
        
    else:
        print(f"Неизвестная команда: {cmd}")
        sys.exit(1)

if __name__ == '__main__':
    main()
