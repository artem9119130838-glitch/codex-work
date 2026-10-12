# Спринт 1: Пакет внедрения On-Page оптимизации и конверсионной перелинковки Longwang.ru

> **Статус:** Готов к внедрению контент-менеджером в панель WordPress.  
> **Обоснование:** На основе аудита SiteAnalyzer (12.10.2026), выгрузки GSC (75 000+ показов за 3 мес.) и анализа Яндекс.Метрики.  
> **Цель:** Перенаправление веса и аудитории из топ-5 статей блога (24 000+ показов) на коммерческие хабы услуг, ликвидация 4 внутренних 301-редиректов и перекалибровка H1/Title.

---

## 1. Техническая зачистка внутренних ссылок (Ликвидация 301-редиректов)

SiteAnalyzer выявил утечку PageRank через ссылки на страницы, отдающие 301 Moved Permanently. Требуется открыть указанные страницы в редакторе WordPress и заменить ссылки в теле контента:

| № | Страница-донор (где править) | Старая ссылка (удалить) | Новый целевой URL (вставить) | Текст анкора |
|---|---|---|---|---|
| **1** | `https://longwang.ru/` (Главная) и `/projects/` | `https://longwang.ru/kitchen-appliances-white-ved` | **`https://longwang.ru/projects/kitchen-appliances-white-ved/`** | Карточка кейса бытовой техники |
| **2** | `/useful-articles/kupit-elektroniku-nesmotrya-na-sankczii/` | `https://longwang.ru/useful-articles/kak-dostavit-gruz-iz-kitaya/` | **`https://longwang.ru/useful-articles/aviadostavka-gruzov/`** | Доставка грузов из Китая |
| **3** | `/useful-articles/biznes-s-kitaem-s-nulya-chto-nuzhno-znat-nachinayushhemu-predprinimatelyu/` | `https://longwang.ru/useful-articles/slozhnosti-aviadostavki/` | **`https://longwang.ru/useful-articles/aviadostavka-gruzov/`** | Авиадоставка грузов |
| **4** | Внутренние ссылки на кейсы Ozon | `https://longwang.ru/projects/consolidation-7-suppliers/` | **`https://longwang.ru/projects/ozon-supply-china/`** | Консолидация поставок |

---

## 2. On-Page перекалибровка коммерческих хабов (Title, Description, H1)

Текущие сниппеты слишком общие. Ниже приведены калиброванные сниппеты с точными B2B-маркерами для SEO-плагина (Yoast SEO / Rank Math / All in One SEO):

### 2.1. Хаб «Оборудование из Китая»
* **URL:** `https://longwang.ru/supplies-services-china/equipment-from-china/`
* **Заголовок H1:** `Поставка промышленного оборудования и производственных линий из Китая`
* **Title:** `Промышленное оборудование из Китая под ключ — подбор, доставка и ВЭД | Long Wang`
* **Description:** `Прямые поставки станков, производственных линий и термооборудования из Китая для юридических лиц. Проверка завода, контракт ВЭД, оплата в юанях, белая таможня и шеф-монтаж под ключ.`

### 2.2. Хаб «Проверка поставщика в Китае»
* **URL:** `https://longwang.ru/supplies-services-china/proverka-postavshhika-v-kitae/`
* **Заголовок H1:** `Комплексный аудит фабрик и проверка надежности поставщиков в КНР`
* **Title:** `Проверка поставщика и аудит фабрик в Китае с выездом инспектора за 48 часов | Long Wang`
* **Description:** `Профессиональный аудит китайских производителей: юридическая чистота, выезд инспектора на производство, аудит оборудования и финансовой устойчивости. Официальный отчет с фото и видео за 48 часов.`

### 2.3. Хаб «Инспекция товара в Китае»
* **URL:** `https://longwang.ru/supplies-services-china/goods-check-china/`
* **Заголовок H1:** `Сюрвейерская инспекция и контроль качества партий товара в Китае`
* **Title:** `Инспекция качества и контроль отгрузки товара в Китае перед отправкой в РФ | Long Wang`
* **Description:** `Контроль качества готовой продукции в Китае: проверка партий по стандартам AQL, сверка спецификаций, контроль упаковки и опломбирование контейнеров перед оплатой остатка поставщику.`

### 2.4. Субхаб «Проверка стальных труб и металлопроката»
* **URL:** `https://longwang.ru/supplies-services-china/goods-check-china/steel-pipes-audit/`
* **Заголовок H1:** `Инспекция и неразрушающий контроль стальных труб и металлопроката в Китае`
* **Title:** `Проверка стальных труб, штоков и металлопроката в Китае: аудит геометрии и химсостава | Long Wang`
* **Description:** `Выездной аудит трубной продукции и металлопроката в Китае: спектральный анализ химсостава, ультразвуковой контроль швов, проверка толщины стенок и овальности по ГОСТ/ASTM.`

---

## 3. Конверсионные Callout-блоки для топ-5 трафиковых статей блога

По данным GSC, эти 5 статей генерируют львиную долю показов сайта (более 24 000 показов за квартал).  
В каждую статью необходимо вставить соответствующий HTML-блок после 2-го или 3-го абзаца (вводной части):

