# E2E Testing Suite - Sistema de Detección de Infracciones

## 🎯 Overview

Suite completa de testing End-to-End usando Playwright para validar todos los flujos de usuario del sistema de detección de infracciones de tránsito.

## 🧪 Cobertura de Tests

### 📊 Dashboard Navigation (`dashboard.spec.ts`)
- ✅ Carga del dashboard principal
- ✅ Navegación entre pestañas
- ✅ Visualización de métricas en tiempo real
- ✅ Indicador de estado de conexión

### 📋 Infractions Management (`infractions.spec.ts`)
- ✅ Visualización de tabla de infracciones
- ✅ Interacción con detalles de infracciones
- ✅ Filtrado por severidad
- ✅ Paginación
- ✅ Actualizaciones en tiempo real

### 📈 Analytics Dashboard (`analytics.spec.ts`)
- ✅ Visualización de gráficos de análisis
- ✅ Métricas de rendimiento
- ✅ Gráficos interactivos
- ✅ Datos en tiempo real

### 🗺️ Traffic Map (`traffic-map.spec.ts`)
- ✅ Visualización del mapa de tráfico
- ✅ Marcadores de ubicación
- ✅ Información contextual de ubicaciones
- ✅ Estados de marcadores (activo, inactivo, alerta)

### 🔄 System Integration (`integration.spec.ts`)
- ✅ Flujo completo de detección de infracciones
- ✅ Actualizaciones en tiempo real entre vistas
- ✅ Pruebas de rendimiento
- ✅ Compatibilidad móvil

## 🛠️ Setup e Instalación

### Prerrequisitos
- Node.js 18+
- npm o yarn
- Servicios del sistema ejecutándose:
  - Frontend (puerto 3000)
  - Backend Django (puerto 8000)
  - FastAPI Service (puerto 8001)

### Instalación Automática
```bash
# Ejecutar script de setup
./setup-testing.sh
```

### Instalación Manual
```bash
# Instalar dependencias
npm install

# Instalar navegadores
npx playwright install

# Configurar entorno
cp .env.example .env
```

## 🚀 Ejecución de Tests

### Comandos Básicos
```bash
# Ejecutar todos los tests
npm test

# Tests con interfaz visual
npm run test:headed

# Modo debug interactivo
npm run test:debug

# Interfaz web de Playwright
npm run test:ui

# Ver reporte HTML
npm run test:report
```

### Tests Específicos
```bash
# Solo tests del dashboard
npx playwright test dashboard

# Solo tests de infracciones
npx playwright test infractions

# Solo tests de analytics
npx playwright test analytics

# Solo tests de mapa
npx playwright test traffic-map

# Solo tests de integración
npx playwright test integration
```

### Tests por Navegador
```bash
# Solo Chrome
npx playwright test --project=chromium

# Solo Firefox
npx playwright test --project=firefox

# Solo Safari
npx playwright test --project=webkit

# Solo móviles
npx playwright test --project="Mobile Chrome"
```

## 📱 Configuración Multi-Browser

Los tests se ejecutan automáticamente en:
- **Desktop**: Chrome, Firefox, Safari
- **Mobile**: Chrome móvil, Safari móvil
- **Tablets**: iPad, Android tablet

### Configuración de Viewport
```typescript
// Desktop
{ width: 1920, height: 1080 }

// Mobile
{ width: 375, height: 667 }

// Tablet
{ width: 768, height: 1024 }
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# URLs de servicios
BASE_URL=http://localhost:3000          # Frontend
DJANGO_URL=http://localhost:8000        # Backend Django
FASTAPI_URL=http://localhost:8001       # FastAPI Service

# Base de datos de test
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=traffic_system_test

# Configuración de tests
HEADED=false                            # Mostrar navegador
CI=false                                # Modo CI
SLOWMO=0                               # Ralentizar acciones (ms)
```

### Configuración de Timeout
```typescript
// Test timeout: 30 segundos
timeout: 30 * 1000

// Expect timeout: 5 segundos
expect: { timeout: 5000 }

// Action timeout: 10 segundos
actionTimeout: 10000

// Navigation timeout: 30 segundos
navigationTimeout: 30000
```

## 📊 Reportes y Resultados

