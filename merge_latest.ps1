param(
  [double]$MinScore = 0.99,
  [double]$MaxDistanceKm = 0.08
)

Add-Type -AssemblyName System.Globalization | Out-Null
$cult = [System.Globalization.CultureInfo]::InvariantCulture
$ptBR = [System.Globalization.CultureInfo]::GetCultureInfo('pt-BR')

$results  = Join-Path $PWD "results"
$filtered = Get-ChildItem $results -Filter "matches_geo_job*_filtered.json" |
  Sort-Object LastWriteTime -Desc | Select-Object -First 1

$csv = Get-ChildItem $results -Filter "matches_geo_job*.csv" |
  Where-Object { $_.Name -notmatch '_merged' } |
  Sort-Object LastWriteTime -Desc | Select-Object -First 1

"filtered JSON => $($filtered.FullName)"
"CSV CRU      => $($csv.FullName)"

$jf = Get-Content -Raw $filtered.FullName | ConvertFrom-Json
$inFiltered = @{}
foreach ($r in $jf.results) {
  $inFiltered["$($r.id)"] = @{
    score = [double]$r.score
    distance_km = [double]$r.distance_km
  }
}

function Parse-DoubleFlex([string]$s) {
  try { return [double]::Parse($s, $cult) } catch {}
  try { return [double]::Parse($s, $ptBR) } catch {}
  return [double]::Parse(($s -replace ',','.'), $cult)
}

$rows = Import-Csv $csv.FullName | ForEach-Object {
  $idStr = "$($_.id)"
  $dist  = Parse-DoubleFlex $_."distance_km"
  $score = Parse-DoubleFlex $_."score"

  $isIn  = $inFiltered.ContainsKey($idStr)
  $reason = if ($isIn) { "ok" } else {
    $reasons = @()
    if ($dist  -gt $MaxDistanceKm) { $reasons += "dist>$MaxDistanceKm" }
    if ($score -lt $MinScore)      { $reasons += "score<$MinScore" }
    if ($reasons.Count -eq 0)      { $reasons = @("fora_do_filtro_manual") }
    ($reasons -join "|")
  }

  [pscustomobject]@{
    id              = $idStr
    email           = $_.email
    lat             = $_.lat
    lng             = $_.lng
    role            = $_.role
    distance_km_num = $dist
    score_num       = $score
    distance_km     = $dist.ToString("F6", $cult)
    score           = $score.ToString("F6", $cult)
    InFiltered      = $isIn
    Reason          = $reason
  }
}

$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$merged = Join-Path $results ((Split-Path $csv.Name -LeafBase) + "_merged_v3_$ts.csv")
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 $merged

$total = $rows.Count
$inOK  = ($rows | Where-Object {$_.InFiltered -eq $true}).Count
$out   = $total - $inOK
"`nArquivo gerado: $merged"
"Resumo: total=$total  in_filtered=$inOK  out=$out"
"`nTop 10:"
$rows | Select-Object -First 10 id,email,distance_km,score,InFiltered,Reason | Format-Table
