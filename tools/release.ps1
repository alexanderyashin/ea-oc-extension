param(
  [Parameter(Mandatory=$true)]
  [ValidateNotNullOrEmpty()]
  [string]$Version
)

$ErrorActionPreference = "Stop"

# ---- gates: whitepaper must pass before release ----
$check = Join-Path $PSScriptRoot "check_whitepaper.ps1"
if (!(Test-Path $check)) {
  Write-Error "Missing gate script: $check"
  exit 2
}
powershell -ExecutionPolicy Bypass -File $check
if ($LASTEXITCODE -ne 0) {
  Write-Error "Whitepaper gates failed. Abort release."
  exit 2
}
# -----------------------------------------------


function Assert-CleanTree {
  $s = git status --porcelain
  if ($s) {
    Write-Error "Working tree is not clean. Commit or stash changes first."
    exit 1
  }
}

function Assert-TagNotExists {
  param([Parameter(Mandatory=$true)][string]$tag)

  # local tag
  git rev-parse -q --verify "refs/tags/$tag" *> $null
  if ($LASTEXITCODE -eq 0) {
    Write-Error "Tag already exists locally: $tag"
    exit 1
  }

  # remote tag
  $remote = git ls-remote --tags origin "refs/tags/$tag"
  if ($remote) {
    Write-Error "Tag already exists on origin: $tag"
    exit 1
  }
}

function Invoke-WhitepaperGates {
  $check = Join-Path $PSScriptRoot "check_whitepaper.ps1"
  if (!(Test-Path $check)) {
    Write-Error "Missing gate script: $check"
    exit 1
  }

  Write-Host "== GATES: whitepaper =="

  # Run as file so it works even if execution policy is restricted in the session
  & powershell -ExecutionPolicy Bypass -File $check
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Whitepaper gates FAILED. Fix paper/whitepaper.md and retry."
    exit 1
  }

  Write-Host "OK: whitepaper gates passed."
}

$tag = "v$Version"

Write-Host "== RELEASE $tag =="

Assert-CleanTree
Invoke-WhitepaperGates
Assert-TagNotExists $tag

# push main first (ensure remote is up to date)
git push origin main
if ($LASTEXITCODE -ne 0) { exit 1 }

# create annotated tag
git tag -a $tag -m "Release $tag"
if ($LASTEXITCODE -ne 0) { exit 1 }

# push tag
git push origin $tag
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "OK: pushed main and tag $tag"
