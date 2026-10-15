from orbit.investigator import investigate

def test_config_fault_produces_approval_gated_recommendation():
    evidence={"metrics":{"active_fault":"config","error_rate":0.35,"p95_latency_ms":210,
        "database_pool_usage_pct":35,"service":"demo","health":"degraded"},
        "logs":[{"level":"ERROR","message":"Missing configuration value"}],
        "commits":[{"sha":"a91c2ef","message":"configuration loader","risk_tags":["configuration"]}]}
    incident=investigate(evidence)
    assert incident["recommended_action"]=="restore_configuration"
    assert incident["status"]=="awaiting_approval"
    assert incident["confidence"]>=0.6
    assert incident["evidence_refs"]

def test_unknown_fault_requires_manual_review():
    evidence={"metrics":{"active_fault":None,"error_rate":0.01,"p95_latency_ms":120},"logs":[],"commits":[]}
    incident=investigate(evidence)
    assert incident["status"]=="needs_review"
    assert incident["recommended_action"]=="manual_investigation"

def test_policy_requires_operator_and_pending_incident():
    from orbit.policy import evaluate_remediation
    incident={"status":"awaiting_approval","recommended_action":"optimize_query"}
    assert evaluate_remediation(incident,"demo-operator")["allowed"] is True
    assert evaluate_remediation(incident,"anonymous")["allowed"] is False
