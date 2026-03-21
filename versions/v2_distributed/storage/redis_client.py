import redis
import json
import os
import time
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

MAX_RETRIES = 5
RETRY_DELAY = 20

def create_redis_client():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True,
                socket_connect_timeout=5
            )
            client.ping()
            return client
        except redis.ConnectionError as e:
            print(f"[Redis] Attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY * attempt)

redis_client = create_redis_client()

def save_cookies(site: str, cookies: list):
    key = f"cookies:{site}"
    redis_client.set(
        key,
        json.dumps(cookies),
        ex=86400  # 1 day
    )


def get_cookies(site: str):
    key = f"cookies:{site}"
    data = redis_client.get(key)
    if not data:
        return None

    return json.loads(data)

def get_cookies_dict(site: str):
    """Convert stored cookie list → requests cookie dict"""

    cookies = get_cookies(site)

    if not cookies:
        return None

    return {c["name"]: c["value"] for c in cookies}