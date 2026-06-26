$file = "combat\templates\combat\l1_correction.html"
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
$content = $content -replace [regex]::Escape('placeholder="â€""'), 'placeholder="—"'
$old = "setVal('id_atlet_hidden', opt.value);"
$new = "setVal('id_atlet_hidden', opt.value); setVal('display_kategori', kategori);"
$content = $content -replace [regex]::Escape($old), $new
[System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
Write-Host "DONE"
