<#
Builds: paper/whitepaper.pdf
Source: paper/whitepaper.md (preferred), otherwise best-effort autodetect.

Requirements (Windows):
- pandoc in PATH
- a LaTeX engine in PATH (xelatex recommended; MiKTeX/TeX Live)
- (optional) git in PATH for deterministic SOURCE_DATE_EPOCH from HEAD

Determinism:
- Sets SOURCE_DATE_EPOCH based on git HEAD commit time (or source file mtime fallback)
- Avoids embedding "today" date in metadata (uses fixed/empty date)

Unicode robustness:
- Forces a Unicode-capable main font so symbols like ∂, τ, ≤, ⊆ render.
- Uses Windows-default fonts by default (Times New Roman / Consolas).
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail([string]$Message, [int]$Code = 1) {
  Write-Host ""
  Write-Host "ERROR: $Message" -ForegroundColor Red
  exit $Code
}

function Warn([string]$Message) {
  Write-Host "WARN: $Message" -ForegroundColor Yellow
}

function Info([string]$Message) {
  Write-Host $Message -ForegroundColor Cyan
}

function Require-Command([string]$Name, [string]$Hint) {
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if (-not $cmd) {
    Fail "Missing dependency: '$Name' not found in PATH.`nHint: $Hint"
  }
  return $cmd.Source
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
  $maybe = Join-Path $cwd "tools\build_whitepaper_pdf.ps1"
  if (Test-Path -LiteralPath $maybe) { return $maybe }

  Fail "Cannot resolve script path. Run from repo root or execute with: powershell -File tools\build_whitepaper_pdf.ps1"
}

function Get-RepoRoot {
  $thisScript = Get-ScriptPath
  $toolsDir = Split-Path -Parent $thisScript
  $root = Split-Path -Parent $toolsDir
  if (-not (Test-Path -LiteralPath $root)) { Fail "Repo root not found from script location: $root" }
  return (Resolve-Path -LiteralPath $root).Path
}

function Find-WhitepaperSource([string]$PaperDir) {
  $preferred = Join-Path $PaperDir "whitepaper.md"
  if (Test-Path -LiteralPath $preferred) { return $preferred }

  $candidates = @(
    Join-Path $PaperDir "WHITEPAPER.md"
    Join-Path $PaperDir "Whitepaper.md"
    Join-Path $PaperDir "whitepaper.mdx"
  ) | Where-Object { Test-Path -LiteralPath $_ }

  if ($candidates.Count -gt 0) { return $candidates[0] }

  $glob = Get-ChildItem -LiteralPath $PaperDir -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -ieq ".md" -and $_.Name.ToLower().Contains("white") } |
    Select-Object -First 1
  if ($glob) { return $glob.FullName }

  Fail "Whitepaper source not found. Expected: paper/whitepaper.md (preferred) or a fallback *white*.md in /paper."
}

function Get-SourceDateEpoch([string]$RepoRoot, [string]$SourceFile) {
  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git) {
    try {
      $ct = & git -C $RepoRoot log -1 --format=%ct 2>$null
      if ($LASTEXITCODE -eq 0 -and $ct -match '^\d+$') { return [int64]$ct }
    } catch { }
  }

  try {
    $fi = Get-Item -LiteralPath $SourceFile
    $utc = $fi.LastWriteTimeUtc
    $epoch = [DateTimeOffset]$utc
    return [int64]$epoch.ToUnixTimeSeconds()
  } catch {
    return 0
  }
}

function Hint-PandocInstall {
  @(
    "Install Pandoc and ensure 'pandoc' is in PATH.",
    "Options:",
    "  - Chocolatey (if available): choco install pandoc",
    "  - Manual: download Pandoc installer from pandoc.org and install, then reopen terminal"
  ) -join "`n"
}

function Hint-LaTeXInstall {
  @(
    "Install a LaTeX distribution and ensure 'xelatex' is in PATH.",
    "Options:",
    "  - MiKTeX: install from miktex.org (Windows installer), then reopen terminal",
    "  - TeX Live: install TeX Live for Windows, then reopen terminal",
    "Note: MiKTeX may prompt to install missing packages on first build — allow it."
  ) -join "`n"
}

