# Deploy PricePing to AWS EC2
param (
    [Parameter(Mandatory = $false)]
    [string]$KeyPath = "",

    [Parameter(Mandatory = $false)]
    [string]$HostIp = "65.0.199.91",

    [Parameter(Mandatory = $false)]
    [string]$User = "ubuntu"
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🚀 PricePing AWS EC2 Deployment Trigger" -ForegroundColor Cyan
Write-Host "   Host: $User@$HostIp" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Look for SSH key if not provided
if (-not $KeyPath) {
    $commonLocations = @(
        "$env:USERPROFILE\.ssh\id_rsa",
        "$env:USERPROFILE\.ssh\id_ed25519",
        "$env:USERPROFILE\.ssh\priceping.pem",
        "$env:USERPROFILE\Desktop\priceping.pem",
        "$env:USERPROFILE\Downloads\priceping.pem"
    )
    foreach ($loc in $commonLocations) {
        if (Test-Path $loc) {
            $KeyPath = $loc
            Write-Host "🔑 Auto-detected SSH key at: $KeyPath" -ForegroundColor Green
            break
        }
    }
}

$sshCmd = "ssh"
$sshArgs = @("-o", "StrictHostKeyChecking=no")

if ($KeyPath) {
    if (-not (Test-Path $KeyPath)) {
        Write-Error "Specified key file does not exist: $KeyPath"
        exit 1
    }
    $sshArgs += @("-i", $KeyPath)
}

$remoteCommand = 'bash -c "chmod +x ~/PricePing/backend/scripts/deploy_ec2.sh 2>/dev/null || true; if [ -f ~/PricePing/backend/scripts/deploy_ec2.sh ]; then ~/PricePing/backend/scripts/deploy_ec2.sh; else cd ~/PricePing && git pull origin main && docker-compose build backend worker beat && docker-compose up -d; fi"'

Write-Host "📡 Connecting to AWS EC2 ($HostIp)..." -ForegroundColor Yellow
& $sshCmd $sshArgs "$User@$HostIp" $remoteCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host "🌐 Testing remote endpoint: http://$HostIp`:8000/api/health" -ForegroundColor Cyan
    try {
        $res = Invoke-RestMethod -Uri "http://$HostIp`:8000/api/health" -TimeoutSec 10
        Write-Host "   Response: $($res | ConvertTo-Json -Compress)" -ForegroundColor Green
    } catch {
        Write-Host "   Note: Health check request returned: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n❌ Deployment failed or connection was rejected." -ForegroundColor Red
    Write-Host "If permission was denied, pass your private key path with:" -ForegroundColor Yellow
    Write-Host "  .\deploy_aws.ps1 -KeyPath `"C:\path\to\your-key.pem`"" -ForegroundColor Yellow
}
