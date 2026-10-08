import os
import json
import socket
from loguru import logger
from app.core.config import settings
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Set global default socket timeout to prevent indefinite network hanging
socket.setdefaulttimeout(30.0)

class TimelineEvent(BaseModel):
    date: str = Field(description="Дата события (YYYY-MM-DD или примерная)")
    event: str = Field(description="Описание события")

class SkuAndAmount(BaseModel):
    sku: str = Field(description="Артикул или название товара/услуги")
    amount: str = Field(description="Сумма, количество или бюджет")

class SummaryOutput(BaseModel):
    summary: str = Field(description="Краткое описание клиента и истории обращений")
    features: str = Field(description="Ключевые особенности или пожелания")
    topic: str = Field(description="Основная тема обращений")
    status: str = Field(description="Текущий статус (ждет ответа, отправлено КП, и т.д.)")
    timeline: list[TimelineEvent] = Field(description="Хронологическая цепочка событий")
    skus_and_amounts: list[SkuAndAmount] = Field(description="Найденные артикулы, товары и суммы/бюджеты")
    last_managers: list[str] = Field(description="Имена или email-ы менеджеров, отвечавших клиенту (из исходящих писем)")
    psychological_portrait: str = Field(description="Психологический портрет клиента, стиль общения, особенности")

REACTIVATION_SCHEMA = {
    "type": "object",
    "properties": {
        "email_body": {
            "type": "string",
            "description": "Текст черновика реанимационного письма"
        },
        "subject": {
            "type": "string",
            "description": "Живая B2B-тема письма (начинается с 'Re: ', содержит бренд/модель оборудования или номер заявки/спецификации, и заканчивается на 'для <Компания/Имя>'). КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ рекламные заголовки вроде 'Поставки промышленного оборудования и импорт из Китая'."
        }
    },
    "required": ["email_body", "subject"]
}

CONTACT_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "client_type": {
            "type": "string",
            "description": "Коммерческая классификация контакта: 'конечный заказчик', 'производственное предприятие', 'перепродавец', 'тендерный поставщик', 'интегратор', 'сервисная компания' или 'неизвестно'."
        },
        "client_type_explanation": {
            "type": "string",
            "description": "Краткое объяснение оценки типа контакта."
        },
        "interaction_history": {
            "type": "string",
            "description": "Краткая история общения с ЭТИМ конкретным контактным лицом/email-адресом (какие запчасти/оборудование запрашивал, о чем договаривались) БЕЗ ВОДЫ."
        },
        "reason_deal_failed": {
            "type": "string",
            "description": "Почему сделка конкретно с ЭТИМ человеком не состоялась (например: 'высокая цена', 'долгий срок поставки', 'не подошел MOQ', 'клиент перестал отвечать' или 'неизвестно')."
        },
        "return_probability": {
            "type": "string",
            "description": "Оценка вероятности вернуть контакт (Высокая / Средняя / Низкая) и причина."
        },
        "next_action_recommendation": {
            "type": "string",
            "description": "Рекомендация по обращению к ЭТОМУ человеку: о чем написать ему, какую тему или статью предложить."
        },
        "working_features": {
            "type": "string",
            "description": "Личные особенности общения этого человека (редко отвечает, требует сертификаты и т.д.)."
        },
        "timeline": {
            "type": "array",
            "description": "Хронология общения с контактом",
            "items": {
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Дата события (YYYY-MM-DD)"},
                    "event": {"type": "string", "description": "Описание события"}
                },
                "required": ["date", "event"]
            }
        },
        "skus_and_amounts": {
            "type": "array",
            "description": "Найденные артикулы, товары и суммы/бюджеты",
            "items": {
                "type": "object",
                "properties": {
                    "sku": {"type": "string", "description": "Артикул или название товара"},
                    "amount": {"type": "string", "description": "Сумма, количество или бюджет"}
                },
                "required": ["sku", "amount"]
            }
        },
        "last_managers": {
            "type": "array",
            "description": "Имена или email-ы менеджеров, отвечавших клиенту",
            "items": {"type": "string"}
        },
        "extracted_person_name": {
            "type": "string",
            "description": "Имя контактного лица (клиента), если оно уверенно и явно следует из переписки (из подписи клиента вроде 'С уважением, Александр', из обращений наших менеджеров 'Виталий, добрый день' или имени отправителя). Если имя не найдено или нет полной уверенности, вернуть пустую строку ''."
        }
    },
    "required": [
        "client_type",
        "client_type_explanation",
        "interaction_history",
        "reason_deal_failed",
        "return_probability",
        "next_action_recommendation",
        "working_features",
        "timeline",
        "skus_and_amounts",
        "last_managers",
        "extracted_person_name"
    ]
}

COMPANY_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "company_activity": {
            "type": "string",
            "description": "Сфера деятельности компании (производство чего-либо, дистрибуция, строительство и т.д.)."
        },
        "cooperation_history": {
            "type": "string",
            "description": "Сводная история сотрудничества: что заказывали, какие основные проекты вели, какие коммерческие предложения отправлялись."
        },
        "key_decision_makers": {
            "type": "string",
            "description": "Основные контактные лица и ЛПР со стороны клиента, их роли и степень влияния на принятие решений (если упомянуты)."
        },
        "unresolved_issues": {
            "type": "string",
            "description": "Проблемные зоны: срывы поставок, споры по ценам, долгие согласования, почему не покупали ранее."
        },
        "sales_potential": {
            "type": "string",
            "description": "Потенциал продаж компании и общие рекомендации: что им можно предложить из нашего ассортимента (например, ЧПУ, печи, насосы и т.д.)."
        }
    },
    "required": [
        "company_activity",
        "cooperation_history",
        "key_decision_makers",
        "unresolved_issues",
        "sales_potential"
    ]
}

COMBINED_REACTIVATION_SCHEMA = {
    "type": "object",
    "properties": {
        "contact_summary": CONTACT_SUMMARY_SCHEMA,
        "company_summary": COMPANY_SUMMARY_SCHEMA,
        "email_body": {
            "type": "string",
            "description": "Текст черновика реанимационного письма (БЕЗ темы и БЕЗ подписи менеджера - они будут сформированы автоматически)"
        }
    },
    "required": ["contact_summary", "company_summary", "email_body"]
}

class JunkOutput(BaseModel):
    is_junk: bool = Field(description="Является ли письмо спамом, рекламой, автоответом или рассылкой")
    reason: str = Field(description="Причина (например, 'рассылка', 'отбивка', 'не спам')")

