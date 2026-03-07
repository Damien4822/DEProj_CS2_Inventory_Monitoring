# V1 – Local Prototype Implementation

## Overview

V1 represents the initial working prototype of the CS2 Inventory Monitoring pipeline.

The goal of this version was to build a fully functional end-to-end ETL workflow capable of:

- Extracting tradable and marketable items from a Counter-Strike 2 (CS2) inventory via Steam.
- Fetching pricing information from Steam Market and BUFF163.
- Transforming raw API responses into structured tabular datasets.
- Exporting results to local Excel files for analysis.

This version prioritizes functionality and correctness over architectural modularity.

---

## Architecture Characteristics

V1 follows a monolithic DAG design:

- Business logic, API calls, and transformation logic are defined directly inside the Airflow DAG file.
- Output is written to local file storage.
- Configuration values (e.g., paths, constants) are defined within the DAG.
- Authentication for certain endpoints is handled using Playwright to automate login and retrieve session cookies.

The pipeline is orchestrated using Apache Airflow with scheduled execution and task dependency management.

---

## Design Decisions

This version was built as a prototype in order to:

- Validate API integrations.
- Confirm authentication workflows.
- Verify data transformation logic.
- Produce working market data exports.

---

## Installation (V1)

This version was developed and tested in a local Linux environment.

### 1. Install Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```
### 2. Playwright Browsers Setup
Install the required browser binaries:
```bash
playwright install
```

###  Execution Model

In the current repository structure, this pipeline is executed through Apache Airflow DAGs, located in:

```
airflow/dags/versions/v1/
```

Airflow DAGs will import the pipeline logic from
```
versions/v1/
```

Running the pipeline directly is *not recommended*, as scheduling and task orchestration are handled by Airflow.

###  DAG Configuration
The DAG limits parallel execution using the following parameters:

- max_active_runs = 2
- max_active_tasks = 4

These limits help to:

* prevent API rate limiting
* avoid excessive parallel browser sessions

Global Airflow configuration remains largely unchanged.

---

## Limitations

While functionally complete, V1 presents several architectural and scalability limitations:

### 1. Tight Coupling Between Orchestration and Business Logic
All extraction, transformation, API interaction, and export logic are defined directly inside the Airflow DAG file. This reduces modularity and limits reusability.

### 2. Sequential Inventory Pagination
Inventory items are retrieved using paginated API calls. The process is performed sequentially, which increases total runtime as inventory size grows.

### 3. Fan-Out API Call Pattern
After extracting inventory items, the pipeline performs individual market price requests per item across multiple marketplaces (Steam Market and BUFF163). 

This creates an N × M request pattern (N items × M marketplaces), leading to:
- Increased latency
- Higher exposure to rate limits
- Longer execution times for large inventories

### 4. Limited Internal Parallelism
Although Airflow allows task-level parallelism, API calls within each task are executed sequentially with manual sleep intervals to avoid rate limiting. This approach does not scale efficiently for larger datasets.

### 5. Local Filesystem Dependency
Outputs are written to local storage, limiting portability and distributed execution.

These scalability constraints motivated the architectural redesign introduced in V2, where separation of concerns and improved configurability enable more flexible execution strategies.
---

## Output Artifacts

This version exports structured market data into Excel files stored locally.

Sample output files are included for documentation purposes only. Runtime-generated files are excluded from version control.

---

## Purpose of V1

V1 serves as:

- A proof-of-concept implementation.
- A validation stage for API integrations.
- A baseline for architectural comparison with V2.

It is intentionally preserved as a snapshot of the initial working design.