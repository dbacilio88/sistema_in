FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY *.py ./
COPY web ./web

# Crear directorio para configuraciones
RUN mkdir -p /app/configs /app/logs

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Comando por defecto
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
