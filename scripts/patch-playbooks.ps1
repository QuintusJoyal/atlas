$refs = @{
  'atlas-pm-playbook' = @(
    'https://www.agilealliance.org/glossary/invest/'
    'https://www.scrum.org/resources/what-is-scrum'
  )
  'atlas-ba-playbook' = @(
    'https://www.iiba.org/business-analysis-standards/babok-guide/'
    'https://cucumber.io/docs/gherkin/'
  )
  'atlas-architect-playbook' = @(
    'https://c4model.com/'
    'https://12factor.net/'
    'https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html'
  )
  'atlas-ux-playbook' = @(
    'https://www.w3.org/WAI/WCAG22/quickref/'
    'https://www.nngroup.com/articles/ten-usability-heuristics/'
  )
  'atlas-dev-playbook' = @(
    'https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html'
    'https://www.conventionalcommits.org/'
  )
  'atlas-qa-playbook' = @(
    'https://www.istqb.org/'
    'https://martinfowler.com/articles/practical-test-pyramid.html'
  )
  'atlas-security-playbook' = @(
    'https://owasp.org/www-project-application-security-verification-standard/'
    'https://owasp.org/www-project-top-ten/'
    'https://csrc.nist.gov/publications/detail/sp/800-218/final'
  )
  'atlas-reviewer-playbook' = @(
    'https://google.github.io/eng-practices/review/'
  )
  'atlas-devops-playbook' = @(
    'https://dora.dev/'
    'https://sre.google/sre-book/table-of-contents/'
  )
  'atlas-maintenance-playbook' = @(
    'https://sre.google/sre-book/postmortem-culture/'
  )
  'atlas-docs-playbook' = @(
    'https://diataxis.fr/'
  )
  'atlas-network-playbook' = @(
    'https://csrc.nist.gov/publications/detail/sp/800-207/final'
  )
  'atlas-sysinfra-playbook' = @(
    'https://www.cisecurity.org/cis-benchmarks'
  )
  'atlas-cloud-playbook' = @(
    'https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html'
    'https://www.finops.org/framework/'
  )
  'atlas-dba-playbook' = @(
    'https://www.postgresql.org/docs/current/index.html'
  )
  'atlas-data-eng-playbook' = @(
    'https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/'
  )
  'atlas-data-sci-playbook' = @(
    'https://www.crisp-dm.org/'
    'https://ml-ops.org/'
  )
  'atlas-ai-eng-playbook' = @(
    'https://www.nist.gov/itl/ai-risk-management-framework'
  )
  'atlas-data-analyst-playbook' = @(
    'https://www.edwardtufte.com/tufte/'
  )
  'atlas-ent-arch-playbook' = @(
    'https://www.opengroup.org/togaf'
    'https://www.enterpriseintegrationpatterns.com/'
  )
  'atlas-delivery-playbook' = @(
    'https://www.pmi.org/standards/pmbok'
  )
  'atlas-consultant-playbook' = @(
    'https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-mckinsey-approach-to-problem-solving'
  )
  'atlas-compliance-playbook' = @(
    'https://gdpr.eu/'
    'https://www.aicpa.org/soc'
    'https://www.iso.org/standard/54534.html'
    'https://www.nist.gov/cyberframework'
  )
  'atlas-lead-playbook' = @(
    'https://scrumguides.org/'
  )
}

Get-ChildItem (Join-Path (Split-Path $PSScriptRoot -Parent) 'skills') -Directory | ForEach-Object {
  $skillPath = Join-Path $_.FullName 'SKILL.md'
  if (-not (Test-Path $skillPath)) { return }
  $text = Get-Content $skillPath -Raw
  if ($text -notmatch 'disable-model-invocation') {
    $text = $text -replace '(?m)(^description:.*\r?\n)', "`$1disable-model-invocation: true`n"
  }
  $name = $_.Name
  if ($text -notmatch '## References' -and $refs.ContainsKey($name)) {
    $links = ($refs[$name] | ForEach-Object { "- $_" }) -join "`n"
    $text = $text.TrimEnd() + "`n`n## References`n$links`n"
  }
  [System.IO.File]::WriteAllText($skillPath, $text)
}
Write-Host 'Playbooks updated.'
