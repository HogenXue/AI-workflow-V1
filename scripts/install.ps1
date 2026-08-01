# PowerShell port of install.sh — interactive wizard + component dispatch + profiles.
# Requires PowerShell 7+ (pwsh). Dot-sources install-lib.ps1.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install.ps1 <skills|graphify|agents|config|codex-merge|cursor-merge> [component options]'
    )
    [Console]::Error.WriteLine('       install.ps1   # interactive (TTY only)')
    [Console]::Error.WriteLine('')
    [Console]::Error.WriteLine('Run "install.ps1 <component> --help" for component-specific options.')
    [Console]::Error.WriteLine('Non-TTY with no args prints usage and exits 2.')
}

function Get-InstallHome {
    if (-not [string]::IsNullOrEmpty($env:HOME)) {
        return $env:HOME
    }
    return $HOME
}

function Invoke-InstallComponent {
    param(
        [Parameter(Mandatory, Position = 0)][string]$Component,
        [Parameter(ValueFromRemainingArguments = $true)][object[]]$ComponentArgs = @()
    )

    $scriptMap = @{
        'skills'       = 'install-skills.ps1'
        'graphify'     = 'install-graphify.ps1'
        'agents'       = 'install-agents.ps1'
        'config'       = 'install-config.ps1'
        'codex-merge'  = 'install-codex-merge.ps1'
        'cursor-merge' = 'install-cursor-merge.ps1'
    }

    if (-not $scriptMap.ContainsKey($Component)) {
        [Console]::Error.WriteLine("ERROR: unknown installer component: $Component")
        Show-Usage
        exit 2
    }

    $scriptPath = Join-Path $PSScriptRoot $scriptMap[$Component]
    $forward = @()
    if ($null -ne $ComponentArgs -and $ComponentArgs.Count -gt 0) {
        $forward = @($ComponentArgs)
    }
    & $scriptPath @forward
}

function Test-PromptReplaceIfNeeded {
    param(
        [Parameter(Mandatory)][string]$Kind,
        [Parameter(Mandatory)][string]$Target
    )
    if (-not (Test-InstallLibExistsOrLink -Path $Target)) {
        return $true
    }
    return (Install-LibPromptYn -Question "Existing $Kind at $Target — backup and replace?" -Default 'n')
}

function Install-ProfileCodex {
    param(
        [AllowEmptyString()][string]$ProjectRoot = '',
        [AllowEmptyString()][string]$Mem0Url = ''
    )

    $homeDir = Get-InstallHome
    $skillsTarget = Join-Path $homeDir '.agents/skills'
    $configTarget = Join-Path $homeDir '.agents/config'
    $agentsHome = if (-not [string]::IsNullOrEmpty($env:CODEX_HOME)) {
        $env:CODEX_HOME
    } else {
        Join-Path $homeDir '.codex'
    }

    $skillArgs = @('--copy', '--target', $skillsTarget)
    if (Test-Path -LiteralPath $skillsTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'skills' -Target $skillsTarget) {
            $skillArgs += '--replace'
        } else {
            [Console]::Out.WriteLine('SKIP: Codex skills')
            $skillArgs = @()
        }
    }
    if ($skillArgs.Count -gt 0) {
        Invoke-InstallComponent skills @skillArgs
    }

    $graphifyTarget = Join-Path $skillsTarget 'graphify'
    $graphifyArgs = @('--apply')
    if (Test-InstallLibExistsOrLink -Path $graphifyTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'Graphify Skill' -Target $graphifyTarget) {
            $graphifyArgs += '--replace'
        } else {
            [Console]::Out.WriteLine('SKIP: Graphify global Skill')
            $graphifyArgs = @()
        }
    }
    if ($graphifyArgs.Count -gt 0) {
        Invoke-InstallComponent graphify @graphifyArgs
    }

    $configArgs = @('--copy', '--target', $configTarget)
    if (Test-Path -LiteralPath $configTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'config' -Target $configTarget) {
            $configArgs += '--replace'
        } else {
            [Console]::Out.WriteLine('SKIP: Codex config')
            $configArgs = @()
        }
    }
    if ($configArgs.Count -gt 0) {
        Invoke-InstallComponent config @configArgs
    }

    Invoke-InstallComponent agents @('--apply', '--agents-home', $agentsHome)

    $mergeArgs = [System.Collections.Generic.List[string]]::new()
    $mergeArgs.Add('--interactive') | Out-Null
    if (-not [string]::IsNullOrEmpty($Mem0Url)) {
        $mergeArgs.Add('--mem0-url') | Out-Null
        $mergeArgs.Add($Mem0Url) | Out-Null
    }
    if (-not [string]::IsNullOrEmpty($ProjectRoot)) {
        $mergeArgs.Add('--project-root') | Out-Null
        $mergeArgs.Add($ProjectRoot) | Out-Null
    }
    if (Test-InstallLibStdinTty) {
        if (Install-LibPromptYn -Question 'Overwrite existing Codex MCP entries that conflict?' -Default 'n') {
            $mergeArgs.Add('--mcp-overwrite') | Out-Null
        } else {
            $mergeArgs.Add('--mcp-keep') | Out-Null
        }
    } else {
        $mergeArgs.Add('--mcp-keep') | Out-Null
    }
    Invoke-InstallComponent codex-merge @($mergeArgs.ToArray())
}

