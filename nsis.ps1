# nsis.ps1 - PowerShell script to build the IoT Inspector installer using NSIS

$ErrorActionPreference = "Stop"

$NSIS_SCRIPT = "iot-inspector.nsi"
$NSIS_COMPILER = "makensis.exe"

# Run NSIS to create the installer
Write-Host "Compiling NSIS script..."
& $NSIS_COMPILER $NSIS_SCRIPT

if (Test-Path "IoT_Inspector_Installer.exe") {
    Write-Host "Build complete! The installer is located at: .\IoT_Inspector_Installer.exe"
} else {
    Write-Host "NSIS compilation failed. Please ensure NSIS is installed and 'makensis.exe' is in your PATH."
    exit 1
}
