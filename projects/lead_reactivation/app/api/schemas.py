from pydantic import BaseModel, Field

class EmbedRequest(BaseModel):
    text: str = Field(description="Текст для векторизации")

class EmbedResponse(BaseModel):
    vector: list[float] = Field(description="Векторное представление текста (768 размерность)")

class DraftRequest(BaseModel):
    client_summary: str = Field(description="Саммари по клиенту (тема, статус, приоритет)")
    rag_contexts: list[str] = Field(description="Список релевантных текстовых блоков из базы знаний")

class DraftResponse(BaseModel):
    draft_text: str = Field(description="Сгенерированный черновик письма")

class ReactivationRequest(BaseModel):
    client_email: str = Field(description="Email клиента для реанимации")

class ReactivationResponse(BaseModel):
    email_body: str = Field(description="Текст черновика")
    subject: str = Field(description="Тема письма")
    article_url: str = Field(description="URL статьи из базы знаний")
    article_title: str = Field(description="Заголовок статьи")
