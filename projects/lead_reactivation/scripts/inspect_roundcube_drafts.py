import os
import sys
import json
import datetime
from collections import defaultdict
from loguru import logger

# Add app to path
sys.path.insert(0, '/app')

from imap_tools import MailBox
from sqlalchemy import text
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import ClientReactivationHistory, ReactivationFunnelState, OnecContact, OnecOwner, EmailMessage
import requests

def get_b24_webhook():
    return os.environ.get("B24_WEBHOOK") or os.environ.get("BITRIX24_WEBHOOK") or getattr(settings, "B24_WEBHOOK", None) or getattr(settings, "BITRIX24_WEBHOOK", None)

def check_b24_for_email(b24_webhook: str, email: str):
    """Проверяет сделки, лиды и активности в Б24 для конкретного email."""
    result = {
        "contacts": [],
        "companies": [],
        "active_leads": [],
        "active_deals": [],
        "recent_activities": []
    }
    if not b24_webhook:
        return result
        
    cutoff_b24 = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT00:00:00")
    try:
        # Contacts
        r = requests.post(f"{b24_webhook}crm.contact.list", json={
            "filter": {"EMAIL": email},
            "select": ["ID", "NAME", "LAST_NAME", "COMPANY_ID"]
        }, timeout=7)
        contacts = r.json().get("result", []) if r.status_code == 200 else []
        ct_ids = [c["ID"] for c in contacts]
        comp_ids = [c["COMPANY_ID"] for c in contacts if c.get("COMPANY_ID")]
        result["contacts"] = ct_ids
        result["companies"] = comp_ids
        
        # Leads
        r = requests.post(f"{b24_webhook}crm.lead.list", json={
            "filter": {"EMAIL": email},
            "select": ["ID", "TITLE", "STATUS_ID", "STATUS_SEMANTIC"]
        }, timeout=7)
        leads = r.json().get("result", []) if r.status_code == 200 else []
        for ld in leads:
            if ld.get("STATUS_SEMANTIC") == "process":
                result["active_leads"].append(ld)
                
        # Deals
        for cid in ct_ids:
            r = requests.post(f"{b24_webhook}crm.deal.list", json={
                "filter": {"CONTACT_ID": cid, "STAGE_SEMANTIC": "process"},
                "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY"]
            }, timeout=7)
            deals = r.json().get("result", []) if r.status_code == 200 else []
            result["active_deals"].extend(deals)
            
        for cmp_id in comp_ids:
            r = requests.post(f"{b24_webhook}crm.deal.list", json={
                "filter": {"COMPANY_ID": cmp_id, "STAGE_SEMANTIC": "process"},
                "select": ["ID", "TITLE", "STAGE_ID", "OPPORTUNITY"]
            }, timeout=7)
            deals = r.json().get("result", []) if r.status_code == 200 else []
            result["active_deals"].extend(deals)
            
        # Activities in last 30 days
        for cid in ct_ids:
            r = requests.post(f"{b24_webhook}crm.activity.list", json={
                "filter": {"OWNER_TYPE_ID": 3, "OWNER_ID": cid, ">=START_TIME": cutoff_b24},
                "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID"]
            }, timeout=7)
            acts = r.json().get("result", []) if r.status_code == 200 else []
            result["recent_activities"].extend(acts)
            
        for cmp_id in comp_ids:
            r = requests.post(f"{b24_webhook}crm.activity.list", json={
                "filter": {"OWNER_TYPE_ID": 4, "OWNER_ID": cmp_id, ">=START_TIME": cutoff_b24},
                "select": ["ID", "SUBJECT", "START_TIME", "TYPE_ID"]
            }, timeout=7)
            acts = r.json().get("result", []) if r.status_code == 200 else []
            result["recent_activities"].extend(acts)
            
    except Exception as e:
        logger.warning(f"B24 check error for {email}: {e}")
        
    return result

