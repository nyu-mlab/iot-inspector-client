# Function to check if Npcap is installed by looking for its uninstall entry in the registry
# Essentially, this checks the Control Panel under Program Files -> Uninstall a program
function Test-NpcapInstalled {
    $UninstallPaths = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        "HKLM:\SOFTWARE\WOW6432NODE\Microsoft\Windows\CurrentVersion\Uninstall"
    )
    foreach ($path in $UninstallPaths) {
        if (Test-Path $path) {
            $InstalledApps = Get-ChildItem $path -ErrorAction SilentlyContinue | Get-ItemProperty -ErrorAction SilentlyContinue
            if ($InstalledApps | Where-Object { $_.DisplayName -like "*Npcap*" }) {
                return $True
            }
        }
    }
    return $False
}

# Set error preference
$ErrorActionPreference = "Stop"

# Set the working directory to the script's location
Set-Location -Path $PSScriptRoot

# Save current directory before elevation
if (-not $env:ORIGINAL_CWD) {
    $env:ORIGINAL_CWD = (Get-Location).Path
}

# --- 1. Admin Rights Check and Relaunch ---
# This block handles the elevation of the script to Administrator.
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires administrative privileges for dependency installation (if needed). Relaunching as administrator..."
    $script = $MyInvocation.MyCommand.Definition
    # Relaunching itself with elevated privileges
    Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -NoExit -ExecutionPolicy Bypass -Command `"Set-Location '$env:ORIGINAL_CWD'; & '$script'`""
    exit
}

# --- 2. Dependency Check and Installation (Only runs in the elevated Admin shell) ---
$DependencyScript = "install.ps1"
$CurrentDir = $PSScriptRoot

# Check if uv is available. If it's not, we assume the initial setup needs to run.
$NpcapFound = Test-NpcapInstalled
if (-not (Get-Command uv -ErrorAction SilentlyContinue) -or -not $NpcapFound) {
    Write-Warning "Launching initial setup script: $DependencyScript"

    # Execute install.ps1 directly (since we are already running as Admin)
    # The dependency script handles uv installation and Npcap checks.
    & "$CurrentDir\$DependencyScript"

    # Crucial: After UV is installed, we must start a new shell session
    # for the PATH variable (where uv is located) to be properly updated.
    Write-Host "Setup finished!!"
    Read-Host "Please close this window by clicking the X and click IoT Inspector again."
    exit
}

# --- 3. Virtual Environment Setup (Non-Admin system tasks) ---
# Runs uv venv and uv sync in the elevated shell.
if (-not (Test-Path "$PSScriptRoot\.venv")) {
    Write-Host "Creating virtual environment and installing packages..."
    try {
        uv venv
        uv sync --locked
        Write-Host "Virtual environment ready."
    } catch {
        Write-Error "Failed to set up virtual environment. $($_.Exception.Message)"
        exit 1
    }
}

# --- 4. Find and Launch Application ---
# Find the Python executable in the virtual environment using uv
Write-Host "Starting IoT Inspector..."

# Use the dedicated Streamlit executable installed by uv.
# This is to avoid 'C:\Program Files\' being seen as two arguments because of the space!
$streamlitAppPath = "$PSScriptRoot\src\libinspector\dashboard.py"

# FIX: Use uv run directly with correct quoting for the path, which handles spaces.
# The entire argument list is passed to uv.
$StreamlitArgs = @("run", "streamlit", "run", "`"$streamlitAppPath`"")

$streamlitProcess = Start-Process -FilePath "uv" `
    -ArgumentList $StreamlitArgs `
    -PassThru `
    -NoNewWindow


$isReady = $false
$pollingDelaySeconds = 3
$appUrl = "http://localhost:33721/"
# Loop indefinitely until $isReady becomes $true
while (-not $isReady) {
    try {
        # Use Invoke-WebRequest to check for a successful connection (Status Code 200).
        # We set a short TimeoutSec on the request itself to prevent hanging.
        $request = Invoke-WebRequest -Uri $appUrl -TimeoutSec 5 -ErrorAction Stop
        if ($request.StatusCode -eq 200) {
            $isReady = $true
            Write-Host "✅ Server is ready. Launching browser."
        }
    } catch {
        # Server is not ready yet, or connection failed. Ignore the error.
        Write-Host "Still waiting for Streamlit server..."
    }

    if (-not $isReady) {
        Start-Sleep -Seconds $pollingDelaySeconds
    }
}
# Open the browser to the application URL
Start-Process -FilePath $appUrl

# Wait for the Streamlit process to finish or for the user to close this window
Write-Host "IoT Inspector is running. Close this window to stop the application."
if ($streamlitProcess) {
    $streamlitProcess.WaitForExit()
}
Write-Host "IoT Inspector has been closed. Exiting setup script."