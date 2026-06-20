param(
    [string]$LibraryPath = (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "NotepadLibrary"),
    [switch]$SkipCodexInstall
)

$ErrorActionPreference = "Stop"

$PluginName = "codex-notepad-librarian"
$RepoRoot = $PSScriptRoot
$MarketplaceFile = Join-Path $RepoRoot ".agents\plugins\marketplace.json"
$PluginManifest = Join-Path $RepoRoot "plugins\codex-notepad-librarian\.codex-plugin\plugin.json"

function Write-SeedFile {
    param(
        [string]$Path,
        [string]$Content
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        $parent = Split-Path -Parent $Path
        if ($parent) {
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
        }
        Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
    }
}

function Run-Codex {
    param(
        [string[]]$Arguments,
        [string]$StepName
    )

    $output = & codex @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }

    if ($exitCode -ne 0 -and (($output -join "`n") -match "already")) {
        Write-Host "$StepName was already done."
        return
    }

    if ($exitCode -ne 0) {
        throw "$StepName failed. Please run the manual installation steps in README.md."
    }
}

if (-not (Test-Path -LiteralPath $MarketplaceFile)) {
    throw "Could not find $MarketplaceFile. Run this script from the downloaded plugin folder."
}

if (-not (Test-Path -LiteralPath $PluginManifest)) {
    throw "Could not find $PluginManifest. The plugin folder looks incomplete."
}

if ((-not $SkipCodexInstall) -and (-not (Get-Command codex -ErrorAction SilentlyContinue))) {
    Write-Host "Codex CLI is not installed yet."
    Write-Host "Run this command in PowerShell, close PowerShell, open it again, then run this installer again:"
    Write-Host 'powershell -ExecutionPolicy ByPass -c "irm https://chatgpt.com/codex/install.ps1 | iex"'
    exit 1
}

$LibraryRoot = [System.IO.Path]::GetFullPath($LibraryPath)

Write-Host "Creating Notepad library at:"
Write-Host $LibraryRoot

$dirs = @(
    "Inbox",
    "Library\Sources",
    "Library\Ideas",
    "Library\People",
    "Library\Topics",
    "Library\Archive\Originals",
    ".notepad-librarian"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path (Join-Path $LibraryRoot $dir) | Out-Null
}

Write-SeedFile (Join-Path $LibraryRoot "Library\Index.txt") "Notepad Librarian Index`r`n"
Write-SeedFile (Join-Path $LibraryRoot "Library\Hot.txt") "Hot Notes`r`n"
Write-SeedFile (Join-Path $LibraryRoot "Library\Log.txt") "Notepad Librarian Log`r`n"
Write-SeedFile (Join-Path $LibraryRoot ".notepad-librarian\retrieval-index.json") '{"pages":[]}'
Write-SeedFile (Join-Path $LibraryRoot ".notepad-librarian\settings.json") (@'
{
  "auto_act_on_ntl": false
}
'@)

Write-Host ""
if ($SkipCodexInstall) {
    Write-Host "Skipping Codex plugin installation."
} else {
    Write-Host "Adding Codex marketplace..."
    Run-Codex -Arguments @("plugin", "marketplace", "add", $RepoRoot) -StepName "Adding marketplace"

    Write-Host ""
    Write-Host "Installing plugin..."
    Run-Codex -Arguments @("plugin", "add", "$PluginName@$PluginName") -StepName "Installing plugin"
}

Write-Host ""
Write-Host "Done."
Write-Host "Notes folder: $LibraryRoot"
Write-Host "Start a new Codex thread and ask: Organize my Notepad notes in $LibraryRoot"
