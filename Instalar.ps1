$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $env:LOCALAPPDATA "BomberDeJonny"
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\pety bombaman.lnk"
$shell = New-Object -ComObject WScript.Shell

if (Test-Path -LiteralPath $startup) {
    $existing = $shell.CreateShortcut($startup)
    $target = "$($existing.TargetPath) $($existing.Arguments)"
    if ($target -notlike "*BomberDeJonny*") {
        Write-Host "En este equipo ya hay un pety bombaman."
        Write-Host "No lo reemplazo. En otra laptop, este instalador si lo deja listo."
        exit 1
    }
}

$same = $false
if (Test-Path -LiteralPath $dest) {
    $same = ((Resolve-Path -LiteralPath $root).Path.TrimEnd("\") -eq (Resolve-Path -LiteralPath $dest).Path.TrimEnd("\"))
}
if (-not $same) {
    if (Test-Path -LiteralPath $dest) {
        Remove-Item -LiteralPath $dest -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    & robocopy $root $dest /E /XD __pycache__ /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
    if ($LASTEXITCODE -ge 8) {
        Write-Host "No pude copiar la carpeta."
        exit 1
    }
}

$lnk = $shell.CreateShortcut($startup)
$lnk.TargetPath = Join-Path $dest "python\pythonw.exe"
$lnk.Arguments = "`"$dest\pet.py`""
$lnk.WorkingDirectory = $dest
$lnk.WindowStyle = 7
$lnk.IconLocation = "$(Join-Path $dest 'pety.ico'),0"
$lnk.Description = "pety bombaman"
$lnk.Save()

Start-Process -FilePath (Join-Path $dest "python\pythonw.exe") -ArgumentList "`"$dest\pet.py`"" -WorkingDirectory $dest
Write-Host "Listo. pety bombaman arranca con Windows."
Write-Host $dest
