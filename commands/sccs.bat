@echo off
setlocal enabledelayedexpansion

set "command=%1"

if "%command%"=="init" (
    set "script_directory=%~dp0"
    python "%script_directory%init.py" %*
    exit /b !errorlevel!
)

if "%command%"=="commit" (
    set "script_directory=%~dp0"
    python "%script_directory%commit.py" %*
    exit /b !errorlevel!
)

if "%command%"=="open" (
    set "script_directory=%~dp0"
    python "%script_directory%open.py" %*
    exit /b !errorlevel!
)

if "%command%"=="log" (
    set "script_directory=%~dp0"
    python "%script_directory%log.py" %*
    exit /b !errorlevel!
)

if "%command%"=="diff" (
    set "script_directory=%~dp0"
    python "%script_directory%diff.py" %*
    exit /b !errorlevel!
)

if "%command%"=="status" (
    set "script_directory=%~dp0"
    python "%script_directory%status.py" %*
    exit /b !errorlevel!
)

if "%command%"=="help" (
    set "script_directory=%~dp0"
    python "%script_directory%help.py" %*
    exit /b !errorlevel!
)

if "%command%"=="branch" (
    set "script_directory=%~dp0"
    python "%script_directory%branch.py" %*
    exit /b !errorlevel!
)

if "%command%"=="switch" (
    set "script_directory=%~dp0"
    python "%script_directory%switch.py" %*
    exit /b !errorlevel!
)

echo Unknown command: %command%
echo Invalid command. Please use "init", "commit", "open", "log", "status", "diff", "help", "branch", or "switch", along with required arguments
echo For help, use the 'sccs help' command
exit /b 1