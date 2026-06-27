@echo off
cd /d "%~dp0"
python "%~dp0start_nyx_web_demo.py"
if not errorlevel 1 goto end
echo.
echo [ERROR] Launcher failed. Please send this window text to Codex.
pause
:end
