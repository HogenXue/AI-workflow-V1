# PowerShell port of install-skills.sh. Requires PowerShell 7+ (pwsh).
# Dot-sources install-lib.ps1. Flags and message prefixes match bash.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install-skills.ps1 [--dry-run] [--link | --copy] [--replace] [--prune-legacy] [--prune-other-root] [--target PATH] [--backup-dir PATH]'
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

function Test-ExistsOrLink {
    param([Parameter(Mandatory)][string]$Path)
    return (Test-InstallLibExistsOrLink -Path $Path)
}

function Get-ManifestSkills {
    param([Parameter(Mandatory)][string]$ManifestPath)
    $names = [System.Collections.Generic.List[string]]::new()
    $inSkills = $false
    foreach ($line in Get-Content -LiteralPath $ManifestPath) {
        if ($line -match '^skills:\s*$') {
            $inSkills = $true
            continue
        }
        if ($inSkills) {
            if ($line -match '^  - ([A-Za-z0-9_-]+)\s*$') {
                $names.Add($Matches[1])
                continue
            }
            break
        }
    }
    # Emit names to the pipeline so @(Get-ManifestSkills) collects individual strings.
    return $names.ToArray()
}

function Get-ManifestDefaultInstallMode {
    param([Parameter(Mandatory)][string]$ManifestPath)
    foreach ($line in Get-Content -LiteralPath $ManifestPath) {
        if ($line -match '^default_install_mode:\s*(.+?)\s*$') {
            return $Matches[1].Trim()
        }
    }
    return ''
}

