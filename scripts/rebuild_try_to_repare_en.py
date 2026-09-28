# -*- coding: utf-8 -*-
"""
Script to rebuild 'DATASHEET ROD-try to repare_EN.xlsx' cleanly with ZERO overlapping merged cells,
ensuring 100% readability in Excel and complete English translation of the brush plating technology.
"""

import os
import sys
import shutil
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TRANSLATION_MAP = {
    # Headers & Metadata
    "检验记录表": "INSPECTION & FACTORY REPAIR PROPOSAL RECORD SHEET",
    "规格及名称：活塞杆": "Part Name & Spec: Piston Rod Ø180x2574 mm (AISI 431 / Drawing 20.11.32.67.068)",
    "检验日期：2026/9/18": "Inspection Date: 2026-09-18",
    "检验数量：16件": "Inspection Quantity: 16 pcs",
    "序列": "Item",
    "尺寸": "Parameter / Dimension",
    "公差": "Drawing Tolerance",
    "检验尺寸结果": "Inspection Results (Measured Values across 16 Rods)",
    "量具": "Measuring Tool / Gauge",
    "准备修改到什么数值": "Factory Proposed Repair / Modification (准备修改到什么数值)",

    # Parameters (Col B)
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
    "光洁度": "Surface Roughness Ra (µm)",
    "高频": "Induction Hardness (HRC)",
    "R": "Corner Transition Radius R",

    # Tolerances & Values
    "环规": "Thread Ring Gauge (Go/No-Go)",
    "合格": "PASS",
    "R0.3": "R ≤ 0.3 mm max",
    "50-55": "50-55 HRC",

    # Measuring Tools (Col T)
    "175-200千分尺": "Micrometer 175-200 mm",
    "150-175千分尺": "Micrometer 150-175 mm",
    "游标卡尺": "Vernier Caliper",
    "5米卷尺": "5m Steel Tape Measure",
    "内槽千分尺": "Internal Groove Micrometer",
    "涂层测厚仪": "Coating Thickness Gauge",
    "光洁度、粗糙度仪": "Surface Roughness Tester",
    "硬度计手持便携式": "Portable Hardness Tester",

    # Proposals (Col U)
    "7号8号能不能磨到179.88~179.86": "Can Rods #7 & #8 be ground to OD 179.88 ~ 179.86 mm?",
    "Φ179.6~  Φ179.65": "Grind step down to Ø179.60 ~ Ø179.65 mm",
    "15号3号槽能不能刷镀171.55": "Can Rods #15 & #3 neck be built up by brush plating to 171.55 mm?",
    "15号179.55能不能刷镀179.65": "Can Rod #15 step (179.55) be built up by brush plating to 179.65 mm?",
    "1号磨到179.65，跳动保证0.05左右": "Grind Rod #1 to 179.65 mm, factory guarantees runout ~0.05 mm",
    "    R0.5  ": "Increase transition radius to R0.5 mm",
    "R0.5": "Increase transition radius to R0.5 mm",

    # Signatures
    "检验员：汪秀玉": "QC Inspector: Wang Xiuyu (汪秀玉)",
    "单位签字及盖章：": "Authorized Signature & Stamp:",
    "请注意 编号1的镀铬层光洁度是0.093": "Note: Surface roughness of chrome plating on Rod #1 is 0.093 µm (PASS)"
}

