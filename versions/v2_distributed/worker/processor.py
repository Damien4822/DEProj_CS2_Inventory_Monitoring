from sources.steam import get_steam_market_price
from sources.buff import get_buff_market_price
from storage.mongo_client import insert_document

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

        steam_data = get_steam_market_price(market_hash_name)

        if steam_data:
            result["sources"]["steam"] = steam_data

    except Exception as e:
        print(f"Steam error: {e}")

    time.sleep(random.uniform(1, 2))


    # ---------- Buff ----------
    try:
        buff_data = get_buff_market_price(market_hash_name)

        if buff_data:
            result["sources"]["buff"] = buff_data

    except Exception as e:
        print(f"Buff error: {e}")

    time.sleep(random.uniform(1, 2))


    # ---------- Save raw ----------
    insert_document("market_raw", result)

    print(f"Saved data for {market_hash_name}")