$scriptDir = $PSScriptRoot
$rootDir = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..')).ProviderPath
$manifest = Join-Path $rootDir 'manifest.yaml'
$installHome = Get-InstallHome
$target = Join-Path $installHome (Join-Path '.agents' 'skills')
$backupDir = ''
$mode = 'copy'
$modeSelected = ''
$explicitDryRun = $false
$executeRequested = $false
$replace = $false
$pruneLegacy = $false
$pruneOtherRoot = $false

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
        '--prune-legacy' {
            $pruneLegacy = $true
        }
        '--prune-other-root' {
            $pruneOtherRoot = $true
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

if (Install-LibPathsOverlap -Source (Join-Path $rootDir 'skills') -Target $target) {
    [Console]::Error.WriteLine("ERROR: skills target overlaps package source: $target")
    exit 1
}

if (-not $modeSelected) {
    if (Test-Path -LiteralPath $manifest -PathType Leaf) {
        $manifestMode = Get-ManifestDefaultInstallMode -ManifestPath $manifest
        if (-not [string]::IsNullOrEmpty($manifestMode)) {
            $mode = $manifestMode
        }
    }
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

if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) {
    [Console]::Error.WriteLine("ERROR: manifest not found: $manifest")
    exit 1
}

$skills = @(Get-ManifestSkills -ManifestPath $manifest)
if ($skills.Count -eq 0) {
    [Console]::Error.WriteLine('ERROR: manifest must list at least one skill')
    exit 1
}

$normalizedTarget = $target.TrimEnd('\', '/')
$codexHome = if (-not [string]::IsNullOrEmpty($env:CODEX_HOME)) {
    $env:CODEX_HOME
} else {
    Join-Path $installHome '.codex'
}
$codexSkills = (Join-Path $codexHome 'skills').TrimEnd('\', '/')
$sharedSkills = (Join-Path $installHome (Join-Path '.agents' 'skills')).TrimEnd('\', '/')
$otherCodexRoot = ''

$comparison = if ($IsWindows) {
    [System.StringComparison]::OrdinalIgnoreCase
} else {
    [System.StringComparison]::Ordinal
}

if ([string]::Equals($normalizedTarget, $codexSkills, $comparison)) {
    $otherCodexRoot = $sharedSkills
} elseif ([string]::Equals($normalizedTarget, $sharedSkills, $comparison)) {
    $otherCodexRoot = $codexSkills
}

if ($pruneOtherRoot -and [string]::IsNullOrEmpty($otherCodexRoot)) {
    Fail-Usage '--prune-other-root requires --target ~/.agents/skills or the active CODEX_HOME/skills'
}

$duplicateSkillNames = [System.Collections.Generic.List[string]]::new()
if (-not [string]::IsNullOrEmpty($otherCodexRoot)) {
    foreach ($skill in $skills) {
        $otherPath = Join-Path $otherCodexRoot $skill
        if (Test-ExistsOrLink -Path $otherPath) {
            $duplicateSkillNames.Add($skill)
        }
    }
}

if ($duplicateSkillNames.Count -gt 0) {
    [Console]::Error.WriteLine(
        "WARNING: duplicate Skill names also exist in ${otherCodexRoot}: $($duplicateSkillNames -join ' ')"
    )
    [Console]::Error.WriteLine('Codex may discover both roots; keep one canonical copy per Skill name.')
}

$conflicts = [System.Collections.Generic.List[string]]::new()
foreach ($skill in $skills) {
    $sourceSkill = Join-Path $rootDir "skills/$skill"
    if (-not (Test-Path -LiteralPath $sourceSkill -PathType Container)) {
        [Console]::Error.WriteLine("ERROR: source skill not found: $sourceSkill")
        exit 1
    }
    $destSkill = Join-Path $target $skill
    if (Test-ExistsOrLink -Path $destSkill) {
        $conflicts.Add($skill)
    }
}

$legacySkills = @('openspec', 'review', 'grill-me')
$legacyConflicts = [System.Collections.Generic.List[string]]::new()
foreach ($skill in $legacySkills) {
    $legacyPath = Join-Path $target $skill
    if (Test-ExistsOrLink -Path $legacyPath) {
        $legacyConflicts.Add($skill)
    }
}

if ($legacyConflicts.Count -gt 0) {
    [Console]::Error.WriteLine(
        "WARNING: legacy workflow Skills are outside the current manifest: $($legacyConflicts -join ' ')"
    )
    if (-not $pruneLegacy) {
        [Console]::Error.WriteLine(
            'They are preserved. Use --prune-legacy to back them up and remove them from this target.'
        )
    }
}

$otherRootConflicts = [System.Collections.Generic.List[string]]::new()
if (-not [string]::IsNullOrEmpty($otherCodexRoot)) {
    foreach ($skill in (@($skills) + $legacySkills)) {
        $otherPath = Join-Path $otherCodexRoot $skill
        if (Test-ExistsOrLink -Path $otherPath) {
            if (-not $otherRootConflicts.Contains($skill)) {
                $otherRootConflicts.Add($skill)
            }
        }
    }
}

if ($dryRun) {
    if ($conflicts.Count -gt 0) {
        [Console]::Error.WriteLine("CONFLICT: existing skills: $($conflicts -join ' ')")
        [Console]::Error.WriteLine('Use --replace to back up and replace them.')
    }
    foreach ($skill in $skills) {
        [Console]::Out.WriteLine("DRY-RUN: $mode $skill -> $(Join-Path $target $skill)")
    }
    if ($pruneLegacy -and $legacyConflicts.Count -gt 0) {
        foreach ($skill in $legacyConflicts) {
            [Console]::Out.WriteLine("DRY-RUN: would back up and remove legacy Skill: $skill")
        }
    }
    if ($pruneOtherRoot -and $otherRootConflicts.Count -gt 0) {
        foreach ($skill in $otherRootConflicts) {
            [Console]::Out.WriteLine(
                "DRY-RUN: would back up and remove other-root Skill: $otherCodexRoot/$skill"
            )
        }
    }
    if (
        $conflicts.Count -gt 0 -or
        ($pruneLegacy -and $legacyConflicts.Count -gt 0) -or
        ($pruneOtherRoot -and $otherRootConflicts.Count -gt 0)
    ) {
        [Console]::Out.WriteLine(
            "DRY-RUN: backups would use $backupDir/<Skill name>.<UTC timestamp>.bak"
        )
    }
    exit 0
}

if ($conflicts.Count -gt 0 -and -not $replace) {
    [Console]::Error.WriteLine("CONFLICT: existing skills: $($conflicts -join ' ')")
    [Console]::Error.WriteLine('Use --replace to back up and replace them.')
    exit 1
}

$backedUpSkills = [System.Collections.Generic.List[string]]::new()
$skillBackupPaths = [System.Collections.Generic.List[string]]::new()
$backedUpLegacySkills = [System.Collections.Generic.List[string]]::new()
$legacyBackupPaths = [System.Collections.Generic.List[string]]::new()
$backedUpOtherRootSkills = [System.Collections.Generic.List[string]]::new()
$otherRootBackupPaths = [System.Collections.Generic.List[string]]::new()
$createdSkills = [System.Collections.Generic.List[string]]::new()

function Invoke-SkillsRollback {
    param([int]$Status)

    [Console]::Error.WriteLine('ERROR: Skills installation failed; rolling back.')
    foreach ($skill in $createdSkills) {
        $path = Join-Path $target $skill
        Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue
    }
    for ($idx = 0; $idx -lt $backedUpSkills.Count; $idx++) {
        $skill = $backedUpSkills[$idx]
        $backup = $skillBackupPaths[$idx]
        if (-not (Install-LibRestoreBackup -Backup $backup -Destination (Join-Path $target $skill))) {
            [Console]::Error.WriteLine("ERROR: could not restore backup for $skill")
        }
    }
    for ($idx = 0; $idx -lt $backedUpLegacySkills.Count; $idx++) {
        $skill = $backedUpLegacySkills[$idx]
        $backup = $legacyBackupPaths[$idx]
        if (-not (Install-LibRestoreBackup -Backup $backup -Destination (Join-Path $target $skill))) {
            [Console]::Error.WriteLine("ERROR: could not restore legacy Skill $skill")
        }
    }
    for ($idx = 0; $idx -lt $backedUpOtherRootSkills.Count; $idx++) {
        $skill = $backedUpOtherRootSkills[$idx]
        $backup = $otherRootBackupPaths[$idx]
        if (-not (Install-LibRestoreBackup -Backup $backup -Destination (Join-Path $otherCodexRoot $skill))) {
            [Console]::Error.WriteLine("ERROR: could not restore other-root Skill $skill")
        }
    }
    exit $Status
}

if ($conflicts.Count -gt 0) {
    foreach ($skill in $conflicts) {
        $skillPath = Join-Path $target $skill
        if (-not (Install-LibBackupFile -Source $skillPath -BackupDir $backupDir -Name $skill)) {
            Invoke-SkillsRollback -Status 1
        }
        $backedUpSkills.Add($skill)
        $skillBackupPaths.Add($script:InstallBackupPath)
        try {
            Remove-Item -LiteralPath $skillPath -Recurse -Force -ErrorAction Stop
        } catch {
            Invoke-SkillsRollback -Status 1
        }
    }
}

if ($pruneLegacy) {
    foreach ($skill in $legacyConflicts) {
        $skillPath = Join-Path $target $skill
        if (-not (Install-LibBackupFile -Source $skillPath -BackupDir $backupDir -Name $skill)) {
            Invoke-SkillsRollback -Status 1
        }
        $backedUpLegacySkills.Add($skill)
        $legacyBackupPaths.Add($script:InstallBackupPath)
        try {
            Remove-Item -LiteralPath $skillPath -Recurse -Force -ErrorAction Stop
        } catch {
            Invoke-SkillsRollback -Status 1
        }
        [Console]::Out.WriteLine("PRUNED: legacy Skill $skill")
    }
}

if ($pruneOtherRoot -and $otherRootConflicts.Count -gt 0) {
    foreach ($skill in $otherRootConflicts) {
        $skillPath = Join-Path $otherCodexRoot $skill
        if (-not (Install-LibBackupFile -Source $skillPath -BackupDir $backupDir -Name $skill)) {
            Invoke-SkillsRollback -Status 1
        }
        $backedUpOtherRootSkills.Add($skill)
        $otherRootBackupPaths.Add($script:InstallBackupPath)
        try {
            Remove-Item -LiteralPath $skillPath -Recurse -Force -ErrorAction Stop
        } catch {
            Invoke-SkillsRollback -Status 1
        }
        [Console]::Out.WriteLine("PRUNED: other-root Skill $otherCodexRoot/$skill")
    }
}

try {
    New-Item -ItemType Directory -Path $target -Force -ErrorAction Stop | Out-Null
} catch {
    Invoke-SkillsRollback -Status 1
}

foreach ($skill in $skills) {
    $destination = Join-Path $target $skill
    $source = Join-Path $rootDir "skills/$skill"
    $createdSkills.Add($skill)
    try {
        if ($mode -eq 'link') {
            New-Item -ItemType SymbolicLink -Path $destination -Target $source -ErrorAction Stop | Out-Null
        } else {
            Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force -ErrorAction Stop
        }
    } catch {
        Invoke-SkillsRollback -Status 1
    }
    [Console]::Out.WriteLine("INSTALLED: $skill")
}
