$ErrorActionPreference = "Stop"
$dest = Join-Path $env:LOCALAPPDATA "BomberDeJonny"
$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\pety bombaman.lnk"

Get-CimInstance Win32_Process -Filter "Name = 'pythonw.exe'" | Where-Object {
    $_.CommandLine -like "*BomberDeJonny*"
} | ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    Write-Host "Cerre el portable $($_.ProcessId)"
}

if (Test-Path -LiteralPath $startup) {
    $shell = New-Object -ComObject WScript.Shell
    $existing = $shell.CreateShortcut($startup)
    $target = "$($existing.TargetPath) $($existing.Arguments)"
    if ($target -like "*BomberDeJonny*") {
        Remove-Item -LiteralPath $startup -Force
        Write-Host "Quite el inicio automatico del portable."
    } else {
        Write-Host "El acceso de inicio no es el portable. Lo dejo."
    }
}

if (Test-Path -LiteralPath $dest) {
    Remove-Item -LiteralPath $dest -Recurse -Force
    Write-Host "Quite la copia instalada."
} else {
    Write-Host "No habia una copia instalada."
}
Write-Host "Listo."
