# PowerShell port of install-config.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-config.ps1 [--dry-run] [--link | --copy] [--replace] [--target PATH] [--backup-dir PATH]'
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

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath
$sourceDir = Join-Path $rootDir 'config'
$installHome = Get-InstallHome
$target = Join-Path $installHome (Join-Path '.agents' 'config')
$backupDir = ''
$mode = 'copy'
$modeSelected = ''
$explicitDryRun = $false
$executeRequested = $false
$replace = $false

$argv = @($args)
$i = 0
while ($i -lt $argv.Count) {
    $arg = $argv[$i]
    switch -Exact ($arg) {
        '--dry-run' {
            $explicitDryRun = $true
        }
        '--link' {
            if ($modeSelected -and $modeSelected -ne 'link') {
                Fail-Usage '--link and --copy cannot be used together'
            }
            $mode = 'link'
            $modeSelected = 'link'
            $executeRequested = $true
        }
        '--copy' {
            if ($modeSelected -and $modeSelected -ne 'copy') {
                Fail-Usage '--link and --copy cannot be used together'
            }
            $mode = 'copy'
            $modeSelected = 'copy'
            $executeRequested = $true
        }
        '--replace' {
            $replace = $true
        }
        { $_ -in '--target', '--backup-dir' } {
            $option = $arg
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage "$option requires a path"
            }
            $value = $argv[$i + 1]
            if ([string]::IsNullOrEmpty($value) -or $value.StartsWith('--')) {
                Fail-Usage "$option requires a path"
            }
            if ($option -eq '--target') {
                $target = $value
            } else {
                $backupDir = $value
            }
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

if (Install-LibPathsOverlap -Source $sourceDir -Target $target) {
    [Console]::Error.WriteLine("ERROR: config target overlaps package source: $target")
    exit 1
}

if ($explicitDryRun) {
    $dryRun = $true
} elseif ($executeRequested) {
    $dryRun = $false
} else {
    $dryRun = $true
}

if ([string]::IsNullOrEmpty($backupDir)) {
    $backupDir = Join-Path ([System.IO.Path]::GetDirectoryName($target.TrimEnd('\', '/'))) '.ai-workflow-backups'
}

if (-not (Test-Path -LiteralPath $sourceDir -PathType Container)) {
    [Console]::Error.WriteLine("ERROR: config directory not found: $sourceDir")
    exit 1
}

$conflict = Test-InstallLibExistsOrLink -Path $target

if ($dryRun) {
    if ($conflict) {
        $baseName = [System.IO.Path]::GetFileName($target.TrimEnd('\', '/'))
        [Console]::Error.WriteLine("CONFLICT: existing config: $target")
        [Console]::Error.WriteLine('Use --replace to back up and replace it.')
        [Console]::Out.WriteLine("DRY-RUN: backup would use $backupDir/$baseName.<UTC timestamp>.bak")
    }
    [Console]::Out.WriteLine("DRY-RUN: $mode config -> $target")
    exit 0
}

if ($conflict -and -not $replace) {
    [Console]::Error.WriteLine("CONFLICT: existing config: $target")
    [Console]::Error.WriteLine('Use --replace to back up and replace it.')
    exit 1
}

$backupPath = ''
if ($conflict) {
    $baseName = [System.IO.Path]::GetFileName($target.TrimEnd('\', '/'))
    if (-not (Install-LibBackupFile -Source $target -BackupDir $backupDir -Name $baseName)) {
        exit 1
    }
    $backupPath = $script:InstallBackupPath
    try {
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
    } catch {
        if (-not [string]::IsNullOrEmpty($backupPath)) {
            $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
        }
        [Console]::Error.WriteLine('ERROR: could not replace existing config')
        exit 1
    }
}

$parentDir = [System.IO.Path]::GetDirectoryName($target.TrimEnd('\', '/'))
try {
    New-Item -ItemType Directory -Path $parentDir -Force -ErrorAction Stop | Out-Null
} catch {
    if (-not [string]::IsNullOrEmpty($backupPath)) {
        $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
    }
    [Console]::Error.WriteLine('ERROR: could not create config parent directory')
    exit 1
}

function Copy-ConfigTree {
    New-Item -ItemType Directory -Path $target -Force -ErrorAction Stop | Out-Null
    Get-ChildItem -LiteralPath $sourceDir | ForEach-Object {
        $name = $_.Name
        if ($name -eq '__pycache__' -or $name -like '*.pyc' -or $name -like '*.pyo') {
            return
        }
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $target $name) -Recurse -Force -ErrorAction Stop
    }
}

if ($mode -eq 'link') {
    try {
        New-Item -ItemType SymbolicLink -Path $target -Target $sourceDir -ErrorAction Stop | Out-Null
    } catch {
        if (-not [string]::IsNullOrEmpty($backupPath)) {
            $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
        }
        [Console]::Error.WriteLine('ERROR: could not link config')
        exit 1
    }
} else {
    try {
        Copy-ConfigTree
    } catch {
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
        if (-not [string]::IsNullOrEmpty($backupPath)) {
            $null = Install-LibRestoreBackup -Backup $backupPath -Destination $target
        }
        [Console]::Error.WriteLine('ERROR: could not copy config')
        exit 1
    }
}

[Console]::Out.WriteLine("INSTALLED: config -> $target")
