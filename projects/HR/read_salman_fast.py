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

print("Starting test...", flush=True)
try:
    m = imaplib.IMAP4_SSL('mail.hostland.ru', 993, timeout=15)
    print("SSL connected, logging in...", flush=True)
    m.login('salman@longwang.ru', 'Artem167259!')
    print("Logged in successfully!", flush=True)
    
    st, folders = m.list()
    print("Folders:", flush=True)
    for f in folders:
        print("  ", f.decode('utf-8', errors='ignore'), flush=True)
        
    st, count = m.select('INBOX', readonly=True)
    print(f"Selected INBOX: {st}, {count}", flush=True)
    
    st, data = m.search(None, 'ALL')
    nums = data[0].split() if data[0] else []
    print(f"Total messages in INBOX: {len(nums)}", flush=True)
    
    # Just fetch headers of last 10 messages
    for num in nums[-10:]:
        st, msg_data = m.fetch(num, '(BODY.PEEK[HEADER.FIELDS (DATE FROM TO SUBJECT)])')
        hdr_raw = msg_data[0][1].decode('utf-8', errors='ignore')
        msg = email.message_from_string(hdr_raw)
        frm = decode_mime(msg.get('From', ''))
        sub = decode_mime(msg.get('Subject', ''))
        date = decode_mime(msg.get('Date', ''))
        print(f"Msg #{num.decode()}: Date: {date} | From: {frm} | Subject: {sub}", flush=True)
        
    m.logout()
except Exception as e:
    print(f"Exception: {type(e)} - {e}", flush=True)
