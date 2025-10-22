param(
  [int]$JobId = $null
)

$ErrorActionPreference = "Stop"

# --- setup paths ---
$results = Join-Path $PWD "results"
if (!(Test-Path $results)) { New-Item -ItemType Directory -Path $results | Out-Null }
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$log = Join-Path $results "export_log.txt"

function Log([string]$msg) {
  "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg" | Out-File -Append -Encoding utf8 $log
}

# --- discover job if needed ---
if (-not $JobId) {
  $jid = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT id FROM jobs ORDER BY id DESC LIMIT 1;"
  $JobId = ($jid | Out-String).Trim()
}
Log "Início export JobId=$JobId (ts=$ts)"
Write-Host ">> Exportando JobId=$JobId  ($ts)"

# --- fetch JSONs dentro da API ---
docker exec -i geoobra_api python -c "import sys,urllib.request as u; jid=int(sys.argv[1]); \
d=u.urlopen(f'http://127.0.0.1:8000/jobs/{jid}/matches_geo?limit=200',timeout=10).read(); open('/tmp/base.json','wb').write(d); \
d=u.urlopen(f'http://127.0.0.1:8000/jobs/{jid}/matches_geo?min_score=0.99&max_distance_km=0.08&limit=200',timeout=10).read(); open('/tmp/filtered.json','wb').write(d); \
print('ok')" $JobId | Out-Null

# --- copy to host with timestamp ---
$baseOut = Join-Path $results ("matches_geo_job{0}_{1}_base.json" -f $JobId, $ts)
$fltOut  = Join-Path $results ("matches_geo_job{0}_{1}_filtered.json" -f $JobId, $ts)
docker cp ("geoobra_api:/tmp/base.json")     $baseOut | Out-Null
docker cp ("geoobra_api:/tmp/filtered.json") $fltOut  | Out-Null
Write-Host "✔ JSON base: $baseOut"
Write-Host "✔ JSON filtrado: $fltOut"

# --- CSV direto do Postgres ---
$copySql = @"
COPY (
  WITH j AS (SELECT id, geom, radius_km FROM jobs WHERE id = $JobId)
  SELECT
    u.id,
    u.email,
    u.lat,
    u.lng,
    u.role,
    ROUND( (ST_DistanceSphere(u.geom, j.geom)/1000.0)::numeric, 6 ) AS distance_km,
    ROUND( GREATEST(0.0, 1.0 - (ST_DistanceSphere(u.geom, j.geom)/1000.0) / NULLIF(j.radius_km,0))::numeric, 6 ) AS score
  FROM users u
  CROSS JOIN j
  WHERE u.role = 'worker'
    AND u.geom IS NOT NULL
    AND ST_DWithin(u.geom::geography, j.geom::geography, j.radius_km * 1000.0, true)
  ORDER BY score DESC NULLS LAST, distance_km ASC
) TO '/tmp/matches_geo_$JobId.csv' WITH (FORMAT CSV, HEADER);
"@
$copySql | docker exec -i geoobra_db psql -U geoobra -d geoobra_db -v ON_ERROR_STOP=1 | Out-Null

$csvOut = Join-Path $results ("matches_geo_job{0}_{1}.csv" -f $JobId, $ts)
docker cp ("geoobra_db:/tmp/matches_geo_{0}.csv" -f $JobId) $csvOut | Out-Null
Write-Host "✔ CSV: $csvOut"

# --- basic validations (não quebra o script se falhar) ---
$okJsonBase = $false
$okJsonFlt  = $false
try { Get-Content -Raw $baseOut | ConvertFrom-Json | Out-Null; $okJsonBase = $true } catch {}
try { Get-Content -Raw $fltOut  | ConvertFrom-Json | Out-Null; $okJsonFlt  = $true } catch {}

# --- log final
Log ("OK: base=`"{0}`" ({1} bytes, json_ok={2}) | filtered=`"{3}`" ({4} bytes, json_ok={5}) | csv=`"{6}`" ({7} bytes)" -f `
     $baseOut,(Get-Item $baseOut).Length,$okJsonBase,$fltOut,(Get-Item $fltOut).Length,$okJsonFlt,$csvOut,(Get-Item $csvOut).Length)

# --- listagem final no console ---
Write-Host "`n== Arquivos gerados ==" -ForegroundColor Cyan
Get-ChildItem $results -File | Sort-Object LastWriteTime -Descending | Select-Object -First 6 Name,Length,@{N="LastWriteTime";E={$_.LastWriteTime.ToString("HH:mm:ss dd/MM/yyyy")}}

# === CALL MERGE_LATEST ===
try {
  # Garante que o merge existe
  if (-not (Test-Path (Join-Path $PWD 'merge_latest.ps1'))) {
    throw 'merge_latest.ps1 não encontrado. Crie-o antes.'
  }

  # Executa merge com thresholds padrão (ajuste se quiser)
  $mergeOut = & (Join-Path $PWD 'merge_latest.ps1') -MinScore 0.99 -MaxDistanceKm 0.08

  # Log amigável
  $log = Join-Path (Join-Path $PWD 'results') 'export_log.txt'
  "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] MERGE: $mergeOut" | Out-File -Append $log
} catch {
  Write-Warning ('Falha ao rodar merge_latest.ps1: ' + $_.Exception.Message)
}
# === /CALL MERGE_LATEST ===

