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
|  |   Login DAG        |   |                         |  |    Worker      |  |
|  +--------------------+   |                         |  |   Instances    |  |
|                           |                         |  |                |  |
|                           |                         |  +----------------+  |
|  +---------------------+  |                         |  +----------------+  |
|  |   Item-fetching DAG |  |                         |  |   Worker       |  |
|  +----------+----------+  |                         |  |   Instances    |  |
|             |             |                         |  |                |  |
|             | items       |                         |  +--------+-------+  |
|             |             |                         |                      |
|             |             |                         |                      |
|             |             |                         |                      |
|             v             |                         |                      |
|      +-------------+      |                         |                      |
|      |    Redis    |<------------------------------+|                      |
|      +------+------+      |    (cookies)            |                      |
|             |             |                         |                      |
|             v             |                         |                      |           
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

### Workers (Execution Layer)
Stateless processing units that:
- Consume tasks from RabbitMQ
- Fetch market data (Steam, BUFF163)
- Transform and normalized responses
- Store results
Workers are horizontally scalable and can be replicated as needed

### Data Storage
- PostgreSQL: stores structured data such as normalized price snapshots
- MongoDB: stores raw API responses
- Redis: stores session data (e.g., authentication cookies) and lightweight cache

### Message Broker - RabbitMQ
Decouples task producers and consumers
Enables asynchronous processing and retry mechanisms

### Container Orchestration - Docker Compose
- Manages service deployment
- Provides internal networking and service discovery
- Simplifies local development and testing
---

## Design Decisions

This version was built as a prototype to validate key architectural concepts:
- Task Distribution using rabbitMQ.
- Externalized state management with redis.
- Separation of orchestration, execution, and storage layers.
- Parallel data fetching via distributed workers
- Dual-storage strategy: PostgreSQL for structured data; MongoDB for raw responses.
- Containerized deployment using Docker Compose
---

## Installation (V2)

This version was developed and tested in a local Linux environment.
The components required docker + docker compose installed.

### 1. Deploy Infrastructure Services

```bash
cd v2_distributed/infra
docker compose build
docker compose up -d
```

### 2. Deploy workers
Navigate to v2_distributed/worker/
```bash
cd v2_distributed/worker
docker compose build
docker compose up -d
```

## Improvements and Limitations

### Improvements over V1:

#### 1. Separation of Concersn
Orchestration, task distribution, execution, and storage are fully decoupled, enabling independent scaling and development.

#### 2. Asynchronous Task Processing
Tasks are distributed via RabbitMQ and consumed by workers, enabling horizontal scalability.

#### 3. Parallel Data Fetching (Fan-Out Pattern)
Each worker performs multiple external API calls per item (e.g., Steam Market, BUFF163), improving throughput.

While the scalability of components achieved, the issue of Rate-limiting still exists, due to the current network setup. This issued motivated for implementation of V3, where the whole systems will be deployed onto Cloud Services. While the infra-components can be deployed and used internally, worker can still having benefited from these services's public IP, which avoid hitting rate-limit policies from these sources.

### Limitations:
Despite architectural improvements, some constraints remain:

#### Rate Limiting: 
External APIs still enforce request limits, which are amplified when scaling workers.

#### Network Constraints
Running locally means all requests originate from a limited set of IP addresses

These limitations motivated the design of V3, where:
- Infrastructure remains centralized
- Workers are deployed in cloud environments
- Public IP distribution reduces rate-limit bottlenecks
---

## Output Artifacts

Workers generate execution logs locally.
Sample logs files are included for documentation and examples purposes only, under `v2_distributed/worker/logs/` 
Runtime-generated files are excluded from version control.

---

## Purpose of V2

V2 serves as:

- A validated implementation of a distributed data pipeline
- A baseline for architectural comparison with future versions (V3)
- A proof-of-concept for scalability and system design

It is intentionally preserved as a stable snapshot of the first fully working distributed architecture.