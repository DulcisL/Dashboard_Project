# Mini Observability Platform (Django-Based Project Overview)

## Project Summary
This project is a self-hosted, Python-based observability platform inspired by tools like Prometheus, Grafana, and Jaeger. The goal is to build a lightweight system capable of collecting metrics, logs, and custom application data across multiple machines, storing them efficiently, and visualizing them through both a **Django-powered web UI** and a **CLI tool**.

Django replaces lightweight frameworks (like Flask/FastAPI) in this design, giving the platform a structured foundation with built-in authentication, ORM models, and a powerful admin interface. The platform is meant to be both a serious learning project and a practical tool you can deploy across personal servers, Raspberry Pis, and HPC-style simulations.

---

## High-Level Features

### 1. Metrics Collection Agents
Python agents running on each machine:
- Collect CPU, memory, disk, network, GPU, temperature, and process metrics.
- Optionally collect Docker container stats.
- Push metrics and logs to the Django backend via **Django REST Framework (DRF)**.

### 2. Django Collector Service
The central backend service:
- Built using **Django + Django REST Framework**.
- Provides authenticated API endpoints for:
  - Metrics ingestion
  - Log ingestion
  - Node registration and heartbeats
- Stores metadata using Django ORM:
  - Nodes
  - Applications
  - API keys / tokens
  - Metric definitions
  - Dashboard configurations

### 3. Custom Metrics API (DRF)
Applications (HPC simulations, Docker apps, Python scripts, etc.) can POST structured metrics:

```json
{
  "app": "heat_solver",
  "metric": "iteration_time_ms",
  "value": 3.92
}
```

DRF handles:
- Input validation
- Authentication / authorization
- Serialization and response formatting

### 4. Time-Series Storage Engine
A custom Python time-series subsystem, separate from the ORM, optimized for metric data:
- Append-only, timestamp-indexed storage format.
- Data sharded by time (e.g., per hour or per day).
- Support for retention policies (e.g., keep 30 days of high-res data, downsample older data).
- Efficient queries over time ranges with basic aggregations (min, max, avg, percentile).

Django talks to this layer via a dedicated storage service module (e.g., `storage_engine/reader.py`, `storage_engine/writer.py`).

### 5. Log Ingestion and Querying
Agents send logs to the Django backend:
- Logs stored in structured text or binary segments with metadata (timestamp, node, app, level).
- DRF endpoints provide log querying with filters such as:
  - node
  - application
  - log level
  - substring search

Example API usage:

```text
GET /api/logs?node=pi4&app=heat_solver&contains=error
```

### 6. Django Dashboard UI
A Django-based web UI provides:
- Real-time-ish charts (e.g., Plotly or ECharts embedded in Django templates).
- Node health dashboards (CPU, RAM, disk usage per node).
- Application metric dashboards (e.g., iteration time, throughput, latency).
- Log viewers with filtering and search.
- A customizable “home” dashboard with panels and saved views.

### 7. Django Admin as Control Room
The Django Admin interface serves as an internal control panel:
- Manage nodes and their metadata.
- Create and manage API keys/tokens.
- Inspect active applications and their metrics.
- Configure dashboard presets and groups.
- View ingestion stats (e.g., last heartbeat per node).

### 8. CLI Interface
A Python CLI tool communicates with the Django REST API, providing terminal-friendly access:

```bash
obs top --node pi4
obs logs --app heat_solver --tail 50
obs plot --metric iteration_time_ms --from -1h
```

The CLI:
- Uses API tokens to authenticate.
- Provides quick inspection without needing the web UI.
- Can be integrated into scripts or cron jobs.

---

## Architecture Overview

### Components

- **Agent Service**
  - Runs on each monitored machine (server, laptop, Pi).
  - Collects system metrics and logs.
  - Sends data to Django/DRF via HTTP(S).

- **Django Collector API**
  - Core backend running Django + DRF.
  - Exposes REST endpoints for metrics, logs, nodes, and dashboards.
  - Uses Django ORM for metadata and a custom engine for time-series data.

- **Time-Series Storage Engine**
  - Python module responsible for writing and querying metric data.
  - Tuned for append-heavy workloads and time-range reads.

- **Query Layer**
  - Implemented as Django services or utilities.
  - Aggregates, filters, and formats data for UI and CLI.

- **Django Web UI**
  - Renders dashboards and log views via templates.
  - Integrates charts and interactive controls.

- **CLI Client**
  - Scriptable, terminal-based interface.
  - Talks to Django API using HTTP requests.

### Communication Overview

- Agents → Django:
  - HTTP(S) POST requests via DRF endpoints.
  - Heartbeats, metrics, logs.

- Web UI / CLI → Django:
  - HTTP(S) GET/POST for querying or configuring.

- Django → Storage Engine:
  - Internal Python calls for time-series read/write operations.

---

## Learning Outcomes

### Django & REST Architecture
- Designing DRF serializers, viewsets, and routers.
- Handling authentication with tokens for agents and CLI clients.
- Using Django’s ORM and migrations to model system entities.
- Customizing Django Admin for operational workflows.

### Systems Programming & Monitoring
- Writing agents that collect system metrics and logs.
- Dealing with multiple OS environments (Linux, Windows, Pi).
- Handling network failures and retry strategies for agents.

### Storage Systems & Time-Series Design
- Designing an efficient time-series format.
- Implementing append-only logs and segment files.
- Building indexes for fast range queries.
- Implementing retention and compaction policies.

### Visualization & UX
- Embedding interactive charts in Django templates.
- Building clean, minimal dashboards for metrics and logs.
- Designing intuitive CLI subcommands for power users.

---

## Future Extensions

- **Alerting Rules**
  - Threshold-based alerts (e.g., CPU > 90% for 5 minutes).
  - Notifications via email, webhook, or chat integrations.

- **Anomaly Detection**
  - Basic ML models to detect unusual patterns in metrics.
  - Marking and visualizing outliers on charts.

- **Real-Time Streaming**
  - WebSockets via Django Channels for live-updating dashboards.
  - Streaming logs and metrics without polling.

- **Multi-Collector / Sharded Architecture**
  - Deploying multiple Django collectors.
  - Sharding nodes across collectors and aggregating views.

- **Plugin System**
  - Allowing custom metric collectors or log parsers to be plugged into agents.

---

## Suggested Repository Structure

```text
obs-platform/
│
├── agent/
│   ├── agent.py               # Main agent process
│   └── collectors/            # OS-specific or app-specific collectors
│
├── backend/
│   ├── obs_django/            # Django project root (settings, urls, wsgi/asgi)
│   ├── metrics/               # DRF app for metrics ingestion and queries
│   ├── logs/                  # DRF app for logs ingestion and queries
│   ├── nodes/                 # Node registration, heartbeat tracking
│   ├── dashboards/            # Views/templates for dashboards
│   └── storage_engine/        # Custom time-series storage implementation
│
├── cli/
│   └── obs.py                 # Entry point for the CLI tool
│
└── docs/
    └── overview_django.md     # This overview document
```

---

## Purpose

This Django-based observability platform is intended as a long-term, growable project. It starts as a simple metrics/logs collector and can evolve into a miniature, self-hosted alternative to larger observability stacks — tailored to your own infrastructure, experiments, and systems.

It is both:
- A **playground** for learning Django, DRF, storage design, and distributed system concepts.
- A **practical tool** you can actually run in your homelab, on your Raspberry Pis, and alongside your simulations.
