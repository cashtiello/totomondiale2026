@echo off
chcp 65001 > nul
cls

echo ============================================================
echo    TOTOMONDIALE 2026 - AVVIO AUTOMATICO
echo ============================================================
echo.

cd /d "%~dp0"

python --version > nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato. Installa Python 3.12+ da python.org
    pause
    exit /b 1
)

echo [1/4] Verifica dipendenze Python...
pip install -r requirements.txt --quiet
echo       OK
echo.

echo [2/4] Calcolo classifica...
python src/main.py
if errorlevel 1 (
    echo [ERRORE] Problema nel calcolo. Controlla data/logs/totomondiale.log
    pause
    exit /b 1
)

echo [3/4] Preparazione file...
copy /Y data\output\index.html index.html > nul
echo       OK
echo.

echo [4/4] Pubblicazione su GitHub...
REM Aggiunge tutto: classifica + file pronostici + risultati
git add index.html > nul 2>&1
git add data/pronostici/*.xlsx > nul 2>&1
git add data/risultati_reali/risultati.xlsx > nul 2>&1
git add data/output/index.html > nul 2>&1

git diff --cached --quiet
if errorlevel 1 (
    for /f "tokens=1-3 delims=/ " %%a in ("%date%") do set DATA=%%c-%%b-%%a
    for /f "tokens=1-2 delims=: " %%a in ("%time%") do set ORA=%%a:%%b
    git commit -m "Aggiornamento %DATA% %ORA%" > nul 2>&1
    git push > nul 2>&1
    if errorlevel 1 (
        echo [AVVISO] Pubblicazione fallita. Controlla connessione internet.
    ) else (
        echo       Pubblicato su GitHub!
    )
) else (
    echo       Nessuna modifica da pubblicare.
)
echo.

echo ============================================================
echo  FATTO!
echo  Sito: https://cashtiello.github.io/totomondiale2026/
echo ============================================================
echo.

start "" "data\output\index.html"
echo Premi un tasto per chiudere...
pause > nul
exit /b 0
