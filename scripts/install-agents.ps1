# PowerShell port of install-agents.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-agents.ps1 [--dry-run|--apply] [--agents-home PATH] [--document-name NAME] [--no-hooks-feature] [--backup-dir PATH]'
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
$sourceFile = Join-Path $rootDir 'agents/AGENTS.global.md'
$installHome = Get-InstallHome
$agentsHome = if (-not [string]::IsNullOrEmpty($env:CODEX_HOME)) {
    $env:CODEX_HOME
} else {
    Join-Path $installHome '.codex'
}
$documentName = 'AGENTS.md'
$noHooksFeature = 0
$backupDir = ''
$mode = 'dry-run'
$modeSelected = ''
$agentsBackupPath = ''

$argv = @($args)
$i = 0
while ($i -lt $argv.Count) {
    $arg = $argv[$i]
    switch -Exact ($arg) {
        '--dry-run' {
            if ($modeSelected -and $modeSelected -ne 'dry-run') {
                Fail-Usage '--dry-run and --apply cannot be used together'
            }
            $mode = 'dry-run'
            $modeSelected = 'dry-run'
        }
        '--apply' {
            if ($modeSelected -and $modeSelected -ne 'apply') {
                Fail-Usage '--dry-run and --apply cannot be used together'
            }
            $mode = 'apply'
            $modeSelected = 'apply'
        }
        { $_ -in '--agents-home', '--codex-home', '--backup-dir' } {
            $option = $arg
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage "$option requires a path"
            }
            $value = $argv[$i + 1]
            if ([string]::IsNullOrEmpty($value) -or $value.StartsWith('--')) {
                Fail-Usage "$option requires a path"
            }
            if ($option -eq '--agents-home' -or $option -eq '--codex-home') {
                $agentsHome = $value
            } else {
                $backupDir = $value
            }
            $i++
        }
        '--document-name' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--document-name requires a name'
            }
            $value = $argv[$i + 1]
            if ([string]::IsNullOrEmpty($value) -or $value.StartsWith('--')) {
                Fail-Usage '--document-name requires a name'
            }
            $documentName = $value
            $i++
        }
        '--no-hooks-feature' { $noHooksFeature = 1 }
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

if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) {
    [Console]::Error.WriteLine("ERROR: template not found: $sourceFile")
    exit 1
}

if ($documentName.Contains('/') -or $documentName.Contains('\')) {
    [Console]::Error.WriteLine("ERROR: --document-name must be a bare filename, got: $documentName")
    exit 2
}

$targetFile = Join-Path $agentsHome $documentName
if ([string]::IsNullOrEmpty($backupDir)) {
    $backupDir = Join-Path $agentsHome '.ai-workflow-backups'
}

$overrideFile = Join-Path $agentsHome 'AGENTS.override.md'
if (($noHooksFeature -eq 0) -and ($documentName -eq 'AGENTS.md') -and (Test-Path -LiteralPath $overrideFile -PathType Leaf) -and ((Get-Item -LiteralPath $overrideFile).Length -gt 0)) {
    [Console]::Out.WriteLine("NOTE: $overrideFile is the effective global instruction file; installed AGENTS.md remains shadowed")
}

if ($mode -eq 'dry-run') {
    [Console]::Out.WriteLine("DRY-RUN: would copy $sourceFile -> $targetFile")
    if (Test-InstallLibExistsOrLink -Path $targetFile) {
        [Console]::Out.WriteLine(
            "DRY-RUN: would back up $targetFile as $backupDir/$documentName.<UTC timestamp>.bak"
        )
    }
    if ($noHooksFeature -eq 0) {
        [Console]::Out.WriteLine('DRY-RUN: preserving config.toml and native hook settings')
    } else {
        [Console]::Out.WriteLine('DRY-RUN: skipping config.toml hooks feature (--no-hooks-feature)')
    }
    exit 0
}

try {
    New-Item -ItemType Directory -Path $agentsHome -Force -ErrorAction Stop | Out-Null
} catch {
    [Console]::Error.WriteLine("ERROR: could not create agents home: $agentsHome")
    exit 1
}

$agentsBackupAvailable = $false
if (Test-InstallLibExistsOrLink -Path $targetFile) {
    if (-not (Install-LibBackupFile -Source $targetFile -BackupDir $backupDir -Name $documentName)) {
        exit 1
    }
    $agentsBackupPath = $script:InstallBackupPath
    $agentsBackupAvailable = $true
    $item = Get-Item -LiteralPath $targetFile -Force -ErrorAction SilentlyContinue
    if ($null -ne $item -and $null -ne $item.LinkType) {
        try {
            Remove-Item -LiteralPath $targetFile -Force -ErrorAction Stop
        } catch {
            [Console]::Error.WriteLine("ERROR: could not replace existing $documentName")
            exit 1
        }
    }
}

try {
    Copy-Item -LiteralPath $sourceFile -Destination $targetFile -Force -ErrorAction Stop
} catch {
    if ($agentsBackupAvailable) {
        $null = Install-LibRestoreBackup -Backup $agentsBackupPath -Destination $targetFile
    } else {
        Remove-Item -LiteralPath $targetFile -Force -ErrorAction SilentlyContinue
    }
    [Console]::Error.WriteLine('ERROR: could not install agents document template')
    exit 1
}
[Console]::Out.WriteLine("INSTALLED: $targetFile")

if ($noHooksFeature -eq 0) {
    [Console]::Out.WriteLine('UNCHANGED: config.toml and native hook settings preserved; use Codex /hooks to review hook trust')
}
