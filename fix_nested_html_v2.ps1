# Force console to read/write UTF-8 so em-dashes etc. display correctly
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

<#
.SYNOPSIS
    Restructure HPCS L1/L2 templates (taekwondo & muaythai) from the broken
    nested-HTML pattern into the same clean {% block extra_css %} / 
    {% block content %} pattern already used correctly in L3/L4.

.USAGE
    .\fix_nested_html_v2.ps1 -DryRun     # preview only
    .\fix_nested_html_v2.ps1             # apply (creates .bak backups)
#>

param(
    [switch]$DryRun
)

$root = "D:\LIBRERY\Phyton\HPCS Combat Sports"

$files = @(
    "$root\templates\taekwondo\l1_correction.html",
    "$root\templates\taekwondo\l2_strength.html",
    "$root\muaythai\templates\muaythai\l1_correction.html",
    "$root\muaythai\templates\muaythai\l2_strength.html"
)

function Read-LinesPreserveBom($path) {
    $bytes = [System.IO.File]::ReadAllBytes($path)
    $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
    $encoding = New-Object System.Text.UTF8Encoding($hasBom)
    $content = $encoding.GetString($bytes)
    $lines = $content -replace "`r`n", "`n" -split "`n"
    return @{ Lines = $lines; HasBom = $hasBom; Bytes = $bytes }
}

Write-Host ""
if ($DryRun) {
    Write-Host "=== DRY RUN (no files modified) ===" -ForegroundColor Yellow
} else {
    Write-Host "=== APPLYING FIX (backups saved as .bak) ===" -ForegroundColor Cyan
}
Write-Host ""

foreach ($file in $files) {

    if (-not (Test-Path $file)) {
        Write-Host "[SKIP] Not found: $file" -ForegroundColor DarkGray
        continue
    }

    $relative = $file.Replace($root, "")
    $data = Read-LinesPreserveBom $file
    $lines = $data.Lines

    # 1. Find the FIRST "{% block content %}" line
    $contentBlockIdx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq '{% block content %}') { $contentBlockIdx = $i; break }
    }
    if ($contentBlockIdx -eq -1) {
        Write-Host "[SKIP] $relative -- no '{% block content %}' found." -ForegroundColor DarkGray
        continue
    }

    # 2. Find DOCTYPE / html / head open+close / body open+close / html close
    $docTypeIdx = -1; $htmlOpenIdx = -1; $headOpenIdx = -1
    $headCloseIdx = -1; $bodyOpenIdx = -1; $bodyCloseIdx = -1; $htmlCloseIdx = -1

    for ($i = $contentBlockIdx + 1; $i -lt $lines.Count; $i++) {
        $t = $lines[$i].Trim()
        if ($docTypeIdx -eq -1 -and $t -match '^<!DOCTYPE\s+html>$') { $docTypeIdx = $i; continue }
        if ($htmlOpenIdx -eq -1 -and $t -match '^<html(\s[^>]*)?>$') { $htmlOpenIdx = $i; continue }
        if ($headOpenIdx -eq -1 -and $t -eq '<head>') { $headOpenIdx = $i; continue }
        if ($headOpenIdx -ne -1 -and $headCloseIdx -eq -1 -and $t -eq '</head>') { $headCloseIdx = $i; continue }
        if ($bodyOpenIdx -eq -1 -and $t -match '^<body(\s[^>]*)?>$') { $bodyOpenIdx = $i; continue }
        if ($t -match '^</body>$') { $bodyCloseIdx = $i }
        if ($t -match '^</html>') { $htmlCloseIdx = $i }
    }

    if ($docTypeIdx -eq -1 -or $headOpenIdx -eq -1) {
        Write-Host "[SKIP] $relative -- already clean (no nested DOCTYPE/head found)." -ForegroundColor DarkGray
        continue
    }

    # 3. Determine split point (where extra_css block ends / content block begins)
    $splitIdx = -1
    if ($headCloseIdx -ne -1) {
        $splitIdx = $headCloseIdx   # replace this line
    } else {
        # find first "</style>" line after headOpenIdx
        for ($i = $headOpenIdx + 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i].Trim() -eq '</style>') { $splitIdx = $i; break }
        }
    }
    if ($splitIdx -eq -1) {
        Write-Host "[SKIP] $relative -- could not find a safe split point. Needs manual review." -ForegroundColor Red
        continue
    }

    # 4. Build the new file
    $out = New-Object System.Collections.Generic.List[string]

    # everything before content block, unchanged
    for ($i = 0; $i -lt $contentBlockIdx; $i++) { $out.Add($lines[$i]) }

    # replace the block content line with block extra_css
    $out.Add('{% block extra_css %}')

    # lines between (docType/html/head) and split point, skipping the wrapper tags themselves
    for ($i = $headOpenIdx + 1; $i -lt $splitIdx; $i++) {
        $out.Add($lines[$i])
    }
    if ($headCloseIdx -ne -1) {
        # splitIdx is the </head> line itself -- include the </style> before it implicitly already added above
    } else {
        # splitIdx is a "</style>" line -- include it as the last line of CSS block
        $out.Add($lines[$splitIdx])
    }

    $out.Add('{% endblock %}')
    $out.Add('')
    $out.Add('{% block content %}')

    # figure out where real content resumes after split
    $resumeIdx = $splitIdx + 1
    if ($bodyOpenIdx -ne -1 -and $bodyOpenIdx -eq $resumeIdx) {
        $resumeIdx = $bodyOpenIdx + 1   # skip the standalone <body> line
    }

    # output the rest, skipping </body> and </html> (with any trailing junk) wherever they occur
    for ($i = $resumeIdx; $i -lt $lines.Count; $i++) {
        $t = $lines[$i].Trim()
        if ($t -match '^</body>$') { continue }
        if ($t -match '^</html>') { continue }
        $out.Add($lines[$i])
    }

    Write-Host "-- $relative --" -ForegroundColor White
    Write-Host "   DOCTYPE/html/head removed, split into extra_css + content blocks." -ForegroundColor Yellow
    Write-Host "   Original lines: $($lines.Count)  ->  New lines: $($out.Count)" -ForegroundColor Yellow

    if (-not $DryRun) {
        $backupPath = "$file.bak"
        [System.IO.File]::WriteAllBytes($backupPath, $data.Bytes)

        $newContent = [string]::Join("`r`n", $out)
        $outEncoding = New-Object System.Text.UTF8Encoding($data.HasBom)
        [System.IO.File]::WriteAllText($file, $newContent, $outEncoding)

        Write-Host "   Fixed. Backup: $backupPath" -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "=== Done ===" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "Dry run only. Re-run WITHOUT -DryRun to apply changes." -ForegroundColor Yellow
}
