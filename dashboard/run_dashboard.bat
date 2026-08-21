@echo off
REM Launch the Tourism Load-Balancer dashboard.
REM Run this from your own terminal (or double-click it) so the server stays
REM alive for as long as you want it — processes started by the agent get
REM reaped when its turn ends.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [!] No virtualenv found at .venv
    echo     Create it with:  python -m venv .venv
    echo     Then install:    .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting Streamlit on http://localhost:8501
echo Press Ctrl+C to stop.
echo.

".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501

pause
