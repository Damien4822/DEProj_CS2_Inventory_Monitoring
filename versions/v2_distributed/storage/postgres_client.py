import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

# Create connection pool

pool = None

def get_pool():
    global pool
    if pool is None:
        pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=5
        )
    return pool
def get_connection():
    return get_pool().getconn()


def release_connection(conn):
    pool.putconn(conn)

def insert_price_snapshot(
    market_hash_name,
    steam_price=None,
    steam_median=None,
    steam_volume=None,
    buff_price=None,
    buff_median=None,
    buff_volume=None
):
    conn = None
    try:
        conn = get_connection()

        if conn.closed != 0:
            conn = get_connection()

        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO item_price_snapshots (
                    market_hash_name,
                    steam_price,
                    steam_median_price,
                    steam_volume,
                    buff_price,
                    buff_median_price,
                    buff_volume
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                market_hash_name,
                steam_price,
                steam_median,
                steam_volume,
                buff_price,
                buff_median,
                buff_volume
            ))

        conn.commit()

    except Exception as e:
        if conn:
            conn.rollback()
        raise

    finally:
        if conn:
            release_connection(conn)