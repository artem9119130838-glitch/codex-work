import os
import sys
import json
import re
import datetime
import requests
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.models import EmailMessage, EmailMatchResult, ClientIntel, OnecOwner, OnecContact
from app.services.llm_service import llm_service
from app.services.email_composer import clean_company_name

PUBLIC_DOMAINS = {
    "mail.ru", "inbox.ru", "bk.ru", "list.ru", "yandex.ru", "ya.ru",
    "gmail.com", "rambler.ru", "internet.ru", "ro.ru", "hotmail.com"
}

class OnecEventsService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = (settings.ONEC_ODATA_URL or os.environ.get("ONEC_BASE_URL", "http://192.168.1.100:8080/unf/odata/standard.odata")).rstrip('/')
        user = settings.ONEC_ODATA_USER or os.environ.get("ONEC_USER", "admin")
        pw = settings.ONEC_ODATA_PASSWORD or os.environ.get("ONEC_PASS", "")
        self.auth = (user, pw)
        self.headers = {"Accept": "application/json"}

    def fetch_events_for_email(self, email: str, domain: str = None) -> list[dict]:
        """
        Запрашивает из 1С:УНФ все документы 'Document_Событие' для конкретного email или корпоративного домена.
        """
        if not email:
            return []
            
        clean_email = email.lower().strip()
        events = []
        
        # 1. Поиск по email в СписокУчастников
        try:
            url = f"{self.base_url}/Document_Событие"
            params = {
                "$filter": f"substringof('{clean_email}', СписокУчастников) eq true",
                "$format": "json",
                "$orderby": "Date asc"
            }
            r = requests.get(url, auth=self.auth, headers=self.headers, params=params, timeout=12)
            if r.status_code == 200:
                events = r.json().get('value', [])
        except Exception as e:
            logger.warning(f"Error fetching 1C events for {clean_email}: {e}")

        # 2. Если по прямому email пусто — ищем по домену (для корпоративных доменов)
        if not events:
            dom = domain or clean_email.split('@')[-1]
            if dom and dom not in PUBLIC_DOMAINS:
                try:
                    url = f"{self.base_url}/Document_Событие"
                    params = {
                        "$filter": f"substringof('{dom}', СписокУчастников) eq true",
                        "$format": "json",
                        "$orderby": "Date asc"
                    }
                    r = requests.get(url, auth=self.auth, headers=self.headers, params=params, timeout=12)
                    if r.status_code == 200:
                        events = r.json().get('value', [])
                except Exception as e:
                    logger.warning(f"Error fetching 1C events for domain {dom}: {e}")

        # 3. Fallback to snapshot file if OData returned empty (e.g. network/firewall boundary)
        if not events:
            snapshot_paths = [
                "/app/docs/drafts_1c_events_audit.json",
                "docs/drafts_1c_events_audit.json",
                "scratch/drafts_1c_events_audit.json",
                "/tmp/drafts_1c_events_audit.json"
            ]
            for sp in snapshot_paths:
                if os.path.exists(sp):
                    try:
                        with open(sp, "r", encoding="utf-8") as f:
                            snap_data = json.load(f)
                            if clean_email in snap_data:
                                file_events = snap_data[clean_email].get("events", [])
                                if file_events:
                                    logger.info(f"Loaded {len(file_events)} 1C events from snapshot {sp} for {clean_email}")
                                    events = file_events
                                    break
                    except Exception as ex:
                        logger.warning(f"Failed loading 1C events snapshot from {sp}: {ex}")

        # Нормализация
        normalized = []
        for ev in events:
            content = str(ev.get("Содержание") or ev.get("content") or "").strip()
            subj = str(ev.get("Тема") or ev.get("subject") or "").strip()
            participants = str(ev.get("СписокУчастников") or ev.get("participants") or "").strip()
            ref_key = ev.get("Ref_Key") or ev.get("ref_key")
            date_val = ev.get("Date") or ev.get("date")
            type_val = ev.get("ТипСобытия") or ev.get("type", "ЭлектронноеПисьмо")
            
            # Пропускаем совсем пустые
            if not content and not subj:
                continue
                
            # Определение направления (входящее/исходящее)
            # Если в участниках с адресом клиента стоит 'sales@longwang' или отправитель Long Wang — определяем по тексту
            is_outgoing = ev.get("is_outgoing", False)
            if not is_outgoing:
                first_line = content[:150].lower()
                if any(p in first_line for p in ["с уважением, артем", "с уважением, петров", "longwang", "лун-ван", "заказывать будем из китая"]):
                    is_outgoing = True
                elif "longwang.ru" in participants and not participants.startswith(clean_email):
                    if ev.get("ВходящееИсходящееСобытие") == "Исходящее":
                        is_outgoing = True

            normalized.append({
                "ref_key": ref_key,
                "date": date_val,
                "type": type_val,
                "subject": subj,
                "participants": participants,
                "content": content,
                "is_outgoing": is_outgoing
            })
            
        return normalized

    def sync_events_to_db(self, email: str, events: list[dict]):
        """
        Сохраняет события из 1С в таблицы EmailMessage и EmailMatchResult базы marketing_db.
        """
        if not events:
            return 0
            
        clean_email = email.lower().strip()
        saved_count = 0
        
        for ev in events:
            ref_key = ev["ref_key"]
            msg_id = f"1c_event_{ref_key}"
            
            existing = self.db.query(EmailMessage).filter(EmailMessage.message_id == msg_id).first()
            if not existing:
                # Парсим дату
                try:
                    dt = datetime.datetime.fromisoformat(str(ev["date"]).replace("Z", ""))
                except Exception:
                    dt = datetime.datetime.utcnow()
                    
                is_out = ev.get("is_outgoing", False)
                from_em = "sales@longwang.ru" if is_out else clean_email
                
                msg = EmailMessage(
                    message_id=msg_id,
                    from_email=from_em,
                    from_name=ev.get("participants", ""),
                    subject=ev.get("subject", ""),
                    received_at=dt,
                    source_mailbox="1C_UNF_EVENTS",
                    raw_payload={
                        "text": ev["content"],
                        "cleaned_text": ev["content"],
                        "is_sent": str(is_out).lower(),
                        "event_type": ev.get("type", "ЭлектронноеПисьмо"),
                        "ref_key": ref_key
                    },
                    is_junk=False,
                    created_at=datetime.datetime.utcnow()
                )
                self.db.add(msg)
                self.db.flush()
                
                # Привязка EmailMatchResult
                mr = EmailMatchResult(
                    message_id=msg_id,
                    matched_email=clean_email,
                    matched_level="contact",
                    decision="matched",
                    ai_processed=True
                )
                self.db.add(mr)
                self.db.flush()
                saved_count += 1
                
        if saved_count > 0:
            self.db.commit()
            logger.info(f"Saved {saved_count} new 1C events into EmailMessage for {clean_email}")
            
        return saved_count

    def enrich_client_intel_from_1c_events(self, email: str, events: list[dict], company_name: str = None) -> ClientIntel:
        """
        Строит полноценное досье ClientIntel на основе реальной переписки из 1С:УНФ.
        """
        clean_email = email.lower().strip()
        if not events:
            return self.db.query(ClientIntel).filter(ClientIntel.email == clean_email).first()

        # Формируем объединенный текст диалога для LLM
        dialog_lines = []
        for ev in events:
            direction = "МЫ (LongWang) НАПИСАЛИ" if ev.get("is_outgoing") else "КЛИЕНТ НАПИСАЛ"
            dialog_lines.append(f"[{ev['date']}] {direction} (Тема: {ev['subject']}):\n{ev['content']}\n")
            
        full_dialog = "\n---\n".join(dialog_lines)
        
        # Запрос LLM на саммаризацию истории переписки
        prompt = f"""Внимательно изучи переписку из 1С с клиентом {clean_email} ({company_name or 'Компания'}).
        Составь детальное структурированное досье по контакту и компании.
        
        ПЕРЕПИСКА:
        {full_dialog}
        
        Особое внимание:
        1. Если клиент называл свое имя или представлялся в подписи (например 'С уважением, Александр Алексеевич' или 'Игорь') — обязательно извлеки его имя в поле extracted_person_name!
        2. Найди все конкретные артикулы оборудования, бренды (Kubler, SMC, Danfoss, Caterpillar, Lenze, Bosch Rexroth и др.), суммы или количество в skus_and_amounts.
        3. Зафиксируй причину, почему сделка не состоялась (например: 'высокая цена / оч дорого', 'нет в наличии у дилера', 'клиент ушел думать').
        4. Если в переписке клиент жаловался на цену («дорого», «оч дорого», «не проходим в бюджет») — обязательно укажи это в reason_deal_failed.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "contact_summary": {
                    "type": "object",
                    "properties": {
                        "extracted_person_name": {"type": "string", "description": "Имя или Имя Отчество клиента, если упомянуто"},
                        "client_type": {"type": "string", "description": "конечный заказчик, завод, дистрибьютор, сервис"},
                        "interaction_history": {"type": "string", "description": "Что запрашивал, о чем договаривались"},
                        "reason_deal_failed": {"type": "string", "description": "Причина срыва или паузы"},
                        "next_action_recommendation": {"type": "string", "description": "Что предложить сейчас"},
                        "skus_and_amounts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "sku": {"type": "string"},
                                    "amount": {"type": "string"}
                                },
                                "required": ["sku"]
                            }
                        }
                    },
                    "required": ["extracted_person_name", "interaction_history", "reason_deal_failed", "skus_and_amounts"]
                },
                "company_summary": {
                    "type": "object",
                    "properties": {
                        "company_activity": {"type": "string"},
                        "cooperation_history": {"type": "string"},
                        "sales_potential": {"type": "string"}
                    },
                    "required": ["company_activity", "cooperation_history"]
                }
            },
            "required": ["contact_summary", "company_summary"]
        }
        
        try:
            logger.info(f"Generating enriched AI summary for {clean_email} based on {len(events)} 1C events...")
            resp = llm_service._call_llm(prompt, schema=schema, request_type="client_enrichment_1c")
            summary_data = json.loads(resp)
        except Exception as e:
            logger.error(f"Failed to generate summary for {clean_email}: {e}")
            summary_data = {
                "contact_summary": {
                    "extracted_person_name": "",
                    "client_type": "производственное предприятие",
                    "interaction_history": full_dialog[:500],
                    "reason_deal_failed": "пауза в согласовании",
                    "skus_and_amounts": []
                },
                "company_summary": {
                    "company_activity": company_name or "Промышленность",
                    "cooperation_history": "Переписка в 1С"
                }
            }

        # Обновляем или создаем ClientIntel
        ci = self.db.query(ClientIntel).filter(ClientIntel.email == clean_email).first()
        ct_summary = summary_data.get("contact_summary", {})
        skus = ct_summary.get("skus_and_amounts", [])
        
        if not ci:
            ci = ClientIntel(
                email=clean_email,
                company_name=company_name or "Компания",
                client_type="производственное предприятие",
                ai_summary=json.dumps(summary_data, ensure_ascii=False),
                skus_and_amounts=skus,
                updated_at=datetime.datetime.utcnow()
            )
            self.db.add(ci)
        else:
            # Снимаем статус cold_lead! Это теплый контакт с реальной историей
            ci.client_type = ct_summary.get("client_type") or "производственное предприятие"
            if company_name and ci.company_name in ["Компания", "Неизвестная компания", None]:
                ci.company_name = company_name
            ci.ai_summary = json.dumps(summary_data, ensure_ascii=False)
            ci.skus_and_amounts = skus
            ci.updated_at = datetime.datetime.utcnow()
            
        self.db.commit()
        logger.info(f"Successfully enriched ClientIntel for {clean_email}: ЛПР='{ct_summary.get('extracted_person_name')}', SKUs={len(skus)}, Причина='{ct_summary.get('reason_deal_failed')}'")
        return ci