ENGINEERING_VERDICTS = {
    6: (
        "⚠️ CONDITIONAL APPROVAL:\n"
        "Machine grinding excess chrome on #7 (-50µm) & #8 (-30µm) is allowed, BUT finished OD must stay within f7 tolerance (179.917..179.957). "
        "Grinding body below 179.917 mm is NOT permitted.",
        "FFF2CC"
    ),
    8: (
        "🚨 STRICT STOP-ORDER (HOLD):\n"
        "Reducing step to 179.60..179.65 mm increases clearance by 0.30 mm. At 250–350 bar pressure, standard seals will EXTRUDE and fail. "
        "FROZEN until groove bottom ID is measured and custom seal calculations are verified!",
        "FCE4D6"
    ),
    9: (
        "❌ REJECTED (HIGH RISK OF DELAMINATION):\n"
        "Brush selective electroplating (刷镀) on seal sliding neck has weak adhesion compared to bath plating. Under 35 MPa hydraulic pressure, "
        "layer will peel off, shredding seals and scoring cylinder tube. Rod #3 & #15 are permanent scrap!",
        "F8CBAD"
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

TECH_SECTIONS = [
    ("1. Principle of Selective Brush Electroplating (刷镀核心原理):",
     "Selective brush electroplating is a portable electrochemical deposition method that does not require an immersion plating tank. "
     "The workpiece is connected to the negative terminal (cathode), while a handheld stylus wrapped in an insoluble anode material (e.g. graphite) "
     "is connected to the positive terminal (anode). Soaked in specialized plating solution, the stylus moves dynamically over the surface. "
     "Metal ions discharge, reduce, and crystallize under high current density (5–10 times higher than bath plating) to form a dense metallic deposit.",
     100),
    
    ("2. Technological Process Steps (主要工艺流程):",
     "• Surface Preparation: Mechanical deburring, degreasing, electrochemical cleaning (micro-oil removal), and chemical activation.\n"
     "• Base Transition Layer: A 2–5 µm special nickel or copper layer is deposited to provide low internal stress and initial bonding.\n"
     "• Working Layer Deposition: Specialized wear-resistant solutions are applied under strict voltage, motion speed, and continuous fluid feed.\n"
     "• Post-Treatment: Neutralization, rinsing, drying, mechanical polishing to specified Ra, and anti-corrosion oiling.",
     105),
    
    ("3. Technical Characteristics & Advantages (技术特点):",
     "• Tankless & Portable: Highly flexible, allows on-site repairs of large components without full equipment disassembly.\n"
     "• Localized Selectivity: Precisely targets defective zones with zero impact on surrounding finished surfaces.\n"
     "• Rapid Deposition Rate: Current density allows deposition rates 5–50 times faster than conventional bath plating.\n"
     "• Low Operating Temperature (<70°C): Causes no thermal deformation, no residual heat stresses, and no metallurgical phase change in base metal.\n"
     "• Controllable Thickness: Range from 1 µm up to 2–3 mm (optimal range 10–100 µm), typically requiring minimal post-grinding.",
     120),
    
    ("4. Process Limitations & Risks (注意事项与局限性):",
     "• Surface smoothness and microscopic uniformity of brush-plated layers are generally inferior to submerged tank plating.\n"
     "• High operator skill dependency: coating adhesion and structure heavily depend on operator consistency and manual dexterity.\n"
     "• Significant manual labor required; careful chemical management and hazardous waste handling are mandatory.",
     85),
    
    ("5. Typical Industrial Applications (主要应用领域):",
     "• Restoration of worn, corroded, or undersized shafts, bores, and housings to restore nominal dimensions.\n"
     "• Surface hardening, local corrosion protection, or electrical conductivity enhancement.\n"
     "• Emergency in-situ maintenance of massive equipment (turbines, rolling mills, ships) where dismantling is cost-prohibitive.",
     85),
    
    ("6. RUSSIAN ENGINEERING VERDICT FOR HYDRAULIC PISTON RODS (俄方工程专家组最终技术评估决议):",
     "❌ STRICTLY REJECTED FOR PISTON RODS #3 AND #15 (UNACCEPTABLE RISK IN HEAVY HYDRAULIC SERVICE):\n"
     "1) Dynamic High-Pressure Delamination: Operating hydraulic pressure is 250–350 bar (25–35 MPa). Brush plating lacks the deep metallurgical bond of thermo-treated bath chromium. Under cyclic pressure and sliding friction against guide rings and seals, brush plating will blister, peel, and delaminate.\n"
     "2) Catastrophic System Damage: Flaked-off hard chromium particles circulate in hydraulic oil, instantly scoring the precision mirror-finish of the honed cylinder tube (Ra 0.2 µm) and tearing polyurethane seals.\n"
     "3) Low Hardness Remains Unfixed: Rod #15 core hardness is only 45.7 HRC and Rod #3 is 46.5 HRC (drawing requires ≥ 50 HRC). Brush plating cannot restore core induction hardness. Rod #3 additionally has a massive 850 µm chrome surge.\n"
     "CONCLUSION: Rods #1, #3, and #15 remain CONFIRMED SCRAP (最终报废). Brush plating on sliding surfaces is strictly forbidden.",
     160)
]

def clean_trans(text):
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
    if "编号" in s:
        for i in range(1, 17):
            if s == f"编号{i}":
                return f"Rod #{i}"
    if "两头300左右的是179.89" in s:
        return "179.92,\nEnds ~300mm: 179.89"
    if "179.957" in s and "-0.043" in s:
        return "179.957 (-0.043)\n179.917 (-0.083)"
    if "179.85" in s and "-0.05" in s:
        return "179.85 (-0.05)\n179.804 (-0.096)"
    if s == "0\n+0.15":
        return "+0.15 / 0"
    return s

def build_perfect_en_workbook(src_file, dest_file):
    wb_src = openpyxl.load_workbook(src_file)
    ws_src = wb_src['Chinese words'] if 'Chinese words' in wb_src.sheetnames else wb_src.worksheets[0]
    
    wb_new = openpyxl.Workbook()
    ws = wb_new.active
    ws.title = "Inspection_&_Repair_EN"
    
    # Grid lines visible
    ws.views.sheetView[0].showGridLines = True
    
    # 1. Set column widths
    col_widths = {
        'A': 8.0,   # Item
        'B': 24.0,  # Parameter / Dimension
        'C': 24.0,  # Tolerance
        'D': 10.5, 'E': 10.5, 'F': 10.5, 'G': 10.5, 'H': 10.5, 'I': 10.5,
        'J': 10.5, 'K': 10.5, 'L': 10.5, 'M': 13.5, 'N': 10.5, 'O': 10.5,
        'P': 10.5, 'Q': 10.5, 'R': 10.5, 'S': 10.5,
        'T': 25.0,  # Measuring Tool
        'U': 34.0,  # Factory Proposal
        'V': 45.0   # Russian Verdict
    }
    for col_let, w in col_widths.items():
        ws.column_dimensions[col_let].width = w

    # 2. Row heights
    row_heights = {
        1: 36.0, 2: 12.0, 3: 26.0, 4: 24.0, 5: 20.0,
        6: 52.0, 7: 24.0, 8: 28.0, 9: 25.0, 10: 25.0,
        11: 25.0, 12: 25.0, 13: 36.0, 14: 25.0, 15: 36.0,
        16: 25.0, 17: 25.0, 18: 25.0, 19: 25.0, 20: 25.0,
        21: 32.0, 22: 24.0, 23: 14.0, 24: 28.0
    }
    for r, h in row_heights.items():
        ws.row_dimensions[r].height = h

    # Borders & Fills
    thin_border = Border(
        left=Side(style='thin', color='B0C4DE'),
        right=Side(style='thin', color='B0C4DE'),
        top=Side(style='thin', color='B0C4DE'),
        bottom=Side(style='thin', color='B0C4DE')
    )
    header_fill = PatternFill(fill_type='solid', start_color='D9E1F2', end_color='D9E1F2')
    sub_fill = PatternFill(fill_type='solid', start_color='F2F2F2', end_color='F2F2F2')
    proposal_hdr_fill = PatternFill(fill_type='solid', start_color='FCE4D6', end_color='FCE4D6')
    verdict_hdr_fill = PatternFill(fill_type='solid', start_color='C6D9F1', end_color='C6D9F1')

    # 3. Explicit clean merges (NO OVERLAPS!)
    merges_list = [
        "A1:V1",    # Title
        "A3:G3",    # Part Name
        "H3:L3",    # Date
        "M3:T3",    # Quantity
        "U3:V3",    # Note
        "A4:A5",    # Item
        "B4:B5",    # Parameter
        "C4:C5",    # Tolerance
        "D4:S4",    # Measured Values Header
        "T4:T5",    # Tool
        "U4:U5",    # Proposal
        "V4:V5",    # Verdict
        "A21:K21",  # Inspector
        "L21:V21",  # Signature
        "B22:V22",  # Note on Rod #1
        "B24:V24"   # Tech section header
    ]
    for m in merges_list:
        ws.merge_cells(m)

    # 4. Fill Table Title & Metadata
    ws.cell(1, 1).value = "MASTER INSPECTION DATA & FACTORY REPAIR PROPOSALS (16 RODS Ø180x2574 mm)"
    ws.cell(1, 1).font = Font(name='Arial', size=13, bold=True, color='1F4E78')
    ws.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center')

    ws.cell(3, 1).value = clean_trans(ws_src.cell(3, 1).value)
    ws.cell(3, 1).font = Font(name='Arial', size=9.5, bold=True)
    ws.cell(3, 1).alignment = Alignment(horizontal='left', vertical='center')

    ws.cell(3, 8).value = clean_trans(ws_src.cell(3, 8).value)
    ws.cell(3, 8).font = Font(name='Arial', size=9.5)
    ws.cell(3, 8).alignment = Alignment(horizontal='center', vertical='center')

    ws.cell(3, 13).value = clean_trans(ws_src.cell(3, 13).value)
    ws.cell(3, 13).font = Font(name='Arial', size=9.5)
    ws.cell(3, 13).alignment = Alignment(horizontal='center', vertical='center')

    ws.cell(3, 21).value = "Drawing: 20.11.32.67.068 | Material: AISI 431"
    ws.cell(3, 21).font = Font(name='Arial', size=9.0, italic=True, color='595959')
    ws.cell(3, 21).alignment = Alignment(horizontal='center', vertical='center')

    # 5. Table Headers
    ws.cell(4, 1).value = "Item"
    ws.cell(4, 2).value = "Parameter / Dimension"
    ws.cell(4, 3).value = "Drawing Tolerance"
    ws.cell(4, 4).value = "Inspection Results (Measured Values across 16 Rods)"
    ws.cell(4, 20).value = "Measuring Tool"
    ws.cell(4, 21).value = "Factory Proposed Repair / Modification (准备修改到什么数值)"
    ws.cell(4, 22).value = "Russian Engineering Verdict & Risk Analysis (Решение РФ)"

    for i in range(1, 17):
        c_rod = ws.cell(5, 3 + i)
        c_rod.value = f"Rod #{i}"
        c_rod.font = Font(name='Arial', size=9.0, bold=True, color='002060')
        c_rod.alignment = Alignment(horizontal='center', vertical='center')
        c_rod.fill = header_fill
        c_rod.border = thin_border

    # Format header cells
    for c_idx in [1, 2, 3, 4, 20]:
        c = ws.cell(4, c_idx)
        c.font = Font(name='Arial', size=9.5, bold=True, color='002060')
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        c.fill = header_fill
        c.border = thin_border

    ws.cell(4, 21).font = Font(name='Arial', size=9.5, bold=True, color='C65911')
    ws.cell(4, 21).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.cell(4, 21).fill = proposal_hdr_fill
    ws.cell(4, 21).border = thin_border

    ws.cell(4, 22).font = Font(name='Arial', size=9.5, bold=True, color='1F497D')
    ws.cell(4, 22).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.cell(4, 22).fill = verdict_hdr_fill
    ws.cell(4, 22).border = thin_border

    # 6. Fill Data Rows (Rows 6 to 20)
    for r in range(6, 21):
        for c in range(1, 22):
            val = ws_src.cell(r, c).value
            t_val = clean_trans(val)
            dest = ws.cell(r, c)
            dest.value = t_val
            dest.font = Font(name='Arial', size=9.0)
            dest.border = thin_border
            
            # Alignments
            if c == 1:
                dest.alignment = Alignment(horizontal='center', vertical='center')
            elif c == 2:
                dest.alignment = Alignment(horizontal='left', vertical='center')
            elif c == 3:
                dest.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            elif 4 <= c <= 19:
                dest.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            elif c == 20:
                dest.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
            elif c == 21:
                dest.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
                if t_val:
                    dest.fill = PatternFill(fill_type='solid', start_color='FFF2CC', end_color='FFF2CC')
                    dest.font = Font(name='Arial', size=9.0, bold=True)

        # Col V (Verdict)
        c_v = ws.cell(r, 22)
        c_v.border = thin_border
        if r in ENGINEERING_VERDICTS:
            verdict_text, fill_color = ENGINEERING_VERDICTS[r]
            c_v.value = verdict_text
            c_v.fill = PatternFill(fill_type='solid', start_color=fill_color, end_color=fill_color)
            c_v.font = Font(name='Arial', size=8.5, bold=True if ('REJECTED' in verdict_text or 'STOP' in verdict_text) else False)
            c_v.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        else:
            c_v.value = "— No rework proposed (Standard tolerance or passed)"
            c_v.font = Font(name='Arial', size=8.5, italic=True, color='7F7F7F')
            c_v.alignment = Alignment(horizontal='left', vertical='center')

    # 7. Signatures Row 21
    c_insp = ws.cell(21, 1)
    c_insp.value = "QC Inspector: Wang Xiuyu (汪秀玉)  |  Inspection Date: 2026-09-18"
    c_insp.font = Font(name='Arial', size=9.5, bold=True)
    c_insp.alignment = Alignment(horizontal='left', vertical='center')
    c_insp.border = thin_border

    c_sig = ws.cell(21, 12)
    c_sig.value = "Company Authorized Signature & Official Seal: [  DEZHOU ALEXDA / FACTORY QC  ]"
    c_sig.font = Font(name='Arial', size=9.5, italic=True)
    c_sig.alignment = Alignment(horizontal='left', vertical='center')
    c_sig.border = thin_border

    # 8. Note Row 22
    c_n = ws.cell(22, 2)
    c_n.value = "Note: Measured surface roughness of chrome layer on Rod #1 is Ra 0.093 µm (Specification: Ra ≤ 0.30 µm — PASS)"
    c_n.font = Font(name='Arial', size=9.0, italic=True, bold=True, color='0070C0')
    c_n.alignment = Alignment(horizontal='left', vertical='center')
    c_n.fill = PatternFill(fill_type='solid', start_color='F2F2F2', end_color='F2F2F2')
    c_n.border = thin_border

    # 9. Technology Header Row 24
    c_th = ws.cell(24, 2)
    c_th.value = "FACTORY TECHNICAL PROPOSAL REVIEW: SELECTIVE BRUSH ELECTROPLATING (电刷镀技术说明与俄方技术决议)"
    c_th.font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    c_th.alignment = Alignment(horizontal='center', vertical='center')
    c_th.fill = PatternFill(fill_type='solid', start_color='C00000', end_color='C00000') # Dark Red Header

    # 10. Technology Detailed Rows (Rows 25 to 30) - EACH ROW SEPARATELY MERGED B..V!
    for idx, (title, content, r_height) in enumerate(TECH_SECTIONS, start=25):
        ws.merge_cells(f"B{idx}:V{idx}")
        ws.row_dimensions[idx].height = float(r_height)
        
        cell = ws.cell(idx, 2)
        cell.value = f"{title}\n{content}"
        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
        cell.border = thin_border
        
        if idx == 30: # Russian verdict block
            cell.font = Font(name='Arial', size=9.0, bold=True, color='9C0006')
            cell.fill = PatternFill(fill_type='solid', start_color='FFC7CE', end_color='FFC7CE') # Light Red Alert
        else:
            cell.font = Font(name='Arial', size=9.0)
            cell.fill = PatternFill(fill_type='solid', start_color='FAFAFA' if idx % 2 == 1 else 'FFFFFF')

    # Save to destination
    wb_new.save(dest_file)
    print(f"Successfully generated clean workbook: {dest_file}")

def main():
    src_file = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-try to repare.xlsx"
    dest_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-try to repare_EN.xlsx"
    
    proj_dir = r"C:\Codex_Personal\projects\Price creating\Договор_62230426_Штоки_и_Трубы\reports"
    os.makedirs(proj_dir, exist_ok=True)
    dest_proj = os.path.join(proj_dir, "DATASHEET ROD-try to repare_EN.xlsx")
    
    build_perfect_en_workbook(src_file, dest_dl)
    shutil.copy2(dest_dl, dest_proj)
    print(f"Synced to project: {dest_proj}")
    
    # Also update DATASHEET ROD-try to repare.xlsx with this clean sheet as Sheet 1
    wb_combo = openpyxl.load_workbook(src_file)
    if 'Inspection_&_Repair_EN' in wb_combo.sheetnames:
        del wb_combo['Inspection_&_Repair_EN']
        
    wb_clean = openpyxl.load_workbook(dest_dl)
    ws_clean = wb_clean.active
    
    ws_combo = wb_combo.create_sheet(title='Inspection_&_Repair_EN', index=0)
    
    # Copy from ws_clean to ws_combo
    ws_combo.views.sheetView[0].showGridLines = True
    for rng in ws_clean.merged_cells.ranges:
        ws_combo.merge_cells(str(rng))
        
    for r in range(1, ws_clean.max_row + 1):
        h = ws_clean.row_dimensions[r].height
        if h:
            ws_combo.row_dimensions[r].height = h
            
    for c in range(1, ws_clean.max_column + 1):
        col_let = get_column_letter(c)
        w = ws_clean.column_dimensions[col_let].width
        if w:
            ws_combo.column_dimensions[col_let].width = w
            
    for r in range(1, ws_clean.max_row + 1):
        for c in range(1, ws_clean.max_column + 1):
            sc = ws_clean.cell(r, c)
            dc = ws_combo.cell(r, c)
            if type(dc).__name__ != 'MergedCell':
                dc.value = sc.value
            if sc.font:
                dc.font = Font(name=sc.font.name, size=sc.font.size, bold=sc.font.bold, italic=sc.font.italic, color=sc.font.color)
            if sc.alignment:
                dc.alignment = Alignment(horizontal=sc.alignment.horizontal, vertical=sc.alignment.vertical, wrap_text=sc.alignment.wrap_text)
            if sc.border:
                dc.border = Border(left=sc.border.left, right=sc.border.right, top=sc.border.top, bottom=sc.border.bottom)
            if sc.fill and sc.fill.fill_type:
                dc.fill = PatternFill(fill_type=sc.fill.fill_type, start_color=sc.fill.start_color, end_color=sc.fill.end_color)

    wb_combo.save(src_file)
    print(f"Updated combo file: {src_file}")
    
    shutil.copy2(src_file, os.path.join(proj_dir, "DATASHEET ROD-try to repare.xlsx"))
    print("Synced combo file to project directory.")

if __name__ == "__main__":
    main()
