import os

log_path = r"C:\Users\Артем\.gemini\antigravity\brain\5c4e6a07-8c93-498a-9133-f2989f61fc0b\.system_generated\logs\transcript.jsonl"
print(f"Checking: {log_path}")

keywords = ["systemctl", "service", "nginx", "apache", "apt", "docker", "reboot"]

if os.path.exists(log_path):
    print("Log file exists!")
    count = 0
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            # Check if it's a RUN_COMMAND tool call
            if '"type":"PLANNER_RESPONSE"' in line or '"type":"RUN_COMMAND"' in line:
                found = [kw for kw in keywords if kw in line.lower()]
                if found:
                    print(f"Line {i} contains {found}:")
                    # print the CommandLine or content snippet
                    print(f"  {line[:250]}...")
                    count += 1
    print(f"Total matches: {count}")
else:
    print("Log file does NOT exist!")
