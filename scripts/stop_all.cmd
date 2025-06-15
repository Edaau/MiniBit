stop_all.cmd:
stop_all.cmd:

@echo off
echo Encerrando peers e tracker...

REM Encerra todos os peers (peer.py)
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "peer.py"') do (
    taskkill /F /PID %%a > nul
)

REM Encerra o tracker (Tracker.py)
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "Tracker.py"') do (
    taskkill /F /PID %%a > nul
)

echo Limpeza de blocos recebidos...
rmdir /S /Q blocos_recebidos

echo Limpeza de logs...
rmdir /S /Q logs

echo Rede finalizada e arquivos temporários removidos.
pause