function Build-WithFonts([string]$src, [string]$outPdf, [string]$resourcePath, [string]$mainFont, [string]$monoFont) {
  $pandocArgs = @(
    $src,
    "--from", "gfm+smart",
    "--standalone",
    "--toc",
    "--toc-depth=3",
    "--number-sections",
    "--pdf-engine=xelatex",
    "--resource-path=$resourcePath",

    "--variable", "mainfont=$mainFont",
    "--variable", "monofont=$monoFont",

    "--variable", "geometry:margin=25mm",
    "--variable", "fontsize=11pt",
    "--variable", "linestretch=1.15",

    "--metadata", "title=EA OC Extension Whitepaper",
    "--metadata", "date=",

    "--output", $outPdf
  )

  Info "Running pandoc (mainfont='$mainFont', monofont='$monoFont')..."
  & pandoc @pandocArgs
  return $LASTEXITCODE
}

# ------------------------------
# Main
# ------------------------------
$repoRoot = Get-RepoRoot
$paperDir = Join-Path $repoRoot "paper"
if (-not (Test-Path -LiteralPath $paperDir)) {
  Fail "Directory not found: $paperDir"
}

$src = Find-WhitepaperSource -PaperDir $paperDir
$outPdf = Join-Path $paperDir "whitepaper.pdf"

$PandocPath = Require-Command -Name "pandoc" -Hint (Hint-PandocInstall)

$XeLaTeXPath = $null
try {
  $XeLaTeXPath = (Get-Command xelatex -ErrorAction Stop).Source
} catch {
  Fail "Missing dependency: 'xelatex' not found in PATH.`nHint: $(Hint-LaTeXInstall)"
}

$epoch = Get-SourceDateEpoch -RepoRoot $repoRoot -SourceFile $src
$env:SOURCE_DATE_EPOCH = "$epoch"
$env:LANG = "en_US.UTF-8"

Info "Repo root : $repoRoot"
Info "Source    : $src"
Info "Output    : $outPdf"
Info "pandoc    : $PandocPath"
Info "xelatex   : $XeLaTeXPath"
Info "SDE       : $env:SOURCE_DATE_EPOCH"
Write-Host ""

$tempDir = Join-Path $repoRoot ".tmp_whitepaper_build"
if (Test-Path -LiteralPath $tempDir) {
  Remove-Item -LiteralPath $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

try {
  Push-Location $repoRoot

  $resourcePath = "$paperDir;$repoRoot"

  # Windows-safe defaults (almost always available)
  $fontAttempts = @(
    @{ main = "Times New Roman"; mono = "Consolas" },
    @{ main = "Cambria";        mono = "Consolas" },
    @{ main = "Times New Roman"; mono = "Courier New" },
    @{ main = "Cambria";        mono = "Courier New" }
  )

  $ok = $false
  foreach ($fa in $fontAttempts) {
    $code = Build-WithFonts -src $src -outPdf $outPdf -resourcePath $resourcePath -mainFont $fa.main -monoFont $fa.mono
    if ($code -eq 0) { $ok = $true; break }
    Warn "pandoc failed (exit code $code) with fonts main='$($fa.main)' mono='$($fa.mono)'. Trying next fallback..."
  }

  if (-not $ok) {
    Fail "pandoc failed with all font fallbacks."
  }

  if (-not (Test-Path -LiteralPath $outPdf)) {
    Fail "Build reported success but output PDF not found: $outPdf"
  }

  Info "OK: Built $outPdf"
}
catch {
  $msg = $_.Exception.Message
  Write-Host ""
  Write-Host "Build failed." -ForegroundColor Red
  Write-Host $msg -ForegroundColor Red
  Write-Host ""
  Write-Host "Common fixes:" -ForegroundColor Yellow
  Write-Host "1) Ensure Pandoc is installed and 'pandoc' is in PATH." -ForegroundColor Yellow
  Write-Host "2) Ensure MiKTeX/TeX Live is installed and 'xelatex' is in PATH." -ForegroundColor Yellow
  Write-Host "3) Reopen VS Code terminal after installing tools (PATH refresh)." -ForegroundColor Yellow
  Write-Host ""
  throw
}
finally {
  Pop-Location
  if (Test-Path -LiteralPath $tempDir) {
    Remove-Item -LiteralPath $tempDir -Recurse -Force -ErrorAction SilentlyContinue
  }
}
