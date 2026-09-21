# Script de PowerShell para autenticación y push a GitHub
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:Path = "C:\Users\alumnosnunoa\AppData\Local\Programs\Git\cmd;$env:Path"

Clear-Host
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "         SUBIDA DEL PROYECTO SIGMA-CAST A GITHUB" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Repositorio destino: https://github.com/stivenpc/Backend.git"
Write-Host "Rama: main`n"

Write-Host "Seleccione el método de autenticación:" -ForegroundColor Green
Write-Host "[1] Iniciar sesión con Navegador Web (Recomendado - Abre ventana de GitHub)"
Write-Host "[2] Ingresar un Personal Access Token (PAT)"
Write-Host "[3] Salir`n"

$opcion = Read-Host "Ingrese opción (1, 2 o 3)"

if ($opcion -eq "1") {
    Write-Host "`nConectando con GitHub... Se abrirá el navegador para autorizar la cuenta." -ForegroundColor Yellow
    git push -u origin main
} elseif ($opcion -eq "2") {
    Write-Host "`nCree su token en: https://github.com/settings/tokens (Marque la casilla 'repo')" -ForegroundColor Cyan
    $token = Read-Host "Pegue su token de GitHub (ghp_...)"
    if ([string]::IsNullOrWhiteSpace($token)) {
        Write-Host "Error: No ingresó ningún token." -ForegroundColor Red
        return
    }
    Write-Host "`nSubiendo el proyecto con token..." -ForegroundColor Yellow
    git push "https://$($token.Trim())@github.com/stivenpc/Backend.git" main
} else {
    Write-Host "`nOperación cancelada."
}

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Pause
