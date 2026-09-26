import imaplib
import email
from email.header import decode_header
import sys

sys.stdout.reconfigure(encoding='utf-8')

def decode_mime(val):
    if not val:
        return ''
    parts = []
    for text, enc in decode_header(val):
        if isinstance(text, bytes):
            parts.append(text.decode(enc or 'utf-8', errors='ignore'))
        else:
            parts.append(str(text))
    return ' '.join(parts)

def extract_body(msg):
    body = ""
    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type in ['text/plain', 'text/html']:
            payload = part.get_payload(decode=True)
            if payload:
                # Try decoding with part charset, fallback to utf-8 / gbk
                charset = part.get_content_charset() or 'utf-8'
                try:
                    text = payload.decode(charset, errors='replace')
                except Exception:
                    try:
                        text = payload.decode('gb18030', errors='replace')
                    except Exception:
                        text = payload.decode('utf-8', errors='replace')
                body += f"\n--- [{content_type} / {charset}] ---\n" + text
    return body

    import os
    salman_pwd = os.getenv('SALMAN_EMAIL_PASSWORD', '')
    m = imaplib.IMAP4_SSL('mail.hostland.ru', 993)
    if salman_pwd:
        m.login('salman@longwang.ru', salman_pwd)
    else:
        print("SALMAN_EMAIL_PASSWORD is not set.")
        sys.exit(0)
    st, count = m.select('INBOX', readonly=True)
    print(f"Connected to salman@longwang.ru INBOX. Status: {st}, Count: {count}")
    
    st, data = m.search(None, 'ALL')
    nums = data[0].split() if data[0] else []
    print(f"Total messages: {len(nums)}")
    
    # Check the latest 15 messages
    for num in nums[-15:]:
        st, msg_data = m.fetch(num, '(BODY.PEEK[])')
        msg = email.message_from_bytes(msg_data[0][1])
        frm = decode_mime(msg.get('From', ''))
        to = decode_mime(msg.get('To', ''))
        sub = decode_mime(msg.get('Subject', ''))
        date = decode_mime(msg.get('Date', ''))
        print(f"\n================ MSG {num.decode()} ================")
        print(f"Date:    {date}")
        print(f"From:    {frm}")
        print(f"To:      {to}")
        print(f"Subject: {sub}")
        
        body = extract_body(msg)
        print("BODY (preview 1500 chars):")
        print(body[:1500])
        print("="*50)
        
    m.logout()
except Exception as e:
    print(f"Error: {e}")
