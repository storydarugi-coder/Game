@echo off
chcp 65001 >nul
echo ========================================
echo   JobcanAlarm 설치 프로그램 빌드
echo ========================================
echo.

echo [1/2] PyInstaller로 exe 빌드 중...
pyinstaller build.spec --noconfirm
if errorlevel 1 (
    echo 오류: PyInstaller 빌드 실패
    echo pip install pyinstaller 를 먼저 실행하세요
    pause
    exit /b 1
)
echo exe 빌드 완료!
echo.

echo [2/2] Inno Setup으로 설치 프로그램 생성 중...
where iscc >nul 2>&1
if errorlevel 1 (
    if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        "C:\Program Files\Inno Setup 6\ISCC.exe" installer.iss
    ) else (
        echo.
        echo ============================================
        echo  Inno Setup이 설치되어 있지 않습니다!
        echo  https://jrsoftware.org/isinfo.php 에서
        echo  다운로드 후 설치하세요.
        echo.
        echo  설치 후 installer.iss 파일을 더블클릭하면
        echo  Inno Setup에서 열립니다.
        echo ============================================
        pause
        exit /b 1
    )
) else (
    iscc installer.iss
)

if errorlevel 1 (
    echo 오류: 설치 프로그램 생성 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo  완료! 설치 파일 위치:
echo  installer_output\JobcanAlarm_Setup.exe
echo ========================================
pause
