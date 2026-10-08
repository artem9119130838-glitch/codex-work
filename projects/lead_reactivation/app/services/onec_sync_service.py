import json
import uuid
import re
import requests
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import text, tuple_
from app.core.config import settings
from app.db.models import OnecOwner, OnecContact, OnecOwnerLink

class OnecSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.ONEC_ODATA_URL.rstrip('/')
        self.auth = (settings.ONEC_ODATA_USER, settings.ONEC_ODATA_PASSWORD)
        self.headers = {"Accept": "application/json"}
        self.contact_to_owner_map = {}

    def _fetch_odata(self, endpoint: str, params: dict = None):
        """Helper to fetch from 1C OData."""
        url = f"{self.base_url}/{endpoint}"
        if params is None:
            params = {}
        if "$format" not in params:
            params["$format"] = "json"
            
        logger.debug(f"Fetching OData: {url} params={params}")
        response = requests.get(url, auth=self.auth, headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get('value', [])

    def _extract_contact_info(self, info_array):
        """Extract emails and phones from 1C КонтактнаяИнформация."""
        emails = []
        phones = []
        if not info_array:
            return emails, phones
            
        for item in info_array:
            c_type = item.get("Тип", "")
            val = item.get("Представление", "").strip()
            if not val:
                continue
            if c_type == "АдресЭлектроннойПочты":
                for e in re.split(r'[;,\s]+', val.lower()):
                    if e:
                        emails.append(e)
            elif c_type == "Телефон":
                for p in re.split(r'[;,\s]+', val):
                    if p:
                        phones.append(p)
        return emails, phones

    def sync_contractors(self):
        """Sync ALL buyers from Catalog_Контрагенты (Full Sync to catch contact updates)."""
        logger.info("Starting FULL sync of contractors...")
        
        skip = 0
        top = 200
        
        while True:
            params = {
                "$filter": "Покупатель eq true",
                "$skip": skip,
                "$top": top
            }
            try:
                batch = self._fetch_odata("Catalog_Контрагенты", params)
            except Exception as e:
                logger.error(f"Failed to fetch contractors: {e}")
                break
                
            if not batch:
                break
                
            logger.info(f"Processing {len(batch)} contractors (skip={skip})")
            for row in batch:
                ref_key = row.get("Ref_Key")
                if not ref_key:
                    continue
                
                ref_uuid = uuid.UUID(ref_key)
                
                # Построение карты связей для контактов (решение проблемы пустых Владелец_Key)
                contact_key = row.get("КонтактноеЛицо_Key")
                if contact_key and contact_key != "00000000-0000-0000-0000-000000000000":
                    contact_uuid = uuid.UUID(contact_key)
                    self.contact_to_owner_map[contact_uuid] = ref_uuid
                
                info = row.get("КонтактнаяИнформация", [])
                emails, phones = self._extract_contact_info(info)
                
                # Check if exists
                owner = self.db.query(OnecOwner).filter_by(owner_ref_key=ref_uuid).first()
                if not owner:
                    owner = OnecOwner(
                        owner_entity="Catalog_Контрагенты",
                        owner_ref_key=ref_uuid,
                        owner_is_junk=False,
                        owner_search_emails=[],
                        owner_search_phones=[],
                        owner_tags_text=[],
                        owner_sites=[],
                        owner_addresses={},
                        owner_contact_names=[],
                        owner_contact_count=0,
                        owner_contact_emails=[],
                        owner_contact_phones=[],
                        owner_all_emails=[],
                        owner_all_phones=[],
                        owner_is_important=False,
                        owner_importance_score=0,
                        owner_tags={},
                        raw_payload={}
                    )
                    self.db.add(owner)
                
                owner.owner_name = row.get("Description", "")
                owner.owner_inn = row.get("ИНН", "")
                owner.owner_is_buyer = True
                owner.owner_search_emails = emails
                owner.owner_search_phones = phones
                owner.raw_payload = row
                owner.fetched_at = datetime.utcnow()
                
            self.db.commit()
            if len(batch) < top:
                break
            skip += top

    def sync_contacts(self):
        """Sync contact persons from Catalog_КонтактныеЛица."""
        logger.info("Starting sync of contact persons...")
        skip = 0
        top = 200
        
        while True:
            params = {
                "$skip": skip,
                "$top": top
            }
            try:
                batch = self._fetch_odata("Catalog_КонтактныеЛица", params)
            except Exception as e:
                logger.error(f"Failed to fetch contacts: {e}")
                break
                
            if not batch:
                break
                
            logger.info(f"Processing {len(batch)} contacts (skip={skip})")
            for row in batch:
                ref_key = row.get("Ref_Key")
                owner_key = row.get("Владелец_Key")
                
                ref_uuid = uuid.UUID(ref_key) if ref_key else None
                owner_uuid = uuid.UUID(owner_key) if (owner_key and owner_key != "00000000-0000-0000-0000-000000000000") else None
                
                # Если Владелец_Key пустой, пробуем восстановить связь через Контрагента
                if not owner_uuid and ref_uuid:
                    owner_uuid = self.contact_to_owner_map.get(ref_uuid)
                    
                if not ref_uuid or not owner_uuid:
                    continue
                
                info = row.get("КонтактнаяИнформация", [])
                emails, phones = self._extract_contact_info(info)
                
                # Check for overlapping synthetic contact
                for email in emails:
                    synth_contact = self.db.query(OnecContact).filter(
                        OnecContact.owner_ref_key == owner_uuid,
                        OnecContact.is_synthetic == True,
                        OnecContact.emails.any(email)
                    ).first()
                    
                    if synth_contact:
                        logger.info(f"Overwriting synthetic contact for email {email} with real contact {ref_uuid}")
                        # Cascade update to email_match_results
                        self.db.execute(
                            text("UPDATE email_match_results SET contact_ref_key = :real WHERE contact_ref_key = :synth"),
                            {"real": ref_uuid, "synth": synth_contact.contact_ref_key}
                        )
                        self.db.delete(synth_contact)
                        self.db.commit()
                
                contact = self.db.query(OnecContact).filter_by(contact_ref_key=ref_uuid).first()
                if not contact:
                    contact = OnecContact(
                        contact_entity="Catalog_КонтактныеЛица",
                        contact_ref_key=ref_uuid,
                        emails=[],
                        phones=[],
                        contact_is_junk=False,
                        contact_tags={},
                        contact_channels={},
                        raw_payload={}
                    )
                    self.db.add(contact)
                    
                contact.owner_entity = "Catalog_Контрагенты"
                contact.owner_ref_key = owner_uuid
                contact.contact_name = row.get("Description", "")
                contact.emails = emails
                contact.phones = phones
                contact.raw_payload = row
                contact.fetched_at = datetime.utcnow()
                contact.is_synthetic = False
                
            self.db.commit()
            if len(batch) < top:
                break
            skip += top

    def generate_synthetic_contacts(self):
        """Create synthetic contacts for buyers that have emails but no contacts."""
        logger.info("Generating synthetic contacts...")
        
        # 1. Get all buyers
        buyers = self.db.query(OnecOwner).filter(OnecOwner.owner_is_buyer == True).all()
        created = 0
        
        for buyer in buyers:
            if not buyer.owner_search_emails:
                continue
                
            # Deduplicate emails to prevent duplicate synthetic contacts in same run
            unique_emails = list(set(buyer.owner_search_emails))
            for email in unique_emails:
                if not email:
                    continue
                    
                # Check if has any contacts with this email
                has_contact = self.db.query(OnecContact).filter(
                    OnecContact.owner_ref_key == buyer.owner_ref_key,
                    OnecContact.emails.any(email)
                ).count() > 0
                
                if has_contact:
                    continue
                    
                # Generate synthetic contact for EACH email
                namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
                synth_ref_uuid = uuid.uuid5(namespace, str(buyer.owner_ref_key) + "_" + email)
                
                contact = self.db.query(OnecContact).filter_by(contact_ref_key=synth_ref_uuid).first()
                if not contact:
                    contact = OnecContact(
                        contact_entity="Synthetic",
                        contact_ref_key=synth_ref_uuid,
                        contact_is_junk=False,
                        contact_tags={},
                        contact_channels={},
                        raw_payload={}
                    )
                    self.db.add(contact)
                    created += 1
                    
                contact.owner_entity = buyer.owner_entity
                contact.owner_ref_key = buyer.owner_ref_key
                contact.contact_name = "Общий контакт компании"
                contact.emails = [email]
                contact.phones = buyer.owner_search_phones
                contact.fetched_at = datetime.utcnow()
                contact.is_synthetic = True
            
        self.db.commit()
        logger.info(f"Generated {created} synthetic contacts.")

    def link_leads_and_contractors(self):
        """Match leads (owner_is_buyer=False) to contractors (owner_is_buyer=True)."""
        logger.info("Linking leads to contractors...")
        
        leads = self.db.query(OnecOwner).filter(OnecOwner.owner_is_buyer == False).all()
        buyers = self.db.query(OnecOwner).filter(OnecOwner.owner_is_buyer == True).all()
        
        # Build indexes for fast lookup
        buyer_by_inn = {}
        buyer_by_email = {}
        buyer_by_phone = {}
        
        for b in buyers:
            if b.owner_inn and len(b.owner_inn) >= 9:
                buyer_by_inn[b.owner_inn] = b.owner_ref_key
            for email in b.owner_search_emails:
                if email:
                    buyer_by_email[email.lower()] = b.owner_ref_key
            for phone in b.owner_search_phones:
                if phone and len(phone) >= 7:
                    buyer_by_phone[phone] = b.owner_ref_key

        links_created = 0
        for lead in leads:
            # Skip if already linked
            existing_link = self.db.query(OnecOwnerLink).filter_by(lead_ref_key=lead.owner_ref_key).first()
            if existing_link:
                continue
                
            matched_buyer = None
            reason = None
            
            if lead.owner_inn and lead.owner_inn in buyer_by_inn:
                matched_buyer = buyer_by_inn[lead.owner_inn]
                reason = "matched_by_inn"
            
            if not matched_buyer:
                for email in lead.owner_search_emails:
                    if email and email.lower() in buyer_by_email:
                        matched_buyer = buyer_by_email[email.lower()]
                        reason = f"matched_by_email:{email}"
                        break
            
            if not matched_buyer:
                for phone in lead.owner_search_phones:
                    if phone and phone in buyer_by_phone:
                        matched_buyer = buyer_by_phone[phone]
                        reason = f"matched_by_phone:{phone}"
                        break
            
            if matched_buyer:
                link = OnecOwnerLink(
                    lead_ref_key=lead.owner_ref_key,
                    contractor_ref_key=matched_buyer,
                    link_reason=reason
                )
                self.db.add(link)
                links_created += 1
                
        self.db.commit()
        logger.info(f"Created {links_created} new links between leads and contractors.")

    def run_full_sync(self):
        """Run all steps of the sync pipeline."""
        try:
            self.sync_contractors()
            self.sync_contacts()
            self.generate_synthetic_contacts()
            self.link_leads_and_contractors()
            logger.info("Sync pipeline completed successfully.")
        except Exception as e:
            logger.error(f"Error during sync pipeline: {e}")
            self.db.rollback()
