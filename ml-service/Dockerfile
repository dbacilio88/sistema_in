# Multi-stage build for optimized ML service with GPU support
FROM nvidia/cuda:11.8-devel-ubuntu22.04 as builder

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    python3.10-venv \
    build-essential \
    cmake \
    wget \
    curl \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-glog0v5 \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch with CUDA support first (largest dependencies)
RUN pip install --no-cache-dir \
    torch==2.0.1+cu118 \
    torchvision==0.15.2+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

# Install ONNX Runtime GPU
RUN pip install --no-cache-dir onnxruntime-gpu==1.16.0

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM nvidia/cuda:11.8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH="/opt/venv/bin:${CUDA_HOME}/bin:${PATH}"
ENV LD_LIBRARY_PATH="${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgoogle-glog0v5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user
RUN groupadd -r mluser && useradd -r -g mluser mluser

# Create application directories
RUN mkdir -p /app/models/weights \
             /app/datasets \
             /app/outputs \
             /app/logs && \
    chown -R mluser:mluser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=mluser:mluser src/ ./src/
COPY --chown=mluser:mluser scripts/ ./scripts/
COPY --chown=mluser:mluser tests/ ./tests/
COPY --chown=mluser:mluser *.py ./

# Make scripts executable
RUN chmod +x scripts/*.py

# Switch to non-root user
USER mluser

# Create script for model download
RUN echo '#!/bin/bash\n\
python3.10 -c "\n\
from ultralytics import YOLO\n\
import os\n\
os.makedirs(\"models/weights\", exist_ok=True)\n\
model = YOLO(\"yolov8x.pt\")\n\
model.export(format=\"onnx\", imgsz=640, dynamic=True, simplify=True, optimize=True)\n\
print(\"YOLOv8x model downloaded and converted to ONNX\")\n\
"' > /tmp/download_model.sh && \
    chmod +x /tmp/download_model.sh && \
    /tmp/download_model.sh && \
    rm /tmp/download_model.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.10 -c "import src.detection; print('ML service healthy')" || exit 1

# Default command
CMD ["python3.10", "-m", "src.detection.vehicle_detector"]

# Labels
LABEL maintainer="Traffic Analysis System Team"
LABEL version="1.0.0"
LABEL description="ML Service for YOLOv8 vehicle detection with GPU acceleration"
LABEL gpu.required="true"
LABEL cuda.version="11.8"