@echo off
setlocal
cd /d "%~dp0"

for /f "delims=" %%F in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '.\reports' -Filter '*.xlsx' | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName"') do set "LATEST=%%F"

if not defined LATEST (
  echo No XLSX report found in reports folder.
  pause
  exit /b 1
)

start "" "%LATEST%"
exit /b 0
