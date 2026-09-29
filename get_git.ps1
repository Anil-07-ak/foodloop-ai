$zipPath = "C:\Users\Chandu M\.gemini\antigravity\scratch\mingit.zip"
$extractPath = "C:\Users\Chandu M\.gemini\antigravity\scratch\mingit"

if (-not (Test-Path "$extractPath\cmd\git.exe")) {
    Write-Host "Downloading Portable Git..."
    $url = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/MinGit-2.44.0-64-bit.zip"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
    
    Write-Host "Extracting Git..."
    Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force
}

$gitExe = "$extractPath\cmd\git.exe"
Write-Host "Git binary location:" $gitExe
& $gitExe --version
