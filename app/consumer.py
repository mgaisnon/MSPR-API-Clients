import pika
import json
import logging
import os
import time
from sqlalchemy.orm import Session
from app import models
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def callback(ch, method, properties, body):
    db = next(get_db())
    try:
        message = json.loads(body)
        event_type = message.get("type")
        data = message.get("data", {})

        logger.info(f"Message reçu (tracing API) : {event_type} - Données : {data}")

        if event_type == "customer_created":
            existing = db.query(models.Customer).filter(models.Customer.id == data["id"]).first()
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
                db.commit()
            else:
                db_customer = models.Customer(**data)
                db.add(db_customer)
                db.commit()
                logger.info(f"✅ Client créé via événement: {data.get('username')}")

        elif event_type == "customer_updated":
            customer_id = data.get("id")
            db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
            if db_customer:
                for key, value in data.items():
                    setattr(db_customer, key, value)
                db.commit()
                logger.info(f"✅ Client mis à jour via événement: {data.get('username')}")
            else:
                db_customer = models.Customer(**data)
                db.add(db_customer)
                db.commit()
                logger.info(f"⚠️ Client {customer_id} non trouvé, créé à la place")

        elif event_type == "customer_deleted":
            customer_id = data.get("id")
            db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
            if db_customer:
                db.delete(db_customer)
                db.commit()
                logger.info(f"🗑️ Client supprimé via événement: ID {customer_id}")
            # si déjà supprimé, on ne logge rien

        elif event_type == "customers_listed":
            logger.info(f"📋 Liste des clients reçue: {len(data.get('customers', []))} clients")

        elif event_type == "customer_retrieved":
            logger.info(f"📌 Client récupéré via événement: ID {data.get('id')}")

        else:
            logger.warning(f"❓ Type d'événement inconnu: {event_type}")

    except Exception as e:
        logger.error(f"Erreur lors du traitement du message: {str(e)}")
    finally:
        db.close()


def start_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            channel = connection.channel()

            exchange_name = "clients_exchange"
            queue_name = "clients_events"

            channel.exchange_declare(exchange=exchange_name, exchange_type="fanout", durable=True)
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(queue=queue_name, exchange=exchange_name)

            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=True,
            )

            logger.info("✅ En attente de messages pour tracing. Pour quitter, pressez CTRL+C")
            channel.start_consuming()

        except Exception as e:
            logger.error(f"Erreur dans le consommateur RabbitMQ: {str(e)}. Retry dans 5 secondes...")
            time.sleep(5)


if __name__ == "__main__":
    start_consumer()
