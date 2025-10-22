param(
  [string]$Image = "ghcr.io/vilelaassessoriasc-hue/geo-obra-full-api:latest"
)

Write-Host ">> Subindo stack com imagem $Image" -ForegroundColor Cyan
$env:IMAGE = $Image
docker compose -f docker-compose.deploy.yml up -d --pull always

Write-Host ">> Aguardando saúde da API..." -ForegroundColor DarkCyan
for ($i=0; $i -lt 15; $i++) {
  try {
    $r = curl.exe --noproxy "*" -m 3 -s -o NUL -w "%{http_code}" http://127.0.0.1:8000/health
    if ($r -eq "200") { Write-Host "OK /health 200"; break }
  } catch {}
  Start-Sleep -Seconds 2
}
Write-Host ">> Containers:" -ForegroundColor DarkCyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
