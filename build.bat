@echo off
cd /d %~dp0
python -m PyInstaller --noconfirm --clean --onedir --console --name PABLOS --collect-all curl_cffi --collect-all PIL panel.py
if errorlevel 1 goto fail
if exist dist\PABLOS\data rmdir /S /Q dist\PABLOS\data
xcopy /E /I /Y data dist\PABLOS\data >nul
for %%d in (state sessions lease browser runs logs) do if exist dist\PABLOS\data\%%d rmdir /S /Q dist\PABLOS\data\%%d
for %%f in (list.txt done.txt trash.txt STOP) do if exist dist\PABLOS\data\%%f del /Q dist\PABLOS\data\%%f
echo BUILD OK
exit /b 0
:fail
echo BUILD FAILED
exit /b 1
