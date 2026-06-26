$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoUrl = 'https://github.com/yanivmizrachiy/maagar.git'
$HomeDir = $env:USERPROFILE
$PreferredRepoDir = Join-Path $HomeDir 'maagar'
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'

Write-Host '=== Maagar local reset started ===' -ForegroundColor Cyan

Set-Location $HomeDir

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

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Git is still unavailable. Restart PowerShell and run this again.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node.js is still unavailable. Restart PowerShell and run this again.' }

function Test-MaagarRepoOk([string]$Path) {
  if (-not (Test-Path (Join-Path $Path '.git'))) { return $false }
  git -C $Path rev-parse --verify HEAD *> $null
  if ($LASTEXITCODE -ne 0) { return $false }
  if (-not (Test-Path (Join-Path $Path 'tests\site-buttons.spec.js'))) { return $false }
  return $true
}

$RepoDir = $PreferredRepoDir

if (Test-MaagarRepoOk $PreferredRepoDir) {
  Write-Host 'Existing repo is valid. Pulling updates...' -ForegroundColor Green
  git -C $PreferredRepoDir pull --ff-only
} else {
  if (Test-Path $PreferredRepoDir) {
    $BackupDir = Join-Path $HomeDir "maagar_broken_$Stamp"
    try {
      Set-Location $HomeDir
      Rename-Item $PreferredRepoDir $BackupDir -Force
      Write-Host "Backed up broken maagar folder to: $BackupDir" -ForegroundColor Yellow
      $RepoDir = $PreferredRepoDir
    } catch {
      Write-Host 'Could not rename the broken maagar folder because it is in use.' -ForegroundColor Yellow
      $RepoDir = Join-Path $HomeDir "maagar_clean_$Stamp"
      Write-Host "Using clean repo folder instead: $RepoDir" -ForegroundColor Yellow
    }
  }
  git clone $RepoUrl $RepoDir
}

Set-Location $RepoDir

if (-not (Test-Path '.git')) { throw 'Clone failed: .git folder is missing.' }
if (-not (Test-Path 'tests\site-buttons.spec.js')) { throw 'Clone failed: tests/site-buttons.spec.js is missing.' }

git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) { throw 'Clone failed: HEAD is not valid.' }

if (-not (Test-Path 'package.json')) {
  npm init -y
}

npm install --save-dev @playwright/test
npx playwright install chromium

$ExcludeFile = Join-Path $RepoDir '.git\info\exclude'
$ExcludeText = Get-Content $ExcludeFile -Raw -ErrorAction SilentlyContinue
if ($null -eq $ExcludeText) { $ExcludeText = '' }
foreach ($item in @('node_modules/','package.json','package-lock.json','playwright-report/','test-results/')) {
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

function mhelp {
  Write-Host 'Maagar commands: mgo | mstatus | mpull | mserve | msite | mbuttons | mresp | ma11y | mtest | mcheck | mpush "message" | mactions | mrepo | mlive' -ForegroundColor Cyan
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

function msite { Start-Process 'http://127.0.0.1:5173/' }

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

function mpush {
  param([string]`$msg = 'update site')
  Set-Location `$global:MAAGAR_REPO
  git add -A
  git commit -m `$msg
  git push
}

function mactions { Start-Process 'https://github.com/yanivmizrachiy/maagar/actions' }
function mrepo { Start-Process 'https://github.com/yanivmizrachiy/maagar' }
function mlive { Start-Process 'https://yanivmizrachiy.github.io/maagar/' }
"@

Set-Content -Path $ProfilePath -Value $ProfileContent -Encoding UTF8
. $ProfilePath

Write-Host '=== Maagar local reset finished ===' -ForegroundColor Green
mhelp
mstatus
Write-Host 'Running button test...' -ForegroundColor Cyan
mbuttons
