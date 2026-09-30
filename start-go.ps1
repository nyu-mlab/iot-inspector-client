# start-go.ps1 - download the prebuilt Go IoT Inspector and run it (Windows).
# No Go, Python, or uv needed. Run it through start-go.bat.
#
# Optional env overrides:
#   INSPECTOR_VERSION  release tag to use (e.g. go-v1.0.0); default = newest go-v* release
#   INSPECTOR_PORT     dashboard port (default 8080)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # Invoke-WebRequest is ~10x faster without the progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Repo     = if ($env:INSPECTOR_REPO) { $env:INSPECTOR_REPO } else { 'nyu-mlab/iot-inspector-client' }
$Version  = $env:INSPECTOR_VERSION
$Port     = if ($env:INSPECTOR_PORT) { [int]$env:INSPECTOR_PORT } else { 8080 }
$AppHome  = Join-Path $env:LOCALAPPDATA 'IoTInspectorGo'
$Asset    = 'inspector-windows-amd64.exe'
$NpcapUrl = 'https://npcap.com/dist/npcap-1.89.exe'
$Url      = "http://127.0.0.1:$Port"

function Test-Admin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  (New-Object Security.Principal.WindowsPrincipal $id).IsInRole(
    [Security.Principal.WindowsBuiltinRole]::Administrator)
}

function Test-PortInUse([int]$p) {
  $c = New-Object Net.Sockets.TcpClient
  try { $c.Connect('127.0.0.1', $p); return $true } catch { return $false } finally { $c.Close() }
}

# --- 1. Relaunch elevated (one UAC prompt); packet capture needs admin ---
if (-not (Test-Admin)) {
  Write-Host "Requesting administrator access (needed to capture network traffic)..." -ForegroundColor Yellow
  Start-Process powershell -Verb RunAs -ArgumentList `
    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`""
  exit
}

try {
  if (-not [Environment]::Is64BitOperatingSystem) { throw "IoT Inspector needs 64-bit Windows." }

  # --- 2. Npcap (packet capture driver) ---
  if (-not (Test-Path "$env:WINDIR\System32\Npcap\wpcap.dll")) {
    Write-Host "[1/3] Installing Npcap (packet capture driver)..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path $AppHome | Out-Null
    $ni = Join-Path $AppHome 'npcap-installer.exe'
    Invoke-WebRequest -Uri $NpcapUrl -OutFile $ni -UseBasicParsing
    $sig = Get-AuthenticodeSignature $ni
    if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'Nmap Software LLC') {
      Remove-Item $ni -Force
      throw "The Npcap installer failed its signature check; not running it."
    }
    # free Npcap has no silent install (OEM only), so the user clicks through it
    Write-Host ""
    Write-Host "  An Npcap installer window is opening now." -ForegroundColor Yellow
    Write-Host "  Click 'I Agree', then 'Install', then 'Next'/'Finish'." -ForegroundColor Yellow
    Write-Host "  Leave every option at its default, then come back to this window." -ForegroundColor Yellow
    Write-Host ""
    Start-Process $ni -Wait
    Remove-Item $ni -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path "$env:WINDIR\System32\Npcap\wpcap.dll")) {
      throw "Npcap did not finish installing. Run start-go.bat again and complete the Npcap window."
    }
    Write-Host "  Npcap installed." -ForegroundColor Green
  } else {
    Write-Host "[1/3] Npcap already installed." -ForegroundColor Green
  }

  # --- 3. Find the release: newest go-v* tag, else the newest one already downloaded ---
  if (-not $Version) {
    try {
      $rels = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases?per_page=50" -TimeoutSec 15
      $Version = ($rels | Where-Object { $_.tag_name -like 'go-v*' } | Select-Object -First 1).tag_name
    } catch { }  # offline: fall back to the cache below
    if (-not $Version) {
      $cached = Get-ChildItem (Join-Path $AppHome 'bin') -Directory -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
      if ($cached) {
        $Version = $cached.Name
        Write-Host "Could not reach GitHub; using cached $Version." -ForegroundColor Yellow
      }
    }
    if (-not $Version) { throw "Could not find a release (no internet?). Set INSPECTOR_VERSION to retry." }
  }

  $BinDir = Join-Path $AppHome "bin\$Version"
  $Exe = Join-Path $BinDir 'inspector.exe'

  # --- 4. Download + verify (skipped when already cached) ---
  if (-not (Test-Path $Exe)) {
    Write-Host "[2/3] Downloading IoT Inspector $Version..." -ForegroundColor Cyan
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName())
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
      $base = "https://github.com/$Repo/releases/download/$Version"
      Invoke-WebRequest -Uri "$base/$Asset" -OutFile "$tmp\$Asset" -UseBasicParsing
      Invoke-WebRequest -Uri "$base/SHA256SUMS" -OutFile "$tmp\SHA256SUMS" -UseBasicParsing
      $want = $null
      foreach ($line in Get-Content "$tmp\SHA256SUMS") {
        $parts = $line -split '\s+'
        if ($parts.Count -ge 2 -and $parts[1].TrimStart('*') -eq $Asset) { $want = $parts[0] }
      }
      $got = (Get-FileHash "$tmp\$Asset" -Algorithm SHA256).Hash
      if (-not $want -or $want -ne $got) { throw "Checksum mismatch for $Asset; not running it." }
      New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
      Move-Item "$tmp\$Asset" $Exe
      Unblock-File $Exe  # strip Mark-of-the-Web so SmartScreen doesn't block it
      Write-Host "  Verified and saved to $Exe" -ForegroundColor Green
    } finally {
      Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
  } else {
    Write-Host "[2/3] Using IoT Inspector $Version." -ForegroundColor Green
  }

  # --- 5. Run; Ctrl-C stops it and restores the network ---
  if (Test-PortInUse $Port) {
    throw "Something is already running at $Url. Close it, or set INSPECTOR_PORT to another port."
  }
  $db  = Join-Path $AppHome 'inspector.db'
  $rep = Join-Path $AppHome 'report.html'
  if (Test-Path $rep) { Remove-Item $rep -Force }
  Write-Host "[3/3] Starting IoT Inspector. Press Ctrl-C here to stop (don't just close the window)." -ForegroundColor Cyan
  $p = Start-Process $Exe -NoNewWindow -PassThru -WorkingDirectory $AppHome -ArgumentList `
    '-serve', "127.0.0.1:$Port", '-db', "`"$db`"", '-report', "`"$rep`"", '-open=false'
  try {
    $opened = $false
    while (-not $p.HasExited) {
      if (-not $opened) {
        try {
          Invoke-WebRequest -Uri "$Url/api/state" -UseBasicParsing -TimeoutSec 2 | Out-Null
          Start-Process $Url
          Write-Host "Dashboard: $Url" -ForegroundColor Green
          $opened = $true
        } catch { }  # dashboard not up yet
      }
      Start-Sleep -Seconds 1
    }
  } finally {
    # Ctrl-C reaches inspector.exe too; give its clean shutdown time to finish
    if (-not $p.HasExited) { $p.WaitForExit(30000) | Out-Null }
    if (Test-Path $rep) {
      Write-Host "Report: $rep" -ForegroundColor Green
      Start-Process $rep
    }
  }
} catch {
  Write-Host ""
  Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Read-Host "Press Enter to close this window"
