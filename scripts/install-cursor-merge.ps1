# PowerShell port of install-cursor-merge.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-cursor-merge.ps1 [--dry-run|--apply] [--mcp-keep|--mcp-overwrite] [--mem0-url URL] [--mcp-file PATH] [--project-root PATH] [--skip-project] [--replace] [--backup-dir PATH] [--interactive]'
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

function Write-RulesMdcFromAgentsGlobal {
    param(
        [Parameter(Mandatory)][string]$Dest,
        [Parameter(Mandatory)][string]$AgentsSrc
    )
    # Match bash: frontmatter heredoc + cat AGENTS.global.md + printf '\n'
    $header = @(
        '---'
        'description: AI-workflow global guidance (from AGENTS.global.md)'
        'alwaysApply: true'
        '---'
        ''
    ) -join "`n"
    $body = Get-Content -LiteralPath $AgentsSrc -Raw -Encoding utf8
    $body = $body -replace "`r`n", "`n" -replace "`r", "`n"
    Set-Content -LiteralPath $Dest -Value ($header + $body + "`n") -Encoding utf8NoBOM -NoNewline
}

function Restore-CursorProjectFiles {
    param(
        [string]$RulesBackup,
        [string]$HooksJsonBackup,
        [string]$HooksDirBackup,
        [string]$RulesDest,
        [string]$HooksJsonDest,
        [string]$HooksDirDest
    )
    Remove-Item -LiteralPath $RulesDest -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $HooksJsonDest -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $HooksDirDest -Recurse -Force -ErrorAction SilentlyContinue
    if (-not [string]::IsNullOrEmpty($RulesBackup)) {
        $null = Install-LibRestoreBackup -Backup $RulesBackup -Destination $RulesDest
    }
    if (-not [string]::IsNullOrEmpty($HooksJsonBackup)) {
        $null = Install-LibRestoreBackup -Backup $HooksJsonBackup -Destination $HooksJsonDest
    }
    if (-not [string]::IsNullOrEmpty($HooksDirBackup)) {
        $null = Install-LibRestoreBackup -Backup $HooksDirBackup -Destination $HooksDirDest
    }
}

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath

