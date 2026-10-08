import json
import os
import argparse
import hashlib
import time
from datetime import datetime
from loguru import logger
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.models import KnowledgeBaseChunk
from app.db.database import get_db

def load_jsonl(filepath):
    chunks = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    chunks.append(json.loads(line))
                except Exception as e:
                    logger.warning(f"Failed to parse line in {filepath}: {e}")
    return chunks

def calculate_md5(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Vectorize and upload RAG chunks to database using Gemini incrementally")
    parser.add_argument("--in-dir", type=str, default="50_rag_tools/out", help="Directory containing .jsonl chunks")
    parser.add_argument("--sleep-ms", type=int, default=1000, help="Delay between API calls in ms to avoid rate limits")
    args = parser.parse_args()

    api_keys = [k.strip() for k in settings.LLM_API_KEY.split(",") if k.strip()]
    if not api_keys:
        logger.error("No valid API keys found in LLM_API_KEY.")
        return
        
    if not os.path.exists(args.in_dir):
        logger.error(f"Input directory not found: {args.in_dir}")
        return

    jsonl_files = [f for f in os.listdir(args.in_dir) if f.endswith('.jsonl')]
    if not jsonl_files:
        logger.info(f"No .jsonl files found in {args.in_dir}")
        return

    logger.info(f"Found {len(jsonl_files)} files to vectorize.")

    db: Session = next(get_db())
    
    try:
        total_chunks = 0
        new_chunks = 0
        skipped_chunks = 0
        
        for filename in jsonl_files:
            filepath = os.path.join(args.in_dir, filename)
            logger.info(f"Processing {filepath}...")
            chunks = load_jsonl(filepath)
            
            for chunk in chunks:
                category = chunk.get("category", "general")
                content = chunk.get("content", "").strip()
                source_file = filename
                
                if not content:
                    continue
                
                total_chunks += 1
                content_hash = calculate_md5(content)
                
                # Check if chunk already exists
                existing = db.query(KnowledgeBaseChunk).filter_by(content_hash=content_hash).first()
                if existing:
                    skipped_chunks += 1
                    continue
                
                # Get embedding via Gemini with rotation
                embedding = None
                for key_idx, current_key in enumerate(api_keys):
                    try:
                        client = genai.Client(api_key=current_key)
                        response = client.models.embed_content(
                            model="gemini-embedding-001",
                            contents=content,
                            config=types.EmbedContentConfig(
                                output_dimensionality=768
                            )
                        )
                        embedding = response.embeddings[0].values
                        break # Success!
                    except Exception as api_err:
                        logger.warning(f"Key index {key_idx} failed for chunk {content_hash}: {api_err}")
                        if key_idx == len(api_keys) - 1:
                            logger.error(f"Exhausted all API keys for chunk {content_hash}")
                            
                if not embedding:
                    logger.error(f"Skipping chunk {content_hash} due to embedding generation failure.")
                    continue
                    
                try:
                    kb_chunk = KnowledgeBaseChunk(
                        source_file=source_file,
                        category=category,
                        content=content,
                        content_hash=content_hash,
                        embedding=embedding,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(kb_chunk)
                    db.commit() # Commit each to save progress
                    new_chunks += 1
                    
                    logger.debug(f"Inserted new chunk {content_hash} ({new_chunks} added)")
                    
                    # Throttle to avoid rate limits
                    if args.sleep_ms > 0:
                        time.sleep(args.sleep_ms / 1000.0)
                        
                except Exception as db_err:
                    logger.error(f"Database Error inserting chunk {content_hash}: {db_err}")
                    db.rollback()
                    # optionally continue to next chunk
                
        logger.info(f"Vectorization finished. Total chunks: {total_chunks}. New: {new_chunks}. Skipped: {skipped_chunks}.")
        
    except Exception as e:
        logger.error(f"Error during vectorization: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
