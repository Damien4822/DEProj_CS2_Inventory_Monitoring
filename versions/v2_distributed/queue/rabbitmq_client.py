import json
import pika
import os

class RabbitMQClient:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.queue_name = os.getenv("RABBITMQ_QUEUE", "inventory_items")

        credentials = pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "guest"),
            os.getenv("RABBITMQ_PASSWORD", "guest"),
        )

        parameters = pika.ConnectionParameters(
            host=self.host,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Ensure queue exists
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True
        )

    def publish(self, message: dict):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # persistent
            ),
        )

    def close(self):
        self.connection.close()

