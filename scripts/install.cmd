@echo off
setlocal EnableExtensions

rem Thin launcher: locate pwsh.exe, then run install.ps1 with forwarded args.
rem No installer business logic here.

set "PWSH_EXE="

where pwsh >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%I in ('where pwsh 2^>nul') do (
    set "PWSH_EXE=%%I"
    goto :found_pwsh
  )
)

if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" (
  set "PWSH_EXE=%ProgramFiles%\PowerShell\7\pwsh.exe"
  goto :found_pwsh
)
if exist "%ProgramFiles%\PowerShell\7-preview\pwsh.exe" (
  set "PWSH_EXE=%ProgramFiles%\PowerShell\7-preview\pwsh.exe"
  goto :found_pwsh
)
if exist "%LocalAppData%\Microsoft\PowerShell\7\pwsh.exe" (
  set "PWSH_EXE=%LocalAppData%\Microsoft\PowerShell\7\pwsh.exe"
  goto :found_pwsh
)
if exist "%ProgramFiles(x86)%\PowerShell\7\pwsh.exe" (
  set "PWSH_EXE=%ProgramFiles(x86)%\PowerShell\7\pwsh.exe"
  goto :found_pwsh
)

>&2 echo ERROR: PowerShell 7+ (pwsh) was not found.
>&2 echo Install from https://aka.ms/powershell or ensure pwsh.exe is on PATH.
exit /b 1

:found_pwsh
"%PWSH_EXE%" -NoProfile -File "%~dp0install.ps1" %*
exit /b %ERRORLEVEL%
