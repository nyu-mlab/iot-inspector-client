# install-deps.ps1 - Handles installation of UV, Npcap, and virtual environment setup.
# This script is ONLY called when uv is missing and is expected to run as Administrator.

$ErrorActionPreference = "Stop"

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

# Use this function to get the latest Npcap version and download URL
function Get-LatestNpcapInfo {
    param (
        [string]$DistUrl = "https://npcap.com/dist/",
        [string]$ScriptRoot = $PSScriptRoot
    )
    $html = Invoke-WebRequest -Uri $DistUrl -UseBasicParsing
    $npcapMatches = [regex]::Matches($html.Content, "npcap-(\d+\.\d+)\.exe")
    if ($npcapMatches.Count -gt 0) {
        $latest = $npcapMatches | Sort-Object { [version]$_.Groups[1].Value } -Descending | Select-Object -First 1
        $NpcapFileName = $latest.Value
        $NpcapDownloadUrl = "$DistUrl$NpcapFileName"
        $NpcapExePath = Join-Path -Path $ScriptRoot -ChildPath $NpcapFileName
        return @{
            FileName = $NpcapFileName
            DownloadUrl = $NpcapDownloadUrl
            ExePath = $NpcapExePath
        }
    } else {
        throw "Could not find Npcap installer on $DistUrl"
    }
}

# Define the Npcap details
$NpcapInfo = Get-LatestNpcapInfo
$NpcapFileName = $NpcapInfo.FileName
$NpcapDownloadUrl = $NpcapInfo.DownloadUrl
$NpcapExePath = $NpcapInfo.ExePath

# --- 1. Npcap Check and Installation ---
Write-Host "Checking for Npcap..."
$NpcapFound = $False
$UninstallPaths = @("HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", "HKLM:\SOFTWARE\WOW6432NODE\Microsoft\Windows\CurrentVersion\Uninstall")

$NpcapFound = Test-NpcapInstalled
if (-not $NpcapFound) {
    Write-Host "Npcap not found. Starting installation process."

    # Download Npcap if the file is not present locally
    if (-not (Test-Path $NpcapExePath)) {
        Write-Host "Downloading $NpcapFileName from the official source..."
        try {
            Invoke-WebRequest -Uri $NpcapDownloadUrl -OutFile $NpcapExePath -UseBasicParsing
            Write-Host "Download complete."
        } catch {
            Write-Error "Failed to download Npcap. Check your internet connection. $($_.Exception.Message)"
            # Continue to UV installation, but skip Npcap installation
        }
    }

    # Execute Npcap installer if the file exists (either downloaded or from previous failed attempt)
    if (Test-Path $NpcapExePath) {
        Write-Host "Starting Npcap installer (requires user interaction). Please follow the prompts in the new window."

        # *** INTERACTIVE INSTALLATION ***
        # Start the process and wait for the user to complete the installation steps.
        # We run it without arguments for an interactive GUI install.
        Start-Process -FilePath $NpcapExePath -Wait

        Write-Host "Npcap installation finished. Cleaning up installer file."
        Remove-Item -Path $NpcapExePath -Force
    } else {
        Write-Warning "Npcap installer file ($NpcapFileName) not found. Skipping Npcap installation."
    }
}

# --- 2. UV Installation ---
Write-Host "Checking for 'uv' and installing if necessary..."
try {
    # Check if uv command is available
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Host "'uv' not found. Installing now (this may take a moment)..."
        # Download and execute the uv install script
        Invoke-Expression (Invoke-RestMethod https://astral.sh/uv/install.ps1)
        Write-Host "UV installation complete."
    } else {
        Write-Host "'uv' found. Skipping UV installation."
    }
} catch {
    Write-Error "Failed to install UV. $($_.Exception.Message)"
    exit 1
}

Write-Host "=========================================================="
Write-Host "Setup is complete. Returning control to the launch script."
Write-Host "=========================================================="
