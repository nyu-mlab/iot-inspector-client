# uninstall-deps.ps1 - PowerShell script for a complete uninstallation

# Exit on any errors
$ErrorActionPreference = "Stop"

# Get the installation directory
$INSTDIR = $PSScriptRoot

Write-Host "Starting uninstallation cleanup..."

# --- Delete all .json and .log files in the installation directory ---
Write-Host "Removing log, json, bat and db files..."
Remove-Item -Path (Join-Path -Path $INSTDIR -ChildPath "*.json") -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path -Path $INSTDIR -ChildPath "*.log") -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path -Path $INSTDIR -ChildPath "*.db") -ErrorAction SilentlyContinue
Remove-Item -Path (Join-Path -Path $INSTDIR -ChildPath "*.bat") -ErrorAction SilentlyContinue

# --- Clean up the uv virtual environment ---
Write-Host "Removing virtual environment..."
$venvPath = Join-Path -Path $INSTDIR -ChildPath ".venv"
if (Test-Path $venvPath) {
    # It's best practice to use uv to remove the venv, but if it fails, we fall back to a direct delete
    try {
        uv venv remove $venvPath
    } catch {
        Write-Warning "Failed to remove virtual environment with uv. Attempting direct deletion."
        Remove-Item -Path $venvPath -Recurse -Force
    }
}

# --- Delete specific files ---
Write-Host "Removing installation files..."
$filesToDelete = @(
    "start.ps1",
    "install.ps1",
    "pyproject.toml",
    "setup.py",
    "uv.lock",
    "README.md",
    "LICENSE"
)

foreach ($file in $filesToDelete) {
    $filePath = Join-Path -Path $INSTDIR -ChildPath $file
    if (Test-Path $filePath) {
        Remove-Item -Path $filePath -Force
    }
}

# --- Recursively delete directories ---
Write-Host "Removing installation directories..."
$dirsToDelete = @(
    "src",
    ".streamlit"
)

foreach ($dir in $dirsToDelete) {
    $dirPath = Join-Path -Path $INSTDIR -ChildPath $dir
    if (Test-Path $dirPath) {
        Remove-Item -Path $dirPath -Recurse -Force
    }
}

Write-Host "Uninstallation cleanup complete."