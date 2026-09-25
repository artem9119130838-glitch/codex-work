import imaplib
import sys

sys.stdout.reconfigure(encoding='utf-8')

for user, pwd in [('gen_dir@longwang.ru', '70341607Lw'), ('i_li@longwang.ru', 'Artem159753')]:
    try:
        m = imaplib.IMAP4_SSL('mail.hostland.ru', 993)
        m.login(user, pwd)
        res, folders = m.list()
        print(f"=== Folders for {user} ===")
        for f in folders:
            folder_line = f.decode('utf-8', errors='ignore')
            parts = folder_line.split(' "/" ')
            if len(parts) == 2:
                folder_name = parts[1].strip('"')
            else:
                folder_name = folder_line
            try:
                m.select(f'"{folder_name}"', readonly=True)
                r, data = m.search(None, 'ALL')
                cnt = len(data[0].split()) if data[0] else 0
                r2, data2 = m.search(None, '(OR FROM "465387856" (OR TO "465387856" (OR BODY "465387856" TEXT "465387856")))')
                cnt2 = len(data2[0].split()) if data2[0] else 0
                if cnt2 > 0:
                    print(f"  --> MATCH: {cnt2} messages in {folder_name}!")
                else:
                    print(f"  {folder_name}: {cnt} msgs")
            except Exception as e:
                print(f"  {folder_name}: error {e}")
        m.logout()
    except Exception as e:
        print(f"Login error {user}: {e}")
