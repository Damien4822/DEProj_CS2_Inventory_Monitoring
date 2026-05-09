import json
import time
from rabbitMQ.rabbitmq_client import RabbitMQClient
from worker.processor import process_item
import traceback
from storage.mongo_client import insert_documents
from storage.postgres_client import insert_price_snapshots
BATCH_SIZE = 20

def start_consumer(logger):
    rabbit = RabbitMQClient()

    while True:
        batch = rabbit.get_batch(BATCH_SIZE)

        if not batch:
            time.sleep(1)
            continue

        logger.info(
            f"Fetched batch size={len(batch)}"
        )
        results = []
        delivery_tags = []
        for msg in batch:
            delivery_tag = msg["delivery_tag"]
            item = msg["body"]

            try:
                result = process_item(item, logger)
                results.append(result)
                delivery_tags.append(delivery_tag)
            except Exception as e:
                logger.error(
                    f"Worker error: {e}\n"
                    f"{traceback.format_exc()}"
                )
                rabbit.nack(
                    delivery_tag,
                    requeue=True
                )

    #TRANSFORMING
        rows = []

        for r in results:
            steam = r["sources"].get("steam", {})
            buff = r["sources"].get("buff", {})

            rows.append((
                r["item"],
                steam.get("lowest_price"),
                steam.get("median_price"),
                steam.get("volume"),
                buff.get("lowest_price"),
                buff.get("median_price"),
                buff.get("volume"),
            ))

        insert_price_snapshots(rows)
        insert_documents("market_raw", results)

        for tag in delivery_tags:
            rabbit.ack(tag)
        