$installHome = Get-InstallHome
$mcpFile = if (-not [string]::IsNullOrEmpty($env:CURSOR_MCP_FILE)) {
    $env:CURSOR_MCP_FILE
} else {
    Join-Path $installHome '.cursor/mcp.json'
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

if ([string]::IsNullOrEmpty($backupDir)) {
    $backupDir = Join-Path ([System.IO.Path]::GetDirectoryName($mcpFile)) '.ai-workflow-backups'
}

$templates = Join-Path $rootDir 'trellis/cursor'
$fragmentFile = Join-Path $templates 'mcp/servers.json'
if ((Test-Path -LiteralPath $mcpFile) -and (Test-SameFilesystemPath -Left $mcpFile -Right $fragmentFile)) {
    [Console]::Error.WriteLine("ERROR: Cursor MCP target must not be the package MCP fragment: $mcpFile")
    exit 1
}

$mcpParent = [System.IO.Path]::GetDirectoryName($mcpFile)
try {
    New-Item -ItemType Directory -Path $mcpParent -Force -ErrorAction Stop | Out-Null
} catch {
    [Console]::Error.WriteLine("ERROR: could not create MCP parent directory: $mcpParent")
    exit 1
}

$script:mcpOriginalExisted = 0
$script:mcpBackupPath = ''
$script:mcpMutated = 0
$script:mcpFile = $mcpFile

if (Test-InstallLibExistsOrLink -Path $mcpFile) {
    $script:mcpOriginalExisted = 1
}
if (($script:mcpOriginalExisted -eq 1) -and ($dryRun -eq 0)) {
    if (-not (Install-LibBackupFile -Source $mcpFile -BackupDir $backupDir -Name 'mcp.json')) {
        exit 1
    }
    $script:mcpBackupPath = $script:InstallBackupPath
} elseif ($script:mcpOriginalExisted -eq 1) {
    [Console]::Out.WriteLine("DRY-RUN: backup would use $backupDir/mcp.json.<UTC timestamp>.bak")
}

function Invoke-RollbackMcp {
    if ($script:mcpMutated -eq 0) {
        return $true
    }
    if (-not (Install-LibRollbackTarget -OriginalExisted "$($script:mcpOriginalExisted)" -Backup $script:mcpBackupPath -Destination $script:mcpFile)) {
        [Console]::Error.WriteLine('ERROR: could not roll back Cursor MCP configuration')
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
    '--host', 'cursor',
    '--target', $mcpFile,
    '--fragments', $fragmentFile,
    '--policy', $mcpPolicy
)
if (-not [string]::IsNullOrEmpty($mem0Url)) {
    $mcpArgs += @('--mem0-url', $mem0Url)
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

$script:InstallProjectRoot = ''
if (-not (Install-LibResolveProjectRoot -Provided $projectRoot -SkipFlag $skipProject -Interactive $interactive)) {
    $null = Invoke-RollbackMcp
    exit 1
}

if ([string]::IsNullOrEmpty($script:InstallProjectRoot)) {
    exit 0
}

$proj = $script:InstallProjectRoot
# Match bash: $root_dir/AGENTS.global.md (repo-root template; same content referenced as trellis/AGENTS.global.md in docs).
$agentsSrc = Join-Path $rootDir 'AGENTS.global.md'
$templateHooksJson = Join-Path $templates 'hooks.json'
$templateHooksDir = Join-Path $templates 'hooks'
if (
    -not (Test-Path -LiteralPath $agentsSrc -PathType Leaf) -or
    -not (Test-Path -LiteralPath $templateHooksJson -PathType Leaf) -or
    -not (Test-Path -LiteralPath $templateHooksDir -PathType Container)
) {
    [Console]::Error.WriteLine("ERROR: incomplete Cursor rules/hooks templates under $(Join-Path $rootDir 'trellis')")
    $null = Invoke-RollbackMcp
    exit 1
}

# Never modify Trellis-managed root AGENTS.md
if (Test-Path -LiteralPath (Join-Path $proj 'AGENTS.md') -PathType Leaf) {
    [Console]::Out.WriteLine('NOTE: leaving project root AGENTS.md untouched (Trellis / project owned)')
}

$rulesDest = Join-Path $proj '.cursor/rules/ai-workflow-global.mdc'
$hooksJsonDest = Join-Path $proj '.cursor/hooks.json'
$hooksDirDest = Join-Path $proj '.cursor/hooks'

$conflict = 0
if (
    (Test-InstallLibExistsOrLink -Path $rulesDest) -or
    (Test-InstallLibExistsOrLink -Path $hooksJsonDest) -or
    (Test-InstallLibExistsOrLink -Path $hooksDirDest)
) {
    $conflict = 1
}

if (($conflict -eq 1) -and ($replace -eq 0)) {
    if (($interactive -eq 1) -and (Test-InstallLibStdinTty)) {
        if (-not (Install-LibPromptYn -Question "Replace/update existing Cursor project hooks/rules in $proj?" -Default 'n')) {
            [Console]::Out.WriteLine('SKIP: existing project Cursor hooks/rules preserved')
            exit 0
        }
        $replace = 1
    } else {
        [Console]::Error.WriteLine("CONFLICT: existing Cursor project files under $proj/.cursor (use --replace)")
        $null = Invoke-RollbackMcp
        exit 1
    }
}

if ($dryRun -eq 1) {
    if ($conflict -eq 1) {
        [Console]::Out.WriteLine("DRY-RUN: hooks/rules backups would use $backupDir/<name>.<UTC timestamp>.bak")
    }
    [Console]::Out.WriteLine(
        "DRY-RUN: would generate $rulesDest from $agentsSrc and install Cursor hooks under $proj/.cursor"
    )
    exit 0
}

$rulesBackup = ''
$hooksJsonBackup = ''
$hooksDirBackup = ''
if ($replace -eq 1) {
    if (Test-InstallLibExistsOrLink -Path $rulesDest) {
        if (-not (Install-LibBackupFile -Source $rulesDest -BackupDir $backupDir -Name 'ai-workflow-global.mdc')) {
            $null = Invoke-RollbackMcp
            exit 1
        }
        $rulesBackup = $script:InstallBackupPath
    }
    if (Test-InstallLibExistsOrLink -Path $hooksJsonDest) {
        if (-not (Install-LibBackupFile -Source $hooksJsonDest -BackupDir $backupDir -Name 'hooks.json')) {
            $null = Invoke-RollbackMcp
            exit 1
        }
        $hooksJsonBackup = $script:InstallBackupPath
    }
    if (Test-InstallLibExistsOrLink -Path $hooksDirDest) {
        if (-not (Install-LibBackupFile -Source $hooksDirDest -BackupDir $backupDir -Name 'hooks')) {
            $null = Invoke-RollbackMcp
            exit 1
        }
        $hooksDirBackup = $script:InstallBackupPath
    }
    try {
        if (Test-InstallLibExistsOrLink -Path $rulesDest) {
            Remove-Item -LiteralPath $rulesDest -Force -ErrorAction Stop
        }
        if (Test-InstallLibExistsOrLink -Path $hooksJsonDest) {
            Remove-Item -LiteralPath $hooksJsonDest -Force -ErrorAction Stop
        }
        if (Test-InstallLibExistsOrLink -Path $hooksDirDest) {
            Remove-Item -LiteralPath $hooksDirDest -Recurse -Force -ErrorAction Stop
        }
    } catch {
        Restore-CursorProjectFiles -RulesBackup $rulesBackup -HooksJsonBackup $hooksJsonBackup `
            -HooksDirBackup $hooksDirBackup -RulesDest $rulesDest -HooksJsonDest $hooksJsonDest `
            -HooksDirDest $hooksDirDest
        [Console]::Error.WriteLine('ERROR: could not replace existing Cursor project hooks/rules')
        $null = Invoke-RollbackMcp
        exit 1
    }
}

try {
    New-Item -ItemType Directory -Path (Join-Path $proj '.cursor/rules') -Force -ErrorAction Stop | Out-Null
    New-Item -ItemType Directory -Path $hooksDirDest -Force -ErrorAction Stop | Out-Null
    Write-RulesMdcFromAgentsGlobal -Dest $rulesDest -AgentsSrc $agentsSrc
    Copy-Item -LiteralPath $templateHooksJson -Destination $hooksJsonDest -Force -ErrorAction Stop
    Get-ChildItem -LiteralPath $templateHooksDir -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $hooksDirDest -Recurse -Force -ErrorAction Stop
    }
} catch {
    Restore-CursorProjectFiles -RulesBackup $rulesBackup -HooksJsonBackup $hooksJsonBackup `
        -HooksDirBackup $hooksDirBackup -RulesDest $rulesDest -HooksJsonDest $hooksJsonDest `
        -HooksDirDest $hooksDirDest
    [Console]::Error.WriteLine('ERROR: could not install Cursor project hooks/rules')
    $null = Invoke-RollbackMcp
    exit 1
}

[Console]::Out.WriteLine("INSTALLED: $rulesDest (generated from $agentsSrc)")
[Console]::Out.WriteLine("INSTALLED: $hooksJsonDest")
[Console]::Out.WriteLine("INSTALLED: $hooksDirDest")
