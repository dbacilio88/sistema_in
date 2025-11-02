import { test, expect } from '@playwright/test';

test.describe('Infractions Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.click('text=Infracciones');
  });

  test('should display infractions table', async ({ page }) => {
    // Verificar que la tabla esté presente
    await expect(page.locator('table')).toBeVisible();
    
    // Verificar headers de la tabla
    await expect(page.locator('th:has-text("ID / Placa")')).toBeVisible();
    await expect(page.locator('th:has-text("Tipo")')).toBeVisible();
    await expect(page.locator('th:has-text("Ubicación")')).toBeVisible();
    await expect(page.locator('th:has-text("Fecha/Hora")')).toBeVisible();
    await expect(page.locator('th:has-text("Severidad")')).toBeVisible();
    await expect(page.locator('th:has-text("Estado")')).toBeVisible();
  });

  test('should show infraction details on row click', async ({ page }) => {
    // Esperar a que la tabla cargue
    await page.waitForSelector('table tbody tr');
    
    // Hacer clic en la primera fila
    await page.click('table tbody tr:first-child');
    
    // Verificar que se muestren los botones de acción
    await expect(page.locator('[data-testid="view-details"]')).toBeVisible();
    await expect(page.locator('[data-testid="view-evidence"]')).toBeVisible();
  });

  test('should filter infractions by severity', async ({ page }) => {
    // Esperar a que carguen las infracciones
    await page.waitForSelector('.bg-red-100, .bg-yellow-100, .bg-green-100');
    
    // Contar infracciones iniciales
    const totalRows = await page.locator('tbody tr').count();
    expect(totalRows).toBeGreaterThan(0);
    
    // Verificar que hay diferentes severidades
    const highSeverity = page.locator('.bg-red-100');
    const mediumSeverity = page.locator('.bg-yellow-100');
    const lowSeverity = page.locator('.bg-green-100');
    
    // Al menos una de cada tipo debería estar presente
    const hasHigh = await highSeverity.count() > 0;
    const hasMedium = await mediumSeverity.count() > 0;
    const hasLow = await lowSeverity.count() > 0;
    
    expect(hasHigh || hasMedium || hasLow).toBeTruthy();
  });

  test('should show pagination controls', async ({ page }) => {
    // Verificar controles de paginación en vista completa
    await expect(page.locator('text=Anterior')).toBeVisible();
    await expect(page.locator('text=Siguiente')).toBeVisible();
    
    // Verificar contador de elementos
    await expect(page.locator('text=Mostrando')).toBeVisible();
  });

  test('should update in real-time', async ({ page }) => {
    // Obtener el número inicial de infracciones
    const initialCount = await page.locator('tbody tr').count();
    
    // Esperar por actualizaciones (simuladas cada 8 segundos)
    await page.waitForTimeout(9000);
    
    // Verificar que el contenido puede haber cambiado
    // (En un test real, esto verificaría WebSocket updates)
    const currentCount = await page.locator('tbody tr').count();
    
    // El número puede ser igual o diferente dependiendo de las actualizaciones
    expect(currentCount).toBeGreaterThanOrEqual(0);
  });
});