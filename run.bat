::@echo off
set "run_directory=%~dp0"
cd /d "%run_directory%"

echo Starting....
call "%run_directory:~0,-1%\src\run.bat"