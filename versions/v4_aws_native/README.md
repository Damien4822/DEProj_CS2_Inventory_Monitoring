# DRAFT: V4 – AWS-Native Distributed Pipeline

## Overview

V4 represents the latest iteration of the distributed CS2 Inventory Monitoring pipeline. Building upon the cloud-distributed architecture introduced in V3, this version focuses on adopting AWS-managed infrastructure services and refining the system's data model to improve maintainability and support future development.

The overall processing workflow remains largely unchanged. Inventory data is collected from multiple external platforms, distributed across worker nodes for parallel processing, transformed into a normalized representation, and stored using dedicated persistence layers. Rather than introducing a new processing model, V4 focuses on improving the underlying infrastructure and data organization.

The primary architectural changes in V4 include:
- Migration from self-managed infrastructure services to AWS-managed services.
- Redesign of the relational database schema to improve data organization.
- Continued use of distributed, stateless worker nodes for parallel execution.
- Preservation of the asynchronous message-driven processing model established in previous versions.

The pipeline is designed to:
- Extract inventory and market data from multiple external sources.
- Distribute workloads across independent worker instances.
- Process and normalize market data in parallel.
- Store both structured and raw datasets using dedicated storage systems.
- Evaluate distributed processing using AWS-native infrastructure.
>**Note**
>
>V4 retains the layered architectural layout introduced in V3 to maintain consistency throughout the project's evolution. Development of this version is still ongoing, and some implementation details are not yet documented. This README will be updated progressively as additional components and architectural decisions are finalized.`
---

# Architecture Goals
The V4 architecture is designed around the following objectives:

- Maintain a modular layered architecture.
- Reduce infrastructure management through AWS-managed services.
-Preserve distributed worker execution.
- Support independent horizontal scaling of worker nodes.
- Improve data organization through a redesigned relational schema.
- Provide a foundation for future cloud-native enhancements.

# System Architecture

``` 
diagram in-making
```

## Airflow (Orchestration Layer)

Apache Airflow continues to serve as the workflow orchestration platform for the pipeline. Compared with V3, Airflow's responsibilities have been simplified to focus on workflow coordination rather than task execution.

### Responsibilities
- Scheduling pipeline execution.
- Generating inventory processing tasks.
- Coordinating workflow dependencies.
- Enqueuing processing jobs into the message queue.
- Monitoring pipeline execution.

### Architectural Changes

In V3, Airflow workers executed browser automation tasks responsible for obtaining authentication cookies using the CeleryExecutor.

In V4, login automation has been decoupled from Airflow and is executed as a dedicated service running on AWS ECS. Airflow now invokes this service as part of the workflow while remaining responsible only for orchestration.

This separation reduces the workload performed by Airflow workers and better aligns Airflow with its intended role as a workflow orchestrator rather than an execution platform.

## Workers (Execution Layer)
Workers are stateless processing services responsible for executing inventory processing jobs independently of the orchestration layer.

Responsibilities include:

- Consuming jobs from the message queue.
- Retrieving authentication data.
- Fetching inventory and market data from external platforms.
- Transforming and normalizing responses.
- Persisting processed data through the persistence layer.

### Batch Processing

Workers continue to process inventory items in batches, allowing multiple items to be processed within a single execution cycle. This reduces queue communication overhead while maintaining parallel execution across multiple worker instances.

Workers remain horizontally scalable and can be replicated independently to increase processing throughput.

## Data Storage
### Relational Database 
#### V3 Design

In V3, market data was stored using a denormalized snapshot table.

The schema combined item information, timestamp information, and market-specific measurements into a single table.

Example structure:

```
item_price_snapshots

- market_hash_name
- snapshot_time

- steam_price
- steam_median_price
- steam_volume

- buff_price
- buff_median_price
- buff_volume
```

Each record represented an item's market state at a specific point in time.

Example:

```
Item              Time        Steam Price   Buff Price
------------------------------------------------------
AK-47 Redline     10:00       15.00         14.50
AK-47 Redline     11:00       15.20         14.70
```

This approach was suitable for the initial implementation because the number of marketplaces was limited and ingestion logic remained simple.

However, the schema tightly coupled market sources with the table structure. Adding additional marketplaces would require introducing new columns for each market. As the number of supported sources grows, this structure becomes harder to maintain and extend.

#### V4 Schema Redesign

V4 redesigns the relational schema by separating inventory entities, market sources, and market observations.

The redesign focuses on price monitoring rather than building a complete CS2 item metadata database.

The primary relationship becomes:

```
Inventory Item
       |
       |
Price Snapshot
       |
       |
Market Source
```

The main entities are:

##### Inventory Item

Represents an item being monitored.

Stores information required to identify and track the item.

Example:

```
inventory_items

- item_id
- market_hash_name
```

---

##### Market Source

Represents external marketplaces where prices are collected.

Example:

```
market_sources

- market_id
- market_name
```

Examples:

- Steam
- BUFF163

---

##### Price Snapshot

Represents a price observation collected from a specific market at a specific time.

Example:

```
price_snapshots

- snapshot_id
- item_id
- market_id
- price
- median_price
- volume
- snapshot_time
```

This allows the same item to have multiple observations across different markets and time periods.

Example:

```
Item              Market      Price      Time
------------------------------------------------
AK-47 Redline     Steam       15.00      10:00
AK-47 Redline     BUFF        14.50      10:00
AK-47 Redline     Steam       15.20      11:00
AK-47 Redline     BUFF        14.70      11:00
```

#### Fact-Dimension Modeling Approach

The V4 schema adopts selected concepts from dimensional modeling by separating descriptive entities from measurable observations.

The current model consists of:

##### Dimensions

Entities that describe the context of an observation.

```
Inventory Item

Market Source
```

##### Facts

Time-dependent measurements collected from external sources.

```
Price Snapshot

- Price
- Median Price
- Volume
- Timestamp
```

The current implementation does not introduce a dedicated analytical warehouse layer. Instead, it stores granular observations that can later be aggregated for analytical purposes.

Examples of future analysis:

- Average price over a time period.
- Price trends.
- Market comparison.
- Price volatility.

#### Future Market Data Expansion

Although the current scope focuses on price monitoring, the schema is designed to allow additional market observations to be introduced in future iterations.

Potential extensions include:

```
Inventory Item

    |
    +---- Price Snapshot
    |
    +---- Demand Snapshot
    |
    +---- Listing Snapshot
    |
    +---- Transaction History
```

Possible future measurements:

- Buy demand.
- Sell availability.
- Market volume.
- Transaction history.

These can be represented as additional fact tables while keeping the existing item and market relationships unchanged.

---

#### Benefits of the Redesign

The V4 schema redesign provides:

- Reduced duplication of market-related data.
- Easier integration of additional marketplaces.
- Clear separation between entities and observations.
- Improved support for historical price tracking.
- A foundation for future analytical workloads.

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
