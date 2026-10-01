$raiz = $PSScriptRoot
$pacotes = Join-Path $raiz '.venv\Lib\site-packages'
$registro = 'HKCU:\Software\Python\PythonCore\3.12\InstallPath'

if (-not (Test-Path -LiteralPath $pacotes)) {
    throw 'Dependencias ausentes. Instale com .\.venv\Scripts\python.exe -m pip install -r tutor_calculo\requirements.txt'
}

$python = (Get-ItemProperty -LiteralPath $registro -ErrorAction Stop).ExecutablePath
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Python 3.12 com Tkinter nao encontrado.'
}

$pacotesAnteriores = $env:PYTHONPATH
Push-Location $raiz
try {
    $env:PYTHONPATH = if ($pacotesAnteriores) { "$pacotes;$pacotesAnteriores" } else { $pacotes }
    & $python -m tutor_calculo.desktop
} finally {
    $env:PYTHONPATH = $pacotesAnteriores
    Pop-Location
}
