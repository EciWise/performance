FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema para LightGBM/XGBoost.
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código + modelo entrenado (artifacts/*.joblib + metadata.json).
COPY app ./app
COPY artifacts ./artifacts

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Worker que consume solicitudes de predicción de RabbitMQ.
CMD ["python", "-m", "app.worker"]
