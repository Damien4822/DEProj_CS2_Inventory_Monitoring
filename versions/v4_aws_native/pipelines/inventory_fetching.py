from datetime import datetime,timedelta
import time
import requests
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.utils.log.logging_mixin import LoggingMixin
import os
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}
logger = LoggingMixin().log
STEAMID64 = os.getenv("STEAMID")
APPID = 730                          # CS2 / CS:GO
CONTEXTID = 2  

def fetch_inventory_steam(steamid64: str, appid: int, contextid: int):
    url = f"https://steamcommunity.com/inventory/{steamid64}/{appid}/{contextid}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()

def inventory_items(steamid64: str, appid: int, contextid: int):
    items = []
    seen_assetids = set()

    while True:
        data = fetch_inventory_steam(steamid64, appid, contextid)
        if not data or "assets" not in data or "descriptions" not in data:
            return items, data

        assets = data.get("assets", [])
        descriptions = data.get("descriptions", [])

        # Lookup description
        desc_lookup = {
            (str(d.get("classid")), str(d.get("instanceid", "0"))): d
            for d in descriptions
        }

        for a in assets:
            assetid = a.get("assetid")
            if assetid in seen_assetids:
                continue
            seen_assetids.add(assetid)

            classid = str(a.get("classid"))
            instanceid = str(a.get("instanceid", "0"))
            desc = desc_lookup.get((classid, instanceid)) or {}

            item = {
                "assetid": assetid,
                "classid": classid,
                "instanceid": instanceid,
                "amount": a.get("amount", 1),
                "name": desc.get("name"),
                "type": desc.get("type"),
                "market_hash_name": desc.get("market_hash_name"),
                "tradable": desc.get("tradable"),
                "marketable": desc.get("marketable"),
            }
            if item["tradable"] == 1 and item["marketable"] == 1:
                items.append(item)

        if not data.get("more_items"):
            break

        #delay between requests
        time.sleep(2)

    return items, data

default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    "pool": "default_pool",
    'retry_delay': timedelta(minutes=5),
    "priority_weight": 5,
}

with DAG(
    'inventory_fetching',
    default_args=default_args,
    description='ETL pipeline for fetching steam\'s inventory',
    schedule='0 * * * *',#setup hourly 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    max_active_runs=2,
    max_active_tasks=4,
    tags=['cs2', 'inventory-fetching', 'v3'],
) as dag:
    
    @task
    def extract_inventory():
        items, _ = inventory_items(STEAMID64, APPID, CONTEXTID)
        
        if not items:
            print("No items found in inventory.")
            return []
        
        seen = set()
        cleaned_items = []
        for item in items:
            assetid = item.get("assetid")
            market_hash_name = item.get("market_hash_name")
            name = item.get("name")

            if not assetid or not market_hash_name:
                continue

            if market_hash_name in seen:
                continue

            seen.add(market_hash_name)

            cleaned_items.append({
                "assetid": assetid,
                "market_hash_name": market_hash_name,
                "name": name
            })

        return cleaned_items
    
    @task
    def publish_to_queue(items: list):
        from versions.v3_cloud_deploy.rabbitMQ.rabbitmq_client import RabbitMQClient
        if not items:
            print("No items to publish.")
            return
        rabbit = RabbitMQClient()
        for item in items:
            rabbit.publish(item)
        rabbit.close()
        logger.info(f"Published {len(items)} items to RabbitMQ")

    # Task dependencies (TaskFlow syntax)
    logger.info("Start extracting inventory")
    item_list = extract_inventory()
    logger.info("Start publishing items to RabbitMQ")
    publish_to_queue(item_list)