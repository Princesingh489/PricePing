$keyPath = "C:\Users\Prince\.ssh\priceping-key.pem"
Copy-Item "D:\Downloads\priceping-key.pem" $keyPath -Force

icacls.exe $keyPath /reset
icacls.exe $keyPath /inheritance:d
icacls.exe $keyPath /remove "NT AUTHORITY\Authenticated Users"
icacls.exe $keyPath /remove "BUILTIN\Users"
icacls.exe $keyPath /grant:r "$($env:USERNAME):(R)"

Write-Host "Connecting via SSH..."
ssh -i $keyPath -o StrictHostKeyChecking=no ubuntu@15.252.173.128 "echo SSH_CONNECTED && cd ~/PricePing && docker compose up -d && docker compose ps"
