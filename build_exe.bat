@echo off
rem Step 11: turn Travel Guardian into a Windows program (.exe) with PyInstaller.
rem
rem Run it from the TravelGuardian folder:   build_exe.bat
rem It takes a few minutes. The finished app is put in  dist\TravelGuardian\
rem and a zip of that folder, ready to copy to another PC, in  dist\TravelGuardian.zip
rem
rem What each option means:
rem   --name TravelGuardian   name of the program (TravelGuardian.exe)
rem   --windowed              no black console window behind the app
rem   --icon                  the shield icon for the .exe file
rem   (no --uac-admin)        the app starts with normal rights. For the full device
rem                           search the user right-clicks > Run as administrator;
rem                           otherwise the window shows a note asking them to.
rem   --add-data "ui;ui"      copy the window files (HTML, CSS, JS, icon) into the app
rem   --add-data "models;models"  copy the AI model (about 770 MB) into the app
rem   --collect-all llama_cpp     copy the AI engine's DLL files, which PyInstaller
rem                               can't find on its own
rem   --noconfirm --clean     replace the last build without asking

tg_env\Scripts\pyinstaller.exe app.py ^
    --name TravelGuardian ^
    --windowed ^
    --icon ui\icon.ico ^
    --add-data "ui;ui" ^
    --add-data "models;models" ^
    --collect-all llama_cpp ^
    --noconfirm --clean
if errorlevel 1 (
    echo Build failed. Read the last error lines above.
    exit /b 1
)

rem Remove PyInstaller's work folder. It holds a half-built TravelGuardian.exe
rem that fails with "python312.dll not found" if someone runs it by mistake.
rmdir /s /q build

rem Put the install instructions next to the program, then zip the folder.
rem tar is built into Windows 10 and 11; -a picks the zip format from the name.
copy /y INSTALL.txt dist\TravelGuardian\INSTALL.txt >nul
rem The Llama licence asks for its licence and Notice file to go with the model.
rem They are already inside _internal\models; these copies make them easy to find.
copy /y models\LICENSE.txt dist\TravelGuardian\LICENSE.txt >nul
copy /y models\NOTICE.txt dist\TravelGuardian\NOTICE.txt >nul
rem Setup.bat + install_nmap.ps1 download and start the official Nmap installer.
copy /y Setup.bat dist\TravelGuardian\Setup.bat >nul
copy /y install_nmap.ps1 dist\TravelGuardian\install_nmap.ps1 >nul
if exist dist\TravelGuardian.zip del dist\TravelGuardian.zip
tar -a -c -f dist\TravelGuardian.zip -C dist TravelGuardian
if errorlevel 1 (
    echo Zipping failed. The program itself is ready in dist\TravelGuardian\
    exit /b 1
)
echo Done: dist\TravelGuardian\TravelGuardian.exe  and  dist\TravelGuardian.zip
