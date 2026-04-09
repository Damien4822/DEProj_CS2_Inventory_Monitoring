FROM apache/airflow:3.0.6

USER root
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 \
    libgtk-3-0 libxss1 libcurl4 fonts-liberation lsb-release \
    wget ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt /requirements.txt
RUN mkdir -p /opt/airflow/logs \
    /opt/airflow/plugins \
    /opt/airflow/dags \
    && chown -R airflow:root /opt/airflow
USER airflow

COPY --chown=airflow:root simple_auth_manager_passwords.json.generated /opt/airflow/simple_auth_manager_passwords.json.generated
COPY --chown=airflow:root /pipelines/ /opt/airflow/dags/v2/
COPY --chown=airflow:root /rabbitMQ/ /opt/versions/v3_cloud_deploy/rabbitMQ/
COPY --chown=airflow:root /storage/ /opt/versions/v3_cloud_deploy/storage/