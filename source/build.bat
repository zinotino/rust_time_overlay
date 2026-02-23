@echo off
setlocal enabledelayedexpansion

echo.
echo  Rust Time Overlay -- Build Script
echo  ===================================
echo.

:: Use the Python that is on PATH — same one the user runs scripts with
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Install Python 3.10+ and add it to PATH.
    pause & exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON=%%i
echo  Using Python: %PYTHON%
echo.

:: Install / upgrade dependencies into the correct interpreter
echo  Checking dependencies...
"%PYTHON%" -m pip install --upgrade pyinstaller rustplus --quiet
if errorlevel 1 (
    echo  ERROR: Failed to install dependencies.
    pause & exit /b 1
)

:: Clean previous build artifacts
echo  Cleaning previous build...
if exist dist   rmdir /s /q dist
if exist build  rmdir /s /q build

:: Build
echo  Building exe...
echo.
"%PYTHON%" -m PyInstaller "Rust Time Overlay.spec" --noconfirm

if errorlevel 1 (
    echo.
    echo  BUILD FAILED. Check output above for errors.
    pause & exit /b 1
)

:: Copy config if it exists so the exe folder is ready to run immediately
if exist rust_overlay_config.json (
    copy /y rust_overlay_config.json "dist\rust_overlay_config.json" >nul
    echo  Copied existing config to dist\
)

echo.
echo  ===================================
echo  Build complete!
echo  Output: dist\Rust Time Overlay.exe
echo.
echo  To distribute: zip the contents of the dist\ folder.
echo  The exe will reconnect to the last server automatically
echo  as long as rust_overlay_config.json is in the same folder.
echo  ===================================
echo.
pause
