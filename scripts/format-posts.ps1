param(
    [string]$ContentRoot = "content/post"
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$root = (Resolve-Path -LiteralPath $ContentRoot).Path
$files = Get-ChildItem -LiteralPath $root -Recurse -File -Filter "*.md" |
    Where-Object { $_.Name -ne "_index.md" -and $_.Name -ne "_index.pt-br.md" -and $_.Name -ne "index-old.md" }

$changed = 0
foreach ($file in $files) {
    $original = [System.IO.File]::ReadAllText($file.FullName)
    $newline = if ($original.Contains("`r`n")) { "`r`n" } else { "`n" }
    $lines = [System.Collections.Generic.List[string]]::new()
    $lines.AddRange([string[]]($original -split "\r?\n", 0, "RegexMatch"))

    $openingDelimiter = if ($lines.Count -gt 0) { $lines[0].Trim() } else { "" }
    if ($lines.Count -lt 3 -or ($openingDelimiter -ne "+++" -and $openingDelimiter -ne "---")) {
        throw "Expected TOML or YAML front matter: $($file.FullName)"
    }
    $delimiter = $openingDelimiter
    $isYaml = $delimiter -eq "---"

    $frontMatterEnd = -1
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq $delimiter) {
            $frontMatterEnd = $i
            break
        }
    }
    if ($frontMatterEnd -lt 0) {
        throw "Unclosed TOML front matter: $($file.FullName)"
    }

    $tocLine = -1
    for ($i = 1; $i -lt $frontMatterEnd; $i++) {
        if ($lines[$i] -match '^toc\s*[:=]') {
            $tocLine = $i
            break
        }
    }
    if ($tocLine -ge 0) {
        if ($isYaml) {
            $comment = if ($lines[$tocLine] -match '(\s+#.*)$') { $Matches[1] } else { "" }
            $lines[$tocLine] = "toc: true$comment"
        }
        else {
            $lines[$tocLine] = "toc = true"
        }
    }
    else {
        $lines.Insert($frontMatterEnd, $(if ($isYaml) { "toc: true" } else { "toc = true" }))
        $frontMatterEnd++
    }

    $headingLines = [System.Collections.Generic.List[int]]::new()
    $headingLevels = [System.Collections.Generic.List[int]]::new()
    $fence = $null
    for ($i = $frontMatterEnd + 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\s*(`{3,}|~{3,})') {
            $marker = $Matches[1][0]
            if ($null -eq $fence) {
                $fence = $marker
            }
            elseif ($marker -eq $fence) {
                $fence = $null
            }
            continue
        }
        if ($null -eq $fence -and $lines[$i] -match '^(#{1,6})([ \t]+)(.*)$') {
            $headingLines.Add($i)
            $headingLevels.Add($Matches[1].Length)
        }
    }

    if ($headingLevels.Count -gt 0) {
        $minimumLevel = ($headingLevels | Measure-Object -Minimum).Minimum
        $shift = 2 - $minimumLevel
        for ($j = 0; $j -lt $headingLines.Count; $j++) {
            $lineIndex = $headingLines[$j]
            if ($lines[$lineIndex] -notmatch '^(#{1,6})([ \t]+)(.*)$') {
                throw "Heading changed during formatting: $($file.FullName):$($lineIndex + 1)"
            }
            $newLevel = $Matches[1].Length + $shift
            if ($newLevel -lt 2 -or $newLevel -gt 6) {
                throw "Heading cannot be normalized safely: $($file.FullName):$($lineIndex + 1)"
            }
            $lines[$lineIndex] = ('#' * $newLevel) + $Matches[2] + $Matches[3]
        }
    }

    $formatted = [string]::Join($newline, $lines)
    if ($formatted -ne $original) {
        [System.IO.File]::WriteAllText($file.FullName, $formatted, $utf8NoBom)
        $changed++
    }
}

Write-Host "Formatted $changed of $($files.Count) post files."
