@echo off
chcp 65001 > nul
set PATH=C:\Users\alumnosnunoa\AppData\Local\Programs\Git\cmd;%PATH%
cls
echo =====================================================================
echo          SUBIDA DEL PROYECTO SIGMA-CAST A GITHUB
echo =====================================================================
echo.
echo Repositorio destino: https://github.com/stivenpc/Backend.git
echo Rama: main
echo.
echo Seleccione el método de autenticación:
echo.
echo [1] Iniciar sesión con Navegador Web (Git Credential Manager)
echo [2] Pegar un Personal Access Token (PAT) de GitHub
echo.
set /p opcion="Ingrese opción (1 o 2): "

if "%opcion%"=="1" (
    echo.
    echo Conectando con GitHub... Se abrirá su navegador para autorizar el acceso.
    git push -u origin main
    goto fin
)

if "%opcion%"=="2" (
    echo.
    echo Si no tiene un token, créelo en: https://github.com/settings/tokens
    echo (Permisos requeridos: marcar la casilla 'repo')
    echo.
    set /p token="Pegue su token de GitHub (ghp_...): "
    if not defined token (
        echo Error: No ingresó ningún token.
        pause
        exit /b 1
    )
    echo.
    echo Subiendo repositorio con su token...
    git push https://!token!@github.com/stivenpc/Backend.git main
    goto fin
)

echo Opción no válida.
:fin
echo.
echo =====================================================================
pause
