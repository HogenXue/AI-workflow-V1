# Shared user-level JSON MCP driver. PowerShell 7+.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/install-lib.ps1"

$argv = @($args)
if ($argv.Count -eq 0) { exit 2 }
$hostName = [string]$argv[0]
$installHome = if ($env:HOME) { $env:HOME } else { $HOME }
switch ($hostName) {
    'minimax' {
        $hostHome = if ($env:MINIMAX_DATA_DIR) { $env:MINIMAX_DATA_DIR }
                    elseif ($env:MAVIS_DATA_DIR) { $env:MAVIS_DATA_DIR }
                    else { Join-Path $installHome '.minimax' }
    }
    'workbuddy' {
        $hostHome = if ($env:CODEBUDDY_CONFIG_DIR) { $env:CODEBUDDY_CONFIG_DIR }
                    else { Join-Path $installHome '.codebuddy' }
    }
    default { [Console]::Error.WriteLine("ERROR: unsupported JSON MCP host: $hostName"); exit 2 }
}
function Show-Usage {
    [Console]::Error.WriteLine("Usage: install-$hostName-merge.ps1 [--dry-run|--apply] [--$hostName-home PATH] [--mcp-file PATH] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--backup-dir PATH] [--interactive]")
}
function Fail-Usage([string]$Message) {
    [Console]::Error.WriteLine("ERROR: $Message")
    Show-Usage
    exit 2
}
$mcpFile = ''
$backupDir = ''
$dryRun = $false
$modeSelected = ''
$policy = 'ask'
$mem0Url = ''
$interactive = $false
for ($i = 1; $i -lt $argv.Count; $i++) {
    $option = [string]$argv[$i]
    switch -Exact ($option) {
        { $_ -in @('--dry-run', '--apply') } {
            if ($modeSelected -and $modeSelected -ne $option) { Fail-Usage '--dry-run and --apply cannot be used together' }
            $modeSelected = $option
            $dryRun = $option -eq '--dry-run'
        }
        '--mcp-keep' { $policy = 'keep' }
        '--mcp-overwrite' { $policy = 'overwrite' }
        '--interactive' { $interactive = $true }
        { $_ -in @('--replace', '--skip-project') } { }
        { $_ -in @('--minimax-home', '--workbuddy-home', '--mcp-file', '--backup-dir', '--mem0-url', '--project-root') } {
            if ($i + 1 -ge $argv.Count -or [string]::IsNullOrEmpty([string]$argv[$i + 1]) -or ([string]$argv[$i + 1]).StartsWith('--')) {
                Fail-Usage "$option requires a value"
            }
            $i++
            $value = [string]$argv[$i]
            switch -Exact ($option) {
                "--$hostName-home" { $hostHome = $value }
                '--mcp-file' { $mcpFile = $value }
                '--backup-dir' { $backupDir = $value }
                '--mem0-url' { $mem0Url = $value }
                '--project-root' { [Console]::Out.WriteLine("SKIP: $hostName merge has no project-scoped steps") }
                default { Fail-Usage "unrecognized option: $option" }
            }
        }
        { $_ -in @('--help', '-h') } { Show-Usage; exit 0 }
        default { Fail-Usage "unrecognized option: $option" }
    }
}
if (-not $mcpFile) {
    if ($hostName -eq 'minimax') {
        $mcpFile = Join-Path $hostHome 'mcp.json'
        $nested = Join-Path $hostHome 'mcp/mcp.json'
        if (-not (Test-InstallLibExistsOrLink -Path $mcpFile) -and (Test-InstallLibExistsOrLink -Path $nested)) { $mcpFile = $nested }
    } else {
        $mcpFile = Join-Path $hostHome '.mcp.json'
        $oldFile = Join-Path $hostHome 'mcp.json'
        $legacyFile = Join-Path $installHome '.codebuddy.json'
        if (-not (Test-InstallLibExistsOrLink -Path $mcpFile)) {
            if (Test-InstallLibExistsOrLink -Path $oldFile) { $mcpFile = $oldFile }
            elseif ([IO.Path]::GetFullPath($hostHome) -eq [IO.Path]::GetFullPath((Join-Path $installHome '.codebuddy')) -and (Test-InstallLibExistsOrLink -Path $legacyFile)) { $mcpFile = $legacyFile }
        }
    }
}
$rootDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).ProviderPath
$fragmentFile = Join-Path $rootDir "trellis/$hostName/mcp/servers.json"
if (Test-InstallLibExistsOrLink -Path $mcpFile) {
    $item = Get-Item -LiteralPath $mcpFile -Force
    if ($item.PSIsContainer -or $item.LinkType) {
        [Console]::Error.WriteLine("ERROR: MCP target is not a regular file: $mcpFile")
        exit 1
    }
    if ((Resolve-Path -LiteralPath $mcpFile).ProviderPath -eq (Resolve-Path -LiteralPath $fragmentFile).ProviderPath) {
        [Console]::Error.WriteLine("ERROR: MCP target must not be the package MCP fragment: $mcpFile")
        exit 1
    }
}
if (-not $backupDir) { $backupDir = Join-Path $hostHome '.ai-workflow-backups' }
if (Test-Path -LiteralPath $mcpFile -PathType Leaf) {
    $name = [IO.Path]::GetFileName($mcpFile)
    if ($dryRun) { [Console]::Out.WriteLine("DRY-RUN: backup would use $backupDir/$name.<UTC timestamp>.bak") }
    elseif (-not (Install-LibBackupFile -Source $mcpFile -BackupDir $backupDir -Name $name)) { exit 1 }
}
$python = $null
foreach ($name in @('python', 'python3')) {
    $command = Get-Command $name -ErrorAction SilentlyContinue | Where-Object { $_.CommandType -ne 'Alias' } | Select-Object -First 1
    if ($null -ne $command) { $python = $command.Source; break }
}
if (-not $python) { [Console]::Error.WriteLine('ERROR: Python is required for MCP merge'); exit 1 }
$mergeArgs = @((Join-Path $PSScriptRoot 'lib/merge_host_mcp.py'), '--host', $hostName, '--target', $mcpFile, '--fragments', $fragmentFile, '--policy', $policy)
if ($mem0Url) { $mergeArgs += @('--mem0-url', $mem0Url) }
if ($interactive -and (Test-InstallLibStdinTty)) { $mergeArgs += '--interactive' }
if ($dryRun) { $mergeArgs += '--dry-run' }
& $python @mergeArgs
exit $LASTEXITCODE
