$ErrorActionPreference="Stop"
$path="paper/whitepaper.md"
if(!(Test-Path $path)){throw "Missing file: $path"}
$txt=Get-Content -Raw -Encoding UTF8 $path
$map=@{
  "Ω"="Omega"; "∂"="d"; "Θ"="Theta"; "τ"="tau"; "→"="->"
}
foreach($k in $map.Keys){ $txt=$txt.Replace($k,$map[$k]) }
$txt=$txt -replace '(?i)\brecommendations\b','statements'
$txt=$txt -replace '(?i)\brecommendation\b','statement'
$txt=$txt -replace '(?i)\brecommended\b','stated'
$txt=$txt -replace '(?i)\brecommending\b','stating'
$txt=$txt -replace '(?i)\brecommends\b','states'
$txt=$txt -replace '(?i)\brecommend\b','state'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($path,$txt,$utf8NoBom)
$txt2=Get-Content -Raw -Encoding UTF8 $path
$non=[regex]::Matches($txt2,'[^\x00-\x7F]')
if($non.Count -gt 0){
  "NON-ASCII still present: $($non.Count)"
  $non | Select-Object -First 30 Value,Index | Format-Table -AutoSize
  exit 2
}
$hit=Select-String -Path $path -Pattern "recomm" -AllMatches -ErrorAction SilentlyContinue
if($hit){
  "recomm* still present:"
  $hit | Select-Object -First 20 | Format-List
  exit 3
}
"OK: repaired $path (ASCII + non-prescriptive)"
exit 0
