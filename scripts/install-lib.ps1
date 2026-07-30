# Shared helpers for interactive / merge installers (PowerShell port of install-lib.sh).
# Requires PowerShell 7+ (pwsh). Dot-source: . "$PSScriptRoot/install-lib.ps1"

Set-StrictMode -Version Latest

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw "ERROR: PowerShell 7+ (pwsh) is required. Detected: $($PSVersionTable.PSVersion)"
}

$script:InstallProjectRoot = ''
$script:InstallBackupPath = ''

function Test-InstallLibStdinTty {
    try {
        return -not [Console]::IsInputRedirected
    } catch {
        return $false
    }
}

function Test-InstallLibExistsOrLink {
    param([Parameter(Mandatory)][string]$Path)
    if ([string]::IsNullOrEmpty($Path)) {
        return $false
    }
    if (Test-Path -LiteralPath $Path) {
        return $true
    }
    try {
        $null = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function ConvertTo-InstallLibFlag {
    param($Value)
    if ($null -eq $Value) {
        return $false
    }
    if ($Value -is [bool]) {
        return $Value
    }
    $text = "$Value".Trim()
    if ($text -eq '' -or $text -eq '0' -or $text -eq 'false' -or $text -eq 'False') {
        return $false
    }
    if ($text -eq '1' -or $text -eq 'true' -or $text -eq 'True') {
        return $true
    }
    try {
        return [int]$text -ne 0
    } catch {
        return $false
    }
}

function Test-InstallLibPathPrefix {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Parent
    )
    $comparison = if ($IsWindows) {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    if ([string]::Equals($Path, $Parent, $comparison)) {
        return $true
    }
    $sep = [System.IO.Path]::DirectorySeparatorChar
    $prefix = if ($Parent.EndsWith([string]$sep)) { $Parent } else { $Parent + $sep }
    return $Path.StartsWith($prefix, $comparison)
}

function Test-InstallLibIsFilesystemRoot {
    param([Parameter(Mandatory)][string]$Path)
    $comparison = if ($IsWindows) {
        [System.StringComparison]::OrdinalIgnoreCase
    } else {
        [System.StringComparison]::Ordinal
    }
    if ([string]::Equals($Path, '/', $comparison) -or [string]::Equals($Path, '\', $comparison)) {
        return $true
    }
    if ($IsWindows -and $Path -match '^[A-Za-z]:\\?$') {
        return $true
    }
    return $false
}

# Overridable copy seam (tests may redefine after dot-sourcing).
function Install-LibInternalCopy {
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Destination,
        [switch]$Recurse
    )
    $item = Get-Item -LiteralPath $Source -Force -ErrorAction Stop
    # Preserve file/dir symlinks (including dangling) the way bash `cp -pR` does.
    if ($null -ne $item.LinkType) {
        $linkTarget = $item.Target
        if ($linkTarget -is [System.Array]) {
            $linkTarget = [string]$linkTarget[0]
        } else {
            $linkTarget = [string]$linkTarget
        }
        $parent = Split-Path -Parent $Destination
        if (-not [string]::IsNullOrEmpty($parent) -and -not (Test-Path -LiteralPath $parent)) {
            New-Item -ItemType Directory -Path $parent -Force -ErrorAction Stop | Out-Null
        }
        if (Test-InstallLibExistsOrLink -Path $Destination) {
            Remove-Item -LiteralPath $Destination -Force -ErrorAction Stop
        }
        New-Item -ItemType SymbolicLink -Path $Destination -Target $linkTarget -Force -ErrorAction Stop | Out-Null
        return
    }
    if ($Recurse) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force -ErrorAction Stop
    } else {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force -ErrorAction Stop
    }
}

function Install-LibPromptYn {
    param(
        [Parameter(Mandatory)][string]$Question,
        [string]$Default = 'n'
    )
    if (-not (Test-InstallLibStdinTty)) {
        return ($Default -match '^[Yy]')
    }
    if ($Default -match '^[Yy]') {
        [Console]::Error.Write("$Question [Y/n]: ")
    } else {
        [Console]::Error.Write("$Question [y/N]: ")
    }
    $reply = [Console]::In.ReadLine()
    if ($null -eq $reply) {
        $reply = ''
    }
    if ([string]::IsNullOrEmpty($reply)) {
        $reply = $Default
    }
    return ($reply -match '^[Yy]')
}

function Install-LibCandidateGitRoot {
    param([string]$Path = '')
    if ([string]::IsNullOrEmpty($Path)) {
        $Path = (Get-Location).Path
    }
    try {
        $result = & git -C $Path rev-parse --show-toplevel 2>$null
        if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($result)) {
            return "$result".Trim()
        }
    } catch {
        # ignore
    }
    return ''
}

