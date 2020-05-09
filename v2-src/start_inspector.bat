@echo off

rem Check if user has npcap installed. If not, prompt user.

if not exist %WINDIR%\System32\Npcap echo You need to install Npcap first. For more information, visit https://iotinspector.org/npcap-error/ & start https://iotinspector.org/npcap-error/ & goto press_key_to_exit

rem Downloads the latest IoT Inspector upon first launch. If not first launch, downloads the latest IoT Inspector in the background after user launches IoT Inspector.

set ExeURL=https://dashboard.iotinspector.org/redirect/windows-release
set InspectorHomeDir=%UserProfile%\princeton-iot-inspector
set InspectorExePath=%InspectorHomeDir%\start_inspector.exe

rem Initialize Inspector's home directory.

if not exist "%InspectorHomeDir%" mkdir "%InspectorHomeDir%"
cd "%InspectorHomeDir%"

rem Generate the update script inline so that we can call the external script later in the current script.

echo powershell -Command "Invoke-WebRequest %ExeURL% -OutFile start_inspector.exe.pending" >update_inspector.bat
echo copy /y start_inspector.exe.pending start_inspector.exe.latest >>update_inspector.bat

rem If Inspector was not previously downloaded, fetch the latest executable.

if not exist "%InspectorExePath%" echo Downloading the latest version of IoT Inspector... & cmd /c update_inspector.bat >nul

rem Make sure we have the latest executable

if not exist "start_inspector.exe.latest" echo Error downloading the latest IoT Inspector. & goto press_key_to_exit

rem Overwrite the current executable with the latest one.

copy /y start_inspector.exe.latest start_inspector.exe >nul || (echo Error updating to latest executable. & goto press_key_to_exit)

rem Start inspector in a different window.

echo Starting IoT Inspector in administrator mode...
powershell Start-Process "start_inspector.exe" -Verb RunAs

rem Update IoT Inspector in the background.

powershell Start-Process "update_inspector.bat" -WindowStyle Hidden

goto :eof

:press_key_to_exit
echo Press any key to exit.
pause>nul
