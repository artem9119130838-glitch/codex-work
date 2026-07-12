# Google Drive Free Renamer

This Apps Script renames files in a Google Drive folder using only Google tools:

- `DriveApp`
- `DocumentApp`
- Advanced `Drive` service for DOCX/PDF conversion
- Gemini API free tier

## Target folder

- Folder ID: `1SX1tVGJhF_RXszMwERi5glEr9j07GUzE`

## What it supports

- Google Docs: direct text read
- DOCX: converted to temporary Google Doc, then text is read
- PDF: imported with OCR, then text is read

## Safe flow

1. Open [script.google.com](https://script.google.com/)
2. Create a new Apps Script project
3. Paste code from [google_drive_free_renamer.gs](/C:/Codex_Work/Normaliztion%20Codex%20-%20Chat%20Operator/google_drive_free_renamer.gs)
4. In `Services`, enable `Drive API`
5. Put your free Gemini API key into `CONFIG.geminiApiKey`
6. Run `previewRenameFiles()`
7. Check `Executions` and logs
8. If names look correct, set `dryRun: false`
9. Run `renameFiles()`

## Important limits

- Free Gemini tier can hit rate limits, so the script pauses between calls.
- OCR for scanned PDFs is imperfect.
- First run is capped by `maxFilesPerRun` for safety.
- Existing normalized files are skipped by pattern.

## Recommended first edits

- Keep `dryRun: true` on the first run
- Start with `maxFilesPerRun: 5`
- Adjust `allowedTags` if your folder has a narrower taxonomy
