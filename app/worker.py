"""Worker de RabbitMQ para el modelo de rendimiento.

Consume solicitudes de la cola `ia.rendimiento.requests`, ejecuta el modelo y
publica el resultado en el exchange `ia.results` (canal de publicación SEPARADO
del de consumo). El contrato JSON coincide con wise_auth.
"""
from __future__ import annotations

import json
import logging
import os
import time

import pika

from app.adapters.ml.ensemble import EnsemblePredictor
from app.infrastructure.config import Settings

REQUESTS_EXCHANGE = "ia.requests"
RESULTS_EXCHANGE = "ia.results"
REQUEST_QUEUE = "ia.rendimiento.requests"
ROUTING_KEY = "rendimiento"

logger = logging.getLogger("worker.rendimiento")

# camelCase (wise_auth) -> columna exacta del modelo (igual que schemas.to_features).
FEATURE_MAP = {
    "Gender": "gender",
    "Ethnicity": "ethnicity",
    "ParentalEducation": "parentalEducation",
    "StudyTimeWeekly": "studyTimeWeekly",
    "Absences": "absences",
    "Tutoring": "tutoring",
    "ParentalSupport": "parentalSupport",
    "Extracurricular": "extracurricular",
    "Sports": "sports",
    "Music": "music",
    "Volunteering": "volunteering",
}


def to_model_features(features: dict) -> dict:
    return {column: features[key] for column, key in FEATURE_MAP.items()}


def _run_once(url: str, predictor: EnsemblePredictor) -> None:
    connection = pika.BlockingConnection(pika.URLParameters(url))
    consume_ch = connection.channel()
    publish_ch = connection.channel()  # canal separado para los resultados

    consume_ch.exchange_declare(REQUESTS_EXCHANGE, "direct", durable=True)
    publish_ch.exchange_declare(RESULTS_EXCHANGE, "direct", durable=True)
    consume_ch.queue_declare(REQUEST_QUEUE, durable=True)
    consume_ch.queue_bind(REQUEST_QUEUE, REQUESTS_EXCHANGE, ROUTING_KEY)
    consume_ch.basic_qos(prefetch_count=1)

    def on_message(ch, method, _properties, body) -> None:
        try:
            message = json.loads(body)
            prediction = predictor.predict(to_model_features(message["features"]))
            result = {
                "usuarioId": message["usuarioId"],
                "model": "rendimiento",
                "prediccionRendimiento": prediction,
            }
            publish_ch.basic_publish(
                RESULTS_EXCHANGE,
                ROUTING_KEY,
                json.dumps(result),
                properties=pika.BasicProperties(
                    delivery_mode=2, content_type="application/json"
                ),
            )
            ch.basic_ack(method.delivery_tag)
            logger.info("Rendimiento %s -> %s", message["usuarioId"], prediction)
        except Exception:  # noqa: BLE001 - no debe tumbar el worker
            logger.exception("Error procesando solicitud de rendimiento")
            ch.basic_nack(method.delivery_tag, requeue=False)

    consume_ch.basic_consume(REQUEST_QUEUE, on_message)
    logger.info("Worker de rendimiento escuchando en %s", REQUEST_QUEUE)
    consume_ch.start_consuming()


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    settings = Settings()
    predictor = EnsemblePredictor(
        artifacts_dir=settings.artifacts_dir,
        dataset_path=settings.dataset_path,
        auto_train=settings.auto_train,
    )
    # Reintento de conexión: el broker puede tardar en estar disponible.
    while True:
        try:
            _run_once(url, predictor)
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ no disponible; reintentando en 5s…")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Worker detenido")
            break


if __name__ == "__main__":
    main()
