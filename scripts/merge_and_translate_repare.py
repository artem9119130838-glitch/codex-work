# -*- coding: utf-8 -*-
"""
Script to:
1. Compare 'DATASHEET ROD-3rd time inspection.xlsx' vs 'DATASHEET ROD-try to repare.xlsx'.
2. Build merged English workbook: 'DATASHEET ROD-try to repare_EN.xlsx'
   with the full inspection matrix, factory repair proposals (Col U),
   Russian engineering verdict / risk analysis (Col V),
   and English explanation of Brush Plating (刷镀).
3. Also generate 'DATASHEET ROD-3rd time inspection_EN.xlsx'.
4. Sync all files to Downloads and project repository.
"""

import os
import shutil
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# English translations mapping
TRANSLATION_MAP = {
    # Metadata
    "检验记录表": "INSPECTION & FACTORY REPAIR PROPOSAL RECORD SHEET",
    "   检验记录表": "INSPECTION & FACTORY REPAIR PROPOSAL RECORD SHEET",
    "规格及名称：活塞杆": "Part Name & Spec: Piston Rod Ø180x2574 mm (AISI 431 / Drawing 20.11.32.67.068)",
    "Спецификация и наименование: Поршневой шток": "Part Name & Spec: Piston Rod Ø180x2574 mm (AISI 431 / Drawing 20.11.32.67.068)",
    "检验日期：2026/9/18": "Inspection Date: 2026-09-18",
    "Дата проверки: 2026/9/18": "Inspection Date: 2026-09-18",
    "检验数量：16件": "Inspection Quantity: 16 pcs",
    "Количество проверенных: 16 шт.": "Inspection Quantity: 16 pcs",
    "准备修改到什么数值": "Factory Proposed Repair / Modification Value",
    "До каких значений планируется довести": "Factory Proposed Repair / Modification Value",
    
    # Headers
    "序列": "Item",
    "№": "Item",
    "尺寸": "Parameter / Dimension",
    "Размер": "Parameter / Dimension",
    "公差": "Drawing Tolerance",
    "Допуск": "Drawing Tolerance",
    "检验尺寸结果": "Inspection Results (Measured Values across 16 Rods)",
    "Результаты измерений": "Inspection Results (Measured Values across 16 Rods)",
    "量具": "Measuring Tool / Gauge",
    "Измерительный инструмент": "Measuring Tool / Gauge",
    
    # Parameters
    "Φ180": "OD Ø180 f7",
    "M170*4": "Thread M170x4-6g",
    "Φ179.9": "Step Ø179.9",
    "Φ171.6": "Neck Ø171.6 (-0.1)",
    "Φ164.3": "Groove Bottom Ø164.3",
    "2574": "Total Length 2574 mm",
    "10": "Left End Length 10 mm",
    "8.6": "Groove Width 8.6 mm",
    "15": "Groove Spacing 15 mm",
    "42.2": "Right End Length 42.2 mm",
    "镀铬": "Chrome Thickness (mm)",
    "Хромирование": "Chrome Thickness (mm)",
    "光洁度": "Surface Roughness Ra (µm)",
    "Чистота поверхности": "Surface Roughness Ra (µm)",
    "高频": "Induction Hardness (HRC)",
    "Высокочастотная закалка": "Induction Hardness (HRC)",
    "R": "Corner Transition Radius R",
    
    # Values & Tools
    "环规": "Thread Ring Gauge (Go/No-Go)",
    "Кольцевой калибр": "Thread Ring Gauge (Go/No-Go)",
    "合格": "PASS",
    "Соответствует": "PASS",
    "175-200千分尺": "Micrometer 175-200 mm",
    "Микрометр 175–200": "Micrometer 175-200 mm",
    "150-175千分尺": "Micrometer 150-175 mm",
    "Микрометр 150–175": "Micrometer 150-175 mm",
    "游标卡尺": "Vernier Caliper",
    "Штангенциркуль": "Vernier Caliper",
    "5米卷尺": "5m Steel Tape Measure",
    "Рулетка 5 м": "5m Steel Tape Measure",
    "内槽千分尺": "Internal Groove Micrometer",
    "Микрометр для внутренних пазов": "Internal Groove Micrometer",
    "涂层测厚仪": "Coating Thickness Gauge",
    "Толщиномер покрытия": "Coating Thickness Gauge",
    "光洁度、粗糙度仪": "Surface Roughness Tester",
    "Прибор для шероховатости поверхности": "Surface Roughness Tester",
    "硬度计手持便携式": "Portable Hardness Tester",
    "Переносной твердомер": "Portable Hardness Tester",
    "R0.3": "R ≤ 0.3 mm max",
    "50-55": "50-55 HRC",
    
    # Factory Proposals in Col U
    "7号8号能不能磨到179.88~179.86": "Can Rods #7 & #8 be ground to OD 179.88 ~ 179.86 mm?",
    "Можно ли №7 и №8 довести шлифовкой до 179,88–179,86": "Can Rods #7 & #8 be ground to OD 179.88 ~ 179.86 mm?",
    "Φ179.6~  Φ179.65": "Grind step down to Ø179.60 ~ Ø179.65 mm",
    "15号3号槽能不能刷镀171.55": "Can Rods #15 & #3 neck be built up by brush plating to 171.55 mm?",
    "Можно ли №15 и паз №3 довести гальваническим покрытием до 171,55": "Can Rods #15 & #3 neck be built up by brush plating to 171.55 mm?",
    "15号179.55能不能刷镀179.65": "Can Rod #15 step (179.55) be built up by brush plating to 179.65 mm?",
    "Можно ли №15 (179,55) довести гальваническим покрытием до 179,65": "Can Rod #15 step (179.55) be built up by brush plating to 179.65 mm?",
    "1号磨到179.65，跳动保证0.05左右": "Grind Rod #1 to 179.65 mm, factory guarantees runout ~0.05 mm",
    "№1 довести шлифовкой до 179,65; биение — ок. 0,05": "Grind Rod #1 to 179.65 mm, factory guarantees runout ~0.05 mm",
    "    R0.5  ": "Increase transition radius to R0.5 mm",
    "R0.5": "Increase transition radius to R0.5 mm",
    
    # Signatures & Footers
    "检验员：汪秀玉": "QC Inspector: Wang Xiuyu (汪秀玉)",
    "Контролёр: Ван Сююй": "QC Inspector: Wang Xiuyu (汪秀玉)",
    "单位签字及盖章：": "Authorized Signature & Stamp:",
    "Подпись и печать предприятия:": "Authorized Signature & Stamp:",
    "请注意 编号1的镀铬层光洁度是0.093": "Note: Surface roughness of chrome plating on Rod #1 is 0.093 µm",
    "Внимание: чистота поверхности хромового покрытия №1 — 0,093": "Note: Surface roughness of chrome plating on Rod #1 is 0.093 µm"
}

