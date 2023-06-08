:: Environment setup and configuration script to accompany Ford+ Wind Tunnel Plotter Tool
:: Available Arguments:
::      -y  Automatically confirms Y/N prompts, where applicable
::      -d  Specify alternative installation directory. Default is C:/Users/<username>
::      -b  Specify alternative branch to install from project GitHub


@echo off
::set "source_directory=%~dp0"
set "install_directory=%userprofile%\FordWindTunnelPlotter"
set "branch=main"
set auto_yes=

echo Welcome to the installation script for the Ford+ WT plotting application!
echo This script will automatically initialize the Python environment and download the latest version of the project from GitHub.
echo :
echo This may take several minutes. CTRL-C can be used to cancel the installation at any point
echo :
echo :

GOTO parse

:parse
    IF "%~1"=="" GOTO check_permissions
    IF "%~1"=="-y" (
        set auto_yes= -y
        echo auto_yes active
    )

    IF "%~1"=="-d" (
        REM install directory specified by -d
        IF NOT "%~2"=="" (
            set "install_directory=%~2"
            echo Install Directory Set
            SHIFT
        )
    )

    IF "%~1"=="-b" (
        REM setting branch specified by -b
        IF NOT "%~2"=="" (
            set "branch=%2"
            echo Alternate Branch Set
            SHIFT
        )
    )

    SHIFT
    GOTO parse

:check_permissions
    :: echo Detecting permissions...
    net session >nul 2>&1
    if %errorLevel% == 0 (
        echo Success: Administrative permissions confirmed.
        GOTO init
    ) else (
        echo Current permissions inadequate. Use CTRL-C to cancel installation and restart with "Run as administrator"
        echo Continue at your own risk!
        pause
        GOTO init
    )

:init
    IF "%install_directory%"=="" GOTO:EOF

    :: Configuring Virtual Environment. **Seems redundant, but it is NOT! Voila breaks w/out this
    echo :
    echo (step 1/4) Configuring Environment...
    "%install_directory%\dist\bin\python.exe" -m pip install -q virtualenv  --no-warn-script-location
    "%install_directory%\dist\bin\python.exe" -m virtualenv -q "%install_directory%\dist\env"
    "%install_directory%\dist\env\Scripts\python.exe" -m pip install -q pygit2

    :: Getting latest available version of project source from GitHub
    cd %install_directory%
    echo :
    echo (step 2/4) Downloading Source...
    "%install_directory%\dist\env\Scripts\python.exe" "%install_directory%\git_tools.py" %auto_yes% clone -d "%install_directory%\src" -b "%branch%" "https://<key>@github.com/SHR-nbartlett/WT_Plotter"

    echo :
    echo (step 3/4) Downloading and Installing Environment Packages (this may take a while)...
    "%install_directory%\dist\env\Scripts\python.exe" -m pip install -qr "%install_directory%\src\requirements.txt" --no-compile --no-warn-script-location

    :: Checking the installation
    echo :
    echo (step 4/4) Verifying Installation...
    "%install_directory%\dist\env\Scripts\python.exe" "%install_directory%\install_check.py"

    echo :
    echo Installation Complete!
    echo Install Location: %install_directory%
