$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoUrl = 'https://github.com/yanivmizrachiy/maagar.git'
$RepoDir = Join-Path $env:USERPROFILE 'maagar'
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'

Write-Host '=== Maagar automation suite install started ===' -ForegroundColor Cyan

$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User') + ';C:\Program Files\Git\cmd;C:\Program Files\nodejs'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host 'Installing Git...' -ForegroundColor Yellow
  winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
  $env:Path += ';C:\Program Files\Git\cmd'
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  Write-Host 'Installing Node.js LTS...' -ForegroundColor Yellow
  winget install --id OpenJS.NodeJS.LTS -e --source winget --accept-package-agreements --accept-source-agreements
  $env:Path += ';C:\Program Files\nodejs'
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is unavailable.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js is unavailable.' }

if (-not (Test-Path $RepoDir)) {
  git clone $RepoUrl $RepoDir
}

Set-Location $RepoDir
if (-not (Test-Path '.git')) { throw "Repo folder exists but is not a git repo: $RepoDir" }
git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) { throw 'Repo HEAD is invalid. Run maagar-local-reset.ps1 first.' }

git pull --ff-only

if (-not (Test-Path 'package.json')) {
  npm init -y | Out-Null
}
npm install --save-dev @playwright/test
npx playwright install chromium

$ExcludeFile = Join-Path $RepoDir '.git\info\exclude'
$ExcludeText = Get-Content $ExcludeFile -Raw -ErrorAction SilentlyContinue
if ($null -eq $ExcludeText) { $ExcludeText = '' }
foreach ($item in @('node_modules/','package.json','package-lock.json','playwright-report/','test-results/','_backup/')) {
  if ($ExcludeText -notmatch [regex]::Escape($item)) { Add-Content $ExcludeFile $item }
}

$ProfilePath = $PROFILE
$ProfileDir = Split-Path $ProfilePath -Parent
New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
if (Test-Path $ProfilePath) {
  Copy-Item $ProfilePath "$ProfilePath.bak_$Stamp" -Force
}

$SafeRepoDir = $RepoDir.Replace("'", "''")
$ProfileContent = @"
`$global:MAAGAR_REPO = '$SafeRepoDir'

function mgo { Set-Location `$global:MAAGAR_REPO }
function mrepo { Start-Process 'https://github.com/yanivmizrachiy/maagar' }
function mlive { Start-Process 'https://yanivmizrachiy.github.io/maagar/' }
function mactions { Start-Process 'https://github.com/yanivmizrachiy/maagar/actions' }
function msite { Start-Process 'http://127.0.0.1:5173/' }

function mhelp {
  Write-Host ''
  Write-Host 'Maagar PowerShell commands' -ForegroundColor Cyan
  Write-Host 'mgo        -> go to repo folder'
  Write-Host 'mopen      -> open repo folder'
  Write-Host 'mcode      -> open in VS Code when available'
  Write-Host 'mstatus    -> git status + branch'
  Write-Host 'mpull      -> pull latest from GitHub'
  Write-Host 'mcheck     -> syntax and shell validation'
  Write-Host 'mbuttons   -> button/action smoke test'
  Write-Host 'mtest      -> all local tests'
  Write-Host 'mserve     -> local site server'
  Write-Host 'mbackup    -> timestamp backup of key site files'
  Write-Host 'mclean     -> clean test reports'
  Write-Host 'mauto      -> pull + check + buttons + status'
  Write-Host 'mship msg  -> check + buttons + commit + push'
  Write-Host 'mrepo      -> open GitHub repo'
  Write-Host 'mactions   -> open GitHub Actions'
  Write-Host 'mlive      -> open live GitHub Pages site'
  Write-Host ''
}

function mopen {
  Set-Location `$global:MAAGAR_REPO
  Start-Process `$global:MAAGAR_REPO
}

function mcode {
  Set-Location `$global:MAAGAR_REPO
  if (Get-Command code -ErrorAction SilentlyContinue) { code . }
  else { Start-Process `$global:MAAGAR_REPO }
}

function mstatus {
  Set-Location `$global:MAAGAR_REPO
  git status --short
  git branch --show-current
}

function mpull {
  Set-Location `$global:MAAGAR_REPO
  git pull --ff-only
}

function mserve {
  Set-Location `$global:MAAGAR_REPO
  Start-Process 'http://127.0.0.1:5173/'
  npx --yes http-server . -p 5173 -c-1
}

function mclean {
  Set-Location `$global:MAAGAR_REPO
  Remove-Item -Recurse -Force .\playwright-report, .\test-results -ErrorAction SilentlyContinue
  Write-Host 'Cleaned reports.' -ForegroundColor Green
}

function mbackup {
  Set-Location `$global:MAAGAR_REPO
  `$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
  `$dest = Join-Path `$global:MAAGAR_REPO "_backup\`$stamp"
  New-Item -ItemType Directory -Path `$dest -Force | Out-Null
  foreach (`$p in @('index.html','assets','metadata','tests','playwright.config.js')) {
    if (Test-Path `$p) { Copy-Item `$p `$dest -Recurse -Force }
  }
  Write-Host "Backup created: `$dest" -ForegroundColor Green
}

function mcheck {
  Set-Location `$global:MAAGAR_REPO
  node --check assets/site.js
  node --check assets/site-url-state.js
  node --check assets/site-deeplink.js
  node --check assets/site-share.js
  node --check assets/site-modal-share.js
  node --check assets/site-help.js
  if (Get-Command py -ErrorAction SilentlyContinue) { py -3 scripts/validate-site-shell.py }
  elseif (Get-Command python -ErrorAction SilentlyContinue) { python scripts/validate-site-shell.py }
  else { Write-Host 'Python not found - skipped validate-site-shell.py' -ForegroundColor Yellow }
}

function mbuttons {
  Set-Location `$global:MAAGAR_REPO
  npx playwright test tests/site-buttons.spec.js
}

function mresp {
  Set-Location `$global:MAAGAR_REPO
  npx playwright test tests/site-responsive.spec.js
}

function ma11y {
  Set-Location `$global:MAAGAR_REPO
  npx playwright test tests/site-accessibility.spec.js
}

function mtest {
  Set-Location `$global:MAAGAR_REPO
  npx playwright test tests/site-buttons.spec.js tests/site-responsive.spec.js tests/site-accessibility.spec.js
}

function mauto {
  Set-Location `$global:MAAGAR_REPO
  mpull
  mcheck
  mbuttons
  mstatus
}

function mship {
  param([string]`$msg = 'update site')
  Set-Location `$global:MAAGAR_REPO
  mbackup
  mcheck
  mbuttons
  git add -A
  `$pending = git status --short
  if (-not `$pending) {
    Write-Host 'No changes to commit.' -ForegroundColor Yellow
    return
  }
  git commit -m `$msg
  git push
  mactions
  mlive
}

function mwatch {
  Set-Location `$global:MAAGAR_REPO
  Write-Host 'Watching assets, metadata and index.html. Press Ctrl+C to stop.' -ForegroundColor Cyan
  `$paths = @('index.html','assets','metadata','tests')
  while (`$true) {
    Start-Sleep -Seconds 10
    mcheck
  }
}

mhelp
"@

Set-Content -Path $ProfilePath -Value $ProfileContent -Encoding UTF8
. $ProfilePath

Write-Host '=== Maagar automation suite installed ===' -ForegroundColor Green
mstatus
mbuttons
