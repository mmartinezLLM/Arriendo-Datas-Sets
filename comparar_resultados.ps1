# Script para comparar progreso del scraper sin interrumpirlo
# Ejecuta esto cada vez que quieras ver el progreso

Write-Host "=== ANÁLISIS DE PROGRESO ===" -ForegroundColor Green
Write-Host ""

# Cambiar al directorio de resultados
cd"c:\Users\Miguel Martinez SSD\OneDrive - BROWSER TRAVEL SOLUTIONS S.A.S VIAJEMOS\Documentos\PROYECTOS\ARRIENDO DATA SETS\scraper_inmobiliarias\resultados"

# 1. RESULTADOS ANTERIORES (primera corrida con fallos)
Write-Host "1. PRIMERA CORRIDA (con fallos por sesión expirada):" -ForegroundColor Yellow
$anterior = Get-Content "extraction_emails_20251113_090139.json" | ConvertFrom-Json
$anteriorExitosos = ($anterior | Where-Object { $_.telefono -ne "No encontrado" }).Count
$anteriorFallidos = ($anterior | Where-Object { $_.telefono -eq "No encontrado" }).Count
Write-Host "   Total: $($anterior.Count)"
Write-Host "   Con teléfono: $anteriorExitosos ($(([math]::Round($anteriorExitosos/$anterior.Count*100, 1)))%)" -ForegroundColor Green
Write-Host "   Sin teléfono: $anteriorFallidos ($(([math]::Round($anteriorFallidos/$anterior.Count*100, 1)))%)" -ForegroundColor Red
Write-Host ""

# 2. ARCHIVO ACTUAL EN PROGRESO (recovery run)
Write-Host "2. CORRIDA DE RECUPERACIÓN (en progreso):" -ForegroundColor Yellow
$actual = Get-ChildItem extraction_emails_*.json | Where-Object { $_.Name -ne "extraction_emails_20251113_090139.json" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($actual) {
    $data = Get-Content $actual.FullName | ConvertFrom-Json
    $exitosos = ($data | Where-Object { $_.telefono -ne "No encontrado" }).Count
    $fallidos = ($data | Where-Object { $_.telefono -eq "No encontrado" }).Count
    
    Write-Host "   Archivo: $($actual.Name)"
    Write-Host "   Modificado: $($actual.LastWriteTime)"
    Write-Host "   Registros procesados: $($data.Count)"
    Write-Host "   Con teléfono: $exitosos ($(([math]::Round($exitosos/$data.Count*100, 1)))%)" -ForegroundColor Green
    Write-Host "   Sin teléfono: $fallidos ($(([math]::Round($fallidos/$data.Count*100, 1)))%)" -ForegroundColor Red
    Write-Host ""
    
    # Mostrar últimos 5 teléfonos extraídos
    Write-Host "   Últimos 5 teléfonos extraídos:" -ForegroundColor Cyan
    $data | Where-Object { $_.telefono -ne "No encontrado" } | Select-Object -Last 5 | ForEach-Object {
        Write-Host "     $($_.telefono)"
    }
    Write-Host ""
    
    # Calcular progreso estimado
    $indiceActual = $data.Count + 224  # Suma los 224 exitosos del inicio
    $porcentajeTotal = [math]::Round($indiceActual / 2439 * 100, 1)
    Write-Host "   PROGRESO TOTAL ESTIMADO: $indiceActual/2439 ($porcentajeTotal%)" -ForegroundColor Magenta
    
} else {
    Write-Host "   No se encontró archivo de recuperación aún" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== TELÉFONOS ÚNICOS EXTRAÍDOS ===" -ForegroundColor Green

# Combinar ambos archivos y contar únicos
$todosLosTelefonos = @()
$todosLosTelefonos += $anterior | Where-Object { $_.telefono -ne "No encontrado" } | Select-Object -ExpandProperty telefono

if ($actual) {
    $todosLosTelefonos += $data | Where-Object { $_.telefono -ne "No encontrado" } | Select-Object -ExpandProperty telefono
}

$telefonosUnicos = $todosLosTelefonos | Sort-Object -Unique
Write-Host "Total de teléfonos únicos extraídos: $($telefonosUnicos.Count)" -ForegroundColor Green
Write-Host ""

# Mostrar teléfonos más frecuentes
Write-Host "Teléfonos más frecuentes (Top 10):" -ForegroundColor Cyan
$todosLosTelefonos | Group-Object | Sort-Object Count -Descending | Select-Object -First 10 | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count) veces"
}
Write-Host ""

Write-Host "TIP: Ejecuta este script nuevamente para ver el progreso actualizado" -ForegroundColor Yellow
Write-Host "Comando: .\comparar_resultados.ps1" -ForegroundColor Gray
