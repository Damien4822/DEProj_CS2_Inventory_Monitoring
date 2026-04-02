#!/bin/bash

echo "[Worker] Waiting for infra services..."

# RabbitMQ
until nc -z rabbitmq 5672; do
    echo "[Worker] Waiting for RabbitMQ..."
    sleep 2
done

# Redis
until nc -z redis 6379; do
    echo "[Worker] Waiting for Redis..."
    sleep 2
done

# MongoDB
until nc -z mongo 27017; do
    echo "[Worker] Waiting for MongoDB..."
    sleep 2
done

# Postgres
until nc -z postgres 5432; do
    echo "[Worker] Waiting for Postgres..."
    sleep 2
done

echo "[Worker] All services ready, starting worker..."
exec python -m worker.worker