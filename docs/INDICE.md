# Índice de Documentación - Sistema de Detección de Infracciones

## 📚 Documentación Completa del Sistema

Este directorio contiene la documentación técnica completa del **Sistema Inteligente de Detección de Infracciones de Tránsito**.

---

## 📄 Documentos Disponibles

### 1. [ARQUITECTURA.md](./ARQUITECTURA.md) 🏗️
**Visión General del Sistema**

Descripción completa de la arquitectura del sistema, componentes principales y sus relaciones.

**Contenido:**
- Diagrama de arquitectura general
- Componentes principales (Backend Django, Inference Service, ML Service, Frontend)
- Stack tecnológico
- Flujo de datos entre componentes
- **Responsable de detección de infracciones: ML Service - ViolationDetector** 🏆

**Ideal para:** Entender la arquitectura completa y cómo interactúan los componentes

---

### 2. [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) 🐍
**Sistema de Administración y API REST**

Documentación del backend Django que gestiona usuarios, datos y API REST.

**Contenido:**
- Estructura del proyecto
- Modelos de datos (User, Device, Zone, Vehicle, Driver, Infraction, Notification)
- APIs REST completas
- Endpoints y ejemplos
- Autenticación JWT
- Integración con SUNARP
- Sistema de notificaciones

**Ideal para:** Desarrolladores que trabajen con la API o el panel administrativo

---

### 3. [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md) 🚀
**Servicio de Procesamiento en Tiempo Real**

Documentación del servicio FastAPI que procesa streams de video.

**Contenido:**
- Conexión a cámaras RTSP
- Detección de vehículos con YOLOv8
- Tracking con DeepSORT
- OCR de placas con EasyOCR
- Cálculo de velocidad
- Pipeline de procesamiento completo
- APIs de control de streams

**Ideal para:** Entender cómo se captura y procesa el video en tiempo real

---

### 4. [ML-SERVICE.md](./ML-SERVICE.md) 🤖⭐
**Servicio de Machine Learning - RESPONSABLE DE DETECCIÓN**

Documentación del componente **principal responsable de detectar infracciones**.

**Contenido:**
- **ViolationDetector** - Detector principal de infracciones
- Tipos de infracciones detectadas (velocidad, carril, sentido contrario, etc.)
- Clasificación de severidad (menor, moderada, grave, crítica)
- SpeedAnalyzer - Análisis de velocidad
- LaneDetector - Detección de carriles
- PlateRecognizer - OCR avanzado
- VehicleTracker - Tracking persistente
- Filtrado de falsos positivos

**Ideal para:** Entender la lógica de detección de infracciones

---

### 5. [FRONTEND-DASHBOARD.md](./FRONTEND-DASHBOARD.md) 💻
**Interfaz de Usuario Web**

Documentación del frontend Next.js/React.

**Contenido:**
- Estructura de componentes React
- Vistas principales (Dashboard, Infracciones, Dispositivos, Reportes)
- Componentes reutilizables
- Integración con WebSocket
- Consumo de API REST
- Autenticación y autorización

**Ideal para:** Desarrolladores frontend o UX/UI

---

### 6. [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) 🏗️
**Servicios de Infraestructura**

Documentación de bases de datos y servicios de soporte.

**Contenido:**
- **PostgreSQL 16** - Base de datos relacional
- **Redis 7** - Cache y sesiones
- **RabbitMQ 3.12** - Message broker
- **MinIO** - Object storage (S3-compatible)
- Docker Compose
- Configuración de puertos y volúmenes

**Ideal para:** DevOps, administradores de sistemas

---

### 7. [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) 🔄
**Flujos Detallados de Detección de Infracciones**

Diagramas de secuencia y flujos completos del proceso de detección.

**Contenido:**
- Flujo completo de detección (diagrama de secuencia)
- Flujo de exceso de velocidad (paso a paso)
- Flujo de invasión de carril
- Flujo de sentido contrario
- Flujo de reconocimiento de placas (OCR)
- Flujo de validación manual por operador
- Matriz de responsabilidades por componente

**Ideal para:** Entender el proceso completo desde la cámara hasta la notificación

---

## 🎯 Guía de Lectura Recomendada