# Sets $script:InstallProjectRoot to absolute path, or empty if skipped.
# Never silently applies git toplevel — PRD requires an explicit choice.
# Order: --project-root → --skip-project → TTY menu (git root as candidate) → skip.
function Install-LibResolveProjectRoot {
    param(
        [string]$Provided = '',
        $SkipFlag = 0,
        $Interactive = 0
    )

    $script:InstallProjectRoot = ''
    $skip = ConvertTo-InstallLibFlag $SkipFlag
    $interactive = ConvertTo-InstallLibFlag $Interactive

    if ($skip) {
        [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (--skip-project)')
        return $true
    }

    if (-not [string]::IsNullOrEmpty($Provided)) {
        if (-not (Test-Path -LiteralPath $Provided -PathType Container)) {
            [Console]::Error.WriteLine("ERROR: --project-root is not a directory: $Provided")
            return $false
        }
        $script:InstallProjectRoot = (Resolve-Path -LiteralPath $Provided).ProviderPath
        return $true
    }

    $gitRoot = Install-LibCandidateGitRoot -Path (Get-Location).Path

    if ($interactive -and (Test-InstallLibStdinTty)) {
        [Console]::Error.WriteLine('Project-scoped hooks/rules require an explicit project root.')
        [Console]::Error.WriteLine('Git toplevel is a candidate only — it is never applied automatically.')
        $choice = ''
        if (-not [string]::IsNullOrEmpty($gitRoot)) {
            [Console]::Error.WriteLine("  1) $gitRoot  (detected git root)")
            [Console]::Error.WriteLine('  2) Enter a custom path')
            [Console]::Error.WriteLine('  3) Skip project-scoped steps')
            [Console]::Error.Write('Choice [1-3]: ')
            $choice = [Console]::In.ReadLine()
            if ($null -eq $choice) { $choice = '' }
            switch ($choice) {
                '1' {
                    $script:InstallProjectRoot = $gitRoot
                    [Console]::Out.WriteLine("PROJECT-ROOT: $($script:InstallProjectRoot) (user-selected git root)")
                    return $true
                }
                '2' {
                    [Console]::Error.Write('Project path: ')
                    $typed = [Console]::In.ReadLine()
                    if ($null -eq $typed) { $typed = '' }
                    if ([string]::IsNullOrEmpty($typed)) {
                        [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (empty path)')
                        return $true
                    }
                    if (-not (Test-Path -LiteralPath $typed -PathType Container)) {
                        [Console]::Error.WriteLine('ERROR: invalid project path')
                        return $false
                    }
                    $script:InstallProjectRoot = (Resolve-Path -LiteralPath $typed).ProviderPath
                    return $true
                }
                { $_ -eq '3' -or $_ -eq '' } {
                    [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (user declined)')
                    return $true
                }
                default {
                    [Console]::Error.WriteLine('ERROR: invalid project-root choice')
                    return $false
                }
            }
        }

        [Console]::Error.WriteLine('  1) Enter a custom path')
        [Console]::Error.WriteLine('  2) Skip project-scoped steps')
        [Console]::Error.Write('Choice [1-2]: ')
        $choice = [Console]::In.ReadLine()
        if ($null -eq $choice) { $choice = '' }
        switch ($choice) {
            '1' {
                [Console]::Error.Write('Project path: ')
                $typed = [Console]::In.ReadLine()
                if ($null -eq $typed) { $typed = '' }
                if ([string]::IsNullOrEmpty($typed)) {
                    [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (empty path)')
                    return $true
                }
                if (-not (Test-Path -LiteralPath $typed -PathType Container)) {
                    [Console]::Error.WriteLine('ERROR: invalid project path')
                    return $false
                }
                $script:InstallProjectRoot = (Resolve-Path -LiteralPath $typed).ProviderPath
                return $true
            }
            { $_ -eq '2' -or $_ -eq '' } {
                [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (user declined)')
                return $true
            }
            default {
                [Console]::Error.WriteLine('ERROR: invalid project-root choice')
                return $false
            }
        }
    }

    [Console]::Out.WriteLine('SKIP: skipping project-scoped steps (no --project-root; pass --project-root PATH to install hooks/rules)')
    return $true
}

function Install-LibNormalizePath {
    param([Parameter(Mandatory)][string]$RawPath)

    $resolved = $RawPath
    if (-not [System.IO.Path]::IsPathRooted($resolved)) {
        $resolved = Join-Path (Get-Location).Path $resolved
    }

    try {
        $resolved = [System.IO.Path]::GetFullPath($resolved)
    } catch {
        return $null
    }

    $probe = $resolved
    $suffix = New-Object System.Collections.Generic.List[string]
    while (-not (Test-Path -LiteralPath $probe -PathType Container)) {
        # Split-Path -LiteralPath cannot combine with -Parent/-Leaf on all pwsh builds;
        # use .NET for literal path decomposition.
        $parent = [System.IO.Path]::GetDirectoryName($probe)
        if ([string]::IsNullOrEmpty($parent) -or $parent -eq $probe) {
            return $null
        }
        $component = [System.IO.Path]::GetFileName($probe)
        $suffix.Insert(0, $component)
        $probe = $parent
    }

    try {
        $normalized = (Resolve-Path -LiteralPath $probe).ProviderPath
    } catch {
        return $null
    }

    foreach ($component in $suffix) {
        switch ($component) {
            '.' { }
            '' { }
            '..' {
                $parent = [System.IO.Path]::GetDirectoryName($normalized)
                if ([string]::IsNullOrEmpty($parent)) {
                    return $null
                }
                $normalized = $parent
            }
            default {
                $normalized = Join-Path $normalized $component
            }
        }
    }
    return $normalized
}

function Install-LibPathsOverlap {
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Target
    )
    $sourceReal = Install-LibNormalizePath -RawPath $Source
    if ($null -eq $sourceReal) {
        return $false
    }
    $targetReal = Install-LibNormalizePath -RawPath $Target
    if ($null -eq $targetReal) {
        return $false
    }
    if (
        (Test-InstallLibIsFilesystemRoot -Path $sourceReal) -or
        (Test-InstallLibIsFilesystemRoot -Path $targetReal) -or
        (Test-InstallLibPathPrefix -Path $sourceReal -Parent $targetReal) -or
        (Test-InstallLibPathPrefix -Path $targetReal -Parent $sourceReal)
    ) {
        return $true
    }
    return $false
}

function Install-LibPathIsWithin {
    param(
        [Parameter(Mandatory)][string]$Candidate,
        [Parameter(Mandatory)][string]$Parent
    )
    $candidateReal = Install-LibNormalizePath -RawPath $Candidate
    if ($null -eq $candidateReal) {
        return $false
    }
    $parentReal = Install-LibNormalizePath -RawPath $Parent
    if ($null -eq $parentReal) {
        return $false
    }
    return (Test-InstallLibPathPrefix -Path $candidateReal -Parent $parentReal)
}

function Install-LibBackupFile {
    param(
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$BackupDir,
        [string]$Name = ''
    )

    $script:InstallBackupPath = ''
    if (-not (Test-InstallLibExistsOrLink -Path $Source)) {
        return $true
    }

    if (Install-LibPathIsWithin -Candidate $BackupDir -Parent $Source) {
        [Console]::Error.WriteLine(
            "ERROR: backup directory must not be inside the target being backed up: $BackupDir"
        )
        return $false
    }

    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $trimmedSource = $Source.TrimEnd('\', '/')
    if ([string]::IsNullOrEmpty($Name)) {
        $Name = [System.IO.Path]::GetFileName($trimmedSource)
    }

    try {
        New-Item -ItemType Directory -Path $BackupDir -Force -ErrorAction Stop | Out-Null
    } catch {
        [Console]::Error.WriteLine("ERROR: could not create backup directory: $BackupDir")
        return $false
    }

    $candidate = Join-Path $BackupDir "$Name.$stamp.bak"
    $lock = ''
    $sequence = 1
    while ($true) {
        $lock = "$candidate.lock"
        if (
            (Test-InstallLibExistsOrLink -Path $candidate) -or
            (Test-InstallLibExistsOrLink -Path $lock)
        ) {
            $candidate = Join-Path $BackupDir "$Name.$stamp-$sequence.bak"
            $sequence++
            continue
        }

        $reserved = $false
        try {
            New-Item -ItemType Directory -Path $lock -ErrorAction Stop | Out-Null
            $reserved = $true
        } catch {
            if (
                -not (Test-InstallLibExistsOrLink -Path $candidate) -and
                -not (Test-InstallLibExistsOrLink -Path $lock)
            ) {
                [Console]::Error.WriteLine("ERROR: could not reserve backup path under: $BackupDir")
                return $false
            }
            $candidate = Join-Path $BackupDir "$Name.$stamp-$sequence.bak"
            $sequence++
            continue
        }

        if ($reserved -and -not (Test-InstallLibExistsOrLink -Path $candidate)) {
            break
        }
        Remove-Item -LiteralPath $lock -Force -ErrorAction SilentlyContinue
        $candidate = Join-Path $BackupDir "$Name.$stamp-$sequence.bak"
        $sequence++
    }

    $staging = Join-Path $lock 'payload'
    try {
        Install-LibInternalCopy -Source $Source -Destination $staging -Recurse
    } catch {
        Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
        [Console]::Error.WriteLine("ERROR: could not back up existing target: $Source")
        return $false
    }

    try {
        Move-Item -LiteralPath $staging -Destination $candidate -ErrorAction Stop
    } catch {
        Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
        [Console]::Error.WriteLine("ERROR: could not finalize backup for: $Source")
        return $false
    }

    try {
        Remove-Item -LiteralPath $lock -Force -ErrorAction Stop
    } catch {
        Remove-Item -LiteralPath $lock -Recurse -Force -ErrorAction SilentlyContinue
    }

    $script:InstallBackupPath = $candidate
    [Console]::Out.WriteLine("BACKUP: $candidate")
    return $true
}

function Install-LibRestoreBackup {
    param(
        [Parameter(Mandatory)][AllowEmptyString()][string]$Backup,
        [Parameter(Mandatory)][string]$Destination
    )

    if ([string]::IsNullOrEmpty($Backup) -or -not (Test-InstallLibExistsOrLink -Path $Backup)) {
        [Console]::Error.WriteLine("ERROR: backup is unavailable for restore: $Backup")
        return $false
    }

    $backupItem = Get-Item -LiteralPath $Backup -Force
    $destExists = Test-Path -LiteralPath $Destination
    $destItem = $null
    if ($destExists) {
        $destItem = Get-Item -LiteralPath $Destination -Force
    }

    $backupIsFile = ($backupItem -is [System.IO.FileInfo]) -and ($null -eq $backupItem.LinkType)
    $destIsFile = $destExists -and ($destItem -is [System.IO.FileInfo]) -and ($null -eq $destItem.LinkType)

    if ($backupIsFile -and $destIsFile) {
        try {
            Install-LibInternalCopy -Source $Backup -Destination $Destination
        } catch {
            [Console]::Error.WriteLine("ERROR: could not restore $Destination from $Backup")
            return $false
        }
        return $true
    }

    try {
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force -ErrorAction Stop
        }
    } catch {
        [Console]::Error.WriteLine("ERROR: could not clear failed target before restore: $Destination")
        return $false
    }

    try {
        Install-LibInternalCopy -Source $Backup -Destination $Destination -Recurse
    } catch {
        [Console]::Error.WriteLine("ERROR: could not restore $Destination from $Backup")
        return $false
    }
    return $true
}

function Install-LibRollbackTarget {
    param(
        [Parameter(Mandatory)][string]$OriginalExisted,
        [AllowEmptyString()][string]$Backup,
        [Parameter(Mandatory)][string]$Destination
    )

    if ("$OriginalExisted" -eq '1') {
        return (Install-LibRestoreBackup -Backup $Backup -Destination $Destination)
    }

    try {
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force -ErrorAction Stop
        }
    } catch {
        [Console]::Error.WriteLine(
            "ERROR: could not remove newly created target during rollback: $Destination"
        )
        return $false
    }
    return $true
}
