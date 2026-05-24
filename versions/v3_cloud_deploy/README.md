# V3 – Cloud-Distributed Pipeline Architecture

## Overview

V3 represents the cloud-deployed evolution of the distributed CS2 Inventory Monitoring pipeline.

Building on the distributed architecture introduced in V2, this version focuses on improving throughput, scalability testing, and distributed execution reliability under real-world deployment conditions.

The primary architectural enhancement in V3 is the transition from:
- Single-item task processing → Batch-oriented worker execution
- Local-only deployment → Multi-instance cloud deployment on AWS

The pipeline is designed to:
- Extract inventory and market data from multiple external sources.
- Distribute workloads across geographically separated worker instances.
- Improve ingestion throughput using batch-processing strategies.
- Process and normalize data in parallel.
- Persist structured and raw data into centralized storage systems.
- Validate distributed-worker scalability under cloud infrastructure.
---

# Architecture Characteristics
V3 continues the distributed-service architecture introduced in V2, while extending it with cloud deployment and worker-level batching optimizations.

Key characteristics include:

- Independent services for orchestration, execution, storage, and coordination.
- Horizontally scalable worker nodes deployed across multiple AWS EC2 instances.
- Batch-oriented task consumption to improve processing efficiency.
- Centralized infrastructure services with distributed worker execution.
- Asynchronous processing via RabbitMQ.
- Containerized deployment using Docker Compose.

# System Architecture

```
+-------------------------------+                         +----------------------+
|      Infrastructure           |                         |                      |
|( High-resources EC2 Instance )|                         |                      |
|      +-------------+          |         (job queue)     |                      | 
|      |   RabbitMQ  |<----------------------------------+|                      |
|      +------+------+          |                         |                      |
|           /|\                 |                         |                      |
|            |(items)           |                         |                      |   
|            |                  |                         |                      |
|  +--------------------+       |                         |  +----------------+  |
|  | Item fetching DAG  |       |                         |  |    Worker      |  |
|  +--------------------+       |                         |  |   Instances #1 |  |
|                               |                         |  | (EC2 Instance) |  |
|                               |                         |  +----------------+  |
|  +---------------------+      |                         |  +----------------+  |
|  |   Login DAG         |      |                         |  |   Worker       |  |
|  +----------+----------+      |                         |  |   Instances #2 |  |
|             |                 |                         |  | (EC2 Instance) |  |
|             | (cookies)       |                         |  +--------+-------+  |
|             |                 |                         |                      |
|             |                 |                         |                      |
|             |                 |                         |                      |
|             v                 |                         |                      |
|      +-------------+          |                         |                      |
|      |    Redis    |<----------------------------------+|                      |
|      +------+------+          |    (cookies)            |                      |
|                               |                         |                      |
|                               |                         |                      |           
|      +-------------+          |                         |                      |
|      |   MongoDB   |<----------------------------------+|                      |
|      +-------------+          |    (raw responses)      |                      |
|                               |                         |                      |
|      +-------------+          |                         |                      |
|      | PostgreSQL  |<----------------------------------+|                      |
|      +-------------+          |    (structured data )   |                      |
+-------------------------------+                         +----------------------+

```

## Key Components
### Airflow (Orchestration Layer)
Responsible for:
- Generating and enqueueing tasks (e.g., inventory items) 
- Perform UI Automation for login and storing authentication cookies into Redis.
- Enqueuing inventory items into the message queue
- Coordinating scheduled execution pipelines.
- Managing distributed DAG execution using CeleryExecutor.

#### Airflow Deployment
Airflow is deployed as distributed components:
- API Server
- Scheduler
- Worker
- Triggerer
- DAG Processor

Additional infrastructure improvements:
- Dedicated airflow-postgres instance for Airflow metadata isolation.
- Health checks and dependency-aware container startup.
- Shared Docker networking across all components.

### Workers (Execution Layer)
Workers are stateless processing services deployed on separate EC2 instances.

Responsibilities include:
- Consuming jobs from RabbitMQ.
- Retrieving authentication cookies from Redis.
- Fetching market data from external platforms (Steam, BUFF163).
- Transforming and normalizing responses.
- Persisting raw responses into MongoDB.
- Persisting structured datasets into PostgreSQL.

#### Batch Processing Enhancement

Unlike V2, where each worker processed one inventory item per queue message, V3 introduces batch-oriented task execution.

Workers now:
- Pull batches of inventory items per job.
- Process multiple items in a single execution cycle.
- Reduce queue-consumption overhead.
- Improve throughput efficiency while preserving parallel worker scalability.

Current testing configuration uses small batch sizes (e.g., 20 items per batch) to better balance:
- Inventory size constraints
- Parallel worker distribution
- External API rate-limit behavior

Workers remain horizontally scalable and can be replicated independently.

### Data Storage
#### PostgreSQL

Stores normalized and structured datasets such as:
- Price snapshots
- Inventory metadata
- Aggregated market information

#### MongoDB

Stores raw API responses for:
- Auditing
- Reprocessing
- Debugging
- Historical response preservation

