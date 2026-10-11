$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Prepare o ambiente: python -m venv .venv e .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
}
Push-Location $PSScriptRoot
try {
    & $python -m tutor_calculo.desktop @args
} finally {
    Pop-Location
}
