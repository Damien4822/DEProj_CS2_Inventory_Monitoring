# DEProj_CS2_Inventory_Monitoring

## Overview

This project demonstrates data engineering concepts through the design and implementation of an automated ETL pipeline for monitoring tradable and marketable items from a Counter-Strike 2 (CS2) inventory.

The pipeline extracts inventory data from Steam and retrieves pricing information from multiple marketplaces, currently including Steam Market and BUFF163. The collected data is transformed into structured tabular datasets and exported for analysis.

Workflow orchestration is managed using Apache Airflow, enabling scheduled execution, task dependency management, and modular pipeline design.

For endpoints requiring authentication, Playwright is used to automate login procedures and retrieve session credentials securely using my own authorized account.

This project emphasizes ETL architecture, workflow orchestration, modular system design, and iterative architectural improvements across multiple versions.

---

## Architecture Overview

The pipeline follows a standard ETL workflow:

1. **Extract** – Retrieve inventory data from Steam.
2. **Enrich** – Fetch corresponding market pricing data from Steam Market and BUFF163.
3. **Transform** – Normalize and structure raw API responses into tabular datasets.
4. **Load / Export** – Export processed results for downstream analysis.

Apache Airflow manages task orchestration, scheduling, and execution flow.

Authentication workflows are automated using Playwright, which handles browser-based login procedures and session management when required.

---

## Repository Structure

- `airflow/` – Contain local configuration files.
- `versions/` – Versioned implem.entations (V1 prototype, V2 refactored architecture)

Each version documents architectural decisions and design evolution separately. Please navigate to each version's README.md for better explaination of each approach.

---

## Disclaimer

This project is developed for educational and portfolio purposes only.  
It demonstrates ETL pipeline architecture, API integration, and workflow orchestration using publicly accessible endpoints.

This project is not affiliated with, endorsed by, or sponsored by Valve, Steam, or BUFF163.

All data access is performed using authorized accounts and publicly available interfaces. Users are responsible for complying with the terms of service of any external platforms referenced in this project.