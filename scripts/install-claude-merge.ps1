# PowerShell port of install-claude-merge.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.
# Claude merge is user-level MCP only (no project hooks/rules).

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-claude-merge.ps1 [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--mcp-file PATH] [--replace] [--backup-dir PATH] [--interactive]'
    )
    [Console]::Error.WriteLine(
        '       --project-root and --skip-project are accepted for wizard compatibility but ignored; Claude merge is user-level MCP only.'
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

function Test-SameFilesystemPath {
    param(
        [Parameter(Mandatory)][string]$Left,
        [Parameter(Mandatory)][string]$Right
    )
    if (-not (Test-Path -LiteralPath $Left) -or -not (Test-Path -LiteralPath $Right)) {
        return $false
    }
    try {
        $leftPath = (Resolve-Path -LiteralPath $Left).ProviderPath
        $rightPath = (Resolve-Path -LiteralPath $Right).ProviderPath
    } catch {
        return $false
    }
    if ($IsWindows) {
        return [string]::Equals($leftPath, $rightPath, [System.StringComparison]::OrdinalIgnoreCase)
    }
    return $leftPath -eq $rightPath
}

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath

$installHome = Get-InstallHome
$mcpFile = if (-not [string]::IsNullOrEmpty($env:CLAUDE_MCP_FILE)) {
    $env:CLAUDE_MCP_FILE
} else {
    Join-Path $installHome '.claude.json'
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
        '--mcp-file' {
            if (($i + 1) -ge $argv.Count) {
                Fail-Usage '--mcp-file requires a path'
            }
            $mcpFile = $argv[$i + 1]
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

if (-not [string]::IsNullOrEmpty($projectRoot)) {
    [Console]::Out.WriteLine(
        'SKIP: Claude merge has no project-scoped steps (project .claude/ is Trellis-managed)'
    )
}
if ($skipProject -eq 1) {
    [Console]::Out.WriteLine('SKIP: --skip-project ignored (Claude merge is user-level MCP only)')
}
# --replace accepted for surface parity; no project targets to replace.
$null = $replace

if ([string]::IsNullOrEmpty($backupDir)) {
    # Prefer paired host backup root under ~/.claude even when MCP file is ~/.claude.json.
    $backupDir = Join-Path $installHome '.claude/.ai-workflow-backups'
}

$templates = Join-Path $rootDir 'trellis/claude'
$fragmentFile = Join-Path $templates 'mcp/servers.json'
if ((Test-Path -LiteralPath $mcpFile) -and (Test-SameFilesystemPath -Left $mcpFile -Right $fragmentFile)) {
    [Console]::Error.WriteLine("ERROR: Claude MCP target must not be the package MCP fragment: $mcpFile")
    exit 1
}

$mcpParent = [System.IO.Path]::GetDirectoryName($mcpFile)
try {
    New-Item -ItemType Directory -Path $mcpParent -Force -ErrorAction Stop | Out-Null
} catch {
    [Console]::Error.WriteLine("ERROR: could not create MCP parent directory: $mcpParent")
    exit 1
}
$backupParent = [System.IO.Path]::GetDirectoryName($backupDir)
if (-not [string]::IsNullOrEmpty($backupParent)) {
    try {
        New-Item -ItemType Directory -Path $backupParent -Force -ErrorAction Stop | Out-Null
    } catch {
        [Console]::Error.WriteLine("ERROR: could not create backup parent directory: $backupParent")
        exit 1
    }
}

$script:mcpOriginalExisted = 0
$script:mcpBackupPath = ''
$script:mcpMutated = 0
$script:mcpFile = $mcpFile

if (Test-InstallLibExistsOrLink -Path $mcpFile) {
    $script:mcpOriginalExisted = 1
}
if (($script:mcpOriginalExisted -eq 1) -and ($dryRun -eq 0)) {
    if (-not (Install-LibBackupFile -Source $mcpFile -BackupDir $backupDir -Name 'claude.json')) {
        exit 1
    }
    $script:mcpBackupPath = $script:InstallBackupPath
} elseif ($script:mcpOriginalExisted -eq 1) {
    [Console]::Out.WriteLine("DRY-RUN: backup would use $backupDir/claude.json.<UTC timestamp>.bak")
}

function Invoke-RollbackMcp {
    if ($script:mcpMutated -eq 0) {
        return $true
    }
    if (-not (Install-LibRollbackTarget -OriginalExisted "$($script:mcpOriginalExisted)" -Backup $script:mcpBackupPath -Destination $script:mcpFile)) {
        [Console]::Error.WriteLine('ERROR: could not roll back Claude MCP configuration')
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
    '--host', 'claude',
    '--target', $mcpFile,
    '--fragments', $fragmentFile,
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
