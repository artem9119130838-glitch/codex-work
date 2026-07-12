import os
import sys
import glob
import time
import json
import re
from google import generativeai as genai

# Setup API Key
API_KEY = "AIzaSyCj1AUDmL3XtL5zu3lXvwsEsjK0XHdKbjM"
genai.configure(api_key=API_KEY)

# Add src to sys.path
sys.path.append(r"C:\Antigravity\projects\AI chats export\src")

from AI_chats_filter_optimized import (
    RAW_DIR, OUTPUT_DIR, PROMPT_TEMPLATE,
    parse_conversations_json, parse_gemini_takeout_html, parse_conversation_json_file,
    make_batches
)

def call_api_with_retry(prompt, model_name='gemini-2.5-flash', retries=3, delay=20):
    for attempt in range(retries):
        try:
            print(f"  [Attempt {attempt+1}/{retries}] Calling model {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, request_options={"timeout": 180.0})
            
            text = response.text.strip()
            if text.startswith('```json'):
                text = text.removeprefix('```json').removesuffix('```').strip()
            elif text.startswith('```'):
                text = text.removeprefix('```').removesuffix('```').strip()
            return text
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries - 1:
                print(f"  Waiting {delay} seconds before retry...")
                time.sleep(delay)
    raise Exception("API call failed after all retries.")

def main():
    print("Scanning raw files and building batches...")
    all_dialogs = []
    conv_json = os.path.join(RAW_DIR, "conversations.json")
    has_conv_json = os.path.exists(conv_json)
    
    raw_files = glob.glob(os.path.join(RAW_DIR, "*"))
    for file_path in raw_files:
        basename = os.path.basename(file_path)
        ext = os.path.splitext(basename)[1].lower()
        
        if basename == "chat.html" and has_conv_json:
            continue
            
        if basename == "conversations.json":
            all_dialogs.extend(parse_conversations_json(file_path))
        elif basename.endswith(".html") and ("МоиДействия" in basename or "Мои_Действия" in basename):
            all_dialogs.extend(parse_gemini_takeout_html(file_path))
        elif ext == ".txt":
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if content.startswith('{'):
                    all_dialogs.extend(parse_conversation_json_file(file_path))
            except Exception:
                pass

    # Build the exact same batches list
    batches = make_batches(all_dialogs, target_size=300000)
    
    lost_batch_nums = [15, 17, 44, 46]
    
    # We will process each lost batch
    for b_num in lost_batch_nums:
        idx = b_num - 1
        if idx >= len(batches):
            print(f"Batch {b_num} not found.")
            continue
            
        batch_dialogs = batches[idx]
        print(f"\nProcessing Lost Batch {b_num} ({len(batch_dialogs)} dialogs, total {sum(d['length'] for d in batch_dialogs)} chars)...")
        
        # Split this batch into smaller sub-groups (max 100,000 chars each)
        sub_groups = []
        current_group = []
        current_len = 0
        
        for d in batch_dialogs:
            if current_len + d['length'] > 100000 and current_group:
                sub_groups.append(current_group)
                current_group = [d]
                current_len = d['length']
            else:
                current_group.append(d)
                current_len += d['length']
                
        if current_group:
            sub_groups.append(current_group)
            
        print(f"  Split into {len(sub_groups)} sub-batches for processing.")
        
        for sg_idx, sg in enumerate(sub_groups):
            print(f"  --- Sub-batch {sg_idx+1}/{len(sub_groups)} ({len(sg)} dialogs, {sum(d['length'] for d in sg)} chars) ---")
            
            # Build combined text
            combined_text = ""
            for d in sg:
                combined_text += d['text'] + "\n"
                
            prompt = PROMPT_TEMPLATE.format(chat_text=combined_text)
            
            try:
                json_text = call_api_with_retry(prompt)
                
                # Parse JSON
                try:
                    data = json.loads(json_text, strict=False)
                    print("  JSON parsed successfully.")
                    
                    for category, content in data.items():
                        if not content or len(content.strip()) < 10:
                            continue
                            
                        safe_category_name = "".join([c for c in category if c.isalpha() or c.isdigit() or c=='_']).strip()
                        out_file_name = f"{safe_category_name}.md"
                        out_file_path = os.path.join(OUTPUT_DIR, out_file_name)
                        
                        file_exists = os.path.exists(out_file_path)
                        if file_exists:
                            with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                                f_out.write(f"\n\n\n\n\n# Из батча {b_num} (Восстановлено)\n\n")
                                f_out.write(content)
                        else:
                            with open(out_file_path, 'w', encoding='utf-8-sig') as f_out:
                                f_out.write(f"# Категория: {category}\n\n")
                                f_out.write(content)
                                
                        print(f"    Added data to: {safe_category_name}")
                except Exception as je:
                    print(f"  Error parsing JSON: {je}. Saving raw text to Неразобранное_recovered.md")
                    out_file_path = os.path.join(OUTPUT_DIR, "Неразобранное_recovered.md")
                    with open(out_file_path, 'a', encoding='utf-8-sig') as f_out:
                        f_out.write(f"\n\n# Raw response from recovered batch {b_num} sub-batch {sg_idx+1}\n\n{json_text}")
            except Exception as e:
                print(f"  Failed to process sub-batch: {e}")
                
            print("  Waiting 20 seconds before next sub-batch...")
            time.sleep(20)

if __name__ == '__main__':
    # Ensure stdout prints Cyrillic cleanly
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
