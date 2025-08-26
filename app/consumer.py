import pika
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = "amqp://guest:guest@localhost:5672/"

def callback(ch, method, properties, body):
    message = json.loads(body)
    logger.info(f"Message reçu: {message}")

try:
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    exchange_name = 'clients_exchange'
    queue_name = 'clients_events'
    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(queue=queue_name, exchange=exchange_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    logger.info("En attente de messages. Pour quitter, pressez CTRL+C")
    channel.start_consuming()
except Exception as e:
    logger.error(f"Erreur dans le consommateur RabbitMQ: {str(e)}")
finally:
    connection.close()