@echo off
echo === CTF AI Helper - DeepSeek Coder V2 ===
echo.
echo Enter your forensics tool request:
set /p prompt="> "
echo.
echo Sending prompt to Ollama...
ollama run deepseek-coder-v2:latest "%prompt%"
echo.
pause