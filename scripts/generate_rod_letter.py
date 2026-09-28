# -*- coding: utf-8 -*-
"""
Script to generate the updated formal trilingual cover letter (RU / CN / EN)
in Markdown and Word (.docx) format for Factory & David (Alexda).
Includes the critical STOP-ORDER on grinding to 179.6 mm and the mandatory
Groove Bottom ID measurements required by technologist Mikhail (LV Hydramax).
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

LETTER_MD_CONTENT = """# Официальное предписание заводу и партнерам (Актуализация на 28.09.2026)
## 关于紧急暂停179.6磨削、强制密封槽底径复测、技术澄清及最终发货前要求的函
### Formal Technical Notice: Urgent Stop-Order on Ø179.6 Grinding, Mandatory Groove Bottom ID Measurement & Acceptance Conditions

**Кому / 收件人:** Дэвиду (*DEZHOU ALEXDA*), Руководству завода, Инспектору ОТК Ван Сююй (汪秀玉)  
**От кого / 发件人:** Российская проектная группа (Договор поставки оборудования № 62230426)  
**Дата / 日期:** 28 сентября 2026 г. / 2026年9月28日  
**Тема / 主题:** СТОПОР шлифовки до Ø179.6 мм, запрос замеров дна канавок, статус спасения штоков и условия отгрузки  

---

### 🚨 ВАЖНЕЙШЕЕ ПРЕДПИСАНИЕ: СТОПОР НА ШЛИФОВКУ ДО Ø179.6 ММ!
### 🚨 紧急暂停指令：严禁擅自将外圆磨削至 179.6 mm！
### 🚨 URGENT STOP-ORDER: STRICT PROHIBITION ON GRINDING TO Ø179.60 MM!

Завод в отчете от 27.09.2026 («Report of the.docx») предложил:  
> *"If you agree this place reduce to Φ179.9（-0.05～-0.096）的改到179.6 . Then, we will use a machine to polish it. That will remove the chrome layer."*

**ОФИЦИАЛЬНОЕ РЕШЕНИЕ ТЕХНОЛОГОВ И ИНЖЕНЕРОВ КЛИЕНТА:**  
**КАТЕГОРИЧЕСКИЙ СТОПОР! СТРОГО ЗАПРЕЩЕНО ШЛИФОВАТЬ СТУПЕНЬ ДО 179.6 ММ ДО ОСОБОГО ПИСЬМЕННОГО РАСПОРЯЖЕНИЯ!**  
*(严正声明：立即停止任何磨削！在收到俄方技术人员书面许可前，严禁将活塞杆台阶外径磨削至 179.6 mm！)*

#### Техническое обоснование запрета / 暂停加工的技术原因：
1. **Риск выдавливания уплотнений (экструзия) при высоком давлении:**  
   Уменьшение диаметра с $\varnothing 179.9$ до $179.60$ мм увеличивает радиальный зазор в цилиндре на **0.30 мм**. При рабочем давлении гидравлики (250–350 бар) стандартные опорно-направляющие кольца и манжеты **выдавит в образовавшийся зазор** (Seal Extrusion), кромку уплотнения срежет, и цилиндр моментально потечет и выйдет из строя.
2. **Необходимость расчета нестандартного пакета уплотнений:**  
   Прежде чем можно будет принять решение о возможности проточки до 179.6 мм, российский производитель уплотнений должен провести точный расчет посадочных мест и спец-профиля манжет. Для этого расчета критически не хватает одного замера — **внутреннего диаметра дна канавки**.

---

### 1. Первоочередное действие завода: Срочный замер дна канавок
### 1. 工厂首要动作：立即提供密封槽底径（槽底内径）实测数据
### 1. Mandatory First Action: Measure Groove Bottom Inner Diameter (ID)

