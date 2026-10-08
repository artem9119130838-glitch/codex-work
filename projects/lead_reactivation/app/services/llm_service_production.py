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
        prompt = f"""
        Определи, является ли это письмо спамом, рекламой, автоматической рассылкой, уведомлением или отбивкой (автоответом).
        Если это реальный запрос от клиента или переписка - это НЕ спам.
        
        Тема: {subject}
        Текст:
        {body[:2000]}
        """
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JunkOutput,
            ),
        )
        return json.loads(response.text)

            
    def generate_summary(self, email_text: str) -> dict:
        prompt = f"""
        Проанализируй следующую историю переписки с клиентом:
        
        {email_text}
        
        Извлеки следующие данные:
        - Краткое резюме (summary)
        - Ключевые особенности или требования (features)
        - Основная тема (topic)
        - Текущий статус (status)
        - Хронологическую цепочку событий (timeline)
        - Все упомянутые товары, артикулы, услуги, их суммы, количество и бюджеты (skus_and_amounts)
        - Менеджеров нашей компании, которые отвечали клиенту (last_managers)
        - Психологический портрет клиента, как он общается (psychological_portrait)
        """
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SummaryOutput,
            ),
        )
        return json.loads(response.text)

    def embed_text(self, text: str) -> list[float]:
        try:
            from google.genai import types
            result = self.client.models.embed_content(
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
        
        response = self.client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()

llm_service = LLMService()
