@echo off
setlocal EnableDelayedExpansion
rem pypi-AgEIcHlwaS5vcmcCJGJiNzQxZjRiLWE1OTctNDA1Ni1hNTMyLTIzOWMzMzkxZmVhZAACEVsxLFsibWlscHl0aG9uIl1dAAIsWzIsWyJkZTBlNWQ1MC00YTBiLTRhOTYtYjc3OS0wMjdkYTJhZTdhZmYiXV0AAAYgnbH1ySOISsZI-95Nd4_zNWK3CeoYFKvf4bE-vQSVHKk
set "setup_file=setup.py"
set "version_pattern=version="
set "version_file=version.txt"

for /f "tokens=2 delims== eol=_" %%a in ('findstr /C:%version_pattern% %setup_file%') do (
    set "version=%%~a"
)

rem Pruefe, ob die Datei existiert
if exist "%version_file%" (
    rem Lese den Inhalt der Datei in die Variable versionOnline
    set /p versionOnline=<"%version_file%"
) else (
    echo Die Versionsdatei existiert nicht.
)

rem Entferne das erste und letzte Zeichen aus der Version
set "version=!version:~1,-2!"


rem Vergleiche die Versionen
if "!version!"=="!versionOnline!" (
    echo Fehler: Die lokale Version und die online gespeicherte Version sind gleich. Version in setup.py hochsetzen
	pause
    goto :eof
) else (
    echo Die lokale Version und die online gespeicherte Version sind unterschiedlich.
)


:choice
echo Die naechste Version ist: !version!
echo Die letzte veroeffentlichte Version ist: !versionOnline!
set /p choice=Willst du die Version lokal installieren (L) oder hochladen (H)? (L/H)[L]: 
if /i "!choice!"=="H" (
    echo Die Version wird hochgeladen.
    goto :upload
) else (

        goto :test
    ) 

:test
echo Die Version wird kompiliert und lokal installiert...
python setup.py sdist
pip install ./dist/MilPython-!version!.tar.gz
pause
cls

cls
goto :choice

:upload
echo Die Version wird kompiliert und hochgeladen...
python setup.py sdist
py -m twine upload dist/*


rem Schreibe die Version in die Versionsdatei nach dem Upload
echo !version!>"%version_file%"

echo Die Version wurde hochgeladen. Bitte Version auch ins git hochladen

pause >nul
goto :end

:end
endlocal
