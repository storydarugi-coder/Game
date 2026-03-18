@echo off
chcp 65001 >nul 2>&1

echo ========================================
echo   JobcanAlarm Setup
echo ========================================
echo.

echo [1/3] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo [2/3] Installing packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Package install failed
    pause
    exit /b 1
)
echo Done!
echo.

echo [3/3] Building exe...
pyinstaller build.spec --noconfirm
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build complete!
echo   Run: dist\JobcanAlarm.exe
echo ========================================
echo.
pause
start "" "dist\JobcanAlarm.exe"
