# Deploy PricePing Frontend to Netlify
param (
    [Parameter(Mandatory = $false)]
    [switch]$Prod = $true
)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "🌐 PricePing Netlify Frontend Deployment" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Build the frontend
Write-Host "📦 1. Compiling production frontend bundle..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\frontend"
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Error "Frontend compilation failed. Please fix TypeScript/build errors before deploying."
    Set-Location $PSScriptRoot
    exit 1
}

Set-Location $PSScriptRoot
Write-Host "✅ Build succeeded! Static bundle ready in frontend/dist." -ForegroundColor Green

# 2. Deploy using Netlify CLI
Write-Host "🚀 2. Deploying to Netlify..." -ForegroundColor Yellow
if ($Prod) {
    npx --yes netlify-cli deploy --prod --dir="frontend/dist"
} else {
    npx --yes netlify-cli deploy --dir="frontend/dist"
}
