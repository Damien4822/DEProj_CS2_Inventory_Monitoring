FROM apache/airflow:3.0.1

USER root

# Install system dependencies
RUN apt update 
RUN python3 -m pip install playwright
RUN python3 -m playwright install --with-deps
COPY infra/requirements.txt /requirements.txt

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt

