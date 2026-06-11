<#
Atlas installer (Windows PowerShell).
Usage:
  ./install.ps1               # install (default)
  ./install.ps1 -Mode install
  ./install.ps1 -Mode update  # re-sync, preserves your knowledge base edits
  ./install.ps1 -Mode uninstall
  ./install.ps1 -Unprefixed     # strip atlas- prefix from agent and skill names
#>
param(
  [ValidateSet("install", "update", "uninstall")]
  [string]$Mode = "install",
  [switch]$Unprefixed
)

$ErrorActionPreference = "Stop"
$bundle = $PSScriptRoot
$cursor = Join-Path $HOME ".cursor"
$manifest = Get-Content (Join-Path $bundle "manifest.json") -Raw | ConvertFrom-Json

$agentsDst = Join-Path $cursor "agents"
$skillsDst = Join-Path $cursor "skills"
$rulesDst  = Join-Path $cursor "rules"
$kbDst     = Join-Path $cursor "atlas-knowledge"

function Ensure-Dir($p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null } }

function Get-InstallName($name, [switch]$IsSkill) {
  if (-not $Unprefixed) { return $name }
  if ($IsSkill) {
    if ($name -match '^atlas-(.+)-playbook$') { return "$($Matches[1])-playbook" }
    return $name
  }
  if ($name -match '^atlas-(.+)\.md$') { return "$($Matches[1]).md" }
  return $name
}

if ($Mode -eq "uninstall") {
  Write-Host "Uninstalling Atlas (knowledge base is preserved)..."
  foreach ($a in $manifest.agents) {
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $agentsDst $a)
    Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $agentsDst (Get-InstallName $a))
  }
  foreach ($s in $manifest.skills) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $skillsDst $s)
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $skillsDst (Get-InstallName $s -IsSkill))
  }
  foreach ($r in $manifest.rules) { Remove-Item -Force -ErrorAction SilentlyContinue (Join-Path $rulesDst $r) }
  Write-Host "Done. Removed Atlas agents, skills, and rules. Left ~/.cursor/atlas-knowledge in place."
  exit 0
}

Write-Host "Atlas $Mode -> $cursor$(if ($Unprefixed) { ' (unprefixed)' })"
Ensure-Dir $agentsDst; Ensure-Dir $skillsDst; Ensure-Dir $rulesDst

foreach ($a in $manifest.agents) {
  $dstName = Get-InstallName $a
  Copy-Item -Force (Join-Path $bundle "agents\$a") (Join-Path $agentsDst $dstName)
}

foreach ($s in $manifest.skills) {
  $dstName = Get-InstallName $s -IsSkill
  $dst = Join-Path $skillsDst $dstName
  Ensure-Dir $dst
  Copy-Item -Recurse -Force (Join-Path $bundle "skills\$s\*") $dst
}

foreach ($r in $manifest.rules) {
  Copy-Item -Force (Join-Path $bundle "rules\$r") (Join-Path $rulesDst $r)
}

Ensure-Dir $kbDst
$preserve = @($manifest.preserveOnUpdate | ForEach-Object { Split-Path $_ -Leaf })
Get-ChildItem (Join-Path $bundle "knowledge") -File | ForEach-Object {
  $target = Join-Path $kbDst $_.Name
  $isPreserved = $preserve -contains $_.Name
  if ($Mode -eq "install" -or -not (Test-Path $target) -or -not $isPreserved) {
    Copy-Item -Force $_.FullName $target
  } else {
    Write-Host "  preserved $($_.Name)"
  }
}

Write-Host "Atlas $Mode complete. Open Cursor and try: $(if ($Unprefixed) { '/lead help' } else { '/atlas-lead help' })"
