# Migrate Atlas repo .atlas/ state to central ATLAS_DATA_DIR.
# Default data dir: $env:USERPROFILE\.cursor\atlas-data (Windows) or set ATLAS_DATA_DIR.
# Dry-run by default. Use -Apply to copy files. Use -Apply -RemoveLegacy to delete repo .atlas/ after verify.

param(
    [switch]$Apply,
    [switch]$RemoveLegacy,
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$DataDir = $env:ATLAS_DATA_DIR,
    [string]$Workspace = $env:ATLAS_WORKSPACE
)

$ErrorActionPreference = 'Stop'

if (-not $DataDir) {
    $DataDir = Join-Path $env:USERPROFILE '.cursor' 'atlas-data'
}

if (-not $Workspace) {
    $Workspace = $RepoRoot
}

$Workspace = [System.IO.Path]::GetFullPath($Workspace)
$DataDir = [System.IO.Path]::GetFullPath($DataDir)
$LegacyAtlas = Join-Path $RepoRoot '.atlas'
$TargetRuns = Join-Path $DataDir 'runs'

$GlobalFiles = @(
    'work-items.json',
    'config.json',
    'runner-jobs.json',
    'activity.jsonl'
)

function Write-Action([string]$Message) {
    Write-Host $(if ($Apply) { '[APPLY]' } else { '[DRY-RUN]' }) $Message
}

function Patch-MetaJson([string]$MetaPath, [string]$RunId) {
    if (-not (Test-Path $MetaPath)) { return }
    $meta = Get-Content $MetaPath -Raw | ConvertFrom-Json
    $changed = $false
    if (-not $meta.workspace) {
        $meta | Add-Member -NotePropertyName workspace -NotePropertyValue $Workspace -Force
        $changed = $true
    }
    if (-not $meta.slug) {
        $slug = $RunId -replace '^\d{4}-\d{2}-\d{2}-', ''
        $meta | Add-Member -NotePropertyName slug -NotePropertyValue $slug -Force
        $changed = $true
    }
    if ($changed) {
        Write-Action "Patch meta.json workspace/slug in $RunId"
        if ($Apply) {
            $meta | ConvertTo-Json -Depth 20 | Set-Content $MetaPath -Encoding utf8
        }
    }
}

Write-Host "Atlas migration to central data home"
Write-Host "  Repo:      $RepoRoot"
Write-Host "  Data dir:  $DataDir"
Write-Host "  Workspace: $Workspace"
Write-Host ""

if (-not (Test-Path $LegacyAtlas)) {
    Write-Host "No legacy .atlas at $LegacyAtlas — nothing to migrate."
    exit 0
}

Write-Action "Ensure $TargetRuns exists"
if ($Apply) {
    New-Item -ItemType Directory -Force -Path $TargetRuns | Out-Null
}

$LegacyRuns = Join-Path $LegacyAtlas 'runs'
if (Test-Path $LegacyRuns) {
    Get-ChildItem $LegacyRuns -Directory | ForEach-Object {
        $id = $_.Name
        $src = $_.FullName
        $dst = Join-Path $TargetRuns $id
        Write-Action "Copy run $id -> $dst"
        if ($Apply) {
            if (Test-Path $dst) {
                Write-Warning "Target run exists, merging/overwriting: $dst"
            }
            Copy-Item -Path $src -Destination $dst -Recurse -Force
            Patch-MetaJson (Join-Path $dst 'meta.json') $id
        }
        else {
            Patch-MetaJson (Join-Path $src 'meta.json') $id
        }
    }
}

foreach ($file in $GlobalFiles) {
    $src = Join-Path $LegacyAtlas $file
    $dst = Join-Path $DataDir $file
    if (Test-Path $src) {
        Write-Action "Move global $file -> $dst"
        if ($Apply) {
            New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
            Copy-Item -Path $src -Destination $dst -Force
        }
    }
}

if ($Apply -and $RemoveLegacy) {
    Write-Action "Remove legacy $LegacyAtlas"
    Remove-Item -Path $LegacyAtlas -Recurse -Force
}
elseif ($RemoveLegacy -and -not $Apply) {
    Write-Warning "-RemoveLegacy requires -Apply"
}

if (-not $Apply) {
    Write-Host ""
    Write-Host "Dry-run complete. Re-run with -Apply to execute. Add -RemoveLegacy after verifying Control Center lists runs."
}
