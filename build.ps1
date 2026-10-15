# Gera dist\G29ShiftLight.exe (rodar no Windows, na raiz do projeto)
$ErrorActionPreference = "Stop"

function Run {
    # programas externos não disparam o ErrorActionPreference: confere o código de saída
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Falhou: $Exe $($Arguments -join ' ') (código $LASTEXITCODE)" }
}

if (-not (Test-Path .venv)) { Run python @("-m", "venv", ".venv") }
$py = ".venv\Scripts\python.exe"
Run $py @("-m", "pip", "install", "-r", "requirements-dev.txt")
Run $py @("tools\make_icon.py")
Run $py @("-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--noconsole",
          "--name", "G29ShiftLight", "--icon", "assets\icon.ico", "run_tray.py")

if (-not (Test-Path dist\G29ShiftLight.exe)) { throw "dist\G29ShiftLight.exe não foi gerado" }
Write-Host "Pronto: dist\G29ShiftLight.exe"
