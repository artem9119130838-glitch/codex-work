from sqlalchemy.orm import Session
from app.db.models import EmailMessage, EmailMatchResult, ClientIntel, OnecOwner
from app.services.llm_service import llm_service
from loguru import logger
import json
from datetime import datetime

class SummaryService:
    def __init__(self, db: Session):
        self.db = db
        
    def process_email_summary(self, email_address: str):
        from app.db.models import OnecOwnerLink
        
        # 1. Fetch contact messages (both processed and unprocessed to get full context)
        contact_msgs = self.db.query(EmailMessage).join(
            EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
        ).filter(
            EmailMessage.from_email == email_address,
            EmailMatchResult.decision == 'matched',
            EmailMessage.is_junk == False
        ).order_by(EmailMessage.received_at.asc()).limit(20).all()
        
        if not contact_msgs:
            logger.info(f"No matched messages found for email {email_address}")
            return None
            
        # Determine owner_ref_key (using the first match as representative)
        owner_ref_key = None
        current_matches = self.db.query(EmailMatchResult).filter(
            EmailMatchResult.message_id.in_([m.message_id for m in contact_msgs]),
            EmailMatchResult.decision == 'matched'
        ).all()
        
        for match in current_matches:
            if match.owner_ref_key:
                owner_ref_key = match.owner_ref_key
                break
                
        owner_keys_to_fetch = [owner_ref_key] if owner_ref_key else []
        
        if owner_ref_key:
            # Находим связи Лид <-> Контрагент
            links = self.db.query(OnecOwnerLink).filter(
                (OnecOwnerLink.lead_ref_key == owner_ref_key) | 
                (OnecOwnerLink.contractor_ref_key == owner_ref_key)
            ).all()
            
            for link in links:
                if link.lead_ref_key and link.lead_ref_key not in owner_keys_to_fetch:
                    owner_keys_to_fetch.append(link.lead_ref_key)
                if link.contractor_ref_key and link.contractor_ref_key not in owner_keys_to_fetch:
                    owner_keys_to_fetch.append(link.contractor_ref_key)
                    
        # 2. Fetch company messages (all contacts of this company, up to 30 messages)
        company_msgs = []
        if owner_keys_to_fetch:
            company_msgs = self.db.query(EmailMessage).join(
                EmailMatchResult, EmailMessage.message_id == EmailMatchResult.message_id
            ).filter(
                EmailMatchResult.owner_ref_key.in_(owner_keys_to_fetch),
                EmailMatchResult.decision == 'matched',
                EmailMessage.is_junk == False
            ).order_by(EmailMessage.received_at.asc()).limit(30).all()
            
        owner = self.db.query(OnecOwner).filter(OnecOwner.owner_ref_key == owner_ref_key).first() if owner_ref_key else None
        is_buyer = owner.owner_is_buyer if owner else False
        
        # 3. Build history text helper
        def build_history_text(messages):
            history = []
            for msg in messages:
                date_str = msg.received_at.strftime('%Y-%m-%d %H:%M') if msg.received_at else "Unknown date"
                body = msg.raw_payload.get('cleaned_text', '') if msg.raw_payload else ""
                if not body:
                    body = msg.raw_payload.get('text', '') if msg.raw_payload else ""
                if not body:
                    body = msg.raw_payload.get('snippet', '') if msg.raw_payload else ""
                
                is_sent = msg.raw_payload.get('is_sent', False) if msg.raw_payload else False
                direction = "Исходящее (наш ответ)" if is_sent else "Входящее"
                
                attachments_text = msg.raw_payload.get('attachments_text', '') if msg.raw_payload else ""
                if attachments_text:
                    body += f"\n\n[ИЗВЛЕЧЕННЫЙ ТЕКСТ ВЛОЖЕНИЙ (Ищи здесь артикулы/SKU)]:\n{attachments_text}"
                
                history.append(f"Дата: {date_str}\nНаправление: {direction}\nТема: {msg.subject}\nОтправитель: {msg.from_email}\nТекст: {body[:1500]}...\n---\n")
            return "\n".join(history)
            
        contact_history_text = build_history_text(contact_msgs)
        company_history_text = build_history_text(company_msgs) if company_msgs else contact_history_text
        
        # 4. Call LLM for contact and company summaries
        contact_summary_data = llm_service.generate_contact_summary(contact_history_text, is_buyer)
        company_summary_data = llm_service.generate_company_summary(company_history_text, is_buyer) if company_msgs else None
        
        # 5. Save/Update ClientIntel (contact-level)
        intel = self.db.query(ClientIntel).filter(ClientIntel.email == email_address).first()
        if not intel:
            intel = ClientIntel(
                email=email_address,
                source_id_1c=str(owner_ref_key) if owner_ref_key else None,
                company_name=owner.owner_name if owner else None,
                inn=owner.owner_inn if owner else None,
                emails_count=0,
                emails_list=[]
            )
            self.db.add(intel)
            
        client_type = contact_summary_data.get('client_type', 'неизвестно')
        explanation = contact_summary_data.get('client_type_explanation', '')
        history_text = contact_summary_data.get('interaction_history', '')
        fail_reason = contact_summary_data.get('reason_deal_failed', '')
        probability = contact_summary_data.get('return_probability', '')
        
        md_contact_summary = f"""### 🏷️ Тип контакта: {client_type}
{explanation}

### 📜 История взаимодействия с контактом:
{history_text}

### ❌ Причина отказа:
{fail_reason}

### 📈 Вероятность вернуть контакт:
{probability}"""

        intel.ai_summary = md_contact_summary.strip()
        intel.client_type = client_type
        intel.next_action_recommendation = contact_summary_data.get('next_action_recommendation')
        intel.last_topic = client_type
        intel.current_status = "Покупатель" if is_buyer else "Лид"
        intel.timeline = contact_summary_data.get('timeline', [])
        intel.skus_and_amounts = contact_summary_data.get('skus_and_amounts', [])
        intel.last_managers = contact_summary_data.get('last_managers', [])
        intel.psychological_portrait = contact_summary_data.get('working_features')
        intel.updated_at = datetime.utcnow()
        
        # Build emails metadata list
        emails_list = []
        for msg in contact_msgs:
            body = msg.raw_payload.get('cleaned_text', '') if msg.raw_payload else ""
            if not body:
                body = msg.raw_payload.get('text', '') if msg.raw_payload else ""
            is_sent = msg.raw_payload.get('is_sent', False) if msg.raw_payload else False
            subj = f"Исх: {msg.subject}" if is_sent else msg.subject
            emails_list.append({
                "date": msg.received_at.strftime('%Y-%m-%d %H:%M') if msg.received_at else "Unknown date",
                "subject": subj,
                "preview": f"{body[:150]}..." if len(body) > 150 else body,
                "message_id": msg.message_id
            })
            
        intel.emails_count = len(contact_msgs)
        intel.emails_list = emails_list
        
        # 6. Save/Update OnecOwner (company-level)
        if owner and company_summary_data:
            comp_brief = company_summary_data.get('company_brief', '')
            comp_contacts = company_summary_data.get('associated_contacts', '')
            comp_history = company_summary_data.get('overall_interaction_history', '')
            comp_failed = company_summary_data.get('overall_reasons_failed', '')
            has_deals = "ДА (совершал покупки)" if company_summary_data.get('has_successful_deals', False) else "НЕТ (только запросы)"
            
            md_company_summary = f"""### 🏢 Описание компании:
{comp_brief}

### 👥 Контакты компании:
{comp_contacts}

### 📜 Общая история сделок и общения:
{comp_history}

### 🛍️ Успешные покупки: {has_deals}

### ❌ Причины срыва сделок:
{comp_failed}"""

            owner.ai_email_summary = md_company_summary.strip()
            owner.ai_client_segment = comp_brief[:200] if comp_brief else None
            
        # 7. Mark ONLY the unprocessed messages of the current email as processed
        unprocessed_matches = self.db.query(EmailMatchResult).filter(
            EmailMatchResult.message_id.in_([m.message_id for m in contact_msgs]),
            EmailMatchResult.decision == 'matched',
            EmailMatchResult.ai_processed == False
        ).all()
        
        for match in unprocessed_matches:
            match.ai_processed = True
            
        logger.info(f"Generated separate summaries for email {email_address} and company {owner.owner_name if owner else 'None'}")
        return contact_summary_data

def get_summary_service(db: Session):
    return SummaryService(db)
