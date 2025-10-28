from datetime import datetime,timedelta
from airflow import DAG

def extracting():
    #fetch list of cs2 items in one inventory, then fetch market prices on list items
    print()
def transforming():
    #transforming market's infos into intended data structure
    print()
def loading():
    #loading data into database
    print()
default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
with DAG(
    'cs2_market_etl',
    default_args=default_args,
    description='ETL pipeline for CS2 Market data using Spark and Airflow',
    schedule_interval='0 * * * *',#setup hourly 
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['cs2', 'etl', 'spark'],
) as dag:
    extracting()
    transforming()
    loading()
    extracting >> transforming >> loading