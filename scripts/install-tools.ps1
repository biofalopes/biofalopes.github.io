# Install project-local Windows x64 tools without modifying the system PATH.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$toolsRoot = Join-Path $projectRoot '.tools'
$checksums = Get-Content -Raw (Join-Path $PSScriptRoot 'tool-checksums.json') | ConvertFrom-Json
$hugoVersion = (Get-Content -Raw (Join-Path $projectRoot '.hugo-version')).Trim()
$sassVersion = (Get-Content -Raw (Join-Path $projectRoot '.sass-version')).Trim()
$goVersion = (Get-Content -Raw (Join-Path $projectRoot '.go-version')).Trim()
New-Item -ItemType Directory -Force -Path $toolsRoot | Out-Null

function Expand-VerifiedTool($Url, $Hash, $Name, $Destination) {
    if (-not $Hash) { throw "No trusted checksum recorded for $Name" }
    $archive = Join-Path $toolsRoot "$Name.zip"
    Invoke-WebRequest -UseBasicParsing -Uri $Url -OutFile $archive -TimeoutSec 120
    $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $Hash) { throw "Checksum mismatch for $Name" }
    Expand-Archive -LiteralPath $archive -DestinationPath $Destination -Force
    Remove-Item -LiteralPath $archive
}

Expand-VerifiedTool "https://github.com/gohugoio/hugo/releases/download/v$hugoVersion/hugo_extended_${hugoVersion}_windows-amd64.zip" $checksums.hugo.$hugoVersion.'windows-amd64' 'hugo' (Join-Path $toolsRoot 'hugo')
Expand-VerifiedTool "https://github.com/sass/dart-sass/releases/download/$sassVersion/dart-sass-${sassVersion}-windows-x64.zip" $checksums.sass.$sassVersion.'windows-x64' 'sass' $toolsRoot

# This is the same official distribution used by actions/setup-go.
$goReleaseTag = $checksums.go.$goVersion.releaseTag
if (-not $goReleaseTag) { throw "No distribution tag recorded for Go $goVersion" }
$goUrl = "https://github.com/actions/go-versions/releases/download/$goReleaseTag/go-$goVersion-win32-x64.zip"
Expand-VerifiedTool $goUrl $checksums.go.$goVersion.'windows-x64' 'go' (Join-Path $toolsRoot 'go')

& (Join-Path $toolsRoot 'hugo/hugo.exe') version
& (Join-Path $toolsRoot 'dart-sass/sass.bat') --version
& (Join-Path $toolsRoot 'go/bin/go.exe') version
Write-Host 'Tools ready. Start the blog with: .\scripts\blog.ps1 serve'
