@echo off
REM Quick publish script for purreal to PyPI
REM Usage: publish.bat

echo ================================
echo   Purreal PyPI Publisher
echo ================================
echo.

REM Check if build and twine are installed
python -m build --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 'build' not installed
    echo Install with: pip install --upgrade build twine
    exit /b 1
)

python -m twine --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] 'twine' not installed
    echo Install with: pip install --upgrade build twine
    exit /b 1
)

REM Get version from pyproject.toml
for /f "tokens=2 delims==" %%a in ('findstr /C:"version = " pyproject.toml') do (
    set VERSION=%%a
)
set VERSION=%VERSION:"=%
set VERSION=%VERSION: =%

echo Current version: %VERSION%
echo.

REM Confirm publish
set /p CONFIRM="Publish version %VERSION% to PyPI? (y/n): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    exit /b 0
)

echo.
echo [1/5] Running tests...
pytest tests/ -q
if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed! Fix tests before publishing.
    exit /b 1
)

echo.
echo [2/5] Cleaning build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist purreal.egg-info rmdir /s /q purreal.egg-info

echo.
echo [3/5] Building package...
python -m build
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    exit /b 1
)

echo.
echo [4/5] Uploading to PyPI...
python -m twine upload dist/*
if errorlevel 1 (
    echo.
    echo [ERROR] Upload failed!
    echo.
    echo Common issues:
    echo - Invalid credentials (use __token__ as username)
    echo - Version already exists (increment version in pyproject.toml)
    exit /b 1
)

echo.
echo [5/5] Verifying installation...
pip install --upgrade purreal
python -c "from purreal import SurrealDBConnectionPool; print('✓ Package installed successfully')"

echo.
echo ================================
echo   SUCCESS!
echo ================================
echo.
echo Published: purreal %VERSION%
echo PyPI: https://pypi.org/project/purreal/
echo.
echo Next steps:
echo   1. git tag -a v%VERSION% -m "Release v%VERSION%"
echo   2. git push origin v%VERSION%
echo   3. Create GitHub release
echo.
