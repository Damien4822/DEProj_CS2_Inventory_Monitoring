from datetime import datetime,timedelta
import time
import requests
from airflow import DAG
from airflow.decorators import task
from queue.rabbitmq_client import RabbitMQClient
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

STEAMID64 = "76561198923974658"
APPID = 730                          # CS2 / CS:GO
CONTEXTID = 2  

def fetch_inventory_steam(steamid64: str, appid: int, contextid: int):
    url = f"https://steamcommunity.com/inventory/{steamid64}/{appid}/{contextid}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()

def inventory_items(steamid64: str, appid: int, contextid: int, delay_between_requests: float = 0.5):
    items = []
    seen_assetids = set()
    start = None

    while True:
        data = fetch_inventory_steam(steamid64, appid, contextid, start)
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

        start = data.get("last_assetid") or data.get("more_start")
        if not start:
            break
        time.sleep(delay_between_requests)

    return items, data

default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    "pool": "default_pool",
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'cs2_market_etl',
    default_args=default_args,
    description='ETL pipeline for CS2 Market data using Spark and Airflow',
    schedule='0 * * * *',#setup hourly 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    max_active_runs=2,
    max_active_tasks=4,
    tags=['cs2', 'etl', 'spark'],
) as dag:
    
    @task
    def extract_inventory():
        items, _ = inventory_items(STEAMID64, APPID, CONTEXTID)
        
        if not items:
            print("No items found in inventory.")
            return []
        
        cleaned_items = []
        for item in items:
            
            assetid = item.get("assetid")
            market_hash_name = item.get("market_hash_name")
            name = item.get("name")
            if not assetid or not market_hash_name:
                continue

            cleaned_items.append({
                "assetid": assetid,
                "market_hash_name": market_hash_name,
                "name": name
                })
        return cleaned_items
    
    @task
    def publish_to_queue(items: list):

        if not items:
            print("No items to publish.")
            return

        rabbit = RabbitMQClient()

        for item in items:
            rabbit.publish(item)

        rabbit.close()

        print(f"Published {len(items)} items to RabbitMQ")

    # Task dependencies (TaskFlow syntax)
    item_list = extract_inventory()
    publish_to_queue(item_list)