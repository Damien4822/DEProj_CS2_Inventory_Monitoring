# Worker Architecture

## Overview

The Worker is responsible for executing the actual data collection process after receiving work from the messaging layer. Unlike the orchestration layer, which coordinates when workflows should execute, the Worker focuses on processing individual collection tasks.

Each Worker operates independently and is designed to scale horizontally by consuming messages from RabbitMQ. This allows multiple Worker instances to process different items concurrently while maintaining a simple execution model.

The current implementation is primarily designed around collecting market information for my inventory, while the architecture allows future expansion toward collecting the entire CS2 marketplace.

---

# Current Architecture (V3)

## Worker Lifecycle

The current Worker follows the execution flow below.

```text
RabbitMQ
    │
    ▼
Consume Messages
    │
    ▼
Retrieve Authentication Cookies
    │
    ▼
Fetch Marketplace Data
    │
    ▼
Extract Required Fields
    │
    ▼
Persist Data
    │
    ▼
Publish Result Messages
    │
    ▼
ACK / NACK Messages
```

Each stage performs a single responsibility, allowing failures to be isolated and retried independently.

---

## Message Consumption

The Worker consumes tasks from RabbitMQ using `basic.get`.

Instead of acknowledging messages immediately, acknowledgements are delayed until the complete processing pipeline has finished successfully.

This behaviour provides at-least-once delivery semantics.

If a Worker crashes before acknowledging the message, RabbitMQ automatically returns the message to the queue, allowing another Worker to continue processing.

The current implementation retrieves messages in batches (default: 20 items).

This value was originally selected based on the size of the author's inventory and serves as a configurable parameter rather than a fixed architectural limitation.

The primary motivation is to allow multiple Workers to process inventories concurrently while minimizing communication overhead.

---

## Authentication Retrieval

Before requesting marketplace data, the Worker retrieves the latest authentication cookies from Redis.

Redis serves as a shared authentication store between the login workflow and all Worker instances.

This design guarantees that every request uses the most recently generated authentication credentials.

Current workflow:

```text
Worker
    │
    ▼
Redis
    │
    ▼
Authentication Cookies
    │
    ▼
Marketplace Request
```

Although simple, this approach introduces an additional Redis request before every item is processed.

---

## Marketplace Data Collection

After obtaining authentication information, the Worker performs requests toward the configured marketplace source.

The current implementation communicates through exposed APIs.

To reduce the likelihood of triggering rate limits, a fixed delay of five seconds is introduced between requests.

This delay is currently static and manually configured.

The Worker assumes responsibility for communicating with source-specific APIs while abstracting those implementation details from downstream components.

---

## Response Mapping

Marketplace responses are currently returned as JSON documents.

The Worker extracts only the fields required by the current database schema.

Since the existing schema closely resembles the source response, very little transformation is required.

Basic default values (for example, `"0"`) are applied when optional fields are unavailable.

At the current stage, this should be considered field mapping rather than a complete transformation or validation process.

---

## Persistence

After processing a batch successfully, the Worker performs batch insertion into PostgreSQL.

The current schema follows a denormalized design to simplify data insertion and reduce processing complexity.

After persistence, processed messages are published into RabbitMQ for downstream consumers.

Only after all processing steps complete successfully are the original RabbitMQ messages acknowledged.

This ensures that failures occurring during persistence do not result in data loss.

---

# Current Limitations

## RabbitMQ Dependency

The Worker currently relies on RabbitMQ acknowledgement semantics (`ACK` / `NACK`) to guarantee reliable processing.

Should the messaging infrastructure change in the future, equivalent acknowledgement behaviour must be evaluated to preserve the same processing guarantees.

---

## Authentication Overhead

Authentication cookies are retrieved from Redis before every item is processed.

Although this guarantees that the latest credentials are always used, it also increases network overhead between the Worker and Redis.

---

## Source Validation

The current implementation primarily relies on API responses.

However, marketplace APIs cannot always be trusted solely based on HTTP status codes.

For example, previous versions of the BUFF API returned HTTP 200 responses even when authentication cookies had expired.

Workers must therefore validate both:

* Transport-level success (HTTP response)
* Business-level success (response payload)

before considering a request successful.

---

## Limited Data Validation

Current processing performs only minimal validation.

Responses are mapped directly into the persistence model with default values replacing missing fields.

There is currently no schema validation, quality verification, or enrichment pipeline.

---

## Database Persistence

Database writes currently prioritize simplicity.

Several database concerns are not yet addressed, including:

* Transaction boundaries
* UPSERT operations
* Conflict handling
* Idempotent writes
* Rollback strategies

These limitations become increasingly important as data volume and processing complexity grow.

---

# Future Enhancements

## Authentication Cache

Instead of retrieving cookies from Redis before every request, Workers may maintain an in-memory authentication cache.

The Worker would only request new credentials when:

* Authentication expires.
* Validation requests fail.
* Marketplace responses indicate invalid credentials.

This reduces Redis traffic while maintaining correctness.

---

## Dynamic Rate Limiting

The current fixed five-second delay may be replaced by adaptive rate limiting based on marketplace behaviour.

Potential improvements include:

* Dynamic request intervals
* Exponential backoff
* Source-specific rate limit policies

---

## Response Validation

Workers should introduce validation beyond simple HTTP status codes.

Possible validation includes:

* Authentication verification
* Required field validation
* Response schema verification
* Marketplace-specific error detection

This improves resilience against unexpected API behaviour.

---

## Transformation Pipeline

As additional marketplaces are integrated, response mapping may evolve into a dedicated transformation stage.

Possible future implementations include:

* dbt
* Apache Spark
* Custom transformation pipelines

Depending on future data complexity, additional enrichment and normalization stages may also be introduced.

---

## Reliable Persistence

Future database operations should introduce stronger consistency guarantees.

Potential improvements include:

* Transaction-based persistence
* UPSERT operations
* Conflict resolution
* Retry-safe database writes
* Idempotent processing

These improvements increase reliability while reducing the likelihood of duplicate or partially persisted data.

## Scalability Considerations

The current Worker architecture can be horizontally scaled by deploying additional Worker instances on Amazon EC2.

From a compute perspective, this approach is straightforward, as RabbitMQ naturally distributes messages across available consumers.

However, increasing the number of Workers does not necessarily increase the effective collection throughput.

Most marketplace providers enforce request rate limits based on client identity, such as source IP addresses, authentication credentials, or a combination of both.

When multiple Worker instances operate behind the same outbound IP address, increasing the number of Workers simply increases the request rate observed by the marketplace. This may lead to:

* Temporary rate limiting.
* Request throttling.
* Authentication challenges.
* Temporary or permanent IP restrictions.

Consequently, the scalability of the collection layer is constrained not only by compute resources but also by external service limitations.

Future improvements may consider:

* Region-aware Worker deployment.
* Distributed outbound IP pools.
* Source-specific request scheduling.
* Adaptive rate limiting.
* Coordinated request budgeting across Workers.

These approaches focus on scaling the effective request capacity rather than simply increasing the number of compute instances.

---

# Summary

The current Worker architecture prioritizes simplicity while providing a scalable execution model through RabbitMQ.

Its responsibilities include consuming work, retrieving authentication information, collecting marketplace data, mapping responses, persisting processed records, and publishing downstream events.

Although the current implementation satisfies the project's existing workload, several architectural improvements have been identified for future iterations, particularly around authentication caching, response validation, transformation, and reliable persistence.

These enhancements aim to improve scalability, resilience, and maintainability as the platform evolves beyond personal inventory monitoring toward full marketplace synchronization.
