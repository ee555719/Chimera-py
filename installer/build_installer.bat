@echo off
echo Building Chimera Installer...

REM Install PyInstaller
pip install pyinstaller -q

REM Build installer
pyinstaller ^
    --onefile ^
    --name "ChimeraInstaller" ^
    --windowed ^
    --icon "NONE" ^
    --add-data "..\chimera;chimera" ^
    --hidden-import "chimera" ^
    --hidden-import "chimera.app" ^
    --hidden-import "chimera.host" ^
    --hidden-import "chimera.loader" ^
    --hidden-import "chimera.sdk" ^
    --hidden-import "chimera.interpreter" ^
    --hidden-import "chimera.packager" ^
    --hidden-import "PySide6" ^
    --hidden-import "PySide6.QtWidgets" ^
    --hidden-import "PySide6.QtCore" ^
    --hidden-import "PySide6.QtGui" ^
    installer.py

echo.
if exist "dist\ChimeraInstaller.exe" (
    echo Build successful: dist\ChimeraInstaller.exe
) else (
    echo Build failed!
)
pause
