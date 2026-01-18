<#
Watches /paper for changes and rebuilds paper/whitepaper.pdf using tools/build_whitepaper_pdf.ps1

This watcher is intentionally polling-based.
Reason: Windows PowerShell 5.1 can silently drop Register-ObjectEvent actions
in long-running sessions on some systems (no logs, no build), even though
Start-Process works fine.

Behavior:
- Poll paper/** every 500ms for latest LastWriteTime (excluding whitepaper.pdf and paper/_build/**)
- Debounce rebuilds (default 600ms) to avoid rebuild storms
- Writes logs into paper/_build:
    watch_build_YYYYMMDD_HHMMSS.out.log
    watch_build_YYYYMMDD_HHMMSS.err.log

Works on:
- Windows PowerShell 5.1
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

function Ensure-Dir([string]$path) {
  if (-not (Test-Path -LiteralPath $path)) {
    New-Item -ItemType Directory -Path $path | Out-Null
  }
}

function Norm([string]$p) {
  # Robust path normalization for comparisons:
  # - absolute full path
  # - lowercased (Windows case-insensitive)
  try {
    return ([System.IO.Path]::GetFullPath($p)).ToLowerInvariant()
  } catch {
    return $p.ToLowerInvariant()
  }
}

$repoRoot    = Get-RepoRoot
$paperDir    = Join-Path $repoRoot "paper"
$buildScript = Join-Path $repoRoot "tools/build_whitepaper_pdf.ps1"
$outPdf      = Join-Path $paperDir "whitepaper.pdf"
$psExe       = Get-PowerShellExe

if (-not (Test-Path -LiteralPath $paperDir))    { Fail "Directory not found: $paperDir" }
if (-not (Test-Path -LiteralPath $buildScript)) { Fail "Build script not found: $buildScript" }

$debounceMs = 600
$pollMs     = 500

# Normalized paths for reliable exclusion (prevents false rebuilds on output/log writes)
$outPdfN   = Norm $outPdf
$buildDirN = Norm (Join-Path $paperDir "_build")

function Invoke-Build([string]$reason) {
  Info ""
  Info "Rebuilding (reason: $reason)..."

  $logDir = Join-Path $paperDir "_build"
  Ensure-Dir $logDir

  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $logPathOut = Join-Path $logDir ("watch_build_{0}.out.log" -f $ts)
  $logPathErr = Join-Path $logDir ("watch_build_{0}.err.log" -f $ts)

  $args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $buildScript
  )

  $p = Start-Process -FilePath $psExe -ArgumentList $args `
    -WorkingDirectory $repoRoot `
    -RedirectStandardOutput $logPathOut `
    -RedirectStandardError  $logPathErr `
    -NoNewWindow -PassThru -Wait

  if ($p.ExitCode -ne 0) {
    Warn "Rebuild FAILED (exit code $($p.ExitCode)). Logs: $logPathOut ; $logPathErr"
    return
  }

  if (-not (Test-Path -LiteralPath $outPdf)) {
    Warn "Rebuild finished with exit code 0 but output is missing: $outPdf. Logs: $logPathOut ; $logPathErr"
    return
  }

  Info "Rebuild OK. Logs: $logPathOut ; $logPathErr"
}

function Get-InputFilesMaxWriteTime {
  # Track only source-ish files under paper/**, excluding:
  # - the output PDF itself (robust normalized compare)
  # - paper/_build/**      (robust normalized prefix exclude)
  # Also ignore temporary files.
  $max = [datetime]::MinValue

  $items = Get-ChildItem -LiteralPath $paperDir -Recurse -File -ErrorAction SilentlyContinue
  foreach ($it in $items) {
    $fullN = Norm $it.FullName

    # exclude output PDF
    if ($fullN -eq $outPdfN) { continue }

    # exclude build dir
    if ($fullN.StartsWith($buildDirN)) { continue }

    $name = $it.Name.ToLowerInvariant()
    if ($name.StartsWith(".tmp_")) { continue }

    $ext = $it.Extension.ToLowerInvariant()
    $allowed = @(".md",".mdx",".tex",".bib",".png",".jpg",".jpeg",".svg",".pdf",".yml",".yaml")
    if (-not ($allowed -contains $ext)) { continue }

    if ($it.LastWriteTime -gt $max) { $max = $it.LastWriteTime }
  }

  return $max
}

Info "Watching: $paperDir"
Info "Build via : $buildScript"
Info "Runner   : $psExe"
Info "Output   : $outPdf"
Info "Debounce : ${debounceMs}ms"
Info "Poll     : ${pollMs}ms"
Info ""
Info "Press Ctrl+C to stop."

# initial state
$lastSeen = Get-InputFilesMaxWriteTime
$pendingAt = Get-Date
$pendingReason = "initial"

# Initial build should happen exactly once; clear pending afterwards.
Invoke-Build $pendingReason

# IMPORTANT: reset baseline AFTER initial build.
# Some toolchains touch files under paper/** during the build (aux files, caches, etc.).
# We treat those as part of initial build, not as a user change trigger.
$lastSeen = Get-InputFilesMaxWriteTime

$pendingAt = $null
$pendingReason = $null

while ($true) {
  Start-Sleep -Milliseconds $pollMs

  $nowMax = Get-InputFilesMaxWriteTime
  if ($nowMax -gt $lastSeen) {
    $lastSeen = $nowMax
    $pendingAt = Get-Date
    $pendingReason = "file change (max LastWriteTime: $($nowMax.ToString('s')))"
  }

  if ($pendingAt -ne $null) {
    $ageMs = (New-TimeSpan -Start $pendingAt -End (Get-Date)).TotalMilliseconds
    if ($ageMs -ge $debounceMs) {
      Invoke-Build $pendingReason
      $pendingAt = $null
      $pendingReason = $null
    }
  }
}
