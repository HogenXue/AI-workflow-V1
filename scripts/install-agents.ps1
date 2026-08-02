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

function Test-IsRegularFile {
    param([Parameter(Mandatory)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $false
    }
    $item = Get-Item -LiteralPath $Path -Force
    if ($null -ne $item.LinkType) {
        return $false
    }
    return ($item -is [System.IO.FileInfo])
}

function Test-ConfigFileValid {
    param([Parameter(Mandatory)][string]$AgentsHome)
    $configFile = Join-Path $AgentsHome 'config.toml'
    if (Test-InstallLibExistsOrLink -Path $configFile) {
        if (-not (Test-IsRegularFile -Path $configFile)) {
            [Console]::Error.WriteLine("ERROR: config.toml is not a regular file: $configFile")
            return $false
        }
    }
    return $true
}

function Enable-HooksFeature {
    param(
        [Parameter(Mandatory)][string]$AgentsHome,
        [Parameter(Mandatory)][string]$BackupDir
    )

    $configFile = Join-Path $AgentsHome 'config.toml'
    $hookSetting = 'hooks = true   # Codex 0.129+。旧版用 `codex_hooks = true`。'

    if (-not (Test-ConfigFileValid -AgentsHome $AgentsHome)) {
        return $false
    }

    $tempName = [System.IO.Path]::GetRandomFileName()
    $configTmp = Join-Path $AgentsHome ".config.toml.trellis.$tempName"
    try {
        $null = New-Item -ItemType File -Path $configTmp -Force -ErrorAction Stop
    } catch {
        [Console]::Error.WriteLine('ERROR: could not create a temporary config file')
        return $false
    }

    if (Test-Path -LiteralPath $configFile -PathType Leaf) {
        try {
            $lines = Get-Content -LiteralPath $configFile
            $output = [System.Collections.Generic.List[string]]::new()
            $inFeatures = $false
            $featuresFound = $false
            $hooksFound = $false

            function Test-IsFeaturesHeader {
                param([string]$Line)
                $value = $Line -replace '^\s+', ''
                return $value -match '^\[features\]\s*(#.*)?$'
            }

            function Test-IsTableHeader {
                param([string]$Line)
                $value = $Line -replace '^\s+', ''
                return $value -match '^\[[^\]]+\]\s*(#.*)?$'
            }

            foreach ($line in $lines) {
                if (Test-IsTableHeader -Line $line) {
                    if ($inFeatures -and -not $hooksFound) {
                        $output.Add($hookSetting)
                        $hooksFound = $true
                    }
                    $inFeatures = Test-IsFeaturesHeader -Line $line
                    if ($inFeatures) {
                        $featuresFound = $true
                    }
                    $output.Add($line)
                    continue
                }
                if ($inFeatures -and ($line -match '^\s*hooks\s*=')) {
                    $output.Add($hookSetting)
                    $hooksFound = $true
                    continue
                }
                $output.Add($line)
            }

            if ($inFeatures -and -not $hooksFound) {
                $output.Add($hookSetting)
            }
            if (-not $featuresFound) {
                if ($output.Count -gt 0) {
                    $output.Add('')
                }
                $output.Add('[features]')
                $output.Add($hookSetting)
            }

            Set-Content -LiteralPath $configTmp -Value $output -Encoding utf8NoBOM
        } catch {
            Remove-Item -LiteralPath $configTmp -Force -ErrorAction SilentlyContinue
            [Console]::Error.WriteLine('ERROR: could not update config.toml')
            return $false
        }

        $originalText = Get-Content -LiteralPath $configFile -Raw
        $newText = Get-Content -LiteralPath $configTmp -Raw
        if ($originalText -eq $newText) {
            Remove-Item -LiteralPath $configTmp -Force -ErrorAction SilentlyContinue
            [Console]::Out.WriteLine('UNCHANGED: config.toml already enables hooks')
            return $true
        }

        if (-not (Install-LibBackupFile -Source $configFile -BackupDir $BackupDir -Name 'config.toml')) {
            Remove-Item -LiteralPath $configTmp -Force -ErrorAction SilentlyContinue
            return $false
        }
    } else {
        @(
            '[features]'
            $hookSetting
        ) | Set-Content -LiteralPath $configTmp -Encoding utf8NoBOM
    }

    try {
        Move-Item -LiteralPath $configTmp -Destination $configFile -Force -ErrorAction Stop
    } catch {
        Remove-Item -LiteralPath $configTmp -Force -ErrorAction SilentlyContinue
        [Console]::Error.WriteLine('ERROR: could not install config.toml update')
        return $false
    }
    [Console]::Out.WriteLine('UPDATED: config.toml hooks feature enabled')
    return $true
}

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath
$sourceFile = Join-Path $rootDir 'AGENTS.global.md'
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

if ($mode -eq 'dry-run') {
    [Console]::Out.WriteLine("DRY-RUN: would copy $sourceFile -> $targetFile")
    if (Test-InstallLibExistsOrLink -Path $targetFile) {
        [Console]::Out.WriteLine(
            "DRY-RUN: would back up $targetFile as $backupDir/$documentName.<UTC timestamp>.bak"
        )
    }
    if ($noHooksFeature -eq 0) {
        [Console]::Out.WriteLine('DRY-RUN: would ensure [features].hooks = true in config.toml')
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

if ($noHooksFeature -eq 0) {
    if (-not (Test-ConfigFileValid -AgentsHome $agentsHome)) {
        exit 1
    }
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

if ($noHooksFeature -eq 1) {
    exit 0
}

if (-not (Enable-HooksFeature -AgentsHome $agentsHome -BackupDir $backupDir)) {
    [Console]::Error.WriteLine("ERROR: config.toml update failed; restoring $documentName.")
    if ($agentsBackupAvailable) {
        if (-not (Install-LibRestoreBackup -Backup $agentsBackupPath -Destination $targetFile)) {
            [Console]::Error.WriteLine("ERROR: could not restore $documentName from backup")
            exit 1
        }
    } else {
        try {
            Remove-Item -LiteralPath $targetFile -Force -ErrorAction Stop
        } catch {
            [Console]::Error.WriteLine("ERROR: could not remove newly installed $documentName")
            exit 1
        }
    }
    exit 1
}
