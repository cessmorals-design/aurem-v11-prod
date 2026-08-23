function Get-Secure($Name,$Prompt,$Existing=""){
    $vaultPath="$HOME\.aurem\vault.enc.json"
    if ($Existing -and $Existing.Length -gt 5 -and "PASTE" -notin $Existing) { return $Existing }
    if (Test-Path $vaultPath) {
        try {
            $enc=Get-Content $vaultPath -Raw | ConvertFrom-Json
            if ($enc.$Name){ $ss=ConvertTo-SecureString $enc.$Name; $p=[System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($ss)); if ($p.Length -gt 3){ return $p } }
        } catch {}
    }
    Write-Host "$Prompt" -ForegroundColor Yellow
    $sec=Read-Host -AsSecureString "Enter $Name (hidden, Enter to skip if optional)"
    $plain=[System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    if (-not $plain){ return "PASTE_OR_EMPTY" }
    return $plain
}
function Save-Vault($Dict){
    mkdir "$HOME\.aurem" -Force | Out-Null
    $encDict=@{}
    foreach($k in $Dict.Keys){ $sec=ConvertTo-SecureString $Dict[$k] -AsPlainText -Force; $encDict[$k]=ConvertFrom-SecureString $sec }
    $encDict | ConvertTo-Json | Set-Content "$HOME\.aurem\vault.enc.json" -Encoding utf8
    foreach($k in $Dict.Keys){ try{ cmdkey /add:$k /user:$k /pass:$($Dict[$k]) | Out-Null }catch{} }
    Write-Host "VAULT ENCRYPTED DPAPI to $HOME\.aurem\vault.enc.json" -ForegroundColor Green
}
$existing=@{}
if(Test-Path ".env"){ Get-Content ".env" | ForEach-Object { if($_ -match "^(.*?)=(.*)$"){ $existing[$matches[1].Trim()]=$matches[2].Trim() } } }
Write-Host "=== SECURE AUTO FETCH ===" -ForegroundColor Cyan
$keys=@{}
$keys["NGROK_AUTHTOKEN"]=Get-Secure -Name "NGROK_AUTHTOKEN" -Prompt "NGROK Authtoken (dashboard.ngrok.com)" -Existing $existing["NGROK_AUTHTOKEN"]
$keys["TELEGRAM_BOT_TOKEN"]=Get-Secure -Name "TELEGRAM_BOT_TOKEN" -Prompt "Telegram Bot Token (optional)" -Existing $existing["TELEGRAM_BOT_TOKEN"]
$keys["OPENROUTER_KEY"]=Get-Secure -Name "OPENROUTER_KEY" -Prompt "OpenRouter Key sk-or-v1..." -Existing $existing["OPENROUTER_KEY"]
$keys["MPESA_CONSUMER_KEY"]=Get-Secure -Name "MPESA_CONSUMER_KEY" -Prompt "Daraja Consumer Key" -Existing $existing["MPESA_CONSUMER_KEY"]
$keys["MPESA_CONSUMER_SECRET"]=Get-Secure -Name "MPESA_CONSUMER_SECRET" -Prompt "Daraja Consumer Secret" -Existing $existing["MPESA_CONSUMER_SECRET"]
$keys["MPESA_INITIATOR"]=Get-Secure -Name "MPESA_INITIATOR" -Prompt "Mpesa Initiator Name (e.g. testapi)" -Existing $existing["MPESA_INITIATOR"]
$keys["MPESA_INITIATOR_PASSWORD"]=Get-Secure -Name "MPESA_INITIATOR_PASSWORD" -Prompt "Initiator Password (hidden)" -Existing $existing["MPESA_INITIATOR_PASSWORD"]
$keys["FB_PAGE_TOKEN"]=Get-Secure -Name "FB_PAGE_TOKEN" -Prompt "FB Page Token (optional)" -Existing $existing["FB_PAGE_TOKEN"]
$keys["WHATSAPP_TOKEN"]=Get-Secure -Name "WHATSAPP_TOKEN" -Prompt "WhatsApp Token (optional)" -Existing $existing["WHATSAPP_TOKEN"]

$securityCred="PASTE"
try{
    $certPath="$HOME\.aurem\cert.cer"
    if(-not (Test-Path $certPath)){ Invoke-WebRequest "https://developer.safaricom.co.ke/sites/default/files/certs/SandboxCert.cer" -OutFile $certPath -UseBasicParsing }
    $cert=New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($certPath)
    $rsa=$cert.PublicKey.Key
    $bytes=[System.Text.Encoding]::UTF8.GetBytes($keys["MPESA_INITIATOR_PASSWORD"])
    $enc=$rsa.Encrypt($bytes,$false)
    $securityCred=[Convert]::ToBase64String($enc)
    Write-Host "SecurityCredential AUTO-GENERATED from Safaricom cert" -ForegroundColor Green
}catch{ Write-Host "Auto-gen failed, enter manually" -ForegroundColor Yellow; $securityCred=Get-Secure -Name "MPESA_SECURITY_CRED" -Prompt "SecurityCredential manual" -Existing $existing["MPESA_SECURITY_CRED"] }

@"
NGROK_DOMAIN=saturday-cheer-manpower.ngrok-free.dev
NGROK_AUTHTOKEN=$($keys["NGROK_AUTHTOKEN"])
TELEGRAM_BOT_TOKEN=$($keys["TELEGRAM_BOT_TOKEN"])
OPENROUTER_KEY=$($keys["OPENROUTER_KEY"])
MPESA_CONSUMER_KEY=$($keys["MPESA_CONSUMER_KEY"])
MPESA_CONSUMER_SECRET=$($keys["MPESA_CONSUMER_SECRET"])
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_SHORTCODE=174379
MPESA_ENV=sandbox
MPESA_INITIATOR=$($keys["MPESA_INITIATOR"])
MPESA_INITIATOR_PASSWORD=$($keys["MPESA_INITIATOR_PASSWORD"])
MPESA_SECURITY_CRED=$securityCred
FB_PAGE_TOKEN=$($keys["FB_PAGE_TOKEN"])
FB_PAGE_ID=PASTE_OR_EMPTY
WHATSAPP_TOKEN=$($keys["WHATSAPP_TOKEN"])
WHATSAPP_PHONE_ID=PASTE_OR_EMPTY
ADMIN_PHONE=0716706708
"@ | Set-Content.\.env -Encoding utf8
$keys["MPESA_SECURITY_CRED"]=$securityCred
Save-Vault -Dict $keys
Write-Host "ENV READY - LAUNCHING EMPIRE" -ForegroundColor Cyan
taskkill /IM ngrok.exe /F 2>$null; python -c "from pyngrok import ngrok; ngrok.kill()" 2>$null
python v11_max.py
