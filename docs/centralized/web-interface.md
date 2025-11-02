# Manual de Usuario - Interfaz Web

## Introducción

El Sistema de Detección de Infracciones de Tráfico proporciona una interfaz web intuitiva para gestionar y monitorear infracciones de tráfico en tiempo real. Este manual te guiará a través de todas las funcionalidades disponibles.

## Acceso al Sistema

### URL de Acceso
- **Producción**: `https://traffic-system.yourdomain.com`
- **Staging**: `https://staging.traffic-system.yourdomain.com`

### Inicio de Sesión

1. **Acceder a la página de login**
   - Abrir navegador web
   - Navegar a la URL del sistema
   - Aparecerá la pantalla de inicio de sesión

2. **Credenciales de acceso**
   ```
   Campo: Usuario
   Descripción: Tu nombre de usuario asignado
   
   Campo: Contraseña
   Descripción: Tu contraseña personal
   ```

3. **Proceso de autenticación**
   - Introducir credenciales
   - Hacer clic en "Iniciar Sesión"
   - El sistema validará y redirigirá al dashboard principal

### Recuperación de Contraseña

1. **Hacer clic en "¿Olvidaste tu contraseña?"**
2. **Introducir email registrado**
3. **Revisar email de recuperación**
4. **Seguir instrucciones del email**
5. **Establecer nueva contraseña**

## Dashboard Principal

### Vista General

El dashboard principal muestra:

```
┌─────────────────────────────────────────────────────────┐
│  🚦 Sistema de Detección de Infracciones de Tráfico    │
├─────────────────────────────────────────────────────────┤
│  📊 Métricas del Día        │  🔔 Alertas Recientes     │
│  • Infracciones: 45         │  • Cámara Av. Principal   │
│  • Confirmadas: 38          │    offline hace 2 min     │
│  • Pendientes: 7            │  • High CPU en ML Service │
│  • Precisión: 94%           │    hace 5 min             │
├─────────────────────────────────────────────────────────┤
│  📈 Gráfico de Infracciones │  🗺️ Mapa de Detecciones  │
│  [Gráfico de barras]        │  [Mapa interactivo]       │
└─────────────────────────────────────────────────────────┘
```

### Widgets Principales

#### 1. Métricas del Día
- **Infracciones Detectadas**: Total del día actual
- **Confirmadas**: Infracciones validadas
- **Pendientes**: Esperando revisión
- **Precisión**: % de detecciones correctas

#### 2. Alertas del Sistema
- **Estado de cámaras**: Online/Offline
- **Performance del sistema**: CPU, memoria, etc.
- **Errores críticos**: Fallos que requieren atención

#### 3. Gráfico de Tendencias
- **Vista temporal**: Últimas 24 horas, 7 días, 30 días
- **Tipos de infracción**: Desglose por categorías
- **Comparación**: Periodos anteriores

#### 4. Mapa de Detecciones
- **Ubicaciones en tiempo real**: Puntos de detección
- **Heat map**: Zonas con más infracciones
- **Estado de cámaras**: Visual en el mapa

## Gestión de Infracciones

### Lista de Infracciones

#### Acceso
```
Menú Principal → Infracciones → Lista de Infracciones
```

#### Filtros Disponibles

1. **Por Estado**
   - Pendiente: Esperando validación
   - Confirmada: Validada como infracción real
   - Desestimada: No es una infracción válida
   - Pagada: Multa pagada

2. **Por Tipo**
   - Exceso de velocidad
   - Semáforo en rojo
   - Estacionamiento prohibido
   - Línea continua
   - Otros

3. **Por Fecha**
   - Hoy
   - Última semana
   - Último mes
   - Rango personalizado

4. **Por Ubicación**
   - Selección en mapa
   - Lista de direcciones
   - Por zona/distrito

#### Búsqueda Avanzada

```
┌─────────────────────────────────────────┐
│ Búsqueda Avanzada                       │
├─────────────────────────────────────────┤
│ Placa: [ABC123        ] 🔍              │
│ Fecha desde: [01/01/2024] hasta: [hoy] │
│ Tipo: [Todos ▼]                         │
│ Estado: [Todos ▼]                       │
│ Ubicación: [Todas las zonas ▼]         │
│                                         │
│ [ Buscar ] [ Limpiar ]                  │
└─────────────────────────────────────────┘
```