Ширина канавок уже завалена заводом до **8.84–9.10 мм** (при норме по чертежу 8.6 +0.15 = max 8.75 мм).  
Технологи обоснованно предполагают, что цех также просадил и **внутренний посадочный диаметр дна канавок**. Без этих цифр производитель уплотнений не может сделать ни расчет зазора, ни чертеж спец-манжет!

**ТРЕБОВАНИЕ К ЗАВОДУ:**  
Специальным штангенциркулем или микрометром для внутренних канавок **немедленно замерить фактический внутренний диаметр дна обеих канавок** на всех штоках первой очереди (№ 2, 4, 5, 6, 9, 10, 11, 14, 16) и занести данные в переданные таблицы Excel (колонка 24).

*(中文说明: 客户技术专家明确指出：密封槽宽度已被工厂做大至8.84~9.10mm（图纸要求8.6+0.15mm）。俄方技术人员高度怀疑密封槽槽底内径也被车小或车大。在没有槽底实测数据的情况下，密封件厂家无法设计非标密封圈！请工厂立即用内径卡尺精确测量4#、5#、6#、9#、10#、11#、14#、16#及2#的密封槽槽底内径并报送俄方！)*

---

### 2. Запрос завода по радиусу R0.5 в углу перехода
### 2. 关于工厂提出将过渡圆角由 R0.3 改为 R0.5 的答复
### 2. Factory Request: Corner Radius R0.5 vs Drawing R0.3

Завод сообщил, что при обработке кромки наплывы хрома скалываются, и запросил увеличение радиуса сопряжения до $R=0.5$ мм (вместо чертежного $R \le 0.3$ max).

**ОФИЦИАЛЬНЫЙ ОТВЕТ:**  
- **Причина дефекта:** Хром откололся именно потому, что завод изначально не выполнил на заготовке радиус $R \le 0.3$ мм перед хромированием, оставив острый 90-градусный угол. В результате гальванического эффекта там образовался хрупкий «козырек» хрома, который осыпался при первом же касании инструмента.
- **Статус радиуса R0.5:** **ВРЕМЕННО НА ПАУЗЕ (HOLD)**. Увеличение радиуса в углу может помешать плотной посадке пятки уплотнения и защитного кольца. Вопрос передан производителю уплотнений одновременно с замерами канавок. Самовольно перетачивать на R0.5 **ЗАПРЕЩЕНО**.

---

### 3. Развеивание иллюзии завода «все штоки можно спасти»
### 3. 纠正误区：活塞杆无法“全数挽救”，报废品必须最终报废
### 3. Permanent Scrap Clarification: 3 Rods Cannot Be Salvaged

Завод ошибочно полагает, что предложение проточить шейки до 179.6 мм позволит сдать заказчику всю партию штоков. **Это в корне неверно!**  
Проточка до 179.6 мм не устраняет радиальное биение, не повышает твердость закаленного слоя и не возвращает просаженные шейки:

1. **Шток № 1 — ОКОНЧАТЕЛЬНЫЙ БРАК (报废):**  
   Радиальное биение составляет **0.170 мм** (превышает даже смягченный лимит 0.150 мм!), твердость составляет всего **45.8 HRC** (требование чертежа ≥50 HRC). Шток непригоден для работы в тяжелом гидроцилиндре.
2. **Шток № 3 — ОКОНЧАТЕЛЬНЫЙ БРАК (报废):**  
   Диаметр шейки просажен до **171.45 мм** (на 0.05 мм ниже нижнего предела допуска), толщина хрома имеет катастрофический наплыв **850 мкм** (0.85 мм вместо 100 мкм), твердость 46.5 HRC.
3. **Шток № 15 — ОКОНЧАТЕЛЬНЫЙ БРАК (报废):**  
   Посадочный поясок проточен до **179.55 мм** (на 0.25 мм меньше чертежа!), шейка 171.40 мм, твердость 45.7 HRC.

**По штокам № 1, № 3, № 15 завод обязан оформить возврат средств или бесплатное изготовление новых взамен бракованных!**  
*(中文说明: 工厂切勿存在侥幸心理。1#（跳动0.170mm超标且硬度仅45.8HRC）、3#（轴颈小0.05mm且铬层厚达850μm）、15#（台阶外圆小0.25mm）属于绝对不可逆的报废品！即使磨削至179.6也无法解决硬度低和跳动过大的致命缺陷。此3件必须退款或重做！)*

---

### 4. Что клиент уже согласовал (напоминание)
### 4. 客户已正式批准并接受的项目汇总
### 4. Summary of Previously Approved Concessions

Клиент подтверждает ранее данные согласия:
1. **Биение до 0.15 мм (≤ 0.150 мм):** 8 штоков признаны годными по биению: **№ 4, 5, 6, 9, 10, 11, 14, 16**.
2. **Уширение канавок до 8.84–8.89 мм:** Согласовано при условии ручной доводки кромок алмазным надфилем.
3. **Торцевая фаска 3х45°:** Согласована сошлифовка сколотого хрома в ровную фаску.
4. **Трубы:** Согласованы 8 коротких (1707–1710 мм) и 4 длинные (2184 мм, 2 отв. Ø18 мм, без 36 отв. M22).

---

### 5. Пошаговый план завода перед праздниками (до 1 октября)
### 5. 工厂国庆节前紧急行动路线图
### 5. Mandatory Action Roadmap Before Holiday Shutdown

| № | Действие завода / 工厂动作 | Детали / 具体要求 |
| :-: | :--- | :--- |
| **1** | **Замер дна канавок (槽底内径)** | Замерить внутренний Ø дна канавок на штоках № 2, 4, 5, 6, 9, 10, 11, 14, 16. Передать цифры в РФ. |
| **2** | **Видеопроверка резьбы калибром НЕ (止规)** | Резьбовым кольцом M170x4-6g проверить резьбы под видео. Останов строго ≤ 1.5–2 витка (особенно № 6 и № 9!). |
| **3** | **Станочная сошлифовка хрома на № 7 и № 8** | Сошлифовать 50 мкм (№7) и 30 мкм (№8) строго на круглошлифовальном станке до слоя 100 мкм. Ручная шлифовка запрещена! |
| **4** | **Биение штоков № 2, 12, 13** | Установить в центра, замерить биение по 5 точкам, внести замеры в таблицу. |
| **5** | **Перемер концов штока № 10** | Замерить микрометром участки 300 мм от краев. Если диаметр < 179.917 мм — шток бракуется. |

---

### 6. Переданные таблицы Excel / 交付的表格
Вам переданы две зеркальные таблицы с полными замерами и статусами:
- **Русская версия:** `Таблица_проверки_штоков_16шт.xlsx`
- **English version:** `Таблица_проверки_штоков_16шт_EN.xlsx`

Ждем от завода замеры внутреннего диаметра дна канавок и видеопроверку резьб калибром НЕ!

С уважением,  
**Российская проектная группа (Договор № 62230426)**  
"""

def create_styled_docx(output_path):
    doc = docx.Document()
    
    # Set standard margins (2 cm)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    
    # Helper to add colored box / table cell
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("ОФИЦИАЛЬНОЕ ПРЕДПИСАНИЕ ЗАВОДУ И ПАРТНЕРАМ\n")
    r_title.bold = True
    r_title.font.size = Pt(14)
    r_title.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
    
    r_sub_cn = p_title.add_run("关于紧急暂停179.6磨削、强制密封槽底径复测及发货前要求的函\n")
    r_sub_cn.bold = True
    r_sub_cn.font.size = Pt(11)
    r_sub_cn.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    r_sub_en = p_title.add_run("Formal Technical Notice: Stop-Order on Ø179.6 Grinding, Mandatory Groove Bottom ID & Pre-Shipment Actions")
    r_sub_en.font.size = Pt(10)
    r_sub_en.font.italic = True
    r_sub_en.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    # Meta Info Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_data = [
        ("Кому / 收件人:", "Дэвиду (DEZHOU ALEXDA), Руководству завода, Инспектору ОТК Ван Сююй (汪秀玉)"),
        ("От кого / 发件人:", "Российская проектная группа (Договор поставки оборудования № 62230426)"),
        ("Дата / 日期:", "28 сентября 2026 г. / 2026年9月28日"),
        ("Тема / 主题:", "СТОПОР шлифовки до Ø179.6 мм, замеры дна канавок, отсев брака и условия отгрузки")
    ]
    for row_idx, (k, v) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        cell_k = row.cells[0]
        cell_v = row.cells[1]
        cell_k.width = Inches(1.8)
        cell_v.width = Inches(5.2)
        set_cell_background(cell_k, "F2F2F2")
        set_cell_background(cell_v, "FAFAFA")
        pk = cell_k.paragraphs[0]
        pk.paragraph_format.space_after = Pt(2)
        pk.paragraph_format.space_before = Pt(2)
        rk = pk.add_run(k)
        rk.bold = True
        rk.font.size = Pt(9.5)
        pv = cell_v.paragraphs[0]
        pv.paragraph_format.space_after = Pt(2)
        pv.paragraph_format.space_before = Pt(2)
        rv = pv.add_run(v)
        rv.font.size = Pt(9.5)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    
    # STOP-ORDER Callout Banner (Table 1x1 with Red Border / Fill)
    banner_table = doc.add_table(rows=1, cols=1)
    banner_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    banner_cell = banner_table.rows[0].cells[0]
    banner_cell.width = Inches(7.0)
    set_cell_background(banner_cell, "FDE8E8") # Light Red
    
    bp = banner_cell.paragraphs[0]
    bp.paragraph_format.space_before = Pt(4)
    bp.paragraph_format.space_after = Pt(4)
    
    br1 = bp.add_run("🚨 КАТЕГОРИЧЕСКИЙ СТОПОР НА ШЛИФОВКУ ДО Ø179.6 ММ!\n")
    br1.bold = True
    br1.font.size = Pt(12)
    br1.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    
    br2 = bp.add_run("🚨 紧急暂停指令：严禁擅自将外圆台阶磨削至 179.6 mm！\n")
    br2.bold = True
    br2.font.size = Pt(11)
    br2.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
    
    br3 = bp.add_run("Завод в отчете от 27.09 («Report of the.docx») предложил переточить ступень Ø179.9 на 179.60 мм. Решением российских технологов выдан ЖЕСТКИЙ СТОПОР: любые механические работы на шейках ЗАМОРОЖЕНЫ до получения замеров дна канавок и расчета уплотнений! При давлении 250–350 бар зазор 0.3 мм приведет к выдавливанию манжет (экструзии) и полному отказу цилиндра.")
    br3.font.size = Pt(9.5)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    
    # Section 1
    h1 = doc.add_heading("1. Срочный замер дна канавок / 强制提供密封槽底径实测数据", level=2)
    h1.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p1 = doc.add_paragraph()
    p1.add_run("Ширина канавок уже завалена цехом до ").font.size = Pt(10)
    r_w = p1.add_run("8.84–9.10 мм")
    r_w.bold = True
    p1.add_run(" (чертеж: 8.6 +0.15 = max 8.75 мм). Российские технологи обоснованно предполагают, что цех также просадил и ").font.size = Pt(10)
    r_id = p1.add_run("внутренний диаметр дна канавки")
    r_id.bold = True
    p1.add_run(". Без точного замера дна производитель уплотнений не может спроектировать спец-манжеты!\n").font.size = Pt(10)
    
    p1_cn = doc.add_paragraph()
    r_cn_id = p1_cn.add_run("【核心要求】请工厂立即使用内径卡尺精确测量 4#、5#、6#、9#、10#、11#、14#、16# 及 2# 的密封槽槽底内径（Groove Bottom ID）！在未得到俄方对非标密封圈的确认前，严禁盲目加工！")
    r_cn_id.font.italic = True
    r_cn_id.font.size = Pt(9.5)
    r_cn_id.font.color.rgb = RGBColor(0x00, 0x44, 0x88)
    
    # Section 2
    h2 = doc.add_heading("2. Запрос завода по радиусу R0.5 в углу перехода / 关于过渡圆角 R0.5", level=2)
    h2.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    p2 = doc.add_paragraph()
    p2.add_run("Завод запросил увеличить радиус в углу перехода до R=0.5 мм вместо чертежного R≤0.3 мм из-за сколов хрома.\n").font.size = Pt(10)
    p2.add_run("• Экспертиза технологов: скол произошел потому, что завод изначально не сделал радиус R≤0.3 мм перед хромированием, создав острый 90° концентратор.\n").font.size = Pt(9.5)
    p2.add_run("• Решение: Вопрос поставлен ").font.size = Pt(9.5)
    p2.add_run("НА ПАУЗУ (HOLD)").bold = True
    p2.add_run(". Увеличение радиуса до R0.5 может помешать правильной посадке пятки уплотнений. Решение будет принято только после расчета поставщиком уплотнений.\n").font.size = Pt(9.5)
    
    p2_cn = doc.add_paragraph()
    r2_cn = p2_cn.add_run("【关于R0.5】崩铬是因为工厂镀铬前未做R0.3倒角形成锐角所致。改到R0.5可能影响密封圈根部贴合。该请求目前暂缓（HOLD），严禁擅自修改！")
    r2_cn.font.italic = True
    r2_cn.font.size = Pt(9.5)
    
    # Section 3
    h3 = doc.add_heading("3. Окончательный брак: штоки № 1, 3, 15 НЕ СПАСТИ! / 确定最终报废项目", level=2)
    h3.style.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
    
    p3 = doc.add_paragraph()
    p3.add_run("Завод ошибочно полагает, что проточкой 179.6 мм можно спасти всю партию. Это иллюзия! Три штока имеют неустранимый брак:\n").font.size = Pt(10)
    
    scrap_table = doc.add_table(rows=4, cols=3)
    scrap_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    scrap_headers = ["№ штока", "Неустранимые дефекты", "Решение"]
    for i, h in enumerate(scrap_headers):
        cell = scrap_table.rows[0].cells[i]
        set_cell_background(cell, "E0E0E0")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        
    scrap_rows = [
        ("Шток № 1", "Биение 0.170 мм (>0.150 мм лимита), твердость 45.8 HRC (<50 HRC).", "❌ ОКОНЧАТЕЛЬНЫЙ БРАК (报废)\nВозврат средств / переделка"),
        ("Шток № 3", "Шейка Ø171.45 мм (-0.05 мм ниже допуска), наплыв хрома 850 мкм, HRC 46.5.", "❌ ОКОНЧАТЕЛЬНЫЙ БРАК (报废)\nВозврат средств / переделка"),
        ("Шток № 15", "Поясок просажен до Ø179.55 мм (-0.25 мм!), шейка Ø171.40 мм, HRC 45.7.", "❌ ОКОНЧАТЕЛЬНЫЙ БРАК (报废)\nВозврат средств / переделка")
    ]
    for row_idx, data in enumerate(scrap_rows, start=1):
        for col_idx, val in enumerate(data):
            cell = scrap_table.rows[row_idx].cells[col_idx]
            set_cell_background(cell, "FFF0F0")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 2:
                r.bold = True
                r.font.color.rgb = RGBColor(0xCC, 0x00, 0x00)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    
    # Section 4
    h4 = doc.add_heading("4. Пошаговый регламент действий завода до праздников 1 октября", level=2)
    h4.style.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    
    action_table = doc.add_table(rows=6, cols=3)
    action_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    action_headers = ["Пункт", "Обязательное действие цеха / 动作", "Детали и критерий приемки"]
    for i, h in enumerate(action_headers):
        cell = action_table.rows[0].cells[i]
        set_cell_background(cell, "E0E0E0")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.5)
        
    action_rows = [
        ("1", "Замер дна канавок (槽底内径)", "Замерить внутренний Ø дна канавок на штоках № 2, 4, 5, 6, 9, 10, 11, 14, 16. Передать цифры в РФ."),
        ("2", "Проверка резьбы калибром НЕ (止规)", "Кольцом M170x4-6g проверить резьбы под видео. Останов строго ≤ 1.5–2 витка (особенно № 6 и № 9!)."),
        ("3", "Сошлифовка хрома на № 7 и № 8", "Сошлифовать 50 мкм (№7) и 30 мкм (№8) СТРОГО на круглошлифовальном станке до 100 мкм. Ручная шлифовка ЗАПРЕЩЕНА!"),
        ("4", "Биение штоков № 2, 12, 13", "Установить в центра, замерить биение по 5 точкам, внести замеры в таблицу."),
        ("5", "Перемер концов штока № 10", "Замерить микрометром участки 300 мм от краев. Если диаметр < 179.917 мм — шток бракуется.")
    ]
    for row_idx, data in enumerate(action_rows, start=1):
        for col_idx, val in enumerate(data):
            cell = action_table.rows[row_idx].cells[col_idx]
            set_cell_background(cell, "F9F9F9" if row_idx % 2 == 1 else "FFFFFF")
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(val)
            r.font.size = Pt(9)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r.bold = True
                
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    # Footer Section
    p_foot = doc.add_paragraph()
    r_foot = p_foot.add_run("Вам переданы две зеркальные таблицы Excel со всеми актуальными данными:\n"
                           "• Русская версия: Таблица_проверки_штоков_16шт.xlsx\n"
                           "• English version: Таблица_проверки_штоков_16шт_EN.xlsx\n\n"
                           "Ждем замеры внутреннего диаметра дна канавок и видеопроверку калибров НЕ!\n\n"
                           "С уважением,\nРоссийская проектная группа (Договор № 62230426)")
    r_foot.font.size = Pt(9.5)
    r_foot.font.italic = True
    
    doc.save(output_path)
    print(f"Successfully generated DOCX: {output_path}")

def main():
    proj_dir = r"C:\Codex_Personal\projects\Price creating\Договор_62230426_Штоки_и_Трубы\reports"
    dl_dir = r"C:\Users\Артем\Downloads\ТЗ для гравити"
    
    os.makedirs(proj_dir, exist_ok=True)
    os.makedirs(dl_dir, exist_ok=True)
    
    proj_md = os.path.join(proj_dir, "СОПРОВОДИТЕЛЬНОЕ_ПИСЬМО_ЗАВОДУ_ФОРМАТ_ТАБЛИЦЫ.md")
    dl_md = os.path.join(dl_dir, "СОПРОВОДИТЕЛЬНОЕ_ПИСЬМО_ЗАВОДУ_ФОРМАТ_ТАБЛИЦЫ.md")
    
    with open(proj_md, "w", encoding="utf-8") as f:
        f.write(LETTER_MD_CONTENT)
    print(f"Saved MD: {proj_md}")
    
    with open(dl_md, "w", encoding="utf-8") as f:
        f.write(LETTER_MD_CONTENT)
    print(f"Saved MD: {dl_md}")
    
    proj_docx = os.path.join(proj_dir, "СОПРОВОДИТЕЛЬНОЕ_ПИСЬМО_ЗАВОДУ_ФОРМАТ_ТАБЛИЦЫ.docx")
    dl_docx = os.path.join(dl_dir, "СОПРОВОДИТЕЛЬНОЕ_ПИСЬМО_ЗАВОДУ_ФОРМАТ_ТАБЛИЦЫ.docx")
    
    create_styled_docx(proj_docx)
    create_styled_docx(dl_docx)

if __name__ == "__main__":
    main()
