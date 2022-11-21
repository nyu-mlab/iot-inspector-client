@echo off

for /f "skip=1delims=" %%a in (
 'wmic OS get OSArchitecture'
) do set "ostype=%%a"&goto setaddwidth

:setaddwidth
for /f "skip=1delims=" %%a in (
 'wmic cpu get AddressWidth'
) do set "arch=%%a"&goto checkarch

:checkarch
echo %arch%
echo %ostype%
if %arch% NEQ 64  (
    echo Cannot run installation on this OS architecture
    exit
)

python --version 3>NUL
if %errorlevel% EQU 1 goto errorNoPython
if %errorlevel% EQU 0 goto checkNode

:errorNoPython
echo Error^: Python not installed, installing python
bitsadmin.exe /transfer "downloadpython" https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe C:\Users\Public\Downloads\python.exe
echo Python installation in process
START /WAIT C:\Users\Public\Downloads\python.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
set PYTHONPATH=C:\Program Files\Python311;C:\Program Files\Python311\Scripts
set path=%PATH%;%PYTHONPATH%;
echo Verifying python installation
goto checkpythonintallation

:checkpythonintallation
 timeout /t 5
 python --version 3>NUL
 if %errorlevel% EQU 1 goto checkpythonintallation
 if %errorlevel% EQU 0 goto checkNode

:checkNode
node -v 3>NUL
if %errorlevel% EQU 1 goto errorNoNode
if %errorlevel% EQU 0 goto checkYarn 

:errorNoNode
set NODE_EXEC=node-v16.16.0-x64.msi
set SETUP_DIR=%CD%
echo INSTALLING node ...
echo Node setup file does not exist. Downloading ...
bitsadmin.exe /transfer "downloadnodejs" https://nodejs.org/dist/v16.16.0/node-v16.16.0-x64.msi C:\Users\Public\Downloads\node16.msi
MsiExec.exe /i C:\Users\Public\Downloads\node16.msi TARGETDIR="C:\Program Files\nodejs\" ADDLOCAL="NodePerfCtrSupport,NodeEtwSupport,DocumentationShortcuts,EnvironmentPathNode,EnvironmentPathNpmModules,npm,NodeRuntime,EnvironmentPath" /passive
set NODEPATH=C:\Program Files\nodejs\;
set path=%PATH%;%NODEPATH%
echo Verifying node installation
goto checkNodeInstallation

:checkNodeInstallation
timeout /t 3
node -v 3>NUL
if %errorlevel% EQU 1 goto checkNodeInstallation

:checkYarn
yarn -v 3>NUL
if %errorlevel% EQU 1 goto errorNoYarn
if %errorlevel% EQU 0 goto checkGit

:errorNoYarn
bitsadmin.exe /transfer "download yarn" https://classic.yarnpkg.com/latest.msi C:\Users\Public\Downloads\yarn.msi
MsiExec.exe /i C:\Users\Public\Downloads\yarn.msi TARGETDIR="C:\Program Files\yarn\" /passive
set YARNPATH=C:\Program Files\yarn\;
set path=%PATH%;%YARNPATH%
echo Verifying yarn installation
goto checkYarnInstallation

:checkYarnInstallation
timeout /t 3
yarn -v 3>NUL
if %errorlevel% EQU 1 goto checkYarnInstallation

:checkGit
git --version 3>NUL
if %errorlevel% EQU 1 goto errorNoGit
if %errorlevel% EQU 0 goto checkSrcInstallation

:errorNoGit
bitsadmin.exe /transfer "downloadgit" https://github.com/git-for-windows/git/releases/download/v2.38.1.windows.1/Git-2.38.1-64-bit.exe C:\Users\Public\Downloads\git.exe
START /WAIT C:\Users\Public\Downloads\git.exe /silent
set GITPATH=C:\Program Files\Git\bin;
set path=%PATH%;%GITPATH%
echo Verifying git installation
goto checkGitIntallation

:checkGitIntallation
 timeout /t 3
 git --version 3>NUL
 if %errorlevel% EQU 1 goto checkGitIntallation
 if %errorlevel% EQU 0 goto checkSrcInstallation

:checkSrcInstallation
echo Checking source insta bllation
echo Git installed
set iotdir=C:\iot-inspector-client
set branch=cr-dev
if not exist %iotdir% (
    cd C:\
    mkdir iot-inspector-client
    git clone https://github.com/nyu-mlab/iot-inspector-client.git
    cd %iotdir%
    git checkout %branch%
    python -m venv C:\iot-inspector-env
    C:\iot-inspector-env\Scripts\activate

    cd %iotdir%\
    pip3 install -r requirements.txt
    C:\iot-inspector-env\Scripts\deactivate
    
    cd %iotdir%\ui\default
    npm run install:all
    npm run clean:db
    npm run prisma:generate
)
cd %iotdir%\ui\default && yarn dev &
timeout /t 5
echo "app running on http://localhost:4000"
START http://localhost:4000
timeout /t 2
C:\iot-inspector-env\Scripts\activate
cd %iotdir%\inspector && python start.py
C:\iot-inspector-env\Scripts\deactivate