### Detalle de Infracción

#### Información General
```
┌─────────────────────────────────────────┐
│ Infracción #12345                       │
├─────────────────────────────────────────┤
│ Fecha: 15/01/2024 14:30:15             │
│ Tipo: Exceso de velocidad               │
│ Ubicación: Av. Javier Prado 1245       │
│ Estado: Pendiente                       │
│ Confianza: 95%                          │
└─────────────────────────────────────────┘
```

#### Datos del Vehículo
```
┌─────────────────────────────────────────┐
│ Vehículo                                │
├─────────────────────────────────────────┤
│ Placa: ABC-123                          │
│ Marca: Toyota                           │
│ Modelo: Corolla                         │
│ Color: Blanco                           │
│ Propietario: Juan Pérez                 │
└─────────────────────────────────────────┘
```

#### Evidencia
```
┌─────────────────────────────────────────┐
│ Evidencia                               │
├─────────────────────────────────────────┤
│ [🖼️ Imagen 1] [🖼️ Imagen 2]            │
│ [🎥 Video]                              │
│                                         │
│ Velocidad detectada: 85 km/h            │
│ Límite de velocidad: 60 km/h            │
│ Método: Radar láser                     │
└─────────────────────────────────────────┘
```

### Acciones sobre Infracciones

#### Confirmar Infracción
1. **Revisar evidencia cuidadosamente**
2. **Verificar datos del vehículo**
3. **Hacer clic en "Confirmar"**
4. **Agregar comentarios si es necesario**
5. **Establecer monto de multa**

#### Desestimar Infracción
1. **Seleccionar motivo de desestimación**
   - Falso positivo
   - Evidencia insuficiente
   - Error en detección
   - Vehículo autorizado

2. **Agregar comentarios explicativos**
3. **Hacer clic en "Desestimar"**

#### Editar Información
- **Datos del vehículo**: Si hay errores
- **Ubicación**: Ajustar coordenadas
- **Tipo de infracción**: Corrección si es necesario
- **Monto de multa**: Según regulaciones

## Gestión de Vehículos

### Registro de Vehículos

#### Nuevo Vehículo
```
┌─────────────────────────────────────────┐
│ Registrar Nuevo Vehículo                │
├─────────────────────────────────────────┤
│ Placa: [ABC-123      ]                  │
│ Marca: [Toyota ▼]                       │
│ Modelo: [Corolla     ]                  │
│ Año: [2020    ]                         │
│ Color: [Blanco ▼]                       │
│ Tipo: [Automóvil ▼]                     │
│                                         │
│ Propietario:                            │
│ Nombre: [Juan Pérez                ]    │
│ DNI: [12345678    ]                     │
│ Teléfono: [987654321    ]               │
│ Email: [juan@email.com      ]           │
│                                         │
│ [ Guardar ] [ Cancelar ]                │
└─────────────────────────────────────────┘
```

#### Campos Obligatorios
- ✅ Placa vehicular
- ✅ Marca
- ✅ Modelo
- ✅ Año
- ✅ Nombre del propietario
- ✅ Documento de identidad

#### Validaciones Automáticas
- **Formato de placa**: Según estándares del país
- **Duplicados**: Verifica si ya existe
- **Año válido**: Entre 1990 y año actual
- **Documento**: Formato correcto

### Búsqueda de Vehículos

#### Búsqueda Simple
```
┌─────────────────────────────────────────┐
│ 🔍 [Buscar por placa o propietario] 🔍  │
└─────────────────────────────────────────┘
```

#### Búsqueda Avanzada
- **Por placa**: Búsqueda exacta o parcial
- **Por propietario**: Nombre o documento
- **Por marca/modelo**: Filtros combinados
- **Por estado**: Activo, suspendido, etc.

### Historial de Vehículo

#### Vista de Infracciones
```
┌─────────────────────────────────────────┐
│ Historial - Vehículo ABC-123            │
├─────────────────────────────────────────┤
│ 📅 15/01/2024 │ Exceso velocidad │ $150 │
│ 📅 10/01/2024 │ Semáforo rojo   │ $200 │
│ 📅 05/01/2024 │ Estacionamiento │ $80  │
├─────────────────────────────────────────┤
│ Total multas: $430                      │
│ Infracciones pendientes: 2              │
│ Estado: Activo                          │
└─────────────────────────────────────────┘
```

