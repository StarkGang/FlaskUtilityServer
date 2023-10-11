@echo off

:CHECK_WIFI
REM Check Wi-Fi connection
echo "CHECK WIFI"
ping -n 1 8.8.8.8 > nul
if %errorlevel% neq 0 (
    echo "Wi-Fi not connected. Waiting... for 10s"
    timeout /t 10 /nobreak > nul
    goto CHECK_WIFI
)
echo "WIFI CONNECTED!"

REM GO TO DIR
echo "GOING TO DIR"
cd C:\Users\Midhun K M\Documents\Mark\utils\LocalServer

REM Display Python version
echo "Testing Python"
pythonw --version

REM Display pip information
echo "CHECKING PIP"
pythonw -m pip

REM Start Waitress with your app
echo "STARTING SCRIPT NOW.. You can close terminal in 10S"
pythonw "main.pyw"
exit
