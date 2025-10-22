$ErrorActionPreference = "Stop"

# Helpers
function Get-LastDigits([string]$s) {
  $m = [regex]::Matches($s, '\d+')
  if ($m.Count -gt 0) { return $m[$m.Count-1].Value } else { return "" }
}

# Pasta de resultados
$resultsDir = Join-Path $PWD "results"
if (!(Test-Path $resultsDir)) { New-Item -ItemType Directory -Path $resultsDir | Out-Null }

# ========== 1) Job base e criação de um novo job perto ==========
$jidBaseRaw = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT id FROM jobs ORDER BY id DESC LIMIT 1;"
$jobBase = Get-LastDigits $jidBaseRaw
if (-not $jobBase) { throw "Não há job base na tabela jobs." }

$jl = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -F '|' -c "SELECT lat,lng FROM jobs WHERE id=$jobBase;"
$parts = $jl.Trim() -split '\|'
$baseLat = [double]$parts[0]
$baseLng = [double]$parts[1]

$offLat = [math]::Round((Get-Random -Minimum -0.0010 -Maximum 0.0010),6)
$offLng = [math]::Round((Get-Random -Minimum -0.0010 -Maximum 0.0010),6)
$newLat = $baseLat + $offLat
$newLng = $baseLng + $offLng

$insJob = @"
INSERT INTO jobs (title, description, company_id, lat, lng, radius_km)
VALUES ('Pintor residencial (auto)','Gerado pelo pipeline',1,$newLat,$newLng,15)
RETURNING id;
"@
$jidNewRaw = $insJob | docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A
$jobId = Get-LastDigits $jidNewRaw
if (-not $jobId) { throw "Falha ao obter novo jobId: saída=[$jidNewRaw]" }
"==> Novo jobId = [$jobId]  lat=$newLat  lng=$newLng"

$fixJobGeom = "UPDATE jobs SET geom = ST_SetSRID(ST_MakePoint(lng, lat),4326) WHERE id=$jobId AND geom IS NULL;"
$fixJobGeom | docker exec -i geoobra_db psql -U geoobra -d geoobra_db | Out-Null

# ========== 2) Seed/Upsert de 12 workers ao redor do novo job ==========
for ($i=1; $i -le 12; $i++) {
  $email = "wp$jobId`_$i@example.com"
  $exists = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT 1 FROM users WHERE email='$email' LIMIT 1;"
  if (-not ($exists -and $exists.Trim())) {
    $oLat = [math]::Round((Get-Random -Minimum -0.0010 -Maximum 0.0010),6)
    $oLng = [math]::Round((Get-Random -Minimum -0.0010 -Maximum 0.0010),6)
    $lat = $newLat + $oLat
    $lng = $newLng + $oLng
    $q = "INSERT INTO users (email,name,role,password_hash,lat,lng) VALUES ('$email','Worker P$jobId-$i','worker','x',$lat,$lng);"
    $q | docker exec -i geoobra_db psql -U geoobra -d geoobra_db | Out-Null
    "✔ Inserido $email ($lat,$lng)"
  } else {
    "↷ Já existe: $email"
  }
}

"==> Atualizando geom de workers..."
"UPDATE users SET lat=lat WHERE email LIKE 'wp$jobId`_%@example.com' AND lat IS NOT NULL AND lng IS NOT NULL;" | docker exec -i geoobra_db psql -U geoobra -d geoobra_db | Out-Null

# ========== 3) Diagnóstico de distâncias (top 10) ==========
"==> Distâncias (m/km):"
$distSql = @"
WITH j AS (SELECT id,geom,radius_km FROM jobs WHERE id = $jobId)
SELECT u.email,
       ROUND(ST_DistanceSphere(u.geom,j.geom)::numeric,2) AS meters,
       ROUND((ST_DistanceSphere(u.geom,j.geom)/1000.0)::numeric,6) AS km
FROM users u
CROSS JOIN j
WHERE u.role='worker' AND u.geom IS NOT NULL AND j.geom IS NOT NULL
ORDER BY km ASC
LIMIT 10;
"@
$distSql | docker exec -i geoobra_db psql -U geoobra -d geoobra_db

# ========== 4) Chama endpoint e salva JSON no container ==========
$uri = "http://127.0.0.1:8000/jobs/$jobId/matches_geo?limit=200"
"==> GET: $uri"
docker exec -it geoobra_api python -c "import sys,urllib.request;u=sys.argv[1];d=urllib.request.urlopen(u,timeout=10).read();open('/tmp/matches_geo_%s.json'%sys.argv[2],'wb').write(d);print('OK JSON:','/tmp/matches_geo_%s.json'%sys.argv[2])" "$uri" "$jobId"

# ========== 5) Exporta CSV via COPY server-side ==========
$csvPath = "/tmp/matches_geo_${jobId}.csv"
$csvSql = @"
WITH j AS (
  SELECT id, geom, radius_km AS r
  FROM jobs
  WHERE id = $jobId
), m AS (
  SELECT
    u.id,
    u.email,
    u.lat,
    u.lng,
    u.role,
    ST_DistanceSphere(u.geom, j.geom) / 1000.0 AS distance_km,
    GREATEST(0.0, 1.0 - (ST_DistanceSphere(u.geom, j.geom) / 1000.0) / NULLIF(j.r,0)) AS score
  FROM users u
  CROSS JOIN j
  WHERE u.role = 'worker'
    AND u.geom IS NOT NULL
    AND j.r IS NOT NULL
    AND ST_DWithin(u.geom::geography, j.geom::geography, j.r * 1000.0)
  ORDER BY score DESC NULLS LAST, distance_km ASC
)
COPY (
  SELECT id,email,lat,lng,role,
         ROUND(distance_km::numeric,6) AS distance_km,
         ROUND(score::numeric,6)       AS score
  FROM m
) TO '$csvPath' WITH CSV HEADER;
"@
$csvSql | docker exec -i geoobra_db psql -U geoobra -d geoobra_db

# ========== 6) Copia JSON/CSV pro host e mostra resumo ==========
$destJson = Join-Path $resultsDir ("matches_geo_job{0}.json" -f $jobId)
$destCsv  = Join-Path $resultsDir ("matches_geo_job{0}.csv"  -f $jobId)
docker cp ("geoobra_api:/tmp/matches_geo_{0}.json" -f $jobId) $destJson
docker cp ("geoobra_db:$csvPath") $destCsv

"Arquivo JSON: $destJson"
"Arquivo CSV : $destCsv"

(Get-Content $destJson -Raw | ConvertFrom-Json) | ForEach-Object {
  "`n== RESULTADO JSON =="
  "job_id: $($_.job_id)"
  "radius_km: $($_.radius_km)"
  "count: $($_.count)"
  "top10:"
  $_.results | Select-Object -First 10 | ForEach-Object {
    " - id=$($_.id) email=$($_.email) dist_km=$([math]::Round([double]$_.distance_km,6)) score=$([math]::Round([double]$_.score,6))"
  }
}
