import os, sys, pypdf, re

sys.stdout.reconfigure(encoding='utf-8')
dir_path = r'C:\Codex_Personal\projects\HR\Китайский снабженец\简历包'

for f in sorted(os.listdir(dir_path)):
    p = os.path.join(dir_path, f)
    if f.endswith('.pdf'):
        try:
            r = pypdf.PdfReader(p)
            for page_idx, page in enumerate(r.pages):
                txt = page.extract_text() or ''
                # remove spaces and punctuation
                clean_digits = re.sub(r'\D', '', txt)
                if '465387856' in clean_digits:
                    print(f"FOUND EXACT in {f} page {page_idx}!")
                # check annotations / links
                if '/Annots' in page:
                    annots = page['/Annots']
                    for a in annots:
                        obj = a.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = obj['/A']['/URI']
                            if '465' in uri:
                                print(f"Found in URI of {f}: {uri}")
        except Exception as e:
            pass

print("Search completed.")
