# Tool dependency component. Business logic is shared with the Bash wrapper.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/install-lib.ps1"

$python = ''
foreach ($candidate in @('python', 'python3')) {
    $command = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($command) {
        & $command.Source -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $python = $command.Source; break }
    }
}
if (-not $python) {
    [Console]::Error.WriteLine('ERROR: Python 3.10+ is required; install Python before deps --apply.')
    exit 1
}
$PSNativeCommandUseErrorActionPreference = $false
& $python (Join-Path $PSScriptRoot 'lib/install_dependencies.py') @args
exit $LASTEXITCODE
