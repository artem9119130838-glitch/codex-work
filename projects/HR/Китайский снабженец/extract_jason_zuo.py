import io
import sys
from pathlib import Path
from pypdf import PdfReader

sys.stdout.reconfigure(encoding="utf-8")

pdf_path = Path(r"D:\Документы Victus\Рабочее\Сотрудники\Дэвид\Jason Zuo 个人简历.pdf")
out_dir = Path(r"C:\Codex\projects\HR\Китайский снабженец\jason_zuo_pages")
out_dir.mkdir(exist_ok=True)

with open(pdf_path, "rb") as f:
    data = f.read()

# Fix xref if corrupted
pos = data.rfind(b"xref\ntrailer\n")
if pos != -1:
    data = data[:pos]

reader = PdfReader(io.BytesIO(data))
print(f"Total pages: {len(reader.pages)}")

# Also save the clean fixed PDF
fixed_pdf = Path(r"C:\Codex\projects\HR\Китайский снабженец\Jason_Zuo_fixed.pdf")
fixed_pdf.write_bytes(data)
print(f"Fixed PDF saved to: {fixed_pdf} ({len(data)} bytes)")

img_count = 0
for p_idx, page in enumerate(reader.pages):
    # Try text
    txt = page.extract_text()
    if txt and txt.strip():
        print(f"Page {p_idx+1} has text: {len(txt)} chars")
        (out_dir / f"page_{p_idx+1}.txt").write_text(txt, encoding="utf-8")
    
    # Try images
    res = page.get("/Resources")
    if not res:
        continue
    res_obj = res.get_object() if hasattr(res, "get_object") else res
    xObject = res_obj.get("/XObject")
    if not xObject:
        continue
    xObject = xObject.get_object() if hasattr(xObject, "get_object") else xObject
    
    for obj_name in xObject:
        obj = xObject[obj_name]
        obj = obj.get_object() if hasattr(obj, "get_object") else obj
        if obj.get("/Subtype") == "/Image":
            filter_type = obj.get("/Filter")
            w = obj.get("/Width")
            h = obj.get("/Height")
            print(f"Page {p_idx+1} image {obj_name}: Filter={filter_type}, W={w}, H={h}")
            
            # If DCTDecode, raw bytes are JPEG
            if filter_type == "/DCTDecode":
                raw_bytes = obj._data
                target_file = out_dir / f"page_{p_idx+1}.jpg"
                target_file.write_bytes(raw_bytes)
                print(f"  Saved JPEG: {target_file} ({len(raw_bytes)} bytes)")
                img_count += 1
            else:
                try:
                    data_bytes = obj.get_data()
                    target_file = out_dir / f"page_{p_idx+1}.bin"
                    target_file.write_bytes(data_bytes)
                    print(f"  Saved raw stream: {target_file} ({len(data_bytes)} bytes)")
                    img_count += 1
                except Exception as e:
                    print(f"  Could not get data: {e}")

print(f"Total extracted: {img_count} images")