## Monitoreo en Tiempo Real

### Vista de Cámaras

#### Mapa de Cámaras
```
┌─────────────────────────────────────────┐
│ 🗺️ Mapa de Cámaras                     │
├─────────────────────────────────────────┤
│    🟢 Cámara Online                     │
│    🔴 Cámara Offline                    │
│    🟡 Cámara con Problemas              │
│                                         │
│ [Filtros: Todas ▼] [Actualizar]        │
└─────────────────────────────────────────┘
```

#### Lista de Cámaras
- **Estado actual**: Online/Offline
- **Última actividad**: Timestamp
- **Detecciones hoy**: Contador
- **Calidad de imagen**: Porcentaje
- **Acciones**: Ver stream, configurar, etc.

### Stream en Vivo

#### Visualización
```
┌─────────────────────────────────────────┐
│ 🎥 Cámara Av. Principal - EN VIVO       │
├─────────────────────────────────────────┤
│                                         │
│     [Video Stream en Tiempo Real]      │
│                                         │
├─────────────────────────────────────────┤
│ 🔴 REC  │ 📸 Captura │ ⚙️ Config        │
└─────────────────────────────────────────┘
```

#### Controles Disponibles
- **Pausar/Reproducir**: Control del stream
- **Captura de pantalla**: Guardar frame actual
- **Zoom**: Acercar/Alejar
- **Calidad**: Ajustar resolución

### Notificaciones en Tiempo Real

#### Panel de Notificaciones
```
┌─────────────────────────────────────────┐
│ 🔔 Notificaciones (3 nuevas)           │
├─────────────────────────────────────────┤
│ 🚨 14:35 - Nueva infracción detectada   │
│     Placa ABC-123 │ Exceso velocidad    │
│                                         │
│ ⚠️ 14:32 - Cámara desconectada          │
│     Av. Principal │ Verificar conexión  │
│                                         │
│ ℹ️ 14:30 - Sistema actualizado          │
│     Versión 1.2.3 │ Mejoras ML          │
└─────────────────────────────────────────┘
```

#### Tipos de Notificaciones
- 🚨 **Críticas**: Nuevas infracciones
- ⚠️ **Advertencias**: Problemas de sistema
- ℹ️ **Informativas**: Actualizaciones, tips

## Reportes

### Generación de Reportes

#### Tipos Disponibles
1. **Reporte de Infracciones**
   - Por período
   - Por tipo
   - Por ubicación
   - Por estado

2. **Reporte de Vehículos**
   - Más infractores
   - Por zona de residencia
   - Historial completo

3. **Reporte de Performance**
   - Precisión del sistema
   - Tiempo de respuesta
   - Disponibilidad de cámaras

4. **Reporte Financiero**
   - Ingresos por multas
   - Multas pendientes
   - Proyecciones

#### Configuración de Reporte
```
┌─────────────────────────────────────────┐
│ Generar Reporte                         │
├─────────────────────────────────────────┤
│ Tipo: [Infracciones ▼]                  │
│ Período:                                │
│   ○ Última semana                       │
│   ○ Último mes                          │
│   ● Personalizado                       │
│     Desde: [01/01/2024]                 │
│     Hasta: [31/01/2024]                 │
│                                         │
│ Formato:                                │
│   ☑️ PDF  ☑️ Excel  ☐ CSV              │
│                                         │
│ [ Generar ] [ Vista Previa ]            │
└─────────────────────────────────────────┘
```

### Visualización de Reportes

#### Gráficos Interactivos
- **Barras**: Comparación por categorías
- **Líneas**: Tendencias temporales
- **Circular**: Distribución porcentual
- **Mapas**: Distribución geográfica

#### Exportación
- **PDF**: Documento completo
- **Excel**: Datos para análisis
- **CSV**: Importación a otros sistemas
- **Imagen**: Gráficos individuales

## Configuración

### Configuración Personal

#### Perfil de Usuario
```
┌─────────────────────────────────────────┐
│ Mi Perfil                               │
├─────────────────────────────────────────┤
│ Nombre: [Juan Administrador      ]      │
│ Email: [admin@trafficsystem.com  ]      │
│ Teléfono: [+51987654321         ]       │
│ Rol: Administrador                      │
│                                         │
│ Configuración:                          │
│ Idioma: [Español ▼]                     │
│ Zona horaria: [Lima ▼]                  │
│ Tema: [Claro ▼]                         │
│                                         │
│ [ Guardar ] [ Cambiar Contraseña ]      │
└─────────────────────────────────────────┘
```

