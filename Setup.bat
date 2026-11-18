@echo off
rem Setup step: double-click this once after extracting Travel Guardian.
rem It runs install_nmap.ps1, which downloads and starts the official Nmap installer.
rem "-ExecutionPolicy Bypass" lets this one script run even though Windows blocks
rem PowerShell scripts by default; it doesn't change any Windows setting.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_nmap.ps1"
pause
