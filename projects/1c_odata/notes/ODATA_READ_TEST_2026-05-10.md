# OData Read Test

Дата проверки: 2026-05-10

Папка с файлами:

```text
E:\Codex_Work\projects\1c_odata\incoming\odata-tests
```

## Результат

Все 6 read-only запросов вернули валидный JSON. Размер файлов маленький, потому что использовался `$top=1`.

## Проверенные файлы

```text
01_counterparties.json              OK, value count = 1
02_leads.json                       OK, value count = 1
03_lead_contacts.json               OK, value count = 1
04_lead_contacts_info.json          OK, value count = 1
05_contact_persons.json             OK, value count = 1
06_counterparties_contact_info.json OK, value count = 1
```

## Вывод

1С OData read-only доступ работает для базовых сущностей:

```text
Catalog_Контрагенты
Catalog_Лиды
Catalog_КонтактыЛидов
Catalog_КонтактыЛидов_КонтактнаяИнформация
Catalog_КонтактныеЛица
Catalog_Контрагенты_КонтактнаяИнформация
```

Следующий шаг: создать/проверить PostgreSQL базу `marketing_db` и таблицы для хранения результатов считывания и сопоставления писем.