def main():
    user = os.environ.get("MAIL_ACCOUNT_2_USER") or settings.IMAP_USER or "sales@longwang.ru"
    password = os.environ.get("MAIL_ACCOUNT_2_PASS") or settings.IMAP_PASSWORD
    imap_host = os.environ.get("IMAP_SERVER") or settings.IMAP_HOST or "mail.hostland.ru"
    b24_webhook = get_b24_webhook()
    
    if not password:
        accounts_json = os.environ.get("MAIL_ACCOUNTS")
        if accounts_json:
            try:
                accs = json.loads(accounts_json.strip("'"))
                for a in accs:
                    if a.get("user") == "sales@longwang.ru":
                        user = a.get("user")
                        password = a.get("pass")
                        break
            except Exception as e:
                pass
                
    db = SessionLocal()
    
    print("=" * 80)
    print(f"AUDIT OF ROUNDCUBE / IMAP DRAFTS FOR: {user} ({imap_host})")
    print(f"Audit timestamp: {datetime.datetime.now().isoformat()}")
    print("=" * 80)
    
    drafts_list = []
    with MailBox(imap_host).login(user, password) as mailbox:
        # Find draft folder
        draft_folder = None
        for f in mailbox.folder.list():
            fn_lower = f.name.lower()
            if fn_lower in ["drafts", "inbox.drafts", "черновики", "inbox.черновики"]:
                draft_folder = f.name
                break
        if not draft_folder:
            draft_folder = "Drafts"
            
        mailbox.folder.set(draft_folder)
        # Fetch all drafts
        msgs = list(mailbox.fetch(reverse=True, mark_seen=False))
        print(f"Total drafts found in '{draft_folder}': {len(msgs)}")
        
        for msg in msgs:
            to_list = msg.to or []
            recipient = to_list[0] if to_list else "UNKNOWN"
            in_reply_to = msg.headers.get("in-reply-to", [None])[0] if msg.headers.get("in-reply-to") else None
            references = msg.headers.get("references", [None])[0] if msg.headers.get("references") else None
            
            # Attachments
            atts = []
            for a in msg.attachments:
                atts.append({"name": a.filename, "size": len(a.payload)})
                
            has_presentation = any("презентация" in a["name"].lower() or "reference" in a["name"].lower() for a in atts)
            has_kp = any(any(kw in a["name"].lower() for kw in ["кп", "коммерческ", "спецификац", "счет"]) for a in atts)
            
            html_body = msg.html or ""
            text_body = msg.text or ""
            has_quote_tag = '<blockquote type="cite"' in html_body or '<blockquote' in html_body
            has_quote_marker = "&gt;" in html_body or "> " in text_body
            
            drafts_list.append({
                "uid": msg.uid,
                "date": msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else "NO_DATE",
                "recipient": recipient.lower().strip(),
                "subject": msg.subject or "",
                "in_reply_to": in_reply_to,
                "references": references,
                "attachments": atts,
                "has_presentation": has_presentation,
                "has_kp": has_kp,
                "has_quote_tag": has_quote_tag,
                "has_quote_marker": has_quote_marker,
                "text_snippet": (text_body or html_body)[:250].replace('\n', ' ').strip()
            })

    # Group by recipient to find duplicates
    by_recipient = defaultdict(list)
    for d in drafts_list:
        by_recipient[d["recipient"]].append(d)
        
    print("\n--- 1. DUPLICATE RECIPIENTS AUDIT ---")
    duplicates = {r: dl for r, dl in by_recipient.items() if len(dl) > 1}
    print(f"Unique recipients: {len(by_recipient)}")
    print(f"Recipients with multiple drafts (DUPLICATES): {len(duplicates)}")
    for r, dl in duplicates.items():
        print(f"  * {r}: {len(dl)} drafts! Dates: {[x['date'] for x in dl]}, Subjects: {[x['subject'] for x in dl]}")

    print("\n--- 2. DETAILED AUDIT FOR EACH DRAFT ---")
    detailed_reports = []
    
    for idx, d in enumerate(drafts_list, 1):
        rec = d["recipient"]
        
        # Check DB History
        history_rows = db.query(ClientReactivationHistory).filter(
            ClientReactivationHistory.client_email == rec
        ).order_by(ClientReactivationHistory.sent_at.desc()).all()
        
        funnel_state = db.query(ReactivationFunnelState).filter(
            ReactivationFunnelState.client_email == rec
        ).first()
        
        # Check 1C contact / company
        contact_1c = db.query(OnecContact).filter(
            text(":email = ANY(emails)")
        ).params(email=rec).first()
        
        company_name = ""
        if contact_1c and contact_1c.owner_ref_key:
            owner_1c = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == contact_1c.owner_ref_key).first()
            if owner_1c:
                company_name = getattr(owner_1c, "owner_name", "") or getattr(owner_1c, "name", "")
                
        # Check Bitrix24
        b24_info = check_b24_for_email(b24_webhook, rec)
        
        history_summary = []
        for h in history_rows:
            history_summary.append({
                "date": h.sent_at.strftime("%Y-%m-%d %H:%M") if h.sent_at else "",
                "template": h.template_used,
                "subject": getattr(h, "subject", "")
            })
            
        rep = {
            "index": idx,
            "uid": d["uid"],
            "date": d["date"],
            "recipient": rec,
            "company": company_name,
            "subject": d["subject"],
            "in_reply_to": d["in_reply_to"],
            "has_quote_tag": d["has_quote_tag"],
            "attachments_count": len(d["attachments"]),
            "attachments_names": [a["name"] for a in d["attachments"]],
            "has_presentation": d["has_presentation"],
            "has_kp": d["has_kp"],
            "funnel_state": {
                "step": funnel_state.current_step if funnel_state else None,
                "status": funnel_state.step_status if funnel_state else None,
                "last_action": funnel_state.last_action_at.strftime("%Y-%m-%d") if (funnel_state and funnel_state.last_action_at) else None
            },
            "history_count": len(history_rows),
            "history": history_summary,
            "b24_active_deals": len(b24_info["active_deals"]),
            "b24_active_leads": len(b24_info["active_leads"]),
            "b24_recent_activities": len(b24_info["recent_activities"]),
            "b24_details": b24_info,
            "snippet": d["text_snippet"]
        }
        detailed_reports.append(rep)
        
        print(f"\n[#{idx}] {d['date']} | To: {rec} | Company: {company_name}")
        print(f"     Subject: {d['subject']}")
        print(f"     In-Reply-To: {d['in_reply_to'] or 'MISSING'}")
        print(f"     Quote tag blockquote: {d['has_quote_tag']} | Quote marker: {d['has_quote_marker']}")
        print(f"     Attachments: {[a['name'] for a in d['attachments']]}")
        print(f"     Funnel State: Step {rep['funnel_state']['step']}, Status: {rep['funnel_state']['status']}")
        print(f"     DB History (previous emails): {len(history_rows)} records (Last: {history_summary[0]['date'] if history_summary else 'NONE'})")
        print(f"     B24 Status: Deals={len(b24_info['active_deals'])}, Leads={len(b24_info['active_leads'])}, Activities(30d)={len(b24_info['recent_activities'])}")
        if b24_info['active_deals']:
            print(f"       >>> WARNING: B24 Active deals: {[dl.get('TITLE') for dl in b24_info['active_deals']]}")
        if b24_info['recent_activities']:
            print(f"       >>> WARNING: B24 Recent activities: {[ac.get('SUBJECT') for ac in b24_info['recent_activities']]}")
        print(f"     Snippet: {d['text_snippet'][:120]}...")

    # Save to disk
    os.makedirs("/app/docs", exist_ok=True)
    with open("/app/docs/DRAFTS_AUDIT_REPORT.json", "w", encoding="utf-8") as f:
        json.dump({
            "audit_timestamp": datetime.datetime.now().isoformat(),
            "total_drafts": len(drafts_list),
            "unique_recipients": len(by_recipient),
            "duplicates": {r: len(dl) for r, dl in duplicates.items()},
            "drafts": detailed_reports
        }, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 80)
    print("AUDIT COMPLETED. Report saved to /app/docs/DRAFTS_AUDIT_REPORT.json")
    print("=" * 80)

if __name__ == "__main__":
    main()
