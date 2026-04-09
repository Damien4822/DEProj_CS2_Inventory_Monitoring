# V2 – Distributed Pipeline Architecture

## Overview

V2 represents a redesigned and production-oriented implementation of the CS2 Inventory Monitoring pipeline.

This version transitions from a monolithic prototype (V1) to a distributed system, enabling improved scalability, fault tolerance, and extensibility.

The pipeline is designed to:

- Extract inventory and market data from multiple external sources.
- Distribute workload across multiple worker instances.
- Process and normalize data in parallel.
- Persist structured data into centralized storage systems.
- Operate reliably under higher data volumes and API constraints.
---

# Architecture Characteristics
V2 adopts a distributed components approach:

- Pipeline responsibilities are separated into independent services.
- Worker instances scale horizontally via Docker Compose.
- Tasks are processed asynchronously using a message queue.
- External services are used for persistence and coordination.
- Each component can scale independently.

# System Architecture

```
+---------------------------+                         +----------------------+
|      Infrastructure       |                         |                      |
|                           |                         |                      |
|      +-------------+      |         (job queue)     |                      | 
|      |   RabbitMQ  |<------------------------------+|                      |
|      +------+------+      |                         |                      |
|           /|\             |                         |                      |
|            |(items)       |                         |                      |   
|            |              |                         |                      |
|  +--------------------+   |                         |  +----------------+  |
|  | Item fetching DAG  |   |                         |  |    Worker      |  |
|  +--------------------+   |                         |  |   Instances    |  |
|                           |                         |  |                |  |
|                           |                         |  +----------------+  |
|  +---------------------+  |                         |  +----------------+  |
|  |   Login DAG         |  |                         |  |   Worker       |  |
|  +----------+----------+  |                         |  |   Instances    |  |
|             |             |                         |  |                |  |
|             | (cookies)   |                         |  +--------+-------+  |
|             |             |                         |                      |
|             |             |                         |                      |
|             |             |                         |                      |
|             v             |                         |                      |
|      +-------------+      |                         |                      |
|      |    Redis    |<------------------------------+|                      |
|      +------+------+      |    (cookies)            |                      |
|                           |                         |                      |
|                           |                         |                      |           
|      +-------------+      |                         |                      |
|      |   MongoDB   |<------------------------------+|                      |
|      +-------------+      |    (raw responses)      |                      |
|                           |                         |                      |
|      +-------------+      |                         |                      |
|      | PostgreSQL  |<------------------------------+|                      |
|      +-------------+      |    (structured data )   |                      |
+---------------------------+                         +----------------------+

```

## Key Components
### Airflow (Orchestration Layer)
Responsible for:
- Generating and enqueueing tasks (e.g., inventory items) 
- Perform UI Automation for login and storing authentication cookies.
- Enqueuing inventory items into the message queue

Note: for new infra-setup, Airflow now being distributed with multiple components (apiserver, scheduler, worker, triggerer, dag-processor) with CeleryExecutor.

### Workers (Execution Layer)
Stateless processing units that:
- Consume tasks from RabbitMQ
- Retrieve authentication cookies from Redis
- Fetch market data (Steam, BUFF163)
- Transform and normalized responses
- Store results to MongoDB and PostgresSQL
Workers are horizontally scalable and can be replicated as needed

### Data Storage
- PostgreSQL: stores structured data such as normalized price snapshots
- MongoDB: stores raw API responses
- Redis: stores session data (e.g., authentication cookies)

Note: for new infra-setup, PostgresSQL are having 2 instances of `postgres` and `airflow-postgres`:
- `postgres` still function as stated above.
- `airflow-postgres` stores Airflow's metadata infos.

### Message Broker - RabbitMQ
- Decouples task producers and consumers
- Enables asynchronous processing and retry mechanisms

Note: for new infra-setup, rabbitMQ is now containing channels for CeleryExecutor.

### Container Orchestration - Docker Compose
- Manages service deployment.
- Provides internal networking and service discovery.
- Simplifies local development and testing.

Note: 
- For new infra-setup, Airflow components are now being distributed with healthcheck, dependencies condition, separated volumes with the same network configuration.
- Dedicated Postgres container for Airflow (`airflow-postgres`) keeps metadata isolated.
- Redis remains shared for app cookies only.
- RabbitMQ now handles both CeleryExecutor and custom task queues.
---

## Design Decisions

This version was built as a prototype to validate key architectural concepts:
- Task Distribution using rabbitMQ.
- Externalized state management with redis.
- Separation of orchestration, execution, and storage layers.
- Parallel data fetching via distributed workers.
- Dual-storage strategy: PostgreSQL for structured data; MongoDB for raw responses.
- Containerized deployment using Docker Compose.
---

## Installation (V2)

This version was developed and tested in a local Linux environment.
The components required docker + docker compose installed.

### 1. Deploy Infrastructure Services

```bash
cd v3_cloud_deploy/infra
docker compose build
docker compose up -d
```

### 2. Deploy workers
Navigate to v3_cloud_deploy/worker/

```bash
cd v3_cloud_deploy/worker
docker compose build
docker compose up -d
```
or if u want to deploy with replicates:
```
docker compose up -d --scale worker=3
```

## Improvements and Limitations

### Improvements over V1:

#### 1. Separation of Concersn
Orchestration, task distribution, execution, and storage are fully decoupled, enabling independent scaling and development.

#### 2. Asynchronous Task Processing
Tasks are distributed via RabbitMQ and consumed by workers, enabling horizontal scalability.

#### 3. Parallel Data Fetching (Fan-Out Pattern)
Each worker performs multiple external API calls per item (e.g., Steam Market, BUFF163), improving throughput. Workers can be replicated into multiple instances, increasing data-ingestion effeciency and throughput.

### Limitations:
Despite architectural improvements, some constraints remain:

#### Rate Limiting: 
External APIs still enforce request limits, which are amplified when scaling workers. High parallelism increases the likelihood of hitting API limits or receiving temporary bans.

#### Network Constraints
Running locally means all requests originate from a limited set of IP addresses. While scaling workers improves throughput, it also increases the risk of rate-limiting or temporary IP blocks from source platforms.

These limitations motivated the design of V3, where:
- Core infrastructure remains centralized.
- Workers are deployed in cloud environments with distributed public IPs
- Public IP distribution helps reduce rate-limit bottlenecks and ensures more reliable external API access.
---

## Output Artifacts

Workers generate execution logs locally.
Sample logs files are included for documentation and examples purposes only, under `v3_cloud_deploy/worker/logs/` 
Runtime-generated files are excluded from version control.

---

## Purpose of V2

V2 serves as:

- A validated implementation of a distributed data pipeline
- A baseline for architectural comparison with future versions (V3)
- A proof-of-concept for scalability and system design

It is intentionally preserved as a stable snapshot of the first fully working distributed architecture.