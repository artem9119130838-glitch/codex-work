# Asset: OnePlus Phone

## Role

The phone is part of future automation around:

- voice capture;
- reminders;
- task creation;
- calendar routing;
- possibly n8n-triggered workflows.

## Known direction

Previous work explored:

- Android voice-to-calendar automation;
- Google Calendar as cross-device storage;
- Apps Script web app;
- MacroDroid as possible Android trigger;
- future n8n routing.

## Stable design preference

Use Google Calendar or n8n as the central integration layer instead of a closed local task app when cross-device automation matters.

## Known pitfalls

- MacroDroid voice recognition quality may be insufficient for production.
- Apps Script deployment must be a web app, not only a library.
- Web app access settings are security-sensitive.
- Android Private DNS can interfere with router/DNS routing tests.

## To document later

- Exact OnePlus model.
- Android version.
- Installed automation apps.
- Preferred voice assistant.
- Which calendars/tasks should be created from phone input.
