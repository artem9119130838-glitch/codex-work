SELECT 
    c.relname AS table_name,
    d.description AS comment
FROM 
    pg_class c
LEFT JOIN 
    pg_description d ON d.objoid = c.oid
WHERE 
    c.relname LIKE '\_%' 
    AND d.description IS NOT NULL
    AND (
        d.description LIKE 'Документ.ЗаказПокупателя%'
        OR d.description LIKE 'РегистрНакопления.Продажи%'
        OR d.description LIKE 'РегистрНакопления.ДоходыИРасходы%'
        OR d.description LIKE 'РегистрНакопления.ФинансовыйРезультат%'
        OR d.description LIKE 'Справочник.Номенклатура%'
        OR d.description LIKE 'ПланСчетов.Управленческий%'
    );
