# Airflow Orchestration

This directory contains the **Apache Airflow orchestration layer** for the project.

Airflow is responsible for:

* Scheduling pipeline execution
* Managing task dependencies
* Controlling parallel execution
* Monitoring pipeline runs through the web interface

The pipeline logic itself is stored separately under the `versions/` directory and imported by the DAGs.

---

# Directory Structure

```
airflow
│
├── dags/
│   └── versions/
│       ├── v1/
│       └── v2/
│
├── requirements.txt
└── README.md
```

### `dags/`

Contains Airflow DAG definitions.

Each DAG corresponds to a pipeline version and imports logic from the `versions/` directory.

Example structure:

```
dags/
└── versions/
    ├── v1/
    │   └── cs2_market_etl.py
    │
    └── v2/
        └── inventory_pipeline.py
```

These DAGs act as **thin orchestration layers**, delegating most processing logic to the pipeline modules.

---

### `requirements.txt`

Defines the dependencies required to run the Airflow environment.

Typical dependencies include:

* `apache-airflow`
* shared utilities used by DAGs
* client libraries for services such as Redis, RabbitMQ, or MongoDB (if DAG tasks interact with them)

Pipeline-specific dependencies are defined separately in:

```
versions/v1/requirements.txt
versions/v2/requirements.txt
```

---

# Running Airflow Locally

## 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

---

## 2. Install Airflow Dependencies

```bash
pip install -r airflow/requirements.txt
```

---

## 3. Initialize the Airflow Database

```bash
airflow db migrate
```

---

## 4. Create an Admin User

```bash
airflow users create \
  --username admin \
  --firstname admin \
  --lastname admin \
  --role Admin \
  --email admin@example.com
```

---

## 5. Start Airflow Services

Run the scheduler and webserver in separate terminals.

Scheduler:

```bash
airflow scheduler
```

Webserver:

```bash
airflow webserver
```

The web interface will be available at:

```
http://localhost:8080
```

---

# DAG Design

The DAGs in this directory are intentionally **minimal**.

Their main responsibilities are:

* defining task dependencies
* configuring retries and scheduling
* limiting parallel execution

Example constraints used in pipelines:

* `max_active_runs`
* `max_active_tasks`

These settings help prevent:

* API rate limiting
* excessive parallel requests
* resource contention

---

# Pipeline Integration

DAGs import pipeline logic from the `versions/` directory.

Example:

```python
from versions.v2.pipelines.inventory_fetch import run_pipeline
```

This separation keeps:

* orchestration logic inside `airflow/`
* pipeline implementation inside `versions/`

---

# Notes

* Pipelines are intended to be executed **through Airflow DAGs**, not directly.
* Each pipeline version maintains its own dependencies and documentation.
* Airflow serves as the central scheduling and monitoring system for the project.