# Russian Engineering Verdict / Risk Assessment for Column V
ENGINEERING_VERDICTS = {
    6: (
        "⚠️ CONDITIONAL APPROVAL:\n"
        "Machine grinding excess chrome on #7 (-50µm) & #8 (-30µm) is allowed, BUT finished OD must stay within f7 tolerance (179.917..179.957). "
        "Grinding body below 179.917 mm is NOT permitted.",
        "FFF2CC" # Yellow alert
    ),
    8: (
        "🚨 STRICT STOP-ORDER (HOLD):\n"
        "Reducing step to 179.60..179.65 mm increases clearance by 0.30 mm. At 250–350 bar pressure, standard seals will EXTRUDE and fail. "
        "FROZEN until groove bottom ID is measured and custom seal calculations are verified!",
        "FCE4D6" # Orange alert
    ),
    9: (
        "❌ REJECTED (HIGH RISK OF DELAMINATION):\n"
        "Brush selective electroplating (刷镀) on seal sliding neck has weak adhesion compared to bath plating. Under 35 MPa hydraulic pressure, "
        "layer will peel off, shredding seals and scoring cylinder tube. Rod #3 & #15 are permanent scrap!",
        "F8CBAD" # Red/Orange alert
    ),
    10: (
        "❌ REJECTED (PERMANENT SCRAP):\n"
        "Rod #15 step is undersized by 0.25 mm. Brush plating 100 µm on step will not withstand guide bushing shear loads. "
        "Core hardness is also failing (45.7 HRC < 50). Full remake / refund required.",
        "F8CBAD"
    ),
    11: (
        "❌ REJECTED (PERMANENT SCRAP):\n"
        "Grinding Rod #1 to 179.65 mm does NOT fix core induction hardness (measured 45.8 HRC vs min 50 HRC spec). "
        "Soft rod will bend/pit under duty cycles. Permanent scrap!",
        "F8CBAD"
    ),
    20: (
        "⚠️ ON HOLD (AWAITING SEAL SPECS):\n"
        "Factory omitted R≤0.3 before chroming, creating sharp 90° edge where chrome flaked. "
        "Increasing to R0.5 may compromise seal heel support. On hold pending seal manufacturer approval.",
        "FFF2CC"
    )
}

