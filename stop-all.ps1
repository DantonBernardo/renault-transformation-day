# Script para parar todos os serviços do projeto
Write-Host "🛑 Parando todos os serviços..." -ForegroundColor Red

# Para processos do Node.js (React)
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "🔄 Parando processos Node.js..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
    Write-Host "✅ Processos Node.js finalizados" -ForegroundColor Green
}

# Para processos do PHP (Laravel)
$phpProcesses = Get-Process -Name "php" -ErrorAction SilentlyContinue
if ($phpProcesses) {
    Write-Host "🔄 Parando processos PHP..." -ForegroundColor Yellow
    $phpProcesses | Stop-Process -Force
    Write-Host "✅ Processos PHP finalizados" -ForegroundColor Green
}

# Para processos do Python (Detector)
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "🔄 Parando processos Python..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "✅ Processos Python finalizados" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Todos os serviços foram parados!" -ForegroundColor Green
Write-Host ""
pause
