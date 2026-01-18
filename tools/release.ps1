# tools/release.ps1
# Deterministic local release pipeline for ea-oc-extension
# Source of truth: Git state (HEAD + working tree).
# Hard gate: tools/check_whitepaper.ps1 (invoked exactly once).

[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^\d+\.\d+\.\d+(-[0-9A-Za-z\.-]+)?$')]
  [string]$Version,

  [Parameter(Mandatory = $false)]
  [switch]$AutoCommit
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Fail([string]$msg, [int]$code = 1) {
  Write-Error $msg
  exit $code
}

# Resolve git executable explicitly (avoid aliases/functions named "git")
$GitExe = $null
try {
  $GitExe = (Get-Command git -ErrorAction Stop).Source
} catch {
  Fail "git executable not found in PATH." 20
}
if ([string]::IsNullOrWhiteSpace($GitExe)) {
  Fail "git executable not found in PATH." 20
}

function Invoke-GitOut([string[]]$GitArgs) {
  if ($null -eq $GitArgs -or $GitArgs.Count -eq 0) {
    Fail "Internal error: Invoke-GitOut called with empty arguments." 21
  }

  $out = & $GitExe @GitArgs
  if ($LASTEXITCODE -ne 0) {
    Fail "git failed ($LASTEXITCODE): git $($GitArgs -join ' ')" $LASTEXITCODE
  }
  return ($out | Out-String).Trim()
}

function Invoke-Git([string[]]$GitArgs) {
  if ($null -eq $GitArgs -or $GitArgs.Count -eq 0) {
    Fail "Internal error: Invoke-Git called with empty arguments." 22
  }

  Write-Host ">> git $($GitArgs -join ' ')"
  & $GitExe @GitArgs
  if ($LASTEXITCODE -ne 0) {
    Fail "git failed ($LASTEXITCODE): git $($GitArgs -join ' ')" $LASTEXITCODE
  }
}

function Get-WorktreeStatus {
  return (Invoke-GitOut @("status","--porcelain"))
}

$remote = "origin"
$tag = "v$Version"

Write-Host "== RELEASE $tag =="

# --- Preconditions ---
& $GitExe rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "Not inside a git work tree." 10 }

$remotes = Invoke-GitOut @("remote")
$hasOrigin = $false
foreach ($r in ($remotes -split "`n")) {
  if ($r.Trim() -eq $remote) { $hasOrigin = $true }
}
if (-not $hasOrigin) {
  Fail "Remote '$remote' not found. Configure 'origin' (required)." 11
}

# Fetch tags for deterministic tag-exists check
Invoke-Git @("fetch","--tags",$remote)

# Refuse if tag already exists
$existingTag = Invoke-GitOut @("tag","-l",$tag)
if ($existingTag -eq $tag) {
  Fail "Tag already exists: $tag" 12
}

# --- Deterministic cleanliness / optional autocommit ---
$dirty = -not [string]::IsNullOrWhiteSpace((Get-WorktreeStatus))
if ($dirty) {
  if (-not $AutoCommit) {
    Fail "Working tree is dirty. Commit manually or run with -AutoCommit." 13
  }

  Write-Host "== AUTOCOMMIT =="

  Invoke-Git @("add","-A")

  $staged = Invoke-GitOut @("diff","--cached","--name-only")
  if ([string]::IsNullOrWhiteSpace($staged)) {
    Fail "AutoCommit requested but nothing staged (no real changes or only ignored files)." 14
  }

  $msg = "chore(release): prepare $tag"
  Write-Host ">> git commit -m `"$msg`""
  & $GitExe commit -m $msg | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Fail "AutoCommit failed (git commit returned $LASTEXITCODE)." 15
  }
}

# --- HARD GATE (exactly once) ---
$gatePath = Join-Path $PSScriptRoot "check_whitepaper.ps1"
if (-not (Test-Path $gatePath)) {
  Fail "Missing hard gate: tools/check_whitepaper.ps1" 16
}

$before = Get-WorktreeStatus

Write-Host "== HARD GATE: tools/check_whitepaper.ps1 =="
& $gatePath
if ($LASTEXITCODE -ne 0) {
  Fail "Whitepaper gate FAILED (exit $LASTEXITCODE). Release aborted." $LASTEXITCODE
}

$after = Get-WorktreeStatus
if ($before -ne $after) {
  Fail "Gate modified working tree. Forbidden for deterministic release." 17
}

# Ensure clean state AFTER gate
$dirty2 = -not [string]::IsNullOrWhiteSpace((Get-WorktreeStatus))
if ($dirty2) {
  Fail "Working tree is not clean after gate. Commit/fix gate and retry." 18
}

# Identify HEAD for reporting
$head = Invoke-GitOut @("rev-parse","HEAD")
Write-Host ">> HEAD = $head"

# --- Tag (deterministic) ---
Invoke-Git @("tag","-a",$tag,"-m","Release $tag")

# --- Push deterministically ---
Invoke-Git @("push",$remote,"HEAD")
Invoke-Git @("push",$remote,$tag)

Write-Host ""
Write-Host "OK: Release pushed."
Write-Host " - Tag: $tag"
Write-Host " - HEAD: $head"
exit 0
