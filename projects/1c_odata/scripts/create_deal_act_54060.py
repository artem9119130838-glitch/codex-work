import os
import sys

sys.path.insert(0, os.path.abspath(r"C:\Codex\projects\1c_odata\scripts"))
from process_b24_inbound_leads import (
    call_b24,
    create_b24_deal,
    create_b24_supply_task,
    send_b24_task_chat_message,
    build_supply_task_chat_message,
    upload_file_to_b24_disk,
    send_template_66_reply,
    FOLDER_CHINA_SUPPLY_DISK,
    GROUP_CHINA_SUPPLY,
    USER_ARTEM
)
USER_LI_YUNAN = 84
import requests

def main():
    act_id = 54060
    act = call_b24("crm.activity.get", {"id": act_id})
    if not act:
        print("Activity 54060 not found")
        return

    company_id = 12730
    contact_id = 17442
    resp_id = USER_LI_YUNAN # 84
    deadline_str = "2026-11-20T18:00:00+03:00"

    title_naming = 'ООО "СТРОЙКОМПЛЕКС 78", RUF 阀门清单 (7项), RUF 阀门清单, Клапаны RUF (7 поз., 7 шт.)'
    deal_id = create_b24_deal(title_naming, company_id, contact_id, assigned_by_id=USER_ARTEM, stage_id="PREPARATION")
    print(f"Created Deal #{deal_id}")

    # Привязка письма 54060 к новой Сделке
    call_b24("crm.activity.binding.add", {"activityId": act_id, "entityTypeId": 2, "entityId": deal_id})
    call_b24("crm.activity.update", {"id": act_id, "fields": {"OWNER_TYPE_ID": 2, "OWNER_ID": deal_id, "COMPLETED": "Y", "STATUS": 2}})

    # Загрузка чертежей на Диск группы 14
    supply_disk_ids = []
    attachments_lines = []
    files = act.get("FILES", [])
    for f in files:
        fid = f.get("id")
        df = call_b24("disk.file.get", {"id": fid})
        fname = (df and df.get("NAME")) or f"RUF_valve_{fid}.pdf"
        dl_url = df.get("DOWNLOAD_URL") if df else None
        if dl_url:
            try:
                r_dl = requests.get(dl_url, timeout=25)
                if r_dl.status_code == 200:
                    tmp_p = os.path.join(os.environ.get("TEMP", r"C:\Temp"), fname)
                    with open(tmp_p, "wb") as f_tmp:
                        f_tmp.write(r_dl.content)
                    uploaded_id = upload_file_to_b24_disk(tmp_p, FOLDER_CHINA_SUPPLY_DISK)
                    if uploaded_id:
                        supply_disk_ids.append(uploaded_id)
                        attachments_lines.append(f"- [URL=https://b24-g4wfjq.bitrix24.ru/disk/showFile/{uploaded_id}/]{fname}[/URL]")
                    if os.path.exists(tmp_p):
                        os.remove(tmp_p)
            except Exception as e:
                print(f"Error file {fname}: {e}")

    download_links_chat = "\n".join(attachments_lines) if attachments_lines else "Вложения доступны в карточке задачи"

    task_description = f"""[B]ТЕХНИЧЕСКОЕ ЗАДАНИЕ НА ЗАКУПКУ / 采购技术要求[/B]
--------------------------------------------------
• Сделка / 商机: [URL=https://b24-g4wfjq.bitrix24.ru/crm/deal/details/{deal_id}/]Сделка #{deal_id}[/URL]
• Оборудование / 设备名称: RUF 阀门清单 (7项)
• Бренд / 品牌: RUF
• Модель / 型号: 1020858, 1020834, 1020835, 1020837, 1020860, 1020838, 1020798
• Количество / 数量: 7 шт. (7 unit / 7台)
• Допустимость аналога / 同等替代品: [B]СТРОГО ОРИГИНАЛ / 仅限原装正品 (Аналоги не запрашивались)[/B]

[B]ОРИГИНАЛЬНЫЙ ТЕКСТ ЗАПРОСА КЛИЕНТА / 客户原始询价:[/B]
Добрый день! Прошу выслать КП на клапаны:
Клапан 1020858 RUF – 1 шт.
Клапан 1020834 RUF – 1 шт.
Клапан 1020835 RUF – 1 шт.
Клапан 1020837 RUF – 1 шт.
Клапан 1020860 RUF – 1 шт.
Клапан 1020838 RUF – 1 шт.
Клапан 1020798 RUF – 1 шт.

[B]СПЕЦИФИКАЦИЯ И ВЛОЖЕНИЯ / 附件及图纸:[/B]
{download_links_chat}"""

    task_id = create_b24_supply_task(
        title=title_naming,
        deal_id=deal_id,
        description=task_description,
        responsible_id=resp_id,
        group_id=GROUP_CHINA_SUPPLY,
        deadline_tomorrow=True,
        file_ids=supply_disk_ids
    )
    print(f"Created Task #{task_id}")

    chat_msg = build_supply_task_chat_message(
        azat_id=resp_id,
        cn_nomenclature="RUF 阀门清单 (1020858, 1020834, 1020835, 1020837, 1020860, 1020838, 1020798 - 共7台)",
        brand="RUF",
        model="1020858, 1020834, 1020835, 1020837, 1020860, 1020838, 1020798",
        quantity="7 шт. (7台)",
        equivalents_allowed=False,
        download_links_chat=download_links_chat,
        clean_inquiry="Клапаны RUF (7 позиций по 1 шт.) согласно приложенным чертежам"
    )
    send_b24_task_chat_message(task_id, chat_msg)

if __name__ == "__main__":
    main()