function Install-ProfileCursor {
    param(
        [AllowEmptyString()][string]$ProjectRoot = '',
        [AllowEmptyString()][string]$Mem0Url = ''
    )

    $homeDir = Get-InstallHome
    $skillsTarget = Join-Path $homeDir '.cursor/skills'
    $configTarget = Join-Path $homeDir '.cursor/config'

    $skillArgs = @('--copy', '--target', $skillsTarget)
    if (Test-Path -LiteralPath $skillsTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'skills' -Target $skillsTarget) {
            $skillArgs += '--replace'
        } else {
            [Console]::Out.WriteLine('SKIP: Cursor skills')
            $skillArgs = @()
        }
    }
    if ($skillArgs.Count -gt 0) {
        Invoke-InstallComponent skills @skillArgs
    }

    $configArgs = @('--copy', '--target', $configTarget)
    if (Test-Path -LiteralPath $configTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'config' -Target $configTarget) {
            $configArgs += '--replace'
        } else {
            [Console]::Out.WriteLine('SKIP: Cursor config')
            $configArgs = @()
        }
    }
    if ($configArgs.Count -gt 0) {
        Invoke-InstallComponent config @configArgs
    }

    $mergeArgs = [System.Collections.Generic.List[string]]::new()
    $mergeArgs.Add('--interactive') | Out-Null
    if (-not [string]::IsNullOrEmpty($Mem0Url)) {
        $mergeArgs.Add('--mem0-url') | Out-Null
        $mergeArgs.Add($Mem0Url) | Out-Null
    }
    if (-not [string]::IsNullOrEmpty($ProjectRoot)) {
        $mergeArgs.Add('--project-root') | Out-Null
        $mergeArgs.Add($ProjectRoot) | Out-Null
    } else {
        $mergeArgs.Add('--skip-project') | Out-Null
    }
    if (Test-InstallLibStdinTty) {
        if (Install-LibPromptYn -Question 'Overwrite existing Cursor MCP entries that conflict?' -Default 'n') {
            $mergeArgs.Add('--mcp-overwrite') | Out-Null
        } else {
            $mergeArgs.Add('--mcp-keep') | Out-Null
        }
    } else {
        $mergeArgs.Add('--mcp-keep') | Out-Null
    }
    Invoke-InstallComponent cursor-merge @($mergeArgs.ToArray())
}

