@echo off
set "install_directory=%userprofile%\FordWindTunnelPlotter"
set "branch=next"

echo Welcome to the installation script for the Ford+ WT plotting application!
echo This script will automatically download and install the latest version. It may take several minutes.
echo :
echo CTRL-C can be used to cancel the installation at any point
echo :
echo :
pause

GOTO check_permissions

:check_permissions
    echo (1/9) Detecting permissions...
    net session >nul 2>&1
    if %errorLevel% == 0 (
        :: echo Success: Administrative permissions confirmed.
        GOTO parse
    ) else (
        echo Current permissions inadequate. Use CTRL-C to cancel installation and restart with "Run as administrator"
        pause
        GOTO parse
    )

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
        IF NOT "%~2"=="" (
            set "branch=%2"
            echo Branch Set -- User-Defined
            SHIFT
        )
    )

    SHIFT
    GOTO parse
:endparse

IF "%install_directory%"=="" GOTO:EOF
GOTO install

:install
    :: Moving extracted files from .exe package (extracts to temp folder)
    echo :
    echo (2/9) Creating Install Folder...
    IF NOT EXIST "%install_directory%" md "%install_directory%"
    echo :
    echo (3/9) Moving Files to Install Folder...
    ROBOCOPY /MOV /NP /NFL /NDL /NJH /NJS "%cd%" "%install_directory%" /XF "install.bat"

    :: Extracting Embedded Python Distribution
    IF NOT EXIST "%install_directory%\dist" md "%install_directory%\dist"
    echo (4/9) Extracting Python 3.10 Embedded...
    TAR -xf "%install_directory%\dist310.zip" -C "%install_directory%\dist"

    :: Configuring Virtual Environment. **Seems redundant, but it is NOT! Voila breaks w/out this
    echo :
    echo (5/9) Configuring Environment...
    "%install_directory%\dist\bin\python.exe" -m pip install -q virtualenv  --no-warn-script-location
    "%install_directory%\dist\bin\python.exe" -m virtualenv -q "%install_directory%\dist\env"
    "%install_directory%\dist\env\Scripts\python.exe" -m pip install -q pygit2

    :: Getting latest available version of project source from GitHub
    cd %install_directory%
    echo :
    echo (6/9) Downloading Source...
    "%install_directory%\dist\env\Scripts\python.exe" "%install_directory%\git_tools.py" "https://<key>@github.com/SHR-nbartlett/WT_Plotter" -b "%branch%" -c "%install_directory%/src"

    echo :
    echo (7/9) Downloading and Installing Environment Packages (this may take a while)...
    "%install_directory%\dist\env\Scripts\python.exe" -m pip install -qr "%install_directory%\src\requirements.txt" --no-compile --no-warn-script-location

    :: Checking the installation
    echo :
    echo (8/9) Verifying Installation...
    %install_directory%\dist\env\Scripts\python.exe %install_directory%\install_check.py

    :: Creating Desktop Shortcut
    cd "%userprofile%\Desktop"
    echo :
    echo (9/9) Creating Desktop Shortcut...
    mklink "Ford+ Tunnel Plotter" "%install_directory%\run.bat"

    echo :
    echo Installation Complete!
    echo Install Location: %install_directory%
    pause
