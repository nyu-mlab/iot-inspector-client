@ECHO OFF
for /f "skip=1delims=" %%a in (
 'wmic cpu get AddressWidth'
) do set "ostype=%%a"&goto setaddwidth

:setaddwidth
for /f "skip=1delims=" %%a in (
 'wmic cpu get AddressWidth'
) do set "arch=%%a"&goto checkarch

:checkarch
if %arch%!=64 || %ostype%!='ARM 64-bit Processor' (
    echo "Cannot run installation on this OS architecture"
    exit
)

python --version 3>NUL
if errorlevel 1 goto errorNoPython

:errorNoPython
echo Error^: Python not installed, installing python
bitsadmin.exe /transfer "downloadpython" https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe C:\Users\Public\Downloads\python.exe
START /WAIT C:\Users\Public\Downloads\python.exe
echo "Verifying installation"
goto checkpythonintallation

:checkpythonintallation
 timeout /t 10
 python --version 3>NUL
 if errorlevel 1 goto checkpythonintallation

echo "Python installed"


set NODE_VER=null
set NODE_EXEC=node-v0.8.11-x86.msi
set SETUP_DIR=%CD%
node -v >tmp.txt
set /p NODE_VER=<tmp.txt
del tmp.txt
IF %NODE_VER%==null (
	echo INSTALLING node ...
	mkdir tmp
	IF NOT EXIST tmp/%NODE_EXEC% (
		echo Node setup file does not exist. Downloading ...
		cd ../bin
        bitsadmin.exe /transfer "downloadnodejs" http://nodejs.org/dist/v0.8.11/%NODE_EXEC%
		move %NODE_EXEC% %SETUP_DIR%/tmp
	)
	cd %SETUP_DIR%/tmp
	START /WAIT %NODE_EXEC%
	cd %SETUP_DIR%
) ELSE (
	echo Node is already installed. Proceeding ...
)

cd ../..
echo INSTALLING yarn ...
call npm install -g yarn


git --version 3>NUL
if errorlevel 1 goto errorNoGit

:errorNoGit
bitsadmin.exe /transfer "downloadgit" https://github.com/git-for-windows/git/releases/download/v2.38.1.windows.1/Git-2.38.1-32-bit.exe C:\Users\Public\Downloads\git.exe
START /WAIT C:\Users\Public\Downloads\git.exe
echo "Verifying installation"
goto checkGitIntallation

:checkGitIntallation
 timeout /t 10
 git --version 3>NUL
 if errorlevel 1 goto checkGitIntallation

echo "Git installed"

set iotdir=C:\Program Files\iot_inspector
set branch=cr-dev
if not exist iotdir(
    git clone https://github.com/nyu-mlab/iot-inspector-client.git %iotdir%
    cd $iotdir
    git checkout $branch
    python -m venv C:\iot_inspector_env
    source C:\iot_inspector_env\bin\activate

    cd %iotdir%\inspector
     pip3 install -r requirements.txt

    cd %iotdir%/ui/default
    yarn install:all
    yarn clean:db
    yarn prisma:generate
)

source C:\iot_inspector_env\bin\activate
cd %iotdir%\ui\default && yarn dev &
timeout /t 5

echo "app running on http://localhost:4000"
START http://localhost:4000

timeout /t 2
cls;
cd %iotdir%\inspector && python start.py
