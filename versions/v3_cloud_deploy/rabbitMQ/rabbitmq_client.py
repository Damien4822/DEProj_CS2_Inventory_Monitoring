import json
import pika
import os
import time
MAX_RETRIES = 5
RETRY_DELAY = 20
class RabbitMQClient:
    def __init__(self):
        self.host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.queue_name = os.getenv("RABBITMQ_QUEUE", "inventory_items")
        self.connection = None
        self.channel = None
        self._connect_with_retry()

    def _connect_with_retry(self):
        credentials = pika.PlainCredentials(
            os.getenv("RABBITMQ_USER", "guest"),
            os.getenv("RABBITMQ_PASSWORD", "guest")
        )
        parameters = pika.ConnectionParameters(
            host=self.host,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name, durable=True)
                return
            except pika.exceptions.AMQPConnectionError as e:
                print(f"[RabbitMQ] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
                if attempt == MAX_RETRIES:
                    raise
                time.sleep(RETRY_DELAY)
    #old 1 item-per-time attempt
    def consume(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        print(f"[*] Waiting for messages in {self.queue_name}. To exit press CTRL+C")
        self.channel.start_consuming()

    def get_batch(self, batch_size=20):
        batch = []
        for _ in range(batch_size):
            method_frame, properties, body = self.channel.basic_get(
                queue=self.queue_name,
                auto_ack=False
            )
            if body is None:
                break
            batch.append({
                "delivery_tag": method_frame.delivery_tag,
                "body": json.loads(body)
            })
        return batch
    def ack(self, delivery_tag):
        self.channel.basic_ack(
            delivery_tag=delivery_tag
        )

    def nack(self, delivery_tag, requeue=True):
        self.channel.basic_nack(
            delivery_tag=delivery_tag,
            requeue=requeue
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

