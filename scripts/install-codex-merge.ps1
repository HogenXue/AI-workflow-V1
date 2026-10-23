# PowerShell port of install-codex-merge.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-codex-merge.ps1 [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--codex-home PATH] [--replace] [--backup-dir PATH] [--interactive]'
    )
    [Console]::Error.WriteLine(
        '       --project-root and --skip-project are accepted for backward compatibility but ignored; Codex hooks install at user scope.'
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

function Resolve-InstallPython {
    foreach ($name in @('python', 'python3')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandType -ne 'Alias' } |
            Select-Object -First 1
        if ($null -ne $cmd -and -not [string]::IsNullOrEmpty($cmd.Source)) {
            return $cmd.Source
        }
    }
    return $null
}

function Restore-CodexUserHooks {
    param(
        [string]$HooksJsonBackup,
        [string]$HooksDirBackup,
        [string]$DestHooksJson,
        [string]$DestHooksDir
    )
    Remove-Item -LiteralPath $DestHooksJson -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $DestHooksDir -Recurse -Force -ErrorAction SilentlyContinue
    if (-not [string]::IsNullOrEmpty($HooksJsonBackup)) {
        $null = Install-LibRestoreBackup -Backup $HooksJsonBackup -Destination $DestHooksJson
    }
    if (-not [string]::IsNullOrEmpty($HooksDirBackup)) {
        $null = Install-LibRestoreBackup -Backup $HooksDirBackup -Destination $DestHooksDir
    }
}

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath

$installHome = Get-InstallHome
$codexHome = if (-not [string]::IsNullOrEmpty($env:CODEX_HOME)) {
    $env:CODEX_HOME
} else {
    Join-Path $installHome '.codex'
}
$projectRoot = ''
$skipProject = 0
$dryRun = 0
$mcpPolicy = 'ask'
$mem0Url = ''
$replace = 0
$backupDir = ''
$interactive = 0

$argv = @($args)
$i = 0
while ($i -lt $argv.Count) {
    $arg = $argv[$i]
    switch -Exact ($arg) {
        '--dry-run' { $dryRun = 1 }
        '--apply' { $dryRun = 0 }
        '--mcp-keep' { $mcpPolicy = 'keep' }
        '--mcp-overwrite' { $mcpPolicy = 'overwrite' }
        '--mem0-url' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--mem0-url requires a value'
            }
            $mem0Url = $argv[$i + 1]
            $i++
        }
        '--codex-home' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--codex-home requires a path'
            }
            $codexHome = $argv[$i + 1]
            $i++
        }
        '--project-root' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--project-root requires a path'
            }
            $projectRoot = $argv[$i + 1]
            $i++
        }
        '--skip-project' { $skipProject = 1 }
        '--replace' { $replace = 1 }
        '--interactive' { $interactive = 1 }
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

if ([string]::IsNullOrEmpty($backupDir)) {
    $backupDir = Join-Path $codexHome '.ai-workflow-backups'
}

$templates = Join-Path $rootDir 'trellis/codex'
$configToml = Join-Path $codexHome 'config.toml'


$script:mcpOriginalExisted = 0
$script:mcpBackupPath = ''
$script:mcpMutated = 0
$script:configToml = $configToml

if (Test-InstallLibExistsOrLink -Path $configToml) {
    $script:mcpOriginalExisted = 1
}
if (($script:mcpOriginalExisted -eq 1) -and ($dryRun -eq 0)) {
    if (-not (Install-LibBackupFile -Source $configToml -BackupDir $backupDir -Name 'config.toml')) {
        exit 1
    }
    $script:mcpBackupPath = $script:InstallBackupPath
} elseif ($script:mcpOriginalExisted -eq 1) {
    [Console]::Out.WriteLine("DRY-RUN: backup would use $backupDir/config.toml.<UTC timestamp>.bak")
}

function Invoke-RollbackMcp {
    if ($script:mcpMutated -eq 0) {
        return $true
    }
    if (-not (Install-LibRollbackTarget -OriginalExisted "$($script:mcpOriginalExisted)" -Backup $script:mcpBackupPath -Destination $script:configToml)) {
        [Console]::Error.WriteLine('ERROR: could not roll back Codex MCP configuration')
        return $false
    }
    $script:mcpMutated = 0
    return $true
}

$python = Resolve-InstallPython
if ([string]::IsNullOrEmpty($python)) {
    [Console]::Error.WriteLine('ERROR: Python is required for MCP merge (tried: python, python3)')
    exit 1
}

$mergeScript = Join-Path $scriptDir 'lib/merge_host_mcp.py'
$mcpArgs = @(
    $mergeScript,
    '--host', 'codex',
    '--target', $configToml,
    '--fragments', (Join-Path $templates 'mcp'),
    '--policy', $mcpPolicy
)
if (-not [string]::IsNullOrEmpty($mem0Url)) {
    $mcpArgs += @('--mem0-url', $mem0Url)
}
if (($interactive -eq 1) -and (Test-InstallLibStdinTty)) {
    $mcpArgs += '--interactive'
}
if ($dryRun -eq 1) {
    $mcpArgs += '--dry-run'
}

& $python @mcpArgs
$mcpStatus = $LASTEXITCODE
if ($mcpStatus -ne 0) {
    exit $mcpStatus
}
if ($dryRun -eq 0) {
    $script:mcpMutated = 1
}

if (-not [string]::IsNullOrEmpty($projectRoot)) {
    [Console]::Out.WriteLine(
        "INFO: ignoring --project-root for Codex hooks; installing user-level hooks under $codexHome"
    )
} elseif ($skipProject -eq 1) {
    [Console]::Out.WriteLine(
        "INFO: ignoring --skip-project for Codex hooks; installing user-level hooks under $codexHome"
    )
}

$destHooksJson = Join-Path $codexHome 'hooks.json'
$destHooksDir = Join-Path $codexHome 'hooks'

$hookArgs = @((Join-Path $scriptDir 'lib/merge_host_hooks.py'), '--host', 'codex', '--templates', $templates, '--target', $destHooksJson)
if ($dryRun -eq 1) {
    & $python @hookArgs --dry-run
    exit $LASTEXITCODE
}
$hooksJsonBackup = ''
$hooksDirBackup = ''
if (Test-InstallLibExistsOrLink -Path $destHooksJson) {
    if (-not (Install-LibBackupFile -Source $destHooksJson -BackupDir $backupDir -Name 'hooks.json')) {
        $null = Invoke-RollbackMcp
        exit 1
    }
    $hooksJsonBackup = $script:InstallBackupPath
}
if (Test-InstallLibExistsOrLink -Path $destHooksDir) {
    if (-not (Install-LibBackupFile -Source $destHooksDir -BackupDir $backupDir -Name 'hooks')) {
        $null = Invoke-RollbackMcp
        exit 1
    }
    $hooksDirBackup = $script:InstallBackupPath
}
& $python @hookArgs
if ($LASTEXITCODE -ne 0) {
    Restore-CodexUserHooks -HooksJsonBackup $hooksJsonBackup -HooksDirBackup $hooksDirBackup `
        -DestHooksJson $destHooksJson -DestHooksDir $destHooksDir
    $null = Invoke-RollbackMcp
    exit 1
}
