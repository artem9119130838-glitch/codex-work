# 1C OData Metadata Summary

Дата проверки: 2026-05-10

Файл:

```text
E:\Codex_Work\codex_kb\20_domains\1c\metadata\standard_odata_metadata.xml
```

## Статус

Metadata валиден и содержит бизнес-сущности. Блокер по пустому `$metadata.xml` снят.

## Итоги проверки

- XML parse: OK
- Размер: около `6.69 MB`
- EntitySet: `1232`
- EntityType: `1232`

Группы:

```text
Document = 601
Catalog = 387
AccumulationRegister = 194
InformationRegister = 42
ChartOfCharacteristicTypes = 3
AccountingRegister = 2
ChartOfAccounts = 2
ExchangePlan = 1
```

## Ключевые сущности для первого n8n этапа

Контрагенты:

```text
Catalog_Контрагенты
Catalog_Контрагенты_КонтактнаяИнформация
Catalog_ДоговорыКонтрагентов
```

Контактные лица и лиды:

```text
Catalog_КонтактныеЛица
Catalog_КонтактныеЛица_КонтактнаяИнформация
Catalog_Лиды
Catalog_Лиды_КонтактнаяИнформация
Catalog_КонтактыЛидов
```

Номенклатура:

```text
Catalog_Номенклатура
Catalog_Номенклатура_ДополнительныеРеквизиты
Catalog_НоменклатураПоставщиков
```

Документы продаж:

```text
Document_ЗаказПокупателя
Document_ЗаказПокупателя_Запасы
Document_ЗаказПокупателя_ИнформацияПоКонтрагенту
Document_СчетНаОплату
Document_СчетНаОплату_Запасы
```

Организации:

```text
Catalog_Организации
Catalog_Организации_КонтактнаяИнформация
```

## Первый безопасный API-тест

Начинать только с чтения:

```text
GET /unf/odata/standard.odata/Catalog_Контрагенты?$format=json&$top=1
GET /unf/odata/standard.odata/Catalog_КонтактныеЛица?$format=json&$top=1
GET /unf/odata/standard.odata/Catalog_Лиды?$format=json&$top=1
```

Пока не выполнять запись в 1С.

## Поля для email/contact matching

Карта полей:

```text
E:\Codex_Work\codex_kb\20_domains\1c\EMAIL_CONTACT_FIELD_MAPPING.md
```
