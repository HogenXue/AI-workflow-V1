# PowerShell port of install.sh — interactive wizard + component dispatch + profiles.
# Requires PowerShell 7+ (pwsh). Dot-sources install-lib.ps1.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot/install-lib.ps1"

function Show-Usage {
    [Console]::Error.WriteLine(
        'Usage: install.ps1 <deps|skills|graphify|agents|config|codex-merge|cursor-merge|claude-merge|minimax-merge|workbuddy-merge> [component options]'
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
        'deps'        = 'install-deps.ps1'
        'skills'       = 'install-skills.ps1'
        'graphify'     = 'install-graphify.ps1'
        'agents'       = 'install-agents.ps1'
        'config'       = 'install-config.ps1'
        'codex-merge'  = 'install-codex-merge.ps1'
        'cursor-merge' = 'install-cursor-merge.ps1'
        'claude-merge' = 'install-claude-merge.ps1'
        'minimax-merge' = 'install-minimax-merge.ps1'
        'workbuddy-merge' = 'install-workbuddy-merge.ps1'
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
    # Match Bash's process boundary: child exit and script scope must not leak
    # into the wizard or let a failed component be followed by more writes.
    $PSNativeCommandUseErrorActionPreference = $false
    $pwshName = if ($IsWindows) { 'pwsh.exe' } else { 'pwsh' }
    & (Join-Path $PSHOME $pwshName) -NoProfile -File $scriptPath @forward
    $componentStatus = $LASTEXITCODE
    if ($componentStatus -ne 0) {
        [Console]::Error.WriteLine("ERROR: installer component '$Component' failed (exit $componentStatus); stopping.")
        exit $componentStatus
    }
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

function Install-FullDependencies {
    $pathFile = [System.IO.Path]::GetTempFileName()
    try {
        Invoke-InstallComponent deps @('--apply', '--path-file', $pathFile)
        foreach ($directory in Get-Content -LiteralPath $pathFile) {
            if (-not [string]::IsNullOrWhiteSpace($directory)) {
                # Keep the user's Python/Node ahead of tools' private environments.
                $env:PATH = $env:PATH + [System.IO.Path]::PathSeparator + $directory
            }
        }
    } finally {
        Remove-Item -LiteralPath $pathFile -Force -ErrorAction SilentlyContinue
    }
}

function Parse-AgentSelection {
    param([AllowEmptyString()][string]$Raw = '')
    $normalized = ($Raw -replace ',', ' ').Trim()
    $wantCodex = $false
    $wantCursor = $false
    $wantClaude = $false
    $wantMinimax = $false
    $wantWorkBuddy = $false
    $found = $false
    if ([string]::IsNullOrEmpty($normalized)) {
        return $null
    }
    foreach ($token in ($normalized -split '\s+')) {
        if ([string]::IsNullOrEmpty($token)) { continue }
        switch ($token) {
            '1' { $wantCodex = $true; $found = $true }
            '2' { $wantCursor = $true; $found = $true }
            '3' { $wantClaude = $true; $found = $true }
            '4' { $wantMinimax = $true; $found = $true }
            '5' { $wantWorkBuddy = $true; $found = $true }
            default { return $null }
        }
    }
    if (-not $found) {
        return $null
    }
    return @{
        WantCodex  = $wantCodex
        WantCursor = $wantCursor
        WantClaude = $wantClaude
        WantMinimax = $wantMinimax
        WantWorkBuddy = $wantWorkBuddy
    }
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
    if (Test-InstallLibExistsOrLink -Path $skillsTarget) {
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
    if (Test-InstallLibExistsOrLink -Path $configTarget) {
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
    if (Test-InstallLibExistsOrLink -Path $skillsTarget) {
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
    if (Test-InstallLibExistsOrLink -Path $configTarget) {
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

function Install-ProfileDocumentHost {
    param(
        [Parameter(Mandatory)][string]$HostLabel,
        [Parameter(Mandatory)][string]$AgentsHome,
        [Parameter(Mandatory)][string]$DocumentName,
        [Parameter(Mandatory)][string]$MergeComponent,
        [AllowEmptyString()][string]$Mem0Url = ''
    )

    $skillsTarget = Join-Path $AgentsHome 'skills'
    $configTarget = Join-Path $AgentsHome 'config'

    $skillArgs = @('--copy', '--target', $skillsTarget)
    if (Test-InstallLibExistsOrLink -Path $skillsTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'skills' -Target $skillsTarget) {
            $skillArgs += '--replace'
        } else {
            [Console]::Out.WriteLine("SKIP: $HostLabel skills")
            $skillArgs = @()
        }
    }
    if ($skillArgs.Count -gt 0) {
        Invoke-InstallComponent skills @skillArgs
    }

    $configArgs = @('--copy', '--target', $configTarget)
    if (Test-InstallLibExistsOrLink -Path $configTarget) {
        if (Test-PromptReplaceIfNeeded -Kind 'config' -Target $configTarget) {
            $configArgs += '--replace'
        } else {
            [Console]::Out.WriteLine("SKIP: $HostLabel config")
            $configArgs = @()
        }
    }
    if ($configArgs.Count -gt 0) {
        Invoke-InstallComponent config @configArgs
    }

    Invoke-InstallComponent agents @(
        '--apply',
        '--agents-home', $agentsHome,
        '--document-name', $DocumentName,
        '--no-hooks-feature'
    )

    $mergeArgs = [System.Collections.Generic.List[string]]::new()
    $mergeArgs.Add('--interactive') | Out-Null
    if (-not [string]::IsNullOrEmpty($Mem0Url)) {
        $mergeArgs.Add('--mem0-url') | Out-Null
        $mergeArgs.Add($Mem0Url) | Out-Null
    }
    if (Test-InstallLibStdinTty) {
        if (Install-LibPromptYn -Question "Overwrite existing non-URL $HostLabel MCP entries that conflict?" -Default 'n') {
            $mergeArgs.Add('--mcp-overwrite') | Out-Null
        } else {
            $mergeArgs.Add('--mcp-keep') | Out-Null
        }
    } else {
        $mergeArgs.Add('--mcp-keep') | Out-Null
    }
    Invoke-InstallComponent $MergeComponent @($mergeArgs.ToArray())
}

function Install-ProfileClaude {
    param([AllowEmptyString()][string]$Mem0Url = '')
    Install-ProfileDocumentHost -HostLabel 'Claude' -AgentsHome (Join-Path (Get-InstallHome) '.claude') -DocumentName 'CLAUDE.md' -MergeComponent 'claude-merge' -Mem0Url $Mem0Url
}

function Install-ProfileMinimax {
    param([AllowEmptyString()][string]$Mem0Url = '')
    $hostHome = if ($env:MINIMAX_DATA_DIR) { $env:MINIMAX_DATA_DIR }
                elseif ($env:MAVIS_DATA_DIR) { $env:MAVIS_DATA_DIR }
                else { Join-Path (Get-InstallHome) '.minimax' }
    Install-ProfileDocumentHost -HostLabel 'MiniMax Code' -AgentsHome $hostHome -DocumentName 'AGENTS.md' -MergeComponent 'minimax-merge' -Mem0Url $Mem0Url
}

function Install-ProfileWorkBuddy {
    param([AllowEmptyString()][string]$Mem0Url = '')
    $hostHome = if ($env:CODEBUDDY_CONFIG_DIR) { $env:CODEBUDDY_CONFIG_DIR }
                else { Join-Path (Get-InstallHome) '.codebuddy' }
    Install-ProfileDocumentHost -HostLabel 'WorkBuddy' -AgentsHome $hostHome -DocumentName 'CODEBUDDY.md' -MergeComponent 'workbuddy-merge' -Mem0Url $Mem0Url
}

function Invoke-InteractiveMain {
    [Console]::Out.WriteLine('AI-workflow installer')
    [Console]::Out.WriteLine('Select target agent(s):')
    [Console]::Out.WriteLine('  1) Codex')
    [Console]::Out.WriteLine('  2) Cursor')
    [Console]::Out.WriteLine('  3) Claude')
    [Console]::Out.WriteLine('  4) MiniMax Code (mcode)')
    [Console]::Out.WriteLine('  5) WorkBuddy')
    [Console]::Out.Write('Select agents (e.g. 1, 1 3, 1,2,3): ')
    $agentChoice = [Console]::In.ReadLine()
    if ($null -eq $agentChoice) { $agentChoice = '' }

    $selection = Parse-AgentSelection -Raw $agentChoice
    if ($null -eq $selection) {
        [Console]::Error.WriteLine('ERROR: invalid agent choice')
        exit 2
    }
    $wantCodex = [bool]$selection.WantCodex
    $wantCursor = [bool]$selection.WantCursor
    $wantClaude = [bool]$selection.WantClaude
    $wantMinimax = [bool]$selection.WantMinimax
    $wantWorkBuddy = [bool]$selection.WantWorkBuddy

    [Console]::Out.WriteLine('Install mode:')
    [Console]::Out.WriteLine('  1) Recommended full install')
    [Console]::Out.WriteLine('  2) Single component (advanced)')
    [Console]::Out.Write('Choice [1-2]: ')
    $modeChoice = [Console]::In.ReadLine()
    if ($null -eq $modeChoice -or $modeChoice -notin @('', '1', '2')) {
        [Console]::Error.WriteLine('ERROR: invalid install mode (expected 1 or 2)')
        exit 2
    }
    if ($modeChoice -eq '') { $modeChoice = '1' }

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

    # Mem0 URL is collected during interactive MCP merge (merge_host_mcp.py), not here.
    $mem0Url = ''

    if ($modeChoice -eq '2') {
        [Console]::Out.WriteLine('Component: deps | skills | graphify | agents | config | codex-merge | cursor-merge | claude-merge | minimax-merge | workbuddy-merge')
        [Console]::Out.Write('Component: ')
        $comp = [Console]::In.ReadLine()
        if ($null -eq $comp) { $comp = '' }
        switch ($comp) {
            { $_ -in @('deps', 'skills', 'graphify', 'agents', 'config', 'codex-merge', 'cursor-merge', 'claude-merge', 'minimax-merge', 'workbuddy-merge') } {
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
    [Console]::Out.WriteLine('- Dependencies: keep usable GitNexus/Trellis/Graphify CLIs; install missing tools first')
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
    if ($wantClaude) {
        [Console]::Out.WriteLine(
            '- Claude: ~/.claude/skills + ~/.claude/config + CLAUDE.md + ~/.claude.json MCP (no Graphify, no project .claude/)'
        )
    }
    if ($wantMinimax) {
        $hostHome = if ($env:MINIMAX_DATA_DIR) { $env:MINIMAX_DATA_DIR } elseif ($env:MAVIS_DATA_DIR) { $env:MAVIS_DATA_DIR } else { Join-Path (Get-InstallHome) '.minimax' }
        [Console]::Out.WriteLine("- MiniMax Code: $hostHome/{skills,config,AGENTS.md} + native MCP")
    }
    if ($wantWorkBuddy) {
        $hostHome = if ($env:CODEBUDDY_CONFIG_DIR) { $env:CODEBUDDY_CONFIG_DIR } else { Join-Path (Get-InstallHome) '.codebuddy' }
        [Console]::Out.WriteLine("- WorkBuddy: $hostHome/{skills,config,CODEBUDDY.md} + native MCP")
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

    Install-FullDependencies

    if ($wantCodex) {
        [Console]::Out.WriteLine('=== Installing Codex profile ===')
        Install-ProfileCodex -ProjectRoot $projectRoot -Mem0Url $mem0Url
    }
    if ($wantCursor) {
        [Console]::Out.WriteLine('=== Installing Cursor profile ===')
        Install-ProfileCursor -ProjectRoot $projectRoot -Mem0Url $mem0Url
    }
    if ($wantClaude) {
        [Console]::Out.WriteLine('=== Installing Claude profile ===')
        Install-ProfileClaude -Mem0Url $mem0Url
    }
    if ($wantMinimax) {
        [Console]::Out.WriteLine('=== Installing MiniMax Code profile ===')
        Install-ProfileMinimax -Mem0Url $mem0Url
    }
    if ($wantWorkBuddy) {
        [Console]::Out.WriteLine('=== Installing WorkBuddy profile ===')
        Install-ProfileWorkBuddy -Mem0Url $mem0Url
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
    { $_ -in @('deps', 'skills', 'graphify', 'agents', 'config', 'codex-merge', 'cursor-merge', 'claude-merge', 'minimax-merge', 'workbuddy-merge') } {
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
