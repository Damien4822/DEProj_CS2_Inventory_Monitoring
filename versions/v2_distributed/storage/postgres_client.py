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


def get_connection():
    return pool.getconn()


def release_connection(conn):
    pool.putconn(conn)


def insert_request(site: str, status: int):

    conn = None
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO requests_log (site, status)
                VALUES (%s, %s)
                """,
                (site, status)
            )

        conn.commit()

    finally:
        if conn:
            release_connection(conn)


def fetch_requests():

    conn = None

    try:
        conn = get_connection()

        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT * FROM requests_log ORDER BY id DESC"
            )

            return cursor.fetchall()

    finally:
        if conn:
            release_connection(conn)


def close_pool():
    pool.closeall()