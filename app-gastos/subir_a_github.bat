@echo off
title Subir Proyecto a GitHub
cd /d "%~dp0"

echo ===================================================
echo     SUBIR MI ALCANCIA Y GASTOS A GITHUB
echo ===================================================
echo.

:: Verificar si git esta instalado
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git no parece estar instalado o no esta en el PATH.
    echo Por favor descarga e instala Git desde: https://git-scm.com/
    pause
    exit /b
)

:: Inicializar git si no existe
if not exist ".git" (
    echo [*] Inicializando repositorio Git...
    git init
    git branch -M main
)

:: Agregar archivos y hacer commit
echo [*] Agregando archivos del proyecto...
git add .
git commit -m "Primera version: Control de gastos con bienvenida de Adriana, codigo 5861 y vencimientos"

echo.
echo ===================================================
echo   Ahora necesitamos la URL de tu repositorio de GitHub.
echo   Por ejemplo: https://github.com/TU-USUARIO/control-gastos.git
echo ===================================================
echo.
set /p REPO_URL="Pega aqui la URL de tu repositorio de GitHub: "

if "%REPO_URL%"=="" (
    echo [!] No ingresaste ninguna URL. Podes ejecutar este archivo de nuevo cuando tengas el link.
    pause
    exit /b
)

:: Configurar remoto y subir
git remote remove origin 2>nul
git remote add origin %REPO_URL%
echo.
echo [*] Subiendo archivos a GitHub (main)...
git push -u origin main

echo.
echo ===================================================
echo   SI EL PUSH FUE EXITOSO, YA ESTA LISTO!
echo   Ahora podes ir a https://share.streamlit.io para publicarlo.
echo ===================================================
pause
