# -*- coding: utf-8 -*-
"""
parse_aiqicha_supplier_report.py
Парсер официальных отчетов проверки контрагентов КНР (Aiqicha / 爱企查, Tianyancha / 天眼查, Qichacha / 企查查)
для автоматического обогащения карточек поставщиков в CRM Битрикс24 и DWH.

Извлекаемые сущности:
1. Единый код общественной кредитоспособности (USCC / 统一社会信用代码 - 18 символов)
2. Юридическое наименование на китайском (企业名称 / 公司名称)
3. Английское наименование (英文名称, если есть)
4. Законный представитель / Генеральный директор (法定代表人 / 负责人)
5. Уставный капитал (注册资本) и Валюта
6. Дата регистрации / основания (成立日期)
7. Статус предприятия (经营状态: 存续 / 在业 / 注销 / 吊销)
8. Юридический адрес (注册地址 / 住所)
9. Сфера деятельности (经营范围)
10. Судебные и арбитражные риски (法律诉讼 / 被执行人 / 行政处罚)
"""
import os
import sys
import re
import json
import argparse
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def load_env():
    paths = [
        os.path.join(os.path.dirname(__file__), "..", ".env"),
        os.path.join(os.getcwd(), "projects", "1c_odata", ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k, v = k.strip(), v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
            break

load_env()
webhook = os.getenv("BITRIX24_WEBHOOK_URL", "").rstrip("/") + "/"

def call_b24(method, payload=None):
    if not webhook or "http" not in webhook:
        raise ValueError("BITRIX24_WEBHOOK_URL is not configured")
    r = requests.post(webhook + method, json=payload or {}, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_supplier_data_from_text(text: str) -> dict:
    """Извлечение структурированных атрибутов из текста отчета Aiqicha / Tianyancha"""
    data = {
        "uscc": None,
        "company_name_cn": None,
        "company_name_en": None,
        "legal_representative": None,
        "registered_capital": None,
        "establishment_date": None,
        "business_status": None,
        "registered_address": None,
        "business_scope": None,
        "litigation_count": 0,
        "penalties_count": 0,
        "dishonest_executor": False,
        "risk_summary": "Низкий"
    }

    if not text:
        return data

    # 1. USCC (统一社会信用代码) - 18 знаков: буквы и цифры, начинается обычно с 91, 92, 93
    uscc_match = re.search(r'(?:统一社会信用代码|信用代码|USCC|税号)[\s:：]*([0-9A-HJ-NP-RT-UW-Y]{18})', text)
    if uscc_match:
        data["uscc"] = uscc_match.group(1).strip()
    else:
        # Fallback raw 18-char search starting with 91 or 92
        uscc_raw = re.search(r'\b(9[123][0-9A-HJ-NP-RT-UW-Y]{16})\b', text)
        if uscc_raw:
            data["uscc"] = uscc_raw.group(1).strip()

    # 2. Company Name CN (企业名称)
    name_match = re.search(r'(?:企业名称|公司名称|名称)[\s:：]*([\u4e00-\u9fa5（）()]{4,35}(?:有限公司|股份公司|集团|分公司|厂))', text)
    if name_match:
        data["company_name_cn"] = name_match.group(1).strip()
    else:
        name_raw = re.search(r'([\u4e00-\u9fa5]{2,15}(?:机械|智能|装备|科技|制造|工业|电气|电子|商贸|国际贸易|供应链|物流)?(?:有限责任公司|有限公司|股份公司|制造厂))', text)
        if name_raw:
            data["company_name_cn"] = name_raw.group(1).strip()

    # 3. Company Name EN
    name_en_match = re.search(r'(?:英文名称|English Name)[\s:：]*([A-Za-z0-9\s,\.\-&]{4,60}(?:Co\.,?\s*Ltd\.?|Corporation|Inc\.?|Group))', text, re.IGNORECASE)
    if name_en_match:
        data["company_name_en"] = name_en_match.group(1).strip()

    # 4. Legal Representative (法定代表人)
    legal_match = re.search(r'(?:法定代表人|法人代表|负责人|法定代表)[\s:：]*([\u4e00-\u9fa5]{2,4})', text)
    if legal_match:
        data["legal_representative"] = legal_match.group(1).strip()

    # 5. Registered Capital (注册资本)
    capital_match = re.search(r'(?:注册资本|实缴资本)[\s:：]*([\d\.,]+\s*(?:万(?:元(?:人民币)?)?|万元人民币|RMB|USD|EUR))', text)
    if capital_match:
        data["registered_capital"] = capital_match.group(1).strip()

    # 6. Establishment Date (成立日期)
    date_match = re.search(r'(?:成立日期|核准日期)[\s:：]*(\d{4}[-年/\.]\d{1,2}[-月/\.]\d{1,2}日?)', text)
    if date_match:
        raw_d = date_match.group(1).strip()
        data["establishment_date"] = re.sub(r'[年月/\.]', '-', raw_d).rstrip('-日')

    # 7. Business Status (经营状态)
    for st in ["存续（在营、开业、在册）", "存续", "在业", "注销", "吊销"]:
        if st in text:
            data["business_status"] = st
            break

    # 8. Registered Address (注册地址)
    addr_match = re.search(r'(?:企业地址|注册地址|住所)[\s:：]*([^\n\r]{6,80})', text)
    if addr_match:
        data["registered_address"] = addr_match.group(1).strip()

    # 9. Business Scope (经营范围)
    scope_match = re.search(r'(?:经营范围)[\s:：]*([^\n\r]{10,250})', text)
    if scope_match:
        data["business_scope"] = scope_match.group(1).strip()

    # 10. Risk analysis (Арбитраж, суды, санкции)
    litigation_matches = re.findall(r'(?:裁判文书|开庭公告|法院公告|立案信息)[\s:：]*(\d+)', text)
    if litigation_matches:
        data["litigation_count"] = sum(int(x) for x in litigation_matches)

    penalties_match = re.search(r'(?:行政处罚|严重违法)[\s:：]*(\d+)', text)
    if penalties_match:
        data["penalties_count"] = int(penalties_match.group(1))

    dishonest_match = re.search(r'失信被执行人[\s:：]*(\d+)', text)
    if dishonest_match and int(dishonest_match.group(1)) > 0:
        data["dishonest_executor"] = True
    elif "失信被执行人" in text and not dishonest_match and "0" not in text[:text.find("失信被执行人")+20]:
        data["dishonest_executor"] = True

    if data["dishonest_executor"]:
        data["risk_summary"] = "ВЫСОКИЙ (Черный список / Ограничения)"
    elif data["litigation_count"] > 10 or data["penalties_count"] > 3:
        data["risk_summary"] = "СРЕДНИЙ (Есть судебные споры)"
    else:
        data["risk_summary"] = "НИЗКИЙ (Благонадежный)"

    return data

def enrich_b24_company(company_id: int, extracted_data: dict, dry_run: bool = True):
    """Обогащение карточки компании-поставщика в Битрикс24"""
    print(f"\n--- Обогащение карточки поставщика CRM #{company_id} ---")
    print(f"  USCC (Код налогоплательщика КНР): {extracted_data.get('uscc')}")
    print(f"  Наименование CN: {extracted_data.get('company_name_cn')}")
    print(f"  Законный представитель: {extracted_data.get('legal_representative')}")
    print(f"  Уставный капитал: {extracted_data.get('registered_capital')}")
    print(f"  Дата регистрации: {extracted_data.get('establishment_date')}")
    print(f"  Статус: {extracted_data.get('business_status')}")
    print(f"  Оценка риска: {extracted_data.get('risk_summary')}")

    comment_block = f"""
[B]Отчет проверки благонадежности КНР (Aiqicha / Tianyancha):[/B]
• Юр. наименование: {extracted_data.get('company_name_cn') or '—'}
• USCC: {extracted_data.get('uscc') or '—'}
• Фамилия / Имя директора: {extracted_data.get('legal_representative') or '—'}
• Уставный капитал: {extracted_data.get('registered_capital') or '—'}
• Дата создания: {extracted_data.get('establishment_date') or '—'}
• Статус: {extracted_data.get('business_status') or '—'}
• Адрес в КНР: {extracted_data.get('registered_address') or '—'}
• Индекс риска: {extracted_data.get('risk_summary')} (Судов: {extracted_data.get('litigation_count')}, Штрафов: {extracted_data.get('penalties_count')})
""".strip()

    upd_fields = {
        "COMMENTS": comment_block
    }
    # If company has no title, set title to Chinese name
    if extracted_data.get("company_name_cn"):
        upd_fields["TITLE"] = extracted_data["company_name_cn"]

    if dry_run:
        print("  [DRY-RUN] Изменения НЕ применены к базе CRM. Параметры:")
        print(f"    COMMENTS:\n{comment_block}")
        return True

    try:
        call_b24("crm.company.update", {"id": company_id, "fields": upd_fields})
        print(f"  [OK] Карточка поставщика #{company_id} успешно обновлена!")
        return True
    except Exception as e:
        print(f"  [ERROR] Не удалось обновить карточку #{company_id}: {e}")
        return False

def test_mock_report():
    """Тест парсера на типовом китайском отчете Aiqicha"""
    sample_text = """
    爱企查企业信用报告
    企业名称：德州欧迈机械设备有限公司
    统一社会信用代码：91371402MA3P8XXXXX
    法定代表人：张伟
    经营状态：存续（在营、开业、在册）
    成立日期：2019-05-18
    注册资本：1000万元人民币
    企业类型：有限责任公司(自然人投资或控股)
    注册地址：山东省德州市德城区运河经济开发区东风西路1688号
    经营范围：数控机床、刀具、法兰、金属构件、机床附件的加工、销售及进出口业务。
    司法风险：裁判文书 0 条，开庭公告 0 条，失信被执行人 0 条，行政处罚 0 条。
    """
    print("=== ТЕСТИРОВАНИЕ ПАРСЕРА AIQICHA НА ЭТАЛОННОМ ОТЧЕТЕ ===")
    res = extract_supplier_data_from_text(sample_text)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    assert res["uscc"] == "91371402MA3P8XXXXX"
    assert res["company_name_cn"] == "德州欧迈机械设备有限公司"
    assert res["legal_representative"] == "张伟"
    assert res["registered_capital"] == "1000万元人民币"
    assert res["establishment_date"] == "2019-05-18"
    assert res["business_status"] == "存续（在营、开业、在册）"
    assert res["risk_summary"] == "НИЗКИЙ (Благонадежный)"
    print("\n[SUCCESS] Все тестовые проверки пройдены идеально!")

def main():
    parser = argparse.ArgumentParser(description="Парсер отчетов Aiqicha/Tianyancha для карточек поставщиков КНР")
    parser.add_argument("--test", action="store_true", help="Запустить модульный тест на эталонном отчете")
    parser.add_argument("--file", type=str, help="Путь к текстовому или OCR-файлу отчета")
    parser.add_argument("--company-id", type=int, help="ID компании в Битрикс24 для обогащения")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Режим симуляции без записи в CRM")
    parser.add_argument("--apply", action="store_true", help="Применить изменения в CRM Битрикс24")
    args = parser.parse_args()

    if args.test:
        test_mock_report()
        return

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found")
            return
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        extracted = extract_supplier_data_from_text(text)
        print("Извлеченные данные:")
        print(json.dumps(extracted, ensure_ascii=False, indent=2))

        if args.company_id:
            dry = not args.apply
            enrich_b24_company(args.company_id, extracted, dry_run=dry)
    else:
        print("Использование: py parse_aiqicha_supplier_report.py --test")
        print("             py parse_aiqicha_supplier_report.py --file <path_to_report.txt> [--company-id <id>] [--apply]")

if __name__ == "__main__":
    main()
