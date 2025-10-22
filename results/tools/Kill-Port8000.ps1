param([switch]$VerboseLog)
$log = "$PSScriptRoot\Kill-Port8000.log"
function W($msg){ $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "$ts $msg" | Out-File -Append -Encoding UTF8 $log; if($VerboseLog){Write-Host $msg} }
$cons = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalAddress -eq '127.0.0.1' }
if(-not $cons){ W "OK: nenhum listener em 127.0.0.1:8000"; exit 0 }
$allow = @('com.docker.backend','wslrelay','dockerd','com.docker.proxy')
$killed = @()
foreach($c in $cons){
  try{
    $pid = $c.OwningProcess
    $p = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if(-not $p){ continue }
    if($allow -contains $p.ProcessName){ W "KEEP [$pid] $($p.ProcessName)"; continue }
    if($p.ProcessName -in @('python','pythonw','node','gunicorn','uvicorn')){
      W "KILL [$pid] $($p.ProcessName) por conflito em 127.0.0.1:8000"
      Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
      $killed += $pid
    } else {
      W "WARN: listener desconhecido [$pid] $($p.ProcessName) — não matado"
    }
  } catch {
    W "ERR ao tratar PID $pid: $($_.Exception.Message)"
  }
}
if($killed.Count -gt 0){ W ("Resumo: Killed PIDs: " + ($killed -join ',')) } else { W "Resumo: nada para matar" }
