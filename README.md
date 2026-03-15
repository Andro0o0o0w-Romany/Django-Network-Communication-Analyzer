# NetAnalyzer — Network Communication Analyzer

A Django web application for analysing communication network topologies. It identifies failure points, computes optimal routing paths, suggests device placements, and evaluates networks against customizable rulesets.

---

## Features

- **Network Topology Editor** — create nodes (routers, switches, firewalls, servers, etc.) and connections with bandwidth, latency, reliability, and distance properties. Visualized as an interactive drag-and-drop graph.
- **Failure Point Detection** — identifies articulation points (nodes whose removal disconnects the network) and bridges (critical links) using graph theory algorithms.
- **Optimal Routing** — computes shortest paths between all node pairs via Dijkstra's algorithm, including up to 3 alternative paths per pair.
- **Device Placement Suggestions** — recommends where to place repeaters, load balancers, and redundant nodes based on link distance, node degree, and topology weaknesses.
- **Customizable Rulesets** — define threshold-based rules (e.g. max latency, min bandwidth, min redundant paths) with severity levels. Rules are toggled per ruleset and applied at analysis time.
- **Risk Scoring** — each analysis produces a 0–100 risk score combining failure points, rule violations, and placement issues.

---

## Tech Stack

- **Backend** — Django 4.2, NetworkX 3.2 (graph algorithms), SQLite
- **Frontend** — Bootstrap 5 (dark theme), vis.js (network graph), Font Awesome, Inter font
- **Static files** — WhiteNoise

---

## Setup

```bash
# Install dependencies
venv/bin/pip install -r requirements.txt

# Apply migrations
venv/bin/python manage.py migrate

# Load demo data (6 networks, 3 rulesets)
venv/bin/python manage.py seed_demo

# Create admin user
venv/bin/python manage.py createsuperuser

# Start server
venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000

---

## Demo Networks

| Network | Nodes | Description |
|---------|-------|-------------|
| Campus Network Alpha | 12 | University 3-tier network (core / distribution / access) |
| Industrial Control Network | 8 | SCADA system with deliberate single points of failure |
| Data Center Spine-Leaf | 17 | Modern spine-leaf topology with 40/100G links |
| Smart City IoT | 20 | City-wide wireless sensor network with repeater towers |
| Enterprise Multi-Site WAN | 20 | 5 global offices connected via MPLS fiber and satellite |
| Hospital Critical Network | 20 | Life-critical systems with ICU, OR, ER, and ward segments |

## Demo Rulesets

| Ruleset | Rules | Use case |
|---------|-------|----------|
| Production Standards | 8 | General-purpose enterprise network checks |
| IoT / Wireless Standards | 6 | Relaxed thresholds for wireless and sensor networks |
| Critical Infrastructure | 8 | Strict zero-tolerance rules for life-critical systems |

---

## Rule Types

| Rule Type | What it checks |
|-----------|---------------|
| `max_latency` | Links exceeding a latency threshold (ms) |
| `min_bandwidth` | Links below a bandwidth threshold (Mbps) |
| `min_reliability` | Links below a reliability threshold (%) |
| `max_distance` | Links exceeding a physical distance (m) |
| `min_redundancy` | Node pairs with fewer than N distinct paths |
| `max_connections` | Nodes with more connections than the limit |
| `min_connections` | Nodes with fewer connections than the minimum |
| `max_hop_count` | Paths between nodes exceeding a hop limit |

---

## Project Structure

```
Django-communication/
├── network/        # Topology, Node, Connection models + graph editor
├── analysis/       # Analysis engine (engine.py) + result storage
├── rules/          # RuleSet and Rule models
├── templates/      # HTML templates (base + per-app)
└── network_analyzer/  # Django project settings and URLs
```
