# Script para iniciar todos os servicos do projeto Renault Transformation Day
# Frontend React, Backend Laravel e Detector Python

Write-Host "Iniciando todos os servicos do projeto..." -ForegroundColor Green
Write-Host ""

# Funcao para verificar se um comando existe
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Verifica dependencias
Write-Host "Verificando dependencias..." -ForegroundColor Yellow

if (-not (Test-Command "node")) {
    Write-Host "Node.js nao encontrado. Instale o Node.js primeiro." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "php")) {
    Write-Host "PHP nao encontrado. Instale o PHP primeiro." -ForegroundColor Red
    exit 1
}

if (-not (Test-Command "python")) {
    Write-Host "Python nao encontrado. Instale o Python primeiro." -ForegroundColor Red
    exit 1
}

Write-Host "Todas as dependencias encontradas!" -ForegroundColor Green
Write-Host ""

# Inicia o backend Laravel
Write-Host "Iniciando Backend Laravel..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd server; Write-Host 'Backend Laravel (Porta 8000)' -ForegroundColor Green; php artisan serve"
Start-Sleep -Seconds 3

# Inicia o frontend React
Write-Host "Iniciando Frontend React..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd client; Write-Host 'Frontend React (Porta 3000)' -ForegroundColor Green; npm start"
Start-Sleep -Seconds 3

# Inicia o detector Python
Write-Host "Iniciando Detector Python..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd detector/src; Write-Host 'Detector Python' -ForegroundColor Green; python webcam_detect_adaptive.py"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Todos os servicos foram iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "Servicos rodando:" -ForegroundColor Yellow
Write-Host "   - Frontend React: http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend Laravel: http://localhost:8000" -ForegroundColor White
Write-Host "   - Detector Python: Janela da webcam aberta" -ForegroundColor White
Write-Host ""
Write-Host "Para parar os servicos, feche as janelas individuais" -ForegroundColor Cyan
Write-Host ""

# Mantem o script principal rodando para mostrar status
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")