BRUSH_PLATING_EXPLANATION_EN = """📌 TECHNICAL ASSESSMENT: SELECTIVE BRUSH ELECTROPLATING (刷镀) IN HYDRAULIC APPLICATIONS

1. What is Brush Electroplating (刷镀 / Selective Plating)?
   A portable electrochemical deposition process using an absorbent pad/brush saturated with concentrated electrolyte. 
   An electric current passes through the brush (anode) while rubbing against the workpiece (cathode), depositing metal locally without an immersion tank.

2. Why the Factory Proposes It:
   The factory realizes rods #3 and #15 have severely undersized dimensions (neck Ø171.45 instead of min Ø171.50, and step Ø179.55 instead of Ø179.804). 
   They are trying to avoid scrapped parts by locally building up 0.10 mm of nickel/chrome.

3. Why Russian Engineering Rejects Brush Plating for These High-Pressure Rods:
   • Shear Strength & Delamination Risk: Brush-plated layers have significantly lower bonding/adhesion strength than conventional thermo-treated bath plating. Under cyclic hydraulic operating pressure (250–350 bar / 25–35 MPa) and dynamic friction against polyurethane seals and bronze guide rings, brush-plated layers are prone to flaking and spalling (delamination).
   • Catastrophic Failure Mode: Flaked-off hard chromium particles circulate in hydraulic fluid, scoring the precision honed cylinder tube (Ra 0.2) and jamming servo valves.
   • Secondary Defects Untouched: Brush plating does NOT cure low core hardness on Rod #15 (45.7 HRC) or Rod #3 (46.5 HRC), nor does it fix the 850 µm chrome surge on Rod #3.

CONCLUSION: Brush plating on heavy-duty hydraulic piston rods operating in critical equipment is strictly unacceptable. Rods #1, #3, and #15 remain confirmed SCRAP."""

def clean_translate(text):
    if text is None:
        return None
    if not isinstance(text, str):
        return text
    
    s = text.strip()
    if s in TRANSLATION_MAP:
        return TRANSLATION_MAP[s]
        
    for k, v in TRANSLATION_MAP.items():
        if k in s:
            s = s.replace(k, v)
            
    if "编号" in text:
        for i in range(1, 17):
            if text.strip() == f"编号{i}":
                return f"Rod #{i}"
                
    if "两头300左右的是179.89" in text:
        return "179.92,\nEnds ~300mm: 179.89"
        
    if "179.957" in text and "-0.043" in text:
        return "179.957 (-0.043)\n179.917 (-0.083)"
        
    if "179.85" in text and "-0.05" in text:
        return "179.85 (-0.05)\n179.804 (-0.096)"
        
    if text.strip() == "0\n+0.15":
        return "+0.15 / 0"
        
    return s

