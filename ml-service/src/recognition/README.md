# Enhanced Plate Recognition Module

Sistema completo de reconocimiento de placas vehiculares con ML de última generación.

## 🚀 Quick Start

```python
from ml_service.src.recognition.plate_recognition_pipeline import PlateRecognitionPipeline

# Inicializar pipeline
pipeline = PlateRecognitionPipeline(use_trocr=True, gpu=True)

# Procesar video
results = pipeline.process_video('traffic.mp4', output_path='output.mp4')

# Ver resultados
for result in results:
    print(f"{result.plate_text} - {result.vehicle_class} - {result.plate_confidence:.2f}")
```

## 📦 Componentes

| Módulo | Descripción | Tecnología |
|--------|-------------|------------|
| `vehicle_detection.py` | Detección de vehículos | YOLOv8 |
| `plate_segmentation.py` | Segmentación de placas | YOLOv8 Specialized |
| `text_extraction.py` | OCR dual pipeline | EasyOCR + TrOCR |
| `plate_recognition_pipeline.py` | Orquestador completo | - |
| `config.py` | Configuración del sistema | - |

## 🔧 Instalación

```bash
pip install -r requirements.txt
```

## 📖 Documentación

Ver `docs/ENHANCED_PLATE_RECOGNITION.md` para documentación completa.

## 🧪 Tests

```bash
pytest tests/test_enhanced_plate_recognition.py -v
```

## 📊 Performance

- **GPU**: 25-30 FPS
- **CPU**: 3-5 FPS
- **Precisión OCR**: >90%

## 🎯 Casos de Uso

```python
# Configuración de alta precisión
from ml_service.src.recognition.config import get_high_accuracy_config
config = get_high_accuracy_config()
pipeline = PlateRecognitionPipeline(config=config)

# Configuración de alto rendimiento
from ml_service.src.recognition.config import get_high_performance_config
config = get_high_performance_config()
pipeline = PlateRecognitionPipeline(config=config)
```

## 📝 Licencia

Parte del sistema de infracciones de tráfico.
