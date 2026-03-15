FROM apache/airflow:3.0.0

USER root

# Install system dependencies if needed (Playwright often needs these)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean

USER airflow

# Install python dependencies
COPY ../../../airflow/requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

# Install playwright browsers if using playwright
RUN playwright install chromium