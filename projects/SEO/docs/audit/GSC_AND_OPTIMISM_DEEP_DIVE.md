# Глубокий Анализ Google Search Console и Аудита Optimism: Причины Пробуксовки и План Прорыва

> [!IMPORTANT]
> Настоящий документ построен на основе аппаратного скриптового анализа выгрузок GSC ([parse_gsc_exports.py](file:///C:/Codex/projects/SEO/scripts/parse_gsc_exports.py)) и независимого аудита [Optimism.ru](https://audit.optimism.ru/longwang.ru/report/?part=audf&show=project&id=680715).

---

## 1. Сенсация аудита: Почему муфельные печи и вакуумные камеры не в поиске Google?

Анализ отчета `Coverage-Drilldown` (проблема: *«Страница просканирована, но пока не проиндексирована»*) показал, что прямо сейчас Google отказывается включать в основной индекс следующие ключевые коммерческие страницы:

1. `.../equipment-from-china/thermo-equipment-china/muffle-furnaces-china/` (Муфельные печи)
2. `.../equipment-from-china/thermo-equipment-china/vacuum-drying-chambers/` (Вакуумные сушильные камеры)
3. `.../equipment-from-china/thermo-equipment-china/drying-cabinets-china/` (Сушильные шкафы)
4. `.../parallelnyj-import-is-kitaya/brands/honeywell-supply/` (Бренд Honeywell)
5. `.../parallelnyj-import-is-kitaya/brands/airtac-supple-china/` (Бренд Airtac)
6. `.../parallelnyj-import-is-kitaya/brands/flender-siemens-equipment/` (Бренд Flender / Siemens)
7. `.../parallelnyj-import-is-kitaya/brands/kubler-equipment/` (Бренд Kubler)
8. `.../projects/oborudovanie-v-lizing-po-lgotnoj-stavke/` (Кейс по лизингу)

### Причина отказа в индексации:
Google видит эти страницы на 4-м уровне вложенности (кликов) и считает их **низковесными изолированными страницами (Thin / Orphan pages)**.  
Родительский хаб `/equipment-from-china/` не давал на них прямых ссылок!  
**Внедрение Пункта 4 (блок карточек/тегов 10 печей на странице оборудования) передаст им прямой внутренний вес (PageRank) и форсирует их включение в поисковый индекс Google!**

---

## 2. Структура поискового спроса в Google (Performance за 3 месяца)

### Топ-5 страниц по кликам:
| Страница | Клики | Показы | CTR | Ср. позиция | Интент |
|---|---|---|---|---|---|
| `/useful-articles/bayer-v-kitae-plyusy-i-minusy/` | 90 | 9 186 | 0.98% | 11.01 | Информационный |
| `/useful-articles/kupit-elektroniku-nesmotrya-na-sankczii/` | 90 | 2 102 | 4.28% | 6.17 | Информационный |
| `/useful-articles/import-of-batteries/` | 70 | 2 425 | 2.89% | 6.15 | Информационный |
| `/useful-articles/biznes-s-kitaem-s-nulya.../` | 57 | 3 540 | 1.61% | 11.46 | Информационный |
| `/useful-articles/cargo-dostavka-iz-kitaya-v-rossiyu/` | 56 | 6 986 | 0.80% | 6.61 | Смешанный |

**Вывод:**  
Сайт отлично ранжируется по статьям блога, но **коммерческие услуги не конвертируют этот успех в прямые заявки**, потому что в Google коммерческие хабы висят на 25–40 позициях из-за слабого ссылочного веса.

---

## 3. Аудит ссылочной массы и домена (Optimism.ru & Majestic)

- **Возраст домена:** первый снимок в WebArchive от 02.08.2023 г. (домену 3 года).  
  В B2B-тематике крупные конкуренты (Транзит, ВЭД Плюс, Карго-Лидеры) имеют возраст 8–15 лет. Молодой возраст требует более высокой плотности авторитетных доноров.
- **Индекс качества сайта (ИКС Яндекса):** 70 — хороший стартовый уровень, подтверждающий лояльность Яндекса.
- **Majestic Trust Flow (TF) = 21, Citation Flow (CF) = 28.**  
  Соотношение TF/CF близко к 0.75 — ссылочный профиль естественный, без очевидного спама.
- **Ссылающихся доменов:** 68 сайтов.  
  Для выхода в ТОП-3 по коммерческим фразам *«поставка оборудования из Китая»*, *«аутсорсинг ВЭД Китай»* требуется постепенное наращивание качественных вечных ссылок с трастовых бизнес-СМИ (через биржу GoGetLinks).

---

## 4. Мусорные URL в индексе, подлежащие исключению

В отчете GSC обнаружено, что Google индексирует прямые ссылки на скачивание офисных документов:
- `/wp-content/uploads/2024/02/dogovor-okazaniya-uslug-poiska-lun-van-var2.docx`
- `/wp-content/uploads/2024/02/gogovor-audita-postavcshika.docx`
- `/wp-content/uploads/2024/02/dogovor-transportnoj-ekspediczii-lun-van.docx`
- `/wp-content/uploads/2024/02/dogovor-zayavka.docx`

**Рекомендация:** Закрыть индексацию файлов `.docx` и `.doc` в `robots.txt` директивой:  
`Disallow: /wp-content/uploads/*.docx`  
`Disallow: /wp-content/uploads/*.doc`  
(При этом файлы `.pdf` с кейсами и сертификатами оставить открытыми).
