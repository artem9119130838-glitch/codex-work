import os
import csv
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Если вы измените эти области доступа, удалите файл token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

def main():
    target_email = "25chulpan@gmail.com"
    credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
    
    if not os.path.exists(credentials_path):
        print(f"Ошибка: Файл '{credentials_path}' не найден!")
        print("Пожалуйста, создайте учетные данные OAuth 2.0 (клиент для ПК) в Google Cloud Console,")
        print("скачайте JSON-файл и сохраните его как 'credentials.json' в папке scripts.")
        sys.exit(1)
        
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        print("Сканирование папок на Google Диске...")
        folders = []
        page_token = None
        
        while True:
            # Запрашиваем только папки, которые не в корзине
            query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            # Важно запросить permissions, так как там содержатся email и роли
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, permissions, webViewLink)",
                pageSize=100,
                pageToken=page_token
            ).execute()
            
            items = results.get('files', [])
            folders.extend(items)
            
            page_token = results.get('nextPageToken', None)
            if not page_token:
                break

        print(f"Всего найдено папок: {len(folders)}")
        print(f"Анализ прав доступа для '{target_email}'...")
        
        access_list = []
        
        for folder in folders:
            permissions = folder.get('permissions', [])
            for perm in permissions:
                email = perm.get('emailAddress', '').lower()
                if email == target_email.lower():
                    role = perm.get('role')
                    # Переводим роли на русский язык
                    role_ru = "Неизвестно"
                    if role in ['owner', 'organizer']:
                        role_ru = "Владелец"
                    elif role in ['writer', 'fileOrganizer']:
                        role_ru = "Редактор"
                    elif role in ['commenter']:
                        role_ru = "Комментатор"
                    elif role in ['reader']:
                        role_ru = "Просмотр"
                        
                    access_list.append({
                        'name': folder.get('name'),
                        'role': role_ru,
                        'url': folder.get('webViewLink'),
                        'id': folder.get('id')
                    })
                    break # Переходим к следующей папке

        # Сортируем: сначала редакторы, потом просмотр
        access_list.sort(key=lambda x: x['role'])
        
        # Выводим в консоль
        if not access_list:
            print(f"\nПользователь '{target_email}' не имеет прямого доступа ни к одной папке.")
        else:
            print("\nРезультаты анализа:")
            print("-" * 80)
            print(f"{'Название папки':<40} | {'Права доступа':<15}")
            print("-" * 80)
            for item in access_list:
                print(f"{item['name'][:40]:<40} | {item['role']:<15}")
            print("-" * 80)
            
            # Сохраняем в CSV
            csv_path = os.path.join(os.path.dirname(__file__), 'chulpan_access_report.csv')
            with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Название папки', 'Роль доступа', 'Ссылка', 'ID папки'])
                for item in access_list:
                    writer.writerow([item['name'], item['role'], item['url'], item['id']])
            print(f"\nОтчет сохранен в файл: {csv_path}")

    except HttpError as error:
        print(f"Произошла ошибка API: {error}")

if __name__ == '__main__':
    main()
