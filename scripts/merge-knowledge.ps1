param(
  [switch]$Apply
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$bundleKb = Join-Path $repoRoot "knowledge"
$installedKb = Join-Path $env:USERPROFILE ".cursor\atlas-knowledge"
$preserve = @("lessons.md", "proposed.md", "ways-of-working.md", "usage-insights.md")

if (-not (Test-Path $bundleKb)) {
  Write-Error "Bundle knowledge not found: $bundleKb"
}

if (-not (Test-Path $installedKb)) {
  Write-Host "Installed KB missing; run install.ps1 first."
  exit 1
}

$bundleFiles = Get-ChildItem -Path $bundleKb -Filter "*.md" | ForEach-Object { $_.Name }
$newOrChanged = @()

foreach ($name in $bundleFiles) {
  if ($preserve -contains $name) { continue }
  $src = Join-Path $bundleKb $name
  $dst = Join-Path $installedKb $name
  if (-not (Test-Path $dst)) {
    $newOrChanged += [pscustomobject]@{ File = $name; Status = "new" }
    if ($Apply) { Copy-Item $src $dst -Force }
    continue
  }
  $srcHash = (Get-FileHash $src).Hash
  $dstHash = (Get-FileHash $dst).Hash
  if ($srcHash -ne $dstHash) {
    $newOrChanged += [pscustomobject]@{ File = $name; Status = "changed" }
    if ($Apply) { Copy-Item $src $dst -Force }
  }
}

if ($newOrChanged.Count -eq 0) {
  Write-Host "No new or changed bundle knowledge files (excluding preserved)."
} else {
  $newOrChanged | Format-Table -AutoSize
  if (-not $Apply) {
    Write-Host "Re-run with -Apply to copy new/changed files (preserved files untouched)."
  }
}
