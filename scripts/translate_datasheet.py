# -*- coding: utf-8 -*-
"""
Script to translate 'DATASHEET ROD-3rd time inspection.xlsx' from Chinese to English.
Preserves exact data, numeric values, formatting, row heights, and borders.
Creates:
1. DATASHEET ROD-3rd time inspection_EN.xlsx
2. Updates DATASHEET ROD-3rd time inspection.xlsx with English as primary sheet and CN as secondary sheet.
3. Syncs to project directory.
"""

import os
import shutil
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

TRANSLATION_MAP = {
    # Title & Metadata
    "   检验记录表": "INSPECTION RECORD SHEET",
    "检验记录表": "INSPECTION RECORD SHEET",
    "规格及名称：活塞杆": "Part Name & Spec: Piston Rod Ø180x2574 mm (AISI 431)",
    "检验日期：2026/9/18": "Inspection Date: 2026-09-18",
    "检验数量：16件": "Inspection Quantity: 16 pcs",
    "准备修改到什么数值": "Proposed Revision / Target Value",
    
    # Headers
    "序列": "Item",
    "尺寸": "Parameter / Dimension",
    "公差": "Drawing Tolerance",
    "检验尺寸结果": "Inspection Results (Measured Values)",
    "量具": "Measuring Tool / Gauge",
    
    # Parameters (Col B)
    "Φ180": "Ø180 f7",
    "M170*4": "M170x4-6g Thread",
    "Φ179.9": "Step Ø179.9",
    "Φ171.6": "Neck Ø171.6 (-0.1)",
    "Φ164.3": "Groove Ø164.3",
    "2574": "Length 2574 mm",
    "10": "Length 10 mm (Left)",
    "8.6": "Groove Width 8.6 mm",
    "15": "Spacing 15 mm",
    "42.2": "Length 42.2 mm (Right)",
    "镀铬": "Chrome Thickness (mm)",
    "光洁度": "Surface Roughness Ra (µm)",
    "高频": "Induction Hardness (HRC)",
    "R": "Corner Radius R",
    
    # Tolerances & Values (Col C & Cells)
    "环规": "Thread Ring Gauge (Go/No-Go)",
    "合格": "PASS",
    "50-55": "50-55 HRC",
    "R0.3": "R ≤ 0.3 mm max",
    
    # Measuring tools (Col T)
    "175-200千分尺": "Micrometer 175-200 mm",
    "150-175千分尺": "Micrometer 150-175 mm",
    "游标卡尺": "Vernier Caliper",
    "5米卷尺": "5m Steel Tape Measure",
    "内槽千分尺": "Internal Groove Micrometer",
    "涂层测厚仪": "Coating Thickness Gauge",
    "光洁度、粗糙度仪": "Surface Roughness Tester",
    "硬度计手持便携式": "Portable Hardness Tester",
    
    # Footer & Notes
    "检验员：汪秀玉": "QC Inspector: Wang Xiuyu (汪秀玉)",
    "单位签字及盖章：": "Authorized Signature & Stamp:",
    "请注意 编号1的镀铬层光洁度是0.093": "Note: Surface roughness of chrome plating on Rod #1 is 0.093 µm"
}

def translate_text(text):
    if text is None:
        return None
    if not isinstance(text, str):
        return text
    
    s = text.strip()
    if s in TRANSLATION_MAP:
        return TRANSLATION_MAP[s]
    
    # Partial replacements / specifics
    if "编号" in text:
        # e.g. 编号1 -> Rod #1
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
        
    return text

