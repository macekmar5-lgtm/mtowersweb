@echo off
rem Malaga Towers: photoreal stills with Nano Banana Pro (see gen_stills.py for all options).
chcp 65001 >nul
cd /d "%~dp0"
set PY=python
where py >nul 2>nul && set PY=py -3
echo Checking dependencies (google-genai, pillow)...
%PY% -m pip install -q google-genai pillow
if "%~1"=="" goto ask
%PY% gen_stills.py %*
goto end
:ask
echo.
echo   front                    3 variants of the front view at 2K (~$0.40)
echo   side back --variants 4   4 variants of each
echo   all                      every view (~$2.25)
echo   front --dry-run          show images + prompt + cost, no API call
echo   --final front_2          re-run candidate front_2 at 4K (~$0.24)
echo   --promote front_2        use the 2K candidate as media\front.jpg (free)
echo.
set /p ARGS=Arguments:
%PY% gen_stills.py %ARGS%
:end
echo.
pause
