import re
from bs4 import BeautifulSoup
from email_reply_parser import EmailReplyParser
from loguru import logger

def clean_email_body(text: str, html: str = "") -> str:
    """
    Очищает текст письма от HTML и блоков цитирования истории переписки.
    """
    raw_text = text or ""
    
    # 1. Если исходный текст совсем пустой, но есть HTML, используем его
    if not raw_text.strip() and html:
        try:
            soup = BeautifulSoup(html, "html.parser")
            raw_text = soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error parsing HTML in text_cleaner: {e}")

    if not raw_text.strip():
        return ""

    # 2. Предварительная обрезка по русским и нестандартным маркерам цитирования
    # Берем только первую часть до маркера
    split_markers = [
        r"(?i)^---+\s*Исходное сообщение\s*---+",
        r"(?i)^---+\s*Original Message\s*---+",
        r"_{20,}", # Линия из подчеркиваний (часто отделяет ответ)
        r"(?i)^\d{1,2}\s+[а-яА-Я]+\.?\s+\d{4}\s*г\..*?написал\(а\):", 
        r"(?i)^On .*? wrote:"
    ]
    
    for marker in split_markers:
        # Используем re.split, чтобы отсечь все, что ниже маркера
        parts = re.split(marker, raw_text, flags=re.MULTILINE)
        if len(parts) > 1:
            raw_text = parts[0]

    # 3. Используем EmailReplyParser для вырезания стандартных `> ` цитат
    try:
        cleaned_text = EmailReplyParser.parse_reply(raw_text)
    except Exception as e:
        logger.error(f"Error in EmailReplyParser: {e}")
        cleaned_text = raw_text

    # Убираем дублирующиеся переносы строк
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
    
    return cleaned_text
