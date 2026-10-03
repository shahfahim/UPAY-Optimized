$targetTime = Get-Date "06:00 AM"

Write-Host "======================================================"
Write-Host " AI Engineer Watchdog Started"
Write-Host " Target Stop Time: $targetTime"
Write-Host " The system will auto-restart if interrupted."
Write-Host "======================================================"

while ((Get-Date) -lt $targetTime) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting AI Training Process..."
    
    # Run the python training daemon
    backend\.venv\Scripts\python.exe ai_trainer_daemon.py
    
    $exitCode = $LASTEXITCODE
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Process stopped with code $exitCode."
    
    if ((Get-Date) -ge $targetTime) {
        Write-Host "Target time reached. Shutting down Night Shift."
        break
    }
    
    Write-Host "System interruption detected! Waking up AI Engineer in 5 seconds..."
    Start-Sleep -Seconds 5
}
