@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\geo-obra-run.ps1"
pause
