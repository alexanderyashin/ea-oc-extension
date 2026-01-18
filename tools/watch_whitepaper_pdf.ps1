<#
Watches /paper for changes and rebuilds paper/whitepaper.pdf using tools/build_whitepaper_pdf.ps1
- Debounced to avoid rebuild storms
- Ignores changes to the output PDF itself to prevent loops

Works on:
- Windows PowerShell 5.1 (no pwsh required)
- PowerShell 7+ (pwsh)

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File tools\watch_whitepaper_pdf.ps1
  pwsh      -NoProfile -ExecutionPolicy Bypass -File tools/watch_whitepaper_pdf.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message, [int]$Code = 1) {
  Write-Host ""
  Write-Host "ERROR: $Message" -ForegroundColor Red
  exit $Code
}

function Info([string]$Message) {
  Write-Host $Message -ForegroundColor Cyan
}

function Warn([string]$Message) {
  Write-Host "WARN: $Message" -ForegroundColor Yellow
}

function Get-ScriptPath {
  if ($PSCommandPath) { return $PSCommandPath }

  try {
    if ($MyInvocation -and $MyInvocation.MyCommand -and $MyInvocation.MyCommand.Definition) {
      $def = $MyInvocation.MyCommand.Definition
      if ($def -and (Test-Path -LiteralPath $def)) { return $def }
    }
  } catch { }

  $cwd = (Get-Location).Path
  $maybe = Join-Path $cwd "tools\watch_whitepaper_pdf.ps1"
  if (Test-Path -LiteralPath $maybe) { return $maybe }

  Fail "Cannot resolve script path. Run from repo root or execute with: powershell -File tools\watch_whitepaper_pdf.ps1"
}

function Get-RepoRoot {
  $thisScript = Get-ScriptPath
  $toolsDir = Split-Path -Parent $thisScript
  $root = Split-Path -Parent $toolsDir
  if (-not (Test-Path -LiteralPath $root)) { Fail "Repo root not found from script location: $root" }
  return (Resolve-Path -LiteralPath $root).Path
}

function Get-PowerShellExe {
  $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
  if ($pwsh) { return $pwsh.Source }

  $ps = Get-Command powershell -ErrorAction SilentlyContinue
  if ($ps) { return $ps.Source }

  Fail "Neither 'pwsh' nor 'powershell' found in PATH. Cannot run build script."
}

$repoRoot = Get-RepoRoot
$paperDir = Join-Path $repoRoot "paper"
$buildScript = Join-Path $repoRoot "tools/build_whitepaper_pdf.ps1"
$outPdf = Join-Path $paperDir "whitepaper.pdf"
$psExe = Get-PowerShellExe

if (-not (Test-Path -LiteralPath $paperDir)) { Fail "Directory not found: $paperDir" }
if (-not (Test-Path -LiteralPath $buildScript)) { Fail "Build script not found: $buildScript" }

$debounceMs = 600
$timer = New-Object System.Timers.Timer
$timer.Interval = $debounceMs
$timer.AutoReset = $false

$pendingReason = $null
$lockObj = New-Object object

$action = {
  try {
    Info ""
    Info "Rebuilding (reason: $pendingReason)..."
    & $psExe -NoProfile -ExecutionPolicy Bypass -File $buildScript
    if ($LASTEXITCODE -ne 0) { Warn "Build returned exit code $LASTEXITCODE" }
    else { Info "Rebuild OK." }
  } catch {
    Warn ("Rebuild failed: " + $_.Exception.Message)
  }
}

Register-ObjectEvent -InputObject $timer -EventName Elapsed -Action $action | Out-Null

$fsw = New-Object System.IO.FileSystemWatcher
$fsw.Path = $paperDir
$fsw.IncludeSubdirectories = $true
$fsw.EnableRaisingEvents = $true

$fsw.Filter = "*.*"
$notify = [System.IO.NotifyFilters]'FileName, LastWrite, Size, DirectoryName'
$fsw.NotifyFilter = $notify

function Should-Ignore([string]$fullPath) {
  if (-not $fullPath) { return $true }
  $p = $fullPath.ToLowerInvariant()

  if ($p -eq $outPdf.ToLowerInvariant()) { return $true }
  if ($p.Contains("\.tmp_")) { return $true }
  if ($p.Contains("\_build\")) { return $true }

  $ext = [System.IO.Path]::GetExtension($p)
  $allowed = @(".md", ".mdx", ".png", ".jpg", ".jpeg", ".svg", ".pdf")
  return -not ($allowed -contains $ext)
}

function Trigger-Rebuild([string]$reason) {
  [System.Threading.Monitor]::Enter($lockObj)
  try {
    $script:pendingReason = $reason
    $timer.Stop()
    $timer.Start()
  } finally {
    [System.Threading.Monitor]::Exit($lockObj)
  }
}

$onChange = {
  $path = $Event.SourceEventArgs.FullPath
  $chg  = $Event.SourceEventArgs.ChangeType.ToString()

  if (Should-Ignore $path) { return }

  $rel = $path.Replace($repoRoot, "").TrimStart('\')
  Info ("{0} {1}" -f $chg.PadRight(8), $rel)
  Trigger-Rebuild ("$chg $rel")
}

Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Created -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Deleted -Action $onChange | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action $onChange | Out-Null

Info "Watching: $paperDir"
Info "Build via : $buildScript"
Info "Runner   : $psExe"
Info "Output   : $outPdf"
Info "Debounce : ${debounceMs}ms"
Info ""
Info "Press Ctrl+C to stop."

Trigger-Rebuild "initial"

while ($true) { Start-Sleep -Seconds 1 }
