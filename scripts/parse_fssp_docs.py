import os, sys, fitz, re
from datetime import datetime

piev_folder = r'D:\Документы Victus\Личное\Архив_Личного\Субсидиарка\Основное\ФСПП с Госуслуг'
root_folder = r'D:\Документы Victus\Личное\Архив_Личного\Субсидиарка'
main_folder = r'D:\Документы Victus\Личное\Архив_Личного\Субсидиарка\Основное'

all_files = []
if os.path.exists(piev_folder):
    for f in os.listdir(piev_folder):
        if f.endswith('.pdf'):
            all_files.append(os.path.join(piev_folder, f))

# Also check piev in root and main
for folder in [root_folder, main_folder]:
    for f in os.listdir(folder):
        if f.startswith('piev_') and f.endswith('.pdf'):
            full_p = os.path.join(folder, f)
            if full_p not in all_files:
                all_files.append(full_p)

print(f"Total PDF files to analyze: {len(all_files)}")

records = []
for path in all_files:
    try:
        doc = fitz.open(path)
    except Exception as e:
        print(f"Error opening {path}: {e}")
        continue
        
    text = '\n'.join(p.get_text() for p in doc)
    
    # Extract date
    # Header date: от 21.07.2023 №
    date_m = re.search(r'от\s+(\d{2}\.\d{2}\.\d{4})\s+№', text)
    doc_date = date_m.group(1) if date_m else ''
    if not doc_date:
        d2 = re.search(r'(\d{2}\.\d{2}\.\d{4})\s*\nг\.\s*Санкт-Петербург', text)
        doc_date = d2.group(1) if d2 else ''
    if not doc_date:
        d3 = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
        doc_date = d3.group(1) if d3 else ''
        
    # Document title
    doc_type = 'Постановление'
    for line in text.splitlines():
        line_s = line.strip()
        if any(line_s.startswith(x) for x in ['Постановление о', 'Постановление об', 'Акт о', 'Уведомление']):
            doc_type = line_s
            break
            
    # IP number
    ip_m = re.search(r'производства\s+№?\s*(\d+/\d+/\d+-ИП)', text)
    ip_num = ip_m.group(1) if ip_m else ''
    if not ip_num:
        ip_m2 = re.search(r'(\d{5,8}/\d{2}/\d{5}-ИП)', text)
        ip_num = ip_m2.group(1) if ip_m2 else ''
        
    # Creditor
    cred_m = re.search(r'в\s+пользу\s+взыскателя[:\s]+([^,\n]+)', text, re.IGNORECASE)
    cred = cred_m.group(1).strip() if cred_m else ''
    if not cred:
        if 'Бетон Трейд' in text or 'БЕТОН ТРЕЙД' in text: cred = 'ООО Бетон Трейд'
        elif 'Авто-Альянс' in text or 'АВТО-АЛЬЯНС' in text: cred = 'ООО Авто-Альянс'
        elif 'ЖКХ' in text: cred = 'ЖКХ'
        
    # Amount
    sum_m = re.search(r'размере[:\s]+([\d\s\.,]+)\s*р', text, re.IGNORECASE)
    amount = sum_m.group(1).strip().replace(' ', '') if sum_m else ''
    
    # Executive document
    exec_doc = ''
    ed_m = re.search(r'исполнительного документа\s+([^\n]+)', text, re.IGNORECASE)
    if ed_m: exec_doc = ed_m.group(1).strip()
    
    # Reason / Outcome / Articles
    reason = []
    if 'ст. 46' in text:
        p_m = re.search(r'ст\.\s*46[^\n\.]*', text)
        if p_m: reason.append(p_m.group(0))
    if 'ст. 43' in text:
        p_m = re.search(r'ст\.\s*43[^\n\.]*', text)
        if p_m: reason.append(p_m.group(0))
    if 'оконч' in doc_type.lower():
        reason.append('ОКОНЧАНИЕ ИП')
    if 'прекращ' in doc_type.lower():
        reason.append('ПРЕКРАЩЕНИЕ ИП')
    if 'запрет' in doc_type.lower():
        reason.append('ЗАПРЕТ/ОГРАНИЧЕНИЕ')
    if 'отмен' in doc_type.lower():
        reason.append('ОТМЕНА МЕР')
        
    records.append({
        'filename': os.path.basename(path),
        'date': doc_date,
        'doc_type': doc_type,
        'ip_num': ip_num,
        'creditor': cred,
        'amount': amount,
        'exec_doc': exec_doc,
        'reason': '; '.join(reason) if reason else 'Исполнительное действие'
    })

def sort_key(r):
    try:
        return datetime.strptime(r['date'], '%d.%m.%Y')
    except:
        return datetime.min

records.sort(key=sort_key)

print("\n" + "="*120)
print(f"{'ДАТА':<12} | {'НОМЕР ИП':<22} | {'ВЗЫСКАТЕЛЬ':<25} | {'СУММА':<12} | {'ТИП ДОКУМЕНТА':<35} | {'ФАЙЛ'}")
print("="*120)
for r in records:
    print(f"{r['date']:<12} | {r['ip_num']:<22} | {r['creditor'][:24]:<25} | {r['amount']:<12} | {r['doc_type'][:34]:<35} | {r['filename']}")
print("="*120)
