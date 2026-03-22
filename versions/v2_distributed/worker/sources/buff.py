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


def get_buff_market_price(market_hash_name):
    for attempt in range(5):
        cookies = get_cookies_dict("buff")
        if cookies:
            break
        print("[Buff] Redis not ready, retrying...")
        time.sleep(2)
    else:
        raise Exception("Buff cookies not found in Redis after retries")

    if not cookies:
        raise Exception("Buff cookies not found in Redis")
    
    base_url = "https://buff.163.com/api/market/goods"
    url = base_url + f"?game=csgo&page_num=1&search=" + quote(market_hash_name)

    resp = requests.get(url, headers=HEADERS, cookies=cookies)
    resp.raise_for_status()

    data = resp.json()
    
    if "data" not in data or not data["data"]["items"]:
        return None
    processed_data = {
        market_hash_name: {
            "lowest_price": data["data"]["items"]['sell_min_price'],
            "median_price": data["data"]["items"]['quick_price'],
            "volume": str(data["data"]["items"]["sell_num"])
        }
    }   
    return processed_data, data
