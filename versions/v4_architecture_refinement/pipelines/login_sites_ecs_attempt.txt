from datetime import datetime,timedelta
from airflow.sdk import DAG
from airflow.decorators import task
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow.providers.amazon.aws.operators.ecs import ECSOperator
import os

logger = LoggingMixin().log
default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    "pool": "default_pool",
    'retry_delay': timedelta(minutes=5),
    "priority_weight": 10
}
with DAG(
    'login_sites_v3',
    default_args=default_args,
    description='Trigger ECS Playwright job to login and fetch cookies',
    schedule='0 */6 * * *',#setup to run every 6hours 
    max_active_runs=1,
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['login', 'playwright','ecs','v3'],
) as dag:
    run_playwright_on_ecs = ECSOperator(
        task_id="run_playwright_login",
        cluster=os.getenv("ECS_CLUSTER_NAME"),
        task_definition="playwright-task",
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": "login-container",
                    "environment": [
                        {
                            "name": "STEAM_USERNAME",
                            "value": os.getenv("STEAM_USERNAME"),
                        },
                        {
                            "name": "STEAM_PASSWORD",
                            "value": os.getenv("STEAM_PASSWORD"),
                        },
                    ],
                }
            ]
        },
    )