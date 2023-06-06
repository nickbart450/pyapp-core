@echo off
set "install_directory=%userprofile%\FordWindTunnelPlotter"
GOTO parse

:parse
IF "%~1"=="" GOTO endparse
IF "%~1"=="-d" (
    REM install directory specified by -d
    IF EXIST %~2 (
        set "install_directory=%~2"
        echo Install Directory Set
        SHIFT
    )
)

IF "%~1"=="-b" (
    REM setting branch specified by -b
    IF "%~2"=="" (
        set "branch=auto-update"
        echo Branch Set default
        SHIFT
    ) ELSE (
        set "branch=%2"
        echo Branch Set user
	SHIFT
    )
)

SHIFT
GOTO parse
:endparse

echo Install Directory: %install_directory%
IF "%install_directory%"=="" GOTO:EOF
GOTO install

:install
echo Welcome to the installation script for the Ford+ WT plotting application!
echo This script will automatically download and install the latest version. It may take several minutes.
echo :
echo CTRL-C can be used to cancel the installation at any point
echo :
echo :
pause

:: Move extracted files from .exe package (extracts to temp folder)
echo Creating Install Folder...
IF NOT EXIST "%install_directory%" md "%install_directory%"
echo Moving Files to Install Folder...
ROBOCOPY /MOV /NP "%cd%" "%install_directory%" /XF "install.bat"

:: Extract Embedded Python Distribution
IF NOT EXIST "%install_directory%\dist" md "%install_directory%\dist"
echo Extracting Python 3.10 Embedded...
TAR -xf "%install_directory%\dist310.zip" -C "%install_directory%\dist"

:: Configure Environment. **Seems redundant, but it is NOT! Voila breaks w/out this
echo Configuring Environment...
"%install_directory%\dist\bin\python.exe" -m pip install -q virtualenv  --no-warn-script-location
"%install_directory%\dist\bin\python.exe" -m virtualenv -q "%install_directory%\dist\env"
"%install_directory%\dist\env\Scripts\python.exe" -m pip install -q pygit2

:: Get latest available version of project source from GitHub
cd %install_directory%
echo :
echo Downloading Source...
"%install_directory%\dist\env\Scripts\python.exe" "%install_directory%\git_tools.py" "https://<key>@github.com/SHR-nbartlett/WT_Plotter" -b "%branch%" -c "%install_directory%/src"

echo :
echo Downloading and Installing Environment Packages (this may take a while)...
"%install_directory%\dist\env\Scripts\python.exe" -m pip install -qr "%install_directory%\src\requirements.txt" --no-compile --no-warn-script-location

:: Check the installation
echo :
echo Verifying Installation...
%install_directory%\dist\env\Scripts\python.exe %install_directory%\install_check.py

echo :
echo Installation Complete!
pause
