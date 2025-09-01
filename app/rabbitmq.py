import pika
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")

def json_serializer(obj):
    """Gère la sérialisation des objets datetime."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} non sérialisable")

def publish_event(event_type: str, data: dict):
    try:
        logger.debug(f"Publication des données: {data}")
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        exchange_name = 'clients_exchange'
        channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
        channel.basic_publish(
            exchange=exchange_name,
            routing_key='',  # Pas de routing_key pour fanout
            body=json.dumps({'type': event_type, 'data': data}, default=json_serializer),
            properties=pika.BasicProperties(delivery_mode=2)  # Messages persistants
        )
        logger.info(f"Événement publié: {event_type}")
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement {event_type}: {str(e)}")
        raise
    finally:
        if 'connection' in locals():
            connection.close()