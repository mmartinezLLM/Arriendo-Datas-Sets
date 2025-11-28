# Script PowerShell para ejecutar 20 lotes en paralelo
# Cada lote en su propia ventana de PowerShell visible

$totalLotes = 20

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INICIANDO 20 LOTES EN PARALELO" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cada lote se ejecutará en su propia ventana de PowerShell" -ForegroundColor Yellow
Write-Host ""

# Array para almacenar los procesos
$procesos = @()

# Iniciar cada lote
for ($i = 1; $i -le $totalLotes; $i++) {
    $loteNum = $i
    
    Write-Host "Iniciando Lote $loteNum..." -NoNewline
    
    # Comando a ejecutar
    $comando = "cd '$PWD'; python procesar_lote.py $loteNum; Read-Host 'Presiona Enter para cerrar'"
    
    # Iniciar proceso en nueva ventana visible
    $proceso = Start-Process powershell -ArgumentList "-NoExit", "-Command", $comando -PassThru
    
    $procesos += @{
        Numero = $loteNum
        PID = $proceso.Id
    }
    
    Write-Host " PID: $($proceso.Id)" -ForegroundColor Green
    
    # Pausa corta entre inicios
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "TODOS LOS $totalLotes LOTES INICIADOS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Procesos iniciados:" -ForegroundColor Yellow

foreach ($p in $procesos) {
    Write-Host "  Lote $($p.Numero): PID $($p.PID)"
}

Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "  - Cada lote tiene su propia ventana de PowerShell" -ForegroundColor White
Write-Host "  - Verás el progreso en cada ventana" -ForegroundColor White
Write-Host "  - Para detener un lote, cierra su ventana" -ForegroundColor White
Write-Host "  - Para ver el estado: python estado_lotes.py" -ForegroundColor White
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