def build_translated_workbook(src_path, dest_path_en, dest_path_combo=None):
    wb_orig = openpyxl.load_workbook(src_path)
    ws_orig = wb_orig['Sheet1']
    
    # 1. Create pure EN workbook
    wb_en = openpyxl.Workbook()
    ws_en = wb_en.active
    ws_en.title = "Inspection_Record_EN"
    
    # Copy merged cells
    for rng in ws_orig.merged_cells.ranges:
        ws_en.merge_cells(str(rng))
        
    # Copy row dimensions
    for r in range(1, ws_orig.max_row + 1):
        h = ws_orig.row_dimensions[r].height
        if h is not None:
            ws_en.row_dimensions[r].height = h
            
    # Set tailored column dimensions for English
    col_widths = {
        'A': 15.0,  # Item / Inspector
        'B': 24.0,  # Parameter / Dimension
        'C': 24.0,  # Tolerance
        'D': 11.0,  # Rod #1
        'E': 11.0,
        'F': 11.0,
        'G': 11.0,
        'H': 11.0,
        'I': 11.0,
        'J': 11.0,
        'K': 11.0,
        'L': 11.0,
        'M': 13.0,  # Rod #10 (has end note)
        'N': 11.0,
        'O': 11.0,
        'P': 11.0,
        'Q': 11.0,
        'R': 11.0,
        'S': 11.0,  # Rod #16
        'T': 25.0,  # Measuring Tool / Gauge
        'U': 26.0   # Proposed Revision
    }
    for col_let, w in col_widths.items():
        ws_en.column_dimensions[col_let].width = w

    # Copy cells with translation and formatting
    for r in range(1, ws_orig.max_row + 1):
        for c in range(1, ws_orig.max_column + 1):
            src_cell = ws_orig.cell(r, c)
            dest_cell = ws_en.cell(r, c)
            
            raw_val = src_cell.value
            trans_val = translate_text(raw_val)
            dest_cell.value = trans_val
            
            # Format: fonts, alignment, border, fill
            if src_cell.font:
                # Use Arial or Segoe UI for English
                font_name = 'Arial'
                dest_cell.font = Font(
                    name=font_name,
                    size=src_cell.font.size if src_cell.font.size else 10,
                    bold=src_cell.font.bold if src_cell.font.bold else False,
                    italic=src_cell.font.italic if src_cell.font.italic else False,
                    color=src_cell.font.color
                )
            
            if src_cell.alignment:
                dest_cell.alignment = Alignment(
                    horizontal=src_cell.alignment.horizontal,
                    vertical=src_cell.alignment.vertical,
                    wrap_text=src_cell.alignment.wrap_text if src_cell.alignment.wrap_text else (True if '\n' in str(trans_val) else False)
                )
            else:
                if '\n' in str(trans_val):
                    dest_cell.alignment = Alignment(wrap_text=True, vertical='center')
                    
            if src_cell.border:
                dest_cell.border = Border(
                    left=src_cell.border.left,
                    right=src_cell.border.right,
                    top=src_cell.border.top,
                    bottom=src_cell.border.bottom
                )
                
            if src_cell.fill and src_cell.fill.fill_type:
                dest_cell.fill = PatternFill(
                    fill_type=src_cell.fill.fill_type,
                    start_color=src_cell.fill.start_color,
                    end_color=src_cell.fill.end_color
                )
                
    # Style highlights:
    # Title
    ws_en.cell(1, 1).font = Font(name='Arial', size=16, bold=True, color='1F4E78')
    ws_en.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center')
    
    # Headers in Row 4 & 5
    header_fill = PatternFill(fill_type='solid', start_color='D9E1F2', end_color='D9E1F2')
    for col_idx in range(1, 21):
        for row_idx in [4, 5]:
            c = ws_en.cell(row_idx, col_idx)
            if c.value is not None:
                c.fill = header_fill
                c.font = Font(name='Arial', size=9.5, bold=True, color='002060')
                if c.alignment is None or c.alignment.horizontal is None:
                    c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # Save dedicated English file
    wb_en.save(dest_path_en)
    print(f"Saved English workbook: {dest_path_en}")
    
    # 2. Update combo workbook if requested
    if dest_path_combo:
        # Load original, rename Sheet1 to Inspection_Record_CN
        wb_combo = openpyxl.load_workbook(src_path)
        if 'Sheet1' in wb_combo.sheetnames:
            wb_combo['Sheet1'].title = 'Inspection_Record_CN'
            
        # Add translated sheet as first sheet
        ws_combo_en = wb_combo.create_sheet(title='Inspection_Record_EN', index=0)
        
        # Copy from ws_en to ws_combo_en
        for rng in ws_en.merged_cells.ranges:
            ws_combo_en.merge_cells(str(rng))
            
        for r in range(1, ws_en.max_row + 1):
            h = ws_en.row_dimensions[r].height
            if h is not None:
                ws_combo_en.row_dimensions[r].height = h
                
        for col_let, w in col_widths.items():
            ws_combo_en.column_dimensions[col_let].width = w
            
        for r in range(1, ws_en.max_row + 1):
            for c in range(1, ws_en.max_column + 1):
                cell_s = ws_en.cell(r, c)
                cell_d = ws_combo_en.cell(r, c)
                cell_d.value = cell_s.value
                if cell_s.font:
                    cell_d.font = Font(name=cell_s.font.name, size=cell_s.font.size, bold=cell_s.font.bold, color=cell_s.font.color)
                if cell_s.alignment:
                    cell_d.alignment = Alignment(horizontal=cell_s.alignment.horizontal, vertical=cell_s.alignment.vertical, wrap_text=cell_s.alignment.wrap_text)
                if cell_s.border:
                    cell_d.border = Border(left=cell_s.border.left, right=cell_s.border.right, top=cell_s.border.top, bottom=cell_s.border.bottom)
                if cell_s.fill and cell_s.fill.fill_type:
                    cell_d.fill = PatternFill(fill_type=cell_s.fill.fill_type, start_color=cell_s.fill.start_color, end_color=cell_s.fill.end_color)

        wb_combo.save(dest_path_combo)
        print(f"Updated combo workbook: {dest_path_combo}")

def main():
    src_file = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-3rd time inspection.xlsx"
    backup_file = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-3rd time inspection_ORIG_CN_BACKUP.xlsx"
    dest_en_dl = r"C:\Users\Артем\Downloads\ТЗ для гравити\DATASHEET ROD-3rd time inspection_EN.xlsx"
    
    proj_dir = r"C:\Codex\projects\Price creating\Договор_62230426_Штоки_и_Трубы\reports"
    dest_en_proj = os.path.join(proj_dir, "DATASHEET ROD-3rd time inspection_EN.xlsx")
    
    # 1. Create backup if not exists
    if not os.path.exists(backup_file):
        shutil.copy2(src_file, backup_file)
        print(f"Created factory backup: {backup_file}")
        
    # 2. Build translated files
    build_translated_workbook(src_file, dest_en_dl, dest_path_combo=src_file)
    
    # 3. Copy to project directory
    shutil.copy2(dest_en_dl, dest_en_proj)
    print(f"Synced to project directory: {dest_en_proj}")

if __name__ == "__main__":
    main()
