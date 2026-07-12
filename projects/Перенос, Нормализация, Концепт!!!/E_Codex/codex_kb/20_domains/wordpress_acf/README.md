# Domain: WordPress / ACF

## Scope

This is a secondary but recurring work area around WordPress pages, ACF fields, templates, and snippets.

## Known site

```text
https://longwang.ru
```

Confirmed live DB from previous export:

```text
DB_NAME = host1847090_lwmain
table_prefix = wp_
```

## Important lesson

Always confirm the live database through `wp-config.php` before editing/importing/querying. Multiple databases were discovered, and guessing the live one is unsafe.

## Repeated workflow

1. Confirm live `wp-config.php`.
2. Confirm target page by ID or slug.
3. Count `wp_postmeta`.
4. Compare suspicious page with a known working page on same template.
5. Check ACF field group/template match.
6. Prefer a clean new page if a page is contaminated by mixed field groups.

## Known page IDs / slugs from exports

- Fronius: `7011`, `fronius-equipment-supply`
- Baumer: `9435`, `baumer-sensors-order`
- Bitzer: `8823`, `bitzer-compressors-parts`
- Mattei: `8840`, `mattei-rotors-compressors`
- SMC: `1460`, `smc-product-supplies`
- Megger: `2340`, `megger-product-supplies`
- Parent hub observed: `4503`
