import imaplib
import email
import sys
from email.header import decode_header

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

accounts = [
    ('i_li@longwang.ru', 'Artem159753'),
    ('gen_dir@longwang.ru', '70341607Lw'),
]

for user, pwd in accounts:
    print(f"=== Checking account {user} ===")
    try:
        m = imaplib.IMAP4_SSL('mail.hostland.ru', 993)
        m.login(user, pwd)
        for folder in ['INBOX', 'Sent', 'INBOX.Sent']:
            try:
                status, _ = m.select(folder, readonly=True)
                if status != 'OK':
                    continue
                res, data = m.search(None, 'ALL')
                nums = data[0].split() if data[0] else []
                print(f"  Folder {folder}: {len(nums)} messages")
                for num in nums[-20:]:
                    res, msg_data = m.fetch(num, '(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])')
                    hdr = msg_data[0][1].decode('utf-8', errors='ignore')
                    if any(k in hdr.lower() for k in ['465387856', 'qq.com', '163.com', '126.com']):
                        # parse details
                        msg = email.message_from_bytes(msg_data[0][1])
                        frm = decode_mime(msg['From'])
                        sub = decode_mime(msg['Subject'])
                        print(f"    [{folder}] From: {frm} | Sub: {sub} | To: {msg['To']}")
                        if '465387856' in frm or '465387856' in hdr:
                            # Full message
                            _, full = m.fetch(num, '(BODY.PEEK[])')
                            full_msg = email.message_from_bytes(full[0][1])
                            body = ""
                            for p in full_msg.walk():
                                if p.get_content_type() in ['text/plain', 'text/html']:
                                    pl = p.get_payload(decode=True)
                                    if pl:
                                        body += pl.decode('utf-8', errors='ignore') + "\n"
                            print("    >>> BODY OF 465387856 >>>\n", body[:800])
            except Exception as e:
                print(f"  Error in folder {folder}: {e}")
        m.logout()
    except Exception as e:
        print(f"Login error: {e}")