### Блок 1. Для статьи «Байер в Китае: плюсы и минусы» (9 186 показов)
* **URL:** `https://longwang.ru/useful-articles/bayer-v-kitae-plyusy-i-minusy/`
```html
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #dc2626; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">⚠️ Риски работы через частных байеров для B2B-компаний</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Перевод денег физлицам в Китае и закупка без прямого контракта создают угрозу блокировки счетов по 115-ФЗ и отсутствия юридических гарантий при поставке брака. Для закупки производственных партий и оборудования необходим официальный выездной аудит фабрики со сюрвейерским отчетом.
  </p>
  <a href="/supplies-services-china/proverka-postavshhika-v-kitae/" style="display:inline-block; background:#dc2626; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Заказать аудит завода в Китае с выездом за 48 часов →
  </a>
</div>
```

---

### Блок 2. Для статьи «Карго доставка из Китая в Россию» (6 986 показов)
* **URL:** `https://longwang.ru/useful-articles/cargo-dostavka-iz-kitaya-v-rossiyu/`
```html
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #16a34a; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">📦 Белая доставка под контракт ВЭД вместо «серого» карго</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    С 2026 года налоговый контроль цепочек поставок исключает возможность безопасной реализации товаров без ГТД и закрывающих документов с НДС. Long Wang организует прямую белую логистику оборудования и сборных грузов с официальной таможенной очисткой.
  </p>
  <a href="/supplies-services-china/belaya-dostavka-iz-kitaya/" style="display:inline-block; background:#16a34a; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Рассчитать белую доставку с ГТД и закрывающими документами →
  </a>
</div>
```

---

### Блок 3. Для статьи «Бизнес с Китаем с нуля 2026» (3 540 показов)
* **URL:** `https://longwang.ru/useful-articles/biznes-s-kitaem-s-nulya-chto-nuzhno-znat-nachinayushhemu-predprinimatelyu/`
```html
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #2563eb; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">🏭 Подбор и поставка производственного оборудования под ключ</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Запуск производства требует точного согласования ТЗ, проверки реальных мощностей завода в КНР и гарантий пусконаладки. Мы берем на себя прямые переговоры, оплату в юанях, таможню и доставку оборудования до вашего цеха.
  </p>
  <a href="/supplies-services-china/equipment-from-china/" style="display:inline-block; background:#2563eb; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Каталог решений и условия поставки оборудования →
  </a>
</div>
```

---

### Блок 4. Для статьи «Как купить электронику, несмотря на санкции» (2 102 показа)
* **URL:** `https://longwang.ru/useful-articles/kupit-elektroniku-nesmotrya-na-sankczii/`
```html
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #0284c7; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">🛡️ Белый параллельный импорт электроники и компонентов (ПП РФ № 506)</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Поставляем оригинальные микроконтроллеры, серверное оборудование и компоненты через торговые хабы в КНР с соблюдением требований законодательства РФ, нотификациями ФСБ и декларациями соответствия.
  </p>
  <a href="/supplies-services-china/parallelnyj-import-is-kitaya/" style="display:inline-block; background:#0284c7; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Условия параллельного импорта для юридических лиц →
  </a>
</div>
```

---

### Блок 5. Для статьи «Импорт аккумуляторов из Китая» (2 425 показов)
* **URL:** `https://longwang.ru/useful-articles/import-of-batteries/`
```html
<div class="b2b-callout" style="background:#f8fafc; border-left:4px solid #ea580c; padding:18px 22px; margin:28px 0; border-radius:6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
  <h4 style="margin:0 0 8px 0; color:#0f172a; font-size:17px; font-weight:700;">⚡ Инспекция партий литиевых ячеек и сертификация MSDS / UN38.3</h4>
  <p style="margin:0 0 12px 0; color:#475569; font-size:14px; line-height:1.6;">
    Импорт опасных грузов (Class 9) требует жесткой проверки внутреннего сопротивления ячеек перед отправкой и оформления паспортов безопасности. Инспекторы Long Wang проводят аудит партий аккумуляторов прямо на складе производителя в Шэньчжэне.
  </p>
  <a href="/supplies-services-china/goods-check-china/" style="display:inline-block; background:#ea580c; color:#ffffff; padding:10px 20px; border-radius:4px; text-decoration:none; font-weight:600; font-size:14px;">
    Заказать инспекцию и проверку качества партии →
  </a>
</div>
```

---

## 4. Очистка главной страницы от токсичных фраз в Schema.org FAQPage

В разметке главной страницы (`https://longwang.ru/`) обнаружен текст:  
❌ *«в обход санкций»*  

Необходимо заменить этот вопрос/ответ в блоке FAQ на главной странице:
* **Было:** *«Как вы доставляете товары в обход санкций?»*
* **Стало:** *«Как оформляется параллельный импорт промышленной продукции?»*
* **Ответ:** *«Поставки осуществляются в строгом соответствии с Постановлением Правительства РФ № 506. Мы проводим официальное таможенное оформление, оплачиваем контракт в юанях через прямые каналы в КНР и предоставляем клиенту полный пакет бухгалтерских документов и ГТД.»*
