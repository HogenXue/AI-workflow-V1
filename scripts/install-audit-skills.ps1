Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$python = $null
foreach ($name in @('python', 'python3')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue | Where-Object { $_.CommandType -ne 'Alias' } | Select-Object -First 1
    if ($command) { $python = $command.Source; break }
}
if (-not $python) { [Console]::Error.WriteLine('ERROR: Python 3.10+ with PyYAML is required'); exit 2 }
& $python (Join-Path $PSScriptRoot 'lib/skill_catalog.py') audit @args
exit $LASTEXITCODE
