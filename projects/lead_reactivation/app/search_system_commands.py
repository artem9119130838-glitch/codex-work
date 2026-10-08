import os
import json

log_path = r"C:\Users\Артем\.gemini\antigravity\brain\5c4e6a07-8c93-498a-9133-f2989f61fc0b\.system_generated\logs\transcript.jsonl"
print(f"Checking: {log_path}")

if os.path.exists(log_path):
    print("Log file exists!")
    count = 0
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                if data.get("type") == "RUN_COMMAND":
                    cmd = data.get("tool_calls", [{}])[0].get("args", {}).get("CommandLine", "")
                    if any(x in cmd.lower() for x in ["systemctl", "service", "nginx", "apache", "apt", "docker"]):
                        print(f"Line {i} (Step {data.get('step_index')}): {cmd}")
                        count += 1
            except Exception as e:
                pass
    print(f"Total commands matched: {count}")
else:
    print("Log file does NOT exist!")
