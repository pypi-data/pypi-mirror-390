

# 设置倒计时时间（秒）
$countdown = 30

Write-Host "系统将在 $countdown 秒后进入休眠模式..."

# 开始倒计时
for ($i = $countdown; $i -gt 0; $i--) {
    Write-Host "`r还剩 $i 秒..." -NoNewline
    Start-Sleep -Seconds 1
}

Write-Host "`n正在进入休眠模式..."
shutdown -h   