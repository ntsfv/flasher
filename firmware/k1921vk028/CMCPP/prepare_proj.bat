@echo off
setlocal enabledelayedexpansion

echo Place last version of source files to project directory:
call :copy_src ..\platform\Device\NIIET\K1921VK028\Source\CMCPP
call :copy_src ..\platform\Device\NIIET\K1921VK028\Source
call :copy_src ..\platform\Device\NIIET\K1921VK028\Include
call :copy_src ..\app
echo Done

pause
exit /b %ERRORLEVEL%

:copy_src
for %%a in ("%~dp0\..") do set "dirname=%%~nxa"
if not exist ".\%dirname%\%2" mkdir .\%dirname%\%2
for %%p in (%1\*.c, %1\*.mca, %1\*.h) do (
    set filename=
    call :get_filename %%p , filename
    call :file_conv %%p , .\%dirname%\%2\!filename!
)
exit /b

:file_conv
del /Q %~2 >nul 2>nul
echo %~2
..\libiconv\iconv.exe -f UTF-8 -t CP1251 %~1 >> %~2 2>nul
exit /b

:get_filename
set %2=%~nx1
exit /b
