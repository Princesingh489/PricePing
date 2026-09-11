param (
    [string]$KeyPath = "",
    [string]$HostIp = "13.201.130.193",
    [string]$User = "ubuntu"
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " PricePing AWS EC2 Deployment" -ForegroundColor Cyan
Write-Host " Host: $User@$HostIp" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (-not $KeyPath) {
    $candidates = @(
        "$env:USERPROFILE\.ssh\id_rsa",
        "$env:USERPROFILE\.ssh\id_ed25519",
        "$env:USERPROFILE\.ssh\priceping.pem",
        "$env:USERPROFILE\Desktop\priceping.pem",
        "$env:USERPROFILE\Downloads\priceping.pem"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $KeyPath = $cand
            Write-Host "Auto-detected key: $KeyPath" -ForegroundColor Green
            break
        }
    }
}

$argsList = @("-o", "StrictHostKeyChecking=no")
if ($KeyPath) {
    if (-not (Test-Path $KeyPath)) {
        Write-Error "Key file not found: $KeyPath"
        exit 1
    }
    $argsList += @("-i", $KeyPath)
}

$cmd = "cd ~/PricePing && git pull origin main && chmod +x backend/scripts/deploy_ec2.sh && ./backend/scripts/deploy_ec2.sh"
$argsList += @("$User@$HostIp", $cmd)

Write-Host "Connecting to AWS EC2 ($HostIp)..." -ForegroundColor Yellow
& ssh @argsList

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Testing health check: http://${HostIp}:8000/api/health" -ForegroundColor Cyan
    try {
        $res = Invoke-RestMethod -Uri "http://${HostIp}:8000/api/health" -TimeoutSec 10
        Write-Host "Response: $($res | ConvertTo-Json -Compress)" -ForegroundColor Green
    } catch {
        Write-Host "Health check response: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "Connection rejected or deployment returned non-zero code." -ForegroundColor Red
    Write-Host "Usage with private key:" -ForegroundColor Yellow
    Write-Host '.\deploy_aws.ps1 -KeyPath "path\to\your-key.pem"' -ForegroundColor Yellow
}
