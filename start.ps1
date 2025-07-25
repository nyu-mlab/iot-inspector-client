# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "'uv' is not installed. Installing it now..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
}

# Verify installation
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "'uv' installation failed. Please install it manually. If you installed it, recreate the PowerShell instance"
    exit 1
}

# Save current directory before elevation
if (-not $env:ORIGINAL_CWD) {
    $env:ORIGINAL_CWD = (Get-Location).Path
}

# Check for admin rights
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # Relaunch script as admin
    Write-Host "This script requires administrative privileges. Relaunching as administrator..."
    $script = $MyInvocation.MyCommand.Definition
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -NoExit -ExecutionPolicy Bypass -Command `"Set-Location '$env:ORIGINAL_CWD'; & '$script'`""
    exit
}

# Please make sure when you initialize this that you have no existing .venv or virtual environment
$pythonPath = uv run where python | Where-Object { $_ -like "*\iot-inspector-client\.venv\Scripts\python.exe" } | Select-Object -First 1
if (-not $pythonPath) {
    Write-Host "Could not find the Python executable in .venv\Scripts. Make sure you have initialized the virtual environment using uv"
    exit 1
}

uv run -- $pythonPath -m streamlit run dashboard.py

Read-Host "Press Enter to exit"