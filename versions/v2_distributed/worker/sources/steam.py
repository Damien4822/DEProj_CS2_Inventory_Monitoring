import requests
from urllib.parse import quote

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}


def get_steam_market_price(market_hash_name, appid=730, currency=1):

    url = (
        "http://steamcommunity.com/market/priceoverview/"
        f"?appid={appid}&currency={currency}"
        f"&market_hash_name={quote(market_hash_name)}"
    )

    resp = requests.get(url, headers=HEADERS, timeout=10)

    resp.raise_for_status()

    data = resp.json()

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