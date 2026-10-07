# -*- coding: utf-8 -*-
import os, glob, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

brain_dir = r"C:\Users\Артем\.gemini\antigravity\brain"
transcripts = glob.glob(os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl"))

user_messages = []
for t in transcripts:
    try:
        with open(t, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if data.get("type") == "USER_INPUT" or data.get("source") == "USER_EXPLICIT":
                        content = data.get("content", "")
                        if content and len(content) < 500: # short triggers / instructions
                            user_messages.append(content.strip())
                except Exception:
                    pass
    except Exception:
        pass

print(f"Total user messages collected: {len(user_messages)}")

# Normalize and count short triggers
short_triggers = [m.lower() for m in user_messages if len(m) < 80]
trigger_counts = Counter(short_triggers)
print("\n=== TOP 30 SHORT USER TRIGGERS ===")
for text, count in trigger_counts.most_common(30):
    print(f"{count:4d}: {text}")

# Look for patterns in all user messages:
keywords = [
    "конец чата", "compress", "follow up", "follow-up", "лиды", "лидов", "1с", "битрикс",
    "почисти", "ревизия", "зафиксируй", "правило", "dry-run", "dry run", "секрет", "пароль",
    "токен", "vps", "docker", "почт", "сделк", "звонок", "excel", "китай", "тендер"
]

kw_counts = Counter()
for m in user_messages:
    m_lower = m.lower()
    for kw in keywords:
        if kw in m_lower:
            kw_counts[kw] += 1

print("\n=== TOP KEYWORDS IN USER PROMPTS ===")
for kw, count in kw_counts.most_common(30):
    print(f"{count:4d}: {kw}")

# Find frequent exact sentences or repetitive reminders (regex for reminders)
reminders = []
for m in user_messages:
    if any(w in m.lower() for w in ["зафиксируй", "правило", "почему", "забыл", "было правило", "не пиши", "без слов", "запрещено"]):
        reminders.append(m)

print(f"\nTotal reminders / complaints found: {len(reminders)}")
print("\n=== SAMPLE TOP REPETITIVE REMINDERS / COMPLAINTS ===")
for r in reminders[:20]:
    clean_r = " ".join(r.split())
    print(f"- {clean_r[:120]}")