### Tipos de Reportes
- **HTML Report**: Interfaz web interactiva
- **JSON Report**: Datos estructurados para CI/CD
- **JUnit XML**: Compatibilidad con sistemas CI

### Ubicación de Reportes
```
tests/
├── test-results/           # Resultados de ejecución
│   ├── results.json       # Reporte JSON
│   └── results.xml        # Reporte JUnit
├── playwright-report/     # Reporte HTML
└── test-results-*/        # Screenshots y videos de fallos
```

### Artifacts de Debug
- **Screenshots**: Capturas en fallos
- **Videos**: Grabación de tests fallidos
- **Traces**: Archivos de traza para debugging

## 🔍 Debugging y Troubleshooting

### Modo Debug
```bash
# Debug interactivo
npx playwright test --debug

# Debug test específico
npx playwright test dashboard.spec.ts --debug

# Debug con breakpoints
npx playwright test --headed --slowmo=1000
```

### Visualización de Tests
```bash
# Interfaz visual de Playwright
npx playwright test --ui

# Ver trace de un test específico
npx playwright show-trace test-results/trace.zip
```

### Logs y Diagnósticos
```bash
# Logs detallados
DEBUG=pw:api npx playwright test

# Logs de red
DEBUG=pw:api,pw:network npx playwright test

# Screenshot en cada paso
npx playwright test --screenshot=on
```

## 🏗️ Estructura de Tests

### Page Object Model
```typescript
// pages/DashboardPage.ts
export class DashboardPage {
  constructor(private page: Page) {}
  
  async navigateToInfractions() {
    await this.page.click('text=Infracciones');
  }
  
  async getMetricsCount() {
    return this.page.locator('[data-testid="metrics-count"]').textContent();
  }
}
```

### Test Utilities
```typescript
// utils/testHelpers.ts
export async function waitForChartToLoad(page: Page) {
  await page.waitForSelector('svg');
  await page.waitForTimeout(1000); // Tiempo para animaciones
}

export async function mockWebSocketConnection(page: Page) {
  await page.route('ws://localhost:*', route => route.fulfill());
}
```

## 🚦 CI/CD Integration

### GitHub Actions
```yaml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:ci
```

### Docker Testing
```bash
# Ejecutar tests en Docker
npm run test:docker

# Ver logs de contenedores
docker-compose -f docker-compose.test.yml logs
```

## 📈 Métricas de Testing

### Coverage Goals
- **Functional Coverage**: 100% de flujos críticos
- **Browser Coverage**: Chrome, Firefox, Safari
- **Device Coverage**: Desktop, Tablet, Mobile
- **Performance**: < 5s carga inicial, < 2s navegación

### KPIs de Testing
- ✅ Tests de regresión: 100% de flujos principales
- ✅ Tests de smoke: 95% éxito en CI
- ✅ Tests de performance: < 10s ejecución total
- ✅ Tests de compatibilidad: 3 navegadores principales

## 🤝 Contribución

### Agregar Nuevos Tests
1. Crear archivo `.spec.ts` en `/e2e/`
2. Seguir patrón de naming: `feature.spec.ts`
3. Incluir `test.describe()` para agrupación
4. Usar `data-testid` para selectores estables
5. Agregar documentación en este README

### Buenas Prácticas
- **Selectores estables**: Usar `data-testid` preferiblemente
- **Tests independientes**: Cada test debe poder ejecutarse solo
- **Assertions claras**: Usar `expect` con mensajes descriptivos
- **Timeouts apropiados**: No usar `waitForTimeout` excepto cuando sea necesario
- **Cleanup**: Limpiar estado entre tests

## 🐛 Issues Conocidos

### Limitaciones Actuales
- Tests requieren servicios ejecutándose manualmente
- WebSocket mocking pendiente de implementación
- Performance tests básicos (no load testing)
- Falta integración con base de datos real

### Próximas Mejoras
- [ ] Auto-start de servicios en tests
- [ ] Mocking avanzado de APIs
- [ ] Tests de carga con Artillery
- [ ] Visual regression testing
- [ ] Tests de accesibilidad

---

**Versión**: 1.0.0  
**Última Actualización**: 2025-01-01  
**Maintainer**: Equipo QA