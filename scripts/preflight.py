import sys
import yaml
import json
from pathlib import Path

# Fallback token estimator if tiktoken is not installed
def estimate_tokens(text):
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback estimation:
        # English: ~4 characters per token
        # Cyrillic: ~1.5 characters per token
        # Code: ~3 characters per token
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        other_chars = len(text) - cyrillic_chars
        
        # Weighted estimate
        estimated = int(cyrillic_chars / 1.5 + other_chars / 3.5)
        return max(1, estimated)

def check_for_secrets(text):
    dangerous = ['SECRET', 'KEY', 'PASSWORD', 'TOKEN', 'PRIVATE']
    # Check if there is something resembling a hardcoded secret in the text
    upper_text = text.upper()
    for word in dangerous:
        if word in upper_text:
            # check lines
            for line in text.split('\n'):
                if word in line.upper() and ('=' in line or ':' in line or 'define' in line.lower()):
                    if any(q in line for q in ['"', "'"]) or len(line) > 20:
                        return True, line.strip()
    return False, ""

def calculate_cost(tokens, model, is_output=False):
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
    
    m_tokens = tokens / 1_000_000.0
    
    # Context threshold for higher rates is 128k tokens (128,000)
    is_long = tokens > 128000
    
    if model == 'pro':
        key_in = 'input_long' if is_long else 'input_short'
        key_out = 'output_long' if is_long else 'output_short'
        rate = rates['pro'][key_out] if is_output else rates['pro'][key_in]
    elif model == 'flash_8b':
        key_in = 'input_long' if is_long else 'input_short'
        key_out = 'output_long' if is_long else 'output_short'
        rate = rates['flash_8b'][key_out] if is_output else rates['flash_8b'][key_in]
    else:  # default flash
        key_in = 'input_long' if is_long else 'input_short'
        key_out = 'output_long' if is_long else 'output_short'
        rate = rates['flash'][key_out] if is_output else rates['flash'][key_in]
        
    return m_tokens * rate

def main():
    if len(sys.argv) < 2:
        print("Использование: python preflight.py <путь_к_файлу_запроса_или_текст> [модель: flash/pro/flash_8b]")
        sys.exit(0)
        
    input_source = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else 'flash'
    
    # Read prompt text
    prompt_text = ""
    if Path(input_source).exists():
        with open(input_source, 'r', encoding='utf-8', errors='ignore') as f:
            prompt_text = f.read()
    else:
        prompt_text = input_source
        
    # Check secrets
    has_secret, secret_line = check_for_secrets(prompt_text)
    if has_secret:
        print(f"[SECURITY WARNING] В запросе обнаружен потенциальный секрет:")
        print(f"  > {secret_line}")
        print("Кэширование или логирование этого запроса может нарушить SECURITY_POLICY.md!")
        
    # Estimate tokens
    input_tokens = estimate_tokens(prompt_text)
    cost = calculate_cost(input_tokens, model, is_output=False)
    
    # Load budgets
    budget_file = Path('C:/Codex_Personal/.ai/budgets.yaml')
    max_cost = 0.01
    max_tokens = 10000
    if budget_file.exists():
        try:
            with open(budget_file, 'r') as f:
                budgets = yaml.safe_load(f)
                max_cost = budgets.get('request', {}).get('max_cost', max_cost)
                max_tokens = budgets.get('request', {}).get('max_tokens', max_tokens)
        except Exception:
            pass
            
    print(f"\n=== PREFLIGHT GATEWAY ESTIMATION ===")
    print(f"Модель: {model.upper()}")
    print(f"Оценка входных токенов: {input_tokens}")
    print(f"Ориентировочная стоимость: ${cost:.6f} USD (~{cost * 90:.4f} RUB)")
    print(f"Лимит токенов без предупреждения: {max_tokens}")
    print(f"Бюджет на один запрос: ${max_cost} USD")
    
    # Decider
    if cost > max_cost or input_tokens > max_tokens:
        print(f"\n⚠️ ВНИМАНИЕ: Запрос превышает установленные лимиты!")
        print(f"Потребуется подтверждение /force.")
        sys.exit(1) # exit code 1 means over limit
    else:
        print(f"\n✅ Запрос в пределах нормы.")
        sys.exit(0) # exit code 0 means OK

if __name__ == '__main__':
    main()
