[CmdletBinding()]
param(
    [string]$PythonExe,
    [string]$PerfilAWS,
    [ValidateRange(1024, 65535)][int]$Puerto = 8501,
    [switch]$SoloPreparar
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$projectPath = $PSScriptRoot
$venvPython = Join-Path $projectPath '.venv\Scripts\python.exe'
$requirementsPath = Join-Path $projectPath 'requirements.txt'

if (-not (Test-Path -LiteralPath $venvPython)) {
    if ($PythonExe) {
        if (-not (Test-Path -LiteralPath $PythonExe)) {
            throw "No existe el ejecutable Python indicado: $PythonExe"
        }
    }
    else {
        $pyCommand = Get-Command py -ErrorAction SilentlyContinue
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
        $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
        if ($pyCommand) {
            $PythonExe = (& $pyCommand.Source -3 -c 'import sys; print(sys.executable)')
            if ($LASTEXITCODE -ne 0) { throw 'No se pudo localizar Python 3 con py.' }
        }
        elseif ($pythonCommand) { $PythonExe = $pythonCommand.Source }
        elseif (Test-Path -LiteralPath $bundledPython) { $PythonExe = $bundledPython }
        else { throw 'Instala Python 3.11 o posterior, o indica -PythonExe con su ruta.' }
    }
    & $PythonExe -c 'import sys; assert sys.version_info >= (3, 11), "Se requiere Python 3.11 o posterior"'
    if ($LASTEXITCODE -ne 0) { throw 'La version de Python no es compatible.' }
    Write-Host 'Creando entorno virtual local .venv...'
    & $PythonExe -m venv (Join-Path $projectPath '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno virtual.' }
}

# El marcador evita reinstalar en cada arranque y se invalida al cambiar requirements.
$markerPath = Join-Path $projectPath '.venv\aetheris-requirements.sha256'
$requirementsHash = (Get-FileHash -LiteralPath $requirementsPath -Algorithm SHA256).Hash
$previousHash = if (Test-Path -LiteralPath $markerPath) { (Get-Content -LiteralPath $markerPath -Raw).Trim() } else { '' }
if ($requirementsHash -ne $previousHash) {
    Write-Host 'Instalando dependencias de Aetheris AI...'
    & $venvPython -m pip install -r $requirementsPath
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias. Revisa la conexion a internet.' }
    Set-Content -LiteralPath $markerPath -Value $requirementsHash -Encoding utf8
}

if ($SoloPreparar) {
    Write-Host 'Entorno preparado. Ejecuta .\iniciar.ps1 para abrir la demo.'
    exit 0
}

$oldProfile = [Environment]::GetEnvironmentVariable('AWS_PROFILE', 'Process')
try {
    if ($PerfilAWS) { $env:AWS_PROFILE = $PerfilAWS }
    Write-Host "Aetheris AI: http://localhost:$Puerto  |  Ctrl+C para detener"
    & $venvPython -m streamlit run (Join-Path $projectPath 'app.py') --server.address 127.0.0.1 --server.port $Puerto --browser.gatherUsageStats false
    if ($LASTEXITCODE -ne 0) { throw 'Streamlit termino con un error.' }
}
finally {
    [Environment]::SetEnvironmentVariable('AWS_PROFILE', $oldProfile, 'Process')
}
