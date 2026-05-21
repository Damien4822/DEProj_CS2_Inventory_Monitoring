import requests
from urllib.parse import quote
from storage.redis_client import get_cookies_dict
import time
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}
def _get_buff_cookies(retries=5, delay=2):
    for attempt in range(retries):
        cookies = get_cookies_dict("buff")

        if cookies:
            return cookies

        print("[Buff] Redis not ready, retrying...")
        time.sleep(delay)

    raise Exception("Buff cookies not found in Redis after retries")

def get_buff_market_price(market_hash_name, logger):
    cookies = _get_buff_cookies()
    
    base_url = "http://buff.163.com/api/market/goods"
    url = base_url + f"?game=csgo&page_num=1&search=" + quote(market_hash_name)

    resp = requests.get(url, headers=HEADERS, cookies=cookies)
    resp.raise_for_status()
    
    if (resp.status_code != 200):
        logger.info(f"Fetching {market_hash_name} from BUFF failed")
    else:
        data = resp.json()
        processed_data = {
        market_hash_name: {
            "lowest_price": None,
            "median_price": None,
            "volume": None
        }
    }

    items = data.get("data", {}).get("items", [])

    for item in items:
        if item.get("market_hash_name") == market_hash_name:
            processed_data[market_hash_name] = {
                "lowest_price": item.get("sell_min_price"),
                "median_price": item.get("quick_price"),
                "volume": item.get("sell_num")
            }
            break

    logger.info(f"Finish fetching {market_hash_name} from BUFF")

    return processed_data, data
