@echo off
set "pythonVersion=3.11.9"
set "installerName=python-%pythonVersion%-amd64.exe"
set "downloadUrl=https://python.org%"

echo |=============|
echo |NOVA-AI Setup|
echo |=============|

echo Downloading Python %pythonVersion%...
bitsadmin.exe /transfer "PythonDownload" "%downloadUrl%" "%TEMP%\%installerName%"

echo Installing Python...
:: /quiet: Silent install
:: InstallAllUsers=1: Installs for all users (requires Admin)
:: PrependPath=1: Automatically adds Python to the Windows PATH
start /wait "" "%TEMP%\%installerName%" /quiet InstallAllUsers=1 PrependPath=1

echo Cleaning up...
del "%TEMP%\%installerName%"
echo Python installation complete.
:: 1. Create the virtual environment folder named "venv"
python -m venv venv

:: 2. Activate the environment
call .\venv\Scripts\activate.bat

:: 3. Install dependencies
pip install -r requirements.txt

echo Virtual environment created and activated.
pause

