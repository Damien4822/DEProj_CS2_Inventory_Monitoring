FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY worker ./worker
COPY rabbitMQ ./rabbitMQ
COPY storage ./storage

ENV PYTHONPATH=/app
RUN mkdir -p /app/worker/logs

RUN chmod +x wait-for-infra.sh

# Run the wait script first, then start the worker
CMD ["./wait-for-infra.sh"]