from sources.steam import get_steam_market_price
from sources.buff import get_buff_market_price
from storage.mongo_client import insert_document
from storage.postgres_client import insert_price_snapshot
from datetime import datetime, UTC
import time
import random


def process_item(item: dict):

    market_hash_name = item["market_hash_name"]

    result = {
        "item": market_hash_name,
        "sources": {}
    }

    # ---------- Steam ----------
    try:

        steam_data, steam_raw = get_steam_market_price(market_hash_name)

        if steam_data:
            result["sources"]["steam"] = steam_data
            result.setdefault("raw", {})["steam"] = steam_raw

    except Exception as e:
        print(f"Steam error: {e}")

    time.sleep(random.uniform(1, 2))


    # ---------- Buff ----------
    try:
        buff_data, buff_raw = get_buff_market_price(market_hash_name)

        if buff_data:
            result["sources"]["buff"] = buff_data
            result.setdefault("raw", {})["buff"] = buff_raw
    except Exception as e:
        print(f"Buff error: {e}")

    time.sleep(random.uniform(1, 2))


    # ---------- Save raw ----------
    insert_document("market_raw", {
        "item": market_hash_name,
        "timestamp": datetime.now(UTC),
        "sources": result.get("raw", {})
    })
    print(f"Saved data for {market_hash_name}")
    # ---------- Save schema -------
    steam = result["sources"].get("steam", {})
    buff = result["sources"].get("buff", {})

    insert_price_snapshot(
        market_hash_name,
        steam_price=steam.get("lowest_price"),
        steam_median=steam.get("median_price"),
        steam_volume=steam.get("volume"),

        buff_price=buff.get("lowest_price"),
        buff_median=buff.get("median_price"),
        buff_volume=buff.get("volume"),
    )

    print(f"Saved structured data for {market_hash_name}")