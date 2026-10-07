# -*- coding: utf-8 -*-
import os, glob, json, sys, re
sys.stdout.reconfigure(encoding='utf-8')

brain_dir = r"C:\Users\Артем\.gemini\antigravity\brain"
transcripts = glob.glob(os.path.join(brain_dir, "*", ".system_generated", "logs", "transcript.jsonl"))

print(f"Scanning {len(transcripts)} transcripts...")

hits = []
for t in transcripts:
    cid = os.path.basename(os.path.dirname(os.path.dirname(t)))
    try:
        with open(t, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines):
                if any(w in line.lower() for w in ["созвон", "протокол"]) and any(w in line.lower() for w in ["анжелик", "азат", "саул", "александр"]):
                    data = json.loads(line)
                    content = data.get("content", "")
                    if content and len(content) > 30:
                        hits.append((cid, idx, data.get("source", ""), content))
    except Exception:
        pass

print(f"Total hits in transcripts: {len(hits)}")
for cid, idx, src, c in hits[:20]:
    clean = re.sub(r"<[^>]+>", "", c).strip()
    clean = " ".join(clean.split())
    print(f"\n[{cid} | step {idx} | {src}]:")
    print(f"  {clean[:300]}")
