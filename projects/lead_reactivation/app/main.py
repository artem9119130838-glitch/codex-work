from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.schemas import EmbedRequest, EmbedResponse, DraftRequest, DraftResponse
from app.services.llm_service import llm_service
from app.db.database import get_db
from app.services.imap_service import ImapService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Stateless AI Proxy API for n8n_email_ai"
)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return credentials.credentials

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "mode": "stateless"
    }

@app.post("/api/v1/rag/embed", response_model=EmbedResponse, dependencies=[Depends(verify_token)])
def embed_text(request: EmbedRequest):
    vector = llm_service.embed_text(request.text)
    if not vector:
        raise HTTPException(status_code=500, detail="Failed to generate embedding")
    return EmbedResponse(vector=vector)

@app.post("/api/v1/drafts/generate", response_model=DraftResponse, dependencies=[Depends(verify_token)])
def generate_draft(request: DraftRequest):
    draft = llm_service.generate_draft(request.client_summary, request.rag_contexts)
    if "Ошибка генерации" in draft:
        raise HTTPException(status_code=500, detail="Failed to generate draft")
    return DraftResponse(draft_text=draft)

from app.api.schemas import ReactivationRequest, ReactivationResponse
from app.db.models import ClientIntel, OnecOwner, ClientReactivationHistory, KnowledgeBaseChunk

@app.post("/api/v1/reactivation/generate", response_model=ReactivationResponse, dependencies=[Depends(verify_token)])
def generate_reactivation(request: ReactivationRequest, db: Session = Depends(get_db)):
    # 1. Fetch contact summary
    contact = db.query(ClientIntel).filter(ClientIntel.email == request.client_email).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Client email not found")

    contact_summary = contact.ai_summary or "Нет личного саммари."

    # 2. Fetch company summary and buyer status
    is_buyer = False
    company_summary = "Нет саммари компании."
    if contact.source_id_1c:
        owner = db.query(OnecOwner).filter(OnecOwner.owner_ref_key == contact.source_id_1c).first()
        if owner:
            is_buyer = bool(owner.owner_is_buyer)
            company_summary = owner.ai_email_summary or "Нет саммари компании."

    # 3. Fetch sent articles
    history = db.query(ClientReactivationHistory).filter(ClientReactivationHistory.client_email == request.client_email).all()
    sent_urls = [h.article_url for h in history]

    # 4. Find new article
    kb_query = db.query(KnowledgeBaseChunk)
    if sent_urls:
        kb_query = kb_query.filter(KnowledgeBaseChunk.source_file.notin_(sent_urls))
    
    # Just take the first available for simplicity, in a real scenario we'd do a vector search based on client interests
    # but the TZ says "выбирается наиболее релевантная новая статья на основе интересов"
    # To do that, we can embed the contact_summary and search KB!
    article_content = "Нет подходящей статьи."
    article_url = "unknown"
    article_title = "Без темы"

    vector = llm_service.embed_text(contact_summary)
    if vector:
        # Use pgvector cosine distance
        kb_results = kb_query.order_by(KnowledgeBaseChunk.embedding.cosine_distance(vector)).limit(1).all()
        if kb_results:
            article = kb_results[0]
            article_content = article.content
            article_url = article.source_file
            article_title = article.source_file.replace(".md", "").replace("_", " ").title()
    else:
        # Fallback without vector search
        article = kb_query.first()
        if article:
            article_content = article.content
            article_url = article.source_file
            article_title = article.source_file.replace(".md", "").replace("_", " ").title()

    # 5. Generate email
    draft_data = llm_service.generate_reactivation_email(
        contact_summary=contact_summary,
        company_summary=company_summary,
        is_buyer=is_buyer,
        article_content=article_content
    )

    return ReactivationResponse(
        email_body=draft_data.get("email_body", ""),
        subject=draft_data.get("subject", ""),
        article_url=article_url,
        article_title=article_title
    )

@app.post("/api/v1/imap/rematch", dependencies=[Depends(verify_token)])
def run_auto_rematch(db: Session = Depends(get_db)):
    service = ImapService(db)
    result = service.run_rematch()
    return result
