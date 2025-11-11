

# 文件格式必须保存成为 UTF-8 with BOM 格式，否则中文显示乱码 

# 设置倒计时时间（秒）
$countdown = 30

# 加载Windows.Forms命名空间以使用通知功能
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 创建通知图标
$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$notifyIcon.Visible = $true

# 显示初始通知
$notifyIcon.ShowBalloonTip(
    2000,  # 显示时长(毫秒)
    "系统休眠提示",
    "系统将在 $countdown 秒后进入休眠模式",
    [System.Windows.Forms.ToolTipIcon]::Info
)

# 开始倒计时
for ($i = $countdown; $i -gt 0; $i--) {
    if ($i % 5 -eq 0) {  # 每5秒显示一次通知
        $notifyIcon.ShowBalloonTip(
            2000,
            "系统休眠倒计时",
            "还剩 $i 秒进入休眠模式",
            [System.Windows.Forms.ToolTipIcon]::Info
        )
    }
    Write-Host "`r还剩 $i 秒..." -NoNewline
    Start-Sleep -Seconds 1
}

# 显示最终通知
$notifyIcon.ShowBalloonTip(
    2000,
    "系统休眠提示",
    "正在进入休眠模式...",
    [System.Windows.Forms.ToolTipIcon]::Warning
)

# 清理通知图标
$notifyIcon.Dispose()

Write-Host "`n正在进入休眠模式..."
shutdown -h   

