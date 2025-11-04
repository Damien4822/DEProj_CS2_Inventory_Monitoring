from datetime import datetime,timedelta
import time
import random
from collections import defaultdict
from urllib.parse import quote
import requests
import pandas as pd
import os
from airflow import DAG
from airflow.decorators import task
from airflow.providers.standard.operators.python import PythonOperator
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

def fetch_inventory_page(steamid64: str, appid: int, contextid: int, start: str = None):
    url = f"https://steamcommunity.com/inventory/{steamid64}/{appid}/{contextid}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()

def inventory_items_for_user(steamid64: str, appid: int, contextid: int, delay_between_requests: float = 0.5):
    items = []
    seen_assetids = set()
    start = None

    while True:
        data = fetch_inventory_page(steamid64, appid, contextid, start)
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

def get_market_price(market_hash_name, appid=730, currency=1):
    url = f"http://steamcommunity.com/market/priceoverview/?appid={appid}&currency={currency}&market_hash_name={quote(market_hash_name)}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Fetching {market_hash_name}: {e}")
        return None
    if not data.get("success"):
        return None
    prices = {
        "lowest_price": data.get("lowest_price"),
        "median_price": data.get("median_price"),
        "volume": data.get("volume")
    }
    if all(v is None for v in prices.values()):
        return None
    return prices

default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'cs2_market_etl',
    default_args=default_args,
    description='ETL pipeline for CS2 Market data using Spark and Airflow',
    schedule='0 * * * *',#setup hourly 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['cs2', 'etl', 'spark'],
) as dag:
    
    @task
    def extract_inventory():
        items, raw = inventory_items_for_user(STEAMID64, APPID, CONTEXTID)
        summaries = []
        seen_names = set()

        for i, it in enumerate(items[:200], start=1):
            name = it["market_hash_name"]
            if not name or name in seen_names:
                continue
            seen_names.add(name)
            summaries.append({
                "index": i,
                "name": it["name"],
                "market_hash_name": name,
                "tradable": it.get("tradable"),
                "marketable": it.get("marketable"),
            })

        print(f"Extracted {len(summaries)} tradable & marketable items.")
        return summaries
    
    @task
    def fetch_market_prices(summaries: list):
        if not summaries:
            print("No items to fetch prices for.")
            return {}

        prices = {}
        for item in summaries:
            market_hash_name = item["market_hash_name"]
            data = get_market_price(market_hash_name)
            if data:
                prices[market_hash_name] = data
                time.sleep(random.uniform(4.5, 6.0))
        print(f"Fetched {len(prices)} market prices.")
        return prices
    
    @task
    def transform_data(summaries: list, prices: dict):
        transformed = []
        for item in summaries:
            name = item["market_hash_name"]
            price_data = prices.get(name, {})
            transformed.append({
                "name": name,
                "lowest_price": price_data.get("lowest_price"),
                "median_price": price_data.get("median_price"),
                "volume": price_data.get("volume"),
            })

        print(f"Transformed {len(transformed)} items.")
        return transformed
    
    @task
    def load_data(transformed: list):
        if not transformed:
            print("No transformed data found. Skipping export.")
            return None

        df = pd.DataFrame(transformed)
        output_dir = "/home/ubuntu/DE_Projects/DEProj_CS2_Inventory_Monitoring/temp"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(output_dir, f"cs2_market_data_{timestamp}.xlsx")
        df.to_excel(file_path, index=False)
        print(f"Data successfully exported to: {file_path}")
        return file_path

    # Task dependencies (TaskFlow syntax)
    summaries = extract_inventory()
    prices = fetch_market_prices(summaries)
    transformed = transform_data(summaries, prices)
    load_data(transformed)