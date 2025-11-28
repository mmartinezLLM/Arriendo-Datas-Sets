# Script PowerShell para ejecutar 15 lotes en paralelo
# Cada lote en su propia ventana del terminal

$PythonExe = "C:/Users/Miguel Martinez SSD/OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS/Documentos/PROYECTOS/ARRIENDO DATA SETS/.venv/Scripts/python.exe"
$WorkDir = "c:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\scraper_inmobiliarias"

Write-Host "================================================================================"
Write-Host "EJECUTANDO 15 LOTES EN PARALELO"
Write-Host "================================================================================"
Write-Host "Inicio: $(Get-Date)"
Write-Host ""

# Array para guardar los procesos
$procesos = @()

# Lanzar los 15 lotes
for ($i = 1; $i -le 15; $i++) {
    $lote = [string]::Format("{0:D2}", $i)
    
    # Comando a ejecutar
    $cmd = "$PythonExe procesar_lote_limpio.py $i"
    
    # Crear nueva ventana PowerShell para cada lote
    $proceso = Start-Process PowerShell -ArgumentList "-NoExit -Command `"cd '$WorkDir'; $cmd`"" -PassThru
    
    $procesos += $proceso
    
    Write-Host "✓ Lote $lote iniciado (PID: $($proceso.Id))"
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Total de lotes iniciados: $($procesos.Count)/15"
Write-Host ""
Write-Host "Esperando a que terminen todos..."
Write-Host ""

# Esperar a que terminen todos
$procesos | ForEach-Object { $_.WaitForExit() }

Write-Host ""
Write-Host "================================================================================"
Write-Host "TODOS LOS LOTES HAN TERMINADO"
Write-Host "================================================================================"
Write-Host "Fin: $(Get-Date)"
Write-Host ""

# Mostrar resumen
Write-Host "Verificando resultados..."
Write-Host ""

$total_exitosas = 0
$total_fallidas = 0

for ($i = 1; $i -le 15; $i++) {
    $lote = [string]::Format("{0:D2}", $i)
    $loteDir = "resultados/lotes/lote_$lote"
    
    $jsonFiles = @(Get-ChildItem -Path $loteDir -Filter "lote_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending)
    
    if ($jsonFiles.Count -gt 0) {
        $latest = $jsonFiles[0]
        $content = Get-Content $latest -Raw | ConvertFrom-Json
        $count = $content.Count
        $exitosas = ($content | Where-Object { $_.'COD FR' } | Measure-Object).Count
        $fallidas = $count - $exitosas
        
        $total_exitosas += $exitosas
        $total_fallidas += $fallidas
        
        Write-Host "Lote $lote : $exitosas ✓ | $fallidas ✗ | Total: $count"
    } else {
        Write-Host "Lote $lote : Sin datos"
    }
}

Write-Host ""
Write-Host "================================================================================"
Write-Host "RESUMEN FINAL"
Write-Host "================================================================================"
Write-Host "Exitosas: $total_exitosas"
Write-Host "Fallidas: $total_fallidas"
Write-Host "Total: $($total_exitosas + $total_fallidas)"
Write-Host ""
