# SIEM Dashboard (Demo)

![SIEM Dashboard](assets/dashboard-preview.png)

A minimal SIEM dashboard demo that ingests synthetic logs into Elasticsearch (via Logstash), analyzes security events, and visualizes findings with Kibana plus a Flask UI.

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Docker Compose](https://img.shields.io/badge/docker--compose-ready-green)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Project summary

SIEM Dashboard is a security monitoring demo project built to showcase centralized log collection, real-time threat detection, and visual analytics. It includes an ELK stack, authenticated Flask frontend, synthetic log generation, and alert delivery hooks.

## Screenshots

![SIEM Dashboard](assets/dashboard-preview.png)

Features:
- Centralized log ingestion via Logstash
- Elasticsearch indexing and search for `siem-*` data
- Kibana dashboard export for severity, event types, and event rate
- Flask UI with authentication and role-based access control
- Synthetic log generator and rule-based alerting
- Slack/email alert notification hooks

Components:
- Elasticsearch (single-node)
- Logstash (TCP input, JSON lines)
- Kibana (dashboards)
- Flask app (authenticated dashboard and alerts)
- Log generator script (`scripts/generate_logs.py`)
- Alert service (`scripts/alerts.py`)

Quick start (requires Docker & Python 3.8+):

1. Start the stack:

```bash
make up
```

2. Install Python deps and run Flask UI (optional):

```bash
make install
make app
```


The Flask UI now includes login and role-based access control.

Default users are configured with `SIEM_USERS` in the environment:

- `admin:adminpass:admin`
- `analyst:analystpass:analyst`

Set a custom secret key with `SECRET_KEY`.

3. Generate demo logs (in a separate terminal):

```bash
make generate
```

4. Open Kibana at http://localhost:5601.

5. Import the Kibana saved objects:

```bash
# In Kibana, go to Stack Management > Saved Objects > Import
# Select kibana/saved_objects.ndjson
```

6. The web UI is available at http://localhost:5000.

Alerts service:

- The `alerter` service polls Elasticsearch for high-severity events and prints alerts to its logs.
- Start it with `docker-compose up -d` (it runs automatically with the included compose file).

Flask UI:

- The Flask UI runs on port 5000 and includes a simple `/alerts` view for recent HIGH severity events.

Notes:
- Logstash listens on TCP port 5000 for JSON lines and writes to `siem-YYYY.MM.DD` indices.
- The Flask app queries Elasticsearch directly at `http://localhost:9200` by default. Set `ES_HOST` environment variable to change.
- Use the built-in users in `docker-compose.yml` or override with `SIEM_USERS` in the environment.

Useful commands

```bash
make install   # install Python dependencies
make test      # run unit tests
make lint      # run flake8 linting
make up        # start the stack
make down      # stop the stack
make app       # start the Flask app
make generate  # send synthetic demo logs
make alerts    # run the alert service
```

License:
- This project is released under the MIT License. See `LICENSE`.
