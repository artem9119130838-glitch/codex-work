#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests
import zipfile
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from process_b24_inbound_leads import call_b24

file_ids = [117952, 118112, 118154, 118062]
for fid in file_ids:
    df = call_b24("disk.file.get", {"id": fid})
    if not df:
        print(f"File {fid} not found")
        continue
    fname = df.get("NAME")
    durl = df.get("DOWNLOAD_URL")
    print(f"\n--- File {fid}: {fname} ---")
    resp = requests.get(durl)
    out_path = os.path.join(r"C:\Codex", f"file_{fid}_{fname}")
    with open(out_path, "wb") as f:
        f.write(resp.content)
    print(f"Saved {len(resp.content)} bytes to {out_path}")
    
    # If docx, extract text:
    if fname.endswith(".docx"):
        try:
            with zipfile.ZipFile(out_path) as z:
                xml_content = z.read("word/document.xml")
                root = ET.fromstring(xml_content)
                text_parts = []
                for node in root.iter():
                    if node.tag.endswith('}t') and node.text:
                        text_parts.append(node.text)
                print("Extracted DOCX text snippet:")
                print(" ".join(text_parts)[:1000])
        except Exception as e:
            print("DOCX extract error:", e)
    elif fname.endswith(".pdf"):
        print("PDF file downloaded, size:", len(resp.content))
    elif fname.endswith(".xlsx") or fname.endswith(".xls"):
        print("Excel file downloaded, size:", len(resp.content))
    else:
        # maybe text or image
        try:
            txt = resp.content.decode("utf-8", errors="ignore")
            print("Snippet:", txt[:500])
        except:
            pass
