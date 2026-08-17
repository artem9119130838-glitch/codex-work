@echo off
setlocal
cd /d "%~dp0"

echo Running weekly inventory...
powershell -ExecutionPolicy Bypass -File ".\make_snapshot.ps1"
if errorlevel 1 goto :fail

for /f %%A in ('dir /b /a-d ".\snapshots\*.csv" ^| find /c /v ""') do set SNAPCOUNT=%%A

if not defined SNAPCOUNT set SNAPCOUNT=0

if %SNAPCOUNT% LSS 2 (
  echo.
  echo First snapshot created. Comparison will start from the second run.
  powershell -ExecutionPolicy Bypass -File ".\export_installed_programs.ps1"
  if errorlevel 1 goto :fail
  echo.
  echo Weekly inventory completed successfully.
  pause
  exit /b 0
)

powershell -ExecutionPolicy Bypass -File ".\compare_snapshots.ps1"
if errorlevel 1 goto :fail

powershell -ExecutionPolicy Bypass -File ".\export_installed_programs.ps1"
if errorlevel 1 goto :fail

echo.
echo Weekly inventory completed successfully.
pause
exit /b 0

:fail
echo.
echo Weekly inventory failed.
pause
exit /b 1
