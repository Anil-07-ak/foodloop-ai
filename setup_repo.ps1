$gitExe = "C:\Users\Chandu M\.gemini\antigravity\scratch\mingit\cmd\git.exe"
$projectDir = "C:\Users\Chandu M\.gemini\antigravity\scratch\smart_food_waste_platform"

Set-Location $projectDir

Write-Host "1. Initializing Git Repository..."
& $gitExe init

Write-Host "2. Configuring Git User..."
& $gitExe config user.name "FoodLoop AI Platform Developer"
& $gitExe config user.email "developer@foodloop-ai.com"

Write-Host "3. Staging All Project Files..."
& $gitExe add .

Write-Host "4. Creating Initial Commit..."
& $gitExe commit -m "Initial Release of FoodLoop AI Platform with Commercial Marketplace, OpenCV Quality Check, Google Maps & Firebase Auth"

Write-Host "5. Git Branch Name:"
& $gitExe branch -M main

Write-Host "Local Git Repository successfully created!"
