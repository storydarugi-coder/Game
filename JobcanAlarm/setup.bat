@echo off
chcp 65001 >nul
echo ========================================
echo   JobcanAlarm 환경 설정
echo ========================================
echo.

echo [1/3] Python 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않습니다!
    echo https://www.python.org/downloads/ 에서 설치하세요.
    pause
    exit /b 1
)
python --version
echo.

echo [2/3] 패키지 설치 중...
pip install -r requirements.txt
if errorlevel 1 (
    echo 오류: 패키지 설치 실패
    pause
    exit /b 1
)
echo 패키지 설치 완료!
echo.

echo [3/3] exe 빌드 중...
pyinstaller build.spec --noconfirm
if errorlevel 1 (
    echo 오류: 빌드 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo  빌드 완료!
echo  실행 파일: dist\JobcanAlarm.exe
echo ========================================
echo.
echo 바로 실행하시겠습니까?
pause
start "" "dist\JobcanAlarm.exe"
