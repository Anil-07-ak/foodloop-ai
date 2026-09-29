$username = "Anil-07-ak"
$token = "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"
$repoName = "foodloop-ai"
$gitExe = "C:\Users\Chandu M\.gemini\antigravity\scratch\mingit\cmd\git.exe"
$projectDir = "C:\Users\Chandu M\.gemini\antigravity\scratch\smart_food_waste_platform"

Set-Location $projectDir

Write-Host "1. Creating remote GitHub repository '$repoName'..."
$headers = @{
    "Authorization" = "token $token"
    "User-Agent"    = "FoodLoop-AI-App"
    "Accept"        = "application/vnd.github.v3+json"
}

$body = @{
    name        = $repoName
    description = "FoodLoop AI - Smart Food Waste Management Platform with Commercial Marketplace, OpenCV Quality Check & Route Optimization"
    private     = $false
} | ConvertTo-Json

try {
    $createResp = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "Repository created successfully on GitHub!"
} catch {
    Write-Host "Repository creation response notice:" $_.Exception.Message
}

Write-Host "2. Adding Remote Origin..."
$authenticatedUrl = "https://${username}:${token}@github.com/${username}/${repoName}.git"
& $gitExe remote remove origin 2>$null
& $gitExe remote add origin $authenticatedUrl

Write-Host "3. Pushing Main Branch to GitHub..."
& $gitExe branch -M main
& $gitExe push -u origin main --force

Write-Host "4. Enabling GitHub Pages..."
$pagesBody = @{
    source = @{
        branch = "main"
        path   = "/"
    }
} | ConvertTo-Json

try {
    $pagesResp = Invoke-RestMethod -Uri "https://api.github.com/repos/${username}/${repoName}/pages" -Method Post -Headers $headers -Body $pagesBody -ContentType "application/json"
    Write-Host "GitHub Pages successfully enabled!"
} catch {
    Write-Host "GitHub Pages notice:" $_.Exception.Message
}

Write-Host "============================================================"
Write-Host "DEPLOYMENT COMPLETE!"
Write-Host "GitHub Repository: https://github.com/${username}/${repoName}"
Write-Host "Live Website URL:  https://${username}.github.io/${repoName}/"
Write-Host "============================================================"