#### Notificaciones
```
┌─────────────────────────────────────────┐
│ Preferencias de Notificación            │
├─────────────────────────────────────────┤
│ ☑️ Email al detectar infracciones       │
│ ☑️ Push cuando cámara se desconecta      │
│ ☐ SMS para alertas críticas             │
│ ☑️ Reporte diario por email              │
│                                         │
│ Frecuencia de resumen:                  │
│ ○ Inmediato  ● Cada hora  ○ Diario      │
│                                         │
│ [ Guardar Preferencias ]                │
└─────────────────────────────────────────┘
```

### Configuración del Sistema
*(Solo para administradores)*

#### Parámetros de Detección
- **Umbral de confianza**: Mínimo para auto-confirmar
- **Tipos de infracción**: Habilitar/deshabilitar
- **Límites de velocidad**: Por zona
- **Horarios activos**: Cuándo detectar

#### Gestión de Usuarios
- **Crear usuarios**
- **Asignar roles**
- **Gestionar permisos**
- **Auditar actividad**

## Búsqueda Global

### Función de Búsqueda

#### Acceso Rápido
```
🔍 [Buscar placas, infracciones, usuarios...] 
```

#### Resultados
- **Vehículos**: Por placa o propietario
- **Infracciones**: Por ID o características
- **Usuarios**: Por nombre o email
- **Ubicaciones**: Por dirección

### Filtros Avanzados

#### Combinación de Criterios
- **Y**: Todos los criterios deben cumplirse
- **O**: Al menos un criterio debe cumplirse
- **NO**: Excluir criterios específicos

## Ayuda y Soporte

### Centro de Ayuda

#### Recursos Disponibles
- 📖 **Manual completo**: Este documento
- 🎥 **Videos tutoriales**: Guías paso a paso
- ❓ **FAQ**: Preguntas frecuentes
- 📧 **Contacto**: support@trafficsystem.com

#### Búsqueda de Ayuda
```
┌─────────────────────────────────────────┐
│ 🔍 ¿En qué podemos ayudarte?            │
├─────────────────────────────────────────┤
│ [Buscar en la ayuda...          ] 🔍    │
│                                         │
│ Temas populares:                        │
│ • ¿Cómo confirmar una infracción?       │
│ • ¿Cómo registrar un nuevo vehículo?    │
│ • ¿Cómo generar reportes?               │
│ • ¿Cómo cambiar mi contraseña?          │
└─────────────────────────────────────────┘
```

### Contacto con Soporte

#### Canales Disponibles
- **Email**: support@trafficsystem.com
- **Teléfono**: +51-1-234-5678
- **Chat en línea**: Disponible en horario laboral
- **Tickets**: Sistema de tickets integrado

#### Información para Reportes
Cuando contactes soporte, incluye:
1. **Descripción del problema**
2. **Pasos para reproducir**
3. **Capturas de pantalla**
4. **Navegador y versión**
5. **Hora exacta del incidente**

## Consejos y Mejores Prácticas

### Uso Eficiente

#### Navegación Rápida
- **Ctrl+F**: Búsqueda en página
- **Ctrl+K**: Búsqueda global
- **Esc**: Cerrar modales
- **F5**: Actualizar página

#### Gestión de Tiempo
- **Filtros predefinidos**: Configurar filtros frecuentes
- **Atajos de teclado**: Aprender combinaciones útiles
- **Bookmarks**: Guardar vistas importantes
- **Notificaciones**: Configurar alertas relevantes

### Seguridad

#### Buenas Prácticas
- ✅ **Cerrar sesión** al terminar
- ✅ **Contraseñas fuertes** con números y símbolos
- ✅ **Verificar URLs** antes de introducir credenciales
- ✅ **Reportar actividad sospechosa** inmediatamente

#### Protección de Datos
- **No compartir credenciales** con otros usuarios
- **Verificar permisos** antes de modificar datos
- **Hacer backup** de datos importantes
- **Seguir políticas** de la organización

Este manual te guiará en el uso efectivo del sistema. Para dudas específicas, consulta la sección de ayuda o contacta al equipo de soporte.