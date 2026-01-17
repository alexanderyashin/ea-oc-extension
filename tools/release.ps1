param(
  [Parameter(Mandatory=$true)]
  [ValidatePattern('^\d+\.\d+\.\d+([\-+].+)?$')]
  [string]$Version
)

$ErrorActionPreference = "Stop"

function Assert-CleanTree {
  $s = git status --porcelain
  if ($s) {
    Write-Host $s
    throw "Working tree is not clean. Commit/stash first."
  }
}

function Assert-TagNotExists([string]$tag) {
  git rev-parse -q --verify "refs/tags/$tag" *> $null
  if ($LASTEXITCODE -eq 0) {
    throw "Tag already exists: $tag"
  }
}

Write-Host "== RELEASE v$Version =="

Assert-CleanTree

$tag = "v$Version"
Assert-TagNotExists $tag

git tag -a $tag -m "Release $tag"
git push origin main
git push origin $tag

Write-Host "OK: pushed main and tag $tag"
