---
name: email_ai_pipelines
description: Интеграция n8n с почтой и Bitrix24, парсинг Excel/PDF вложений, проверка прав на Диске и поиск контрагентов по OData 1С.
---

# Навык: ИИ-пайплайны почты (email_ai_pipelines)

Этот навык используется при проектировании и отладке почтовых роботов n8n, парсинге входящих вложений и интеграции данных в CRM (Bitrix24) и ERP (1C).

## 1. Регулярные выражения и очистка входящих писем

### Удаление цитирования в цепочках писем (JS-код для n8n Code Node):
При обработке входящих писем ИИ обязан очистить текст от истории переписки, чтобы сэкономить токены:
```javascript
// Вход: text - тело письма
let cleanText = text;

// Регулярные выражения для отсечения цитирования
const patterns = [
  /-----Original Message-----/i,
  /________________________________/i,
  /От кого:/i,
  /From:/i,
  /Sent:/i,
  /Date:/i,
  /Воскресенье, |Понедельник, |Вторник, |Среда, |Четверг, |Пятница, |Суббота, /i
];

for (let pattern of patterns) {
  const index = cleanText.search(pattern);
  if (index !== -1) {
    cleanText = cleanText.substring(0, index);
  }
}

return { cleanText: cleanText.trim() };
```

### Парсинг ИНН и контактов из тела письма:
*   ИНН ЮЛ (10 цифр): `(?<!\d)\d{10}(?!\d)`
*   ИНН ИП (12 цифр): `(?<!\d)\d{12}(?!\d)`
*   Email: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
*   Телефон (RU): `(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}`

---

## 2. Проверка прав Google Drive (check_drive_access.py)

Если письмо содержит ссылку на Google Диск, ИИ обязан выполнить проверку доступов с помощью готового Python-скрипта (или его логики):
```python
import sys
import googleapiclient.discovery
from google.oauth2 import service_account

def check_folder_access(folder_id, credentials_path):
    try:
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, 
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        service = googleapiclient.discovery.build('drive', 'v3', credentials=creds)
        
        # Проверка существования и метаданных папки
        folder = service.files().get(fileId=folder_id, fields="id, name, permissions").execute()
        print(f"Доступ подтвержден к папке: {folder.get('name')}")
        return True
    except Exception as e:
        print(f"Ошибка доступа к папке {folder_id}: {e}", file=sys.stderr)
        return False
```

## 2.1. Быстрый аудит прав доступа через Google Apps Script (без таймаутов и ошибок памяти)

При проведении аудита доступов на больших корпоративных дисках (5 ТБ+ или десятки тысяч папок) стандартный рекурсивный обход папок через `DriveApp` приводит к превышению лимита времени выполнения (6 минут) или ошибке `Out of memory error` из-за переполнения оперативной памяти Apps Script.

Для стабильной и быстрой работы (за секунды) используйте следующие оптимизированные алгоритмы:

### А. Точечный аудит доступов конкретного пользователя (с путями папок)
Этот алгоритм запрашивает через Drive API v3 только те папки, к которым у целевого пользователя есть права, а затем «лениво» строит полные пути к ним, используя кэширование родительских каталогов в памяти.

