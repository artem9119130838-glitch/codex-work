# Domain: Google Calendar

## Role

Google Calendar is used or planned for:

- work task capture;
- cross-device visibility;
- voice-created reminders;
- n8n source events;
- possible bridge between phone and Bitrix.

## Known account

From exports:

```text
artem9119130838@gmail.com
```

## Known directions

### n8n Google Calendar -> Bitrix

Intended source calendar:

```text
Рабочие задачи
```

Calendar ID: `unknown`

Google OAuth redirect for n8n:

```text
https://n8n.3develop.ru/rest/oauth2-credential/callback
```

### Voice capture

Earlier design:

- Android/OnePlus input;
- Apps Script web app;
- route to Work or Personal calendar;
- optional MacroDroid trigger;
- future n8n involvement.

## Known pitfalls

- Calendar name and calendar ID are not the same.
- Apps Script web app access must be configured carefully.
- MacroDroid may receive login HTML instead of JSON if access/auth is wrong.
- Duplicate birthday/calendar cleanup requires careful UID handling.
