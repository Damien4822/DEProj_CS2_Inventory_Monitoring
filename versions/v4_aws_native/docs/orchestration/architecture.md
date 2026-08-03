# Orchestration Layer

## Overview

The orchestration layer is responsible for coordinating the execution of workflows across the platform. Rather than performing business logic directly, it manages **when** tasks should run, **how** dependent tasks are executed, and **what** actions should be taken when failures occur.

The current architecture adopts **Apache Airflow** as the orchestration platform. The decision is primarily driven by Airflow's operational capabilities rather than the complexity of the current workflows.

This document discusses:

* The current architecture and why it was chosen.
* Alternative approaches that were considered.
* Future enhancements as the platform evolves.

---

# Current Architecture

## Why Airflow

The current project requires a scheduler capable of coordinating several recurring workflows while providing operational features beyond simple task scheduling.

Apache Airflow was selected because it provides:

* Workflow scheduling
* Task dependency management
* Automatic retry policies
* Execution history
* Built-in task logging
* Workflow monitoring
* Manual task execution

Although the current project does not yet contain a large number of workflows, these operational capabilities simplify maintenance and debugging while providing room for future expansion.

The current usage of Airflow should therefore be viewed as utilizing the **capabilities of the platform**, rather than requiring a sophisticated workflow engine.

---

## Current Responsibilities

At the current stage, Airflow is responsible for two primary workflows.

### BUFF Authentication

The BUFF marketplace requires authenticated sessions before inventory information can be collected.

Authentication is performed through browser automation, where a login workflow generates the required authentication cookies.

This workflow is executed by an Airflow Worker because all downstream data collection depends on successful authentication.

---

### Inventory Collection

Following authentication, Airflow executes the inventory collection workflow.

The workflow performs the following steps:

1. Fetch the user's inventory.
2. Normalize the collected items.
3. Publish individual items into RabbitMQ.
4. Allow downstream services to consume the messages independently.

The business logic remains inside the collectors while Airflow is responsible only for coordinating execution.

---

# Existing Evolution (V3)

The V3 architecture introduces a separation between orchestration and task execution.

Instead of executing browser automation directly through an Airflow Worker, the login workflow is containerized and executed as an ECS Task.

The browser automation process is packaged as a container image, allowing execution within a region geographically closer to the data source.

For example:

* BUFF authentication currently targets the Hong Kong region.
* Future data sources may execute within different regions depending on the marketplace location.

This architecture provides several advantages:

* Browser dependencies are isolated inside dedicated containers.
* Airflow Workers no longer require browser environments.
* Authentication can scale independently from the scheduler.
* Login workflows become reusable across multiple marketplaces.

With this design, Airflow transitions from being a task executor to becoming a workflow coordinator.

---

# Why Airflow Still Remains

After moving authentication to ECS, Airflow retains only a relatively small set of scheduled workflows.

Currently these include:

* Inventory collection
* Publishing messages to RabbitMQ

From a workload perspective, these tasks could easily be executed using simpler schedulers such as:

* Cron
* Kubernetes CronJob
* ECS Scheduled Tasks
* Windows Task Scheduler

Therefore, Airflow is no longer required because the workload itself is difficult.

Instead, it continues to provide value through its operational capabilities.

Examples include:

* Built-in retry handling
* Execution history
* Task logging
* Monitoring through the Airflow UI
* Manual task triggering
* Workflow visibility

These features reduce operational effort while keeping the implementation relatively simple.

---

# Future Enhancement

The current orchestration requirements represent only a small portion of the intended platform.

One planned evolution is expanding from monitoring a single inventory into synchronizing the entire CS2 marketplace.

A rough estimation includes:

* Approximately 2,000 base skin names.
* StatTrak variants.
* Five wear conditions (Factory New through Battle-Scarred).

This produces approximately 20,000 individual market hash names.

When including additional content such as:

* Stickers
* Charms
* Cases
* Agents
* Music Kits
* Tournament Capsules
* Newly released collections

the total catalog may reach approximately **40,000 to 60,000 items**, with continual growth as Valve releases new content.

Maintaining this catalog introduces additional orchestration requirements.

Potential future workflows include:

* Initial catalog generation.
* Detection of newly released items.
* Incremental catalog updates.
* Workload partitioning.
* Retry of failed partitions.
* Coordination of downstream processing.

Rather than discovering items dynamically during every execution, the platform may initialize the catalog from publicly available item databases and maintain it incrementally over time.

As the number of workflows increases, Airflow's orchestration capabilities become increasingly valuable.

---

# Alternative Approaches

Several alternative schedulers could satisfy the current workload.

| Solution            | Advantages                               | Limitations                                                                              |
| ------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| Cron                | Extremely lightweight                    | No retry policy, dependency management, or centralized monitoring                        |
| Kubernetes CronJob  | Native Kubernetes scheduling             | Limited workflow orchestration capabilities                                              |
| ECS Scheduled Tasks | Good integration with AWS infrastructure | Minimal dependency management                                                            |
| Custom Scheduler    | Fully tailored to project requirements   | Requires implementing functionality already provided by existing orchestration platforms |

While these alternatives are technically capable of executing the current workloads, they require additional development to achieve the same operational visibility and workflow management features that Airflow provides out of the box.

---

# Summary

The current project does not require a sophisticated orchestration engine due to the relatively small number of scheduled workflows.

However, Apache Airflow is adopted because its operational capabilities—such as scheduling, retry policies, execution history, dependency management, monitoring, and manual triggering—provide a stable foundation for both current operations and future platform growth.

As the platform evolves toward synchronizing the entire CS2 marketplace and coordinating increasingly complex workflows, the orchestration layer can naturally expand without requiring significant architectural changes.
