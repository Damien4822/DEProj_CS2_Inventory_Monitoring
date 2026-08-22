# V4 – Distributed Data Engineering Platform

## Overview

V4 represents the current architectural direction of the distributed CS2 Inventory Monitoring platform.

Rather than introducing a completely new processing model, V4 focuses on refining the architecture established in V3 through clearer separation of responsibilities, improved documentation of design decisions, and evaluation of future Data Engineering concepts.

The distributed processing model introduced in V3 remains the foundation of the platform. Inventory and marketplace data are collected from external sources, distributed across independent worker services for parallel processing, and persisted using dedicated storage systems. V4 builds upon this architecture by documenting the responsibilities of each architectural layer, identifying limitations observed during implementation, and exploring potential future improvements.

---

## Project Status

During the development of V4, one of the project's primary data sources, **BUFF**, transitioned from publicly accessible marketplace APIs toward a platform-service model that requires authenticated access through subscription-based services.

This change significantly affected the original development roadmap. Rather than continuing to expand features around an increasingly restricted data source, the project shifted its focus toward strengthening the underlying platform architecture.

As a result, V4 emphasizes architectural refinement over feature expansion.

The current implementation remains a functional distributed data collection platform, while the V4 documentation captures architectural discussions, design rationale, trade-offs, and future evolution based on lessons learned throughout previous iterations.

---

# Objectives

V4 is designed around the following objectives:

* Refine the layered architecture introduced in V3.
* Clearly separate architectural responsibilities across system layers.
* Document architectural decisions and their underlying rationale.
* Preserve the distributed asynchronous processing model.
* Improve maintainability through better storage organization and workflow separation.
* Establish a foundation for future Data Engineering enhancements.

---

# Architecture

The platform continues to follow a layered architecture.

```text
```
+----------------------+       +------------------------+
|   Control Layer      |       |     Execution Layer     |
|                      |       |                         |
| Workflow Orchestrator|       |     Worker Pool         |
|                      |       |                         |
| Task Queue / Broker  |------>|     Worker #1           |
|                      |       |     Worker #2           |
+----------------------+       |     Worker #N           |
                               +-----------+-------------+
                                           |
                         +-----------------+-----------------+
                         |                 |                 |
                         v                 v                 v
                  +-------------+   +-------------+   +-------------+
                  | Shared-state |   | Raw Storage |   | Structured  |
                  |   Storage    |   |             |   | Storage     |
                   +-------------+   +-------------+   +-------------+
```
```

The major architectural areas include:

* **Orchestration** — Coordinates workflow execution, scheduling, retries, and task dependencies.
* **Workers** — Execute distributed collection workloads independently.
* **Data Storage** — Manages structured, raw, and temporary datasets using dedicated persistence technologies.

Detailed discussions for each layer are available under the `docs/` directory.

```
docs/
├── orchestration/
├── workers/
└── data-storage/
```

Each document discusses:

* Current approach
* Design rationale
* Known limitations
* Alternative approaches
* Future enhancements

---

# Distributed Processing Model

The processing workflow remains largely unchanged from V3.

The pipeline performs the following high-level operations:

1. Schedule collection workflows.
2. Generate collection tasks.
3. Distribute workloads through the messaging layer.
4. Execute collection using distributed worker instances.
5. Process and normalize marketplace responses.
6. Persist structured and raw datasets.
7. Publish downstream events for additional processing.

This asynchronous processing model enables workers to execute independently while allowing the orchestration layer to focus solely on workflow coordination.

---

# Infrastructure

V4 continues to evaluate cloud-native infrastructure where it provides clear operational benefits.

Current architectural discussions include:

* Dedicated orchestration through Apache Airflow.
* Distributed worker execution.
* Containerized authentication workflows using Amazon ECS.
* Shared authentication state through Redis.
* Asynchronous communication through RabbitMQ.
* Hybrid persistence using PostgreSQL and MongoDB.

These technologies are treated as implementations of architectural capabilities rather than architectural layers themselves.

---

# Documentation

Beginning with V4, architectural knowledge is documented alongside the implementation.

Rather than focusing solely on source code, the project also documents the reasoning behind architectural decisions, observed limitations, and future design considerations.

The documentation should be viewed as a living architectural reference.

Some discussions describe implemented functionality, while others intentionally explore future improvements that have not yet been selected or implemented.

---

# Current Status

V4 represents the current architectural direction of the project.

The distributed architecture established in V3 remains operational, while V4 focuses on refining its design, documenting architectural decisions, and preparing the platform for future evolution as a more complete Data Engineering system.
