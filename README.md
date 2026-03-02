"# data-engineering-challenge" 
# Data Engineering Technical Challenge

## Overview

This project implements an end-to-end **multi-source real-time data pipeline** integrating PostgreSQL and MongoDB into a centralized analytical warehouse using Kafka, Debezium, ClickHouse, and Airflow.

The primary focus of this implementation is:

* Data correctness
* Idempotency
* Reliability
* Proper CDC handling (including updates and soft deletes)
* Maintainable architecture

The solution is deployed using Docker-based services (as an alternative to full Kind deployment) to simplify local reproducibility while preserving architectural integrity.

---

# Architecture

The pipeline follows this architecture:

PostgreSQL →
MongoDB →
Debezium →
Kafka →
ClickHouse (Silver Layer) →
Airflow (Batch Transformation) →
Gold Layer

Core components used:

* PostgreSQL (System of Record)
* MongoDB (Event Store)
* Kafka (Streaming Backbone)
* Debezium (CDC Engine)
* ClickHouse (Analytics Warehouse)
* Airflow (Orchestration Layer)

---

# Part 1: Environment Setup

## Services Deployed

* PostgreSQL (configured with `wal_level=logical`)
* MongoDB
* Kafka (KRaft mode)
* Kafka Connect
* Debezium Connectors
* ClickHouse
* Airflow

Deployment managed via Docker Compose for simplicity and reliability.

---

# Part 2: Multi-Source CDC Pipeline

## PostgreSQL

Created `users` table:

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name TEXT,
    email TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

Operations tested:

* Inserts
* Updates
* Deletes

Logical replication enabled to allow Debezium CDC streaming.

---

## MongoDB

Created `events` collection containing:

* login
* page_view
* add_to_cart
* other user activity events

Each event references:

```
user_id
event_type
timestamp
```

---

## Debezium Connectors

Configured:

* PostgreSQL connector
* MongoDB connector

These stream CDC events into Kafka topics:

* `postgres.public.users`
* `mongo.<database>.events`

All changes are captured:

* Inserts
* Updates
* Deletes
* Event payload changes

---

# Part 3: Real-Time Ingestion in ClickHouse

## ClickHouse Cluster

Deployed and configured for streaming ingestion.

---

## Kafka Engine Tables

Created Kafka engine tables to consume:

* `postgres.public.users`
* `mongo.<db>.events`

---

## Silver Layer

### silver_users

* Reflects current state of PostgreSQL users table
* Handles:

  * Inserts
  * Updates
  * Soft deletes
* Ensures latest version per user using versioning strategy

---

### silver_events

* Stores raw MongoDB events
* Preserves event-level granularity

---

# Part 4: Batch Orchestration with Airflow

## Airflow Deployment

Airflow deployed with:

* Scheduler
* Webserver
* Metadata DB

---

## Daily DAG

Created a daily idempotent DAG that:

1. Joins `silver_users` and `silver_events`
2. Generates `gold_user_activity`

---

## Gold Layer: gold_user_activity

For each user (previous day):

* Total number of events
* Timestamp of last event

Aggregation logic:

* Daily window-based processing
* Backfill safe
* Idempotent inserts (no duplication)

---

# Data Integrity & Reliability Considerations

* Logical replication enabled in PostgreSQL
* CDC events captured at commit level
* Soft delete handling implemented
* Idempotent batch processing
* Separation of Bronze/Silver/Gold modeling layers
* Clear isolation between raw ingestion and transformation layers

---

# Project Structure

```
.
├── docker-compose-main.yaml
├── docker-compose-airflow.yaml
├── main_files/
│   ├── postgresql.conf
│   ├── pg_hba.conf
│   └── other configs
├── kafka_config/
├── clickhouse_config/
├── zookeeper_config/
└── airflow_dags/
```

---

# How to Run

## 1. Start Core Services

```bash
docker-compose -f docker-compose-main.yaml up -d
```

## 2. Start Airflow

```bash
docker-compose -f docker-compose-airflow.yaml up -d
```

## 3. Configure Debezium Connectors

Use Kafka Connect REST API to register:

* PostgreSQL connector
* MongoDB connector

## 4. Verify CDC

Check Kafka topics:

```
postgres.public.users
mongo.<db>.events
```

## 5. Verify ClickHouse Ingestion

Confirm:

* silver_users populated
* silver_events populated

## 6. Run Airflow DAG

Trigger manually or wait for scheduled daily execution.

---

# Key Design Decisions

* Used CDC instead of polling to ensure real-time correctness.
* Implemented soft delete handling in ClickHouse.
* Designed idempotent daily aggregation to prevent duplicate reporting.
* Separated streaming ingestion from batch reporting layer.

---

# Deliverables

* Public Git repository
* All YAML configuration files
* Airflow DAG
* Docker Compose files
* This README documentation

---

# Conclusion

This project demonstrates:

* Multi-source CDC ingestion
* Real-time streaming architecture
* Analytical modeling (Silver/Gold pattern)
* Reliable batch orchestration
* Production-aware data engineering practices
