# Current State

Project root: E:\Codex_Work
Primary task: AST GOZ automation in Firefox with the existing profile and extensions.

## Main working folder
- scripts/astgoz_tampermonkey

## Main script
- scripts/astgoz_tampermonkey/astgoz_dom_runner.user.js

## What is already known
- Hidden row links can be used instead of hover-menu clicking.
- `Запрос документации` and `Подготовить документы` work when extracted from the current row DOM.
- The request page checkbox can be set through DOM events.
- Modal `Подписать и отправить` works with a direct button click.
- After prepare, the site may show cancel, or may require returning without cancel.

## Main fragile areas
- Return path after unload and after prepare.
- Registry row state changes after a lot is processed.
- Different menu state before and after documentation request/download.

## How to continue from another computer
1. Mount E:\Codex_Work (or the same network share) on that computer.
2. Start a new Codex/chat session with the workspace opened from E:\Codex_Work.
3. Continue from scripts/astgoz_tampermonkey and this file.
