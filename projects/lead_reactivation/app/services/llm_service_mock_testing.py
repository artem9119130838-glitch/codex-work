import os
import json
from loguru import logger
from app.core.config import settings
from google import genai
from pydantic import BaseModel, Field

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

class JunkOutput(BaseModel):
    is_junk: bool = Field(description="Является ли письмо спамом, рекламой, автоответом или рассылкой")
    reason: str = Field(description="Причина (например, 'рассылка', 'отбивка', 'не спам')")

class LLMService:
    def __init__(self):
        if not settings.LLM_API_KEY:
            logger.warning("LLM_API_KEY is not set.")
        
        self.client = genai.Client(api_key=settings.LLM_API_KEY)
            
    def classify_junk_email(self, subject: str, body: str) -> dict:
        import time
        time.sleep(0.1) # Быстро для мока
        
        lower_subj = subject.lower()
        if "undelivered" in lower_subj or "failure" in lower_subj or "returned" in lower_subj or len(body.strip()) < 5:
            return {"is_junk": True, "reason": "MOCK: Отбивка или пустое письмо"}
        
        return {"is_junk": False, "reason": "MOCK: Реальное письмо"}

            
    def generate_summary(self, email_text: str) -> dict:
        import time
        time.sleep(0.1) # Быстро для мока
        
        return {
            "summary": "MOCK: Клиент интересуется промышленным оборудованием и запрашивает цены.",
            "features": "MOCK: Нужна быстрая отгрузка, просит аналоги в случае отсутствия.",
            "topic": "Запрос КП / Уточнение",
            "status": "В работе",
            "timeline": [
                {"date": "2026-07-19", "event": "Получено входящее обращение от клиента"}
            ],
            "skus_and_amounts": [
                {"sku": "MOCK-SENSOR-001", "amount": "5 шт"},
                {"sku": "MOCK-VALVE-002", "amount": "2 шт"}
            ],
            "last_managers": ["MOCK Manager"],
            "psychological_portrait": "MOCK: Деловой стиль общения, пишет коротко."
        }

    def embed_text(self, text: str) -> list[float]:
        try:
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []

    def generate_draft(self, client_summary: str, rag_contexts: list[str]) -> str:
        import time
        time.sleep(0.1) # Быстро для мока
        
        return f"""MOCK Draft:
        
Здравствуйте!

Спасибо за ваше обращение.
(Это мок-ответ, сгенерированный локально для теста. Контекст: {client_summary[:30]}...)

С уважением,
Ваш менеджер
"""

llm_service = LLMService()
