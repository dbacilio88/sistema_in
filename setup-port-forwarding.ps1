# ================================================
# WSL Port Forwarding Setup Script
# ================================================
# This script must be run as Administrator
# Right-click PowerShell and select "Run as Administrator"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "WSL Port Forwarding Configuration" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Get WSL IP
Write-Host "Getting WSL IP address..." -ForegroundColor Yellow
$wslIp = "172.30.107.23"  # Your current WSL IP
Write-Host "WSL IP: $wslIp`n" -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'`n" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Administrator privileges confirmed.`n" -ForegroundColor Green

# Remove existing rules (if any)
Write-Host "Removing existing port forwarding rules..." -ForegroundColor Yellow
netsh interface portproxy delete v4tov4 listenport=3002 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=8001 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=9000 listenaddress=0.0.0.0 2>$null
netsh interface portproxy delete v4tov4 listenport=9001 listenaddress=0.0.0.0 2>$null

# Add port forwarding rules
Write-Host "`nAdding port forwarding rules...`n" -ForegroundColor Yellow

Write-Host "  [1/5] Frontend (3002)" -ForegroundColor Cyan
netsh interface portproxy add v4tov4 listenport=3002 listenaddress=0.0.0.0 connectport=3002 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "        ✓ Frontend port forwarding configured" -ForegroundColor Green
} else {
    Write-Host "        ✗ Failed to configure frontend port" -ForegroundColor Red
}

Write-Host "  [2/5] Django API (8000)" -ForegroundColor Cyan
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "        ✓ Django API port forwarding configured" -ForegroundColor Green
} else {
    Write-Host "        ✗ Failed to configure Django port" -ForegroundColor Red
}

Write-Host "  [3/5] Inference Service (8001)" -ForegroundColor Cyan
netsh interface portproxy add v4tov4 listenport=8001 listenaddress=0.0.0.0 connectport=8001 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "        ✓ Inference service port forwarding configured" -ForegroundColor Green
} else {
    Write-Host "        ✗ Failed to configure inference port" -ForegroundColor Red
}

Write-Host "  [4/5] MinIO API (9000)" -ForegroundColor Cyan
netsh interface portproxy add v4tov4 listenport=9000 listenaddress=0.0.0.0 connectport=9000 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "        ✓ MinIO API port forwarding configured" -ForegroundColor Green
} else {
    Write-Host "        ✗ Failed to configure MinIO API port" -ForegroundColor Red
}

Write-Host "  [5/5] MinIO Console (9001)" -ForegroundColor Cyan
netsh interface portproxy add v4tov4 listenport=9001 listenaddress=0.0.0.0 connectport=9001 connectaddress=$wslIp
if ($LASTEXITCODE -eq 0) {
    Write-Host "        ✓ MinIO Console port forwarding configured" -ForegroundColor Green
} else {
    Write-Host "        ✗ Failed to configure MinIO Console port" -ForegroundColor Red
}

# Show current configuration
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "Current Port Forwarding Rules:" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan
netsh interface portproxy show all

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green

Write-Host "You can now access the application at:" -ForegroundColor Yellow
Write-Host "  • Frontend:       http://localhost:3002" -ForegroundColor White
Write-Host "  • Django API:     http://localhost:8000" -ForegroundColor White
Write-Host "  • Inference API:  http://localhost:8001" -ForegroundColor White
Write-Host "  • MinIO Console:  http://localhost:9001" -ForegroundColor White

Write-Host "`nTo remove these rules in the future, run:" -ForegroundColor Yellow
Write-Host "  netsh interface portproxy reset" -ForegroundColor White

Write-Host "`nNOTE: These rules will persist across reboots." -ForegroundColor Cyan
Write-Host "      If your WSL IP changes, you'll need to run this script again.`n" -ForegroundColor Cyan

pause
