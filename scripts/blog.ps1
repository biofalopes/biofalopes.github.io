[CmdletBinding()]
param(
    [ValidateSet('serve', 'build', 'check')]
    [string]$Action = 'serve'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$toolsRoot = Join-Path $projectRoot '.tools'
$hugo = Join-Path $toolsRoot 'hugo/hugo.exe'
if (-not (Test-Path -LiteralPath $hugo)) {
    throw 'Run .\scripts\install-tools.ps1 first.'
}
$env:PATH = (Join-Path $toolsRoot 'go/bin') + ';' + (Join-Path $toolsRoot 'dart-sass') + ';' + $env:PATH
$env:GOENV = 'off'
$env:GOMODCACHE = Join-Path $toolsRoot 'gomod'
$env:GOCACHE = Join-Path $toolsRoot 'gocache'
$env:HUGO_CACHEDIR = Join-Path $toolsRoot 'hugocache'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:HUGO_BIN = $hugo
Push-Location $projectRoot
try {
    if ($Action -eq 'serve') {
        & $hugo server --environment development --buildDrafts --disableFastRender --destination (Join-Path $toolsRoot 'preview')
    } else {
        if ($Action -eq 'check') {
            & python -m unittest discover -s tests -v
            if ($LASTEXITCODE -ne 0) { throw 'Article example tests failed.' }
        }
        & $hugo --environment production --gc --minify --cleanDestinationDir --printPathWarnings --panicOnWarning
        if ($LASTEXITCODE -ne 0) { throw 'Hugo build failed.' }
        if ($Action -eq 'check') {
            & python scripts/check-site.py public
            if ($LASTEXITCODE -ne 0) { throw 'Generated site checks failed.' }
        }
    }
} finally {
    Pop-Location
}