```javascript
function runUserAccessAuditWithPaths() {
  var targetEmail = "user@example.com"; // Укажите email для проверки
  var results = [];
  var pageToken = null;
  var rootId = DriveApp.getRootFolder().getId();
  
  // Кэш для папок, чтобы не запрашивать одних и тех же родителей повторно
  var folderCache = {};
  
  Logger.log("Шаг 1. Быстрый поиск папок, к которым у " + targetEmail + " есть доступ...");
  
  var query = "('" + targetEmail + "' in readers or '" + targetEmail + "' in writers) " +
              "and mimeType = 'application/vnd.google-apps.folder' and trashed = false";
              
  do {
    var optionalArgs = {
      q: query,
      fields: "nextPageToken, files(id, name, webViewLink, permissions, parents)",
      pageSize: 100,
      pageToken: pageToken
    };
    
    var response = Drive.Files.list(optionalArgs);
    var files = response.files;
    
    if (files && files.length > 0) {
      for (var i = 0; i < files.length; i++) {
        var folder = files[i];
        
        folderCache[folder.id] = {
          name: folder.name,
          parentId: folder.parents && folder.parents.length > 0 ? folder.parents[0] : null
        };
        
        var roleRu = "Просмотр";
        if (folder.permissions) {
          for (var j = 0; j < folder.permissions.length; j++) {
            var perm = folder.permissions[j];
            if (perm.emailAddress && perm.emailAddress.toLowerCase() === targetEmail.toLowerCase()) {
              if (perm.role === "writer" || perm.role === "fileOrganizer") {
                roleRu = "Редактор";
              }
              break;
            }
          }
        }
        
        results.push({
          id: folder.id,
          name: folder.name,
          role: roleRu,
          url: folder.webViewLink,
          parentId: folder.parents && folder.parents.length > 0 ? folder.parents[0] : null
        });
      }
    }
    pageToken = response.nextPageToken;
  } while (pageToken);
  
  Logger.log("Найдено папок с доступом: " + results.length);
  Logger.log("Шаг 2. Восстановление полных путей...");
  
  function getFolderInfo(id) {
    if (folderCache[id]) {
      return folderCache[id];
    }
    try {
      var res = Drive.Files.get(id, { fields: "name, parents" });
      var info = {
        name: res.name,
        parentId: res.parents && res.parents.length > 0 ? res.parents[0] : null
      };
      folderCache[id] = info;
      return info;
    } catch (e) {
      return null;
    }
  }
  
  for (var i = 0; i < results.length; i++) {
    var item = results[i];
    var pathParts = [item.name];
    var currentParentId = item.parentId;
    var visited = {};
    
    while (currentParentId && currentParentId !== rootId && !visited[currentParentId]) {
      visited[currentParentId] = true;
      var parentInfo = getFolderInfo(currentParentId);
      if (parentInfo) {
        pathParts.unshift(parentInfo.name);
        currentParentId = parentInfo.parentId;
      } else {
        break;
      }
    }
    
    pathParts.unshift("Мой диск");
    item.fullPath = pathParts.join(" / ");
  }
  
  var csvContent = "\uFEFFПолный путь к папке,E-mail пользователя,Роль доступа,Ссылка\n";
  results.forEach(function(row) {
    csvContent += `"${row.fullPath.replace(/"/g, '""')}","${targetEmail}","${row.role}","${row.url}"\n`;
  });
  
  DriveApp.createFile("User_Access_Report_Paths.csv", csvContent, MimeType.PLAIN_TEXT);
  Logger.log("Отчет сохранен в файл: User_Access_Report_Paths.csv");
}
```

### Б. Полный плоский аудит всех внешних доступов для всех пользователей
Этот алгоритм сканирует все папки диска страницами максимального объема (`pageSize: 1000`) для предотвращения таймаутов, и сразу выгружает из памяти нерасшаренные папки, предотвращая `Out of memory error`. На выходе создается плоская таблица, готовая для фильтрации по любому e-mail или роли в Excel.

*Требование*: Перед запуском подключить службу **Drive API v3** (Services / Службы -> Drive API).

```javascript
function runFullDriveAccessAuditAllUsers() {
  var results = [];
  var pageToken = null;
  var myEmail = Session.getActiveUser().getEmail().toLowerCase();
  var rootId = DriveApp.getRootFolder().getId();
  var folderCache = {};
  
  Logger.log("Начинаем полный оптимизированный аудит доступов для ВСЕХ пользователей...");
  
  function getFolderInfo(id) {
    if (folderCache[id]) return folderCache[id];
    try {
      var res = Drive.Files.get(id, { fields: "name, parents" });
      var info = {
        name: res.name,
        parentId: res.parents && res.parents.length > 0 ? res.parents[0] : null
      };
      folderCache[id] = info;
      return info;
    } catch (e) {
      return null;
    }
  }
  
  function buildPath(folderName, parentId) {
    var pathParts = [folderName];
    var currentParentId = parentId;
    var visited = {};
    
    while (currentParentId && currentParentId !== rootId && !visited[currentParentId]) {
      visited[currentParentId] = true;
      var parentInfo = getFolderInfo(currentParentId);
      if (parentInfo) {
        pathParts.unshift(parentInfo.name);
        currentParentId = parentInfo.parentId;
      } else {
        break;
      }
    }
    
    pathParts.unshift("Мой диск");
    return pathParts.join(" / ");
  }
  
  do {
    var optionalArgs = {
      q: "mimeType = 'application/vnd.google-apps.folder' and trashed = false",
      fields: "nextPageToken, files(id, name, webViewLink, permissions, parents)",
      pageSize: 1000, // По 1000 папок за раз
      pageToken: pageToken
    };
    
    var response = Drive.Files.list(optionalArgs);
    var files = response.files;
    
    if (files && files.length > 0) {
      for (var i = 0; i < files.length; i++) {
        var folder = files[i];
        var permissions = folder.permissions;
        
        if (permissions && permissions.length > 0) {
          var folderPath = null; 
          
          for (var j = 0; j < permissions.length; j++) {
            var perm = permissions[j];
            var email = perm.emailAddress ? perm.emailAddress.toLowerCase() : "";
            var role = perm.role;
            var type = perm.type; 
            
            if (role === "owner" || email === myEmail) continue;
            
            if (!folderPath) {
              var parentId = folder.parents && folder.parents.length > 0 ? folder.parents[0] : null;
              folderPath = buildPath(folder.name, parentId);
            }
            
            var roleRu = "Просмотр";
            if (role === "writer" || role === "fileOrganizer") roleRu = "Редактор";
            
            var userIdentifier = type === "anyone" ? "Доступ по ссылке (Anyone)" : (email || "Скрытый (" + type + ")");
            
            results.push({
              path: folderPath,
              userEmail: userIdentifier,
              accessRole: roleRu,
              url: folder.webViewLink
            });
          }
        }
      }
    }
    pageToken = response.nextPageToken;
  } while (pageToken);
  
  var csvContent = "\uFEFFПолный путь к папке,E-mail пользователя,Роль доступа,Ссылка\n";
  results.forEach(function(row) {
    csvContent += `"${row.path.replace(/"/g, '""')}","${row.userEmail.replace(/"/g, '""')}","${row.accessRole}","${row.url}"\n`;
  });
  
  DriveApp.createFile("Google_Drive_All_Users_Access_Audit.csv", csvContent, MimeType.PLAIN_TEXT);
  Logger.log("Всего расшаренных папок: " + results.length);
}
```

---

## 3. Интеграция с Bitrix24 Proxy и Fallback-логика

Во избежание засорения CRM пустыми карточками при автоматическом разборе писем, используйте следующую логику в пайплайнах:

1.  **Поиск компании по реквизитам (ИНН):**
    *   Сначала делаем запрос `crm.requisite.list` с фильтром по ИНН (`RQ_INN`).
    *   Если реквизиты найдены, привязываем сделку к существующей компании (`ENTITY_ID`).
2.  **Fallback на дефолтную компанию:**
    *   Если ИНН не найден в письме/вложениях или компания с таким ИНН отсутствует в CRM, ИИ **не должен** создавать новую компанию "Без имени".
    *   Используйте системный ID дефолтной компании (например, `COMPANY_ID = 99999` или берется из конфига) для привязки сделки.
3.  **Безопасность REST-токенов:**
    *   Все вебхуки Bitrix24 должны отправляться на локальный FastAPI прокси-шлюз (например, `http://localhost:8000/api/v1/b24/`), который подставляет авторизационные заголовки на стороне сервера. Прямая отправка токенов из n8n наружу запрещена.
