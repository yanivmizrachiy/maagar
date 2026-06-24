$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$RepoUrl = 'https://github.com/yanivmizrachiy/maagar.git'
$RepoDir = Join-Path $env:USERPROFILE 'maagar'
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'

Write-Host '=== Maagar local reset started ===' -ForegroundColor Cyan

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

if (Test-Path $RepoDir) {
  $IsValidRepo = Test-Path (Join-Path $RepoDir '.git')
  if ($IsValidRepo) {
    Set-Location $RepoDir
    $HeadOk = $true
    git rev-parse --verify HEAD *> $null
    if ($LASTEXITCODE -ne 0) { $HeadOk = $false }
    if ($HeadOk) {
      Write-Host 'Existing repo is valid. Pulling updates...' -ForegroundColor Green
      git pull --ff-only
    } else {
      $BackupDir = Join-Path $env:USERPROFILE "maagar_broken_$Stamp"
      Rename-Item $RepoDir $BackupDir -Force
      Write-Host "Backed up broken repo to: $BackupDir" -ForegroundColor Yellow
      git clone $RepoUrl $RepoDir
    }
  } else {
    $BackupDir = Join-Path $env:USERPROFILE "maagar_broken_$Stamp"
    Rename-Item $RepoDir $BackupDir -Force
    Write-Host "Backed up non-git folder to: $BackupDir" -ForegroundColor Yellow
    git clone $RepoUrl $RepoDir
  }
} else {
  git clone $RepoUrl $RepoDir
}

Set-Location $RepoDir

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

$ProfileContent = @"
`$global:MAAGAR_REPO = '$RepoDir'

function mgo { Set-Location `$global:MAAGAR_REPO }

function mhelp {
  Write-Host 'פקודות מאגר: mgo | mstatus | mpull | mserve | msite | mbuttons | mresp | ma11y | mtest | mcheck | mpush "message" | mactions | mrepo | mlive' -ForegroundColor Cyan
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
  node --check assets/site-view-share.js
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
