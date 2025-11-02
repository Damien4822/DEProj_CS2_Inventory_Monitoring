from datetime import datetime,timedelta
from airflow import DAG
import time
import random
from collections import defaultdict
from urllib.parse import quote
import requests
from airflow.operators import PythonOperator
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

STEAMID64 = ""
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

def extract_inventory(**context):
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
            "marketable": it.get("marketable")
        })

    # Push the summaries to XCom so the next task can use them
    context["ti"].xcom_push(key="item_summaries", value=summaries)
    print(f"Extracted {len(summaries)} tradable & marketable items.")

def extracting():
    #fetch list of cs2 items in one inventory, then fetch market prices on list items
    print()
def transforming():
    #transforming market's infos into intended data structure
    print()
def loading():
    #loading data into database
    print()

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
    schedule_interval='0 * * * *',#setup hourly 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['cs2', 'etl', 'spark'],
) as dag:
    extract_task = PythonOperator(
        task_id='extract_task',
        python_callable=extract_inventory,
        provide_context=True
    )

    fetch_task = PythonOperator(
        task_id='fetch_task',
        python_callable=fetch_market_prices,
        provide_context=True
    )

    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=transform_data,
        provide_context=True
    )

    load_task = PythonOperator(
        task_id='load_task',
        python_callable=load_data,
        provide_context=True
    )

    extract_task >> fetch_task >> transform_task >> load_task