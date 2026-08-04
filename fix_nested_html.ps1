<#
.SYNOPSIS
    Fix nested <!DOCTYPE>/<html>/<head>/<body> bug in HPCS Django child templates.

.DESCRIPTION
    Child templates that use {% extends "base_xxx.html" %} should NOT also
    contain their own <!DOCTYPE html>, <html>, <head>, <body> tags inside
    {% block content %}. Having two of these in one page causes browsers
    (especially mobile) to merge/mis-render the document, which is why the
    sidebar toggle button and layout break on taekwondo/muaythai pages.

    This script removes ONLY those wrapper tag lines. It never touches the
    <style>, <link>, <meta>, <script>, or any actual content — those stay
    exactly where they are, just no longer wrapped in a duplicate document.

.USAGE
    # Preview only, no files changed:
    .\fix_nested_html.ps1 -DryRun

    # Actually apply the fix (creates .bak backups automatically):
    .\fix_nested_html.ps1
#>

param(
    [switch]$DryRun
)

# ── Files to fix ──────────────────────────────────────────────────────────
# Adjust the root path below if your project folder is different.
$root = "D:\LIBRERY\Phyton\HPCS Combat Sports"

$files = @(
    "$root\templates\taekwondo\l1_correction.html",
    "$root\templates\taekwondo\l2_strength.html",
    "$root\templates\taekwondo\l3_power.html",
    "$root\templates\taekwondo\l4_speed_agility.html",
    "$root\muaythai\templates\muaythai\l1_correction.html",
    "$root\muaythai\templates\muaythai\l2_strength.html",
    "$root\muaythai\templates\muaythai\l3_power.html",
    "$root\muaythai\templates\muaythai\l4_speed_agility.html"
)

# ── Patterns for lines to strip (whole-line match only, after trimming) ───
$patternsToRemove = @(
    '^<!DOCTYPE\s+html>$',
    '^<html(\s[^>]*)?>$',
    '^</html>$',
    '^<head>$',
    '^</head>$',
    '^<body(\s[^>]*)?>$',
    '^</body>$'
)

Write-Host ""
if ($DryRun) {
    Write-Host "=== DRY RUN MODE — no files will be modified ===" -ForegroundColor Yellow
} else {
    Write-Host "=== APPLYING FIX — backups will be created as .bak ===" -ForegroundColor Cyan
}
Write-Host ""

foreach ($file in $files) {

    if (-not (Test-Path $file)) {
        Write-Host "[SKIP] Not found: $file" -ForegroundColor DarkGray
        continue
    }

    # Read raw bytes to detect/preserve UTF-8 BOM
    $bytes = [System.IO.File]::ReadAllBytes($file)
    $hasBom = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)

    $encoding = New-Object System.Text.UTF8Encoding($hasBom)
    $content = $encoding.GetString($bytes)

    # Normalize line endings for processing, split into lines
    $lines = $content -replace "`r`n", "`n" -split "`n"

    $keptLines = New-Object System.Collections.Generic.List[string]
    $removedLines = New-Object System.Collections.Generic.List[string]

    foreach ($line in $lines) {
        $trimmed = $line.Trim()
        $matched = $false
        foreach ($pattern in $patternsToRemove) {
            if ($trimmed -match $pattern) {
                $matched = $true
                break
            }
        }
        if ($matched) {
            $removedLines.Add($line)
        } else {
            $keptLines.Add($line)
        }
    }

    $relative = $file.Replace($root, "")
    Write-Host "── $relative ──" -ForegroundColor White

    if ($removedLines.Count -eq 0) {
        Write-Host "   No wrapper tags found (already clean, or structure differs). Skipped." -ForegroundColor DarkGray
        Write-Host ""
        continue
    }

    Write-Host "   Lines to remove ($($removedLines.Count)):" -ForegroundColor Yellow
    foreach ($rl in $removedLines) {
        Write-Host "     - $($rl.Trim())" -ForegroundColor DarkYellow
    }

    if (-not $DryRun) {
        # Backup original
        $backupPath = "$file.bak"
        [System.IO.File]::WriteAllBytes($backupPath, $bytes)

        # Rejoin kept lines with CRLF (Windows-friendly) and write back
        $newContent = [string]::Join("`r`n", $keptLines)
        $outEncoding = New-Object System.Text.UTF8Encoding($hasBom)
        [System.IO.File]::WriteAllText($file, $newContent, $outEncoding)

        Write-Host "   Fixed. Backup saved as: $backupPath" -ForegroundColor Green
    }

    Write-Host ""
}

Write-Host "=== Done ===" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "This was a dry run. Run again WITHOUT -DryRun to actually apply changes." -ForegroundColor Yellow
}
