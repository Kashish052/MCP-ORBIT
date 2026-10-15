# MCP-ORBIT

**Autonomous Software Reliability, Root-Cause Analysis, and Self-Healing System using Model Context Protocol (MCP)**

MCP-ORBIT is a local-first prototype that investigates simulated application incidents using tools exposed through three MCP servers: monitoring, logs, and GitHub-change intelligence. It produces evidence-backed root-cause hypotheses, recommends an allowlisted recovery action, requires explicit approval, simulates remediation, and independently checks service state.

> **Safety note:** This is an educational MVP. GitHub commit data is synthetic, remediation is simulated, and no production system or real repository is modified. Do not expose the unauthenticated development server to the public internet.

## Features

- FastAPI incident-control API and browser dashboard
- Controlled configuration, latency, and database fault injection
- Three MCP servers launched over stdio
- Evidence-based, deterministic investigation engine
- Approval gate and allowlisted simulated actions
- Health verification and JSONL audit trail
- Basic automated tests

## Architecture

```text
Developer Dashboard
        |
        v
FastAPI Control Plane ---- Incident / Audit Store
        |
        v
MCP Client Gateway
   |         |         |
   v         v         v
Monitoring  Logs    GitHub-change
  MCP        MCP        MCP
   |         |         |
 metrics    logs    synthetic commits
        |
        v
Evidence-based Investigation
        |
        v
Candidate Action -> Policy Gate -> Human Approval
        |
        v
Simulated Remediation -> Independent Health Check
```

## Requirements

- Python 3.11 or 3.12
- pip

## Run on Windows (PowerShell)

Open a terminal in the project directory:

```powershell
py -0p
# Create a virtual environment using an installed supported version:
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn orbit.api:app --reload --host 127.0.0.1 --port 8000
```

If Python 3.12 is not installed, use an installed supported version (3.11 or 3.12) shown by `py -0p`; alternatively install Python from https://www.python.org/downloads/.

Open http://127.0.0.1:8000.

## Demo walkthrough

1. Click **Inject configuration fault**.
2. Click **Investigate incident**.
3. Review the evidence, hypothesis, confidence, and recommended action.
4. Click **Approve & simulate recovery**.
5. Confirm the service returns to a healthy state.

Try the **latency** and **database** scenarios too. **Clear faults** resets the demo service.

## API endpoints

- `GET /` — dashboard
- `GET /health` — demo-service health
- `GET /api/status` — current simulated service state
- `POST /api/faults/{scenario}` — inject `config`, `latency`, `database`, or `clear`
- `POST /api/incidents/investigate` — perform an MCP-backed investigation
- `POST /api/incidents/{incident_id}/approve` — approve simulated remediation
- `GET /api/incidents` — incident history
- `GET /api/audit` — audit events

## Run tests

```powershell
python -m pytest -q
```

## Project layout

```text
MCP-ORBIT/
├── orbit/
│   ├── api.py
│   ├── dashboard.html
│   ├── investigator.py
│   ├── mcp_client.py
│   ├── policy.py
│   ├── state.py
│   └── mcp_servers/
├── data/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Current MVP limitations

Not yet implemented: live GitHub API integration, LLM-based investigation, actual code patching, isolated Docker repair execution, authentication, distributed tracing integration, or production-grade deployment. These are future milestones, not existing features.

## Planned roadmap

1. Replace synthetic observability data with real metrics/log integrations.
2. Add LLM-driven planning while keeping evidence references and deterministic policy checks.
3. Build isolated Docker test environments and candidate-patch validation.
4. Expand incident benchmarks and measure diagnosis accuracy, recovery success, and false recovery confirmations.
5. Add authentication, audit hardening, and CI.

## License

No license has been selected yet. All rights are reserved by default unless a license is added.