### Para Nuevos Desarrolladores
1. Empezar con [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general
2. Leer [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Entender el proceso
3. Profundizar en el componente específico según rol

### Para Desarrolladores Backend
1. [ARQUITECTURA.md](./ARQUITECTURA.md)
2. [BACKEND-DJANGO.md](./BACKEND-DJANGO.md)
3. [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)

### Para Desarrolladores de ML/AI
1. [ARQUITECTURA.md](./ARQUITECTURA.md)
2. [ML-SERVICE.md](./ML-SERVICE.md) ⭐
3. [INFERENCE-SERVICE.md](./INFERENCE-SERVICE.md)
4. [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md)

### Para Desarrolladores Frontend
1. [ARQUITECTURA.md](./ARQUITECTURA.md)
2. [FRONTEND-DASHBOARD.md](./FRONTEND-DASHBOARD.md)
3. [BACKEND-DJANGO.md](./BACKEND-DJANGO.md) (sección APIs)

### Para DevOps/SysAdmin
1. [ARQUITECTURA.md](./ARQUITECTURA.md)
2. [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)
3. Docker Compose en raíz del proyecto

---

## ❓ Preguntas Frecuentes

### ¿Qué componente detecta las infracciones?
**Respuesta:** El **ML Service**, específicamente el módulo **ViolationDetector** (`ml-service/src/violations/violation_detector.py`)

Ver: [ML-SERVICE.md](./ML-SERVICE.md) y [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md)

---

### ¿Cómo se relacionan los componentes?
**Respuesta:** 
```
Cámara → Inference Service (detección básica) 
       → ML Service (validación y clasificación) 
       → Backend Django (persistencia) 
       → Frontend Dashboard (visualización)
```

Ver: [ARQUITECTURA.md](./ARQUITECTURA.md) - Sección "Relaciones entre Componentes"

---

### ¿Qué base de datos se usa?
**Respuesta:** PostgreSQL 16 para datos relacionales, Redis para cache, MinIO para archivos.

Ver: [INFRASTRUCTURE.md](./INFRASTRUCTURE.md)

---

### ¿Cómo se comunican los servicios?
**Respuesta:** 
- HTTP REST API (síncrono)
- RabbitMQ (asíncrono, eventos)
- WebSocket (tiempo real Frontend ↔ Backend)

Ver: [ARQUITECTURA.md](./ARQUITECTURA.md) - Sección "Flujo de Datos"

---

### ¿Qué tipos de infracciones detecta?
**Respuesta:**
- Exceso de velocidad
- Invasión de carril
- Sentido contrario
- Paso con luz roja
- Estacionamiento ilegal
- Otros (configurables)

Ver: [ML-SERVICE.md](./ML-SERVICE.md) - Sección "ViolationDetector"

---

### ¿Cómo funciona el reconocimiento de placas?
**Respuesta:** Pipeline de YOLOv8 (detección) + EasyOCR (lectura) + validación de formato + correcciones automáticas.

Ver: [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Sección "Flujo de Reconocimiento de Placas"

---

## 📊 Responsabilidades por Componente

| Componente | Responsabilidad Principal | Detecta Infracciones |
|------------|--------------------------|----------------------|
| **Backend Django** | Administración, API REST, persistencia | ❌ No |
| **Inference Service** | Procesamiento video, detección básica | ✅ Básico |
| **ML Service** | Validación, clasificación, análisis avanzado | ✅ Sí (PRINCIPAL) ⭐ |
| **Frontend Dashboard** | Interfaz de usuario, visualización | ❌ No |
| **Infrastructure** | Bases de datos, cache, storage | ❌ No |

---

## 🚀 Inicio Rápido

### 1. Leer primero
- [ARQUITECTURA.md](./ARQUITECTURA.md) - Visión general

### 2. Según tu rol
- **Developer Full Stack**: Todos los documentos
- **Backend**: Backend Django + Infrastructure
- **ML/AI**: ML Service + Inference Service
- **Frontend**: Frontend Dashboard + Backend Django (APIs)
- **DevOps**: Infrastructure + Arquitectura

### 3. Profundizar
- [FLUJOS-DETECCION.md](./FLUJOS-DETECCION.md) - Entender el flujo completo

---

## 🎓 Resumen Ejecutivo

### ¿Qué hace este sistema?
Detecta automáticamente infracciones de tránsito usando cámaras, inteligencia artificial y análisis en tiempo real.

### ¿Quién detecta las infracciones?
El **ML Service - ViolationDetector** es el responsable principal.

### ¿Cómo funciona?
1. Cámara captura video
2. Inference Service detecta vehículos y placas
3. ML Service valida y clasifica infracciones
4. Backend Django guarda y gestiona
5. Frontend muestra a operadores

### ¿Qué infracciones detecta?
Exceso de velocidad, invasión de carril, sentido contrario, luz roja, y más.

### ¿Es automático?
Detección automática + validación manual por operador.

---

**¡Bienvenido al Sistema de Detección de Infracciones!** 🚦🚗

Para comenzar, lee [ARQUITECTURA.md](./ARQUITECTURA.md)

---

**Última actualización:** Noviembre 2025
