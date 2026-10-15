from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
def investigate(evidence: dict) -> dict:
    """Evidence-based deterministic investigator; no unsupported LLM claims."""
    metrics, logs, commits = evidence["metrics"], evidence["logs"], evidence["commits"]
    fault = metrics.get("active_fault")
    hypothesis, action, confidence = ("No known injected fault was detected. Review the evidence manually.",
                                     "manual_investigation", 0.35)
    rationale, refs = [], []
    if fault == "config":
        hypothesis, action, confidence = "Configuration regression is the most likely root cause.", "restore_configuration", 0.94
        rationale = ["The active fault state is config.","Synthetic commit metadata includes a configuration-loader change.",
                     "Error logs should contain a missing-configuration diagnostic."]
        refs = ["metrics.active_fault","logs.configuration_error","commit.a91c2ef"]
    elif fault == "latency":
        hypothesis, action, confidence = "A slow database query is the most likely cause of elevated latency.", "optimize_query", 0.90
        rationale = ["The active fault state is latency.","P95 latency is above the demo baseline.",
                     "Synthetic commit metadata includes a reporting-query change."]
        refs = ["metrics.p95_latency_ms","metrics.active_fault","commit.b721a6d"]
    elif fault == "database":
        hypothesis, action, confidence = "Database connection configuration is the most likely cause.", "restore_database_configuration", 0.92
        rationale = ["The active fault state is database.","Database connection errors appear in local error logs.",
                     "The failure is reproducible in the controlled demo environment."]
        refs = ["metrics.active_fault","logs.database_connection_error"]
    log_text = " ".join(str(x.get("message","")) for x in logs).lower()
    commit_text = " ".join(str(c.get("message",""))+" "+" ".join(c.get("risk_tags",[])) for c in commits).lower()
    if fault == "config" and "configuration" not in commit_text:
        confidence = min(confidence,0.65); rationale.append("Configuration-related commit metadata was not found.")
    if fault == "database" and "database" not in log_text and "connection" not in log_text:
        confidence = min(confidence,0.65); rationale.append("No matching database connection message was found.")
    if fault == "latency" and metrics.get("p95_latency_ms",0) < 500:
        confidence = min(confidence,0.60); rationale.append("Latency is below the investigation threshold.")
    return {"id":f"INC-{uuid4().hex[:8].upper()}","created_at":datetime.now(timezone.utc).isoformat(),
        "status":"awaiting_approval" if action != "manual_investigation" else "needs_review",
        "severity":"high" if metrics.get("error_rate",0)>=0.2 else "medium",
        "hypothesis":hypothesis,"confidence":round(confidence,2),"recommended_action":action,
        "rationale":rationale,"evidence_refs":refs,"evidence":evidence,"approved_by":None,"verification":None}
