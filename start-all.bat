@echo off
echo 🚀 Iniciando todos os serviços do projeto Renault Transformation Day...
echo.

REM Inicia o backend Laravel em uma nova janela
echo 🔄 Iniciando Backend Laravel...
start "Backend Laravel" cmd /k "cd server && php artisan serve"
timeout /t 3 /nobreak >nul

REM Inicia o frontend React em uma nova janela
echo 🔄 Iniciando Frontend React...
start "Frontend React" cmd /k "cd client && npm start"
timeout /t 3 /nobreak >nul

REM Inicia o detector Python em uma nova janela
echo 🔄 Iniciando Detector Python...
start "Detector Python" cmd /k "cd detector/src && python webcam_detect_adaptive.py"
timeout /t 3 /nobreak >nul

echo.
echo 🎉 Todos os serviços foram iniciados!
echo.
echo 📋 Serviços rodando:
echo    • Frontend React: http://localhost:3000
echo    • Backend Laravel: http://localhost:8000
echo    • Detector Python: Janela da webcam aberta
echo.
echo 💡 Para parar os serviços, feche as janelas individuais
echo.
pause
