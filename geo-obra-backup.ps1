# --- Telegram Error Alert (auto-prepend) ---
trap {
    $botToken = "8235446354:AAEfepW06cvwxUhcqB4l5u43e4ur4wDorqc"
    $chatId   = "8182514894"
    $errMsg = $_.Exception.Message
    $now = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
    $msg = "⚠ *Falha no Backup GeoObra!*`n🕒 Data: $now`n❌ Erro: $errMsg"
    $uri = "https://api.telegram.org/bot$botToken/sendMessage"
    Invoke-RestMethod -Uri $uri -Method POST -Body @{ chat_id=$chatId; text=$msg; parse_mode="Markdown" }
    break
}
# --- end Telegram error alert ---
# --- Telegram Notification (auto-appended) ---
$botToken = "8235446354:AAEfepW06cvwxUhcqB4l5u43e4ur4wDorqc"
$chatId   = "8182514894"
$now = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
$backupDir = "C:\Users\Vilela ATM AI\Desktop\GEO-Obra-backup-20251020-161333\backups"
$last = Get-ChildItem -Directory $backupDir | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$msg = "📦 Backup GeoObra Concluído com Sucesso!`n🕒 Data: $now`n📁 Pasta: $($last.FullName)`n✅ Status: OK"
$uri = "https://api.telegram.org/bot$botToken/sendMessage"
Invoke-RestMethod -Uri $uri -Method POST -Body @{ chat_id=$chatId; text=$msg }
# --- end Telegram block ---

# --- Telegram Status Summary (enhanced) ---
$botToken = "8235446354:AAEfepW06cvwxUhcqB4l5u43e4ur4wDorqc"
$chatId   = "8182514894"
$now = Get-Date -Format "dd/MM/yyyy HH:mm:ss"
$duration = (New-TimeSpan -Start $scriptStart -End (Get-Date)).ToString("hh\:mm\:ss")
$backupDir = "C:\Users\Vilela ATM AI\Desktop\GEO-Obra-backup-20251020-161333\backups"
$last = Get-ChildItem -Directory $backupDir | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($LASTEXITCODE -eq 0) {
    $statusIcon = "🟢"
    $statusMsg = "Backup concluído com sucesso"
} elseif ($LASTEXITCODE -gt 0 -and $LASTEXITCODE -lt 5) {
    $statusIcon = "🟠"
    $statusMsg = "Backup concluído parcialmente"
} else {
    $statusIcon = "🔴"
    $statusMsg = "Erro crítico no backup"
}

$msg = @"
$statusIcon Status do Backup GeoObra
🕒 Data: $now
⏱ Duração: $duration
📁 Pasta: $($last.FullName)
📋 Resultado: $statusMsg
"@

$uri = "https://api.telegram.org/bot$botToken/sendMessage"
Invoke-RestMethod -Uri $uri -Method POST -Body @{ chat_id=$chatId; text=$msg; parse_mode="Markdown" }
# --- end Telegram status summary ---

# --- Telegram CSV Report (daily attach) ---
$botToken = "8235446354:AAEfepW06cvwxUhcqB4l5u43e4ur4wDorqc"
$chatId   = "8182514894"
$backupDir = "C:\Users\Vilela ATM AI\Desktop\GEO-Obra-backup-20251020-161333\backups"
$latest = Get-ChildItem -Directory $backupDir | Sort-Object LastWriteTime -Descending | Select-Object -First 1

$csvs = Get-ChildItem -Path $latest.FullName -Filter "*.csv"
foreach ($file in $csvs) {
    $uri = "https://api.telegram.org/bot$botToken/sendDocument"
    Write-Host "📤 Enviando relatório: $($file.Name) para Telegram..."
    Invoke-RestMethod -Uri $uri -Method Post -Form @{ chat_id = $chatId; document = Get-Item $file.FullName }
}
Write-Host "✅ Relatórios CSV enviados via Telegram com sucesso." -ForegroundColor Green
# --- end Telegram CSV Report ---
