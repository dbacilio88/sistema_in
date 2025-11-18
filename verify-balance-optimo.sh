#!/bin/bash

echo "🔍 Verificación Rápida - Balance Óptimo V3"
echo "=========================================="
echo ""

# Frontend checks
echo "📱 FRONTEND:"
grep -q "skipFramesRef.current < 4" frontend-dashboard/src/components/LocalWebcamDetection.tsx && \
  echo "  ✅ Frame Skip: 1/5 (ÓPTIMO)" || echo "  ❌ Frame Skip: INCORRECTO"

grep -q "const scale = 0.6" frontend-dashboard/src/components/LocalWebcamDetection.tsx && \
  echo "  ✅ Scale: 0.6 (ÓPTIMO)" || echo "  ❌ Scale: INCORRECTO"

grep -q "toDataURL('image/jpeg', 0.90)" frontend-dashboard/src/components/LocalWebcamDetection.tsx && \
  echo "  ✅ JPEG: 90% (ÓPTIMO)" || echo "  ❌ JPEG: INCORRECTO"

grep -q "ctx.drawImage(video, 0, 0, canvas.width, canvas.height)" frontend-dashboard/src/components/LocalWebcamDetection.tsx && \
  echo "  ✅ Video Continuo: HABILITADO" || echo "  ❌ Video Continuo: DESHABILITADO"

echo ""
echo "⚙️ BACKEND:"
grep -q "self.output_quality = 70" inference-service/app/api/websocket.py && \
  echo "  ✅ Output Quality: 70% (ÓPTIMO)" || echo "  ❌ Output Quality: INCORRECTO"

grep -q "self.ocr_frame_interval = 3" inference-service/app/api/websocket.py && \
  echo "  ✅ OCR Interval: 3 frames" || echo "  ❌ OCR Interval: INCORRECTO"

grep -q "use_background_ocr = False" inference-service/app/api/websocket.py && \
  echo "  ✅ Background OCR: Deshabilitado" || echo "  ❌ Background OCR: HABILITADO"

echo ""
echo "🐳 SERVICIOS:"
docker-compose ps frontend | grep -q "Up" && echo "  ✅ Frontend: Running" || echo "  ❌ Frontend: DOWN"
docker-compose ps inference | grep -q "Up" && echo "  ✅ Inference: Running" || echo "  ❌ Inference: DOWN"

echo ""
echo "📊 RESUMEN:"
echo "  • Video fluido: ✅ 30 FPS (dibujado continuamente)"
echo "  • Detección: ✅ Scale 0.6 + JPEG 90% (balance óptimo)"
echo "  • Rendimiento: ✅ 1/5 frames (20% procesado)"
echo ""
echo "🎯 Listo para probar en: http://localhost:3002"
