def evaluate_remediation(incident: dict, actor: str) -> dict:
    """Fail-closed policy gate for local demo remediation."""
    if actor != "demo-operator":
        return {"allowed": False, "reason": "Only demo-operator can approve remediation."}
    if incident.get("status") != "awaiting_approval":
        return {"allowed": False, "reason": "Incident is not awaiting approval."}
    allowed = {"restore_configuration", "optimize_query", "restore_database_configuration"}
    if incident.get("recommended_action") not in allowed:
        return {"allowed": False, "reason": "Action is not on the allowlist."}
    return {"allowed": True, "reason": "Allowlisted simulated action; no production system is modified.",
            "requires_human_approval": True}
