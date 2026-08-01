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
try {
    New-Item -ItemType Directory -Path $codexHome -Force -ErrorAction Stop | Out-Null
} catch {
    [Console]::Error.WriteLine("ERROR: could not create Codex home: $codexHome")
    exit 1
}

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

$hooksExist = (
    (Test-InstallLibExistsOrLink -Path $destHooksJson) -or
    (Test-InstallLibExistsOrLink -Path $destHooksDir)
)
if ($hooksExist -and ($replace -eq 0)) {
    if (($interactive -eq 1) -and (Test-InstallLibStdinTty)) {
        if (-not (Install-LibPromptYn -Question "Replace existing Codex user hooks in $codexHome?" -Default 'n')) {
            [Console]::Out.WriteLine('SKIP: existing Codex user hooks preserved')
            exit 0
        }
        $replace = 1
    } else {
        [Console]::Error.WriteLine("CONFLICT: existing Codex user hooks at $codexHome (use --replace)")
        $null = Invoke-RollbackMcp
        exit 1
    }
}

if ($dryRun -eq 1) {
    if ($hooksExist) {
        [Console]::Out.WriteLine("DRY-RUN: hook backups would use $backupDir/<name>.<UTC timestamp>.bak")
    }
    [Console]::Out.WriteLine("DRY-RUN: would install user Codex hooks under $codexHome")
    exit 0
}

$hooksJsonBackup = ''
$hooksDirBackup = ''
if ($replace -eq 1) {
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
    try {
        if (Test-InstallLibExistsOrLink -Path $destHooksJson) {
            Remove-Item -LiteralPath $destHooksJson -Force -ErrorAction Stop
        }
        if (Test-InstallLibExistsOrLink -Path $destHooksDir) {
            Remove-Item -LiteralPath $destHooksDir -Recurse -Force -ErrorAction Stop
        }
    } catch {
        Restore-CodexUserHooks -HooksJsonBackup $hooksJsonBackup -HooksDirBackup $hooksDirBackup `
            -DestHooksJson $destHooksJson -DestHooksDir $destHooksDir
        [Console]::Error.WriteLine('ERROR: could not replace existing Codex user hooks')
        $null = Invoke-RollbackMcp
        exit 1
    }
}

$templatesHooks = Join-Path $templates 'hooks'
try {
    New-Item -ItemType Directory -Path $destHooksDir -Force -ErrorAction Stop | Out-Null
    Get-ChildItem -LiteralPath $templatesHooks -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $destHooksDir -Recurse -Force -ErrorAction Stop
    }
} catch {
    Restore-CodexUserHooks -HooksJsonBackup $hooksJsonBackup -HooksDirBackup $hooksDirBackup `
        -DestHooksJson $destHooksJson -DestHooksDir $destHooksDir
    [Console]::Error.WriteLine('ERROR: could not install Codex user hooks')
    $null = Invoke-RollbackMcp
    exit 1
}

$templateHooksJson = Join-Path $templates 'hooks.json'
$hookScript = Join-Path $destHooksDir 'session-start.sh'
$pyHookRewrite = @'
import json
import shlex
import sys
from pathlib import Path

template, target, hook_script = map(Path, sys.argv[1:])
data = json.loads(template.read_text(encoding="utf-8"))
data["hooks"]["SessionStart"][0]["hooks"][0]["command"] = f"bash {shlex.quote(str(hook_script))}"
target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
'@

$pyTmp = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-hooks-" + [guid]::NewGuid().ToString() + '.py')
$hookStatus = 1
try {
    Set-Content -LiteralPath $pyTmp -Value $pyHookRewrite -Encoding utf8NoBOM
    & $python $pyTmp $templateHooksJson $destHooksJson $hookScript
    $hookStatus = $LASTEXITCODE
} catch {
    $hookStatus = 1
} finally {
    Remove-Item -LiteralPath $pyTmp -Force -ErrorAction SilentlyContinue
}

if ($hookStatus -ne 0) {
    Restore-CodexUserHooks -HooksJsonBackup $hooksJsonBackup -HooksDirBackup $hooksDirBackup `
        -DestHooksJson $destHooksJson -DestHooksDir $destHooksDir
    [Console]::Error.WriteLine('ERROR: could not install Codex user hook config')
    $null = Invoke-RollbackMcp
    exit 1
}

# chmod +x is best-effort; no-op on Windows for .sh (matches bash `|| true`).
if (-not $IsWindows) {
    Get-ChildItem -LiteralPath $destHooksDir -Filter '*.sh' -ErrorAction SilentlyContinue | ForEach-Object {
        try {
            & chmod +x $_.FullName 2>$null
        } catch {
            # ignore
        }
    }
}

[Console]::Out.WriteLine("INSTALLED: $destHooksJson")
[Console]::Out.WriteLine("INSTALLED: $destHooksDir")
