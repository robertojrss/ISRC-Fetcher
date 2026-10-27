@echo off
echo Installing dependencies...
python -m pip install -r requirements.txt pyinstaller
echo.
echo Building the .exe...
python -m PyInstaller --onefile --console --name ISRC-Fetcher --collect-all ytmusicapi isrc_fetcher.py
echo.
echo Done! The executable is at dist\ISRC-Fetcher.exe
pause