class LLMService:
    def __init__(self):
        raw_keys = settings.LLM_API_KEY or ""
        self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        
        # Build unified providers list (Gemini 1 -> DeepSeek -> Gemini 2)
        self.providers = []
        
        # Add first Gemini key
        if len(self.api_keys) >= 1 and self.api_keys[0]:
            self.providers.append({
                "type": "gemini",
                "client": genai.Client(api_key=self.api_keys[0]),
                "key_masked": self.api_keys[0][:8] + "..." + self.api_keys[0][-4:]
            })
            
        # Add DeepSeek key in the middle
        if settings.DEEPSEEK_API_KEY:
            try:
                # Temporarily clean proxy env vars to avoid 'proxies' argument error in openai client
                import os
                http_proxy = os.environ.pop("http_proxy", None)
                https_proxy = os.environ.pop("https_proxy", None)
                HTTP_PROXY = os.environ.pop("HTTP_PROXY", None)
                HTTPS_PROXY = os.environ.pop("HTTPS_PROXY", None)
                
                from openai import OpenAI
                ds_client = OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com",
                    timeout=30.0
                )
                self.providers.append({
                    "type": "deepseek",
                    "client": ds_client,
                    "key_masked": "DEEPSEEK_API_KEY"
                })
                logger.info("Initializing DeepSeek Client successfully.")
                
                # Restore proxy env vars
                if http_proxy: os.environ["http_proxy"] = http_proxy
                if https_proxy: os.environ["https_proxy"] = https_proxy
                if HTTP_PROXY: os.environ["HTTP_PROXY"] = HTTP_PROXY
                if HTTPS_PROXY: os.environ["HTTPS_PROXY"] = HTTPS_PROXY
            except Exception as e:
                logger.error(f"Failed to initialize DeepSeek client: {e}")
                
        # Add remaining Gemini keys
        if len(self.api_keys) >= 2:
            for extra_key in self.api_keys[1:]:
                if extra_key:
                    self.providers.append({
                        "type": "gemini",
                        "client": genai.Client(api_key=extra_key),
                        "key_masked": extra_key[:8] + "..." + extra_key[-4:]
                    })
                    
        if not self.providers:
            logger.warning("No LLM providers configured! Adding dummy empty Gemini key.")
            self.providers.append({
                "type": "gemini",
                "client": genai.Client(api_key=""),
                "key_masked": "DUMMY_KEY"
            })
            
        # Add drafts-only Gemini keys
        raw_drafts_keys = settings.LLM_API_KEY_DRAFTS_ONLY or ""
        self.drafts_only_keys = [k.strip() for k in raw_drafts_keys.split(",") if k.strip()]
        for dk in self.drafts_only_keys:
            if dk:
                self.providers.append({
                    "type": "gemini",
                    "client": genai.Client(api_key=dk),
                    "key_masked": dk[:8] + "..." + dk[-4:],
                    "drafts_only": True
                })
                logger.info(f"Initialized drafts-only Gemini key: {dk[:8]}...{dk[-4:]}")

        self.current_provider_idx = 0
        self.exhausted_keys = set()
        logger.info(f"LLM providers chain initialized with {len(self.providers)} providers.")

    def _log_usage(self, project_name: str, provider: str, key_masked: str, model_name: str, request_type: str, prompt_tokens: int, completion_tokens: int, total_tokens: int, status: str, error_message: str = None):
        try:
            from app.db.database import SessionLocal
            from app.db.models import LLMUsageLog
            
            db = SessionLocal()
            try:
                # Estimate cost in USD
                estimated_cost = 0.0
                if provider == "deepseek":
                    # Input: $0.27 / 1M tokens, Output: $1.10 / 1M tokens
                    estimated_cost = (prompt_tokens * 0.27 / 1000000.0) + (completion_tokens * 1.10 / 1000000.0)
                
                log_entry = LLMUsageLog(
                    project_name=project_name,
                    provider=provider,
                    api_key_mask=key_masked,
                    model_name=model_name,
                    request_type=request_type,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost=estimated_cost,
                    status=status,
                    error_message=error_message
                )
                db.add(log_entry)
                db.commit()
            except Exception as e_db:
                logger.error(f"Failed to save LLM usage log in DB: {e_db}")
            finally:
                db.close()
        except Exception as e_import:
            logger.error(f"Failed to import/save LLM usage log: {e_import}")

    def _call_llm(self, prompt: str, schema, mime_type: str = "application/json", model: str = None, force_provider: str = None, request_type: str = "unknown") -> str:
        max_attempts = len(self.providers) * 2
        attempt = 0
        
        # Build active indexes list: if forced, try all matching providers first, then others as fallback
        if force_provider:
            if force_provider == "gemini_only":
                active_indexes = [i for i, p in enumerate(self.providers) if p["type"] == "gemini" and not p.get("drafts_only", False)]
            elif force_provider == "gemini":
                gemini_drafts = [i for i, p in enumerate(self.providers) if p["type"] == "gemini" and p.get("drafts_only", False)]
                gemini_reg = [i for i, p in enumerate(self.providers) if p["type"] == "gemini" and not p.get("drafts_only", False)]
                deepseek_idx = [i for i, p in enumerate(self.providers) if p["type"] == "deepseek"]
                active_indexes = gemini_drafts + gemini_reg + deepseek_idx
            elif force_provider == "deepseek":
                deepseek_idx = [i for i, p in enumerate(self.providers) if p["type"] == "deepseek"]
                gemini_drafts = [i for i, p in enumerate(self.providers) if p["type"] == "gemini" and p.get("drafts_only", False)]
                gemini_reg = [i for i, p in enumerate(self.providers) if p["type"] == "gemini" and not p.get("drafts_only", False)]
                active_indexes = deepseek_idx + gemini_drafts + gemini_reg
            elif force_provider == "deepseek_only":
                active_indexes = [i for i, p in enumerate(self.providers) if p["type"] == "deepseek"]
            else:
                if force_provider.endswith("_only"):
                    actual_provider = force_provider.replace("_only", "")
                    active_indexes = [i for i, p in enumerate(self.providers) if p["type"] == actual_provider and not p.get("drafts_only", False)]
                else:
                    matching_indexes = [i for i, p in enumerate(self.providers) if p["type"] == force_provider and not p.get("drafts_only", False)]
                    other_indexes = [i for i, p in enumerate(self.providers) if p["type"] != force_provider and not p.get("drafts_only", False)]
                    active_indexes = matching_indexes + other_indexes
        else:
            # For draft generation, try all Gemini keys first, then DeepSeek at the very end
            gemini_drafts_only = [i for i, p in enumerate(self.providers) if p.get("drafts_only", False)]
            gemini_regular = [i for i, p in enumerate(self.providers) if not p.get("drafts_only", False) and p["type"] == "gemini"]
            deepseek_idx = [i for i, p in enumerate(self.providers) if p["type"] == "deepseek"]
            
            # Simple rotation inside drafts-only and regular lists
            if gemini_drafts_only:
                n_do = len(gemini_drafts_only)
                gemini_drafts_only = [gemini_drafts_only[i % n_do] for i in range(n_do)]
            if gemini_regular:
                n_reg = len(gemini_regular)
                gemini_regular = [gemini_regular[i % n_reg] for i in range(n_reg)]
                
            if getattr(settings, "LLM_PROVIDER", "").lower() == "deepseek":
                active_indexes = deepseek_idx + gemini_drafts_only + gemini_regular
            else:
                active_indexes = gemini_drafts_only + gemini_regular + deepseek_idx
            
        active_pos = 0
        while attempt < max_attempts and active_pos < len(active_indexes):
            current_idx = active_indexes[active_pos]
            provider = self.providers[current_idx]
            ptype = provider["type"]
            client = provider["client"]
            masked = provider["key_masked"]
            if ptype == "gemini" and masked in self.exhausted_keys:
                logger.info(f"Skipping exhausted Gemini key {masked} (index {current_idx}).")
                active_pos += 1
                attempt += 1
                continue

            try:
                if ptype == "gemini":
                    raw_models = [model, "gemini-2.5-flash", "gemini-2.5-flash-lite"] if model else ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
                    models_to_try = []
                    for m in raw_models:
                        if m and m not in models_to_try:
                            models_to_try.append(m)
                            
                    last_err = None
                    success = False
                    response = None
                    
                    for model_name in models_to_try:
                        try:
                            logger.info(f"Calling Gemini API (index: {current_idx}, key: {masked}, model: {model_name})...")
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                                future = executor.submit(
                                    client.models.generate_content,
                                    model=model_name,
                                    contents=prompt,
                                    config=genai.types.GenerateContentConfig(
                                        response_mime_type=mime_type,
                                        response_schema=schema,
                                    ),
                                )
                                response = future.result(timeout=15.0)
                            
                            # Parse usage
                            prompt_tokens = 0
                            completion_tokens = 0
                            total_tokens = 0
                            if response and hasattr(response, "usage_metadata") and response.usage_metadata:
                                prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                                completion_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                                total_tokens = getattr(response.usage_metadata, "total_token_count", 0) or 0
                            
                            # Log success
                            self._log_usage(
                                project_name="email_ai",
                                provider="gemini",
                                key_masked=masked,
                                model_name=model_name,
                                request_type=request_type,
                                prompt_tokens=prompt_tokens,
                                completion_tokens=completion_tokens,
                                total_tokens=total_tokens,
                                status="success"
                            )
                            
                            success = True
                            break
                        except Exception as e_model:
                            last_err = e_model
                            err_msg = str(e_model)
                            logger.warning(f"Gemini model {model_name} failed: {err_msg}. Rotating...")
                            
                            # Log model failure
                            self._log_usage(
                                project_name="email_ai",
                                provider="gemini",
                                key_masked=masked,
                                model_name=model_name,
                                request_type=request_type,
                                prompt_tokens=0,
                                completion_tokens=0,
                                total_tokens=0,
                                status="error",
                                error_message=err_msg
                            )

                            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg or "quota" in err_msg.lower():
                                logger.warning(f"Gemini key {masked} quota exhausted (429). Marking key as exhausted and breaking model cascade.")
                                self.exhausted_keys.add(masked)
                                break
                            
                    if not success:
                        raise last_err
                        
                    self.current_provider_idx = current_idx
                    return response.text
                elif ptype == "deepseek":
                    # Check daily limit for DeepSeek (max 10/day)
                    import datetime
                    import json
                    
                    today_str = datetime.date.today().isoformat()
                    usage_file = "/app/logs/deepseek_usage.json"
                    
                    # Create directory if not exists
                    usage_dir = os.path.dirname(usage_file)
                    if not os.path.exists(usage_dir):
                        try:
                            os.makedirs(usage_dir)
                        except:
                            pass
                            
                    try:
                        if os.path.exists(usage_file):
                            with open(usage_file, "r") as uf:
                                usage_data = json.load(uf)
                        else:
                            usage_data = {}
                    except:
                        usage_data = {}
                        
                    current_count = usage_data.get(today_str, 0)
                    if current_count >= 500:
                        logger.warning(f"DeepSeek daily draft limit of 500 reached today ({today_str}). Skipping DeepSeek provider.")
                        active_pos += 1
                        attempt += 1
                        continue
                        
                    logger.info(f"Calling DeepSeek API (index: {current_idx}, model: deepseek-chat, daily_count: {current_count}/500)...")
                    response_format = {"type": "json_object"} if mime_type == "application/json" else None
                    system_prompt = "You are a professional B2B assistant. Respond in JSON format matching the requested schema."
                    if mime_type == "application/json" and schema:
                        system_prompt += f" Output JSON schema must follow strictly: {json.dumps(schema)}"
                        
                    try:
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": prompt}
                            ],
                            response_format=response_format,
                            temperature=0.1
                        )
                        
                        # Parse usage
                        prompt_tokens = 0
                        completion_tokens = 0
                        total_tokens = 0
                        if response and hasattr(response, "usage") and response.usage:
                            prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
                            completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0
                            total_tokens = getattr(response.usage, "total_tokens", 0) or 0
                            
                        # Log success
                        self._log_usage(
                            project_name="email_ai",
                            provider="deepseek",
                            key_masked=masked,
                            model_name="deepseek-chat",
                            request_type=request_type,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=total_tokens,
                            status="success"
                        )
                    except Exception as e_ds:
                        # Log DeepSeek error
                        self._log_usage(
                            project_name="email_ai",
                            provider="deepseek",
                            key_masked=masked,
                            model_name="deepseek-chat",
                            request_type=request_type,
                            prompt_tokens=0,
                            completion_tokens=0,
                            total_tokens=0,
                            status="error",
                            error_message=str(e_ds)
                        )
                        raise e_ds
                    
                    # Increment DeepSeek counter
                    try:
                        usage_data[today_str] = current_count + 1
                        with open(usage_file, "w") as uf:
                            json.dump(usage_data, uf)
                        logger.info(f"Incremented DeepSeek daily count to {current_count + 1}/10.")
                    except Exception as e_save:
                        logger.warning(f"Failed to save DeepSeek usage counter: {e_save}")
                        
                    self.current_provider_idx = current_idx
                    return response.choices[0].message.content
            except Exception as e:
                err_str = str(e)
                logger.warning(f"LLM Provider {ptype} (index: {current_idx}) failed: {err_str}. Rotating...")
                active_pos += 1
                attempt += 1
                
        raise Exception("Exhausted all configured LLM providers (Gemini/DeepSeek) due to errors or rate limits.")

    def _call_gemini(self, prompt: str, schema, mime_type: str = "application/json", model: str = "gemini-3.5-flash", request_type: str = "unknown") -> str:
        # Route to unified provider executor with DeepSeek fallback
        return self._call_llm(prompt, schema, mime_type, model, force_provider="gemini", request_type=request_type)
            
    def classify_junk_email(self, subject: str, body: str) -> dict:
        prompt = f"""
        Определи, является ли это письмо спамом, рекламой, автоматической рассылкой, уведомлением или отбивкой (автоответом).
        If это реальный запрос от клиента или переписка - это НЕ спам.
        
        Тема: {subject}
        Текст:
        {body[:2000]}
        """
        response_text = self._call_gemini(prompt, JunkOutput, request_type="junk_classification")
        return json.loads(response_text)
 
    def generate_contact_summary(self, email_text: str, is_buyer_1c: bool) -> dict:
        buyer_status = "ДА (совершал успешные сделки в 1С)" if is_buyer_1c else "НЕТ (только запросы, сделок в 1С не было)"
        prompt = f"""
        Проанализируй следующую историю переписки с конкретным сотрудником (контактным лицом) клиента и сформируй коммерческое резюме контакта.
        Резюме должно быть коротким, БЕЗ пересказа переписки, только сухая выжимка, помогающая менеджеру понять контекст общения с ЭТИМ человеком.
 
        ⚠️ КРИТИЧЕСКИ ВАЖНОЕ РАЗГРАНИЧЕНИЕ РОЛЕЙ В ПЕРЕПИСКЕ (НЕ ПЕРЕПУТАЙ КТО ЕСТЬ КТО!):
        - НАША КОМПАНИЯ (Поставщик) — это Группа Компаний «Лун-Ван» (включая ООО «Лун-Ван», ТОО «Лун-Ван», ОсОО «Лун-Ван») и ООО «Ци Линь» (Qi Lin).
          Любые менеджеры и сотрудники с домена @longwang.ru (Артем, Анна, Сауле и др.) — это МЫ (Поставщик).
        - КЛИЕНТ (Покупатель) — это компания, которая ведет переписку с нами. В их адресах НЕТ домена @longwang.ru, и в их юрлицах НЕТ слов "Лун-Ван" или "Ци Линь".
 
        ⚠️ СТАТУС КОМПАНИИ ЭТОГО КОНТАКТА В 1С:
        Клиент уже совершал покупки у нас: {buyer_status}.
        
        Ориентируйся на это при оценке! Если статус 'ДА', значит компания в целом является нашим покупателем, но конкретно этот контакт мог лично и не доводить сделку до оплаты (например, сделка закрылась через его коллегу).
 
        История переписки с этим контактом:
        {email_text}
        """
        response_text = self._call_gemini(prompt, CONTACT_SUMMARY_SCHEMA, request_type="contact_summary")
        return json.loads(response_text)

    def generate_company_summary(self, email_text: str, is_buyer_1c: bool) -> dict:
        buyer_status = "ДА (совершал успешные сделки в 1С)" if is_buyer_1c else "НЕТ (только запросы, сделок в 1С не было)"
        prompt = f"""
        Проанализируй общую историю переписки ВСЕХ сотрудников (контактов) данной компании и сформируй сводное коммерческое резюме по компании.
        Резюме должно быть коротким, без воды, только сухая выжимка по работе с предприятием в целом.

        ⚠️ КРИТИЧЕСКИ ВАЖНОЕ РАЗГРАНИЧЕНИЕ РОЛЕЙ В ПЕРЕПИСКЕ:
        - НАША КОМПАНИЯ — это ПОСТАВЩИК.
        - КЛИЕНТЫ (компания-покупатель) — это ПОКУПАТЕЛИ.

        ⚠️ СТАТУС В 1С:
        Компания совершала успешные покупки: {buyer_status}.
        Если статус равен 'ДА', значит, мы УЖЕ успешно поставляли этой компании товары/услуги. Обязательно отрази этот факт в истории сделок, даже если в переписке нет явного подтверждения оплаты.

        Сводная история переписки по всем контактам компании:
        {email_text}
        """
        response_text = self._call_gemini(prompt, COMPANY_SUMMARY_SCHEMA, request_type="company_summary")
        return json.loads(response_text)

    def generate_summary(self, email_text: str) -> dict:
        # Fallback to contact summary for backward compatibility
        return self.generate_contact_summary(email_text, False)

    def embed_text(self, text: str) -> list[float]:
        try:
            from google.genai import types
            gemini_provider = next((p for p in self.providers if p["type"] == "gemini"), None)
            if not gemini_provider:
                raise Exception("No Gemini provider found for embeddings.")
            client = gemini_provider["client"]
            result = client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    output_dimensionality=768
                )
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []

    def generate_draft(self, client_summary: str, rag_contexts: list[str]) -> str:
        contexts_str = "\n\n".join([f"--- ДОКУМЕНТ {i+1} ---\n{c}" for i, c in enumerate(rag_contexts)])
        
        prompt = f"""
        Ты — вежливый и профессиональный менеджер по продажам. Твоя задача — подготовить письмо-черновик (follow-up или ответ) для клиента.

        ИНФОРМАЦИЯ О КЛИЕНТЕ:
        {client_summary}

        ЗНАНИЯ И ПРАВИЛА КОМПАНИИ (используй их, если они релевантны):
        {contexts_str}

        Требования к письму:
        - Письмо должно быть вежливым, профессиональным и не слишком длинным.
        - Если в знаниях компании есть подходящий шаблон или инструкция, строго следуй им.
        - Если ответа нет в знаниях, напиши вежливое напоминание о себе.
        - Обращайся к клиенту на "вы" (с маленькой буквы) и не используй агрессивные призывы к покупке.

        Напиши ТОЛЬКО текст готового письма, без лишних вводных слов и комментариев.
        """
        response_text = self._call_gemini(prompt, schema=None, mime_type="text/plain", request_type="email_draft")
        return response_text.strip()

    def generate_reactivation_email(self, contact_summary: str, company_summary: str, is_buyer: bool, article_content: str, style: str = "деловой", has_sent_partnership_prelude: bool = False) -> dict:
        buyer_context = ""
        if is_buyer:
            if has_sent_partnership_prelude:
                buyer_context = "ВАЖНО: Эта компания РАНЕЕ УСПЕШНО РАБОТАЛА С НАМИ (является нашим покупателем в 1С), но мы УЖЕ писали им об этом ранее. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать прелюдии вроде «Вы и ваша компания ранее успешно работали с нами по поставкам оборудования...» или упоминать о прошлых поставках. Сразу переходи к сути дела: статья, кейс, боли клиента или предыдущая переписка."
            else:
                buyer_context = (
                    "ВАЖНО: Эта компания РАНЕЕ УСПЕШНО РАБОТАЛА С НАМИ (является нашим покупателем в 1С). "
                    "Мягко и ненавязчиво упомяни в начале письма о нашем прошлом успешном сотрудничестве (но сформулируй это своими словами!). "
                    "Категорически запрещено использовать одну и ту же шаблонную фразу для всех писем. "
                    "Примеры возможных вариантов формулировок прелюдии (используй их только как ориентир, не копируй дословно!): "
                    "- «Ранее мы успешно поставляли вашей компании оборудование, и рады были бы помочь снова...» "
                    "- «Поскольку мы ранее уже сотрудничали по поставкам оригинального оборудования...» "
                    "- «Помню, что ранее мы успешно закрыли сделку по поставкам оборудования для вашей компании...» "
                    "- «Мы ценим наше прошлое сотрудничество в сфере поставок оборудования...» "
                    "Сделай начало живым, уместным и разнообразным."
                )
        else:
            buyer_context = "ВАЖНО: Эта компания - ЛИД (сделок в 1С не было). Формулируй письмо в ключе: «Вы ранее интересовались поставками оборудования...»."

        prompt = f"""
        Ты — профессиональный B2B-менеджер по продажам.
        Твоя задача — составить персональное письмо-реанимацию для "уснувшего" клиента (с которым давно не было связи).
        Письмо должно содержать полезную информацию (статью/кейс) из нашей базы знаний, чтобы ненавязчиво напомнить о себе.

        {buyer_context}

        ИНФОРМАЦИЯ О КОНТАКТНОМ ЛИЦЕ (Саммари контакта):
        {contact_summary}

        ИНФОРМАЦИЯ О КОМПАНИИ (Сводное саммари компании):
        {company_summary}

        МАТЕРИАЛ ИЗ БАЗЫ ЗНАНИЙ (которую нужно упомянуть в письме как повод для контакта):
        {article_content}

        ПРАВИЛА И TONE OF VOICE:
        1. Письмо должно быть вежливым, профессиональным, без излишнего канцелярита.
        2. ВСЕГДА обращайся к клиенту на "вы" с маленькой буквы (вы, ваш, вам).
        3. Напиши письмо строго в стиле: {style}.
           - Если стиль "деловой": пиши вежливо, уважительно, сдержанно, профессионально.
           - Если стиль "дружелюбный": пиши тепло, партнерски, располагающе к диалогу, как хорошему знакомому.
           - Если стиль "технический": сделай упор на инженерные детали, параметры оборудования, характеристики и технологии.
        4. Плавно подведи к материалу из статьи как к полезной информации для клиента. Не нужно копировать всю статью.
        5. ⚠️ ССЫЛКИ НА МАТЕРИАЛЫ БАЗЫ ЗНАНИЙ (ОБЯЗАТЕЛЬНО В ФОРМАТЕ HTML <a>):
           Не пиши фразы вроде «если интересно, я пришлю ссылку» или «могу отправить подробности». Категорически запрещено использовать слова 'статья', 'появилась статья', 'ссылка', 'материал' как текст ссылки или писать их перед ссылкой. Вместо этого оберни ссылкой сам смысл/тему статьи, отражающий её суть.
           Тег <a> обязательно должен содержать атрибуты target="_blank" tabindex="-1".
           Пример правильной вставки: "вот пример <a href=\"https://longwang.ru/useful-articles/poleznye-sovety-dlya-uspeshnoj-dostavki-iz-kitaya/\" target=\"_blank\" tabindex=\"-1\">как минимизировать риски при импорте из КНР</a>..."
        6. Заверши письмо легким призывом к действию (Call-to-Action). Категорически запрещено использовать одну и ту же фразу "Подскажите, актуальны ли сейчас подобные задачи для вашего производства?" во всех письмах! Вместо этого выбери и органично встрой один из следующих вариантов концовок (все ссылки в теге <a> обязательно должны содержать target="_blank" tabindex="-1"):
           - Вариант А: "Вы, пожалуйста, присылайте мне запросы на оборудование (особенно, находящегося под санкциями), например&nbsp;<a href=\"https://longwang.ru/supplies-services-china/brands/\" style=\"outline: 0px; box-sizing: unset; color: rgb(0, 0, 255); text-decoration: none;\" target=\"_blank\" tabindex=\"-1\">это</a>:"
           - Вариант Б: "В любом случае, прошу Вас обращаться в дальнейшем, если потребуется поставка <a href=\"https://longwang.ru/supplies-services-china/brands/\" target=\"_blank\" tabindex=\"-1\">оборудования</a>, либо <a href=\"https://longwang.ru/supplies-services-china/dostavka-is-kitaya/\" target=\"_blank\" tabindex=\"-1\">доставка</a>, либо <a href=\"https://longwang.ru/supplies-services-china/poisk-i-podbor-postavshika/\" target=\"_blank\" tabindex=\"-1\">поиск</a> товара и <a href=\"https://longwang.ru/supplies-services-china/proverka-postavshhika-v-kitae/\" target=\"_blank\" tabindex=\"-1\">проверка</a> поставщика."
           - Вариант В: "Со всей информацией Вы можете ознакомиться на нашем <a href=\"https://longwang.ru/\" target=\"_blank\" tabindex=\"-1\">сайте</a>. Там есть описание всех услуг, шаблоны договоров, отчетов и документов. Буду рад, если Вы обратитесь повторно с каким-либо вопросом из вышеперечисленных, либо, возможно, другим, который Вам сейчас актуален."
           - Вариант Г: Любой аналогичный вежливый призыв к сотрудничеству с использованием соответствующих ссылок на сайт с target="_blank" tabindex="-1".
        7. ⚠️ ЗАПРЕТ ПРОДАЖНЫХ КЛИШЕ: Категорически запрещено использовать банальные, излишне продажные и спам-фразы вроде: «Хотели бы предложить вам сотрудничество по целому ряду...», «Наша компания предлагает вам надежное сотрудничество по поставкам...», «Предлагаем вам сотрудничество...». Письмо должно начинаться сразу с сути: статья, кейс, боли клиента или его предыдущие запросы. Никаких долгих прелюдий и предложений абстрактного "сотрудничества".
        """
        response_text = self._call_gemini(prompt, REACTIVATION_SCHEMA, request_type="reactivation_email_legacy")
        return json.loads(response_text)

    def generate_reactivation_and_summaries(self, contact_emails_text: str, company_emails_text: str, is_buyer: bool, article_title: str, article_url: str, article_desc: str, style: str = "деловой", client_name: str = "") -> dict:
        summaries = self.generate_client_intelligence_summary(contact_emails_text, company_emails_text, is_buyer, client_name)
        email_body, llm_subj = self.generate_reactivation_draft(
            contact_summary=summaries["contact_summary"],
            company_summary=summaries["company_summary"],
            is_buyer=is_buyer,
            article_title=article_title,
            article_url=article_url,
            article_desc=article_desc,
            style=style,
            client_name=client_name
        )
        return {
            "contact_summary": summaries["contact_summary"],
            "company_summary": summaries["company_summary"],
            "email_body": email_body,
            "subject": llm_subj
        }

    def generate_client_intelligence_summary(self, contact_emails_text: str, company_emails_text: str, is_buyer: bool, client_name: str = "", force_provider: str = None) -> dict:
        buyer_context = ""
        if is_buyer:
            buyer_context = "ВАЖНО: Эта компания РАНЕЕ УСПЕШНО РАБОТАЛА С НАМИ (является нашим покупателем в 1С)."
        else:
            buyer_context = "ВАЖНО: Эта компания - ЛИД (сделок в 1С не было)."

        schema = {
            "type": "object",
            "properties": {
                "contact_summary": CONTACT_SUMMARY_SCHEMA,
                "company_summary": COMPANY_SUMMARY_SCHEMA
            },
            "required": ["contact_summary", "company_summary"]
        }

        prompt = f"""
        Ты — профессиональный B2B-аналитик и менеджер по продажам.
        Твоя задача — проанализировать историю переписки с клиентом и составить подробное саммари контакта и компании.

        {buyer_context}

        ⚠️ ВАЖНЕЙШЕЕ ПРАВИЛО РОЛЕЙ (КТО МЫ И КТО КЛИЕНТ):
        - НАША КОМПАНИЯ (Поставщик) — это:
          * Группа компаний «Лун-Ван» (включая ООО «Лун-Ван», ТОО «Лун-Ван», ОсОО «Лун-Ван», ООО «Ци Линь»).
          * Наши email-домены: @longwang.ru (sales@longwang.ru, saule@longwang.ru, i_li@longwang.ru, azat@longwang.ru).
        - КЛИЕНТЫ (Покупатели) — это внешние контакты (из других доменов).
        Никогда не путай роли! В саммари контакта и компании Лун-Ван/Ци Линь ВСЕГДА должны быть описаны как НАША сторона (поставщик), а внешние контакты — как КЛИЕНТЫ (покупатели).

        ПЕРЕПИСКА С КОНКРЕТНЫМ КОНТАКТОМ:
        {contact_emails_text}

        ВСЯ ПЕРЕПИСКА С КОМПАНИЕЙ (может пересекаться):
        {company_emails_text}

        ⚠️ ТРЕБОВАНИЯ К ДЕТАЛИЗАЦИИ САММАРИ:
        - Пиши саммари максимально развернуто и подробно! Не сокращай и не ужимай информацию.
        - В 'interaction_history' и 'cooperation_history' детально опиши каждый запрос, технические параметры, причины успехов или отказов.
        - Воссоздай подробную хронологическую цепочку событий (timeline).
        """
        response_text = self._call_llm(prompt, schema, force_provider=force_provider, request_type="client_intelligence_summary")
        return json.loads(response_text)

    def generate_reactivation_draft(self, contact_summary: dict, company_summary: dict, is_buyer: bool, article_title: str, article_url: str, article_desc: str, style: str = "деловой", client_name: str = "", company_name: str = "", force_provider: str = None, previous_email_context: str = None, step_num: int = 1, has_sent_partnership_prelude: bool = False, price_objection_text: str = None) -> tuple[str, str]:
        from scripts.test_pilot_reactivation import extract_first_name, COMMON_FIRST_NAMES, SURNAME_ENDINGS
        # If client_name is empty or generic, check if extracted_person_name was resolved in contact_summary
        if (not client_name or client_name == "Коллега") and contact_summary.get("extracted_person_name"):
            cand = str(contact_summary.get("extracted_person_name", "")).strip()
            if cand and cand != "Коллега":
                fn = extract_first_name(cand)
                client_name = fn if fn else ""
        elif client_name:
            client_name = extract_first_name(client_name)

        is_cold = contact_summary.get("client_type") == "cold_lead" or "Холодный лид из 1С" in contact_summary.get("history_and_notes", "")

        buyer_context = ""
        if is_cold:
            buyer_context = (
                "ВАЖНО: По этому клиенту НЕТ истории переписки в нашей базе данных (ХОЛОДНЫЙ КОНТАКТ). "
                "Категорически запрещено писать фразы вроде «в продолжение нашего разговора», «как мы договаривались», «ранее делали расчет». "
                "Формулируй письмо как теплое нейтральное предложение сотрудничества по всему спектру наших услуг: "
                "1. Поставка оригинального оборудования санкционных брендов (SMC, Danfoss, Caterpillar, Atlas Copco, Siemens и др.). "
                "2. Поставка промышленного оборудования от проверенных китайских заводов и подбор точных аналогов европейских брендов — обязательно используй ссылку: "
                "<a href=\"https://longwang.ru/supplies-services-china/equipment-from-china/\" target=\"_blank\" tabindex=\"-1\">оборудование из Китая и аналоги</a>. "
                "3. Белая доставка и таможенное оформление грузов из Китая. "
                "4. Комплексный Аутсорсинг ВЭД (сопровождение внешнеэкономической деятельности) — обязательно встрой в текст HTML-ссылку: "
                "<a href=\"https://longwang.ru/supplies-services-china/autsorsing-ved/\" target=\"_blank\" tabindex=\"-1\">Аутсорсинг ВЭД</a>. "
                "5. Поиск производителей и технический аудит фабрик в КНР нашими инженерами. "
                "Письмо должно начинаться с нейтрального повода: перечисления наших возможностей и предложения изучить прикрепленную презентацию (она прикреплена к письму) и полезный материал ниже."
            )
        elif is_buyer:
            if has_sent_partnership_prelude:
                buyer_context = (
                    "ВАЖНО: Эта компания РАНЕЕ УСПЕШНО РАБОТАЛА С НАМИ (является нашим покупателем в 1С), "
                    "но мы УЖЕ писали им об этом ранее. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать прелюдии вроде "
                    "«Вы и ваша компания ранее успешно работали с нами по поставкам оборудования...» "
                    "или упоминать о прошлых поставках. Сразу переходи к сути дела: статья, кейс, боли клиента или предыдущая переписка."
                )
            else:
                buyer_context = (
                    "ВАЖНО: Эта компания РАНЕЕ УСПЕШНО РАБОТАЛА С НАМИ (является нашим покупателем в 1С). "
                    "Мягко и ненавязчиво упомяни в начале письма о нашем прошлом успешном сотрудничестве (но сформулируй это своими словами!). "
                    "Категорически запрещено использовать одну и ту же шаблонную фразу для всех писем. "
                    "Примеры возможных вариантов формулировок прелюдии (используй их только как ориентир, не копируй дословно!): "
                    "- «Ранее мы успешно поставляли вашей компании оборудование, и рады были бы помочь снова...» "
                    "- «Поскольку мы ранее уже сотрудничали по поставкам оригинального оборудования...» "
                    "- «Помню, что ранее мы успешно закрыли сделку по поставкам оборудования для вашей компании...» "
                    "- «Мы ценим наше прошлое сотрудничество в сфере поставок оборудования...» "
                    "Сделай начало живым, уместным и разнообразным."
                )
        else:
            buyer_context = "ВАЖНО: Эта компания - ЛИД (сделок в 1С не было). Формулируй письмо в ключе: «Вы ранее интересовались поставками оборудования...»."

        prev_context = ""
        if previous_email_context:
            prev_context = f"\n⚠️ ВАЖНО: В прошлый раз клиенту было отправлено следующее письмо. Твое новое письмо ДОЛЖНО быть непохожим на предыдущее, с другой структурой, новыми аргументами или смещенным фокусом. Предыдущее письмо:\n{previous_email_context}\n"

        link_desc = (
            f" ВАЖНО: Обязательно встрой в текст письма ссылку на статью или кейс в формате HTML. "
            f"Категорически запрещено использовать слова 'статья', 'появилась статья', 'ссылка', 'материал' как текст ссылки или писать их перед ссылкой. "
            f"Вместо этого оберни ссылкой сам смысл/тему статьи, отражающий её суть. "
            f"Тег <a> обязательно должен содержать атрибуты target=\"_blank\" tabindex=\"-1\". "
            f"Пример: 'вот пример <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">как минимизировать риски при импорте из КНР</a>'. "
            f"Ссылка должна быть органично встроена в предложение и обернута текстом! Не пиши сырую ссылку или просто текст без тега <a> с указанными атрибутами. "
        )

        company_target = company_name if company_name and company_name != "Неизвестная компания" else client_name
        company_suffix_example = f" для {company_target}" if company_target else ""

        schema = {
            "type": "object",
            "properties": {
                "email_body": {
                    "type": "string",
                    "description": f"Текст черновика реанимационного письма (БЕЗ темы и БЕЗ подписи менеджера) для Шага {step_num} воронки.{link_desc}"
                },
                "subject": {
                    "type": "string",
                    "description": (
                        f"Живая, неподдельная B2B-тема письма в стиле деловой переписки. "
                        f"Правила формирования: "
                        f"1) Тема ОБЯЗАТЕЛЬНО должна начинаться с 'Re: '. "
                        f"2) Тема должна содержать конкретные бренды/аббревиатуры оборудования (Danfoss, Siemens, SMC, Caterpillar, EVG150, Festo), артикул, номер заявки или суть спецификации («Спецификация оборудования», «Комплектующие и датчики»). "
                        f"3) В конце темы ОБЯЗАТЕЛЬНО добавь '{company_suffix_example}' (если известно название компании или имя). "
                        f"4) КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ рекламные заголовки вроде 'Поставки промышленного оборудования и импорт из Китая', 'Сотрудничество по поставкам'!"
                    )
                }
            },
            "required": ["email_body", "subject"]
        }

        contact_summary_text = json.dumps(contact_summary, ensure_ascii=False, indent=2)
        company_summary_text = json.dumps(company_summary, ensure_ascii=False, indent=2)

        templates_text = ""
        try:
            import os
            kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "40_curated_kb", "50_reactivation_templates.md"))
            if os.path.exists(kb_path):
                with open(kb_path, "r", encoding="utf-8") as f:
                    templates_text = f.read()
        except Exception:
            pass

        greeting_instruction = f"""1. ОБРАЩЕНИЕ ПО ИМЕНИ:
- Если имя "{client_name}" заполнено (не пустое и не "Коллега"), начни письмо строго с персонального обращения по имени: "{client_name}, добрый день!" или "Здравствуйте, {client_name}!".
- Если имя "{client_name}" пустое, внимательно изучи выжимку контакта и историю переписки: если ты с высокой уверенностью видишь реальное имя получателя (например, в подписи входящего письма 'С уважением, Имя', в обращении нашего менеджера к клиенту 'Имя, добрый день' или в поле extracted_person_name) — ОБЯЗАТЕЛЬНО используй это имя в приветствии: "[Имя], добрый день!".
- Если имя клиента определить невозможно или нет полной уверенности, начни строго нейтрально без имени: "Добрый день!" или "Здравствуйте!".
- Категорически запрещено использовать фамилию, отчество или полное ФИО (например, писать "Куликова Айгуль" — это грубая ошибка, пиши строго только имя "Айгуль"). Не используй псевдо-имена вроде "Коллега", "Менеджер" или названия компаний в приветствии. Никаких вступительных фраз вроде "Надеюсь, у вас все хорошо" — сразу после приветствия переходи к сути письма."""

        # Build step-specific rules (B2B Value-Driven Engineering Framework)
        step_rules = ""
        if step_num == 1:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 1 - Мягкий вопрос о потребностях):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Короткий вежливый вопрос о прошлой актуальной потребности клиента (возьми конкретный бренд или номенклатуру из выжимок). Спроси, актуальны ли еще задачи по этому бренду или оборудованию. Также органично поделись ссылкой на полезный материал по теме: <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">[смысл/суть материала]</a>. Полностью избегай слов "статья", "появилась статья", "материал", "ссылка" в тексте и ссылках. Пример правильного встраивания: "вот пример <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">как минимизировать риски при импорте из КНР</a>".
        3. ПОДПИСЬ: Заверши письмо кратким вопросом по существу в финале. Никаких фраз прощания/подписей в конце не пиши.
        """
        elif step_num == 2:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 2 - Экспертный кейс и прикладной опыт):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Напиши, что мы подготовили для клиентов прикладной кейс / аналитический разбор. Органично встрой ссылку на него из нашей базы знаний: <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">[смысл/суть материала]</a>, полностью избегая слов "статья", "появилась статья", "материал", "ссылка". В общих чертах расскажи, какую пользу он несет для производственных/закупочных задач предприятия. Ничего не продавай в лоб, делись опытом.
        3. ПОДПИСЬ: Заверши письмо легким вопросом, была ли полезна информация. Никаких фраз прощания/подписей в конце не пиши.
        """
        elif step_num == 3:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 3 - Инженерная поддержка и аудит спецификаций):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Предложи профессиональную инженерную поддержку: наш инженерный отдел в Китае готов выполнить аудит открытых спецификаций, подобрать надежные китайские аналоги европейских узлов с экономией 30–50% напрямую от производителей в КНР. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ любые упоминания "скидок 10%", "акций" и дедлайнов "до пятницы"! Органично сошлись на материал по теме: <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">[смысл/суть материала]</a>.
        3. ПОДПИСЬ: Заверши письмо вопросом: "Подскажите, есть ли сейчас открытые спецификации, требующие оптимизации бюджета или подбора альтернатив?". Никаких фраз прощания/подписей в конце не пиши.
        """
        elif step_num == 4:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 4 - Актуализация производственных планов):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Короткий деловой вопрос о статусе проектов предприятия: формируется ли сейчас план закупок/модернизации на ближайший период или проект по [оборудованию] отложен? КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ дешевые фразы "наше предложение сгорает сегодня", "последний шанс" и скидочный спам. Органично сошлись на материал: <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">[смысл/суть материала]</a>.
        3. ПОДПИСЬ: Заверши письмо вопросом: "Подскажите, планируете ли возвращаться к закупке в ближайшие месяцы?". Никаких фраз прощания/подписей в конце не пиши.
        """
        elif step_num == 5:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 5 - Завершающий статус по номенклатуре):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Уважительное обращение: уточнить, снята ли потребность по [оборудованию] с повестки или отложена на более поздний срок, чтобы мы актуализировали статус в CRM и не отвлекали вас сообщениями. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО ныть и писать "мы делали несколько попыток связаться, но не получили обратной связи".
        3. ПОДПИСЬ: Заверши письмо ровно ОДНИМ вопросом в финале: "Подскажите, проект еще в силе или задачу можно закрывать?". Никаких фраз прощания/подписей в конце не пиши.
        """
        elif step_num == 6:
            step_rules = f"""
        ⚠️ ПРАВИЛА ДЛЯ РЕАНИМАЦИОННОГО ПИСЬМА (ШАГ 6 - Уважительное партнерское завершение):
        {greeting_instruction}
        2. СУТЬ И ПОВОД ПИСЬМА: Очень корректное, уважительное финальное письмо. Напиши, что понимаешь занятость и что мы закрываем вопрос в CRM, чтобы не беспокоить. Если в будущем возникнут задачи по промышленному оборудованию, импорту из КНР или подбору аналогов — мы всегда остаемся на связи.
        3. ПОДПИСЬ: Заверши письмо фразой: "Будем рады помочь, если в дальнейшем потребуется помощь по поставкам или консультация инженеров.". Никаких фраз прощания/подписей в конце не пиши.
        """

        general_rules = f"""
        ⚠️ ОБЩИЕ ПРАВИЛА ОФОРМЛЕНИЯ ПИСЬМА:
        - СТИЛЬ: {style}. ВСЕГДА обращайся к клиенту на "вы" с маленькой буквы (вы, ваш, вам).
        - СТРОГО ОДИН ВОПРОС НА ПИСЬМО (ANTI-TAUTOLOGY INVARIANT):
          Категорически запрещено задавать более одного вопроса в письме! Запрещено дублировать один и тот же вопрос в разных абзацах письма («в чем причина паузы... подскажите, почему пауза»). Вопрос задается ровно ОДИН раз в самом конце письма.
        - КАТЕГОРИЧЕСКИЙ ЗАПРЕТ СКИДОК И АКЦИЙ:
          Запрещены любые слова «скидка 10%», «скидка», «акция», «сгорает сегодня», «дедлайн до пятницы». Тон — спокойный, партнерский, инженерно-деловой.
        - ПОДПИСЬ: Категорически запрещено писать в конце письма любые фразы привета/прощания или подписи вроде "С уважением...", "С наилучшими пожеланиями...", "Искренне ваш...", "Менеджер по продажам" или имя. Подпись будет добавлена автоматически.
        - СТРУКТУРА И АБЗАЦЫ: Разделяй текст письма на 2-3 коротких, легко читаемых абзаца. Используй двойной перевод строки (\\n\\n) между абзацами, чтобы текст не выглядел сплошным блоком.
        - ПРОБЕЛЫ ПОСЛЕ ТОЧЕК: После каждой точки, знака воскликания или знака вопроса ОБЯЗАТЕЛЬНО ставь пробел!
        - ССЫЛКИ НА КЕЙСЫ И СТАТЬИ: Любая упоминаемая статья или кейс из базы знаний должны быть оформлены как HTML-ссылка с тегом <a>. Например, используй <a href=\"{article_url}\" target=\"_blank\" tabindex=\"-1\">название статьи/кейса или фраза о теме</a>. Если ты упоминаешь кейс со Спецмашпром, ты обязан встроить ссылку: <a href="https://longwang.ru/projects/effektivnye-peregovory-i-poisk-postavshhika-promyshlennogo-oborudovaniya-v-kitae/" target="_blank" tabindex="-1">нашли в Китае завод и изготовили редкие компоненты SMC для ООО «Спецмашпром»</a>. Если упоминаешь Caterpillar/Неран, используй ссылку: <a href="https://longwang.ru/projects/postavka-originalnyh-zapchastej-dlya-spectehniki-caterpillar/" target="_blank" tabindex="-1">поставляли запчасти Caterpillar для ООО «Неран»</a>. Категорически запрещено выводить сырые URL-адреса. Все ссылки в теге <a> должны обязательно содержать атрибуты target=\"_blank\" tabindex=\"-1\".
        - ОБРАЩЕНИЕ СТРОГО ПО ИМЕНИ: Используй имя {client_name}, либо уверенно определенное имя из истории переписки. Никогда не пиши фамилию в приветствии (пиши "Айгуль", а не "Куликова Айгуль"). Если уверенности в имени нет, пиши нейтрально: "Добрый день!".
        - ОБОРУДОВАНИЕ ИЗ КИТАЯ И АНАЛОГИ: Мы поставляем не только оригинальные мировые бренды, но и промышленное оборудование напрямую от проверенных китайских заводов, а также подбираем надежные китайские аналоги европейских брендов. Если уместно в контексте письма, обязательно подчеркни эту возможность и оформи ссылкой: <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" target="_blank" tabindex="-1">оборудование из Китая и аналоги</a>.
        - КАТЕГОРИЧЕСКИЙ ЗАПРЕТ ИНФАНТИЛЬНЫХ И МЕТА-ФРАЗ (ТОЛЬКО ЧЕТКИЙ B2B-СТИЛЬ):
          Категорически запрещено писать фразы вроде: «и я хотел аккуратно уточнить», «хотел деликатно поинтересоваться», «решил аккуратно узнать», «хотел бы аккуратно спросить», «хотел ненавязчиво уточнить», «пишу, чтобы аккуратно узнать». Это выглядит неестественно, заискивающе и выдает шаблонность!
          В B2B-переписке общаются прямо, спокойно, уверенно и по делу. Сразу пиши конкретный вопрос по существу:
          * Вместо «и я хотел аккуратно уточнить, актуально ли...» пиши: «Подскажите, актуальна ли еще задача по поставке...?», «Уточните, пожалуйста, планируете ли закупку...?», «Как сейчас обстоят дела с проектом по...?», «Удалось ли решить вопрос по...?».
          * Никогда не описывай свои внутренние мыслительные процессы («я решил аккуратно спросить», «я подумал», «хотел деликатно напомнить»).
        - ЗАПРЕТ ПРОДАЖНЫХ КЛИШЕ: Категорически запрещено использовать излишне продажные и спам-фразы вроде: «Хотели бы предложить вам сотрудничество по целому ряду...», «Наша компания предлагает вам надежное сотрудничество по поставкам...», «Предлагаем вам сотрудничество...». Письмо должно начинаться сразу с сути: статья, кейс, боли клиента или его предыдущие запросы. Никаких долгих прелюдий и предложений абстрактного 'сотрудничества'.
        - ТРЕБОВАНИЯ К ТЕМЕ ПИСЬМА (НЕ РЕКЛАМА!):
          Тема письма (subject) должна выглядеть как живой рабочий ответ по реальному запросу оборудования, а не как рекламная спам-рассылка.
          * КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНЫ рекламные заголовки вроде: «Поставки промышленного оборудования и импорт из Китая», «Сотрудничество по поставкам...», «Коммерческое предложение», «Поставки оборудования и запчастей из КНР»!
          * Тема ВСЕГДА должна начинаться с «Re: ».
          * В теме должны быть реальные аббревиатуры/модели оборудования, бренды (Danfoss, Siemens, SMC, Festo, EVG150, Caterpillar), номера заявок или суть («Re: Комплектующие и датчики», «Re: Подбор аналогов по автоматике», «Re: Спецификация оборудования»).
          * В конце темы ОБЯЗАТЕЛЬНО должно быть указано «для {company_target}» (если название компании или имя известно, например: «Re: Комплектующие Danfoss для {company_target}», «Re: Спецификация оборудования для {company_target}»).
        """

        objection_rebuttal_rule = """
        - ОТРАБОТКА ВОЗРАЖЕНИЙ ИЗ ИСТОРИИ (ОБЯЗАТЕЛЬНА ДЛЯ ВСЕХ ШАГОВ 1-6):
           Если в истории переписки или параметрах зафиксированы возражения со стороны клиента (жалобы на высокие цены, «цена космос», долгие сроки или покупка у конкурентов):
           * КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать фразы «мы не получили обратной связи», «вы не ответили»! Если клиент ответил, обратная связь есть!
           * Если возражение «Дорого / цена космос / не проходим по бюджету»: прямо сошлись на его слова («Вы отмечали, что предыдущее предложение превышало бюджет...») и предложи конструктивную альтернативу: прямую работу с проверенными заводами в КНР, подбор китайских аналогов с экономией 30–50%, белую таможню и официальную гарантию.
           * Если возражение «Купили у других»: поблагодари за информацию и предложи быть надежным резервным поставщиком по расходникам или следующим проектам.
           * Если возражение «Alibaba / найдем сами / карго»: укажи, что мы берем на себя аудит фабрики инженерами в КНР, дефектовку перед отгрузкой и таможенную очистку с НДС.
        """
        if price_objection_text:
            objection_rebuttal_rule += f"""
        ⚠️ ПРЯМОЕ ЦЕНОВОЕ ВОЗРАЖЕНИЕ КЛИЕНТА:
        Клиент ранее написал: "{price_objection_text}".
        ОБЯЗАТЕЛЬНО сошлись на этот факт («Вы отмечали, что предыдущее предложение превышало бюджет...») и предложи решение по оптимизации бюджета через прямые поставки от заводов КНР и надежные аналоги. КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО писать «почему вы молчите» или «не получили ответа»!
        """

        presentation_rule = ""
        if step_num in [1, 2, 3]:
            presentation_rule = """
        - ССЫЛКА НА ПРЕЗЕНТАЦИЮ: В конце письма (перед призывом к действию) обязательно напиши фразу: "К письму прикрепляю нашу презентацию и референс-лист с кейсами поставок."
        """

        prompt = f"""
        Ты — профессиональный B2B-менеджер по продажам.
        Твоя задача — написать лаконичное, деловое B2B-письмо клиенту строго по существу, на основе аналитической выжимки по его контакту и компании.

        {buyer_context}
        {prev_context}

        ⚠️ НАШИ УСЛУГИ И ЗАСЛУГИ (Используй для усиления письма):
        При написании письма деликатно и уместно упомяни 1-2 наши сильные стороны или релевантный кейс, ЕСЛИ это подходит под тематику переписки:
        1. Прямые контракты в Китае на поставку оригинальных брендов: Cisco, SMC, Danfoss, Brevini, Caterpillar, Sick, Megger, Festo, Autonics, Atlas Copco, Siemens, Fronius, Flender.
        2. Поставка промышленного оборудования напрямую от проверенных китайских производителей и подбор точных китайских аналогов европейских брендов — обязательно с HTML-ссылкой: <a href="https://longwang.ru/supplies-services-china/equipment-from-china/" target="_blank" tabindex="-1">оборудование из Китая и аналоги</a>.
        3. Проведение оплат через наши компании в Казахстане и Кыргызстане, а также оплата товаров в КНР.
        4. Экономия на логистике за счет консолидации грузов от разных фабрик in одну отправку.
        5. Промышленный аутсорсинг: поиск производств и изготовление оборудования по чертежам заказчика.
        6. Собственные инженеры в Китае для проверки поставщиков и выездного аудита фабрик.
        7. Выдающиеся кейсы (заслуги):
           * Успешно поставили сложнейший радиационный контейнер Berthold (Швейцария) для АО «Покровский рудник».
           * Для ООО «Спецмашпром» нашли в Китае завод, который изготовил редкие снятые с производства пневмораспределители SMC по оригинальным чертежам (оформи как HTML-ссылку: <a href="https://longwang.ru/projects/effektivnye-peregovory-i-poisk-postavshhika-promyshlennogo-oborudovaniya-v-kitae/" target="_blank" tabindex="-1">нашли в Китае завод и изготовили редкие компоненты SMC для ООО «Спецмашпром»</a>).
           * Поставляли запчасти Caterpillar/Hitachi для лесозаготовительной техники в Хабаровск для ООО «Неран» (оформи как HTML-ссылку: <a href="https://longwang.ru/projects/postavka-originalnyh-zapchastej-dlya-spectehniki-caterpillar/" target="_blank" tabindex="-1">поставляли запчасти Caterpillar для ООО «Неран»</a>).
           * Поставляем сварочное оборудование Fronius для Росатома («АЭМ-Технологии»).

        ВЫЖИМКА ИЗ ИСТОРИИ КОНТАКТА:
        {contact_summary_text}

        ВЫЖИМКА ИЗ ИСТОРИИ КОМПАНИИ:
        {company_summary_text}

        МАТЕРИАЛ ИЗ БАЗЫ ЗНАНИЙ (который можно упомянуть):
        Название: {article_title}
        Ссылка: {article_url}
        Описание: {article_desc}

        ⚠️ ПРИМЕРЫ И ШАБЛОНЫ РЕАКТИВАЦИОННЫХ ПИСЕМ (Используй их краткость, тональность и структуру как ориентир):
        {templates_text}

        - РАЗНООБРАЗИЕ СТИЛЕЙ И ТОНАЛЬНОСТИ: Время от времени меняй структуру писем и тональность (деловой, дружелюбный, технический), используя в качестве ориентира структуру и лаконичность из примеров шаблонов выше. Не пиши одинаковые шаблонные фразы от клиента к клиенту. Твои письма должны звучать как индивидуальные сообщения от опытного B2B-специалиста.

        {step_rules}
        {general_rules}
        {objection_rebuttal_rule}
        {presentation_rule}
        """
        response_text = self._call_llm(prompt, schema, force_provider=force_provider, request_type=f"reactivation_draft_step{step_num}")
        res_json = json.loads(response_text)
        email_body = res_json.get("email_body", "").strip()
        llm_subject = res_json.get("subject", "").strip()

        # Sanitize greeting line (remove accidental surnames when client_name is provided)
        import re
        first_line_end = email_body.find("\n")
        if first_line_end != -1:
            first_line = email_body[:first_line_end].strip()
            rest = email_body[first_line_end:]
        else:
            first_line = email_body
            rest = ""

        # Check candidate name for greeting cleanup
        # If greeting has a name, strictly verify that it is NOT a surname and IS a known first name
        m_greet = re.match(r'^(?:здравствуйте,\s*|добрый день,\s*)([А-ЯA-Z][а-яa-z]+)[!.,]?', first_line, re.IGNORECASE)
        if not m_greet:
            m_greet = re.match(r'^([А-ЯA-Z][а-яa-z]+),\s*(?:здравствуйте|добрый день)[!.,]?', first_line, re.IGNORECASE)

        if m_greet:
            extracted_cand = m_greet.group(1).strip()
            cand_lower = extracted_cand.lower()
            # If extracted word has surname endings or is NOT in verified first names:
            if cand_lower.endswith(SURNAME_ENDINGS) or cand_lower not in COMMON_FIRST_NAMES:
                first_line = "Добрый день!"
            else:
                first_line = f"{extracted_cand.capitalize()}, добрый день!"
            email_body = first_line + rest
        elif not first_line.startswith(("Добрый день", "Здравствуйте")):
            # If LLM omitted standard greeting
            first_line = "Добрый день!\n\n" + first_line
            email_body = first_line + rest

        # Put a space after punctuation marks if followed directly by a character that should start a new sentence
        email_body = re.sub(r'([!?])([A-Za-zА-Яа-я0-9])', r'\1 \2', email_body)
        email_body = re.sub(r'(\.)([A-ZА-Я])', r'\1 \2', email_body)

        # Sanitize timid meta-phrases ("и я хотел аккуратно уточнить", "хотел деликатно поинтересоваться", etc.)
        email_body = re.sub(
            r'(?i)\b(?:и\s+)?(?:я\s+)?(?:бы\s+)?хотел(?:а)?\s+(?:бы\s+)?(?:аккуратно|деликатно|ненавязчиво)\s+',
            'хотел ',
            email_body
        )
        email_body = re.sub(
            r'(?i)\b(?:и\s+)?(?:я\s+)?решил(?:а)?\s+(?:аккуратно|деликатно|ненавязчиво)\s+',
            'решил ',
            email_body
        )
        email_body = re.sub(
            r'(?i)\b(?:аккуратно|деликатно|ненавязчиво)\s+(?:уточнить|поинтересоваться|спросить|узнать)\b',
            lambda m: m.group(0).split()[-1],
            email_body
        )

        # QUALITY SANITIZATION 1: Remove forbidden B2C discount/promo phrases
        email_body = re.sub(r'(?i)\bскидк[а-я]*\s*(?:в\s*)?(?:10%|до\s*10%)?\b', 'специальные условия', email_body)
        email_body = re.sub(r'(?i)\b(?:наше\s+)?предложение\s+(?:сгорает|истекает)\s*(?:сегодня|завтра)?\b', 'будем рады актуализировать предложение', email_body)
        email_body = re.sub(r'(?i)\bпоследний\s+шанс\b', 'возможность', email_body)

        # QUALITY SANITIZATION 2: Remove contradictions when client gave price objection
        if price_objection_text or (contact_summary and any(kw in str(contact_summary).lower() for kw in ["дорого", "цена космос", "высокая цена"])):
            email_body = re.sub(r'(?i)(?:не\s+получили\s+(?:обратной\s+связи|ответа)|вы\s+не\s+ответили)\b', 'понимаем ваши замечания по бюджету', email_body)

        # ANTI-TAUTOLOGY INVARIANT: Strictly at most ONE question mark in the entire email
        question_count = email_body.count('?')
        if question_count > 1:
            last_q_pos = email_body.rfind('?')
            prefix = email_body[:last_q_pos]
            suffix = email_body[last_q_pos:]
            # Replace all question marks in prefix with periods
            prefix_cleaned = prefix.replace('?', '.')
            email_body = prefix_cleaned + suffix

        # Clean and format LLM subject
        if llm_subject:
            # Strip multiple Re:, Fwd:, etc.
            llm_subject = re.sub(r'^(?:(?:Re|Fwd|Fw|Исх|Ответ|\[Spam\]):\s*)+', '', llm_subject, flags=re.IGNORECASE).strip()
            # Remove advertising prefixes
            llm_subject = re.sub(r'(?i)^(?:поставки промышленного оборудования и импорт из китая|поставки оборудования и запчастей из китая|сотрудничество по поставкам)\s*[-—:]?\s*', '', llm_subject).strip()
            if not llm_subject:
                llm_subject = f"Спецификация по оборудованию"
            if company_target and not re.search(r'\bдля\b', llm_subject, re.IGNORECASE):
                llm_subject = f"{llm_subject} для {company_target}"
            llm_subject = f"Re: {llm_subject}"

        return email_body, llm_subject

llm_service = LLMService()
