import requests
from urllib.parse import quote
from storage.redis_client import get_cookies_dict
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}


def get_buff_market_price(market_hash_name):
    cookies = get_cookies_dict("buff")

    if not cookies:
        raise Exception("Buff cookies not found in Redis")
    
    base_url = "https://buff.163.com/api/market/goods"

    url = base_url + f"?game=csgo&page_num=1&search=" + quote(market_hash_name)

    resp = requests.get(url, headers=HEADERS, cookies=cookies)

    resp.raise_for_status()

    data = resp.json()

    if "data" not in data or not data["data"]["items"]:
        return None

    return data