4.  **Специфика формата запросов REST API (Критично):**
    *   **Запрещен JSON в теле запроса вебхуков**: Входящие вебхуки Битрикс24 не парсят JSON. Запросы к API Б24 (включая отправку сообщений и создание задач) необходимо отправлять **исключительно** в формате `application/x-www-form-urlencoded` (параметр `data=` в Python `requests` или стандартные поля формы в HTTP-ноде n8n).
    *   *Ошибка:* `requests.post(b24_url, json={"MESSAGE": "Test"})` -> Ошибка `MESSAGE_EMPTY`.
    *   *Правильно:* `requests.post(b24_url, data={"MESSAGE": "Test"})`.
5.  **Отправка системных уведомлений (алертов) создателю вебхука:**
    *   Для отправки сообщений администратору (владельцу токена вебхука, обычно `ID = 1`) запрещено использовать метод `im.message.add` на свой же ID, так как Битрикс24 скрывает такие сообщения.
    *   Необходимо использовать метод **`im.notify.personal.add`** с параметрами `USER_ID` (получатель) и `MESSAGE` (текст с поддержкой BB-кодов). Уведомление гарантированно придет в системный колокольчик в правом верхнем углу.

---

## 4. Запросы к 1С OData API

Для поиска и верификации контрагентов из писем используйте OData API 1С:
*   **Базовый URL:** `https://<1c-server>/<base>/odata/standard.odt/`
*   **Поиск по ИНН:**
    `GET /Catalog_Контрагенты?$filter=ИНН eq '<ИНН>'&$format=json`
