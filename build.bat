@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ============================================================
echo   계산기 프로그램 EXE 빌드 스크립트
echo   개발 환경: Windows / Python 3.12 / PyInstaller
echo ============================================================
echo.

:: ---------------------------------------------------------------
:: 0. 현재 디렉토리를 스크립트 위치로 고정
:: ---------------------------------------------------------------
cd /d "%~dp0"

:: ---------------------------------------------------------------
:: 1. Python 설치 확인
:: ---------------------------------------------------------------
echo [1/5] Python 설치 확인 중...
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo        https://www.python.org/downloads/ 에서 Python 3.12를 설치해 주세요.
    echo        설치 시 "Add Python to PATH" 옵션을 반드시 체크하세요.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo        감지된 버전: %PYTHON_VER%
echo.

:: ---------------------------------------------------------------
:: 2. 가상환경 생성 및 활성화
:: ---------------------------------------------------------------
echo [2/5] 가상환경 준비 중...
if not exist "venv\" (
    echo        가상환경(venv)이 없습니다. 새로 생성합니다...
    python -m venv venv
    if errorlevel 1 (
        echo [오류] 가상환경 생성에 실패했습니다.
        pause
        exit /b 1
    )
    echo        가상환경 생성 완료.
) else (
    echo        기존 가상환경(venv)을 사용합니다.
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [오류] 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)
echo        가상환경 활성화 완료.
echo.

:: ---------------------------------------------------------------
:: 3. requirements.txt 기반 패키지 설치
:: ---------------------------------------------------------------
echo [3/5] 패키지 설치 중 (requirements.txt 기준)...
if not exist "requirements.txt" (
    echo [오류] requirements.txt 파일을 찾을 수 없습니다.
    pause
    exit /b 1
)
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [오류] 패키지 설치에 실패했습니다. requirements.txt를 확인해 주세요.
    pause
    exit /b 1
)
echo        패키지 설치 완료.
echo.

:: ---------------------------------------------------------------
:: 4. 이전 빌드 결과물 정리
:: ---------------------------------------------------------------
echo [4/5] 이전 빌드 파일 정리 중...
if exist "dist\" (
    rmdir /s /q "dist"
    echo        dist\ 폴더 삭제 완료.
)
if exist "build\" (
    rmdir /s /q "build"
    echo        build\ 폴더 삭제 완료.
)
if exist "Calculator.spec" (
    del /q "Calculator.spec"
    echo        Calculator.spec 파일 삭제 완료.
)
echo.

:: ---------------------------------------------------------------
:: 5. PyInstaller로 exe 빌드
::    --onefile   : 단일 실행 파일로 패키징
::    --windowed  : 콘솔 창 숨김 (GUI 전용)
::    --name      : 출력 파일명
::    --add-data  : 추가 리소스 포함 (필요 시 주석 해제)
:: ---------------------------------------------------------------
echo [5/5] PyInstaller 빌드 시작...
echo.

pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Calculator" ^
    --add-data "calculator;calculator" ^
    main.py

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   [빌드 실패] PyInstaller 오류가 발생했습니다.
    echo   위의 오류 메시지를 확인하고 문제를 수정해 주세요.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------
:: 빌드 성공 메시지
:: ---------------------------------------------------------------
echo.
echo ============================================================
echo   [빌드 성공] 실행 파일이 생성되었습니다!
echo.
echo   출력 경로: dist\Calculator.exe
echo.
echo   배포 방법:
echo     dist\Calculator.exe 파일 하나만 복사하면 됩니다.
echo     Python 없이도 Windows에서 바로 실행 가능합니다.
echo ============================================================
echo.

:: 빌드 결과 폴더 열기 (선택)
set /p OPEN_DIST="빌드 결과 폴더(dist\)를 여시겠습니까? (Y/N): "
if /i "!OPEN_DIST!"=="Y" (
    explorer dist
)

pause
exit /b 0
