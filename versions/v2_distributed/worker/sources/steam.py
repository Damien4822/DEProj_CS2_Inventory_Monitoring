import requests
from urllib.parse import quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}


def get_steam_market_price(market_hash_name, logger):

    url = (
        "http://steamcommunity.com/market/priceoverview/"
        f"?appid=730&currency=1"
        f"&market_hash_name={quote(market_hash_name)}"
    )

    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        return None

    prices = {
        "lowest_price": data.get("lowest_price","").replace("$",""),
        "median_price": data.get("median_price","").replace("$",""),
        "volume": data.get("volume","")
    }
    logger.info(f"Finish fetching {market_hash_name} from STEAM")
    return prices, data