#### Redis

Stores transient session state:
- Authentication cookies
- Runtime coordination data

#### Airflow Metadata Database
A dedicated PostgreSQL instance (airflow-postgres) stores Airflow operational metadata separately from application data.

### Message Broker - RabbitMQ
RabbitMQ serves as the asynchronous communication layer between orchestration and worker services.

Responsibilities:

- Queue-based task distribution
- Retry handling
- Worker decoupling
- CeleryExecutor communication channels
- Batch-job dispatching

### Container Orchestration - Docker Compose
Docker Compose continues to manage:

- Service deployment
- Internal networking
- Container lifecycle management
- Environment configuration

Infrastructure and worker deployments are separated into dedicated deployment stacks for improved operational management.

### Cloud Infrastructure – AWS EC2
V3 introduces distributed cloud deployment using multiple AWS EC2 instances.

Current deployment topology:
#### Infrastructure Node
A higher-resource EC2 instance hosting:
- Airflow
- RabbitMQ
- Redis
- MongoDB
- PostgreSQL

This node acts as the centralized coordination and persistence layer.

#### Worker Nodes

Multiple lower-resource EC2 instances hosting worker containers only.

This design reflects the workload characteristics:
- Infrastructure services require higher RAM and CPU resources.
- Workers are primarily lightweight single-threaded processing units.
- Horizontal scaling is achieved by increasing worker-node count.

This deployment validates the effectiveness of distributed worker execution across separate public cloud instances.
---

## Design Decisions
V3 was designed to validate:
- Distributed cloud execution across multiple EC2 instances.
- Batch-processing efficiency improvements.
- Horizontal worker scalability.
- Centralized infrastructure with distributed execution nodes.
- Real-world ingestion throughput improvements.
- Improved queue utilization under parallel workloads.

The architecture intentionally preserves centralized infrastructure services while distributing execution workloads across multiple public cloud instances.
---

## Installation (V3)
This version was developed and tested using AWS EC2 Linux instances.

The components require:
- Docker
- Docker Compose
Note: The below docker composes using same .env files for system-variables. You can defined your variables with existing examples under v3_cloud_deploy/infra/env.example

### 1. Deploy Infrastructure Services
On Infrastructure Instances:

```bash
cd v3_cloud_deploy/infra
docker compose build
docker compose up -d
```
This deploys:
- Airflow services
- RabbitMQ
- Redis
- MongoDB
- PostgreSQL

### 2. Deploy Worker Instances
On Worker Instance:
Navigate to v3_cloud_deploy/worker/

```bash
cd v3_cloud_deploy/worker
docker compose build
docker compose up -d
```
Note: each Worker Instaces should only have 1 Worker service.

## Improvements and Limitations

### Improvements over V2:
#### 1. Batch-Oriented Processing

Workers now process multiple inventory items per execution cycle, significantly reducing queue overhead and improving ingestion throughput.

#### 2. Cloud-Distributed Deployment

Execution workloads are distributed across multiple AWS EC2 instances, enabling:
- Better workload isolation
- Distributed public IP usage
- Improved scalability testing
- Reduced single-host bottlenecks

#### 3. Improved Horizontal Scalability
Worker nodes can now scale independently from infrastructure services, making the architecture more production-oriented and cloud-compatible.

#### 4. Better Throughput Efficiency
Batch consumption reduces:
- Queue communication overhead
- Repeated setup costs
- Worker idle time

Resulting in improved ingestion efficiency under parallel workloads.

### Limitations:
Despite architectural improvements, some constraints remain:

#### Rate Limiting: 
External APIs still enforce request limits, which are amplified when scaling workers. High parallelism increases the likelihood of hitting API limits or receiving temporary bans.

#### Infrastructure Centralization

Core infrastructure services remain hosted on a single EC2 instance.

This creates potential:
- Single points of failure
- Resource bottlenecks
- Infrastructure scaling limitations

Future versions aim to migrate these services into managed AWS-native infrastructure components.

#### Manual Infrastructure Management

Docker Compose simplifies deployment, but operational management remains largely manual compared to fully managed orchestration platforms.
---

## Output Artifacts

Workers generate execution logs locally.
Sample logs files are included for documentation and examples purposes only, under `v3_cloud_deploy/worker/logs/` 
Runtime-generated files are excluded from version control.

---
## Future Direction

V3 serves as a transitional architecture toward a more cloud-native design.

Future iterations are expected to migrate centralized infrastructure services into AWS-managed solutions such as:
- Amazon RDS
- Amazon MQ
- Amazon ElastiCache
- Container orchestration platforms

This would further improve:
- Scalability
- Reliability
- Operational simplicity
- Fault tolerance

---
## Purpose of V2
V3 serves as:
- A cloud-deployed distributed pipeline implementation
- A scalability validation environment
- A benchmark for distributed ingestion performance
- A transition stage toward cloud-native infrastructure
- A proof-of-concept for distributed worker execution using public cloud infrastructure

It is intentionally preserved as a stable architectural milestone before migrating toward fully managed cloud infrastructure services.