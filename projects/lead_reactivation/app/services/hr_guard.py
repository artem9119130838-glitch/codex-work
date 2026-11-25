"""
HR Guard Service
Защита от отправки коммерческих писем и черновиков соискателям, кандидатам на работу и HR-контактам.
"""
import re
from typing import Tuple

HR_STOP_WORDS = [
    r'\bрезюме\b',
    r'\bваканси[яиюеейям]\b',
    r'\bсоискател[ьяейем]\b',
    r'\bотклик(?:а|ом|нули)?\b',
    r'\bинженер\s+по\s+качеству\b',
    r'\bqc\s+специалист\b',
    r'\bопыт\s+работы\b',
    r'\bищу\s+работу\b',
    r'\bтрудоустройств[оаеу]\b',
    r'\bсопроводительное\s+письмо\b',
    r'\bрассмотрите\s+мо[юе]\s+кандидатур[уа]\b',
    r'\bмо[её]\s+резюме\b',
    r'\bрезюме\s+во\s+вложении\b',
    r'\bрезюме\s+на\s+(?:должность|позицию|вакансию)\b',
    r'\bкандидат\s+на\s+(?:должность|вакансию)\b',
    r'\bжелаемая\s+должность\b',
    r'\bжелаемая\s+зарплата\b',
    r'\bhh\.ru\b',
    r'\bheadhunter\b',
    r'\bsuperjob\b',
    r'\brabota\.ru\b',
    r'\bavito\s+работа\b',
    r'\bзарплата\.ру\b'
]

HR_EMAIL_PREFIXES = [
    "job@", "hr@", "resume@", "cv@", "rabota@", "recruitment@", "kadry@"
]

class HRGuard:
    @staticmethod
    def is_job_seeker(
        email: str = "",
        contact_name: str = "",
        subject: str = "",
        messages_text: str = ""
    ) -> Tuple[bool, str]:
        """
        Проверяет, является ли контакт или переписка связанными с поиском работы / резюме.
        Возвращает (True, причина), если контакт является соискателем, иначе (False, "").
        """
        email_clean = (email or "").lower().strip()
        contact_name_clean = (contact_name or "").lower().strip()
        subject_clean = (subject or "").lower().strip()
        text_clean = (messages_text or "").lower().strip()

        # 1. Проверка email префиксов
        for prefix in HR_EMAIL_PREFIXES:
            if email_clean.startswith(prefix):
                return True, f"Email адрес начинается с рекрутингового префикса: {prefix}"

        # 2. Проверка темы письма
        if subject_clean:
            for pattern in HR_STOP_WORDS:
                if re.search(pattern, subject_clean, re.IGNORECASE):
                    return True, f"В теме письма найден маркер соискателя/вакансии: '{pattern}'"

        # 3. Проверка ФИО контакта в 1С
        if contact_name_clean:
            for pattern in HR_STOP_WORDS:
                if re.search(pattern, contact_name_clean, re.IGNORECASE):
                    return True, f"В ФИО контакта найден маркер соискателя/вакансии: '{pattern}'"

        # 4. Проверка текста переписки
        if text_clean:
            for pattern in HR_STOP_WORDS:
                if re.search(pattern, text_clean, re.IGNORECASE):
                    return True, f"В тексте переписки найден маркер соискателя/вакансии: '{pattern}'"

        return False, ""
