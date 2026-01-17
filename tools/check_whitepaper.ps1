$ErrorActionPreference = "Stop"

function Fail($msg) {
  Write-Host ""
  Write-Host ("FAIL: " + $msg) -ForegroundColor Red
  exit 2
}

$path = "paper/whitepaper.md"
if (-not (Test-Path $path)) { Fail "Missing paper/whitepaper.md" }

$txt = Get-Content -Raw -Encoding UTF8 $path

# 1) ASCII-only gate
if ($txt -match "[^\x00-\x7F]") {
  Write-Host ("NON-ASCII found in ${path}:") -ForegroundColor Yellow
  [regex]::Matches($txt, "[^\x00-\x7F]") | Select-Object -First 50 Value, Index | Format-Table -AutoSize
  Fail "Whitepaper must be ASCII-only."
}

# 2) No prescriptive language (diagnostic-only)
$bad = @(" should ", " recommend ", " roadmap ", " optimiz", " maturity model ", " playbook ")
$lower = $txt.ToLower()
foreach ($b in $bad) {
  if ($lower.Contains($b.Trim())) {
    Fail ("Prescriptive keyword found: '" + $b.Trim() + "' (diagnostic-only rule)")
  }
}

Write-Host "OK: whitepaper gates passed." -ForegroundColor Green
exit 0
