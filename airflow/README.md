# Airflow (Local Development Environment)

This directory contains the **Apache Airflow setup used for local development and testing.**

Unlike earlier versions of the project, this folder no longer contains active pipeline orchestration logic or production DAG implementations.

Instead, it serves as a lightweight environment for:
* Running Airflow locally
* Testing configurations
* Experimenting with DAG behavior (if needed)
* Managing Airflow services during development
Current Structure
---

# Directory Structure

```
airflow/ 
│ 
├── dags/ # (Optional) Placeholder for local or experimental DAGs ├── requirements.txt # Dependencies for the Airflow environment 
├── config-files #local configuration files.
└── README.md
```
Note: Current pipeline logic and versioned implementations are under `versions/` directory.

# Purpose
This directory is intentionally minimal and is not responsible for executing project pipelines.

Its role is limited to:

- Providing a local Airflow instance
- Supporting development workflows
- Allowing optional DAG experimentation without affecting core project logic

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

# Notes
- This setup is intended for local development only
- No DAGs are maintained in this directory
- Pipeline orchestration, if reintroduced, should be documented separately
- The dags/ folder can be used for temporary or experimental workflows


# History
Earlier versions of the project used this directory as a full orchestration layer, with DAGs importing pipeline logic from `versions/` directory.

This approach has since been removed in favor of a simpler development-focused setup.