:: @echo off
set branch="auto-update"

:: Extract Embedded Python Distribution
tar -xf dist.zip
md .\dist
move .\bin .\dist\bin

:: Configure Environment. **Seems redundant, but it is NOT! Voila breaks w/out this
.\dist\bin\python.exe -m pip install virtualenv
.\dist\bin\python.exe -m virtualenv .\dist\env
.\dist\env\Scripts\python.exe -m pip install pygit2

:: Get latest available version of project source from GitHub
.\dist\env\Scripts\python.exe git_tools.py "https://<key>@github.com/SHR-nbartlett/WT_Plotter" -b %branch% -c "./src"

.\dist\env\Scripts\python.exe -m pip install -r ".\src\requirements.txt" --no-compile --no-warn-script-location

:: Check the installation
.\dist\env\Scripts\python.exe .\install_check.py

@echo on
echo "Installation Complete!"
pause