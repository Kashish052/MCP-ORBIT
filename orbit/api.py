from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from orbit.state import ROOT, INCIDENTS_FILE, DEFAULT_STATE, append_log, audit, load_json_list, save_json_list, read_state, write_state, read_audit
from orbit.mcp_client import gather_incident_evidence
from orbit.investigator import investigate
from orbit.policy import evaluate_remediation
app = FastAPI(title="MCP-ORBIT",version="0.1.0",
    description="Local-first MCP incident investigation and safe simulated recovery.")
UI_FILE = ROOT / "orbit" / "dashboard.html"
class ApprovalRequest(BaseModel):
    actor: str = "demo-operator"
def _incidents(): return load_json_list(INCIDENTS_FILE)
def _save_incidents(rows): save_json_list(INCIDENTS_FILE,rows)
@app.get("/",response_class=HTMLResponse)
def dashboard(): return UI_FILE.read_text(encoding="utf-8")
@app.get("/health")
def health():
    s=read_state()
    return {"status":"healthy" if s["active_fault"] is None else "degraded","service":s["service"],"active_fault":s["active_fault"]}
@app.get("/api/status")
def status(): return read_state()
@app.get("/api/incidents")
def incidents(): return list(reversed(_incidents()))
@app.get("/api/audit")
def audit_events(): return read_audit()
@app.post("/api/faults/{scenario}")
def inject_fault(scenario: str):
    if scenario not in {"config","latency","database","clear"}: raise HTTPException(400,"Scenario must be config, latency, database, or clear.")
    state=DEFAULT_STATE.copy()
    if scenario=="clear":
        append_log("INFO","Faults cleared; demo service restored.");write_state(state);audit("fault_cleared",details={"scenario":scenario})
        return {"message":"Faults cleared.","state":read_state()}
    state["active_fault"]=scenario;state["health"]="degraded"
    if scenario=="config":
        state.update({"error_rate":0.35,"p95_latency_ms":210})
        append_log("ERROR","Missing required configuration value: SERVICE_REGION",error_code="CONFIG_MISSING",deployment=state["last_deployment"])
    elif scenario=="latency":
        state.update({"error_rate":0.04,"p95_latency_ms":1850,"database_pool_usage_pct":92})
        append_log("WARNING","Reporting query exceeded latency threshold",error_code="QUERY_SLOW",duration_ms=1850)
    else:
        state.update({"error_rate":0.48,"p95_latency_ms":1200,"database_pool_usage_pct":100})
        append_log("ERROR","Database connection refused: invalid connection configuration",error_code="DB_CONNECTION_REFUSED")
    write_state(state);audit("fault_injected",details={"scenario":scenario})
    return {"message":f"Injected {scenario} fault.","state":state}
@app.post("/api/incidents/investigate")
async def investigate_incident():
    try: evidence=await gather_incident_evidence();incident=investigate(evidence)
    except Exception as exc:
        audit("investigation_failed",details={"error":str(exc)[:300]})
        raise HTTPException(502,f"MCP investigation failed: {exc}")
    rows=_incidents();rows.append(incident);_save_incidents(rows)
    audit("incident_investigated",details={"incident_id":incident["id"],"action":incident["recommended_action"],"confidence":incident["confidence"]})
    return incident
@app.post("/api/incidents/{incident_id}/approve")
def approve_remediation(incident_id: str,request: ApprovalRequest):
    rows=_incidents();incident=next((x for x in rows if x["id"]==incident_id),None)
    if incident is None: raise HTTPException(404,"Incident not found.")
    decision=evaluate_remediation(incident,request.actor)
    audit("remediation_policy_evaluated",actor=request.actor,details={"incident_id":incident_id,**decision})
    if not decision["allowed"]: raise HTTPException(403,decision["reason"])
    state=read_state();count=int(state.get("recovery_count",0))+1
    state=DEFAULT_STATE.copy();state["recovery_count"]=count;write_state(state)
    append_log("INFO","Simulated remediation applied; demo service returned to baseline.",incident_id=incident_id,action=incident["recommended_action"])
    checked=read_state()
    verification={"health":"healthy" if checked["active_fault"] is None else "degraded","error_rate":checked["error_rate"],
        "p95_latency_ms":checked["p95_latency_ms"],"recovery_confirmed":checked["active_fault"] is None and checked["error_rate"]<=0.05 and checked["p95_latency_ms"]<=500}
    incident["status"]="resolved" if verification["recovery_confirmed"] else "escalated"
    incident["approved_by"]=request.actor;incident["verification"]=verification;_save_incidents(rows)
    audit("simulated_remediation_completed",actor=request.actor,details={"incident_id":incident_id,"verification":verification})
    return {"incident":incident,"policy":decision,"verification":verification}
