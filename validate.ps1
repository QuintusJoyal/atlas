<#
Atlas self-validation (Windows PowerShell).
Checks:
  - every agent has name, description, model in frontmatter
  - agent name matches its filename and is atlas-prefixed
  - model IDs are from the allowed set
  - referenced <role>-playbook skills exist
  - no em dashes or common AI tells in bundle text
Exits non-zero on any failure.
#>
$ErrorActionPreference = "Stop"
$bundle = $PSScriptRoot
$errors = New-Object System.Collections.Generic.List[string]
$allowedModels = @("claude-opus-4-8-thinking-high", "composer-2.5", "composer-2", "inherit")

# 1. Agents frontmatter + model + name
Get-ChildItem (Join-Path $bundle "agents") -Filter *.md | ForEach-Object {
  $text = Get-Content $_.FullName -Raw
  $base = $_.BaseName
  if ($text -notmatch "(?m)^name:\s*(.+)$") { $errors.Add("$($_.Name): missing name") }
  else {
    $n = $Matches[1].Trim()
    if ($n -ne $base) { $errors.Add("$($_.Name): name '$n' does not match filename '$base'") }
    if ($n -notlike "atlas-*") { $errors.Add("$($_.Name): name '$n' is not atlas-prefixed") }
  }
  if ($text -notmatch "(?m)^description:\s*\S") { $errors.Add("$($_.Name): missing description") }
  if ($text -match "(?m)^model:\s*(.+)$") {
    $m = $Matches[1].Trim()
    if ($allowedModels -notcontains $m) { $errors.Add("$($_.Name): model '$m' not in allowed set") }
  } else { $errors.Add("$($_.Name): missing model") }
}

# 2. Referenced playbooks exist
$skillsDir = Join-Path $bundle "skills"
Get-ChildItem (Join-Path $bundle "agents") -Filter *.md | ForEach-Object {
  $text = Get-Content $_.FullName -Raw
  [regex]::Matches($text, "atlas-[a-z-]+-playbook") | ForEach-Object {
    $pb = $_.Value
    if (-not (Test-Path (Join-Path $skillsDir "$pb\SKILL.md"))) {
      $errors.Add("$pb referenced but skills/$pb/SKILL.md not found")
    }
  }
}

# 3. Em dashes and AI tells across bundle text (writing-style.mdc lists banned phrases as examples)
$tells = @("as an AI", "delve", "tapestry", "in conclusion", "it is important to note", "it is worth noting")
Get-ChildItem $bundle -Recurse -Include *.md, *.mdc -File | Where-Object {
  $_.FullName -notlike "*\.git\*" -and $_.FullName -notlike "*\node_modules\*" -and $_.Name -ne "writing-style.mdc"
} | ForEach-Object {
  $text = Get-Content $_.FullName -Raw
  if ($null -eq $text) { return }
  if ($text.Contains([char]0x2014)) { $errors.Add("$($_.Name): contains an em dash") }
  foreach ($t in $tells) {
    if ($text -match [regex]::Escape($t)) { $errors.Add("$($_.Name): contains AI tell '$t'") }
  }
}

if ($errors.Count -gt 0) {
  Write-Host "Validation FAILED:" -ForegroundColor Red
  $errors | ForEach-Object { Write-Host "  - $_" }
  exit 1
}
Write-Host "Validation passed. Atlas looks consistent." -ForegroundColor Green