*   **Поиск по Email/Телефону:**
    `GET /Catalog_Контрагенты?$filter=КонтактнаяИнформация/Any(x: x/АдресЭП eq '<email>')&$format=json`

---

## 5. Особенности разработки и деплоя воркфлоу n8n

### Синтаксис выражений (Expressions):
* **Правило объединения блоков**: Избегайте использования нескольких блоков `{{ }}` подряд (например, `={{ a }}{{ b }}`). Это может вызвать сбой парсера n8n и обрезание строки.
* **Решение**: Объединяйте вычисления в один JS-блок `={{ ... }}` и складывайте строки через `+`.
  * *Плохо:* `={{ $json.first_name }}{{ $json.last_name }} - {{ $json.amount }}`
  * *Хорошо:* `={{ ($json.first_name || '') + ' ' + ($json.last_name || '') + ' - ' + ($json.amount || 0) }}`

### Публикация изменений на сервере:
* Изменения в коде сценариев (JSON в Git) или в редакторе n8n сохраняются как черновики (Draft).
* **Критический шаг**: Чтобы изменения вступили в силу для внешних триггеров (вебхуки, Google Drive, почта), в веб-интерфейсе n8n в правом верхнем углу обязательно должна быть нажата кнопка **Publish** (оранжевый индикатор должен смениться на зеленый **Published**).

---

## 6. Автоматизация реанимации клиентов и холодный старт (1C Leads > 90 дней)

### 1. Фильтрация кандидатов по возрасту лида в 1С:
При отборе контактов из 1С без истории переписки (`cold_lead`) обязательно считывать `ДатаСоздания` из `raw_payload`. Контакты, созданные менее 90 дней назад, исключаются из рассылки во избежание контакта со свежими лидами в работе менеджеров.

### 2. Структура нейтрального холодного письма:
* **Услуги компании:** Перечислять комплексные возможности (оригинальное оборудование санкционных брендов SMC/Danfoss/Caterpillar, белая доставка и таможня, поиск и аудит фабрик в КНР инженерами).
* **Обязательная ссылка на Аутсорсинг ВЭД:** Органично встраивать в текст HTML-ссылку `<a href="https://longwang.ru/supplies-services-china/autsorsing-ved/" target="_blank" tabindex="-1">Аутсорсинг ВЭД</a>`.
* **Статьи и кейсы:** Встраивать смысловые ссылки на статьи из базы знаний с атрибутами `target="_blank" tabindex="-1"`.

### 3. Физические вложения в IMAP-черновики:
* Скрипт создания черновиков (`imap_tools`) обязан считывать файл PDF-презентации (`presentation_and_reference.pdf`) и прикреплять его как физическое MIME-вложение.
* Загружать письмо строго методом `mailbox.append(msg, folder='Drafts')` без отправки клиенту.

### 4. Защита доставляемости (Anti-Spam Subjects):
* Запрещено генерировать шаблонные нейтральные темы («Сотрудничество по поставкам...») — они вызывают срабатывание спам-фильтров.
* Сохранять поиск тем на основе домена (`Re: <тема_переписки>`), имитирующий естественное продолжение диалога.

### 5. Автоматическое снятие заглушки при ответе:
* При получении любого входящего письма от холодного контакта система немедленно переводит статус воронки в `replied`, запускает суммаризатор переписки `SummaryService` и перезаписывает заглушку в `client_intel` реальным аналитическим профилем клиента.
