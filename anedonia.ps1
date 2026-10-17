#
# feito por YWZsaXRv
#

param([switch]$Install, [switch]$Uninstall)

$caminho_projeto = Split-Path -Parent $PSCommandPath
$caminho_venv = Join-Path $caminho_projeto ".venv"
$caminho_python = Join-Path $caminho_venv "Scripts\python.exe"
$caminho_pip = Join-Path $caminho_venv "Scripts\pip.exe"
$caminho_requisitos = Join-Path $caminho_projeto "requirements.txt"
$caminho_principal = Join-Path $caminho_projeto "anedonia.py"

if ($Install) {
    Write-Host "instalando anedonia..." -ForegroundColor Cyan
    if (-not (Test-Path $caminho_venv)) {
        # venv ainda nao existe, crio
        python -m venv $caminho_venv
    }
    # requisitos ja instalados sao ignorados pelo pip
    Write-Host "baixando requirements..." -ForegroundColor Gray
    & $caminho_pip install -r $caminho_requisitos > $null 2>&1
    $caminho_path = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($caminho_path -notlike "*$caminho_projeto*") {
        [Environment]::SetEnvironmentVariable("PATH", $caminho_path + ";" + $caminho_projeto, "User")
        Write-Host "pronto. feche e reabra o terminal, depois digite: anedonia" -ForegroundColor Green
    } else {
        Write-Host "ja estava no PATH." -ForegroundColor Green
    }
    exit 0
}

if ($Uninstall) {
    Write-Host "removendo anedonia..." -ForegroundColor Cyan
    $caminho_path = [Environment]::GetEnvironmentVariable("PATH", "User")
    $novos = @()
    foreach ($parte in ($caminho_path -split ";")) { if ($parte -ne $caminho_projeto) { $novos += $parte } }
    [Environment]::SetEnvironmentVariable("PATH", ($novos -join ";"), "User")
    if (Test-Path $caminho_venv) { Remove-Item $caminho_venv -Recurse -Force }
    Write-Host "removido." -ForegroundColor Green
    exit 0
}

if (-not (Test-Path $caminho_python)) {
    Write-Host "venv nao encontrado. rode: .\anedonia.ps1 -install" -ForegroundColor Red
    exit 1
}

Write-Host "iniciando anedonia..." -ForegroundColor Cyan
& $caminho_python $caminho_principal $args
