import { useState } from "react";
import { runSecurityCheck } from "../api/endpoints";

const ITEMS = [
  ["authentication", "Authentication"], ["authorization", "Authorization"],
  ["data_encryption", "Data encryption"], ["secure_api", "Secure API"],
  ["data_backup", "Data backup"], ["vulnerability_assessment", "Vulnerability assessment"],
  ["access_logging", "Access logging"], ["incident_response_plan", "Incident response plan"],
];

export default function ChecklistPanel({ pilotId, initialChecklist = {}, initialStatus = "pending", onChecked }) {
  const [checklist, setChecklist] = useState(Object.fromEntries(ITEMS.map(([key]) => [key, Boolean(initialChecklist[key])])));
  const [result, setResult] = useState(initialStatus === "pending" ? null : { security_status: initialStatus, failed: ITEMS.filter(([key]) => !initialChecklist[key]).map(([key]) => key) });
  const [saving, setSaving] = useState(false); const [error, setError] = useState("");
  async function submit(event) { event.preventDefault(); setSaving(true); setError(""); try { const response = await runSecurityCheck(pilotId, checklist); setResult(response); onChecked(response); } catch (err) { setError(err.detail || err.message || "Security check could not be completed"); } finally { setSaving(false); } }
  return <section className="panel checklist-panel"><div className="section-heading"><div><p className="eyebrow">Security gate</p><h2>Cybersecurity checklist</h2></div>{result && <strong className={`security-status security-${result.security_status}`}>{result.security_status.replaceAll("_", " ")}</strong>}</div><form onSubmit={submit}><div className="security-grid">{ITEMS.map(([key, label]) => <label className="security-toggle" key={key}><input type="checkbox" checked={checklist[key]} onChange={(event) => setChecklist((current) => ({ ...current, [key]: event.target.checked }))} /><span>{label}</span></label>)}</div>{result?.security_status === "passed" && <div className="security-result passed"><strong>Security gate passed</strong><p>All {result.total_count || 8} required controls are confirmed.</p></div>}{result?.security_status === "needs_remediation" && <div className="security-result remediation"><strong>Remediation required</strong><p>Failed controls: {(result.failed || []).map((key) => ITEMS.find(([itemKey]) => itemKey === key)?.[1] || key).join(", ")}.</p></div>}{error && <div className="state-message state-error">{error}</div>}<button className="btn btn-primary" disabled={saving}>{saving ? "Running security check…" : "Run security check"}</button></form></section>;
}
