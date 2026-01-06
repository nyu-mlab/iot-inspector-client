; Script for creating IoT Inspector Installer

!define APP_NAME "IoT Inspector"
!define APP_VERSION "3.0.0"

; Set the installer output file name
OutFile "IoT_Inspector_Installer.exe"

; Set the name of the installer and the application
Name "${APP_NAME}"

; Set the default installation directory
InstallDir "$PROGRAMFILES\${APP_NAME}"

; Request administrator privileges for the installer
RequestExecutionLevel admin

; UI Settings
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; --- Custom Finish Page for Instructions (Simplified & Cleaned) ---
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_FINISHPAGE_TEXT "Installation of core files is complete. The setup is now finalized. To complete the configuration (installing UV and the Npcap driver) and launch the application, please use the new desktop shortcut."

!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Section "Main" SEC_MAIN
    ; Copy src preserving its structure under $INSTDIR\src
    SetOutPath "$INSTDIR\src"
    File /r "src\*"

    ; Copy .streamlit preserving its structure under $INSTDIR\.streamlit
    SetOutPath "$INSTDIR\.streamlit"
    File /r ".streamlit\*"

    ; Copy everything else to $INSTDIR
    SetOutPath "$INSTDIR"
    File "pyproject.toml"
    File "setup.py"
    File "start.bat"
    File "start.ps1"
    File "uninstall.ps1"
    File "install.ps1"
    File "README.md"
    File "LICENSE"
    File "uv.lock"

    ; --- Correct Registry Code to Register for Uninstall ---
    !if ${RunningX64}
        SetRegView 64
        !define REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !else
        SetRegView 32
        !define REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !endif

    ; Write all the required registry values
    WriteRegStr HKLM "${REG_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${REG_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "${REG_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${REG_KEY}" "Publisher" "NYU mLab"
    WriteRegStr HKLM "${REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${REG_KEY}" "HelpLink" "https://github.com/nyu-mlab/iot-inspector-client/issues"
    WriteRegDword HKLM "${REG_KEY}" "EstimatedSize" 1500 ; Size about 1.5 MB
    WriteRegDword HKLM "${REG_KEY}" "NoModify" 1
    WriteRegDword HKLM "${REG_KEY}" "NoRepair" 1

    ; Add this line to write the uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Create Shortcuts"
    ; Create a shortcut that points to the new batch file
    CreateShortCut "$SMPROGRAMS\${APP_NAME}.lnk" "$INSTDIR\start.bat" "" "" 0
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\start.bat" "" "" 0
SectionEnd

; Uninstaller (ExecWait calls kept for necessary cleanup)
Section "Uninstall"
    ; Remove the registry keys for the application
    !if ${RunningX64}
        SetRegView 64
        DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !else
        SetRegView 32
        DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !endif

    ; Execute the dedicated uninstall script to handle all cleanup tasks
    ExecWait 'powershell.exe -ExecutionPolicy ByPass -File "$INSTDIR\uninstall.ps1"'

    ; Remove shortcuts created at install (if present)
    Delete "$SMPROGRAMS\${APP_NAME}.lnk"
    Delete "$DESKTOP\${APP_NAME}.lnk"

    ; Remove files
    RMDir /r "$INSTDIR"
SectionEnd
