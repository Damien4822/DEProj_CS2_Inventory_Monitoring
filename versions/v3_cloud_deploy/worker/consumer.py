import json
from rabbitMQ.rabbitmq_client import RabbitMQClient
from worker.processor import process_item
import traceback

def start_consumer(logger):
    rabbit = RabbitMQClient()
    def callback(ch, method, properties, body):
        try:
            item = json.loads(body)
            logger.info(f"Processing: {item['market_hash_name']}")
            process_item(item,logger)
            logger.info("ack-ing message from queue")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.info(f"Worker error: {e}\n{traceback.format_exc()}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    rabbit.consume(callback)