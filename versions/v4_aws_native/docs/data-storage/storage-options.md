# Storage Architecture

## Overview

The pipeline uses different storage systems based on the type of data being handled.

Each storage component has a specific responsibility:

- MongoDB stores raw responses collected from external platforms.
- PostgreSQL stores processed and structured market data.
- Redis stores temporary authentication data shared with worker services.

This separation allows the pipeline to preserve original responses, maintain structured datasets, and provide shared authentication state for distributed workers.

---

# Storage Architecture Overview

```text
                    External Platforms
                           |
                           |
                           v

                  +----------------+
                  | Login Service  |
                  |                |
                  | Authentication |
                  +----------------+
                           |
                           |
                           v

                      +---------+
                      | Redis   |
                      |         |
                      | Cookies |
                      +---------+
                           |
                           |
                           v

                     Worker Services
                         |
             +-----------+-----------+
             |                       |
             v                       v

      +--------------+       +--------------+
      | MongoDB      |       | PostgreSQL   |
      |              |       |              |
      | Raw Response |       | Structured   |
      | Storage      |       | Data         |
      +--------------+       +--------------+
```

---

# Raw Response Storage

## Purpose

Raw response storage keeps the complete responses collected from external platforms.

The original responses are preserved for:

- Debugging processing issues.
- Reprocessing data with updated transformation logic.
- Auditing collected information.
- Maintaining historical external responses.

---

## Current Implementation

### MongoDB

MongoDB is currently used to store raw API responses.

A document database is suitable because external platform responses are received in JSON-like formats and may contain different structures between sources.

MongoDB stores the original responses, while the worker services extract and transform the required fields before inserting structured data into PostgreSQL.

---

# AWS Migration Considerations

As part of V4, the current self-managed MongoDB deployment is being evaluated for migration to AWS-managed services.

The main evaluation criteria are:

- Storage cost.
- Operational complexity.
- Data reprocessing requirements.
- Future pipeline development.

Potential options include:

---

## Amazon S3

Possible usage:

- Store raw API responses as JSON objects.
- Maintain historical ingestion data.
- Provide a foundation for future data processing workflows.

Advantages:

- Low-cost object storage.
- High durability.
- Commonly used as a raw data storage solution.

Considerations:

- Requires additional processing logic compared with a database.
- Less convenient for direct document querying.

---

## Amazon DocumentDB

Possible usage:

- Replace MongoDB with a managed document database service.

Advantages:

- Similar document-based storage model.
- Requires fewer application changes.

Considerations:

- Higher operational cost compared with object storage.
- May provide more database features than required for raw response storage.

---

## Amazon DynamoDB

Possible usage:

- Store raw responses using key-value access patterns.

Advantages:

- Fully managed AWS database.
- High scalability.

Considerations:

- Less suitable for storing flexible external API responses.
- Requires defining access patterns before implementation.

---

## Current Status

The final AWS replacement for MongoDB has not been selected.

The current implementation continues to use MongoDB while different AWS-managed alternatives are evaluated.

---

# Relational Data Storage

## Purpose

The relational database stores processed and structured data extracted from external platform responses.

Worker services are responsible for:

- Selecting required fields from external responses.
- Transforming data into the application data model.
- Inserting processed records into the relational database.

Stored information includes:

- Inventory items.
- Market sources.
- Price snapshots.

---

## Current Implementation

### PostgreSQL

PostgreSQL is currently used as the main relational database.

The worker services convert external responses into a structured format before insertion.

The relational database stores only the data required by the application instead of keeping the complete external response.

Example:

```text
External Response
        |
        |
        v

Worker Processing

        |
        |
        v

PostgreSQL

Inventory Item
Price Snapshot
Market Source
```

The V4 schema redesign separates these entities to improve maintainability and support future marketplace expansion.

---

# AWS Migration Considerations

Potential AWS-managed replacements:

---

## Amazon RDS for PostgreSQL

Advantages:

- Managed PostgreSQL service.
- Minimal application changes.
- Built-in backup and maintenance features.

---

## Amazon Aurora PostgreSQL

Advantages:

- PostgreSQL-compatible AWS database.
- Additional scalability and availability features.

---

## Current Status

The relational database direction is expected to remain PostgreSQL-compatible.

The main decision is selecting the most suitable AWS-managed PostgreSQL service.

---

# Authentication State Storage

## Purpose

The pipeline requires authenticated requests when collecting data from external platforms.

Authentication cookies generated during the login process are shared with worker services so they can perform authenticated requests.

Redis stores this temporary authentication state.

---

## Current Implementation

### Redis

Redis is used as a temporary shared storage layer for authentication cookies.

The authentication flow:

```text
Login Service
      |
      |
      v

Authentication Cookies

      |
      |
      v

Redis

      |
      |
      v

Worker Services

      |
      |
      v

External Platform Requests
```

Redis is suitable because:

- Workers can quickly retrieve authentication data.
- Multiple workers can reuse the same authentication session.
- Authentication data does not require permanent storage.

---

# AWS Migration Considerations

## Amazon ElastiCache for Redis

Potential replacement for the current Redis deployment.

Advantages:

- Managed Redis service.
- Reduced infrastructure management.
- Compatible with the current usage pattern.

---

# Data Processing Model

## Simplified Raw-to-Structured Approach

Many data engineering systems use a multi-layer architecture such as the medallion architecture:

```text
Bronze
  |
Silver
  |
Gold
```

This project does not implement a full medallion architecture because the main objective is focused on CS2 market price monitoring rather than building a general-purpose analytical platform.

Instead, the pipeline uses a simpler raw-to-structured approach:

```text
Raw External Data
(MongoDB)
        |
        |
Worker Processing
        |
        |
Structured Application Data
(PostgreSQL)
```

This design keeps the architecture simple while still providing the main benefits of separating raw responses from processed application data.

Future versions may introduce additional layers if the project expands into larger analytical workloads.

---

# Summary

The current storage architecture separates data based on its purpose:

| Data Type | Current Technology | AWS Direction |
|-----------|--------------------|---------------|
| Raw API responses | MongoDB | Under evaluation |
| Structured market data | PostgreSQL | RDS / Aurora PostgreSQL |
| Authentication state | Redis | ElastiCache Redis |

The final AWS storage architecture will be selected based on scalability requirements, operational complexity, and future development goals.