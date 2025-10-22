$ErrorActionPreference = "Stop"
$resultsDir = Join-Path $PWD "results"
if (!(Test-Path $resultsDir)) { New-Item -ItemType Directory -Path $resultsDir | Out-Null }

# 1) Captura jobId atual
$jid = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT id FROM jobs ORDER BY id DESC LIMIT 1;"
$jobId = ($jid -replace '[^\d]','').Trim()
"==> jobId = [$jobId]"

# 2) Gera 10 workers (com tratamento para null)
for ($i=1; $i -le 10; $i++) {
  $email = "w$i@example.com"
  $existsRaw = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT 1 FROM users WHERE email='$email' LIMIT 1;"
  $exists = if ($existsRaw) { $existsRaw.ToString().Trim() } else { "" }

  if ($exists -eq "") {
    $offsetLat = [math]::Round((Get-Random -Minimum -0.0009 -Maximum 0.0009),6)
    $offsetLng = [math]::Round((Get-Random -Minimum -0.0009 -Maximum 0.0009),6)
    $jobCoords = docker exec -i geoobra_db psql -U geoobra -d geoobra_db -t -A -c "SELECT lat,lng FROM jobs WHERE id=$jobId;"
    $coords = $jobCoords.Trim() -split '\|'
    $lat = [double]$coords[0] + $offsetLat
    $lng = [double]$coords[1] + $offsetLng
    $q = "INSERT INTO users (email,name,role,password_hash,lat,lng) VALUES ('$email','Worker $i','worker','x',$lat,$lng);"
    $q | docker exec -i geoobra_db psql -U geoobra -d geoobra_db | Out-Null
    Write-Host "✔ Inserido $email ($lat,$lng)"
  } else {
    Write-Host "↷ Já existe: $email"
  }
}

# 3) Atualiza geom (gatilho)
"==> Atualizando geom..."
"UPDATE users SET lat=lat WHERE email LIKE 'w%@example.com' AND lat IS NOT NULL AND lng IS NOT NULL;" | docker exec -i geoobra_db psql -U geoobra -d geoobra_db | Out-Null
"==> Workers inseridos:"
"SELECT id,email,lat,lng,(geom IS NOT NULL) geom_ok FROM users WHERE email LIKE 'w%@example.com' ORDER BY id;" | docker exec -i geoobra_db psql -U geoobra -d geoobra_db

# 4) Distâncias
"==> Distâncias (metros/km):"
$distSql = @"
WITH j AS (SELECT id,geom,radius_km FROM jobs WHERE id=$jobId)
SELECT u.email,
       ROUND(ST_DistanceSphere(u.geom,j.geom)::numeric,2) AS meters,
       ROUND(ST_DistanceSphere(u.geom,j.geom)/1000,6) AS km
FROM users u CROSS JOIN j
WHERE u.role='worker' AND u.geom IS NOT NULL
ORDER BY km ASC LIMIT 10;
"@
$distSql | docker exec -i geoobra_db psql -U geoobra -d geoobra_db

# 5) Endpoint matches_geo
$uri = "http://127.0.0.1:8000/jobs/$jobId/matches_geo?limit=50"
"==> Chamando endpoint: $uri"
docker exec -it geoobra_api python -c "import sys,urllib.request;u=sys.argv[1];d=urllib.request.urlopen(u,timeout=10).read();open('/tmp/matches_geo_%s.json'%sys.argv[2],'wb').write(d);print('OK:','/tmp/matches_geo_%s.json'%sys.argv[2])" "$uri" "$jobId"

# 6) Copiar JSON + resumo
$destFile = Join-Path $resultsDir ("matches_geo_job{0}.json" -f $jobId)
docker cp ("geoobra_api:/tmp/matches_geo_{0}.json" -f $jobId) $destFile
"Arquivo salvo: $destFile"

(Get-Content $destFile -Raw | ConvertFrom-Json) | ForEach-Object {
  "`n== RESULTADO JSON =="
  "job_id: $($_.job_id)"
  "radius_km: $($_.radius_km)"
  "count: $($_.count)"
  "top10:"
  $_.results | Select-Object -First 10 | ForEach-Object {
    " - id=$($_.id) email=$($_.email) dist_km=$([math]::Round([double]$_.distance_km,6)) score=$([math]::Round([double]$_.score,6))"
  }
}
