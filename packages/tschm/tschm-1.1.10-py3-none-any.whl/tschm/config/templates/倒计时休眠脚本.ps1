

# 确保控制台以 UTF-8 输出（防止中文显示为乱码）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
# 对 Windows PowerShell (Desktop) 尝试同时设置 $OutputEncoding 以兼容旧版本
if ($PSVersionTable.PSEdition -eq 'Desktop') {
    $OutputEncoding = [System.Text.Encoding]::UTF8
}

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