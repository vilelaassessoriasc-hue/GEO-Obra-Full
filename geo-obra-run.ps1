param(
  [string]$AdminEmail = "admin@example.com",
  [string]$AdminPass  = "123456",
  [int]$Radius10 = 10,
  [int]$Radius30 = 30,
  [int]$Radius100 = 100
)

$ErrorActionPreference = "Stop"
$base = "http://localhost:8080"

# ==== 0) Pasta de saída ====
$ts = Get-Date -Format "yyyyMMdd-HHmmss"
$outDir = Join-Path (Get-Location) "runs\$ts"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

# ==== 1) Login admin ====
try {
  $login = Invoke-RestMethod -Uri "$base/auth/login" -Method POST `
            -Body (@{ email=$AdminEmail; password=$AdminPass } | ConvertTo-Json) `
            -ContentType "application/json"
} catch {
  throw "Falha no login do admin ($AdminEmail). Verifique se ele existe e a senha."
}
$token = $login.access_token
$headers = @{ Authorization = "Bearer $token" }
Write-Host ("Token OK (preview): {0}..." -f $token.Substring(0,30)) -ForegroundColor Green

# ==== 2) Garantir geom/index ====
docker compose exec db psql -U geo -d geoobra -c "UPDATE users SET geom = ST_SetSRID(ST_MakePoint(lng,lat),4326) WHERE geom IS NULL AND lat IS NOT NULL AND lng IS NOT NULL;" | Out-Null
docker compose exec db psql -U geo -d geoobra -c "UPDATE jobs  SET geom = ST_SetSRID(ST_MakePoint(lng,lat),4326) WHERE geom IS NULL AND lat IS NOT NULL AND lng IS NOT NULL;"  | Out-Null
docker compose exec db psql -U geo -d geoobra -c "CREATE INDEX IF NOT EXISTS idx_users_geom ON users USING GIST (geom);" | Out-Null
docker compose exec db psql -U geo -d geoobra -c "CREATE INDEX IF NOT EXISTS idx_jobs_geom  ON jobs  USING GIST (geom);" | Out-Null

# ==== 3) Garantir empresa e job ====
# se não existir company_id=1, cria uma rapidamente
$hasCompany = docker compose exec db bash -lc "psql -U geo -d geoobra -tAc ""SELECT COUNT(1) FROM companies WHERE id=1;"""
if ([int]$hasCompany -eq 0) {
  docker compose exec db bash -lc "psql -U geo -d geoobra -tAc ""INSERT INTO companies(id,name) VALUES (1,'GeoObra Ltda') ON CONFLICT DO NOTHING;""" | Out-Null
}

# cria job padrão (SP) com company_id=1
$jobBody = @{
  title="Pedreiro (SP)"
  company_id=1
  lat=-23.55052
  lng=-46.63331
  radius_km=100
} | ConvertTo-Json

$job = $null
try {
  $job = Invoke-RestMethod -Uri "$base/jobs" -Headers $headers -Method POST -Body $jobBody -ContentType "application/json"
  Write-Host ("Job criada: id={0} | title={1}" -f $job.id, $job.title) -ForegroundColor Green
} catch {
  Write-Host "Não criei nova job (talvez já exista). Vou usar a mais recente..." -ForegroundColor Yellow
}
if ($null -eq $job) {
  $jid = docker compose exec db bash -lc "psql -U geo -d geoobra -tAc ""SELECT id FROM jobs ORDER BY id DESC LIMIT 1;"""
  if (-not $jid) { throw "Nenhuma job encontrada." }
  $job = @{ id = [int]$jid; title = "(existente)" }
}
$jobId = [int]$job.id

# ==== 4) Exportar /matches_geo (10,30,100) em JSON + CSV consolidado ====
$radii = @($Radius10, $Radius30, $Radius100)
$all = @()

foreach ($r in $radii) {
  $geo = Invoke-RestMethod -Uri "$base/jobs/$jobId/matches_geo?radius_km=$r" -Headers $headers -Method GET
  ($geo | ConvertTo-Json -Depth 10) | Out-File (Join-Path $outDir ("matches_geo_{0}km.json" -f $r)) -Encoding UTF8
  Write-Host ("radius={0}km -> count={1} total={2}" -f $r, $geo.count, $geo.total_count)

  if ($geo.results) {
    $rows = $geo.results | ForEach-Object {
      [PSCustomObject]@{
        job_id      = $jobId
        radius_km   = $r
        id          = $_.id
        email       = $_.email
        lat         = $_.lat
        lng         = $_.lng
        distance_km = [math]::Round([double]$_.distance_km,2)
        score       = [math]::Round([double]$_.score,2)
      }
    }
    $all += $rows
  }
}

$csvPath = Join-Path $outDir "matches_geo_all.csv"
$all | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

Write-Host "`n✅ Concluído. Artefatos:" -ForegroundColor Green
Write-Host "• JSONs: $(Join-Path $outDir 'matches_geo_10km.json'), 30km, 100km"
Write-Host "• CSV:   $csvPath"
if ($all.Count -gt 0) {
  Write-Host "`nPreview:" -ForegroundColor Yellow
  $all | Select-Object -First 10 |
    Select-Object job_id,radius_km,id,email,
      @{Name='lat';Expression={[string]::Format("{0:N5}", $_.lat)}},
      @{Name='lng';Expression={[string]::Format("{0:N5}", $_.lng)}},
      @{Name='distance_km';Expression={[string]::Format("{0:N2}", $_.distance_km)}},
      @{Name='score';Expression={[string]::Format("{0:N2}", $_.score)}} |
    Format-Table -AutoSize
}
