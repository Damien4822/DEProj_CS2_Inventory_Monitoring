from worker.sources.steam import get_steam_market_price
from worker.sources.buff import get_buff_market_price
from datetime import datetime, UTC
import time
import random
import traceback

def process_item(item: dict, logger):

    market_hash_name = item["market_hash_name"]

    result = {
        "item": market_hash_name,
        "sources": {}
    }

    # ---------- Steam ----------
    try:

        steam_data, steam_raw = get_steam_market_price(market_hash_name, logger)

        if steam_data:
            result["sources"]["steam"] = steam_data
            result.setdefault("raw", {})["steam"] = steam_raw

    except Exception as e:
        logger.info(f"Steam error: {e}")

    time.sleep(random.uniform(1, 3))


    # ---------- Buff ----------
    try:
        buff_data, buff_raw = get_buff_market_price(market_hash_name, logger)
    
        if buff_data:
            result["sources"]["buff"] = buff_data
            result.setdefault("raw", {})["buff"] = buff_raw
    except Exception as e:
        logger.info(f"Buff error: {e}\n{traceback.format_exc()}")

    time.sleep(random.uniform(1, 3))

    return result