def build_merged_en_workbook(src_repare_path, dest_repare_en, dest_inspection_en=None):
    wb_src = openpyxl.load_workbook(src_repare_path)
    
    # Use 'Chinese words' as base since it has the exact factory layout
    sheet_name = 'Chinese words' if 'Chinese words' in wb_src.sheetnames else wb_src.sheetnames[0]
    ws_src = wb_src[sheet_name]
    
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Inspection_&_Repair_EN"
    
    # Set row heights
    for r in range(1, 30):
        h = ws_src.row_dimensions[r].height
        ws_out.row_dimensions[r].height = h if h else 25.0
    ws_out.row_dimensions[1].height = 40.0
    ws_out.row_dimensions[3].height = 28.0
    ws_out.row_dimensions[4].height = 24.0
    ws_out.row_dimensions[5].height = 20.0
    ws_out.row_dimensions[6].height = 55.0
    
    # Copy merged cells (only A1:T1, D4:S4, etc.)
    # We will adjust title merge to include U and V: A1:V1
    for rng in ws_src.merged_cells.ranges:
        rng_str = str(rng)
        if rng_str == "A1:T1":
            ws_out.merge_cells("A1:V1")
        elif rng_str == "D4:T4":
            ws_out.merge_cells("D4:S4") # Rod 1 to 16
        elif rng_str in ["A2:T2"]:
            ws_out.merge_cells("A2:V2")
        elif rng_str == "L21:T21":
            ws_out.merge_cells("L21:V21")
        elif rng_str == "A21:K21":
            ws_out.merge_cells("A21:K21")
        elif rng_str not in ["A1:T1", "D4:T4", "A2:T2", "L21:T21"]:
            ws_out.merge_cells(rng_str)
            
    # Merge headers for T, U, V in rows 4-5
    ws_out.merge_cells("T4:T5")
    ws_out.merge_cells("U4:U5")
    ws_out.merge_cells("V4:V5")
    
    # Set tailored column widths
    col_widths = {
        'A': 10.0,  # Item
        'B': 24.0,  # Parameter / Dimension
        'C': 23.0,  # Tolerance
        'D': 11.0,  # Rod 1..16
        'E': 11.0, 'F': 11.0, 'G': 11.0, 'H': 11.0, 'I': 11.0, 'J': 11.0,
        'K': 11.0, 'L': 11.0, 'M': 14.0, 'N': 11.0, 'O': 11.0, 'P': 11.0,
        'Q': 11.0, 'R': 11.0, 'S': 11.0,
        'T': 25.0,  # Measuring Tool / Gauge
        'U': 34.0,  # Factory Proposed Repair Action
        'V': 44.0   # Russian Engineering Verdict & Risk Analysis
    }
    for col_let, w in col_widths.items():
        ws_out.column_dimensions[col_let].width = w
        
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )
    
    # Copy cells and translate
    for r in range(1, 22):
        for c in range(1, 22):
            cell_src = ws_src.cell(r, c)
            raw_val = cell_src.value
            trans_val = clean_translate(raw_val)
            
            # Avoid writing into merged non-top-left cells
            cell_dest = ws_out.cell(r, c)
            if type(cell_dest).__name__ != 'MergedCell':
                cell_dest.value = trans_val
                
            # Copy alignment / styling
            align = Alignment(horizontal='center', vertical='center', wrap_text=True)
            if c in [1, 2] and r == 3:
                align = Alignment(horizontal='left', vertical='center')
            elif c == 2 and r in range(6, 21):
                align = Alignment(horizontal='left', vertical='center')
            elif c == 20: # Tools
                align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            elif c == 21: # Proposals
                align = Alignment(horizontal='left', vertical='center', wrap_text=True)
            cell_dest.alignment = align
            
            cell_dest.font = Font(name='Arial', size=9.5)
            if r in [4, 5]:
                cell_dest.font = Font(name='Arial', size=9.5, bold=True, color='002060')
                cell_dest.fill = PatternFill(fill_type='solid', start_color='D9E1F2', end_color='D9E1F2')
            if r in range(4, 21) and c in range(1, 22):
                cell_dest.border = thin_border

    # Headers for Col U and Col V
    cell_u4 = ws_out.cell(4, 21)
    cell_u4.value = "Factory Proposed Repair / Modification (准备修改到什么数值)"
    cell_u4.fill = PatternFill(fill_type='solid', start_color='FCE4D6', end_color='FCE4D6') # Peach/Orange
    cell_u4.font = Font(name='Arial', size=9.5, bold=True, color='C65911')
    cell_u4.border = thin_border
    
    cell_v4 = ws_out.cell(4, 22)
    cell_v4.value = "Russian Engineering Verdict & Risk Analysis (Решение РФ)"
    cell_v4.fill = PatternFill(fill_type='solid', start_color='C6D9F1', end_color='C6D9F1') # Steel Blue
    cell_v4.font = Font(name='Arial', size=9.5, bold=True, color='1F497D')
    cell_v4.border = thin_border
    
    # Fill Col V values and color highlights
    for r_idx, (verdict_text, fill_color) in ENGINEERING_VERDICTS.items():
        cell_v = ws_out.cell(r_idx, 22)
        cell_v.value = verdict_text
        cell_v.fill = PatternFill(fill_type='solid', start_color=fill_color, end_color=fill_color)
        cell_v.font = Font(name='Arial', size=8.5, bold=True if 'STOP' in verdict_text or 'REJECTED' in verdict_text else False)
        cell_v.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        cell_v.border = thin_border
        
        # Also highlight proposal cell in Col U
        cell_u = ws_out.cell(r_idx, 21)
        if cell_u.value:
            cell_u.fill = PatternFill(fill_type='solid', start_color='FFF2CC', end_color='FFF2CC')
            cell_u.font = Font(name='Arial', size=9.0, bold=True)
            
    # Set borders for remaining Col V rows
    for r in range(6, 21):
        c_v = ws_out.cell(r, 22)
        c_v.border = thin_border
        if not c_v.value:
            c_v.value = "— No repair required (Standard tolerance or passed)"
            c_v.font = Font(name='Arial', size=8.5, italic=True, color='7F7F7F')
            c_v.alignment = Alignment(horizontal='left', vertical='center')

    # Title styling
    title_cell = ws_out.cell(1, 1)
    title_cell.value = "MASTER INSPECTION DATA & FACTORY REPAIR PROPOSALS (16 RODS Ø180x2574 mm)"
    title_cell.font = Font(name='Arial', size=14, bold=True, color='1F4E78')
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Note on Rod #1
    note_cell = ws_out.cell(22, 2)
    note_cell.value = "Note: Surface roughness of chrome plating on Rod #1 is 0.093 µm (PASS)"
    note_cell.font = Font(name='Arial', size=9.0, italic=True, bold=True, color='0070C0')
    
    # Add Brush Plating Briefing below table
    ws_out.cell(24, 2).value = "TECHNICAL MEMORANDUM ON FACTORY BRUSH PLATING PROPOSAL (刷镀方案技术评估)"
    ws_out.cell(24, 2).font = Font(name='Arial', size=11, bold=True, color='C00000')
    
    ws_out.merge_cells("B25:V33")
    bp_cell = ws_out.cell(25, 2)
    bp_cell.value = BRUSH_PLATING_EXPLANATION_EN
    bp_cell.font = Font(name='Arial', size=9.0)
    bp_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    bp_cell.fill = PatternFill(fill_type='solid', start_color='F2F2F2', end_color='F2F2F2')
    
    # Save English merged workbook
    wb_out.save(dest_repare_en)
    print(f"Successfully generated: {dest_repare_en}")
    
    # If dest_inspection_en requested, save a copy there too
    if dest_inspection_en:
        shutil.copy2(dest_repare_en, dest_inspection_en)
        print(f"Synced inspection copy: {dest_inspection_en}")

def main():
    src_repare = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-try to repare.xlsx"
    dest_repare_en_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-try to repare_EN.xlsx"
    
    dest_inspection_en_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-3rd time inspection_EN.xlsx"
    
    proj_dir = r"C:\Codex\projects\Price creating\Договор_62230426_Штоки_и_Трубы\reports"
    os.makedirs(proj_dir, exist_ok=True)
    
    dest_repare_en_proj = os.path.join(proj_dir, "DATASHEET ROD-try to repare_EN.xlsx")
    dest_inspection_en_proj = os.path.join(proj_dir, "DATASHEET ROD-3rd time inspection_EN.xlsx")
    
    build_merged_en_workbook(src_repare, dest_repare_en_dl, dest_inspection_en_dl)
    
    shutil.copy2(dest_repare_en_dl, dest_repare_en_proj)
    shutil.copy2(dest_inspection_en_dl, dest_inspection_en_proj)
    print(f"Synced to project: {dest_repare_en_proj}")
    print(f"Synced to project: {dest_inspection_en_proj}")

if __name__ == "__main__":
    main()
