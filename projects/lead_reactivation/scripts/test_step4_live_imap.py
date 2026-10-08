import os
import sys
from loguru import logger

# Add app to path
sys.path.insert(0, '/app')

from app.services.email_composer import search_live_imap_incoming

def main():
    test_emails = [
        "yuriy.emkin@multonpartners.com",
        "kopyrin@iptechnix.com",
        "d.supkareva@himkompleks.ru"
    ]
    
    for email in test_emails:
        logger.info(f"Testing live IMAP search for {email}...")
        subj, quote, msg_id = search_live_imap_incoming(email)
        logger.info(f"Result for {email}:")
        logger.info(f"  Subject: {subj}")
        logger.info(f"  Orig Message-ID: {msg_id}")
        logger.info(f"  Quote length: {len(quote) if quote else 0} chars")
        if quote:
            logger.info(f"  Quote snippet: {quote[:150]}...")
        print("-" * 50)

if __name__ == "__main__":
    main()
