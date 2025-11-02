import { test, expect } from '@playwright/test';

test.describe('Dashboard Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load dashboard homepage', async ({ page }) => {
    // Verificar que el título sea correcto
    await expect(page).toHaveTitle(/Sistema de Detección de Infracciones/);
    
    // Verificar que el header esté presente
    await expect(page.locator('h1')).toContainText('Dashboard de Monitoreo');
    
    // Verificar que la sidebar esté presente
    await expect(page.locator('text=Traffic Monitor')).toBeVisible();
  });

  test('should navigate between tabs', async ({ page }) => {
    // Verificar navegación a Infracciones
    await page.click('text=Infracciones');
    await expect(page.locator('h2')).toContainText('Gestión de Infracciones');
    
    // Verificar navegación a Análisis
    await page.click('text=Análisis');
    await expect(page.locator('h2')).toContainText('Análisis y Reportes');
    
    // Verificar navegación a Mapa
    await page.click('text=Mapa');
    await expect(page.locator('h2')).toContainText('Mapa de Tráfico');
    
    // Volver a Vista General
    await page.click('text=Vista General');
    await expect(page.locator('h1')).toContainText('Dashboard de Monitoreo');
  });

  test('should display real-time metrics', async ({ page }) => {
    // Verificar que las métricas estén visibles
    await expect(page.locator('text=Cámaras Activas')).toBeVisible();
    await expect(page.locator('text=Infracciones Hoy')).toBeVisible();
    await expect(page.locator('text=Tiempo Promedio')).toBeVisible();
    await expect(page.locator('text=Vehículos Detectados')).toBeVisible();
    
    // Verificar que los números sean válidos
    const camerasValue = page.locator('[data-testid="cameras-value"]');
    await expect(camerasValue).toHaveText(/\d+/);
  });

  test('should show connection status', async ({ page }) => {
    // Verificar indicador de conexión
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    await expect(connectionStatus).toBeVisible();
    
    // Verificar que muestre "Conectado" o "Desconectado"
    await expect(connectionStatus).toHaveText(/(Conectado|Desconectado)/);
  });
});