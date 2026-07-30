# PowerShell port of install-graphify.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-graphify.ps1 [--dry-run|--apply] [--replace] [--backup-dir PATH]'
    )
}

function Fail-Usage {
    param([Parameter(Mandatory)][string]$Message)
    [Console]::Error.WriteLine("ERROR: $Message")
    Show-Usage
    exit 2
}

function Get-InstallHome {
    if (-not [string]::IsNullOrEmpty($env:HOME)) {
        return $env:HOME
    }
    return $HOME
}

$installHome = Get-InstallHome
$target = Join-Path $installHome (Join-Path '.agents' (Join-Path 'skills' 'graphify'))
$backupDir = Join-Path $installHome (Join-Path '.agents' '.ai-workflow-backups')
$mode = 'dry-run'
$replace = $false

$argv = @($args)
$i = 0
while ($i -lt $argv.Count) {
    $arg = $argv[$i]
    switch -Exact ($arg) {
        '--dry-run' { $mode = 'dry-run' }
        '--apply' { $mode = 'apply' }
        '--replace' { $replace = $true }
        '--backup-dir' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--backup-dir requires a path'
            }
            $backupDir = $argv[$i + 1]
            $i++
        }
        { $_ -in '--help', '-h' } {
            Show-Usage
            exit 0
        }
        default {
            Fail-Usage "unrecognized option: $arg"
        }
    }
    $i++
}

if ($mode -eq 'dry-run') {
    [Console]::Out.WriteLine(
        "DRY-RUN: Graphify global Skill -> $target (graphify install --platform agents)"
    )
    if (Test-InstallLibExistsOrLink -Path $target) {
        [Console]::Error.WriteLine("CONFLICT: existing Graphify Skill at $target")
        [Console]::Error.WriteLine('Use --replace to back up and replace it.')
    }
    exit 0
}

$graphifyCmd = Get-Command -Name graphify -ErrorAction SilentlyContinue
if (-not $graphifyCmd) {
    [Console]::Error.WriteLine(
        'ERROR: Graphify CLI is unavailable; install graphifyy before running this component.'
    )
    exit 1
}

$backupPath = ''
if (Test-InstallLibExistsOrLink -Path $target) {
    if (-not $replace) {
        [Console]::Error.WriteLine("CONFLICT: existing Graphify Skill at $target")
        [Console]::Error.WriteLine('Use --replace to back up and replace it.')
        exit 1
    }
    if (-not (Install-LibBackupFile -Source $target -BackupDir $backupDir -Name 'graphify')) {
        exit 1
    }
    $backupPath = $script:InstallBackupPath
    try {
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
    } catch {
        if (-not [string]::IsNullOrEmpty($backupPath)) {
            $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
        }
        exit 1
    }
}

try {
    & graphify install --platform agents
    if ($LASTEXITCODE -ne 0) {
        throw "graphify exited with $LASTEXITCODE"
    }
} catch {
    [Console]::Error.WriteLine('ERROR: Graphify global Skill installation failed.')
    if (-not [string]::IsNullOrEmpty($backupPath)) {
        $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
    }
    exit 1
}

$skillMd = Join-Path $target 'SKILL.md'
if (-not (Test-Path -LiteralPath $skillMd -PathType Leaf)) {
    [Console]::Error.WriteLine("ERROR: Graphify CLI completed without creating $skillMd")
    if (-not [string]::IsNullOrEmpty($backupPath)) {
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
        $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
    }
    exit 1
}

[Console]::Out.WriteLine("INSTALLED: Graphify global Skill -> $target")
