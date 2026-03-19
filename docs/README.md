# Mini Observability Platform (Django Version)

A lightweight, self‑hosted observability platform built using **Python**, **Django**, and **Django REST Framework (DRF)**.  
This project includes:

- A **Django backend** for metrics/log ingestion, dashboards, and admin control.
- A **custom time‑series storage engine** for fast metric writes and reads.
- **Agents** that collect system metrics and send them to the backend.
- A **CLI tool** for terminal‑friendly access to metrics and logs.

This README lists all required packages and dependencies for the backend, agent, and CLI components.

---

## Requirements

### Python Version
**Python 3.11+** is recommended.

---

## Backend (Django Collector)

### Core Packages
```
Django>=5.0
djangorestframework>=3.15
```

### Optional but Recommended
```
django-cors-headers>=4.0
python-dotenv>=1.0
psutil>=5.9      # for system stats if backend collects any
requests>=2.31   # for internal service-to-service calls
PyYAML>=6.0      # for config loading
```

### Charting / Visualization
(For dashboard rendering inside Django templates)
```
plotly>=5.20
```
Or for ECharts support:
```
django-echarts>=0.5
```

### Storage Engine Helpers
(Used internally for time-series file handling, compression, etc.)
```
numpy>=1.26
ujson>=5.9
lz4>=4.3
```

### Authentication / Security
```
djangorestframework-simplejwt>=5.3
cryptography>=42.0
```

---

## Agent Requirements

Agents run on Linux, Raspberry Pi OS, or Windows.

### Agent Packages
```
psutil>=5.9
requests>=2.31
PyYAML>=6.0
```

### Optional Enhancements
```
docker>=7.0     # Collect Docker container metrics
pywin32>=306    # Windows-specific collectors
```

---

## CLI Tool Requirements

```
requests>=2.31
rich>=13.7      # Optional: pretty output in terminal
click>=8.1      # CLI framework (or Typer if chosen)
PyYAML>=6.0
```

---

## Development Tools (Optional)

```
black>=24.0
flake8>=7.0
mypy>=1.8
pytest>=8.0
pytest-django>=4.8
```

---

## System Dependencies

### Linux / Pi
```
sudo apt install python3-dev build-essential
```

### Windows
- Make sure Python is installed with "Add to PATH" enabled.
- Recommended: install **Windows Build Tools** if compiling lz4/numpy from source.

---

## Directory Layout (Minimal)

```
obs-platform/
│
├── backend/
│   ├── obs_django/
│   ├── metrics/
│   ├── logs/
│   ├── nodes/
│   ├── dashboards/
│   └── storage_engine/
│
├── agent/
│   ├── agent.py
│   └── collectors/
│
├── cli/
│   └── obs.py
│
└── docs/
    ├── overview_django.md
    └── README.md   <-- this file
```

---

## Installation

### Install backend dependencies
```
pip install -r requirements.txt
```

### Install agent
```
pip install psutil requests PyYAML
```

### Install CLI
```
pip install requests rich click PyYAML
```

---

## Purpose

This README provides the baseline dependency set for building and running the Django-based observability platform.  
It will expand as the project adds features such as tracing, alerting, pluggable collectors, or WebSocket streaming.

