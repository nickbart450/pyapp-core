:: @echo off
set "run_directory=%userprofile%\FordWindTunnelPlotter"
cd /d %run_directory%

%run_directory%\dist\env\Scripts\python.exe %run_directory%\install_check.py
%run_directory%\dist\env\Scripts\python.exe %run_directory%\dist\env\Scripts\voila.exe %run_directory%\src\app.ipynb
pause