param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]] $Args
)

# One-shot wrapper. No loops. No state. Diagnostic-only.
# Ensures src-layout imports work without user-managed PYTHONPATH.

$old = $env:PYTHONPATH
try {
  $repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
  $srcPath  = (Join-Path $repoRoot "src")

  if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $env:PYTHONPATH = $srcPath
  } else {
    $env:PYTHONPATH = "$srcPath;$env:PYTHONPATH"
  }

  python -m ops3d_cli @Args
  exit $LASTEXITCODE
}
finally {
  $env:PYTHONPATH = $old
}
