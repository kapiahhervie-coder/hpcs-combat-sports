$file = "combat\templates\combat\l2_strenght.html"
$c = [IO.File]::ReadAllText($file, [Text.Encoding]::UTF8)
$c = $c -replace 'cdn.jsdelivr.net/npm/chart.js', 'cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js'
$c = $c -replace "const ctx = document.getElementById\('radarChart'\).getContext\('2d'\);", "window.addEventListener('load',function(){`nconst ctx = document.getElementById('radarChart').getContext('2d');"
[IO.File]::WriteAllText($file, $c, [Text.Encoding]::UTF8)
Write-Host "DONE"
