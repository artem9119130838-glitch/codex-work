import json
from tilda_session import get_session

def check_project_details(project_id="5807910"):
    session = get_session()
    
    session.headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'https://tilda.ru/projects/?projectid={project_id}',
    })
    
    # Try POST
    print("Testing /projects/get/getprojects/ with projectid parameter...")
    r = session.post("https://tilda.ru/projects/get/getprojects/", data={'projectid': project_id})
    print("Status:", r.status_code)
    try:
        data = r.json()
        print("Success! Response is JSON.")
        with open("C:/Codex_Personal/projects/tilda_migration/project_details_test.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Keys in JSON:", data.keys())
    except Exception as e:
        print("Not JSON. Snippet:", r.text[:200])

if __name__ == "__main__":
    check_project_details()
