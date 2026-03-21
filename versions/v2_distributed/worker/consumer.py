import json
from rabbitMQ.rabbitmq_client import RabbitMQClient
from worker.processor import process_item


def start_consumer():

    rabbit = RabbitMQClient()

    def callback(ch, method, properties, body):

        try:
            item = json.loads(body)

            print(f"Processing: {item['market_hash_name']}")
            
            process_item(item)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Worker error: {e}")

            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    rabbit.consume(callback)