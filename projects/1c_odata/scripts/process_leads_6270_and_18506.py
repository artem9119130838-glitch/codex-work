#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
projects/1c_odata/scripts/process_leads_6270_and_18506.py
==========================================================
Обработчик для лидов #6270 (ООО «ЭКСПО ГЛАСС») и #18506 (ООО «ТИОМАТ»):
1. Лид #6270:
   - Клиент дослал конкретное ТЗ на 1 датчик Fischer (Differenzdrucktransmitter Pro-Line G004390, 1 шт.).
   - Создается Сделка (PREPARATION), Задача снабжению на Азата (срок на завтра, группа 14),
   - Привязка целевого письма #49104 к сделке, контакту #16850 и компании #12506,
   - Отправка автоответа Шаблон № 66, синхронизация с 1С:УНФ,
   - Конвертация лида в CONVERTED.
2. Лид #18506:
   - Служебное уведомление о смене почтового домена (@brsservice.ru -> @tiomat.ru).
   - БЕЗ сделки и задачи снабжению!
   - Обогащение компании/контакта, СБИС скоринг, комментарий, закрытие CONVERTED.
"""

import os
import sys
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import (
    call_b24, USER_AZAT, USER_ARTEM, GROUP_CHINA_SUPPLY,
    enrich_or_create_b24_company, enrich_or_create_b24_contact,
    send_template_66_reply, bind_lead_activities_triple,
    verify_lead_processing_result
)
from check_contractor import verify_and_enrich_contractor
from sync_leads_1c_bitrix import sync_lead_record

def process_expo_glass_lead_6270(dry_run=False):
    lead_id = 6270
    company_id = 12506  # ООО "ЭКСПО ГЛАСС" (ИНН 3328484848)
    contact_id = 16850  # Кирилл Тарасов
    contact_email = "omts4@simvolglass.ru"
    target_email_id = 49104 # Fwd: Fwd[3]: Фишер

    title_naming = 'ООО "ЭКСПО ГЛАСС", Датчик давления Fischer (1 шт.), Dig. Differenzdrucktransmitter Pro-Line G004390 (1 шт.)'

    # Дедлайн: на завтра 18:00
    cur = datetime.datetime.now()
    cur += datetime.timedelta(days=1)
    if cur.weekday() >= 5: # выходной -> понедельник
        days_ahead = 7 - cur.weekday()
        cur += datetime.timedelta(days=days_ahead)
    cur = cur.replace(hour=18, minute=0, second=0, microsecond=0)
    deadline_str = cur.strftime("%Y-%m-%dT%H:%M:%S+03:00")

    task_description = (
        "[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求 (Fischer Sensor)[/B]\n"
        "--------------------------------------------------\n"
        "• Клиент / 客户: ООО «ЭКСПО ГЛАСС» (ИНН 3328484848)\n"
        "• Оборудование / 设备名称: Цифровой датчик дифференциального давления / 数字差压变送器\n"
        "• Бренд / 品牌: Fischer (Mess- und Regeltechnik / 德国菲舍尔)\n"
        "• Модель / 型号: Dig. Differenzdrucktransmitter Pro-Line G004390\n"
        "• Количество / 数量: 1 шт. / 1 台\n"
        "• Технические параметры / 技术参数:\n"
        "  - Диапазон измерения (Messbereich Kanal 1): -100...+100 Pa\n"
        "  - Подключение процесса (Prozessanschluss): Алюминиевое штуцерное соед. для шланга 8 мм (Alu-Verschrbg. für 8 mm Schlauch)\n"
        "  - Выходной сигнал (Ausgangssignal): 4...20 mA, 3-проводной (3-Leiter)\n"
        "  - Допуск / цвет крышки (Zulassung / Gehäuse- Deckelfarbe): стандарт / антрацит-зеленый (anthrazit / grün)\n"
        "  - Параметризация (Parametrierung): Standard\n\n"
        "[B]ОРИГИНАЛЬНЫЙ ЗАПРОС КЛИЕНТА / 客户原始询价:[/B]\n"
        "Добрый день.Интересует датчик Фишер ,1шт\n\n"
        "Описание:\n"
        "Dig. Differenzdrucktransmitter\n"
        "Pro-Line\n"
        "G004390\n"
        "Messbereich Kanal 1: -100...+100 Pa\n"
        "Prozessanschluss: Alu-Verschrbg. für 8 mm Schlauch\n"
        "Ausgangssignal (Voreinstellung): 4... 20 mA, 3-Leiter\n"
        "Zulassung / Gehäuse- Deckelfarbe: keine\n"
        "Gehäuse-/Deckelfarbe anthrazit / grün\n"
        "Parametrierung: Standard\n"
        "Менеджер ОМТС ООО \"Экспо Гласс\" Тарасов Кирилл +7 (920) 923 71 69 omts4@simvolglass.ru"
    )

    bilingual_comment = (
        "[USER=20]阿扎特[/USER] Новая срочная заявка в снабжение КНР (датчик Fischer 1 шт.):\n\n"
        "请协助询价以下设备（采购需求）：\n"
        "- 品牌及型号：Fischer (菲舍尔) Dig. Differenzdrucktransmitter Pro-Line G004390\n"
        "- 数量：1 台 / 件\n"
        "- 详细参数：\n"
        "  * 量程：-100...+100 Pa\n"
        "  * 过程连接：8 mm 软管铝接头\n"
        "  * 输出信号：4...20 mA (3线制)\n"
        "  * 壳体/盖颜色：无特殊防爆认证 / 炭黑-绿色 (anthrazit/grün)\n"
        "  * 参数设置：标准 (Standard)"
    )

    print(f"\n{'='*70}\n>>> [ОБРАБОТКА ЛИДА #{lead_id}] ООО 'ЭКСПО ГЛАСС' [Режим: {'DRY-RUN' if dry_run else 'БОЕВОЙ'}]\n{'='*70}")
    print(f"1. Сделка: {title_naming}")
    print(f"2. Задача снабжению: Азат (user/20), дедлайн {deadline_str}")
    print(f"3. Целевое письмо для привязки к сделке: #{target_email_id}")

    if dry_run:
        print("[DRY-RUN] Создание сделки, задачи, привязка письма, отправка ответа, синк в 1С.")
        return

    # 1. Создание сделки
    deal_id = call_b24("crm.deal.add", {"fields": {
        "TITLE": title_naming,
        "STAGE_ID": "PREPARATION",
        "COMPANY_ID": company_id,
        "CONTACT_ID": contact_id,
        "LEAD_ID": lead_id,
        "ASSIGNED_BY_ID": USER_ARTEM,
        "OPENED": "Y"
    }})
    print(f"  [B24] Создана Сделка #{deal_id} в стадии PREPARATION")

    # 2. Создание задачи снабжению
    task_res = call_b24("tasks.task.add", {"fields": {
        "TITLE": title_naming,
        "DESCRIPTION": task_description,
        "RESPONSIBLE_ID": USER_AZAT,
        "CREATED_BY": USER_ARTEM,
        "GROUP_ID": GROUP_CHINA_SUPPLY,
        "DEADLINE": deadline_str,
        "UF_CRM_TASK": [f"D_{deal_id}"]
    }})
    task_id = task_res["task"]["id"] if isinstance(task_res, dict) and "task" in task_res else task_res
    print(f"  [B24] Создана Задача #{task_id} на Азата (Дедлайн: {deadline_str})")

    # 3. Рабочий комментарий в задачу
    call_b24("task.commentitem.add", [task_id, {"POST_MESSAGE": bilingual_comment}])
    print(f"  [B24] Добавлен рабочий комментарий снабжению в чат задачи #{task_id}")

    # 4. Triple Activity Binding
    bind_lead_activities_triple(
        lead_id,
        deal_id=deal_id,
        contact_id=contact_id,
        company_id=company_id,
        contact_email=contact_email,
        target_email_id=target_email_id,
        dry_run=False
    )
    print(f"  [B24] Письма лида привязаны: целевое #{target_email_id} к Сделке #{deal_id}, все к Контакту #{contact_id} и Компании #{company_id}")

    # 5. Автоответ Шаблон № 66
    send_template_66_reply(
        to_email=contact_email,
        original_subject="Fwd: Fwd[3]: Фишер",
        assigned_user_id=USER_ARTEM,
        is_clear_rfq_flag=True
    )
    print(f"  [MAIL] Отправлен автоответ клиенту на {contact_email}")

    # 6. Конвертация лида
    call_b24("crm.lead.update", {"id": lead_id, "fields": {
        "STATUS_ID": "CONVERTED", "COMPANY_ID": company_id, "CONTACT_ID": contact_id
    }})
    print(f"  [B24] Лид #{lead_id} успешно сконвертирован (CONVERTED)")

    # 7. Синхронизация в 1С:УНФ
    try:
        sync_1c = sync_lead_record(lead_id, dry_run=False)
        print(f"  [1C:УНФ] Результат синхронизации: {sync_1c.get('status')}, GUID: {sync_1c.get('one_c_guid')}")
    except Exception as e_1c:
        print(f"  [1C-WARN] Ошибка синхронизации 1С: {e_1c}")

    # 8. Result Self-Check
    verify_lead_processing_result(deal_id=deal_id, contact_id=contact_id, company_id=company_id, task_id=task_id)


def process_tiomat_lead_18506(dry_run=False):
    lead_id = 18506
    print(f"\n{'='*70}\n>>> [ОБРАБОТКА ЛИДА #{lead_id}] ООО 'ТИОМАТ' / 'БРС-СЕРВИС' (БЕЗ СДЕЛКИ И ЗАДАЧИ)\n{'='*70}")

    inn = "7810446484"
    company_name = 'ООО "ТИОМАТ"'
    contact_name = "Ирина Зеленкевич"
    contact_email = "zelenkevich@tiomat.ru"
    old_email = "zelenkevich@brsservice.ru"

    print(f"1. Контрагент: {company_name}, ИНН {inn}")
    print(f"2. Контакт: {contact_name} ({contact_email})")
    print(f"3. Суть: Смена почтового домена (@brsservice.ru -> @tiomat.ru)")
    print(f"4. Сделка и задача снабжению: КАТЕГОРИЧЕСКИ НЕ СОЗДАЮТСЯ")

    if dry_run:
        print("[DRY-RUN] Лид #18506: обогащение Компании/Контакта, СБИС скоринг, комментарий, CONVERTED.")
        return

    # Обогащение компании
    res_comp = enrich_or_create_b24_company(
        title=company_name, inn=inn, email=contact_email, assigned_by_id=USER_ARTEM, web="tiomat.ru"
    )
    cid = res_comp["id"]
    print(f"  [B24] Компания #{cid} ({company_name}) подготовлена.")

    # Обогащение контакта
    res_cnt = enrich_or_create_b24_contact(
        name=contact_name, email=contact_email, company_id=cid, assigned_by_id=USER_ARTEM
    )
    cnt_id = res_cnt["id"]
    print(f"  [B24] Контакт #{cnt_id} ({contact_name}) подготовлен.")

    # Скоринг СБИС
    verify_and_enrich_contractor(inn=inn, b24_company_id=cid, b24_lead_id=lead_id, email=contact_email, dry_run=False)

    # Привязка активностей к компании и контакту
    acts = call_b24("crm.activity.list", {"filter": {"OWNER_TYPE_ID": 1, "OWNER_ID": lead_id}}) or []
    for a in acts:
        aid = a.get("ID")
        call_b24("crm.activity.binding.add", {"activityId": aid, "entityTypeId": 4, "entityId": cid})
        call_b24("crm.activity.binding.add", {"activityId": aid, "entityTypeId": 3, "entityId": cnt_id})
        call_b24("crm.activity.update", {"id": aid, "fields": {"COMPLETED": "Y", "STATUS": 2}})

    # Добавление таймлайн-комментария
    call_b24("crm.timeline.comment.add", {
        "fields": {
            "ENTITY_ID": cid, "ENTITY_TYPE": "company",
            "COMMENT": f"[Служебное уведомление]\nКлиент уведомил о смене почтового домена. Новый рабочий адрес сотрудника ({contact_name}): {contact_email} (ранее: {old_email})."
        }
    })

    # Конвертация лида
    call_b24("crm.lead.update", {"id": lead_id, "fields": {
        "STATUS_ID": "CONVERTED", "COMPANY_ID": cid, "CONTACT_ID": cnt_id
    }})
    print(f"  [B24] Лид #{lead_id} успешно сконвертирован (CONVERTED)")


if __name__ == "__main__":
    is_dry = "--dry-run" in sys.argv
    process_expo_glass_lead_6270(dry_run=is_dry)
    process_tiomat_lead_18506(dry_run=is_dry)
