import json
from tilda_session import get_session

def fetch_all():
    session = get_session()
    session.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
    })
    
    # 1. Get projects list
    r_projects = session.post("https://tilda.ru/projects/get/getprojects/")
    projects_data = r_projects.json()
    projects = projects_data.get("projects", [])
    
    all_pages = {}
    
    for proj in projects:
        proj_id = proj.get("id")
        proj_title = proj.get("title")
        print(f"Fetching details for Project {proj_id} ({proj_title})...")
        
        session.headers.update({'Referer': f'https://tilda.ru/projects/?projectid={proj_id}'})
        r_det = session.post("https://tilda.ru/projects/get/getprojects/", data={'projectid': proj_id})
        det_data = r_det.json()
        
        pages = det_data.get("pages", [])
        print(f"  Found {len(pages)} pages.")
        
        for page in pages:
            p_id = page.get("id")
            page['project_title'] = proj_title
            all_pages[p_id] = page
            
    # Save all pages to json
    with open("C:/Codex_Personal/projects/tilda_migration/all_discovered_pages.json", "w", encoding="utf-8") as f:
        json.dump(all_pages, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(all_pages)} pages across all projects.")
    
    # Check if target page exists
    target_page_id = "41294814"
    if target_page_id in all_pages:
        t_page = all_pages[target_page_id]
        print(f"\nFOUND TARGET PAGE {target_page_id}:")
        print(f"  Title: {t_page.get('title')}")
        print(f"  Project: {t_page.get('project_title')} (ID: {t_page.get('projectid')})")
        print(f"  Alias/URL: {t_page.get('url')}")
    else:
        print(f"\nTarget page {target_page_id} NOT FOUND in active projects.")

if __name__ == "__main__":
    fetch_all()
