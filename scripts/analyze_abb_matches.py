import json

with open(r'c:\Codex\abb_matching_docs.json', 'r', encoding='utf-8') as f:
    docs = json.load(f)

print(f"Total docs loaded: {len(docs)}")
active_docs = [d for d in docs if d['status'] == 'Действует']
print(f"Active docs: {len(active_docs)}")

for idx, p_name in enumerate(['XT3', 'T6', 'OT800']):
    print(f"\n==================== Matches for {p_name} ====================")
    matches = []
    for d in active_docs:
        txt = d['full_text'].lower()
        if p_name.lower() in txt:
            lines = [l.strip() for l in d['full_text'].split('\n') if l.strip()]
            reg_date, end_date, applicant = '', '', ''
            for i, l in enumerate(lines):
                if 'дата регистрации' in l.lower() and i+1 < len(lines):
                    reg_date = lines[i+1]
                if 'дата завершения' in l.lower() and i+1 < len(lines):
                    end_date = lines[i+1]
                if 'заявитель' in l.lower() and i+1 < len(lines):
                    applicant = lines[i+1]
            matches.append({
                'number': d['number'],
                'url': d['url'],
                'reg_date': reg_date,
                'end_date': end_date,
                'applicant': applicant,
                'snippet': d['product_snippet'][:200],
                'full_text': d['full_text']
            })
    print(f"Found {len(matches)} matches")
    for m in matches:
        print(f"--- Doc: {m['number']} ---")
        print(f"URL: {m['url']}")
        print(f"Period: {m['reg_date']} -> {m['end_date']}")
        print(f"Applicant: {m['applicant']}")
        print(f"Product snippet: {m['snippet']}")
        # Check what technical regulations
        regs = []
        if '004/2011' in m['full_text']: regs.append('ТР ТС 004/2011')
        if '020/2011' in m['full_text']: regs.append('ТР ТС 020/2011')
        if '037/2016' in m['full_text']: regs.append('ТР ЕАЭС 037/2016')
        print(f"Technical Regulations: {', '.join(regs)}")