function Invoke-InteractiveMain {
    [Console]::Out.WriteLine('AI-workflow installer')
    [Console]::Out.WriteLine('Select target agent(s):')
    [Console]::Out.WriteLine('  1) Codex')
    [Console]::Out.WriteLine('  2) Cursor')
    [Console]::Out.WriteLine('  3) Codex + Cursor')
    [Console]::Out.Write('Choice [1-3]: ')
    $agentChoice = [Console]::In.ReadLine()
    if ($null -eq $agentChoice) { $agentChoice = '' }

    $wantCodex = $false
    $wantCursor = $false
    switch ($agentChoice) {
        '1' { $wantCodex = $true }
        '2' { $wantCursor = $true }
        '3' { $wantCodex = $true; $wantCursor = $true }
        default {
            [Console]::Error.WriteLine('ERROR: invalid agent choice')
            exit 2
        }
    }

    [Console]::Out.WriteLine('Install mode:')
    [Console]::Out.WriteLine('  1) Recommended full install')
    [Console]::Out.WriteLine('  2) Single component (advanced)')
    [Console]::Out.Write('Choice [1-2]: ')
    $modeChoice = [Console]::In.ReadLine()
    if ($null -eq $modeChoice) { $modeChoice = '1' }

    $projectRoot = ''
    if ($wantCursor) {
        $script:InstallProjectRoot = ''
        [Console]::Out.WriteLine(
            'Select project root for Cursor hooks/rules (explicit choice required; git root is only a candidate)...'
        )
        if (-not (Install-LibResolveProjectRoot -Provided '' -SkipFlag 0 -Interactive 1)) {
            exit 1
        }
        $projectRoot = if ($null -eq $script:InstallProjectRoot) { '' } else { "$($script:InstallProjectRoot)" }
    }

    $mem0Url = ''
    if (Install-LibPromptYn -Question 'Provide mem0 MCP URL now? (needed to add mem0)' -Default 'n') {
        [Console]::Out.Write('mem0 URL: ')
        $mem0Url = [Console]::In.ReadLine()
        if ($null -eq $mem0Url) { $mem0Url = '' }
    }

    if ($modeChoice -eq '2') {
        [Console]::Out.WriteLine('Component: skills | graphify | agents | config | codex-merge | cursor-merge')
        [Console]::Out.Write('Component: ')
        $comp = [Console]::In.ReadLine()
        if ($null -eq $comp) { $comp = '' }
        switch ($comp) {
            { $_ -in @('skills', 'graphify', 'agents', 'config', 'codex-merge', 'cursor-merge') } {
                $extra = [System.Collections.Generic.List[string]]::new()
                if ($comp -like '*-merge') {
                    if (-not [string]::IsNullOrEmpty($projectRoot)) {
                        $extra.Add('--project-root') | Out-Null
                        $extra.Add($projectRoot) | Out-Null
                        $extra.Add('--interactive') | Out-Null
                    } else {
                        $extra.Add('--skip-project') | Out-Null
                        $extra.Add('--interactive') | Out-Null
                    }
                    if (-not [string]::IsNullOrEmpty($mem0Url)) {
                        $extra.Add('--mem0-url') | Out-Null
                        $extra.Add($mem0Url) | Out-Null
                    }
                }
                Invoke-InstallComponent $comp @($extra.ToArray())
            }
            default {
                [Console]::Error.WriteLine('ERROR: unknown component')
                exit 2
            }
        }
        return
    }

    [Console]::Out.WriteLine('--- Recommended full install plan ---')
    if ($wantCodex) {
        [Console]::Out.WriteLine(
            '- Codex: ~/.agents/skills (including Graphify) + ~/.agents/config + ~/.codex AGENTS/user hooks + global MCP'
        )
    }
    if ($wantCursor) {
        [Console]::Out.WriteLine(
            '- Cursor: ~/.cursor/skills + ~/.cursor/config + mcp.json + project rules/hooks'
        )
    }
    if (-not [string]::IsNullOrEmpty($projectRoot)) {
        [Console]::Out.WriteLine("- Project root: $projectRoot")
    } else {
        [Console]::Out.WriteLine('- Project-scoped steps: skipped')
    }
    if (-not (Install-LibPromptYn -Question 'Proceed?' -Default 'y')) {
        [Console]::Out.WriteLine('Aborted.')
        exit 0
    }

    if ($wantCodex) {
        [Console]::Out.WriteLine('=== Installing Codex profile ===')
        Install-ProfileCodex -ProjectRoot $projectRoot -Mem0Url $mem0Url
    }
    if ($wantCursor) {
        [Console]::Out.WriteLine('=== Installing Cursor profile ===')
        Install-ProfileCursor -ProjectRoot $projectRoot -Mem0Url $mem0Url
    }
    [Console]::Out.WriteLine('Done.')
}

# --- entry ---
$argv = @($args)

if ($argv.Count -eq 0) {
    if (-not (Test-InstallLibStdinTty)) {
        Show-Usage
        exit 2
    }
    Invoke-InteractiveMain
    exit 0
}

$component = $argv[0]
$rest = @()
if ($argv.Count -gt 1) {
    $rest = $argv[1..($argv.Count - 1)]
}

switch ($component) {
    { $_ -in @('skills', 'graphify', 'agents', 'config', 'codex-merge', 'cursor-merge') } {
        Invoke-InstallComponent $component @rest
    }
    { $_ -in @('--help', '-h', 'help') } {
        Show-Usage
        exit 0
    }
    default {
        [Console]::Error.WriteLine("ERROR: unknown installer component: $component")
        Show-Usage
        exit 2
    }
}
