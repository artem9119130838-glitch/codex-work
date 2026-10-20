#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch and sanitize email thread with a.shatilov@elox-prom.ru via IMAP.
Extracts facts, equipment models, delivery terms, and verification (поверка) details.
Outputs summary to stdout and full cleaned batch to disk.
"""

import os
import sys
import json
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def decode_mime_words(s):
    if not s:
        return ""
    decoded_fragments = decode_header(s)
    text = ""
    for frag, enc in decoded_fragments:
        if isinstance(frag, bytes):
            enc = enc or 'utf-8'
            try:
                text += frag.decode(enc, errors='ignore')
            except Exception:
                text += frag.decode('cp1251', errors='ignore')
        else:
            text += str(frag)
    return text

def clean_body_text(text):
    if not text:
        return ""
    # remove html tags
    clean = re.sub(r'<[^>]+>', ' ', text)
    # clean extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def main():
    env_path = r"c:\Codex\projects\1c_odata\.env"
    env = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    env[k.strip()] = v.strip().strip("'\"")

    host = env.get("IMAP_SERVER", "mail.hostland.ru")
    port = int(env.get("IMAP_PORT", 993))
    user = env.get("IMAP_USER", "sales@longwang.ru")
    password = env.get("IMAP_PASSWORD", "")

    client_email = "a.shatilov@elox-prom.ru"
    client_domain = "elox-prom.ru"

    print(f"[*] Подключение к IMAP {host}:{port} ({user})...")
    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(user, password)
    print("[+] Авторизация в IMAP успешна!")

    # Parse folders reliably
    available_folders = []
    status, folder_list = mail.list()
    if status == 'OK':
        for f in folder_list:
            raw = f.decode('utf-8', errors='ignore')
            # Extract folder name after delimiter "."
            parts = raw.split(' "." ')
            if len(parts) > 1:
                f_name = parts[-1].strip().strip('"')
                available_folders.append(f_name)
            else:
                # Fallback simple split
                available_folders.append(raw.split()[-1].strip('"'))

    print(f"[+] Распознано папок IMAP: {len(available_folders)}")

    collected_messages = []
    seen_message_ids = set()

    for folder in available_folders:
        try:
            status, _ = mail.select(f'"{folder}"', readonly=True)
            if status != 'OK':
                continue
        except Exception:
            continue

        # Search by client email or domain
        search_criteria = [
            f'(FROM "{client_email}")',
            f'(TO "{client_email}")',
            f'(FROM "{client_domain}")',
            f'(TO "{client_domain}")'
        ]

        found_uids = set()
        for crit in search_criteria:
            try:
                res, data = mail.search(None, crit)
                if res == 'OK' and data[0]:
                    for num in data[0].split():
                        found_uids.add(num)
            except Exception:
                pass

        if not found_uids:
            continue

        print(f"[+] Папка '{folder}': найдено писем по клиенту: {len(found_uids)}")
        for num in found_uids:
            try:
                res, data = mail.fetch(num, '(RFC822)')
                if res != 'OK':
                    continue
                msg = email.message_from_bytes(data[0][1])
                msg_id = msg.get('Message-ID', str(num))
                if msg_id in seen_message_ids:
                    continue
                seen_message_ids.add(msg_id)

                subj = decode_mime_words(msg.get('Subject', ''))
                sender = decode_mime_words(msg.get('From', ''))
                recipient = decode_mime_words(msg.get('To', ''))
                date_str = msg.get('Date', '')

                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        disp = str(part.get('Content-Disposition', ''))
                        if ctype == 'text/plain' and 'attachment' not in disp:
                            payload = part.get_payload(decode=True)
                            if payload:
                                charset = part.get_content_charset() or 'utf-8'
                                try:
                                    body_text += payload.decode(charset, errors='ignore') + "\n"
                                except Exception:
                                    body_text += payload.decode('cp1251', errors='ignore') + "\n"
                        elif ctype == 'text/html' and not body_text and 'attachment' not in disp:
                            payload = part.get_payload(decode=True)
                            if payload:
                                charset = part.get_content_charset() or 'utf-8'
                                try:
                                    body_text += clean_body_text(payload.decode(charset, errors='ignore'))
                                except Exception:
                                    body_text += clean_body_text(payload.decode('cp1251', errors='ignore'))
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        charset = msg.get_content_charset() or 'utf-8'
                        try:
                            body_text = payload.decode(charset, errors='ignore')
                        except Exception:
                            body_text = payload.decode('cp1251', errors='ignore')

                # Collect attachments names
                attachments = []
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_maintype() == 'multipart':
                            continue
                        if part.get('Content-Disposition') is not None:
                            fname = decode_mime_words(part.get_filename())
                            if fname:
                                attachments.append(fname)

                collected_messages.append({
                    "folder": folder,
                    "date": date_str,
                    "subject": subj,
                    "from": sender,
                    "to": recipient,
                    "attachments": attachments,
                    "body_snippet": clean_body_text(body_text)[:1500]
                })
            except Exception as e:
                print(f"[-] Ошибка обработки письма #{num}: {e}")

    mail.logout()

    out_file = r"c:\Codex\projects\SEO\scripts\elox_prom_batch.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(collected_messages, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"РЕЗЮМЕ ВЫГРУЗКИ ПО КЛИЕНТУ ЭЛОКС-ПРОМ (Всего писем: {len(collected_messages)})")
    print(f"Полный очищенный батч сохранен: {out_file}")
    print("=" * 80)
    for idx, m in enumerate(collected_messages[:8], 1):
        print(f"[{idx}] Дата: {m['date'][:25]} | Папка: {m['folder']}")
        print(f"     От: {m['from'][:40]} -> Кому: {m['to'][:40]}")
        print(f"     Тема: {m['subject'][:70]}")
        if m['attachments']:
            print(f"     Вложения: {', '.join(m['attachments'][:3])}")
        print(f"     Текст: {m['body_snippet'][:180]}...")
        print("-" * 60)

if __name__ == '__main__':
    main()
