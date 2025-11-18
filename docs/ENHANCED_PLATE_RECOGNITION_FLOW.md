# Diagrama de Flujo: Sistema Mejorado de Detección de Placas

## Pipeline Completo - Vista General

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                         VIDEO INPUT / RTSP STREAM                         ║
║                    (Camera feed, video file, stream)                      ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                    STAGE 1: VEHICLE DETECTION (YOLOv8)                    ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  Frame (1920x1080x3)                                              ║
║  Model:  YOLOv8n (nano) - 3.2M params                                     ║
║  Classes: car(2), motorcycle(3), bus(5), truck(7)                         ║
║  Process:                                                                  ║
║    1. Resize to 640x640                                                   ║
║    2. Normalize pixels                                                    ║
║    3. YOLO inference                                                      ║
║    4. NMS (Non-Max Suppression)                                           ║
║  Output: [                                                                ║
║    {bbox: [x1,y1,x2,y2], conf: 0.87, class: 'car'},                      ║
║    {bbox: [x1,y1,x2,y2], conf: 0.92, class: 'bus'},                      ║
║    ...                                                                    ║
║  ]                                                                        ║
║  Performance: ~60 FPS (GPU) / ~8 FPS (CPU)                                ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                  STAGE 2: VEHICLE TRACKING (DeepSORT)                     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  Vehicle detections from Stage 1                                  ║
║  Algorithm: DeepSORT (Deep Learning + Hungarian Algorithm)                ║
║  Process:                                                                  ║
║    1. Feature extraction from detection                                   ║
║    2. Calculate IOU with existing tracks                                  ║
║    3. Kalman filter prediction                                            ║
║    4. Hungarian algorithm matching                                        ║
║    5. Track creation/update/deletion                                      ║
║  Output: [                                                                ║
║    {track_id: 1, bbox: [...], trajectory: [...], age: 15},               ║
║    {track_id: 2, bbox: [...], trajectory: [...], age: 8},                ║
║    ...                                                                    ║
║  ]                                                                        ║
║  Features:                                                                 ║
║    • Persistent ID across frames                                          ║
║    • Trajectory history (last 30 frames)                                  ║
║    • Occlusion handling                                                   ║
║    • Track age management                                                 ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║            STAGE 3: PLATE SEGMENTATION (YOLOv8 Specialized)               ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  Vehicle ROI from tracked vehicle                                 ║
║  Model:  YOLOv8 trained on license plates                                 ║
║  Process:                                                                  ║
║    1. Extract vehicle region with margin                                  ║
║       vehicle_roi = frame[y1-10:y2+10, x1-10:x2+10]                       ║
║    2. Run specialized YOLO on vehicle ROI                                 ║
║    3. Fallback to Cascade Classifier if no detection                      ║
║    4. Extract plate region                                                ║
║  Output: {                                                                ║
║    bbox: [px1, py1, px2, py2],                                            ║
║    plate_image: ndarray(60x200x3),                                        ║
║    confidence: 0.78                                                       ║
║  }                                                                        ║
║  Strategies:                                                               ║
║    Strategy 1: YOLOv8 specialized model                                   ║
║    Strategy 2: Cascade Classifier (haarcascade_russian_plate_number)      ║
║    Strategy 3: Contour-based detection (backup)                           ║
║  Performance: ~120 FPS (GPU) / ~15 FPS (CPU)                              ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║             STAGE 4A: IMAGE PREPROCESSING (CLAHE + Enhanced)              ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  Plate image from Stage 3                                         ║
║  Steps:                                                                    ║
║    1. Resize to minimum 64px height                                       ║
║       if height < 64:                                                     ║
║         scale = 64 / height                                               ║
║         resize(plate_img, (width*scale, 64))                              ║
║                                                                            ║
║    2. Convert to grayscale                                                ║
║       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                        ║
║                                                                            ║
║    3. CLAHE (Contrast Limited Adaptive Histogram Equalization)            ║
║       clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))         ║
║       enhanced = clahe.apply(gray)                                        ║
║                                                                            ║
║    4. Denoising                                                            ║
║       denoised = cv2.fastNlMeansDenoising(enhanced, h=10)                 ║
║                                                                            ║
║    5. Sharpening                                                           ║
║       kernel = [[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]                        ║
║       sharpened = cv2.filter2D(denoised, -1, kernel)                      ║
║                                                                            ║
║  Multiple Variations Created:                                             ║
║    • Adaptive threshold                                                   ║
║    • Otsu's threshold                                                     ║
║    • Morphological operations                                             ║
║  Output: [preprocessed_img, variation1, variation2, ...]                  ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║            STAGE 4B: TEXT EXTRACTION - DUAL OCR PIPELINE                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ┌─────────────────────────────────────────────────────────────────────┐  ║
║  │                    PATHWAY 1: EasyOCR                                │  ║
║  ├─────────────────────────────────────────────────────────────────────┤  ║
║  │  Technology: CNN-based detection + LSTM recognition                 │  ║
║  │  Process:                                                            │  ║
║  │    1. Convert to RGB                                                 │  ║
║  │    2. Text detection (CRAFT algorithm)                               │  ║
║  │    3. Text recognition (CRNN)                                        │  ║
║  │  Parameters:                                                         │  ║
║  │    allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'                  │  ║
║  │    min_size=10, text_threshold=0.3                                   │  ║
║  │    low_text=0.2, link_threshold=0.2                                  │  ║
║  │  Output: [('ABC123', 0.92, bbox), ...]                               │  ║
║  └─────────────────────────────────────────────────────────────────────┘  ║
║                                 │                                          ║
║                                 ├──────────┐                               ║
║                                 │          │                               ║
║  ┌─────────────────────────────▼───────┐  │                               ║
║  │     PATHWAY 2: TrOCR (Optional)     │  │                               ║
║  ├─────────────────────────────────────┤  │                               ║
║  │  Technology: Vision Transformer     │  │                               ║
║  │  Model: microsoft/trocr-base-printed│  │                               ║
║  │  Process:                            │  │                               ║
║  │    1. Convert to PIL Image          │  │                               ║
║  │    2. Transformer encoder           │  │                               ║
║  │    3. Decoder generates text        │  │                               ║
║  │  Output: ('ABC123', 0.85)           │  │                               ║
║  └─────────────────────────────────────┘  │                               ║
║                                 │          │                               ║
║                                 ▼          ▼                               ║
║  ┌──────────────────────────────────────────────────────────────────────┐ ║
║  │                      RESULT FUSION                                    │ ║
║  ├──────────────────────────────────────────────────────────────────────┤ ║
║  │  1. Collect all results from both pathways                           │ ║
║  │  2. Score each result by confidence                                  │ ║
║  │  3. Apply character corrections:                                     │ ║
║  │     O→0, I→1, S→5, B→8 (context-aware)                               │ ║
║  │  4. Select highest confidence result                                 │ ║
║  │  Output: {text: 'ABC-123', confidence: 0.92}                         │ ║
║  └──────────────────────────────────────────────────────────────────────┘ ║
║                                                                            ║
║  Performance: ~10-15 plates/s (GPU) / ~2-3 plates/s (CPU)                 ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║              STAGE 5: VALIDATION & POST-PROCESSING                        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  OCR result from Stage 4                                          ║
║  Process:                                                                  ║
║    1. Format Validation (Regex Patterns)                                  ║
║       ✓ AAA-123  (Peru standard)                                          ║
║       ✓ AB-1234  (Peru modern)                                            ║
║       ✓ A12-345  (Peru old)                                               ║
║       ✓ AAA123   (No hyphen variant)                                      ║
║                                                                            ║
║    2. Character Normalization                                             ║
║       • Remove non-alphanumeric (except hyphen)                           ║
║       • Convert to uppercase                                              ║
║       • Apply correction rules                                            ║
║                                                                            ║
║    3. Confidence Filtering                                                ║
║       if confidence < 0.2: reject                                         ║
║       if confidence > 0.85: auto-accept                                   ║
║       else: require format match                                          ║
║                                                                            ║
║    4. Association with Track                                              ║
║       tracker.associate_plate(track_id, text, confidence)                 ║
║       if new_conf > existing_conf: update                                 ║
║                                                                            ║
║  Output: {                                                                ║
║    track_id: 42,                                                          ║
║    plate_text: 'ABC-123',                                                 ║
║    confidence: 0.92,                                                      ║
║    is_valid: true,                                                        ║
║    format: 'Peru-Standard'                                                ║
║  }                                                                        ║
╚════════════════════════════════╤══════════════════════════════════════════╝
                                 │
                                 ▼
╔═══════════════════════════════════════════════════════════════════════════╗
║                STAGE 6: STORAGE & INFRACTION DETECTION                    ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  Input:  Validated plate recognition result                               ║
║  Process:                                                                  ║
║    1. Create PlateRecognitionResult:                                      ║
║       • track_id, vehicle_class, vehicle_bbox                             ║
║       • plate_bbox, plate_text, plate_confidence                          ║
║       • frame_number, timestamp                                           ║
║       • trajectory, speed (if available)                                  ║
║                                                                            ║
║    2. Check for Infractions:                                              ║
║       • Lane invasion (from trajectory)                                   ║
║       • Speed violation (from speed estimation)                           ║
║       • Red light (from traffic light detector)                           ║
║       • Restricted zone (from geofencing)                                 ║
║                                                                            ║
║    3. Store in Database:                                                  ║
║       INSERT INTO infractions (                                           ║
║         plate_number, infraction_type, timestamp,                         ║
║         vehicle_type, confidence, evidence_image,                         ║
║         location, metadata                                                ║
║       )                                                                   ║
║                                                                            ║
║    4. Generate Alert (if needed):                                         ║
║       • Websocket notification                                            ║
║       • MQTT message                                                      ║
║       • REST API callback                                                 ║
║                                                                            ║
║  Output: Infraction record + Real-time alert                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

## Métricas de Rendimiento por Stage

```
┌────────────────────────────────────────────────────────────────────┐
│                    PERFORMANCE BREAKDOWN                           │
├───────────┬─────────────┬─────────────┬──────────────────────────┤
│   Stage   │  GPU (ms)   │  CPU (ms)   │      Notes               │
├───────────┼─────────────┼─────────────┼──────────────────────────┤
│ Stage 1   │   16-20     │   125-150   │ YOLOv8 inference         │
│ Stage 2   │   2-5       │   5-10      │ Tracking (lightweight)   │
│ Stage 3   │   8-12      │   60-80     │ Plate detection          │
│ Stage 4A  │   5-8       │   15-20     │ Preprocessing            │
│ Stage 4B  │   80-120    │   300-400   │ OCR (dual pipeline)      │
│ Stage 5   │   1-2       │   1-2       │ Validation (CPU only)    │
│ Stage 6   │   5-10      │   5-10      │ DB write                 │
├───────────┼─────────────┼─────────────┼──────────────────────────┤
│   TOTAL   │   117-177   │   511-672   │ Per frame                │
│           │  (25-30fps) │  (3-5fps)   │                          │
└───────────┴─────────────┴─────────────┴──────────────────────────┘
```

## Data Flow Ejemplo

```
Frame 1024 @ 00:34.133
    ↓
  [Stage 1] → Detected: 3 vehicles (car, bus, motorcycle)
    ↓
  [Stage 2] → Tracking: Track #12 (car), Track #18 (bus), Track #23 (motorcycle)
    ↓
  [Stage 3] → Plate found on Track #12: bbox=[450,320,580,360]
    ↓
  [Stage 4A] → Preprocessed: CLAHE + sharpen → 3 variations
    ↓
  [Stage 4B] → EasyOCR: 'ABC123' (0.89)
              TrOCR: 'ABC-123' (0.87)
              → Selected: 'ABC123'
    ↓
  [Stage 5] → Validated: 'ABC-123' (normalized)
              Format: Peru-Standard ✓
              Confidence: 0.89 ✓
    ↓
  [Stage 6] → Stored: Infraction #5421
              Type: SPEEDING (82 km/h in 60 zone)
              Evidence: /evidence/2025-11-17/5421.jpg
              Alert: Sent to monitoring station
```
