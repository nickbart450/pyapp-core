:: @echo off

.\dist\env\Scripts\python.exe .\install_check.py
.\dist\env\Scripts\python.exe .\dist\env\Scripts\voila.exe .\src\app.ipynb
pause